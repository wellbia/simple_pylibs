from office365.runtime.client_request_exception import ClientRequestException
from typing import Any


def check_path_exists(ctx: Any, path: str) -> bool:
    if not path:
        return []

    try:
        return ctx.web.get_folder_by_server_relative_url(path).get().execute_query().exists
    except ClientRequestException as e:
        if e.response.status_code == 404:
            return None
        else:
            raise ValueError(e.response.text)

def create_folder(ctx: Any, path: str):
    if not path:
        return []

    ctx.web.folders.add(path).execute_query()

def print_upload_progress(offset: int):
    print("Uploaded '{0}' bytes...".format(offset))  