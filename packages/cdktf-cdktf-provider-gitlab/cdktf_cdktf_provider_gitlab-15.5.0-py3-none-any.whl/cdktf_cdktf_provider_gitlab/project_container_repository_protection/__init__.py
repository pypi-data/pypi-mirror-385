r'''
# `gitlab_project_container_repository_protection`

Refer to the Terraform Registry for docs: [`gitlab_project_container_repository_protection`](https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class ProjectContainerRepositoryProtection(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.projectContainerRepositoryProtection.ProjectContainerRepositoryProtection",
):
    '''Represents a {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection gitlab_project_container_repository_protection}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        project: builtins.str,
        repository_path_pattern: builtins.str,
        minimum_access_level_for_delete: typing.Optional[builtins.str] = None,
        minimum_access_level_for_push: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection gitlab_project_container_repository_protection} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param project: ID or URL-encoded path of the project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection#project ProjectContainerRepositoryProtection#project}
        :param repository_path_pattern: Container repository path pattern protected by the protection rule. Wildcard character * allowed. Repository path pattern should start with the project's full path Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection#repository_path_pattern ProjectContainerRepositoryProtection#repository_path_pattern}
        :param minimum_access_level_for_delete: Minimum GitLab access level required to delete container images in the container registry. For example maintainer, owner, admin. Must be provided when ``minimum_access_level_for_push`` is not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection#minimum_access_level_for_delete ProjectContainerRepositoryProtection#minimum_access_level_for_delete}
        :param minimum_access_level_for_push: Minimum GitLab access level required to push container images to the container registry. For example maintainer, owner or admin. Must be provided when ``minimum_access_level_for_delete`` is not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection#minimum_access_level_for_push ProjectContainerRepositoryProtection#minimum_access_level_for_push}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fddc4a65e37f12d947aefc291966d3cd1461722ddf169a5780c5c56eb8636060)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ProjectContainerRepositoryProtectionConfig(
            project=project,
            repository_path_pattern=repository_path_pattern,
            minimum_access_level_for_delete=minimum_access_level_for_delete,
            minimum_access_level_for_push=minimum_access_level_for_push,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a ProjectContainerRepositoryProtection resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProjectContainerRepositoryProtection to import.
        :param import_from_id: The id of the existing ProjectContainerRepositoryProtection that should be imported. Refer to the {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProjectContainerRepositoryProtection to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__627c3728e8a4bf3be32765c49a6b7327aaa948031dce82ab95684f9d0398d71a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetMinimumAccessLevelForDelete")
    def reset_minimum_access_level_for_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumAccessLevelForDelete", []))

    @jsii.member(jsii_name="resetMinimumAccessLevelForPush")
    def reset_minimum_access_level_for_push(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumAccessLevelForPush", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="protectionRuleId")
    def protection_rule_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "protectionRuleId"))

    @builtins.property
    @jsii.member(jsii_name="minimumAccessLevelForDeleteInput")
    def minimum_access_level_for_delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minimumAccessLevelForDeleteInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumAccessLevelForPushInput")
    def minimum_access_level_for_push_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minimumAccessLevelForPushInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="repositoryPathPatternInput")
    def repository_path_pattern_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryPathPatternInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumAccessLevelForDelete")
    def minimum_access_level_for_delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimumAccessLevelForDelete"))

    @minimum_access_level_for_delete.setter
    def minimum_access_level_for_delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a84a9d7a26a3b9003528a7169c56a0113fa98ec85b29840bea08d1be6a00e53b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimumAccessLevelForDelete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minimumAccessLevelForPush")
    def minimum_access_level_for_push(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimumAccessLevelForPush"))

    @minimum_access_level_for_push.setter
    def minimum_access_level_for_push(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44681332f728dfb8e0ea5e308b6a68a43bb0c4539f1fdd6f8efe6ee63b40d0eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimumAccessLevelForPush", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0855a8221900b864b93acd23cf88d5ae1dc13f79f81fe412ed340b2b0715ddfe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repositoryPathPattern")
    def repository_path_pattern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryPathPattern"))

    @repository_path_pattern.setter
    def repository_path_pattern(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2f9bad79bc03478897858d584dce040d694a32813aec3f9dfe482b800495ab5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repositoryPathPattern", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.projectContainerRepositoryProtection.ProjectContainerRepositoryProtectionConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "project": "project",
        "repository_path_pattern": "repositoryPathPattern",
        "minimum_access_level_for_delete": "minimumAccessLevelForDelete",
        "minimum_access_level_for_push": "minimumAccessLevelForPush",
    },
)
class ProjectContainerRepositoryProtectionConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        project: builtins.str,
        repository_path_pattern: builtins.str,
        minimum_access_level_for_delete: typing.Optional[builtins.str] = None,
        minimum_access_level_for_push: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param project: ID or URL-encoded path of the project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection#project ProjectContainerRepositoryProtection#project}
        :param repository_path_pattern: Container repository path pattern protected by the protection rule. Wildcard character * allowed. Repository path pattern should start with the project's full path Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection#repository_path_pattern ProjectContainerRepositoryProtection#repository_path_pattern}
        :param minimum_access_level_for_delete: Minimum GitLab access level required to delete container images in the container registry. For example maintainer, owner, admin. Must be provided when ``minimum_access_level_for_push`` is not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection#minimum_access_level_for_delete ProjectContainerRepositoryProtection#minimum_access_level_for_delete}
        :param minimum_access_level_for_push: Minimum GitLab access level required to push container images to the container registry. For example maintainer, owner or admin. Must be provided when ``minimum_access_level_for_delete`` is not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection#minimum_access_level_for_push ProjectContainerRepositoryProtection#minimum_access_level_for_push}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe1b7ded1c9824dd0f9cb309f216dd51fde519bff3921e9484943bb440e0a1b2)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument repository_path_pattern", value=repository_path_pattern, expected_type=type_hints["repository_path_pattern"])
            check_type(argname="argument minimum_access_level_for_delete", value=minimum_access_level_for_delete, expected_type=type_hints["minimum_access_level_for_delete"])
            check_type(argname="argument minimum_access_level_for_push", value=minimum_access_level_for_push, expected_type=type_hints["minimum_access_level_for_push"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "project": project,
            "repository_path_pattern": repository_path_pattern,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if minimum_access_level_for_delete is not None:
            self._values["minimum_access_level_for_delete"] = minimum_access_level_for_delete
        if minimum_access_level_for_push is not None:
            self._values["minimum_access_level_for_push"] = minimum_access_level_for_push

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def project(self) -> builtins.str:
        '''ID or URL-encoded path of the project.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection#project ProjectContainerRepositoryProtection#project}
        '''
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_path_pattern(self) -> builtins.str:
        '''Container repository path pattern protected by the protection rule.

        Wildcard character * allowed. Repository path pattern should start with the project's full path

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection#repository_path_pattern ProjectContainerRepositoryProtection#repository_path_pattern}
        '''
        result = self._values.get("repository_path_pattern")
        assert result is not None, "Required property 'repository_path_pattern' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def minimum_access_level_for_delete(self) -> typing.Optional[builtins.str]:
        '''Minimum GitLab access level required to delete container images in the container registry.

        For example maintainer, owner, admin. Must be provided when ``minimum_access_level_for_push`` is not set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection#minimum_access_level_for_delete ProjectContainerRepositoryProtection#minimum_access_level_for_delete}
        '''
        result = self._values.get("minimum_access_level_for_delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minimum_access_level_for_push(self) -> typing.Optional[builtins.str]:
        '''Minimum GitLab access level required to push container images to the container registry.

        For example maintainer, owner or admin. Must be provided when ``minimum_access_level_for_delete`` is not set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_container_repository_protection#minimum_access_level_for_push ProjectContainerRepositoryProtection#minimum_access_level_for_push}
        '''
        result = self._values.get("minimum_access_level_for_push")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectContainerRepositoryProtectionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProjectContainerRepositoryProtection",
    "ProjectContainerRepositoryProtectionConfig",
]

publication.publish()

def _typecheckingstub__fddc4a65e37f12d947aefc291966d3cd1461722ddf169a5780c5c56eb8636060(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    project: builtins.str,
    repository_path_pattern: builtins.str,
    minimum_access_level_for_delete: typing.Optional[builtins.str] = None,
    minimum_access_level_for_push: typing.Optional[builtins.str] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__627c3728e8a4bf3be32765c49a6b7327aaa948031dce82ab95684f9d0398d71a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a84a9d7a26a3b9003528a7169c56a0113fa98ec85b29840bea08d1be6a00e53b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44681332f728dfb8e0ea5e308b6a68a43bb0c4539f1fdd6f8efe6ee63b40d0eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0855a8221900b864b93acd23cf88d5ae1dc13f79f81fe412ed340b2b0715ddfe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2f9bad79bc03478897858d584dce040d694a32813aec3f9dfe482b800495ab5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe1b7ded1c9824dd0f9cb309f216dd51fde519bff3921e9484943bb440e0a1b2(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    project: builtins.str,
    repository_path_pattern: builtins.str,
    minimum_access_level_for_delete: typing.Optional[builtins.str] = None,
    minimum_access_level_for_push: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
