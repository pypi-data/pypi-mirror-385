from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.core_event import CoreEvent
  from ..models.metadata import Metadata
  from ..models.sandbox_spec import SandboxSpec





T = TypeVar("T", bound="Sandbox")


@_attrs_define
class Sandbox:
    """ Micro VM for running agentic tasks

        Attributes:
            events (Union[Unset, list['CoreEvent']]): Core events
            last_used_at (Union[Unset, str]): Last time the sandbox was used (read-only, managed by the system)
            metadata (Union[Unset, Metadata]): Metadata
            spec (Union[Unset, SandboxSpec]): Sandbox specification
            status (Union[Unset, str]): Sandbox status
            ttl (Union[Unset, int]): TTL timestamp for automatic deletion (optional, nil means no auto-deletion)
     """

    events: Union[Unset, list['CoreEvent']] = UNSET
    last_used_at: Union[Unset, str] = UNSET
    metadata: Union[Unset, 'Metadata'] = UNSET
    spec: Union[Unset, 'SandboxSpec'] = UNSET
    status: Union[Unset, str] = UNSET
    ttl: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        events: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.events, Unset):
            events = []
            for componentsschemas_core_events_item_data in self.events:
                if type(componentsschemas_core_events_item_data) is dict:
                    componentsschemas_core_events_item = componentsschemas_core_events_item_data
                else:
                    componentsschemas_core_events_item = componentsschemas_core_events_item_data.to_dict()
                events.append(componentsschemas_core_events_item)



        last_used_at = self.last_used_at

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if self.metadata and not isinstance(self.metadata, Unset) and not isinstance(self.metadata, dict):
            metadata = self.metadata.to_dict()
        elif self.metadata and isinstance(self.metadata, dict):
            metadata = self.metadata

        spec: Union[Unset, dict[str, Any]] = UNSET
        if self.spec and not isinstance(self.spec, Unset) and not isinstance(self.spec, dict):
            spec = self.spec.to_dict()
        elif self.spec and isinstance(self.spec, dict):
            spec = self.spec

        status = self.status

        ttl = self.ttl


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if events is not UNSET:
            field_dict["events"] = events
        if last_used_at is not UNSET:
            field_dict["lastUsedAt"] = last_used_at
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if spec is not UNSET:
            field_dict["spec"] = spec
        if status is not UNSET:
            field_dict["status"] = status
        if ttl is not UNSET:
            field_dict["ttl"] = ttl

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.core_event import CoreEvent
        from ..models.metadata import Metadata
        from ..models.sandbox_spec import SandboxSpec
        if not src_dict:
            return None
        d = src_dict.copy()
        events = []
        _events = d.pop("events", UNSET)
        for componentsschemas_core_events_item_data in (_events or []):
            componentsschemas_core_events_item = CoreEvent.from_dict(componentsschemas_core_events_item_data)



            events.append(componentsschemas_core_events_item)


        last_used_at = d.pop("lastUsedAt", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, Metadata]
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = Metadata.from_dict(_metadata)




        _spec = d.pop("spec", UNSET)
        spec: Union[Unset, SandboxSpec]
        if isinstance(_spec,  Unset):
            spec = UNSET
        else:
            spec = SandboxSpec.from_dict(_spec)




        status = d.pop("status", UNSET)

        ttl = d.pop("ttl", UNSET)

        sandbox = cls(
            events=events,
            last_used_at=last_used_at,
            metadata=metadata,
            spec=spec,
            status=status,
            ttl=ttl,
        )


        sandbox.additional_properties = d
        return sandbox

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
