from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.dashboard_list_item import DashboardListItem


T = TypeVar("T", bound="DashboardListRT")


@_attrs_define
class DashboardListRT:
    """
    Example:
        {'items': [{'id': 3, 'title': 'Kubernetes Cluster Monitoring', 'uid': 'aeawr2d4xw7pcc', 'url':
            '/d/aeawr2d4xw7pcc'}, {'id': 3, 'title': 'Kubernetes Cluster Monitoring', 'uid': 'aeawr2d4xw7pcc', 'url':
            '/d/aeawr2d4xw7pcc'}, {'id': 3, 'title': 'Kubernetes Cluster Monitoring', 'uid': 'aeawr2d4xw7pcc', 'url':
            '/d/aeawr2d4xw7pcc'}]}

    Attributes:
        items (list['DashboardListItem']): Dashboards Example: [{'id': 3, 'title': 'Kubernetes Cluster Monitoring',
            'uid': 'aeawr2d4xw7pcc', 'url': '/d/aeawr2d4xw7pcc'}, {'id': 3, 'title': 'Kubernetes Cluster Monitoring', 'uid':
            'aeawr2d4xw7pcc', 'url': '/d/aeawr2d4xw7pcc'}, {'id': 3, 'title': 'Kubernetes Cluster Monitoring', 'uid':
            'aeawr2d4xw7pcc', 'url': '/d/aeawr2d4xw7pcc'}, {'id': 3, 'title': 'Kubernetes Cluster Monitoring', 'uid':
            'aeawr2d4xw7pcc', 'url': '/d/aeawr2d4xw7pcc'}].
    """

    items: list["DashboardListItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "items": items,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.dashboard_list_item import DashboardListItem

        d = src_dict.copy()
        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = DashboardListItem.from_dict(items_item_data)

            items.append(items_item)

        dashboard_list_rt = cls(
            items=items,
        )

        dashboard_list_rt.additional_properties = d
        return dashboard_list_rt

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
