from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from django.db import transaction

from django.templatetags.static import static


from .taxonomy.generic import ModelWithTaxon, ModelWithRequiredTaxon
from .taxonomy.lazy import LazyAppTaxon
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey

from localcosmos_server.slugifier import create_unique_slug
from localcosmos_server.utils import generate_md5, get_content_instance_app

from content_licencing.models import ContentLicenceRegistry

from datetime import timedelta
import requests

import uuid, os, json, shutil

# also used by app_kit
IMAGE_SIZES = {
    'regular' : {
        '1x' : 250,
        '2x' : 500,
        #'4x' : 1000,
    },
    'large' : {
        '4x' : 1000,
    },
    'xlarge' : {
        '8x' : 2000,
    },
    'all' : {
        '1x' : 250,
        '2x' : 500,
        '4x' : 1000,
        '8x' : 2000,
    }
}



'''
    Generic Content Images
'''
class ServerContentImageMixin:

    def get_model(self):
        return ServerContentImage


    def get_content_type(self):
        return ContentType.objects.get_for_model(self.__class__)

    def _content_images(self, image_type='image'):

        content_type = self.get_content_type()
        ContentImageModel = self.get_model()

        self.content_images = ContentImageModel.objects.filter(content_type=content_type, object_id=self.pk,
                                                          image_type=image_type).order_by('position')

        return self.content_images

    def all_images(self):

        content_type = self.get_content_type()
        ContentImageModel = self.get_model()

        self.content_images = ContentImageModel.objects.filter(
            content_type=content_type, object_id=self.pk)

        return self.content_images

    def images(self, image_type='image'):
        return self._content_images(image_type=image_type)

    def image(self, image_type='image'):
        content_image = self._content_images(image_type=image_type).first()

        if content_image:
            return content_image

        return None

    def image_url(self, size=400):

        content_image = self.image()

        if content_image:
            return content_image.image_url(size)

        return static('noimage.png')

    # this also deletes ImageStore entries and images on disk

    def delete_images(self):

        content_type = self.get_content_type()
        ContentImageModel = self.get_model()

        content_images = ContentImageModel.objects.filter(
            content_type=content_type, object_id=self.pk)

        for image in content_images:
            # delete model db entries
            image_store = image.image_store
            image.delete()

            image_is_used = ContentImageModel.objects.filter(
                image_store=image_store).exists()

            if not image_is_used:
                image_store.delete()

    def get_content_images_primary_localization(self):

        locale = {}

        content_images = self.images()

        for content_image in content_images:

            if content_image.text and len(content_image.text) > 0:
                locale[content_image.text] = content_image.text

        return locale
    

class LocalcosmosUserManager(UserManager):
    
    def create_user(self, username, email, password, **extra_fields):
        slug = create_unique_slug(username, 'slug', self.model)

        extra_fields.update({
            'slug' : slug,
        })

        user = super().create_user(username, email, password, **extra_fields)
        
        return user

    def create_superuser(self, username, email, password, **extra_fields):

        slug = create_unique_slug(username, 'slug', self.model)

        extra_fields.update({
            'slug' : slug,
        })

        superuser = super().create_superuser(username, email, password, **extra_fields)

        return superuser


