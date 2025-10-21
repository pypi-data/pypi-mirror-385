from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DescribedByT")


@_attrs_define
class DescribedByT:
    """
    Example:
        {'href': 'https://api.com/swagger/...', 'type': 'application/openapi3+json'}

    Attributes:
        href (Union[Unset, str]):  Example: https://api.com/swagger/....
        type_ (Union[Unset, str]):  Example: application/openapi3+json.
    """

    href: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        href = self.href

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if href is not UNSET:
            field_dict["href"] = href
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        href = d.pop("href", UNSET)

        type_ = d.pop("type", UNSET)

        described_by_t = cls(
            href=href,
            type_=type_,
        )

        described_by_t.additional_properties = d
        return described_by_t

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
