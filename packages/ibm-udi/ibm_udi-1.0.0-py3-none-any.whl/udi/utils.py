from collections import defaultdict
import requests

from udi.constants import EnvironmentConstants
from udi.exception import DatasiftSDKException

"""
    Input: Metadata and Operator Name
    Output: Get the attributes/parameters to be defined for a specific operator
            If Output is None, then the operator does not require any user Input and has fixed transformation
    Usage: This is required for flow generation.
"""
def get_attributes(metadata, operator):
    try:
        return metadata[operator].get("attributes")
    except Exception:
        return None

"""
    Input: Metadata and Operator Name
    Output: See the features that would be added for by any operator
            If Output is None, then the operator has not added any new features and transformed an existing feature in flow
    Usage: This is not required for flow generation.
"""
def get_features(metadata, operator):
    try:
        return metadata[operator].get("features")
    except Exception:
        return None

def authorize(url: str,api_key: str,user_name: str  = None, password: str = None,params: dict = None):
    key = "api_key" if api_key else "password"
    value = api_key or password
    headers = {'Content-Type': 'application/json'}
    request_body = {key: value, "username": user_name}
    if params:
        response = requests.post(url, params=params)
        response_str = "access_token"
    else:
        response = requests.post(url, json=request_body, headers=headers, verify=False) 
        response_str = "token"
    response.raise_for_status()
    if response.status_code == 200:
        return response.json().get(response_str)
 
def generate_token(base_url: str, api_key: str = None, env: str = None, user_name: str=None,password: str=None) -> str:
    """
    Generate a token for the CP4D instance.

    Args:
        cp4d_base_url (str): The base URL of the CP4D instance.
        api_key (str): api key for different envs
        user_name (str): CP4D username
        password (str): CP4D password
    Returns:
        str: The generated token.
    """
    if env == EnvironmentConstants.CPD:
        url = f"{base_url}/icp4d-api/v1/authorize"
        return authorize(url,api_key,user_name,password)
    elif (env in [EnvironmentConstants.CLOUD_DEV, EnvironmentConstants.CLOUD_PROD, EnvironmentConstants.CLOUD_TEST]) and api_key:
        url = f"{base_url}/identity/token"
        querystring = {"apikey":api_key,"grant_type":"urn:ibm:params:oauth:grant-type:apikey"}
        return authorize(url,api_key,user_name,password,querystring)
    else:
        raise DatasiftSDKException("Apikey or user_name and password with env must be provided.")
    