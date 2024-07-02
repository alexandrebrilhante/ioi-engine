import socket
from os import environ
from typing import Callable, Dict, Optional
from uuid import uuid1

from fastapi import FastAPI
from pydantic import BaseModel
from redis import Redis
from redis.commands.json.path import Path
from simplefix import FixMessage

from ioi.constants import FIX_TAGS

app = FastAPI()
r = Redis(host=environ["REDIS_SERVER"], port=6379, db=0)


class IOI(BaseModel):
    """
    Represents an Indication of Interest (IOI) message.

    Attributes:
        ioi_id (str): The unique identifier for the IOI, if any.
        ioi_trans_type (str): The type of IOI transaction.
        ioi_ref_id (str | None): The reference identifier for the IOI, if any.
        symbol (str): The symbol of the instrument.
        side (str): The side of the IOI (buy or sell).
        ioi_qty (str): The quantity of the instrument.
        price (str): The price of the instrument.
        checksum (str): The checksum value for the IOI.
    """

    ioi_id: str | None
    ioi_trans_type: str
    ioi_ref_id: str | None
    symbol: str
    side: str
    ioi_qty: str
    price: str
    checksum: str


class IndicationOfInterest:
    """
    Represents an Indication of Interest (IOI) message.

    Args:
        **kwargs: Keyword arguments representing the IOI message fields.

    Attributes:
        message (simplefix.FixMessage): The FIX message object representing the IOI.
    """

    def __init__(self, **kwargs) -> None:
        self.message = FixMessage()

        self._set_headers()

        for key, value in kwargs.items():
            if key in self.FIX_TAGS:
                self.message.append_pair(FIX_TAGS[key], value)

        if "checksum" not in kwargs:
            self.message.append_pair(10, environ["CHECKSUM"])

    def _set_headers(self) -> None:
        """
        Sets the header fields of the IOI message.
        """
        self.message.append_pair(8, "FIX.4.4", header=True)
        self.message.append_pair(35, 6, header=True)
        self.message.append_pair(49, environ["SENDER"], header=True)
        self.message.append_pair(56, environ["TARGET"], header=True)
        self.message.append_pair(34, 4684, header=True)
        self.message.append_time(52, header=True)

    def _send(self) -> bytes:
        """
        Sends the IOI message over a TCP socket.

        Returns:
            bytes: The encoded IOI message.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((environ["HOST"], environ["PORT"]))
            s.sendall(self.message.encode())

    def submit(self) -> Callable:
        """
        Submits the IOI message.

        Returns:
            Callable: A function that sends the IOI message.
        """
        assert (
            self.message["symbol"] is not None
            and self.message["side"] is not None
            and self.message["ioi_qty"] is not None
        ), "Symbol, side, and IOI quantity are required..."

        i = str(uuid1())

        self.message.append_pair(23, i)
        self.message.append_pair(26, i)
        self.message.append_pair(28, "N")

        r.json().set(f"ioi:{i}", Path.root_path(), self.message.to_string())

        return self._send()

    def replace(self) -> Callable:
        """
        Replaces an existing IOI message.

        Returns:
            Callable: A function that sends the replaced IOI message.
        """
        ioi_ref_id = self.message["ioi_ref_id"]

        assert ioi_ref_id is not None, "IOI ref ID required..."

        if r.exists(f"ioi:{ioi_ref_id}"):
            self.message.append_pair(26, self.message["ioi_ref_id"])
            self.message.append_pair(28, "R")

            r.json().set(
                f"ioi:{ioi_ref_id}", Path.root_path(), self.message.to_string()
            )

            return self._send()

    def cancel(self) -> Callable:
        """
        Cancels an existing IOI message.

        Returns:
            Callable: A function that sends the canceled IOI message.
        """
        ioi_ref_id = self.message["ioi_ref_id"]

        assert ioi_ref_id is not None, "IOI ref ID required..."

        if r.exists(f"ioi:{ioi_ref_id}"):
            self.message.append_pair(26, ioi_ref_id)
            self.message.append_pair(28, "C")

            r.json().set(
                f"ioi:{ioi_ref_id}", Path.root_path(), self.message.to_string()
            )

            return self._send()


@app.get("/api/v1/ioi/submit")
def submit(tags: Dict[str, Optional[int | str]]):
    """
    Submit an indication of interest.

    Args:
        tags (Dict[str, Optional[int | str]]): A dictionary containing the tags for the indication of interest.

    Returns:
        Dict[str, str]: A dictionary with the status of the submission.

    """
    ioi = IndicationOfInterest(tags)
    ioi.submit()

    return {"status": "submitted"}


@app.get("/api/v1/ioi/replace")
def replace(tags: Dict[str, Optional[int | str]]):
    """
    Replaces the indication of interest (IOI) based on the provided tags.

    Args:
        tags (Dict[str, Optional[int | str]]): A dictionary containing the tags for the IOI.

    Returns:
        dict: A dictionary with the status of the replacement operation.
    """
    ioi = IndicationOfInterest(tags)
    ioi.replace()

    return {"status": "replaced"}


@app.get("/api/v1/ioi/cancel")
def cancel(tags: Dict[str, Optional[int | str]]):
    """
    Cancel an indication of interest (IOI) based on the provided tags.

    Args:
        tags (Dict[str, Optional[int | str]]): A dictionary containing the tags for the IOI.

    Returns:
        dict: A dictionary with the status of the cancellation.

    """
    ioi = IndicationOfInterest(tags)
    ioi.cancel()

    return {"status": "cancelled"}