class LocalcosmosUser(ServerContentImageMixin, AbstractUser):

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    slug = models.SlugField(unique=True)

    details = models.JSONField(null=True, blank=True)
    
    follows = models.ManyToManyField('self', blank=True)

    is_banned = models.BooleanField(default=False)

    objects = LocalcosmosUserManager()


    # there is a bug in django for Dataset.user.on_delete=models.SET_NULL (django 3.1)
    # anonymize the datasets here instead of letting django call SET_NULL
    def anonymize_datasets(self):
        from localcosmos_server.datasets.models import Dataset, DatasetImages
        datasets = Dataset.objects.filter(user=self)
        for dataset in datasets:

            # delete all images of this dataset, also remove it from disk
            # this is due to legal implications
            images = DatasetImages.objects.filter(dataset=dataset)

            dataset.user = None

        Dataset.objects.bulk_update(datasets, ['user'])

    def dataset_count(self):
        from localcosmos_server.datasets.models import Dataset
        return Dataset.objects.filter(user=self).count()

    # do not alter the delete method
    def delete(self, using=None, keep_parents=False):

        if settings.LOCALCOSMOS_PRIVATE == True:
            self.anonymize_datasets()
            super().delete(using=using, keep_parents=keep_parents)
        else:
            # localcosmos.org uses django-tenants
            from django_tenants.utils import schema_context, get_tenant_model
            Tenant = get_tenant_model()
            
            user_id = self.pk

            # using transactions because multiple schemas can refer to the same
            # user ID as FK references!
            with transaction.atomic():

                deleted = False
                
                # delete user and all of its data across tenants
                for tenant in Tenant.objects.all().exclude(schema_name='public'):
                    with schema_context(tenant.schema_name):

                        self.anonymize_datasets()
                        
                        super().delete(using=using, keep_parents=keep_parents)
                        # reassign the ID because delete() sets it to None
                        self.pk = user_id

                        deleted = True

                
                if deleted == False:
                    
                    # deleting from public schema is not necessary, it happens on the first schema-specific deletion
                    with schema_context('public'):
                        super().delete()
            

    class Meta:
        unique_together = ('email',)


'''
    CLIENTS // DEVICES
    - a client can be used by several users, eg if one logs out and another one logs in on a device
    - the client/user combination is unique
'''
'''
    platform is sent by the platform the app was used on
'''
class UserClients(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=255)
    platform = models.CharField(max_length=255)

    class Meta:
        unique_together = ('user', 'client_id')


'''
    App
    - an App is a webapp which is loaded by an index.html file
    - Apps are served by nginx or apache
'''
class AppManager(models.Manager):

    def create(self, name, primary_language, uid, **kwargs):

        app = self.model(
            name=name,
            primary_language=primary_language,
            uid=uid,
            **kwargs
        )

        app.save()

        return app
    
        
