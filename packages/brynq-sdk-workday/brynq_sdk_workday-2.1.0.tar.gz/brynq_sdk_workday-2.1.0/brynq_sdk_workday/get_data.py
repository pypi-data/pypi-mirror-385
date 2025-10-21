import requests
import pandas as pd
from typing import List, Union, Literal, Optional
from brynq_sdk_brynq import BrynQ
import base64

class GetData(BrynQ):
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False):
        super().__init__()
        self.timeout = 3600
        self.base_url, self.headers = self._set_credentials(system_type)


    def _set_credentials(self, system_type):
        """
        Sets the credentials for the Workday API.

        Parameters:
        label (str): The label for the system credentials.

        Returns:
        base_url (str): The base URL for the API.
        headers (dict): The headers for the API request, including the access token.
        """
        credentials = self.interfaces.credentials.get(system="workday", system_type=system_type)
        credentials = credentials.get('data')
        username = credentials.get('username')
        password = credentials.get('password')
        host = credentials.get('host')
        report_url = credentials.get('report_url')

        if username is None or password is None:
            client_id = credentials.get('client_id')
            client_secret = credentials.get('client_secret')
            refresh_token = credentials.get('refresh_token')
            token_url = credentials.get('token_url')

            # Get the Access Token
            token_url = f'{host}/{token_url}'
            report_url = f'{host}/{report_url}'
            payload = {
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.request("POST", token_url, headers=headers, data=payload, timeout=self.timeout)
            access_token = response.json()['access_token']
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
        else:
            report_url = f'{host}/{report_url}'
            credentials = f"{username}:{password}"
            encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
            headers = {
                'Authorization': f'Basic {encoded_credentials}'
            }
        return report_url, headers

    def get_data(self, endpoint: str, top_level_key: str, format: str = 'json', query: str = None):
        """
        Download data from successfactors via the report method.
        :param endpoint: give the endpoint you want to call
        :param top_level_key: the top level key in the response json
        :param filter: Optional. Enter a filter in OData format. See here more information:
        """
        url = f'{self.base_url}/{endpoint}?format={format}&'
        if query:
            url = f'{url}{query}'

        df = pd.DataFrame()
        while True:
            response = requests.request("GET", url, headers=self.headers, timeout=self.timeout)
            data = response.json()[top_level_key]
            df_temp = pd.DataFrame(data)
            df = pd.concat([df, df_temp])
            url = response.json().get('__next', None)
            if not url:
                break

        return df
