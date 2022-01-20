#!/usr/bin/env python3
"""Modify Draft Object

modify a draft object
"""
from pkgutil import ImpImporter
from django.http import request
from api.models import bco
from api.scripts.utilities import DbUtils
from api.scripts.utilities import UserUtils

# For writing objects to the database.
from django.contrib.auth.models import Group

from django.utils import timezone
from guardian.shortcuts import get_perms
from rest_framework import status
from rest_framework.response import Response

# Source: https://codeloop.org/django-rest-framework-course-for-beginners/

def POST_api_objects_drafts_modify(request):
    """ Modify Draft Object
    
    Take the bulk request and modify a draft object from it.
    """
    
    # import pdb;pdb.set_trace()
    db_utils = DbUtils.DbUtils()
    user = UserUtils.UserUtils().user_from_request(request = request)
    bulk_request = request.data['POST_api_objects_drafts_modify']
    px_perms = UserUtils.UserUtils().prefix_perms_for_user(
        flatten = True,
        user_object = user,
        specific_permission = ['add']
    )

    # Construct an array to return the objects.
    returning = []
    for creation_object in bulk_request:
        import pdb; pdb.set_trace()
        # Get the prefix for this draft.
        prefix = creation_object['object_id'].split('/')[-2].split('_')[0].upper()

        # Does the requestor have change permissions for
        # the *prefix*?

        # TODO: add permission setting view...

        #if 'change_' + prefix in px_perms:
        if 'add_' + prefix in px_perms:
        
            # The requestor has change permissions for
            # the prefix, but do they have object-level
            # change permissions?

            # This can be checked by seeing if the requestor
            # is the object owner OR they are a user with
            # object-level change permissions OR if they are in a 
            # group that has object-level change permissions.

            # To check these options, we need the actual object.
            if bco.objects.filter(object_id = creation_object['object_id']).exists():

                objected = bco.objects.get(
                    object_id = creation_object['object_id']
                )

                # We don't care where the view permission comes from,
                # be it a User permission or a Group permission.
                all_permissions = get_perms(
                    user,
                    objected
                )

                # TODO: add permission setting view...
                # if user.pk == object.owner_user or 'change_' + prefix in all_permissions:
                if user.username == objected.owner_user.username or 'add_' + prefix in all_permissions:
                    # Alex Coleman  7:34 PM
                    # Yeah I'm 99% sure that if statement is pointless. @Chris Armstrong may have had a reason for it but Idk what.


                    # # User does *NOT* have to be in the owner group!
                    # # to assign the object's group owner.
                    # if Group.objects.filter(
                    #     name = creation_object['owner_group'].lower()
                    # ).exists():
                    #
                    # Update the object.

                    # *** COMPLETELY OVERWRITES CONTENTS!!! ***
                    objected.contents = creation_object['contents']

                    # Set the update time.
                    objected.last_update = timezone.now()

                    # Save it.
                    objected.save()

                    # Update the request status.
                    returning.append(
                        db_utils.messages(
                            parameters = {
                                'object_id': creation_object['object_id']
                            }
                        )['200_update']
                    )

                    # else:

                    # Update the request status.
                    returning.append(
                        db_utils.messages(
                            parameters = {}
                        )['400_bad_request']
                    )
                
                else:

                    # Insufficient permissions.
                    returning.append(
                        db_utils.messages(
                            parameters = {}
                        )['403_insufficient_permissions']
                    )

            else:

                # Couldn't find the object.
                returning.append(
                    db_utils.messages(
                        parameters = {
                            'object_id': creation_object['object_id']
                        }
                    )
                )['404_object_id']
            
        else:
            
            # Update the request status.
            returning.append(
                db_utils.messages(
                    parameters = {
                        'prefix': prefix
                    }
                )['401_prefix_unauthorized']
            )

    # As this view is for a bulk operation, status 200
    # means that the request was successfully processed,
    # but NOT necessarily each item in the request.
    # For example, a table may not have been found for the first
    # requested draft.

    return Response(status = status.HTTP_200_OK, data = returning)
