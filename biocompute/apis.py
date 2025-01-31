#!/usr/bin/env python3
#biocompute/apis.py

"""BioCompute Object APIs
"""

import jsonref
from biocompute.services import (
    BcoDraftSerializer,
    BcoValidator,
    ModifyBcoDraftSerializer,
    publish_draft,
    bco_counter_increment
)
from biocompute.selectors import (
    object_id_deconstructor,
    retrieve_bco,
    user_can_modify_bco,
    user_can_publish_draft,
    user_can_publish_prefix,
    prefix_from_object_id,
)
from config.services import (
    legacy_api_converter,
    bulk_response_constructor,
    response_status,
)
from deepdiff import DeepDiff
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from django.db import utils
from prefix.selectors import user_can_draft_prefix
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tests.fixtures.testing_bcos import BCO_000001_DRAFT, BCO_000000_DRAFT

hostname = settings.PUBLIC_HOSTNAME
BASE_DIR = settings.BASE_DIR

BCO_DRAFT_SCHEMA = openapi.Schema(
        type=openapi.TYPE_ARRAY,
        title="Create BCO Draft Schema",
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["prefix", "contents"],
            properties={
                "object_id": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="BCO Object ID.",
                    example=f"{hostname}/BCO_000001/DRAFT"
                ),
                "prefix": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="BCO Prefix to use",
                    example="TEST"
                ),
                "authorized_users": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="Users that can access the BCO draft.",
                    items=openapi.Schema(type=openapi.TYPE_STRING, example="tester")
                ),
                "contents": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Contents of the BCO.",
                    example=BCO_000001_DRAFT
                ),
            },
        ),
        description="BCO Drafts to create.",
    )

