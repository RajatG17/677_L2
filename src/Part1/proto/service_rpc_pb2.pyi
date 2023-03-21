from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class lookupRequestMessage(_message.Message):
    __slots__ = ["stockname"]
    STOCKNAME_FIELD_NUMBER: _ClassVar[int]
    stockname: str
    def __init__(self, stockname: _Optional[str] = ...) -> None: ...

class lookupResponseMessage(_message.Message):
    __slots__ = ["error", "price", "quantity", "stockname"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    STOCKNAME_FIELD_NUMBER: _ClassVar[int]
    error: bool
    price: float
    quantity: int
    stockname: str
    def __init__(self, error: bool = ..., stockname: _Optional[str] = ..., price: _Optional[float] = ..., quantity: _Optional[int] = ...) -> None: ...

class orderRequestMessage(_message.Message):
    __slots__ = ["quantity", "stockname", "type"]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    STOCKNAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    quantity: int
    stockname: str
    type: str
    def __init__(self, stockname: _Optional[str] = ..., quantity: _Optional[int] = ..., type: _Optional[str] = ...) -> None: ...

class orderResponseMessage(_message.Message):
    __slots__ = ["error"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: bool
    def __init__(self, error: bool = ...) -> None: ...

class tradeRequestMessage(_message.Message):
    __slots__ = ["quantity", "stockname", "type"]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    STOCKNAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    quantity: int
    stockname: str
    type: str
    def __init__(self, stockname: _Optional[str] = ..., quantity: _Optional[int] = ..., type: _Optional[str] = ...) -> None: ...

class tradeResponseMessage(_message.Message):
    __slots__ = ["error", "transaction_number"]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    error: bool
    transaction_number: int
    def __init__(self, error: bool = ..., transaction_number: _Optional[int] = ...) -> None: ...
