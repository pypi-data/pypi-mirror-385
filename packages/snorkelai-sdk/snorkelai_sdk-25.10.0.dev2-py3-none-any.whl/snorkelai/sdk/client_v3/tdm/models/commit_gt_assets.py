from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

T = TypeVar("T", bound="CommitGTAssets")


@attrs.define
class CommitGTAssets:
    """
    Attributes:
        application_uid (int):
        node_uid (int):
    """

    application_uid: int
    node_uid: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        application_uid = self.application_uid
        node_uid = self.node_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "application_uid": application_uid,
                "node_uid": node_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        application_uid = d.pop("application_uid")

        node_uid = d.pop("node_uid")

        obj = cls(
            application_uid=application_uid,
            node_uid=node_uid,
        )
        obj.additional_properties = d
        return obj

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
