import certifi
import typing
import requests


class Client:
    def __init__(self, hookurl: str, timeout: int = 15):
        self.hookurl = hookurl
        self.timeout = timeout

    def send(self, data: typing.Union[str, dict]) -> requests.Response:
        if isinstance(data, str):
            fdata = data.replace("\n", "\n\n")
            data = {
                "text": data,
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "type": "AdaptiveCard",
                            "version": "1.2",
                            "msteams": {"width": "full"},
                            "body": [{"type": "TextBlock", "text": fdata}],
                        },
                    }
                ],
            }
        elif isinstance(data, dict):
            data = {
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "type": "AdaptiveCard",
                            "version": "1.2",
                            "msteams": {"width": "full"},
                            "body": [data],
                        },
                    }
                ],
            }
        elif isinstance(data, list):
            data = {
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "type": "AdaptiveCard",
                            "version": "1.2",
                            "msteams": {"width": "full"},
                            "body": data,
                        },
                    }
                ],
            }

        return requests.post(
            self.hookurl,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=self.timeout,
            verify=certifi.where(),
        )

    def safe_send(self, data: typing.Union[str, dict]) -> requests.Response:
        try:
            return self.send(data)
        except:
            pass
