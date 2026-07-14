import base64
import json
import os
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import quote, unquote, urlparse

import msal
import requests

from .utils import print_upload_progress


GRAPH_ROOT = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPE = ["https://graph.microsoft.com/.default"]
GRAPH_TOKEN_AUDIENCES = {
    "https://graph.microsoft.com",
    "00000003-0000-0000-c000-000000000000",
}
SHAREPOINT_REST_TOKEN_AUDIENCE = "00000003-0000-0ff1-ce00-000000000000"
SIMPLE_UPLOAD_MAX_SIZE = 250 * 1024 * 1024
UPLOAD_CHUNK_SIZE = 10 * 1024 * 1024


class GraphRequestError(RuntimeError):
    def __init__(self, method: str, url: str, response: requests.Response):
        body = response.text[:2000] if response.text else ""
        super().__init__(
            "Microsoft Graph request failed "
            "method={0} url={1} status={2} body={3}".format(
                method, url, response.status_code, body
            )
        )
        self.method = method
        self.url = url
        self.status_code = response.status_code
        self.body = body


class Client:
    def __init__(
        self,
        cid: str,
        csec: str,
        base_url: str,
        tenant_id: Optional[str] = None,
    ):
        self.cid = cid
        self.csec = csec
        self.base_url = base_url.rstrip("/")
        self.tenant_id = tenant_id or self._infer_tenant_id()
        self._site_path = unquote(urlparse(self.base_url).path).rstrip("/")
        self._site_id = None
        self._session = requests.Session()
        self._app = msal.ConfidentialClientApplication(
            self.cid,
            authority="https://login.microsoftonline.com/{0}".format(self.tenant_id),
            client_credential=self.csec,
        )

    def upload_file(self, src: str, dst: str, check_dir: bool = True):
        try:
            drive_folder_path = self._to_drive_path(dst)
            if check_dir:
                self._ensure_folder(drive_folder_path)

            filename = os.path.basename(src)
            drive_file_path = self._join_drive_path(drive_folder_path, filename)
            response = self._upload_file(src, drive_file_path)
            uploaded_path = response.get("webUrl") or drive_file_path
            print("[INFO] {0} Success uploaded".format(uploaded_path))
        except Exception as e:
            print("[ERROR] Upload Failed")
            print(e)

    def upload_dir(self, src: str, dst: str):
        try:
            self._ensure_folder(self._to_drive_path(dst))

            for file in os.listdir(src):
                path = os.path.join(src, file)
                if os.path.isdir(path):
                    self.upload_dir(path, "{0}/{1}".format(dst.rstrip("/"), file))
                else:
                    self.upload_file(path, dst, check_dir=False)
        except Exception as e:
            print("[ERROR] Upload failed")
            print(e)

    def download_file(self, src: str, dst: str):
        try:
            drive_path = self._to_drive_path(src)
            response = self._request(
                "GET",
                self._drive_item_path(drive_path, "content"),
                expected_status=(200,),
                stream=True,
            )

            target_dir = os.path.dirname(dst)
            if target_dir:
                os.makedirs(target_dir, exist_ok=True)

            with open(dst, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

            print("[INFO] Download Success {0} => {1}".format(src, dst))
        except Exception as e:
            print("[ERROR] Download failed")
            print(e)

    def download_dir(self, src: str, dst: str):
        try:
            os.makedirs(dst, exist_ok=True)

            for name, is_folder in self.list_dir(src):
                sharepoint_path = "{0}/{1}".format(src.rstrip("/"), name)
                local_path = os.path.join(dst, name)

                if is_folder:
                    self.download_dir(sharepoint_path, local_path)
                else:
                    self.download_file(sharepoint_path, local_path)
        except Exception as e:
            print("[ERROR] Download failed")
            print(e)

    def list_dir(self, src: str):
        result = []

        try:
            drive_path = self._to_drive_path(src)
            path = self._drive_item_path(drive_path, "children")

            while path:
                response = self._request_json("GET", path)
                for item in response.get("value", []):
                    result.append((item["name"], "folder" in item))
                path = response.get("@odata.nextLink")
        except Exception as e:
            print(e)

        return result

    def _infer_tenant_id(self):
        hostname = urlparse(self.base_url).hostname or ""
        tenant_name = hostname.split(".")[0]
        if not tenant_name:
            raise ValueError("tenant_id is required when base_url host cannot be parsed")
        return "{0}.onmicrosoft.com".format(tenant_name)

    def _site_graph_id(self) -> str:
        if self._site_id is None:
            parsed = urlparse(self.base_url)
            hostname = parsed.hostname
            site_path = unquote(parsed.path).rstrip("/")
            if not hostname or not site_path:
                raise ValueError("invalid SharePoint site URL: {0}".format(self.base_url))

            encoded_site_path = quote(site_path, safe="/")
            response = self._request_json(
                "GET",
                "sites/{0}:{1}?$select=id".format(hostname, encoded_site_path),
            )
            self._site_id = response["id"]

        return self._site_id

    def _get_access_token(self) -> str:
        result = self._app.acquire_token_silent(GRAPH_SCOPE, account=None)
        if not result:
            result = self._app.acquire_token_for_client(scopes=GRAPH_SCOPE)

        access_token = result.get("access_token")
        if not access_token:
            error = result.get("error")
            description = result.get("error_description")
            raise RuntimeError(
                "failed to acquire Microsoft Graph token "
                "tenant={0!r} error={1!r} description={2!r}".format(
                    self.tenant_id, error, description
                )
            )

        self._validate_graph_token(access_token)
        return access_token

    def _validate_graph_token(self, token: str):
        claims = self._decode_jwt_claims(token)
        audience = claims.get("aud")
        roles = self._list_claim(claims.get("roles"))
        scopes = self._split_scope_claim(claims.get("scp"))
        permissions = roles + scopes

        if audience == SHAREPOINT_REST_TOKEN_AUDIENCE:
            raise RuntimeError(
                "invalid Microsoft Graph token audience. "
                "The token was issued for SharePoint REST instead of Microsoft Graph; "
                "make sure requests use scope {0!r} and no Office365 REST _api "
                "client path remains. tenant={1!r} aud={2!r}".format(
                    GRAPH_SCOPE[0], self.tenant_id, audience
                )
            )

        if audience not in GRAPH_TOKEN_AUDIENCES:
            raise RuntimeError(
                "invalid Microsoft Graph token audience "
                "tenant={0!r} aud={1!r}".format(self.tenant_id, audience)
            )

        if not any(permission.startswith("Sites.") for permission in permissions):
            raise RuntimeError(
                "Microsoft Graph application permission is missing. "
                "Grant Microsoft Graph Application permission Sites.Read.All "
                "for reads or Sites.ReadWrite.All/Sites.FullControl.All for writes, "
                "then complete admin consent. tenant={0!r} roles={1!r} scp={2!r}".format(
                    self.tenant_id, roles, scopes
                )
            )

    @staticmethod
    def _split_scope_claim(scope_claim: Any) -> List[str]:
        if not scope_claim:
            return []
        if isinstance(scope_claim, str):
            return [scope for scope in scope_claim.split() if scope]
        return []

    @staticmethod
    def _list_claim(claim: Any) -> List[str]:
        if isinstance(claim, str):
            return [claim] if claim else []
        if isinstance(claim, list):
            return [value for value in claim if isinstance(value, str) and value]
        return []

    @staticmethod
    def _decode_jwt_claims(token: str) -> Dict[str, Any]:
        try:
            payload = token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            return json.loads(base64.urlsafe_b64decode(payload).decode("utf-8"))
        except (IndexError, ValueError, UnicodeDecodeError) as exc:
            raise RuntimeError("failed to decode Microsoft Graph token claims") from exc

    def _request(
        self,
        method: str,
        path_or_url: str,
        expected_status: Iterable[int] = (200, 201),
        **kwargs,
    ) -> requests.Response:
        url = self._to_url(path_or_url)
        if self._is_sharepoint_rest_url(url):
            raise RuntimeError(
                "SharePoint REST _api calls are not supported. "
                "simple-sharepoint uses Microsoft Graph only; received url={0!r}".format(
                    url
                )
            )

        headers = dict(kwargs.pop("headers", {}) or {})
        if self._needs_graph_auth(url):
            headers["Authorization"] = "Bearer {0}".format(self._get_access_token())

        response = self._session.request(method, url, headers=headers, **kwargs)
        if response.status_code not in tuple(expected_status):
            raise GraphRequestError(method, url, response)

        return response

    def _request_json(
        self,
        method: str,
        path_or_url: str,
        expected_status: Iterable[int] = (200, 201),
        **kwargs,
    ) -> Dict[str, Any]:
        response = self._request(method, path_or_url, expected_status, **kwargs)
        if not response.content:
            return {}
        return response.json()

    @staticmethod
    def _to_url(path_or_url: str) -> str:
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            return path_or_url
        return "{0}/{1}".format(GRAPH_ROOT, path_or_url.lstrip("/"))

    @staticmethod
    def _needs_graph_auth(url: str) -> bool:
        return url.startswith("{0}/".format(GRAPH_ROOT))

    @staticmethod
    def _is_sharepoint_rest_url(url: str) -> bool:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        return hostname.endswith(".sharepoint.com") and "/_api/" in parsed.path

    def _drive_item_path(self, drive_path: str, action: Optional[str] = None) -> str:
        site_id = self._site_graph_id()
        encoded_path = quote(self._normalize_drive_path(drive_path), safe="/")

        if not encoded_path:
            if action:
                return "sites/{0}/drive/root/{1}".format(site_id, action)
            return "sites/{0}/drive/root".format(site_id)

        if action:
            return "sites/{0}/drive/root:/{1}:/{2}".format(
                site_id, encoded_path, action
            )
        return "sites/{0}/drive/root:/{1}".format(site_id, encoded_path)

    def _upload_file(self, src: str, drive_file_path: str) -> Dict[str, Any]:
        file_size = os.path.getsize(src)
        if file_size <= SIMPLE_UPLOAD_MAX_SIZE:
            return self._upload_file_simple(src, drive_file_path)
        return self._upload_file_session(src, drive_file_path, file_size)

    def _upload_file_simple(self, src: str, drive_file_path: str) -> Dict[str, Any]:
        with open(src, "rb") as f:
            return self._request_json(
                "PUT",
                self._drive_item_path(drive_file_path, "content"),
                headers={"Content-Type": "application/octet-stream"},
                data=f,
            )

    def _upload_file_session(
        self,
        src: str,
        drive_file_path: str,
        file_size: int,
    ) -> Dict[str, Any]:
        filename = os.path.basename(drive_file_path)
        session = self._request_json(
            "POST",
            self._drive_item_path(drive_file_path, "createUploadSession"),
            json={
                "item": {
                    "@microsoft.graph.conflictBehavior": "replace",
                    "name": filename,
                }
            },
        )
        upload_url = session["uploadUrl"]
        response = None

        with open(src, "rb") as f:
            offset = 0
            while offset < file_size:
                chunk = f.read(UPLOAD_CHUNK_SIZE)
                chunk_length = len(chunk)
                end = offset + chunk_length - 1
                headers = {
                    "Content-Length": str(chunk_length),
                    "Content-Range": "bytes {0}-{1}/{2}".format(
                        offset, end, file_size
                    ),
                }
                response = self._session.put(upload_url, headers=headers, data=chunk)
                if response.status_code not in (200, 201, 202):
                    raise GraphRequestError("PUT", upload_url, response)

                print_upload_progress(end + 1)
                offset += chunk_length

        if response is None or not response.content:
            return {}
        return response.json()

    def _ensure_folder(self, drive_path: str):
        current_path = ""
        for segment in self._split_drive_path(drive_path):
            next_path = self._join_drive_path(current_path, segment)
            item = self._get_drive_item(next_path)

            if item is None:
                self._create_folder(current_path, segment)
            elif "folder" not in item:
                raise NotADirectoryError(next_path)

            current_path = next_path

    def _get_drive_item(self, drive_path: str) -> Optional[Dict[str, Any]]:
        path = "{0}?$select=id,name,folder,file".format(
            self._drive_item_path(drive_path)
        )
        response = self._request("GET", path, expected_status=(200, 404))
        if response.status_code == 404:
            return None
        return response.json()

    def _create_folder(self, parent_drive_path: str, name: str):
        try:
            self._request_json(
                "POST",
                self._drive_item_path(parent_drive_path, "children"),
                json={
                    "name": name,
                    "folder": {},
                    "@microsoft.graph.conflictBehavior": "fail",
                },
            )
        except GraphRequestError as exc:
            item = self._get_drive_item(self._join_drive_path(parent_drive_path, name))
            if exc.status_code != 409 or item is None or "folder" not in item:
                raise

    def _to_drive_path(self, path: str) -> str:
        parsed = urlparse(path)
        if parsed.scheme and parsed.netloc:
            path = parsed.path

        path = unquote(path).strip("/")
        site_path = self._site_path.strip("/")

        if site_path and path == site_path:
            path = ""
        elif site_path and path.startswith("{0}/".format(site_path)):
            path = path[len(site_path) + 1 :]

        for library_name in ("Shared Documents", "Documents"):
            if path == library_name:
                return ""
            if path.startswith("{0}/".format(library_name)):
                return path[len(library_name) + 1 :]

        return self._normalize_drive_path(path)

    @staticmethod
    def _normalize_drive_path(path: str) -> str:
        return "/".join(part for part in path.replace("\\", "/").split("/") if part)

    @staticmethod
    def _split_drive_path(path: str) -> List[str]:
        return [part for part in path.replace("\\", "/").split("/") if part]

    @staticmethod
    def _join_drive_path(*parts: str) -> str:
        return "/".join(
            part.strip("/")
            for part in parts
            if part and part.strip("/")
        )