class App(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # this is the app specific subdomain on localcosmos.org/ the unzip folder on lc private
    # unique across all tenants
    uid = models.CharField(max_length=255, unique=True, editable=False)

    # automatically download app updates when you click "publish" on localcosmos.org
    # this feature is not implemented yet
    auto_update = models.BooleanField(default=True)

    primary_language = models.CharField(max_length=15)
    name = models.CharField(max_length=255)

    # the url this app is served at according to your nginx/apache setup
    # online content uses this to load a preview on the LC private installation
    url = models.URLField(null=True)

    # url for downloading the currently released apk
    apk_url = models.URLField(null=True)
    
    # url for downloading the currently released aab
    aab_url = models.URLField(null=True)

    # url for downloading the currently released ipa
    # as of 2019 this does not make any sense, because apple does not support ad-hoc installations
    # for companies < 100 employees
    ipa_url = models.URLField(null=True)

    # COMMERCIAL ONLY
    # url for downloading the current webapp for installing on the private server
    pwa_zip_url = models.URLField(null=True)

    # COMMERCIAL ONLY ?
    # for version comparisons, version of the app in the appkit, version of apk, ipa and webapp might differ
    published_version = models.IntegerField(null=True)

    # an asbolute path on disk to a folder containing a www folder with static index.html file
    # online content uses published_version_path if LOCALCOSMOS_PRIVATE == True
    # online content reads templates and config files from disk
    # usually, published_version_path is settings.LOCALCOSMOS_APPS_ROOT/{App.uid}/published/www/
    # make sure published_version_path is served by your nginx/apache
    published_version_path = models.CharField(max_length=255, null=True)

    # COMMERCIAL ONLY
    # an asbolute path on disk to a folder containing a www folder with static index.html file
    # online content uses preview_version_path if LOCALCOSMOS_PRIVATE == False
    # online content reads templates and config files from disk
    # usually, preview_version_path is settings.LOCALCOSMOS_APPS_ROOT/{App.uid}/preview/www/
    # make sure preview_version_path is served by your nginx/apache
    preview_version_path = models.CharField(max_length=255, null=True)

    # COMMERCIAL ONLY
    # an asbolute path on disk to a folder containing a www folder with static index.html file
    # usually, review_version_path is settings.LOCALCOSMOS_APPS_ROOT/{App.uid}/review/www/
    # make sure review_version_path is served by your nginx/apache
    # review_version_path is used by the localcosmos_server api
    review_version_path = models.CharField(max_length=255, null=True)
    

    objects = AppManager()

    # path where the user uploads app stuff to
    # eg onlince content templates
    @property
    def media_base_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.uid)

    @property
    def media_base_url(self):
        return os.path.join(settings.MEDIA_URL, self.uid)


    def get_url(self):
        if settings.LOCALCOSMOS_PRIVATE == True:
            return self.url

        # commercial installation uses subdomains
        from django_tenants.utils import get_tenant_domain_model
        Domain = get_tenant_domain_model()
        
        domain = Domain.objects.get(app=self)
        return domain.domain

    def get_admin_url(self):
        if settings.LOCALCOSMOS_PRIVATE == True:
            return reverse('appadmin:home', kwargs={'app_uid':self.uid})

        # commercial installation uses subdomains
        from django_tenants.utils import get_tenant_domain_model
        Domain = get_tenant_domain_model()
        
        domain = Domain.objects.get(app=self)
        path = reverse('appadmin:home', kwargs={'app_uid':self.uid}, urlconf='localcosmos_server.urls')

        url = '{0}{1}'.format(domain.domain, path)
        return url

    # preview is used by online content on the commercial installation only
    # on lc private, preview url is the live url
    def get_preview_url(self):
        if settings.LOCALCOSMOS_PRIVATE == True:
            return self.url

        from django_tenants.utils import get_tenant_domain_model
        Domain = get_tenant_domain_model()
        
        domain = Domain.objects.filter(tenant__schema_name='public').first()

        return '{0}.preview.{1}/'.format(self.uid, domain.domain)


    def get_installed_app_path(self, app_state):

        if settings.LOCALCOSMOS_PRIVATE == True:
            app_state = 'published'

        if app_state == 'published':
            root = self.published_version_path

            # on the first build, there is no published_version_path, but only a review_version_path
            # the "review apk" is exactly the same as the later "published apk",
            # so fall back to review settings if no published settings are available
            if root == None and settings.LOCALCOSMOS_PRIVATE == False:
                root = self.review_version_path

        elif app_state == 'preview':
            root = self.preview_version_path
            
            if not root:
                root = os.path.join(settings.LOCALCOSMOS_APPS_ROOT, self.uid, 'preview', 'www')      

        elif app_state == 'review':
            root= self.review_version_path

        else:
            raise ValueError('Invalid app_state: {0}'.format(app_state))
        
        return root

    
    # read app settings from disk, template_content
    # located at /www/settings.json, createb by AppPreviewBuilder or AppReleaseBuilder
    # app_state=='preview' or app_state=='review' are for commercial installation only
    def get_settings(self, app_state='preview'):

        root = self.get_installed_app_path(app_state)
            
        settings_json_path = os.path.join(root, 'settings.json')

        with open(settings_json_path, 'r') as settings_file:
            app_settings = json.loads(settings_file.read())

        return app_settings
    
    
    def get_licence_registry(self, app_state='preview'):
        
        if settings.LOCALCOSMOS_PRIVATE == True:
            app_state = 'published'

        if app_state == 'published':
            root = self.get_installed_app_path(app_state)
            
            registry_json_path = os.path.join(root, 'localcosmos/licence_registry.json')

            with open(registry_json_path, 'r') as registry_file:
                app_settings = json.loads(registry_file.read())

            return app_settings

        return {}


    # read app features from disk, only published apps
    # app_state=='preview' or app_state=='review' are for commercial installation only
    # used eg by AppTaxonSearch.py
    def get_features(self, app_state='preview'):

        if settings.LOCALCOSMOS_PRIVATE == False and app_state == 'preview':
            features = {}

        else:
            root = self.get_installed_app_path(app_state)
            
            features_json_path = os.path.join(root, 'localcosmos', 'features.json')

            with open(features_json_path, 'r') as features_file:
                features = json.loads(features_file.read())

        return features


    # privacyPolicy and legalNotice are required
    def get_frontend(self):
        app_state = None
        frontend = None

        if self.published_version_path:
            app_state = 'published'

        elif self.review_version_path:
            app_state = 'review'
        
        if app_state != None:
            app_root = self.get_installed_app_path(app_state=app_state)

            features = self.get_features(app_state=app_state)

            frontend_relative_path = features['Frontend']['path']
            frontend_path = os.path.join(app_root, frontend_relative_path.lstrip('/'))

            with open(frontend_path, 'r') as frontend_file:
                frontend = json.loads(frontend_file.read())
        
        return frontend
        

    def get_legal_frontend_text(self, key):

        text = ''

        frontend = self.get_frontend()
        if frontend:
            text = frontend['userContent']['texts'][key]
        
        return text


    def get_legal_notice(self):
        return self.get_legal_frontend_text('legalNotice')


    def get_privacy_policy(self):
        return self.get_legal_frontend_text('privacyPolicy')


    @property
    def logo_url(self):
        app_state = 'review'
        features = self.get_features(app_state=app_state)
        if not features:
            app_state = 'published'
            features = self.get_features(app_state=app_state)

        if features:
            frontend_path = features['Frontend']['path'].lstrip('/')
            installed_app_path = self.get_installed_app_path(app_state)
            frontend_filepath = os.path.join(installed_app_path, frontend_path)

            if os.path.isfile(frontend_filepath):
                
                with open(frontend_filepath, 'r') as frontend_file:
                    frontend = json.loads(frontend_file.read())
                    logo = frontend['userContent']['images'].get('logo', None)

                    if logo:
                        return logo['imageUrl']['1x'].lstrip('/')

        return None


    def languages(self):
        languages = [self.primary_language]
        secondary_languages = SecondaryAppLanguages.objects.filter(app=self).values_list('language_code', flat=True)
        languages += secondary_languages
        return languages
    
    def secondary_languages(self):
        return SecondaryAppLanguages.objects.filter(app=self).values_list('language_code', flat=True)


    # only published app
    def get_locale(self, key, language):
        relpath = 'locales/{0}/plain.json'.format(language)
        locale_path = os.path.join(self.published_version_path, relpath)

        if os.path.isfile(locale_path):
            with open(locale_path, 'r') as f:
                locale = json.loads(f.read())
                return locale.get(key, None)

        return None
    

    def get_vernacular(self, taxon, language):

        app_settings = self.get_settings(app_state='published')
        features = self.get_features(app_state='published')

        vernacular_name = None

        if language not in features['BackboneTaxonomy']['vernacularLookup']:
            language = app_settings['PRIMARY_LANGUAGE']
        
        if language in features['BackboneTaxonomy']['vernacularLookup']:
            relpath = features['BackboneTaxonomy']['vernacularLookup'][language].lstrip('/')

            vernacular_lookup_path = os.path.join(self.published_version_path, relpath)

            if os.path.isfile(vernacular_lookup_path):
                with open(vernacular_lookup_path, 'r') as f:
                    vernacular_lookup = json.loads(f.read())
                    vernacular_names = vernacular_lookup.get(taxon.name_uuid, None)

                    if vernacular_names:
                        return vernacular_names['primary']
                
        return vernacular_name


    # LC PRIVATE: remove all contents from disk
    def delete(self, *args, **kwargs):
        app_folder = os.path.join(settings.LOCALCOSMOS_APPS_ROOT, self.uid)
        super().delete(*args, **kwargs)
        
        if os.path.isdir(app_folder):
            shutil.rmtree(app_folder)
        

    def __str__(self):
        return self.name


