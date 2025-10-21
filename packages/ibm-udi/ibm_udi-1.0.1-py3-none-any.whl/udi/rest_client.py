from enum import Enum
import json
import requests

APPLICATION_JSON_TYPE = 'application/json'
TIMEOUT = 60

class RestMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    

class RestClient:
    """
    Provides methods for executing REST API.
    """
    def __init__(self, cpd_url, access_token, project_name, default_query_params: dict=None):
        self.session = requests.Session()
        self.cpd_url = cpd_url
        self.token = f'Bearer {access_token}'
        self.project_name = project_name
        self.default_query_params = default_query_params
        self.verify = False
        
    def call_rest_json(self, method: RestMethod, action: str, url: str, query_params: dict = None,
                       request_body: dict = None, files: dict = None, expected_statuses: list[int] = None):
        headers = {'Content-type': APPLICATION_JSON_TYPE, 'Accept': APPLICATION_JSON_TYPE}
        if files:
            headers = {}
        
        return self.call_rest(method, action, url, query_params, request_body, files, headers, expected_statuses)

    def call_rest(self, method: RestMethod, action: str, url: str, query_params: dict = None, request_body: dict = None,
                  files: dict = None, headers: dict = None, expected_statuses: list[int] = None):
        """
        Executes REST API
        method - type of REST call, namely GET, POST, PUT, PATCH and DELETE
        action - descriptive action to be used in the log message
        url - URL excluding query parameters
        query_parameters - If query parameters are not provided then the default query parameters set in the constructor will be used
        request_body - The JSON request body as dictionary
        file - the file where the request body needs to be read
        header - HTTP Headers to be used
        expected_statuses - If the response from REST API has one of the expected status codes,
                            then it is considered succeeded, otherwise an exception will be thrown
                            If expected_statuses is not passed, then the following status codes are expected
                            GET - 200
                            POST - 200, 201
                            PUT - 200, 201
                            PATCH - 200
                            DELETE - 204
        """
        try:
            # Add bearer token to the header
            headers = headers if headers is not None else {}
            headers["Authorization"] = self.token
            query_params = query_params if query_params is not None else self.default_query_params
            if request_body is not None:
                request_body = json.dumps(request_body)
            # print(f"Calling URL: {method} {url} with params: {query_params} for action: {action}")
            match method:
                case RestMethod.GET:
                    expected_statuses = [200] if expected_statuses is None else expected_statuses
                    response = self.session.get(url, params=query_params, headers=headers, verify=self.verify, timeout=TIMEOUT)
                case RestMethod.POST:
                    expected_statuses = [200, 201] if expected_statuses is None else expected_statuses
                    if files:
                        response = self.session.post(url, params=query_params, headers=headers,
                                                    verify=self.verify, timeout=TIMEOUT, files=files)
                    else:
                        response = self.session.post(url, params=query_params, data=request_body, headers=headers,
                                                    verify=self.verify, timeout=TIMEOUT)
                case RestMethod.PUT:
                    expected_statuses = [200, 201] if expected_statuses is None else expected_statuses
                    if files:
                        response = self.session.put(url, params=query_params, files=files, headers=headers,
                                                    verify=self.verify, timeout=TIMEOUT)
                    else:
                        response = self.session.put(url, data=request_body, headers=headers,
                                verify=self.verify, timeout=TIMEOUT)
                case RestMethod.PATCH:
                    expected_statuses = [200] if expected_statuses is None else expected_statuses
                    response = self.session.patch(url, params=query_params, data=request_body, files=files,
                                                  headers=headers, verify=self.verify, timeout=TIMEOUT)
                case RestMethod.DELETE:
                    expected_statuses = [204] if expected_statuses is None else expected_statuses
                    response = self.session.delete(url, params=query_params, headers=headers, verify=self.verify, timeout=TIMEOUT)
                case _:
                    raise DatasiftException(f"Found an invalid REST method: {method}")
        except Exception as exc:
            return exc

        if response.status_code in expected_statuses:
            if response.status_code == 204:
                return
            return response.json()
        else:
            return response.reason

    