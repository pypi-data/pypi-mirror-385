from typing import Protocol
from twnet_parser.packer import Unpacker

class SnapItem(Protocol):
    item_name: str
    type_id: int
    id: int
    size: int
    def unpack(self, unpacker: Unpacker) -> bool:
        ...
    def pack(self) -> bytes:
        ...

