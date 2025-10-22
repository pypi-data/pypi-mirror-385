from rest_framework import serializers

from localcosmos_server.template_content.models import (LocalizedTemplateContent, LocalizedNavigation,
    PUBLISHED_IMAGE_TYPE_PREFIX)

from content_licencing.models import ContentLicenceRegistry

from localcosmos_server.template_content.utils import get_component_image_type, get_published_image_type

# do not replace camelCase with underscore_case without adapting app_kit's ContentImageBuilder.build_licence
class LocalizedTemplateContentSerializer(serializers.ModelSerializer):

    title = serializers.SerializerMethodField()
    templateName = serializers.SerializerMethodField()
    templatePath = serializers.SerializerMethodField()
    
    version = serializers.SerializerMethodField()
    
    contents = serializers.SerializerMethodField()

    linkedTaxa = serializers.SerializerMethodField()
    linkedTaxonProfiles = serializers.SerializerMethodField()

    template_definition = None

    def get_from_definition(self, localized_template_content, key):
        template_definition = self.get_template_definition(localized_template_content)
        return template_definition[key]


    def get_template_definition(self, localized_template_content):
        preview = self.context.get('preview', True)
        if not self.template_definition:
            if preview == True:
                self.template_definition = localized_template_content.template_content.draft_template.definition
            else:
                self.template_definition = localized_template_content.template_content.template.definition
        return self.template_definition

    def get_title(self, localized_template_content):
        preview = self.context.get('preview', True)
        if preview == True:
            return localized_template_content.draft_title
        return localized_template_content.published_title

    def get_templateName(self, localized_template_content):
        return self.get_from_definition(localized_template_content, 'templateName')

    def get_version(self, localized_template_content):
        return self.get_from_definition(localized_template_content, 'version')

    def get_templatePath(self, localized_template_content):
        return self.get_from_definition(localized_template_content, 'templatePath')

    def get_image_data(self, content_definition, localized_template_content, image_type):

        preview = self.context.get('preview', True)

        if preview == False:
            image_type = get_published_image_type(image_type)

        if content_definition.get('allowMultiple', False) == True:
            content_images = localized_template_content.images(image_type=image_type)
            
            image_data = []
            for content_image in content_images:

                serializer = ContentImageSerializer(content_image)
                image_data.append(serializer.data)

            return image_data
        
        else:
            content_image = localized_template_content.image(image_type=image_type)

            if content_image:

                serializer = ContentImageSerializer(content_image)
                image_data = serializer.data
                return image_data

            return None
    
    def add_image_data_to_component(self, component_key, component, component_definition,
        localized_template_content):

        if component:
        
            component_uuid = component['uuid']

            for component_content_key, component_content_definition in component_definition['contents'].items():

                if component_content_definition['type'] == 'image':

                    image_type = get_component_image_type(component_key, component_uuid, component_content_key)

                    image_data = self.get_image_data(component_content_definition, localized_template_content, image_type)

                    component[component_content_key] = image_data
            
        return component


    def get_contents(self, localized_template_content):

        preview = self.context.get('preview', True)

        contents = {}

        if preview == True:
            if localized_template_content.draft_contents:
                contents = localized_template_content.draft_contents.copy()
        else:
            contents = localized_template_content.published_contents.copy()

        template_definition = self.get_template_definition(localized_template_content)

        primary_language = localized_template_content.template_content.app.primary_language
        primary_locale_template_content = localized_template_content.template_content.get_locale(primary_language)

        # add imageUrl to contents, according to the template definition
        for content_key, content_definition in template_definition['contents'].items():

            content = contents.get(content_key, None)

            if content_definition['type'] == 'image':

                image_type = content_key

                image_data = self.get_image_data(content_definition, primary_locale_template_content, image_type)
                contents[content_key] = image_data

            elif content_definition['type'] == 'component' and content != None:
                
                # content variable can be a list or component dict
                component_key = content_key

                if component_key in contents:
                    
                    if preview == True:
                        component_template = primary_locale_template_content.template_content.get_component_template(
                            component_key)
                    else:
                        component_template = primary_locale_template_content.template_content.get_published_component_template(
                            component_key)
                    
                    component_definition = component_template.definition

                    # one or more components?
                    if content_definition.get('allowMultiple', False) == True:

                        components = contents[component_key]

                        for component_index, component in enumerate(components, 0):  

                            component_with_image_data = self.add_image_data_to_component(component_key, component,
                                component_definition, localized_template_content)

                            content[component_index] = component_with_image_data
                        
                        contents[component_key] = content

                    else:
                        
                        component = contents[component_key]

                        component_with_image_data = self.add_image_data_to_component(component_key, component,
                            component_definition, localized_template_content)

                        contents[component_key] = component_with_image_data
            
            
            elif content_definition['type'] == 'stream' and content != None:
                
                stream_key = content_key

                if stream_key in contents:

                    stream_items = contents[stream_key]

                    for stream_item_index, stream_item in enumerate(stream_items, 0):
                        
                        component_template_name = stream_item['templateName']
                        
                        if preview == True:
                            component_template = primary_locale_template_content.template_content.get_component_template(
                                stream_key, component_template_name)
                        else:
                            component_template = primary_locale_template_content.template_content.get_published_component_template(
                                stream_key, component_template_name)
                            
                            
                        component_definition = component_template.definition

                        stream_item_with_image_data = self.add_image_data_to_component(stream_key, stream_item,
                            component_definition, localized_template_content)

                        stream_items[stream_item_index] = stream_item_with_image_data
                    
                    contents[stream_key] = stream_items

        return contents

    # hasTaxonProfile might be a good addition for the api. it is also present in the built version
    def get_linkedTaxa(self, localized_template_content):

        linked_taxa = []
        restrictions = localized_template_content.template_content.taxonomic_restrictions

        for restriction in restrictions.all():
            
            taxon = restriction.taxon
            taxon_data = {
                'taxonSource': taxon.taxon_source,
                'taxonLatname': taxon.taxon_latname,
                'taxonAuthor': taxon.taxon_author,
                'nameUuid': taxon.name_uuid,
                'taxonNuid': taxon.taxon_nuid,
            }
            linked_taxa.append(taxon_data)

        return linked_taxa
    
    # not implemented yet for the api. App Kits jsonbuilder has it already.
    def get_linkedTaxonProfiles(self, localized_template_content):
        return []


    class Meta:
        model = LocalizedTemplateContent
        fields = ['title', 'templateName', 'templatePath', 'version', 'contents', 'linkedTaxa', 'linkedTaxonProfiles']


