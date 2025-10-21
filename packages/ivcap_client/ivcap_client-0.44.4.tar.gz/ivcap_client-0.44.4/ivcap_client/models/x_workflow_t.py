from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.x_basic_workflow_opts_t import XBasicWorkflowOptsT


T = TypeVar("T", bound="XWorkflowT")


@_attrs_define
class XWorkflowT:
    """Defines the workflow to use to execute this service. Currently supported 'types' are 'basic'
    and 'argo'. In case of 'basic', use the 'basic' element for further parameters. In the current implementation
    'opts' is expected to contain the same schema as 'basic'

       Example:
           {'argo': 'Eos est vitae quos consequatur.', 'basic': {'command': ['/bin/sh', '-c', 'echo $PATH'], 'cpu':
               {'limit': '100m', 'request': '10m'}, 'ephemeral-storage': {'limit': '4Gi', 'request': '2Gi'}, 'gpu-number': 2,
               'gpu-type': 'nvidia-tesla-t4', 'image': 'alpine', 'image-pull-policy': 'Aliquam qui qui voluptates quo.',
               'memory': {'limit': '100Mi', 'request': '10Mi'}, 'shared-memory': '1Gi'}, 'type': 'basic'}

       Attributes:
           type_ (str): Type of workflow Example: basic.
           argo (Union[Unset, Any]): Defines the workflow using argo's WF schema Example: Et suscipit voluptatum qui earum
               inventore..
           basic (Union[Unset, XBasicWorkflowOptsT]):  Example: {'command': ['/bin/sh', '-c', 'echo $PATH'], 'cpu':
               {'limit': '100m', 'request': '10m'}, 'ephemeral-storage': {'limit': '4Gi', 'request': '2Gi'}, 'gpu-number': 2,
               'gpu-type': 'nvidia-tesla-t4', 'image': 'alpine', 'image-pull-policy': 'Blanditiis quos officia.', 'memory':
               {'limit': '100Mi', 'request': '10Mi'}, 'shared-memory': '1Gi'}.
    """

    type_: str
    argo: Union[Unset, Any] = UNSET
    basic: Union[Unset, "XBasicWorkflowOptsT"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        argo = self.argo

        basic: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.basic, Unset):
            basic = self.basic.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if argo is not UNSET:
            field_dict["argo"] = argo
        if basic is not UNSET:
            field_dict["basic"] = basic

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.x_basic_workflow_opts_t import XBasicWorkflowOptsT

        d = src_dict.copy()
        type_ = d.pop("type")

        argo = d.pop("argo", UNSET)

        _basic = d.pop("basic", UNSET)
        basic: Union[Unset, XBasicWorkflowOptsT]
        if isinstance(_basic, Unset):
            basic = UNSET
        else:
            basic = XBasicWorkflowOptsT.from_dict(_basic)

        x_workflow_t = cls(
            type_=type_,
            argo=argo,
            basic=basic,
        )

        x_workflow_t.additional_properties = d
        return x_workflow_t

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
