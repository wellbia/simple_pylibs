Simple way to handle sftp with python.
Provides the ability to upload and download directories. 

## Installation

install the latest stable version using `pip`

```shell
$ pip install simple-sftp
```

## Usage

```python
from simple_sftp.client import Client

ip = < FTP SERVER IP >
user = < FTP LOGIN USER >
password = < FTP LOGIN PASSWORD > 
PORT = < FTP CONNECT PORT > # not required. default 22

c = Client(ip, user, password)
```


## Functions

### upload

A function that uploads a specific directories to ftp server.

```python
remote_path = < FTP SERVER REMOTE DIR PATH >
local_path = < LOCAL DIR PATH >

upload(remote_path, local_path)
```

### download

A function that downloads a specific directories to ftp server.

```python
remote_path = < FTP REMOTE DIR PATH >
local_path = < LOCAL DIR PATH >

download(remote_path, local_path)
```


## Use console scripts

```shell
simple-sftp-cli --ip < FTP SERVER IP > --user < FTP LOGIN USER > --pwd < FTP LOGIN PASSWORD > --local < LOCAL_DIR_PATH > --remote < FTP SERVER REMOTE DIR PATH >
```

Example

```shell
simple-sftp-cli --ip 123.456.789.123 --user user --pwd 1234 --local /home/user/abc --remote /home/my/abc
```

## Third Party Libraries and Dependencies

- [paramiko](https://pypi.org/project/paramiko/)