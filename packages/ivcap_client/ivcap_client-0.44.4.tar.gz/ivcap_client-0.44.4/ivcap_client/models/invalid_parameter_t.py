from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InvalidParameterT")


@_attrs_define
class InvalidParameterT:
    """InvalidParameterT is the error returned when a parameter has the wrong value.

    Example:
        {'message': 'cannot parse date', 'name': 'timestamp', 'value': 'today'}

    Attributes:
        message (str): message describing expected type or pattern. Example: cannot parse date.
        name (str): name of parameter. Example: timestamp.
        value (Union[Unset, str]): provided parameter value. Example: today.
    """

    message: str
    name: str
    value: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        name = self.name

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
                "name": name,
            }
        )
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        message = d.pop("message")

        name = d.pop("name")

        value = d.pop("value", UNSET)

        invalid_parameter_t = cls(
            message=message,
            name=name,
            value=value,
        )

        invalid_parameter_t.additional_properties = d
        return invalid_parameter_t

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
