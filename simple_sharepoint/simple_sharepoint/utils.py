from typing import Any


def check_path_exists(ctx: Any, path: str) -> bool:
    if not path:
        return []

    try:
        return ctx.web.get_folder_by_server_relative_url(path).get().execute_query().exists
    except Exception as e:
        response = getattr(e, "response", None)
        status_code = getattr(response, "status_code", None)
        if status_code == 404:
            return None
        if response is not None:
            raise ValueError(response.text)
        raise

def create_folder(ctx: Any, path: str):
    if not path:
        return []

    ctx.web.folders.add(path).execute_query()

def print_upload_progress(offset: int):
    print("Uploaded '{0}' bytes...".format(offset))
