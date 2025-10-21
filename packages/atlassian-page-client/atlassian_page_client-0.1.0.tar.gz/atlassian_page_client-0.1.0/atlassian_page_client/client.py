# Call JIRA API with HTTPBasicAuth
import json
import requests
from requests.auth import HTTPBasicAuth
from .page import AtlassianPage


class AtlassianPageClient:

    HEADERS = {'Content-Type': 'application/json;charset=iso-8859-1'}
    
    def __init__(self, email: str, token: str, base_url: str):
        self.base_url = base_url
        self.email = email
        self.token = token
        self.basicAuth = HTTPBasicAuth(self.email, self.token)

    def check_response(self, response: requests.Response) -> None:
        if response.status_code != 200:
            raise Exception(f"Failed to get page from url {response.url}: {response.status_code} {response.text}")

    def get(self, page_id: str) -> AtlassianPage:
        apiUrl = f"/wiki/rest/api/content/{page_id}?expand=body.storage,version"

        response = requests.get(
            self.base_url + apiUrl,
            headers=self.HEADERS,
            auth=self.basicAuth
        )

        self.check_response(response)

        return AtlassianPage(page_id, json.loads(response.text))
    
    def put(self, page: AtlassianPage) -> AtlassianPage:
        apiUrl = f"/wiki/rest/api/content/{page.get_page_id()}"
        page.increase_version()
        data = json.dumps(page.get_page_content_dict())

        response = requests.put(
            self.base_url + apiUrl,
            data=data,
            headers=self.HEADERS,
            auth=self.basicAuth
        )

        self.check_response(response)

        return AtlassianPage(page.get_page_id(), json.loads(response.text))
