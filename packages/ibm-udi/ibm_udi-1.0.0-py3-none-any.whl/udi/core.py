# my_sdk/core.py
import json
import os
import time
import traceback
import warnings
from datetime import datetime
from http import HTTPStatus
from http.client import HTTPException
from udi.flows import Flow
from pydantic import ValidationError
from pydantic_core import ErrorDetails
from udi.models.pipeline_model import FlowModel
from typing import Any, Dict, List, Optional
from collections import defaultdict

from urllib3.exceptions import InsecureRequestWarning

from .constants import DatasiftSDKConstants, EnvironmentConstants
from .exception import ElyraGenerationException, DatasiftSDKException
from .rest_client import RestClient, RestMethod
from .utils import generate_token

# Suppress only the InsecureRequestWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)


class UDIClient:
    """
    A class to interact with the UDI API.

   Attributes:
        cpd_url (str): The URL of the CPD instance.
        user_name (str): The username for the CPD instance.
        password (str): The password for the CPD instance.
        project_id (str): The ID of the project to use.
        token (str): Token for the CPD instance.
            Either token or username and password must be provided.
        rest_client (RestClient): The REST client to use for making requests.

    Methods:
        create_flow(flow_name, pipeline_details) -> dict: Creates a flow in the CPD instance.
        run_flow(config: dict={}, status=False) -> dict: Runs a flow in the CPD instance.
        create_run_flow(flow_name, pipeline_details) -> str: Creates and runs a flow in the CPD instance.
    """
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get("base_url").rstrip('/')
        self.project_id = config.get("project_id")
        self.env = config.get("env")
        token = config.get("token")
        api_key = config.get("api_key")
        user_name = config.get("user_name")
        password = config.get("password")

        if not (token or api_key or password):
            raise DatasiftSDKException("Provide token or username/password/api_key.")

        self.access_token = token or generate_token(
            self._get_token_url(), user_name=user_name, password=password, api_key=api_key, env=self.env
        )
        self.rest_client = RestClient(self.base_url, self.access_token, self.project_id)
        self.udp_url = f"{self.base_url}/udp/v1"

    def _get_token_url(self):
        if self.env == EnvironmentConstants.CPD:
            return self.base_url
        elif self.env == EnvironmentConstants.CLOUD_DEV:
            url= "https://iam.test.cloud.ibm.com"
            return url
        elif self.env in [EnvironmentConstants.CLOUD_PROD, EnvironmentConstants.CLOUD_TEST]:
            url = "https://iam.cloud.ibm.com"
            return url
        else:
            raise DatasiftSDKException(f"Supported environments {EnvironmentConstants.ALL_ENVIRONMENTS}.")
        

    def __generate_elyra_json(self, pipeline_details):
        try:
            elyra_sdk_url = f"{self.udp_url}/sdk/generate_elyra"
            response = self.rest_client.call_rest_json(
                    method=RestMethod.POST,
                    action="Generate flow",
                    url=elyra_sdk_url,
                    request_body= pipeline_details,
                    expected_statuses= [HTTPStatus.OK.value,HTTPStatus.BAD_REQUEST.value,HTTPStatus.INTERNAL_SERVER_ERROR.value]
                )
            if not response or isinstance(response, str):
                raise ElyraGenerationException(f"An error occurred during elyra generation. Error: {response}")

            if DatasiftSDKConstants.ERRORS_RESPONSE_KEY in response:
                errors = response.get(DatasiftSDKConstants.ERRORS_RESPONSE_KEY, [])
                raise ElyraGenerationException(f"An error occurred during elyra generation. Error: {json.dumps(errors)}")
            return response
        except ElyraGenerationException:
            raise
        except Exception as ex:
            raise DatasiftSDKException(
                message="Elyra pipeline generation failed.",
                traceback_info=traceback.format_exc(),
            ) from ex

    def __add_select_options_to_operators(self, pipeline_details):
        try:
            elyra_flow = self.__generate_elyra_json(pipeline_details=pipeline_details)
            if elyra_flow is None:
                raise ElyraGenerationException("Elyra pipeline generation failed: No generated Elyra JSON found.")
            url = f"{self.udp_url}/flows/add_select_options_to_operators?container_id={self.project_id}&container_kind=project"
            response = self.rest_client.call_rest_json(
                method=RestMethod.POST,
                action="Add Select Options to Operators",
                url=url,
                request_body=elyra_flow["definition"]
            )

            if not response or isinstance(response, str):
                raise ElyraGenerationException(f"An error occurred while adding options to the operators in the given pipeline. Error : {response}")

            if DatasiftSDKConstants.ERRORS_RESPONSE_KEY in response:
                errors = response.get(DatasiftSDKConstants.ERRORS_RESPONSE_KEY, [])
                raise DatasiftSDKException(f"Error response: {json.dumps(errors)}")
            return response
        except ElyraGenerationException:
            raise
        except Exception as ex:
            raise DatasiftSDKException(
                message="An error occurred while adding options to the operators in the given pipeline.",
                traceback_info=traceback.format_exc(),
            ) from ex
        
    def get_metadata(self):

        metadata_url = f'{self.udp_url}/sdk/get_sdk_operator_metadata'
        res = self.rest_client.call_rest_json(
            method=RestMethod.GET,
            action="Get metadata",
            url=metadata_url
        )
        if isinstance(res, dict):
            return res

        raise DatasiftSDKException(
            message=f"Metadata not retrieved. Error: {res}"

        )
    
    def get_data_asset(self, asset_id):    
        asset_url = f'{self.base_url}/v2/assets/{asset_id}?project_id={self.project_id}'
        res = self.rest_client.call_rest_json(
            method=RestMethod.GET,
            action="Get asset information",
            url=asset_url
        )
        if isinstance(res, dict):
            asset_data = {}
            metadata = res.get('metadata', {})
            asset_data = {
                'asset_id': asset_id,
                'asset_name': metadata.get('name'),
                'created_on': metadata.get('created_at')
            }
            return asset_data
        
        raise DatasiftSDKException(
            message=f"Data for asset {asset_id} not retrieved. Error: {res}"
        )

    
    def get_available_operators(self):
        operator_metadata = self.get_metadata()
        desired_order = ["Ingest", "Extract", "Quality", "Functional", "VectorDB", "Custom"]
        grouped_keys = defaultdict(list)
        for key, value in operator_metadata.items():
            category = value['category']
            grouped_keys[category].append(key)

        # Creating a list of keys in the desired order
        ordered_dict = {category: grouped_keys.get(category, []) for category in desired_order}

        return ordered_dict

    def post_project_settings(self, request_body):
        url = f'{self.udp_url}/project_settings'
        try:
            res = self.rest_client.call_rest_json(
                method=RestMethod.POST,
                action="Create project settings",
                url=url,
                request_body=request_body
            )
            return res
        except Exception as e:
            raise DatasiftSDKException(
                message=f"Error while creating project settings: {e}",
                traceback_info=traceback.format_exc()
            )

    def get_project_settings(self):
        url = f'{self.udp_url}/project_settings?container_kind=project&container_id={self.project_id}'
        try:
            res = self.rest_client.call_rest_json(
                method=RestMethod.GET,
                action="Retrieve project settings",
                url=url
            )
            return res
        except Exception as e:
            raise DatasiftSDKException(
                message=f"Error while retrieving project settings: {e}",
                traceback_info=traceback.format_exc()
            )
        
    def patch_project_settings(self, request_body):
        url = f'{self.udp_url}/project_settings?container_kind=project&container_id={self.project_id}'
        try:
            res = self.rest_client.call_rest_json(
                method=RestMethod.PATCH,
                action="Update project settings",
                url=url,
                request_body = request_body
            )
            return res
        except Exception as e:
            raise DatasiftSDKException(
                message=f"Error while updating project settings: {e}",
                traceback_info=traceback.format_exc()
            )

   
    def read_and_store_file(self,file_path, key, files):
        if file_path:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            files[key] = (os.path.basename(file_path), file_content, 'application/octet-stream')
            return file_content
        return None

    def upload_custom_operator(
        self, file_path: Optional[str] = None, dependency: Optional[str] = None, package: Optional[str] = None
    ) -> Dict[str, Any]:  
        """
        Uploads a custom operator file along with an optional dependency and package archive.

        :param file_path: Operator file (optional .py).
        :param dependency: Dependency file (optional, zip).
        :param package: Package file (optional, zip).
        :return: Response from the API.
        """
        upload_url = f"{self.udp_url}/custom_operator/operators?container_id={self.project_id}"
        files={}
        try:
            for key, path in {
            'custom_operator_file': file_path,
            'custom_operator_dependency_archive': dependency,
            'custom_operator_package_archive': package
            }.items():
                if path:  
                    self.read_and_store_file(path, key, files)

            response = self.rest_client.call_rest_json(
                method=RestMethod.POST,
                action="Upload Custom Operator",
                url=upload_url,
                request_body={},
                files=files
            )
            return response
        except Exception as e:
            return {"error": str(e)}

    
    def delete_custom_operator(self,file_name: str) -> Dict:
        """
        Deletes a custom operator file given its name from custom_operators dir.
        :param file_name: file name.
        :return: JSON response with success or error message.
        """
        delete_url = f"{self.udp_url}/custom_operator/directory/{file_name}"
        try:
            response = self.rest_client.call_rest_json(
                    method=RestMethod.DELETE,
                    action="delete Custom Operator",
                    url=delete_url,
                    request_body={}
                )
            return response
        except Exception as e:
            return {"error": str(e)}

    def get_milvus_feature_mapping_metadata(self, pipeline_details):
        """
        Retrieves the milvus feature mapping metadata from the given pipeline details.

        Args:
           pipeline_details (dict): A dictionary containing the pipeline details.

        Returns:
            dict: A dictionary containing the milvus feature mapping metadata.
        """

        try:
            milvus_feature_mapping_metadata = {}
            elyra_flow_definition = self.__add_select_options_to_operators(pipeline_details=pipeline_details)
            milvus_elyra_node = next((elyra_node for elyra_node in elyra_flow_definition.get("pipelines",[])[0].get("nodes",[]) if elyra_node.get("op") == DatasiftSDKConstants.VECTORDB_MILVUS),None)
            if milvus_elyra_node is None:
                print("Node type Milvus VectorDB is not found in the given Pipeline Details")
                return  milvus_feature_mapping_metadata
            milvus_parameters = milvus_elyra_node.get(DatasiftSDKConstants.OPERATOR_PARAMETERS)
            milvus_feature_mapping_metadata[DatasiftSDKConstants.AVAILABLE_COLLECTIONS] = milvus_parameters.get(DatasiftSDKConstants.AVAILABLE_COLLECTIONS)
            milvus_feature_mapping_metadata[DatasiftSDKConstants.COLLECTIONS_COLUMNS] = milvus_parameters.get(DatasiftSDKConstants.COLLECTIONS_COLUMNS)
            milvus_feature_mapping_metadata[DatasiftSDKConstants.AVAILABLE_FEATURES] = milvus_parameters.get(DatasiftSDKConstants.AVAILABLE_FEATURES)
            milvus_feature_mapping_metadata[DatasiftSDKConstants.MILVUS_FEATURE_MAPPINGS] = milvus_parameters.get(DatasiftSDKConstants.MILVUS_FEATURE_MAPPINGS)
            return milvus_feature_mapping_metadata

        except Exception as ex:
            raise DatasiftSDKException(
                message="An error occurred while retrieving milvus feature mapping metadata",
                traceback_info=traceback.format_exc()
            ) from ex
    

