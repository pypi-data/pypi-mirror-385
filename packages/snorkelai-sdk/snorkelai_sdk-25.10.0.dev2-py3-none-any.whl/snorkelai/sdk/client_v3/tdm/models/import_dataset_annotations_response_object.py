from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

T = TypeVar("T", bound="ImportDatasetAnnotationsResponseObject")


@attrs.define
class ImportDatasetAnnotationsResponseObject:
    """
    Attributes:
        annotation_uid (int):
        source_uid (int):
        x_uid (str):
    """

    annotation_uid: int
    source_uid: int
    x_uid: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        annotation_uid = self.annotation_uid
        source_uid = self.source_uid
        x_uid = self.x_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_uid": annotation_uid,
                "source_uid": source_uid,
                "x_uid": x_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        annotation_uid = d.pop("annotation_uid")

        source_uid = d.pop("source_uid")

        x_uid = d.pop("x_uid")

        obj = cls(
            annotation_uid=annotation_uid,
            source_uid=source_uid,
            x_uid=x_uid,
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
