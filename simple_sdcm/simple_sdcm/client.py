# https://github.com/microsoft/SDCM

import http.client
import json
import requests
from urllib.parse import quote
import time


class Client:
    def __init__(self, tenant_id, client_id, client_secret):
        """Initializes the client with tenant, client, and secret credentials."""
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_resource = "https://manage.devcenter.microsoft.com"
        self.access_token = ""

        self.version = "1.0"
        self.tenant = "my"

        self.token_endpoint_template = "/{0}/oauth2/token"
        self.get_products_url_template = "/v{0}/{1}/hardware/products"
        self.get_submission_url_template = (
            "/v{0}/{1}/hardware/products/{2}/submissions/{3}"
        )
        self.commit_submission_url_template = (
            "/v{0}/{1}/hardware/products/{2}/submissions/{3}/commit"
        )
        self.update_url_template = "/v{0}/{1}/hardware/products/{2}/submissions/{3}/"
        self.product_url_template = "/v{0}/{1}/hardware/products"
        self.product_url_with_continuation_template = "/v{0}/{1}/{2}"
        self.get_product_url_template = "/v{0}/{1}/hardware/products/{2}"
        self.create_submission_url_template = (
            "/v{0}/{1}/hardware/products/{2}/submissions"
        )
        self.product_submission_status_url_template = (
            "/v{0}/{1}/hardware/products/{2}/submissions/{3}"
        )

    def __set_client_credential_access_token(self, token):
        """Sets the token resource."""
        self.access_token = token

    def __get_client_credential_access_token(self):
        """Retrieves access token using client credentials."""
        token_request_body = "grant_type=client_credentials&client_id={0}&client_secret={1}&resource={2}".format(
            self.client_id, self.client_secret, self.token_resource
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        token_connection = http.client.HTTPSConnection("login.microsoftonline.com")
        token_connection.request(
            "POST",
            self.token_endpoint_template.format(self.tenant_id),
            token_request_body,
            headers=headers,
        )

        token_response = token_connection.getresponse()
        token_json = json.loads(token_response.read().decode())
        token_connection.close()

        self.access_token = token_json["access_token"]
        return self.access_token

    def setup_access_token(self):
        """Sets up the access token for the client."""
        self.__set_client_credential_access_token(
            self.__get_client_credential_access_token()
        )

    def get_headers(self):
        """Returns headers for requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-type": "application/json",
            "User-Agent": "Python",
        }

    def make_request(self, method, url_template, *url_params, body=None):
        """Makes an HTTP request and returns the response JSON."""
        headers = self.get_headers()
        connection = http.client.HTTPSConnection("manage.devcenter.microsoft.com")
        url = url_template.format(self.version, self.tenant, *url_params)

        connection.request(method, url, body, headers=headers)
        response = connection.getresponse()
        response_data = response.read().decode().strip()

        if len(response_data) != 0:
            response_json = json.loads(response_data)
        else:
            response_json = {}
        connection.close()

        return response_json

    def get_products(self):
        """Fetches all products."""
        return self.make_request("GET", self.get_products_url_template)

    def get_product(self, product_id):
        """Fetches a specific product by ID."""
        return self.make_request("GET", self.get_product_url_template, product_id)

    def get_submission(self, product_id, submission_id):
        """Fetches a specific submission by product and submission ID."""
        return self.make_request(
            "GET", self.get_submission_url_template, product_id, submission_id
        )

    def create_product(self, product_body):
        """Creates a new product."""
        return self.make_request("POST", self.product_url_template, body=product_body)

    def create_submission(self, product_id, submission_body):
        """Creates a new submission for a product."""
        return self.make_request(
            "POST",
            self.create_submission_url_template,
            product_id,
            body=submission_body,
        )

    def commit_submission(self, product_id, submission_id):
        """Commits a submission for a product."""
        return self.make_request(
            "POST", self.commit_submission_url_template, product_id, submission_id
        )

    def get_product_submission_status(self, product_id, submission_id):
        """Fetches the status of a product submission."""
        return self.make_request(
            "GET",
            self.product_submission_status_url_template,
            product_id,
            submission_id,
        )

    def upload_file(self, file_path, file_upload_url):
        """Uploads a file to the specified URL."""
        with open(file_path, "rb") as file:
            upload_response = requests.put(
                file_upload_url,
                file,
                headers={"x-ms-blob-type": "BlockBlob"},
            )

        return upload_response.status_code

    def wait(self, product_id, submission_id, verbose):
        """Waits for a submission to complete."""
        while True:
            res = self.get_product_submission_status(product_id, submission_id)

            if verbose:
                step = res["workflowStatus"]["currentStep"]
                state = res["workflowStatus"]["state"]
                print(f"{step} {state}")

            if res["workflowStatus"]["state"] == "failed":
                return

            for item in res["downloads"]["items"]:
                if item["type"].lower() == "signedpackage":
                    return item["url"]

            time.sleep(5)