# do not replace camelCase with underscore_case without adapting app_kit's ContentImageBuilder.build_licence
class ContentLicenceSerializer(serializers.ModelSerializer):

    licenceVersion = serializers.CharField(source='licence_version')
    creatorName = serializers.CharField(source='creator_name')
    creatorLink = serializers.CharField(source='creator_link')
    sourceLink = serializers.CharField(source='source_link')

    class Meta:
        model = ContentLicenceRegistry
        fields = ('licence', 'licenceVersion', 'creatorName', 'creatorLink', 'sourceLink')

# do not replace imageUrl with image_url without adapting app_kit's ContentImageBuilder.build_licence
class ContentImageSerializer(serializers.Serializer):
    
    imageUrl = serializers.SerializerMethodField()
    licence = serializers.SerializerMethodField()

    def get_imageUrl(self, content_image):
        return content_image.image_urls()

    def get_licence(self, content_image):

        image_store = content_image.image_store
        licence = image_store.licences.first()

        serializer = ContentLicenceSerializer(licence)

        return serializer.data
    
    
class LocalizedNavigationSerializer(serializers.ModelSerializer):
    
    navigation = serializers.SerializerMethodField()
    
    def get_navigation(self, localized_navigation):
        preview = self.context.get('preview', True)
        
        if preview == True:
            return localized_navigation.serialize()

        return localized_navigation.published_navigation
    
    class Meta:
        model = LocalizedNavigation
        fields = ('navigation',)
        
