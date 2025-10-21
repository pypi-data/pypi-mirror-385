from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProductListItemT")


@_attrs_define
class ProductListItemT:
    """
    Example:
        {'data-href': 'https://api.ivcap.net/1/artifacts/.../data', 'href': 'https://api.ivcap.net/1/artifacts/...',
            'id': 'Qui suscipit voluptas quo.', 'mime-type': 'Et est reiciendis enim adipisci et quibusdam.', 'name':
            'Voluptas consectetur cumque debitis.', 'size': 6093748895470261359, 'status': 'Voluptas ut aut placeat autem
            aut.'}

    Attributes:
        href (str):  Example: https://api.ivcap.net/1/artifacts/....
        id (str):  Example: Autem id dolorum sed voluptatem..
        status (str):  Example: Repudiandae omnis ipsam animi tempore..
        data_href (Union[Unset, str]):  Example: https://api.ivcap.net/1/artifacts/.../data.
        mime_type (Union[Unset, str]):  Example: Id blanditiis..
        name (Union[Unset, str]):  Example: Nulla est vel reiciendis facere inventore..
        size (Union[Unset, int]):  Example: 4028534825099521728.
    """

    href: str
    id: str
    status: str
    data_href: Union[Unset, str] = UNSET
    mime_type: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    size: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        href = self.href

        id = self.id

        status = self.status

        data_href = self.data_href

        mime_type = self.mime_type

        name = self.name

        size = self.size

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "href": href,
                "id": id,
                "status": status,
            }
        )
        if data_href is not UNSET:
            field_dict["data-href"] = data_href
        if mime_type is not UNSET:
            field_dict["mime-type"] = mime_type
        if name is not UNSET:
            field_dict["name"] = name
        if size is not UNSET:
            field_dict["size"] = size

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        href = d.pop("href")

        id = d.pop("id")

        status = d.pop("status")

        data_href = d.pop("data-href", UNSET)

        mime_type = d.pop("mime-type", UNSET)

        name = d.pop("name", UNSET)

        size = d.pop("size", UNSET)

        product_list_item_t = cls(
            href=href,
            id=id,
            status=status,
            data_href=data_href,
            mime_type=mime_type,
            name=name,
            size=size,
        )

        product_list_item_t.additional_properties = d
        return product_list_item_t

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
