import json

from datetime import datetime

from pyutils_spirit.util.json_util import deep_dumps


class Chat:

    def __init__(self):
        self.id: str | None = None
        self.avatar: str | None = None
        self.chat_name: str | None = None
        self.message: Message | None = None
        self.create_time: datetime | None = datetime.now()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "avatar": self.avatar,
            "chat_name": self.chat_name,
            "message": None if self.message is None else self.message.to_dict(),
            "create_time": self.create_time
        }

    def __str__(self) -> str:
        return str(self.to_dict())


class Message:

    def __init__(self):
        self.id: str | None = None
        self.sender: str | None = None
        self.receiver: str | None = None
        self.group: str | None = None
        self.content: str | bytes | None = None
        self.msg_type: int | None = None
        self.location: Location | None = None
        self.reference_msg: str | None = None
        self.create_time: datetime | None = datetime.now()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "group": self.group,
            "content": self.content,
            "msg_type": self.msg_type,
            "location": None if self.location is None else self.location.to_dict(),
            "reference_msg": self.reference_msg,
            "create_time": self.create_time
        }

    def __str__(self) -> str:
        return str(self.to_dict())


class Location:

    def __init__(self):
        self.id: str | None = None
        self.address: str | None = None
        self.latitude: float | None = None
        self.longitude: float | None = None
        self.create_time: datetime = datetime.now()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "create_time": self.create_time
        }

    def __str__(self) -> str:
        return str(self.to_dict())
