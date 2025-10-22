from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.core_spec_configurations import CoreSpecConfigurations
  from ..models.flavor import Flavor
  from ..models.model_private_cluster import ModelPrivateCluster
  from ..models.repository import Repository
  from ..models.revision_configuration import RevisionConfiguration
  from ..models.runtime import Runtime
  from ..models.trigger import Trigger





T = TypeVar("T", bound="AgentSpec")


@_attrs_define
class AgentSpec:
    """ Agent specification

        Attributes:
            configurations (Union[Unset, CoreSpecConfigurations]): Optional configurations for the object
            enabled (Union[Unset, bool]): Enable or disable the resource
            flavors (Union[Unset, list['Flavor']]): Types of hardware available for deployments
            integration_connections (Union[Unset, list[str]]):
            policies (Union[Unset, list[str]]):
            private_clusters (Union[Unset, ModelPrivateCluster]): Private cluster where the model deployment is deployed
            revision (Union[Unset, RevisionConfiguration]): Revision configuration
            runtime (Union[Unset, Runtime]): Set of configurations for a deployment
            sandbox (Union[Unset, bool]): Sandbox mode
            description (Union[Unset, str]): Description, small description computed from the prompt
            repository (Union[Unset, Repository]): Repository
            triggers (Union[Unset, list['Trigger']]): Triggers to use your agent
     """

    configurations: Union[Unset, 'CoreSpecConfigurations'] = UNSET
    enabled: Union[Unset, bool] = UNSET
    flavors: Union[Unset, list['Flavor']] = UNSET
    integration_connections: Union[Unset, list[str]] = UNSET
    policies: Union[Unset, list[str]] = UNSET
    private_clusters: Union[Unset, 'ModelPrivateCluster'] = UNSET
    revision: Union[Unset, 'RevisionConfiguration'] = UNSET
    runtime: Union[Unset, 'Runtime'] = UNSET
    sandbox: Union[Unset, bool] = UNSET
    description: Union[Unset, str] = UNSET
    repository: Union[Unset, 'Repository'] = UNSET
    triggers: Union[Unset, list['Trigger']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        configurations: Union[Unset, dict[str, Any]] = UNSET
        if self.configurations and not isinstance(self.configurations, Unset) and not isinstance(self.configurations, dict):
            configurations = self.configurations.to_dict()
        elif self.configurations and isinstance(self.configurations, dict):
            configurations = self.configurations

        enabled = self.enabled

        flavors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.flavors, Unset):
            flavors = []
            for componentsschemas_flavors_item_data in self.flavors:
                if type(componentsschemas_flavors_item_data) is dict:
                    componentsschemas_flavors_item = componentsschemas_flavors_item_data
                else:
                    componentsschemas_flavors_item = componentsschemas_flavors_item_data.to_dict()
                flavors.append(componentsschemas_flavors_item)



        integration_connections: Union[Unset, list[str]] = UNSET
        if not isinstance(self.integration_connections, Unset):
            integration_connections = self.integration_connections



        policies: Union[Unset, list[str]] = UNSET
        if not isinstance(self.policies, Unset):
            policies = self.policies



        private_clusters: Union[Unset, dict[str, Any]] = UNSET
        if self.private_clusters and not isinstance(self.private_clusters, Unset) and not isinstance(self.private_clusters, dict):
            private_clusters = self.private_clusters.to_dict()
        elif self.private_clusters and isinstance(self.private_clusters, dict):
            private_clusters = self.private_clusters

        revision: Union[Unset, dict[str, Any]] = UNSET
        if self.revision and not isinstance(self.revision, Unset) and not isinstance(self.revision, dict):
            revision = self.revision.to_dict()
        elif self.revision and isinstance(self.revision, dict):
            revision = self.revision

        runtime: Union[Unset, dict[str, Any]] = UNSET
        if self.runtime and not isinstance(self.runtime, Unset) and not isinstance(self.runtime, dict):
            runtime = self.runtime.to_dict()
        elif self.runtime and isinstance(self.runtime, dict):
            runtime = self.runtime

        sandbox = self.sandbox

        description = self.description

        repository: Union[Unset, dict[str, Any]] = UNSET
        if self.repository and not isinstance(self.repository, Unset) and not isinstance(self.repository, dict):
            repository = self.repository.to_dict()
        elif self.repository and isinstance(self.repository, dict):
            repository = self.repository

        triggers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.triggers, Unset):
            triggers = []
            for componentsschemas_triggers_item_data in self.triggers:
                if type(componentsschemas_triggers_item_data) is dict:
                    componentsschemas_triggers_item = componentsschemas_triggers_item_data
                else:
                    componentsschemas_triggers_item = componentsschemas_triggers_item_data.to_dict()
                triggers.append(componentsschemas_triggers_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if configurations is not UNSET:
            field_dict["configurations"] = configurations
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if flavors is not UNSET:
            field_dict["flavors"] = flavors
        if integration_connections is not UNSET:
            field_dict["integrationConnections"] = integration_connections
        if policies is not UNSET:
            field_dict["policies"] = policies
        if private_clusters is not UNSET:
            field_dict["privateClusters"] = private_clusters
        if revision is not UNSET:
            field_dict["revision"] = revision
        if runtime is not UNSET:
            field_dict["runtime"] = runtime
        if sandbox is not UNSET:
            field_dict["sandbox"] = sandbox
        if description is not UNSET:
            field_dict["description"] = description
        if repository is not UNSET:
            field_dict["repository"] = repository
        if triggers is not UNSET:
            field_dict["triggers"] = triggers

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.core_spec_configurations import CoreSpecConfigurations
        from ..models.flavor import Flavor
        from ..models.model_private_cluster import ModelPrivateCluster
        from ..models.repository import Repository
        from ..models.revision_configuration import RevisionConfiguration
        from ..models.runtime import Runtime
        from ..models.trigger import Trigger
        if not src_dict:
            return None
        d = src_dict.copy()
        _configurations = d.pop("configurations", UNSET)
        configurations: Union[Unset, CoreSpecConfigurations]
        if isinstance(_configurations,  Unset):
            configurations = UNSET
        else:
            configurations = CoreSpecConfigurations.from_dict(_configurations)




        enabled = d.pop("enabled", UNSET)

        flavors = []
        _flavors = d.pop("flavors", UNSET)
        for componentsschemas_flavors_item_data in (_flavors or []):
            componentsschemas_flavors_item = Flavor.from_dict(componentsschemas_flavors_item_data)



            flavors.append(componentsschemas_flavors_item)


        integration_connections = cast(list[str], d.pop("integrationConnections", UNSET))


        policies = cast(list[str], d.pop("policies", UNSET))


        _private_clusters = d.pop("privateClusters", UNSET)
        private_clusters: Union[Unset, ModelPrivateCluster]
        if isinstance(_private_clusters,  Unset):
            private_clusters = UNSET
        else:
            private_clusters = ModelPrivateCluster.from_dict(_private_clusters)




        _revision = d.pop("revision", UNSET)
        revision: Union[Unset, RevisionConfiguration]
        if isinstance(_revision,  Unset):
            revision = UNSET
        else:
            revision = RevisionConfiguration.from_dict(_revision)




        _runtime = d.pop("runtime", UNSET)
        runtime: Union[Unset, Runtime]
        if isinstance(_runtime,  Unset):
            runtime = UNSET
        else:
            runtime = Runtime.from_dict(_runtime)




        sandbox = d.pop("sandbox", UNSET)

        description = d.pop("description", UNSET)

        _repository = d.pop("repository", UNSET)
        repository: Union[Unset, Repository]
        if isinstance(_repository,  Unset):
            repository = UNSET
        else:
            repository = Repository.from_dict(_repository)




        triggers = []
        _triggers = d.pop("triggers", UNSET)
        for componentsschemas_triggers_item_data in (_triggers or []):
            componentsschemas_triggers_item = Trigger.from_dict(componentsschemas_triggers_item_data)



            triggers.append(componentsschemas_triggers_item)


        agent_spec = cls(
            configurations=configurations,
            enabled=enabled,
            flavors=flavors,
            integration_connections=integration_connections,
            policies=policies,
            private_clusters=private_clusters,
            revision=revision,
            runtime=runtime,
            sandbox=sandbox,
            description=description,
            repository=repository,
            triggers=triggers,
        )


        agent_spec.additional_properties = d
        return agent_spec

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
