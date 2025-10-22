from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PreviewSpecRequestHeaders")


@_attrs_define
class PreviewSpecRequestHeaders:
    """ Those headers will be set in all requests to your preview. This is especially useful to set the Authorization
    header.

     """

    additional_properties: dict[str, str] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        
        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        if not src_dict:
            return None
        d = src_dict.copy()
        preview_spec_request_headers = cls(
        )


        preview_spec_request_headers.additional_properties = d
        return preview_spec_request_headers

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> str:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: str) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