if __name__ == "__main__":
    from udi.utils import available_operators, get_attributes, get_features
    from udi import UDIClient

    cpd_url = "https://cpd-wkc.apps.udptest7.cp.fyre.ibm.com"
    local_url = "http://0.0.0.0:8000/"
    token = ""
    project_id = "f9cfa851-fbaf-4140-8166-fbbb7d0f4cf9"
    uc = UDIClient(local_url, token, project_id)

    # Get operator metadata
    metadata = uc.get_metadata()
    print(metadata)
    print(json.dumps(metadata, indent=2))
    # Get the operator list in the format category = [List of operators]
    ordered_operators = available_operators(metadata)
    print(json.dumps(ordered_operators, indent=2))

    """
        Input: Metadata and Operator Name
        Output: Get the attributes/parameters to be defined for a specific operator
                If Output is None, then the operator does not require any user Input and has fixed transformation
        Usage: This is required for flow generation.
    """
    operator_attributes = get_attributes(metadata, "pii_extract_redact")
    # print(json.dumps(operator_attributes, indent=2))

    """
        Input: Metadata and Operator Name
        Output: See the features that would be added for by any operator
                If Output is None, then the operator has not added any new features and transformed an existing feature in flow
        Usage: This is not required for flow generation.
    """
    operator_features = get_features(metadata, "pii_extract_redact")
    # print(json.dumps(operator_features, indent=2))

    # Create a sequence of operators.
    operators = [
        {"type": "ingest_cpd_local",
         "parameters": [
             {'asset_id': '83d21a56-f306-4b46-8164-d18c5c723818',
              'asset_name': '2401.00006v1.pdf',
              'created_on': '2024-11-05T17:23:26Z'
              }
         ]
         },
        # {
        #     "type": "ingest_cpd_s3",
        #     "parameters": {
        #         "connection_id": "409fe4ee-d80f-4f94-a9bc-6585660c6544",
        #         "sources": [
        #             "/tm-wkc-storage-1/2_small_files",
        #             "/tm-wkc-storage-1/8_pdf_small_files",
        #             "/tm-wkc-storage-1/_PLT_Demo_/test_invoice_01.pdf"
        #         ],
        #         "include_filter": [
        #             "pdf", "txt","md"
        #         ],
        #     "max_file_size": 100,
        #     "max_files": 100
        #     }
        # },
        # {
        #     "type": "ingest_web_page",
        #     "parameters": {
        #         "seed_urls": [
        #             "https://arxiv.org/pdf/2502.00062",
        #             "https://arxiv.org/pdf/2502.00080"
        #         ],
        #         "allowed_mime_types": [
        #             "application/pdf",
        #             "text/markdown",
        #             "text/plain"
        #         ],
        #         "crawl_depth": 1,
        #         "max_downloads": 10,
        #     }
        # },
        {"type": "extract_cpd"},
        {"type": "lang_detect"},
        {"type": "chunker",
         "parameters": {'chunk_type': 'simple',
                        'chunk_size': 4000,
                        'chunk_overlap': 200
                        }
         },
        {"type": "embeddings"},
        {"type": "elasticsearch",
         "parameters": {
             "connection_id": "3ba79ee8-a265-4b06-9d8b-56510faad5e1",
             "connection_name": "ES conn",
             "dimension_size": 384,
             "index_name": "datasift"
            }
         },
    ]

    flow_name = f"SDK_FLOW_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}"

    """
    Define Pipeline details:
        flow_name: Flow name
        project_id:
        orchestrator:
        flow: Sequence of operators
    """
    pipeline = {
        "flow_name": flow_name,
        "project_id": project_id,
        "orchestrator": "python",
        "flow": operators
    }

    """
    Create a flow from the asset and then run the flow
    """
    # Create flow
    create_flow_response = uc.create_flow(flow_name, pipeline)
    print(json.dumps(create_flow_response, indent=2))
    flow_id = create_flow_response["flow_id"]

    #Use the response to run the flow
    execute_flow_response = uc.run_flow(create_flow_response)


    """
    Create and run a flow
    """
    # execute_flow_response = uc.create_run_flow(flow_name, pipeline)
    # print(json.dumps(execute_flow_response, indent=2))
    # flow_id = execute_flow_response["flow_id"]

    time.sleep(5)
    status = uc.flow_execution_status(execute_flow_response)
    print(f"Execution Status: {status['status']}")


    """
    Get logs for execution  
    """
    for i in range(0,10):
        logs = uc.get_execution_logs(execute_flow_response)
        print(json.dumps(logs, indent=2))
        time.sleep(10)

    """
    To get a flow from the project
    """
    flow_response = uc.get_flow(flow_id)
    # print(json.dumps(flow_response, indent=2))

    """
    To delete a flow from the Project
    """
    # uc.delete_flow(flow_id)

    """
    To cancel an execution
    """
    cancel_execution = uc.cancel_execution(execute_flow_response)
    print(json.dumps(cancel_execution, indent=2))