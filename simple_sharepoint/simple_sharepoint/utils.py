from typing import Any


def _require_graph_client(client: Any) -> Any:
    required_methods = ("_to_drive_path", "_get_drive_item", "_ensure_folder")
    if all(hasattr(client, method) for method in required_methods):
        return client

    raise TypeError(
        "simple_sharepoint utilities require simple_sharepoint.client.Client. "
        "Office365 REST ClientContext is not supported."
    )


def check_path_exists(ctx: Any, path: str) -> bool:
    if not path:
        return []

    client = _require_graph_client(ctx)
    item = client._get_drive_item(client._to_drive_path(path))
    if item is None:
        return None

    return "folder" in item


def create_folder(ctx: Any, path: str):
    if not path:
        return []

    client = _require_graph_client(ctx)
    client._ensure_folder(client._to_drive_path(path))


def print_upload_progress(offset: int):
    print("Uploaded '{0}' bytes...".format(offset))
