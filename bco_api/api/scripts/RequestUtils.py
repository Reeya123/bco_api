# Utilities
from . import JsonUtils

# For checking request formats
from django.conf import settings

# Request-specific methods
from .method_specific.POST_validate_payload_against_schema import POST_validate_payload_against_schema


class RequestUtils:

    # Check for a valid template.
    def check_request_templates(self, method, request):

        # Arguments

        # method: one of DELETE, GET, PATCH, POST
        # request: the request itself

        # We need to check for a valid template.

        # Define the request templates.
        request_templates = settings.REQUEST_TEMPLATES

        # Subset the templates to the ones for this request method.
        request_templates = request_templates[method]

        import json
        print('REQUEST')
        print(json.dumps(request, indent=4, sort_keys=True))
        print('REQUEST_TEMPLATES')
        print(json.dumps(request_templates, indent=4, sort_keys=True))
        print('========================')

        # Validate against the templates.
        return JsonUtils.JsonUtils().check_object_against_schema(object_pass=request, schema_pass=request_templates)

        '''
        # Go over each part of the request.
        for sub_request in request:

            # See if we even have a valid template associated with the request.
            if sub_request['template'] in request_templates[method]:

                # The template is defined, so now check that the request
                # actually matches this template.
                return JsonUtils.JsonUtils().check_object_against_schema(object_pass=request, schema_pass=request_templates[method][request['template']])

            else:

                # Return a template undefined error.
                return {'REQUEST_ERROR': 'Undefined template \'' + request['template'] + '\' for request method \'' + method + '\''}
        '''

    def process_request_templates(self, method, request):

        # Arguments

        # method: one of DELETE, GET, PATCH, POST
        # request: the raw request

        # Define the request templates.
        request_templates = settings.REQUEST_TEMPLATES

        # Subset the templates to the ones for this request method.
        request_templates = request_templates[method]

        # Define a dictionary to hold errors from individual templates.
        errors = {}

        # To avoid exec calls to functions (unsafe), we'll manually
        # enumerate the methods here.
        if 'POST_validate_payload_against_schema' in request:
            run_request = POST_validate_payload_against_schema(request['POST_validate_payload_against_schema'])

            # The operation went fine?
            if run_request is not None:
                errors['POST_validate_payload_against_schema'] = run_request

        # Did we have any errors?

        # Source: https://stackoverflow.com/questions/23177439/python-checking-if-a-dictionary-is-empty-doesnt-seem-to-work
        if bool(errors):
            return errors



