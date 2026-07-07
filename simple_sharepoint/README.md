Simple way to handle sharepoint with python.
Provides the ability to upload files and directories. 

This package authenticates with Microsoft Entra ID client credentials and uses
Microsoft Graph for SharePoint document library access.

## Installation

install the latest stable version using `pip`

```shell
$ pip install simple-sharepoint
```

## Usage

```python
from simple_sharepoint.client import Client

client_id = < CLIENT_ID >
client_secret = < CLIENT_SECRET >
tenant_id = < TENANT_ID >
base_url = < BASE URL >

c = Client(client_id, client_secret, base_url, tenant_id)
```

- <b>TENANT_ID</b> can be either the tenant ID or tenant domain, such as `contoso.onmicrosoft.com`.<br>
If omitted, it is inferred from the SharePoint host name. For example, `https://contoso.sharepoint.com` becomes `contoso.onmicrosoft.com`.

- See the link below for instructions on creating <b>CLIENT_ID</b> and <b>CLIENT_SECRET</b> for Entra ID app authentication.<br>
[Make Token](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app)

- Grant Microsoft Graph application permission for the target SharePoint site and complete admin consent.<br>
Use `Sites.Read.All` for read-only workflows, or `Sites.ReadWrite.All` / `Sites.FullControl.All` for uploads and folder creation.

- <b>BASE_URL</b> refers to the main URL of the sharepoint.<br>
( format ) https://<SHAREPOINT_DOMAIN>/sites/<SHAREPOINT_SITE><br>
( ex ) `https://test.sharepoint.com/sites/testsite`

- SharePoint paths may use the existing server-relative format, such as `/sites/testsite/Shared Documents/excel/example`.<br>
The site prefix and default document library name are normalized to Microsoft Graph drive-root paths internally.


## Functions

### upload_file

A function that uploads a specific file to sharepoint.

```python
default_path = < SHAREPOINT_BASE_PATH >
src = < LOCAL_FILE_PATH >
dst = default_path + < SHAREPOINT_TARGET_PATH >

upload_file(src, dst)
```

- <b><i>SHAREPOINT_BASE_PATH</i></b> refers to the default path for a sharepoint document entry.<br>
( format ) /sites/<SHAREPOINT_SITE>/Shared Documents<br>
( ex ) `/sites/testsite/Shared Documents`

- <b><i>LOCAL_FILE_PATH</i></b> means the path to the file to be uploaded.<br>
( ex ) `/home/ubuntu/test.txt`

- <b><i>SHAREPOINT_TARGET_PATH</i></b> means the actual path to be uploaded to sharepoint.<br>
Think of the document menu in sharepoint as the root directory and enter the path thereafter.<br>
You do not need to include the file name.<br>
( ex ) `excel/example`

- If you run it as above, it will be uploaded as below.<br>
`/sites/testsite/Shared Documents/excel/example/test.txt`


### upload_dir

A function that uploads a particular directory and all its contents under the directory to sharepoint.

```python
default_path = < SHAREPOINT_BASE_PATH >
src = < LOCAL_DIR_PATH >
dst = default_path + < SHAREPOINT_TARGET_PATH >

upload_dir(src, dst)
```

- <b><i>SHAREPOINT_BASE_PATH</i></b>, <b><i>SHAREPIONT_TARGET_PATH</i></b> See item upload_file

- <b><i>LOCAL_DIR_PATH</i></b> means the path to the directory to be uploaded.<br>
( ex ) `/home/ubuntu/files`

### download_file

A function that downloads a specific file from the sharepoint.

```python
default_path = < SHAREPOINT_BASE_PATH >
src = default_path + < SHAREPOINT_TARGET_PATH >
dst = < LOCAL_FILE_PATH >

download_file(src, dst)
```

- <b><i>SHAREPOINT_BASE_PATH</i></b>, <b><i>SHAREPIONT_TARGET_PATH</i></b> See item upload_file

- The download_file function requires you to specify the file name to be stored in <b><i>LOCAL_FILE_PATH</i></b>.
( ex ) `/home/ubuntu/files/test.txt`


### download_dir

A function that downloads a particular directory in the sharepoint and all the contents under it.

```python
default_path = < SHAREPOINT_BASE_PATH >
src = default_path + < SHAREPOINT_TARGET_PATH >
dst = < LOCAL_DIR_PATH >

download_dir(src, dst)
```

- <b><i>SHAREPOINT_BASE_PATH</i></b>, <b><i>SHAREPIONT_TARGET_PATH</i></b>, <b><i>LOCAL_DIR_PATH</i></b> See item upload_dir


### list_dir

A function that listing a particular directory in the sharepoint and all the contents under it.

```python
default_path = < SHAREPOINT_BASE_PATH >
src = default_path + < SHAREPOINT_TARGET_PATH >

list_dir(src)
```

- <b><i>SHAREPOINT_BASE_PATH</i></b>, <b><i>SHAREPIONT_TARGET_PATH</i></b> See item upload_dir


## Use console scripts

```shell
simple-sharepoint-cli < FILE_PATH > --client-id < CLIENT_ID > --client-secret < CLIENT_SECRET > --tenant-id < TENANT_ID > --base-url < BASE_URL > --default-path < DEFAULT_PATH > --remote-dir < REMOTE_DIR >
```

- <b><i>CLIENT_ID</i></b>, <b><i>CLIENT_SECRET</i></b>, <b><i>TENANT_ID</i></b>, <b><i>BASE_URL</i></b> See item Usage.
- <b><i>DEFAULT_PATH</i></b> See upload_dir. same SHAREPOINT_BASE_PATH
- <b><i>REMOTE_DIR</i></b> See upload_dir. same SHAREPOINT_TARGET_PATH

## Third Party Libraries and Dependencies

- [Microsoft Authentication Library (MSAL) for Python](https://pypi.org/project/msal/)
- [Requests](https://pypi.org/project/requests/)