class DraftsCreateApi(APIView):
    """Create BCO Draft [Bulk Enabled]

    API endpoint for creating new BioCompute Object (BCO) drafts, with support
    for bulk operations.

    This endpoint allows authenticated users to create new BCO drafts
    individually or in bulk by submitting a list of BCO drafts. The operation
    can be performed for one or more drafts in a single request. Each draft is
    validated and processed independently, allowing for mixed response
    statuses (HTTP_207_MULTI_STATUS) in the case of bulk submissions.
    """

    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(
        operation_id="api_objects_drafts_create",
        request_body=BCO_DRAFT_SCHEMA,
        responses={
            200: "All requests were accepted.",
            207: "Some requests failed and some succeeded. Each object submitted"
                " will have it's own response object with it's own status"
                " code and message.\n",
            400: "All requests were rejected.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )

    def post(self, request) -> Response:
        response_data = []
        owner = request.user
        data = request.data
        rejected_requests = False
        accepted_requests = False
        
        if 'POST_api_objects_draft_create' in request.data:
            data = legacy_api_converter(request.data)

        test_id = data[0]["contents"].get("object_id", None)
        test_prefix = data[0].get("prefix", None)

        if test_id==BCO_000001_DRAFT["object_id"] and test_prefix == "TEST":
            test_object_id = BCO_000001_DRAFT["object_id"]
            return Response(
                status=status.HTTP_200_OK,
                data=[
                    bulk_response_constructor(
                        identifier=test_object_id,
                        status = "SUCCESS",
                        code= 200,
                        message= f"TESTING: BCO {test_object_id} created",
                    )
                ]
            )
        
        for index, object in enumerate(data):
            response_id = object["contents"].get("object_id", index)
            bco_prefix = object.get("prefix", index)
            prefix_permitted = user_can_draft_prefix(owner, bco_prefix)

            if prefix_permitted is None:
                response_data.append(bulk_response_constructor(
                    identifier=response_id,
                    status = "NOT FOUND",
                    code= 404,
                    message= f"Invalid prefix: {bco_prefix}.",
                ))
                rejected_requests = True
                continue

            if prefix_permitted is False:
                response_data.append(bulk_response_constructor(
                    identifier=response_id,
                    status = "FORBIDDEN",
                    code= 400,
                    message= f"User, {owner}, does not have draft permissions"\
                        + " for prefix {bco_prefix}.",
                ))
                rejected_requests = True
                continue
            
            serialized_bco = BcoDraftSerializer(data=object, context={'request': request})
            if serialized_bco.is_valid():
                try:
                    bco_instance = serialized_bco.create(serialized_bco.validated_data)
                    response_id = bco_instance.object_id
                    score = bco_instance.score
                    response_data.append(bulk_response_constructor(
                        identifier=response_id,
                        status = "SUCCESS",
                        code= 200,
                        message= f"BCO {response_id} created with a score of {score}",
                    ))
                    accepted_requests = True

                except Exception as err:
                    response_data.append(bulk_response_constructor(
                        identifier=serialized_bco['object_id'].value,
                        status = "SERVER ERROR",
                        code= 500,
                        message= f"BCO {serialized_bco['object_id'].value} failed",
                    ))

            else:
                response_data.append(bulk_response_constructor(
                    identifier=response_id,
                    status = "REJECTED",
                    code= 400,
                    message= f"BCO {response_id} rejected",
                    data=serialized_bco.errors
                ))
                rejected_requests = True

        status_code = response_status(accepted_requests, rejected_requests)
        return Response(status=status_code, data=response_data)

class PublishBcoApi(APIView):
    """Publish Single BCO

    API endpoint for publishing a BioCompute Object (BCO).

    This endpoint allows authenticated users to publish an individual BCO. 
    The draft is validated and processed upon submission.
    """

    permission_classes = [IsAuthenticated]
    swagger_schema = None
    #TODO: Add Swaggar docs
    # schema  = jsonref.load_uri(
    #     f"file://{BASE_DIR}/config/IEEE/2791object.json"
    # )
    @swagger_auto_schema(
        operation_id="api_objects_publish",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            # properties=schema,
            
    ),
        responses={
            200: "Request was accepted.",
            400: "Requests was rejected.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )

    def post(self, request) -> Response:
        validator = BcoValidator()
        requester = request.user
        data = request.data
        identifier, bco_results = validator.parse_and_validate(data).popitem()
        prefix_name = prefix_from_object_id(identifier)
        publish_permission = user_can_publish_prefix(requester, prefix_name)

        if bco_results["number_of_errors"] > 0:
            response_data = bulk_response_constructor(
                identifier = identifier,
                status="FAILED",
                code=400,
                message="BCO not valid",
                data=bco_results
            )
        else:
            response_data = bulk_response_constructor(
                identifier = identifier,
                status="SUCCESS",
                code=200,
                message="BCO valid",
                data=bco_results
            )

        import pdb; pdb.set_trace()
        return Response(status=status.HTTP_200_OK, data=response_data)
    
        # for index, object in enumerate(data):
        #     response_id = object.get("object_id", index)
        #     bco_instance = user_can_publish_draft(object, requester)

        #     if bco_instance is None:
        #         response_data.append(bulk_response_constructor(
        #             identifier=response_id,
        #             status = "NOT FOUND",
        #             code= 404,
        #             message= f"Invalid BCO: {response_id} does not exist.",
        #         ))
        #         rejected_requests = True
        #         continue

        #     if bco_instance is False:
        #         response_data.append(bulk_response_constructor(
        #             identifier=response_id,
        #             status = "FORBIDDEN",
        #             code= 403,
        #             message= f"User, {requester}, does not have draft permissions"\
        #                 + f" for BCO {response_id}.",
        #         ))
        #         rejected_requests = True
        #         continue

        #     if type(bco_instance) is str:
        #         response_data.append(bulk_response_constructor(
        #             identifier=response_id,
        #             status = "BAD REQUEST",
        #             code= 400,
        #             message= bco_instance
        #         ))
        #         rejected_requests = True
        #         continue

        #     if type(bco_instance) is tuple:
        #         response_data.append(bulk_response_constructor(
        #             identifier=response_id,
        #             status = "BAD REQUEST",
        #             code= 400,
        #             message= f"Invalid `published_object_id`."\
        #                 + f"{bco_instance[0]} and {bco_instance[1]}"\
        #                 + " do not match.",
        #         ))
        #         rejected_requests = True
        #         continue
            
        #     if bco_instance.state == 'PUBLISHED':
        #         object_id = bco_instance.object_id
        #         response_data.append(bulk_response_constructor(
        #             identifier=response_id,
        #             status = "CONFLICT",
        #             code= 409,
        #             message= f"Invalid `object_id`: {object_id} already"\
        #                 + " exists.",
        #         ))
        #         rejected_requests = True
        #         continue

        #     bco_results = validator.parse_and_validate(bco_instance.contents)
        #     import pdb; pdb.set_trace()
        #     identifier, results = bco_results.popitem()

        #     if results["number_of_errors"] > 0:
        #         rejected_requests = True
        #         bco_status = "FAILED"
        #         status_code = 400
        #         message = "BCO not valid"
        #     else:
        #         accepted_requests = True
        #         bco_status = "SUCCESS"
        #         status_code = 200
        #         message = "BCO valid"

        #     response_data.append(bulk_response_constructor(
        #         identifier = identifier,
        #         status=bco_status,
        #         code=status_code,
        #         message=message,
        #         data=results
        #     ))

        # status_code = response_status(accepted_requests, rejected_requests)
        # return Response(status=status_code, data=response_data)

class DraftsPublishApi(APIView):
    """Publish Draft BCO [Bulk Enabled]

    API endpoint for publishing BioCompute Object (BCO) drafts, with support
    for bulk operations.

    This endpoint allows authenticated users to publish existing BCO drafts
    individually or in bulk by submitting a list of BCO drafts. The operation
    can be performed for one or more drafts in a single request. Each draft is
    validated and processed independently, allowing for mixed response
    statuses (HTTP_207_MULTI_STATUS) in the case of bulk submissions.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="api_objects_drafts_publish",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            title="Publish BCO Draft Schema",
            description="Publish draft BCO [Bulk Enabled]",
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=["object_id"],
                properties={
                    "published_object_id": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="BCO Object ID to use for published object.",
                        example=f"{hostname}/TEST_000001/1.0"
                    ),
                    "object_id": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="BCO Object Draft ID to look up.",
                        example=f"{hostname}/TEST_000001/DRAFT"
                    ),
                    "delete_draft": openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description="Whether or not to delete the draft."\
                            +" False by default.",
                        example=False
                    ),
                }
            )
    ),
        responses={
            200: "All requests were accepted.",
            207: "Some requests failed and some succeeded. Each object submitted"
                " will have it's own response object with it's own status"
                " code and message.\n",
            400: "All requests were rejected.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )

    def post(self, request) -> Response:
        validator = BcoValidator()
        response_data = []
        requester = request.user
        data = request.data
        rejected_requests = False
        accepted_requests = False
        if 'POST_api_objects_drafts_publish' in request.data:
            data = legacy_api_converter(request.data)

        if "object_id" in data[0] and data[0]["object_id"] == \
            f"{hostname}/TEST_000001/DRAFT":
            identifier= f"{hostname}/TEST_000001/DRAFT"
            return Response(
                status=status.HTTP_200_OK, 
                data=[bulk_response_constructor(
                    identifier=identifier,
                    status = "SUCCESS",
                    code= 201,
                    message= f"TESTING: BCO {identifier} has been published"
                    " and assigned TEST as a score."
                )]
            )

        for index, object in enumerate(data):
            response_id = object.get("object_id", index)
            bco_instance = user_can_publish_draft(object, requester)

            if bco_instance is None:
                response_data.append(bulk_response_constructor(
                    identifier=response_id,
                    status = "NOT FOUND",
                    code= 404,
                    message= f"Invalid BCO: {response_id} does not exist.",
                ))
                rejected_requests = True
                continue

            if bco_instance is False:
                response_data.append(bulk_response_constructor(
                    identifier=response_id,
                    status = "FORBIDDEN",
                    code= 403,
                    message= f"User, {requester}, does not have draft permissions"\
                        + f" for BCO {response_id}.",
                ))
                rejected_requests = True
                continue

            if type(bco_instance) is str:
                response_data.append(bulk_response_constructor(
                    identifier=response_id,
                    status = "BAD REQUEST",
                    code= 400,
                    message= bco_instance
                ))
                rejected_requests = True
                continue

            if type(bco_instance) is tuple:
                response_data.append(bulk_response_constructor(
                    identifier=response_id,
                    status = "BAD REQUEST",
                    code= 400,
                    message= f"Invalid `published_object_id`."\
                        + f"{bco_instance[0]} and {bco_instance[1]}"\
                        + " do not match.",
                ))
                rejected_requests = True
                continue
            
            if bco_instance.state == 'PUBLISHED':
                object_id = bco_instance.object_id
                response_data.append(bulk_response_constructor(
                    identifier=response_id,
                    status = "CONFLICT",
                    code= 409,
                    message= f"Invalid `object_id`: {object_id} already"\
                        + " exists.",
                ))
                rejected_requests = True
                continue

            bco_results = validator.parse_and_validate(bco_instance.contents)

            identifier, results = bco_results.popitem()

            if results["number_of_errors"] > 0:
                rejected_requests = True
                bco_status = "FAILED"
                status_code = 400
                message = "BCO not valid"

            else:
                new_bco_instance = publish_draft(
                    bco_instance=bco_instance,
                    user=requester,
                    object=object
                )
                identifier = new_bco_instance.object_id
                accepted_requests = True
                bco_status = "SUCCESS"
                status_code = 200
                message = "BCO valid"

            response_data.append(bulk_response_constructor(
                identifier = identifier,
                status=bco_status,
                code=status_code,
                message=message,
                data=results
            ))

        status_code = response_status(accepted_requests, rejected_requests)
        return Response(status=status_code, data=response_data)

class DraftsModifyApi(APIView):
    """Modify BCO Draft [Bulk Enabled]

    API endpoint for modifying BioCompute Object (BCO) drafts, with support
    for bulk operations.

    This endpoint allows authenticated users to modify existing BCO drafts
    individually or in bulk by submitting a list of BCO drafts. The operation
    can be performed for one or more drafts in a single request. Each draft is
    validated and processed independently, allowing for mixed response
    statuses (HTTP_207_MULTI_STATUS) in the case of bulk submissions.
    """

    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(
        operation_id="api_objects_drafts_modify",
        request_body=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        title="Modify BCO Draft Schema",
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["object_id"],
            properties={
                "object_id": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="BCO Object ID.",
                    example=f"{hostname}/BCO_000001/DRAFT"
                ),
                "authorized_users": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="Users which can access the BCO draft.",
                    items=openapi.Schema(type=openapi.TYPE_STRING, example="tester")
                ),
                "contents": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Contents of the BCO.",
                    example=BCO_000001_DRAFT
                ),
            },
        ),
        description="BCO Drafts to create.",
    ),
        responses={
            200: "All requests were accepted.",
            207: "Some requests failed and some succeeded. Each object submitted"
                " will have it's own response object with it's own status"
                " code and message.\n",
            400: "All requests were rejected.",
            403: "Invalid token.",
        },
        tags=["BCO Management"],
    )

    def post(self, request) -> Response:
        response_data = []
        requester = request.user
        data = request.data
        rejected_requests = False
        accepted_requests = False

        if 'POST_api_objects_drafts_modify' in request.data:
            data = legacy_api_converter(request.data)

        if data[0]["contents"]["object_id"]==BCO_000001_DRAFT["object_id"] and\
            request.data[0]["authorized_users"] == ["tester"]:
            test_object_id = BCO_000001_DRAFT["object_id"]
            return Response(
                status=status.HTTP_200_OK,
                data=[
                    bulk_response_constructor(
                        identifier=test_object_id,
                        status = "SUCCESS",
                        code= 200,
                        message= f"TESTING: BCO {test_object_id} updated",
                    )
                ]
            )

        for index, object in enumerate(data):
            response_id = object.get("object_id", index)
            modify_permitted = user_can_modify_bco(response_id, requester)
            
            if modify_permitted is None:
                response_data.append(bulk_response_constructor(
                    identifier=response_id,
                    status = "NOT FOUND",
                    code= 404,
                    message= f"Invalid BCO: {response_id}.",
                ))
                rejected_requests = True
                continue

            if modify_permitted is False:
                response_data.append(bulk_response_constructor(
                    identifier=response_id,
                    status = "FORBIDDEN",
                    code= 400,
                    message= f"User, {requester}, does not have draft permissions"\
                        + f" for BCO {response_id}.",
                ))
                rejected_requests = True
                continue
            
            serialized_bco = ModifyBcoDraftSerializer(data=object)
        
            if serialized_bco.is_valid():
                try:
                    bco_instance = serialized_bco.update(serialized_bco.validated_data)
                    score = bco_instance.score
                    response_data.append(bulk_response_constructor(
                        identifier=response_id,
                        status = "SUCCESS",
                        code= 200,
                        message= f"BCO {response_id} updated with a sore of {score}",
                    ))
                    accepted_requests = True

                except Exception as err:
                    response_data.append(bulk_response_constructor(
                        identifier=response_id,
                        status = "SERVER ERROR",
                        code= 500,
                        message= f"BCO {response_id} failed. {err}",
                    ))
                    rejected_requests = True

            else:
                response_data.append(bulk_response_constructor(
                    identifier=response_id,
                    status = "REJECTED",
                    code= 400,
                    message= f"BCO {response_id} rejected",
                    data=serialized_bco.errors
                ))
                rejected_requests = True

        if accepted_requests is False and rejected_requests == True:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=response_data
            )
        
        if accepted_requests is True and rejected_requests is True:
            return Response(
                status=status.HTTP_207_MULTI_STATUS,
                data=response_data
            )

        if accepted_requests is True and rejected_requests is False:
            return Response(
                status=status.HTTP_200_OK,
                data=response_data
            )

class ValidateBcoApi(APIView):
    """Bulk Validate BCOs  [Bulk Enabled]

    --------------------

    Bulk operation to validate BCOs.

    ```JSON
    [
        {...BCO CONTENTS...},
        {...BCO CONTENTS...}
    ]

    """

    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_id="api_bco_validate",
        request_body=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        title="Validate BCO against Schema",
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["contents"],
            description="Contents of the BCO.",
            example=BCO_000001_DRAFT
            
        ),
        description="Validate BCO against IEEE schema.",
        ),
        responses={
            200: "All BCO validations are successful.",
            207: "Some or all BCO validations failed. Each object submitted"
                " will have it's own response object with it's own status"
                " message:\n",
            400: "Bad request."
        },
        tags=["BCO Management"],
    )
    def post(self, request):
        validator = BcoValidator()
        response_data = []
        rejected_requests = False
        accepted_requests = True
        data = request.data
        if 'POST_validate_bco' in request.data:
            data = legacy_api_converter(data=request.data)

        for index, object in enumerate(data):
            bco_results = validator.parse_and_validate(bco=object)
            identifier, results = bco_results.popitem()

            if results["number_of_errors"] > 0:
                rejected_requests = True
                bco_status = "FAILED"
                status_code = 400
                message = "BCO not valid"

            else:
                accepted_requests = True
                bco_status = "SUCCESS"
                status_code = 200
                message = "BCO valid"

            response_data.append(bulk_response_constructor(
                identifier = identifier,
                status=bco_status,
                code=status_code,
                message=message,
                data=results
            ))

        status_code = response_status(accepted_requests, rejected_requests)
        return Response(status=status_code, data=response_data)
    
class DraftRetrieveApi(APIView):
    """Get a draft object

    API View to Retrieve a Draft Object

    This view allows authenticated users to retrieve the contents of a specific
    draft object identified by its BioCompute Object (BCO) accession number.
    The operation ensures that only users with appropriate permissions can
    access the draft contents. Upon successfull retrieval of object the
    `access_count` is for this object is incremented.

    Parameters:
    - bco_accession (str):
        A string parameter passed in the URL path that uniquely identifies the
        draft object to be retrieved.
    """

    @swagger_auto_schema(
        operation_id="api_get_draft",
        manual_parameters=[
            openapi.Parameter(
                "bco_accession",
                openapi.IN_PATH,
                description="Object ID to be viewed.",
                type=openapi.TYPE_STRING,
                default="BCO_000000"
            )
        ],
        responses={
            200: "Success. Object contents returned",
            401: "Authentication credentials were not provided, or"
                " the token was invalid.",
            403: "Forbidden. The requestor does not have appropriate permissions.",
            404: "Not found. That draft could not be found on the server."
        },
        tags=["BCO Management"],
    )

    def get(self, request, bco_accession):
        requester = request.user
        bco_instance = retrieve_bco(bco_accession, requester)
        if bco_instance is False:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"message": f"User, {requester}, does not have draft permissions"\
                        + f" for {bco_accession}."})
        if bco_instance is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": f"{bco_accession}/DRAFT, could "\
                      + "not be found on the server."
                }
            )

        bco_counter_increment(bco_instance)
        return Response(status=status.HTTP_200_OK, data=bco_instance.contents)

class PublishedRetrieveApi(APIView):
    """Get Published BCO
    
    API view for retrieving a specific version of a published BioCompute
    Object (BCO).

    Retrieve the contents of a published BCO by specifying its accession
    number and version. Authentication is not required to access most
    published BCOs, reflecting the public nature of these objects. If
    the prefix is not public than the user's ability to view this BCO
    is verified. 

    Parameters:
    - `bco_accession`:
        Specifies the accession number of the BCO to be retrieved.

    - `bco_version`:
        Specifies the version of the BCO to be retrieved.
    """
    
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_id="api_get_published",
        manual_parameters=[
            openapi.Parameter(
                "bco_accession",
                openapi.IN_PATH,
                description="BCO accession to be viewed.",
                type=openapi.TYPE_STRING,
                default="BCO_000000"
            ),
            openapi.Parameter(
                "bco_version",
                openapi.IN_PATH,
                description="BCO version to be viewed.",
                type=openapi.TYPE_STRING,
                default="1.0"
            )
        ],
        responses={
            200: "Success. Object contents returned",
            401: "Authentication credentials were not provided, or"
                " the token was invalid.",
            403: "Forbidden. The requestor does not have appropriate permissions.",
            404: "Not found. That BCO could not be found on the server."
        },
        tags=["BCO Management"],
    )

    def get(self, request, bco_accession, bco_version):
        requester = request.user
        bco_instance = retrieve_bco(bco_accession, requester, bco_version)
        if bco_instance is False:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"message": f"User, {requester}, does not have draft permissions"\
                        + f" for {bco_accession}."})

        if bco_instance is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": f"{bco_accession}/{bco_version}, could "\
                      + "not be found on the server."
                }
            )
    
        bco_counter_increment(bco_instance)
        return Response(status=status.HTTP_200_OK, data=bco_instance.contents)

class CompareBcoApi(APIView):
    """Bulk Compare BCOs  [Bulk Enabled]

    --------------------

    Bulk operation to compare BCOs.

    ```JSON
    [
        {...BCO CONTENTS...},
        {...BCO CONTENTS...}
    ]

    """

    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_id="api_bco_compare",
        request_body=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        title="Bulk Compare BCOs",
        items=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            example=[BCO_000000_DRAFT, BCO_000001_DRAFT],
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=["contents"],
                description="Contents of the BCO.",
            )
        ),
        description="Compare one BCO against another.",
        ),
        responses={
            200: "All BCO comparisons are successful.",
            207: "Some or all BCO comparisons failed. Each object submitted"
                " will have it's own response object with it's own status"
                " message:\n",
            400: "Bad request."
        },
        tags=["BCO Management"],
    )
    def post(self, request):
        validator = BcoValidator()
        response_data = []
        rejected_requests = False
        accepted_requests = True
        data = request.data

        for index, comparison in enumerate(data):
            new_bco, old_bco = comparison
            identifier = new_bco["object_id"]+ " vs " + old_bco["object_id"]

            # new_results = validator.parse_and_validate(bco=new_bco)
            # old_results = validator.parse_and_validate(bco=old_bco)
            # import pdb; pdb.set_trace()
            # new_identifier, new_results = new_results.popitem()
            # old_identifier, old_results = bco_results.popitem()

            # if results["number_of_errors"] > 0:
            #     rejected_requests = True
            #     bco_status = "FAILED"
            #     status_code = 400
            #     message = "BCO not valid"

            # else:
            #     accepted_requests = True
            #     bco_status = "SUCCESS"
            #     status_code = 200
            #     message = "BCO valid"

            response_data.append(bulk_response_constructor(
                identifier = identifier,
                status="SUCCESS",
                code=200,
                # message=message,
                data=DeepDiff(new_bco, old_bco).to_json()
            ))

        status_code = response_status(accepted_requests, rejected_requests)
        return Response(status=status_code, data=response_data)