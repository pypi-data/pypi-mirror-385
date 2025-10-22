def get_component_image_type(component_key, component_uuid, content_key):
    image_key = '{0}:{1}:{2}'.format(component_key, component_uuid, content_key)
    return image_key

PUBLISHED_IMAGE_TYPE_PREFIX = 'published-'
def get_published_image_type(image_type):
    return '{0}{1}'.format(PUBLISHED_IMAGE_TYPE_PREFIX, image_type)

def get_frontend_specific_url(app_settings, ltc):
    slug = ltc.slug

    template = ltc.template_content.draft_template
    template_name = template.definition['templateName']

    template_url = app_settings['templateContent']['urlPattern'].replace('{slug}', slug).replace('{templateName}', template_name)
    return template_url

def get_preview_text(component_template, instance):

    preview_text = None

    if 'identifierContent' in component_template.definition:
        identifier_key = component_template.definition['identifierContent']
        preview_text = instance.get(identifier_key, None)

        if isinstance(preview_text, dict):
            preview_text = preview_text.get('title', None)
            
    if not preview_text:
        preview_text = component_template.definition['templateName']

    
    return preview_text