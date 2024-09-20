Simple way to handle teams workflow message with python.
It supports sending message cards to the Teams channel

## Installation

install the latest stable version using `pip`

```shell
$ pip install simple-msteams
```

## Usage

```python
from simple_msteams.client import Client

url = < WORKFLOW URL >
timeout = < TIMEOUT > # default 15 seconds

c = Client(url) # if you set a timeout, use to c = Client(url, timeout)
```


## Functions

### safe_send

This function performs the function of sending messages to the teams.

```python
# string or dict
# string: "this is sample message"
# dictionary: '{"type": "TextBlock", "text": "this is sample message", "weight": "bolder", "size": "medium"}'
msg = < MESSAGE >

c.safe_send(msg)
```

## Use console scripts

```shell
# timeout not required. default 15
simple_msteams --url < WORLFLOW URL > --msg < MESSAGE > --timeout < TIMEOUT >
```

Example

```shell
# timeout not required. default 15
simple_msteams --url 'http://test.workflow.url' --msg 'this is sample message' --timeout 30

# if use dictionary
simple_msteams --url 'http://test.workflow.url' --msg '{\"type\": \"TextBlock\", \"text\": \"this is sample message\", \"weight\": \"bolder\", \"size\": \"medium\"}' --timeout 30
```