class SecondaryAppLanguages(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    language_code = models.CharField(max_length=15)

    class Meta:
        unique_together = ('app', 'language_code')



APP_USER_ROLES = (
    ('admin',_('admin')), # can do everything
    ('expert',_('expert')), # can validate datasets (Expert Review)
)
class AppUserRole(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    role = models.CharField(max_length=60, choices=APP_USER_ROLES)

    def __str__(self):
        return '%s' % (self.role)

    class Meta:
        unique_together = ('user', 'app')
    

'''
    Taxonomic Restrictions
'''
TAXONOMIC_RESTRICTION_TYPES = (
    ('exists', _('exists')),
    ('required', _('required')),
    ('optional', _('optional')),
)
class TaxonomicRestrictionBase(ModelWithRequiredTaxon):

    LazyTaxonClass = LazyAppTaxon

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField()
    content = GenericForeignKey('content_type', 'object_id')

    restriction_type = models.CharField(max_length=100, choices=TAXONOMIC_RESTRICTION_TYPES, default='exists')
    
    def serialize(self):
        return {
            'taxonSource' : self.taxon_source,
            'taxonLatname' : self.taxon_latname,
            'taxonAuthor' : self.taxon_author,
            'nameUuid' : self.name_uuid,
            'taxonNuid' : self.taxon_nuid,
            'restrictionType' : self.restriction_type,
        }

    def __str__(self):
        return self.taxon_latname

    class Meta:
        abstract = True
        unique_together = ('content_type', 'object_id', 'taxon_latname', 'taxon_author')


class TaxonomicRestrictionManager(models.Manager):

    def get_for_taxon_branch(self, object_model, lazy_taxon):

        content_type = ContentType.objects.get_for_model(object_model)

        taxon_source = lazy_taxon.taxon_source
        nuid = lazy_taxon.taxon_nuid

        taxon_nuids = []

        while len(nuid) >= 3:
            
            taxon_nuids.append(nuid)
            nuid = nuid[:-3]

        queryset =  self.all().filter(content_type=content_type, taxon_source=taxon_source,
            taxon_nuid__in=taxon_nuids)

        return queryset


    def get_for_taxon(self, object_model, lazy_taxon):

        content_type = ContentType.objects.get_for_model(object_model)

        taxon_source = lazy_taxon.taxon_source
        taxon_nuid = lazy_taxon.taxon_nuid

        queryset =  self.all().filter(content_type=content_type, taxon_source=taxon_source,
            taxon_nuid=taxon_nuid)

        return queryset


class TaxonomicRestriction(TaxonomicRestrictionBase):
    
    objects = TaxonomicRestrictionManager()


def get_image_store_path(instance, filename):
    blankname, ext = os.path.splitext(filename)

    md5 = instance.md5

    if not md5:
        md5 = generate_md5(instance.source_image)
        #hashlib.md5(instance.source_image.read()).hexdigest()
        # this line is extremely required. do not delete it. otherwise the file will not be read correctly
        # this now done by generate_md5
        #instance.source_image.seek(0)

    new_filename = '{0}{1}'.format(md5, ext)
    path = '/'.join(['localcosmos-server', 'imagestore', '{0}'.format(instance.uploaded_by.pk),
                     new_filename])
    return path


class ImageStoreAbstract(ModelWithTaxon):

    LazyTaxonClass = LazyAppTaxon

    # null Foreignkey means the user does not exist anymore
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    
    md5 = models.CharField(max_length=255)

    # enables on delete cascade
    licences = GenericRelation(ContentLicenceRegistry)

    class Meta:
        abstract=True


class ServerImageStore(ImageStoreAbstract):
    
    source_image = models.ImageField(upload_to=get_image_store_path)


class ContentImageAbstract(models.Model):

    crop_parameters = models.TextField(null=True)

    # for things like arrows/vectors on the image
    # arrows are stored as [{"type" : "arrow" , "initialPoint": {x:1, y:1}, "terminalPoint": {x:2,y:2}, color: string}]
    features = models.JSONField(null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField()
    content = GenericForeignKey('content_type', 'object_id')

    # a content can have different images
    # eg an image of type 'background' and an image of type 'logo'
    image_type = models.CharField(max_length=100, default='image')

    position = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    # caption, text below image
    text = models.CharField(max_length=355, null=True)

    # flag if a translation is needed
    requires_translation = models.BooleanField(
        default=False)  # not all images require a translation
    
    # SEO
    title = models.CharField(max_length=355, null=True, blank=True)
    alt_text = models.TextField(null=True, blank=True)
    
    
    def save(self, *args, **kwargs):
        
        if self.is_primary == True:
            
            old_primaries = self.__class__.objects.filter(content_type=self.content_type, object_id=self.object_id, image_type=self.image_type, is_primary=True)
            
            if self.pk:
                old_primaries.exclude(pk=self.pk)
                
            old_primaries.update(is_primary=False)
        
        super().save(*args, **kwargs)


    class Meta:
        abstract=True


import hashlib
from PIL import Image
class ContentImageProcessing:

    def get_thumb_filename(self, size=400):

        if self.image_store.source_image:
            filename = os.path.basename(self.image_store.source_image.path)
            blankname, ext = os.path.splitext(filename)

            suffix = 'uncropped'
            if self.crop_parameters:
                suffix = hashlib.md5(
                    self.crop_parameters.encode('utf-8')).hexdigest()

            feature_suffix = 'nofeatures'
            if self.features:
                features_str = json.dumps(self.features)
                feature_suffix = hashlib.md5(
                    features_str.encode('utf-8')).hexdigest()

            thumbname = '{0}-{1}-{2}-{3}{4}'.format(
                blankname, suffix, feature_suffix, size, ext)
            return thumbname

        else:
            return 'noimage.png'


    def plot_features(self, pil_image):
        raise NotImplementedError('Plotting Features not supported by LC Server')

    # apply features and cropping, return pil image
    # original_image has to be Pil.Image instance
    # CASE 1: crop parameters given.
    #   - make a canvas according to crop_parameters.width and crop_parameters.height
    #
    # CASE 2: no crop parameters given
    #   1. apply features
    #   2. thumbnail
    def get_in_memory_processed_image(self, original_image, size):

        # scale the image to match size
        original_width, original_height = original_image.size

        larger_original_side = max(original_width, original_height)
        if larger_original_side < size:
            size = larger_original_side

        # fill color for the background, if the selection expands the original image
        fill_color = (255, 255, 255, 255)

        # offset of the image on the canvas
        offset_x = 0
        offset_y = 0

        if self.crop_parameters:

            square_size = max(original_width, original_height)
            offset_x = int((square_size - original_width) / 2)
            offset_y = int((square_size - original_height) / 2)
            width = size
            height = size

            canvas = Image.new('RGBA', (square_size, square_size), fill_color)
            canvas.paste(original_image, (offset_x, offset_y))

        else:

            # define width and height
            width = size
            scaling_factor = original_width / size
            height = original_height * scaling_factor

            canvas = Image.new(
                'RGBA', (original_width, original_height), fill_color)
            canvas.paste(original_image, (offset_x, offset_y))

        # plot features and creator name
        # matplotlib is awfully slow - only use it if absolutely necessary
        if self.features:
            image_source = self.plot_features(canvas)
            canvas_with_features = Image.open(image_source)
        else:
            canvas_with_features = canvas

        # ATTENTION: crop_parameters are relative to the top-left corner of the original image
        # -> make them relative to the top left corner of square
        if self.crop_parameters:
            # {"x":253,"y":24,"width":454,"height":454,"rotate":0,"scaleX":1,"scaleY":1}
            crop_parameters = json.loads(self.crop_parameters)

            # first crop, then resize
            # box: (left, top, right, bottom)
            box = (
                crop_parameters['x'] + offset_x,
                crop_parameters['y'] + offset_y,
                crop_parameters['x'] + offset_x + crop_parameters['width'],
                crop_parameters['y'] + offset_y + crop_parameters['height'],
            )

            cropped_canvas = canvas_with_features.crop(box)

        else:
            cropped_canvas = canvas_with_features

        cropped_canvas.thumbnail([width, height], Image.LANCZOS)

        if original_image.format != 'PNG':
            cropped_canvas = cropped_canvas.convert('RGB')

        return cropped_canvas


    def image_url(self, size=400, force=False):

        if self.image_store.source_image.path.endswith('.svg'):
            thumburl = self.image_store.source_image.url

        else:

            image_path = self.image_store.source_image.path
            folder_path = os.path.dirname(image_path)

            thumbname = self.get_thumb_filename(size)

            thumbfolder = os.path.join(folder_path, 'thumbnails')
            if not os.path.isdir(thumbfolder):
                os.makedirs(thumbfolder)

            thumbpath = os.path.join(thumbfolder, thumbname)

            if not os.path.isfile(thumbpath) or force == True:

                original_image = Image.open(self.image_store.source_image.path)

                processed_image = self.get_in_memory_processed_image(
                    original_image, size)

                processed_image.save(thumbpath, original_image.format)

            thumburl = os.path.join(os.path.dirname(
                self.image_store.source_image.url), 'thumbnails', thumbname)

        return thumburl
    
    
    def image_urls(self, image_sizes=['regular', 'large']):
        
        image_urls = {}
        
        for image_sizes_key in image_sizes:
            for size_name, size in IMAGE_SIZES[image_sizes_key].items():
                
                image_url = self.image_url(size)
                
                image_urls[size_name] = image_url
        
        return image_urls


    def srcset(self, request=None, force=False):
        
        srcset = {
            '1x' : self.image_url(size=200, force=force),
            '2x' : self.image_url(size=400, force=force),
        }

        if request:

            host = request.get_host()

            for key, url in srcset.items():
                absolute_url = '{0}://{1}{2}'.format(request.scheme, host, url)
                srcset[key] = absolute_url
        

        return srcset



class ServerContentImage(ContentImageProcessing, ContentImageAbstract):

    image_store = models.ForeignKey(ServerImageStore, on_delete=models.CASCADE)
    

'''--------------------------------------------------------------------------------------------------------------
    SEO
    - seo parameters for pages (not images)
    - as it should be reusable for multiple models without modifying the database schema of those models
      GenericRelation is used instead of ForeignKey
--------------------------------------------------------------------------------------------------------------'''
class SeoParametersAbstract(models.Model):

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    title = models.CharField(max_length=355, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title or 'SEO Parameters'} for {self.content_object}"
    
    class Meta:
        unique_together = ('content_type', 'object_id')
        verbose_name = "SEO Parameter"
        verbose_name_plural = "SEO Parameters"
        abstract = True


class ServerSeoParameters(SeoParametersAbstract):
    pass


'''--------------------------------------------------------------------------------------------------------------
    EXTERNAL MEDIA
--------------------------------------------------------------------------------------------------------------'''
EXTERNAL_MEDIA_TYPES = (
    ('image', _('Image')),
    ('youtube', _('Youtube')),
    ('vimeo', _('Vimeo')),
    ('mp3', _('MP3 File')),
    ('wav', _('WAV File')),
    ('pdf', _('PDF Document')),
    ('website', _('Website')),
    ('file', _('File')), # generic file, download links
)

EXTERNAL_MEDIA_CATEGORIES = (
    ('video', _('Video')),
    ('audio', _('Audio')),
    ('document', _('Document')),
)

# Mapping from media types to categories
# Only map types that have meaningful categories (multiple subtypes)
MEDIA_TYPE_TO_CATEGORY = {
    'youtube': 'video',
    'vimeo': 'video',
    'mp3': 'audio',
    'wav': 'audio',
    'pdf': 'document',
    # image and website don't map to categories - they stand alone
}

class ExternalMediaManager(models.Manager):
    
    def needs_checking(self, days=30):
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(
            Q(last_checked_at__lt=cutoff) | Q(last_checked_at__isnull=True)
        )
        
class ExternalMediaAbstract(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=255)
    caption = models.CharField(max_length=255, null=True, blank=True)
    alt_text = models.CharField(max_length=355, null=True, blank=True)
    media_type = models.CharField(max_length=50, choices=EXTERNAL_MEDIA_TYPES)
    media_category = models.CharField(max_length=50, choices=EXTERNAL_MEDIA_CATEGORIES, null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    licence = models.TextField(null=True, blank=True)
    position = models.IntegerField(default=0)
    file_size = models.BigIntegerField(null=True, blank=True, help_text=_('File size in bytes'))
    last_checked_at = models.DateTimeField(null=True, blank=True)
    is_accessible = models.BooleanField(default=True)

    objects = ExternalMediaManager()
    
    def __str__(self):
        return f"{self.title or self.url} ({self.media_type})"
    
    def save(self, *args, **kwargs):
        # Auto-fill media_category based on media_type if not already set
        # Only set category if the media_type has meaningful categorization
        if not self.media_category and self.media_type:
            self.media_category = MEDIA_TYPE_TO_CATEGORY.get(self.media_type)
        
        # Check if this is a new object or if URL has changed
        url_changed = False
        if self.pk is None:  # New object
            url_changed = True
        else:
            # Check if URL changed
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                url_changed = old_instance.url != self.url
            except self.__class__.DoesNotExist:
                url_changed = True
        
        # If URL changed and we don't have file size, try to fetch it
        if url_changed and not self.file_size and self.url:
            self.update_file_size(save=False)
            
        super().save(*args, **kwargs)
    
    def get_media_category_display_name(self):
        """Get the human-readable category name"""
        if self.media_category:
            category_dict = dict(EXTERNAL_MEDIA_CATEGORIES)
            return category_dict.get(self.media_category, self.media_category)
        else:
            # For standalone types, return the media type display name
            media_type_dict = dict(EXTERNAL_MEDIA_TYPES)
            return media_type_dict.get(self.media_type, self.media_type)
    
    def get_file_size_display(self):
        """Return human-readable file size"""
        if not self.file_size:
            return _('Unknown size')
        
        # Convert bytes to human readable format
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def is_large_file(self, threshold_mb=5):
        """Check if file is considered large (default: 5MB)"""
        if not self.file_size:
            return False
        threshold_bytes = threshold_mb * 1024 * 1024
        return self.file_size > threshold_bytes
    
    def fetch_file_size(self):
        """Fetch file size from URL without downloading the entire file"""
        
        if not self.url:
            return None
            
        try:
            # For YouTube and other platform URLs, size determination is complex
            if self.media_type == 'youtube':
                # YouTube file sizes vary by quality, can't determine easily
                return None
            
            # For direct file URLs, use HEAD request to get Content-Length
            response = requests.head(self.url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                content_length = response.headers.get('Content-Length')
                if content_length:
                    return int(content_length)
            
            # If HEAD doesn't work, try GET with range header
            headers = {'Range': 'bytes=0-0'}
            response = requests.get(self.url, headers=headers, timeout=10, stream=True)
            
            if response.status_code == 206:  # Partial Content
                content_range = response.headers.get('Content-Range')
                if content_range:
                    # Content-Range: bytes 0-0/12345 (total size is 12345)
                    total_size = content_range.split('/')[-1]
                    if total_size.isdigit():
                        return int(total_size)
                        
        except Exception as e:
            # Log the error in production
            # logger.warning(f"Could not fetch file size for {self.url}: {e}")
            pass
            
        return None
    
    def update_file_size(self, save=True):
        """Update the file_size field by fetching it from the URL"""
        size = self.fetch_file_size()
        if size is not None:
            self.file_size = size
            if save:
                self.save(update_fields=['file_size'])
            return True
        return False
    
    def check_url_and_update_metadata(self):
        """Check URL accessibility and update metadata including file size"""

        
        if not self.url:
            return False
            
        try:
            # Update file size
            size_updated = self.update_file_size(save=False)
            
            # Check accessibility
            response = requests.head(self.url, timeout=10, allow_redirects=True)
            self.is_accessible = response.status_code == 200
            self.last_checked_at = timezone.now()
            
            # Save all changes at once
            update_fields = ['is_accessible', 'last_checked_at']
            if size_updated:
                update_fields.append('file_size')
                
            self.save(update_fields=update_fields)
            return True
            
        except Exception as e:
            self.is_accessible = False
            self.last_checked_at = timezone.now()
            self.save(update_fields=['is_accessible', 'last_checked_at'])
            return False

    class Meta:
        verbose_name = _('External Media')
        verbose_name_plural = _('External Media')
        ordering = ['position', 'id']
        unique_together = ('content_type', 'object_id', 'url')
        abstract = True


class ServerExternalMedia(ExternalMediaAbstract):
    pass