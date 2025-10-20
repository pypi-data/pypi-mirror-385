from typing import Protocol, Self

type JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
type JSONObj = dict[str, "JSON"]


class JSONSerializable(Protocol):
    """
    Protocol for objects which can be serialized/deserialized via json.
    """

    def to_json(self) -> JSONObj: ...

    @classmethod
    def from_json(cls, data: JSONObj) -> Self: ...
