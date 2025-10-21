import json
import traceback
import warnings
import time
from urllib3.exceptions import InsecureRequestWarning

from .constants import DatasiftSDKConstants, JobStatusConstants
from .exception import ElyraGenerationException, DatasiftSDKException
from .rest_client import RestMethod
from .models.pipeline_model import FlowModel
from http import HTTPStatus

# Suppress only the InsecureRequestWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

class Flow:
    def __init__(self, udp_client):
        self.rest_client = udp_client.rest_client
        self.project_id = udp_client.project_id
        self.udp_url = udp_client.udp_url
        self.base_url = udp_client.base_url

        self.flow_id = None
        self.job_id = None
        self.job_run_id = None
        self.flow_name = None

    def _generate_elyra_json(self, pipeline):
        try:
            url = f"{self.udp_url}/sdk/generate_elyra"
            response = self.rest_client.call_rest_json(
                    method=RestMethod.POST,
                    action="Generate flow",
                    url=url,
                    request_body= pipeline,
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

    def create(self, pipeline: dict):
        try:
            flow_name = pipeline.get("flow_name")
            FlowModel.model_validate(pipeline)
            elyra_json = self._generate_elyra_json(pipeline)

            url = f"{self.udp_url}/flows"
            response = self.rest_client.call_rest_json(method = RestMethod.POST, 
                                                    action="Create Flow",
                                                    url=url,
                                                    request_body=elyra_json,
                                                    expected_statuses=[201,400]
                                                    )
            print("create flow", response)
            self.flow_id = response.get("flow_id")

            if not self.flow_id:
                raise DatasiftSDKException("Flow creation failed: Missing flow_id in response")

            # Create job
            print(f'Flow is created: {self.flow_id}')
            job_name = f'{flow_name}_job'
            create_job_url = f'{self.base_url}/v2/jobs?project_id={self.project_id}'
            print(create_job_url)
            print(flow_name)
            create_job_request_body = {
                "job": {
                    "asset_ref": self.flow_id,
                    "name": job_name,
                    "description": " ",
                    "configuration":{
                        "orchestrator": pipeline["orchestrator"],
                        "runtime_parameters": {},
                        "service_instance": {}
                    }
                    }
                }
            job_response = self.rest_client.call_rest_json(
                method= RestMethod.POST,
                action = "Create Job",
                url = create_job_url,
                request_body=create_job_request_body
            )
            print("job_response",job_response)
            self.job_id = job_response.get("asset_id")

            if not self.job_id:
                raise DatasiftSDKException("Job creation failed: No job_id found in response")

            # Patch job_id into flow
            patch_url = f"{self.base_url}/v2/assets/{self.flow_id}/attributes/ibm_udp_flow?project_id={self.project_id}"
            response = self.rest_client.call_rest_json(method = RestMethod.PATCH, 
                                                    action="Patch Job",
                                                    url=patch_url,
                                                    request_body=[{"op": "add", "path":"/job_id","value": self.job_id}]
                                                    )

        except Exception as ex:
            raise DatasiftSDKException(f"Flow creation failed: {str(ex)}\n{traceback.format_exc()}")

    def run(self, job_id=None):
        try:
            job_id = job_id or self.job_id
            job_run_url = f"{self.base_url}/v2/jobs/{job_id}/runs?project_id={self.project_id}"
            job_run_payload = {
            "job_run": {
                "configuration": {}
            } }
            res = self.rest_client.call_rest_json(RestMethod.POST, "Run Job", job_run_url, job_run_payload)
            print('job_run_response :', res )
            self.job_run_id = res["href"].split("/")[-1].split("?")[0]
        except Exception as ex:
            raise DatasiftSDKException(f"Flow run failed: {str(ex)}\n{traceback.format_exc()}")

    def status(self, flow_id=None, job_run_id=None):
        try:
            flow_id = flow_id or self.flow_id
            job_run_id = job_run_id or self.job_run_id
            url = f"{self.udp_url}/flows/{flow_id}/runs/{job_run_id}?container_id={self.project_id}"
            return self.rest_client.call_rest_json(RestMethod.GET, "Get Status", url)
        except Exception as ex:
            raise DatasiftSDKException(f"Status check failed: {str(ex)}")

    def logs(self, job_id=None, job_run_id=None):
        try:
            job_id = job_id or self.job_id
            job_run_id = job_run_id or self.job_run_id
            url = f"{self.udp_url}/flows/get_execution_logs/{self.job_id}/{self.job_run_id}?container_id={self.project_id}"
            return self.rest_client.call_rest_json(RestMethod.GET, "Get Logs", url)
        except Exception as ex:
            raise DatasiftSDKException(f"Fetching logs failed: {str(ex)}")

    def cancel(self, flow_id=None, job_run_id=None):
        try:
            flow_id = flow_id or self.flow_id
            job_run_id = job_run_id or self.job_run_id
            url = f"{self.udp_url}/flows/{flow_id}/runs/{job_run_id}"
            response = self.rest_client.call_rest_json(RestMethod.DELETE, "Cancel Execution", url)
            return {"status": "Cancelled"} if response == "OK" else {"status": "Failed to cancel"}
        except Exception as ex:
            raise DatasiftSDKException(f"Cancellation failed: {str(ex)}")

    def delete(self,flow_id=None):
        try:
            flow_id = flow_id or self.flow_id
            url = f"{self.udp_url}/flows/{flow_id}?container_kind=project&container_id={self.project_id}"
            return self.rest_client.call_rest_json(RestMethod.DELETE, "Delete Flow", url)
        except Exception as ex:
            raise DatasiftSDKException(f"Flow deletion failed: {str(ex)}")
    
    def get_flow(self, flow_id=None):
        try:
            flow_id = flow_id or self.flow_id
            url = f"{self.udp_url}/flows/{flow_id}?container_kind=project&container_id={self.project_id}"
            return self.rest_client.call_rest_json(
                method=RestMethod.GET,
                action="Get Flow",
                url=url
            )
        except Exception as ex:
            raise DatasiftSDKException(f"Get flow failed: {str(ex)}")
    
    def update_flow(self, pipeline: dict, flow_id=None):
        """
        Update the flow with a new elyra pipeline definition.
        """
        try:
            flow_id = flow_id or self.flow_id
            new_flow = self._generate_elyra_json(pipeline)
            url = f"{self.udp_url}/flows/{flow_id}"
            response = self.rest_client.call_rest_json(
                method=RestMethod.PUT,
                action="Update flow",
                url=url,
                request_body=new_flow
            )
            return response
        except Exception:
            raise DatasiftSDKException(message="Flow not found", traceback_info=traceback.format_exc())

    
    def poll_flow_status(self, flow_id=None, job_run_id=None, interval=10, timeout=600):
        flow_id = flow_id or self.flow_id
        job_run_id = job_run_id or self.job_run_id
        elapsed_time = 0
        status_url = f"{self.udp_url}/flows/{flow_id}/runs/{job_run_id}?container_id={self.project_id}"

        while elapsed_time < timeout:
            response = self.rest_client.call_rest_json(
                method="GET",
                action="Poll Flow Execution Status",
                url=status_url
            )

            status = response.get("status", "unknown")
            print(f"[{elapsed_time}s] Current status: {status}")

            if status in [JobStatusConstants.CANCELED, JobStatusConstants.FAILED, JobStatusConstants.COMPLETED,
                          JobStatusConstants.COMPLETED_WITH_ERRORS, JobStatusConstants.COMPLETED_WITH_WARNINGS]:
                print("Final status:", status)
                return status

            time.sleep(interval)
            elapsed_time += interval

        raise TimeoutError("Flow status polling timed out.")