r'''
# `gitlab_group_access_token`

Refer to the Terraform Registry for docs: [`gitlab_group_access_token`](https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token).
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


class GroupAccessToken(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.groupAccessToken.GroupAccessToken",
):
    '''Represents a {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token gitlab_group_access_token}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        group: builtins.str,
        name: builtins.str,
        scopes: typing.Sequence[builtins.str],
        access_level: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        expires_at: typing.Optional[builtins.str] = None,
        rotation_configuration: typing.Optional[typing.Union["GroupAccessTokenRotationConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
        validate_past_expiration_date: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token gitlab_group_access_token} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param group: The ID or full path of the group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#group GroupAccessToken#group}
        :param name: The name of the group access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#name GroupAccessToken#name}
        :param scopes: The scopes of the group access token. Valid values are: ``api``, ``read_api``, ``read_registry``, ``write_registry``, ``read_virtual_registry``, ``write_virtual_registry``, ``read_repository``, ``write_repository``, ``create_runner``, ``manage_runner``, ``ai_features``, ``k8s_proxy``, ``read_observability``, ``write_observability``, ``self_rotate`` Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#scopes GroupAccessToken#scopes}
        :param access_level: The access level for the group access token. Valid values are: ``no one``, ``minimal``, ``guest``, ``planner``, ``reporter``, ``developer``, ``maintainer``, ``owner``. Default is ``maintainer``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#access_level GroupAccessToken#access_level}
        :param description: The description of the group access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#description GroupAccessToken#description}
        :param expires_at: When the token will expire, YYYY-MM-DD format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#expires_at GroupAccessToken#expires_at}
        :param rotation_configuration: The configuration for when to rotate a token automatically. Will not rotate a token until ``terraform apply`` is run. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#rotation_configuration GroupAccessToken#rotation_configuration}
        :param validate_past_expiration_date: Wether to validate if the expiration date is in the future. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#validate_past_expiration_date GroupAccessToken#validate_past_expiration_date}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfa859d58b20f46c1ff11372120d8c420b300a7cd2b1c6434a2911b8c0daf212)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = GroupAccessTokenConfig(
            group=group,
            name=name,
            scopes=scopes,
            access_level=access_level,
            description=description,
            expires_at=expires_at,
            rotation_configuration=rotation_configuration,
            validate_past_expiration_date=validate_past_expiration_date,
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
        '''Generates CDKTF code for importing a GroupAccessToken resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GroupAccessToken to import.
        :param import_from_id: The id of the existing GroupAccessToken that should be imported. Refer to the {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GroupAccessToken to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ae49a6a945065a47d08b3e502c96efe9180ab17f25b0faba500eaf870d25549)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putRotationConfiguration")
    def put_rotation_configuration(
        self,
        *,
        expiration_days: jsii.Number,
        rotate_before_days: jsii.Number,
    ) -> None:
        '''
        :param expiration_days: The duration (in days) the new token should be valid for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#expiration_days GroupAccessToken#expiration_days}
        :param rotate_before_days: The duration (in days) before the expiration when the token should be rotated. As an example, if set to 7 days, the token will rotate 7 days before the expiration date, but only when ``terraform apply`` is run in that timeframe. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#rotate_before_days GroupAccessToken#rotate_before_days}
        '''
        value = GroupAccessTokenRotationConfiguration(
            expiration_days=expiration_days, rotate_before_days=rotate_before_days
        )

        return typing.cast(None, jsii.invoke(self, "putRotationConfiguration", [value]))

    @jsii.member(jsii_name="resetAccessLevel")
    def reset_access_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessLevel", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetExpiresAt")
    def reset_expires_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpiresAt", []))

    @jsii.member(jsii_name="resetRotationConfiguration")
    def reset_rotation_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationConfiguration", []))

    @jsii.member(jsii_name="resetValidatePastExpirationDate")
    def reset_validate_past_expiration_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValidatePastExpirationDate", []))

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
    @jsii.member(jsii_name="active")
    def active(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "active"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="revoked")
    def revoked(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "revoked"))

    @builtins.property
    @jsii.member(jsii_name="rotationConfiguration")
    def rotation_configuration(
        self,
    ) -> "GroupAccessTokenRotationConfigurationOutputReference":
        return typing.cast("GroupAccessTokenRotationConfigurationOutputReference", jsii.get(self, "rotationConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "token"))

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "userId"))

    @builtins.property
    @jsii.member(jsii_name="accessLevelInput")
    def access_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="expiresAtInput")
    def expires_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expiresAtInput"))

    @builtins.property
    @jsii.member(jsii_name="groupInput")
    def group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationConfigurationInput")
    def rotation_configuration_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "GroupAccessTokenRotationConfiguration"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "GroupAccessTokenRotationConfiguration"]], jsii.get(self, "rotationConfigurationInput"))

    @builtins.property
    @jsii.member(jsii_name="scopesInput")
    def scopes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "scopesInput"))

    @builtins.property
    @jsii.member(jsii_name="validatePastExpirationDateInput")
    def validate_past_expiration_date_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "validatePastExpirationDateInput"))

    @builtins.property
    @jsii.member(jsii_name="accessLevel")
    def access_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessLevel"))

    @access_level.setter
    def access_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a91be87bbdcf2ce01cd80fea821e7bf0b967a17ee991718d91683e7962a11e3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32e98629b61be7b618497f7502f3c88a0685b31a353aad2044e299f49e6df582)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="expiresAt")
    def expires_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expiresAt"))

    @expires_at.setter
    def expires_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84d185b48954b46ef90c021b66859414cd3b3dc7d4928fe2f876b24b20134e56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expiresAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "group"))

    @group.setter
    def group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__520226349e5588723212ab72e0b2fa079fe712523614cefdf20f5067521b83e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "group", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f36b194ee52180ae6579bd4f040e05637ca64c92fd8c3ffa9ffe94cc4f21963f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scopes")
    def scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "scopes"))

    @scopes.setter
    def scopes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a9f6c0fda5dec57b9956bd4b4362aa8a7f2cb48e3b7334161d6e4ed488564c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scopes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="validatePastExpirationDate")
    def validate_past_expiration_date(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "validatePastExpirationDate"))

    @validate_past_expiration_date.setter
    def validate_past_expiration_date(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88e1a02ca28231e4fe89a2d9bdbeaa5ef18cdd5f89ea61c489f22c1217d145e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "validatePastExpirationDate", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.groupAccessToken.GroupAccessTokenConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "group": "group",
        "name": "name",
        "scopes": "scopes",
        "access_level": "accessLevel",
        "description": "description",
        "expires_at": "expiresAt",
        "rotation_configuration": "rotationConfiguration",
        "validate_past_expiration_date": "validatePastExpirationDate",
    },
)
class GroupAccessTokenConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        group: builtins.str,
        name: builtins.str,
        scopes: typing.Sequence[builtins.str],
        access_level: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        expires_at: typing.Optional[builtins.str] = None,
        rotation_configuration: typing.Optional[typing.Union["GroupAccessTokenRotationConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
        validate_past_expiration_date: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param group: The ID or full path of the group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#group GroupAccessToken#group}
        :param name: The name of the group access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#name GroupAccessToken#name}
        :param scopes: The scopes of the group access token. Valid values are: ``api``, ``read_api``, ``read_registry``, ``write_registry``, ``read_virtual_registry``, ``write_virtual_registry``, ``read_repository``, ``write_repository``, ``create_runner``, ``manage_runner``, ``ai_features``, ``k8s_proxy``, ``read_observability``, ``write_observability``, ``self_rotate`` Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#scopes GroupAccessToken#scopes}
        :param access_level: The access level for the group access token. Valid values are: ``no one``, ``minimal``, ``guest``, ``planner``, ``reporter``, ``developer``, ``maintainer``, ``owner``. Default is ``maintainer``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#access_level GroupAccessToken#access_level}
        :param description: The description of the group access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#description GroupAccessToken#description}
        :param expires_at: When the token will expire, YYYY-MM-DD format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#expires_at GroupAccessToken#expires_at}
        :param rotation_configuration: The configuration for when to rotate a token automatically. Will not rotate a token until ``terraform apply`` is run. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#rotation_configuration GroupAccessToken#rotation_configuration}
        :param validate_past_expiration_date: Wether to validate if the expiration date is in the future. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#validate_past_expiration_date GroupAccessToken#validate_past_expiration_date}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(rotation_configuration, dict):
            rotation_configuration = GroupAccessTokenRotationConfiguration(**rotation_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__174d9318ac63dff4a67836b8aca5152d0b9cd326c18add5e4b9358c1250bb6d0)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument scopes", value=scopes, expected_type=type_hints["scopes"])
            check_type(argname="argument access_level", value=access_level, expected_type=type_hints["access_level"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument expires_at", value=expires_at, expected_type=type_hints["expires_at"])
            check_type(argname="argument rotation_configuration", value=rotation_configuration, expected_type=type_hints["rotation_configuration"])
            check_type(argname="argument validate_past_expiration_date", value=validate_past_expiration_date, expected_type=type_hints["validate_past_expiration_date"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "group": group,
            "name": name,
            "scopes": scopes,
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
        if access_level is not None:
            self._values["access_level"] = access_level
        if description is not None:
            self._values["description"] = description
        if expires_at is not None:
            self._values["expires_at"] = expires_at
        if rotation_configuration is not None:
            self._values["rotation_configuration"] = rotation_configuration
        if validate_past_expiration_date is not None:
            self._values["validate_past_expiration_date"] = validate_past_expiration_date

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
    def group(self) -> builtins.str:
        '''The ID or full path of the group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#group GroupAccessToken#group}
        '''
        result = self._values.get("group")
        assert result is not None, "Required property 'group' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the group access token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#name GroupAccessToken#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scopes(self) -> typing.List[builtins.str]:
        '''The scopes of the group access token.

        Valid values are: ``api``, ``read_api``, ``read_registry``, ``write_registry``, ``read_virtual_registry``, ``write_virtual_registry``, ``read_repository``, ``write_repository``, ``create_runner``, ``manage_runner``, ``ai_features``, ``k8s_proxy``, ``read_observability``, ``write_observability``, ``self_rotate``

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#scopes GroupAccessToken#scopes}
        '''
        result = self._values.get("scopes")
        assert result is not None, "Required property 'scopes' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def access_level(self) -> typing.Optional[builtins.str]:
        '''The access level for the group access token.

        Valid values are: ``no one``, ``minimal``, ``guest``, ``planner``, ``reporter``, ``developer``, ``maintainer``, ``owner``. Default is ``maintainer``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#access_level GroupAccessToken#access_level}
        '''
        result = self._values.get("access_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the group access token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#description GroupAccessToken#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expires_at(self) -> typing.Optional[builtins.str]:
        '''When the token will expire, YYYY-MM-DD format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#expires_at GroupAccessToken#expires_at}
        '''
        result = self._values.get("expires_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_configuration(
        self,
    ) -> typing.Optional["GroupAccessTokenRotationConfiguration"]:
        '''The configuration for when to rotate a token automatically. Will not rotate a token until ``terraform apply`` is run.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#rotation_configuration GroupAccessToken#rotation_configuration}
        '''
        result = self._values.get("rotation_configuration")
        return typing.cast(typing.Optional["GroupAccessTokenRotationConfiguration"], result)

    @builtins.property
    def validate_past_expiration_date(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Wether to validate if the expiration date is in the future.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#validate_past_expiration_date GroupAccessToken#validate_past_expiration_date}
        '''
        result = self._values.get("validate_past_expiration_date")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GroupAccessTokenConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.groupAccessToken.GroupAccessTokenRotationConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "expiration_days": "expirationDays",
        "rotate_before_days": "rotateBeforeDays",
    },
)
class GroupAccessTokenRotationConfiguration:
    def __init__(
        self,
        *,
        expiration_days: jsii.Number,
        rotate_before_days: jsii.Number,
    ) -> None:
        '''
        :param expiration_days: The duration (in days) the new token should be valid for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#expiration_days GroupAccessToken#expiration_days}
        :param rotate_before_days: The duration (in days) before the expiration when the token should be rotated. As an example, if set to 7 days, the token will rotate 7 days before the expiration date, but only when ``terraform apply`` is run in that timeframe. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#rotate_before_days GroupAccessToken#rotate_before_days}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30ae66e8be255fea0bb32e6458c74a606c48a7e39f6323a53b63d4d9a6e68b89)
            check_type(argname="argument expiration_days", value=expiration_days, expected_type=type_hints["expiration_days"])
            check_type(argname="argument rotate_before_days", value=rotate_before_days, expected_type=type_hints["rotate_before_days"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "expiration_days": expiration_days,
            "rotate_before_days": rotate_before_days,
        }

    @builtins.property
    def expiration_days(self) -> jsii.Number:
        '''The duration (in days) the new token should be valid for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#expiration_days GroupAccessToken#expiration_days}
        '''
        result = self._values.get("expiration_days")
        assert result is not None, "Required property 'expiration_days' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def rotate_before_days(self) -> jsii.Number:
        '''The duration (in days) before the expiration when the token should be rotated.

        As an example, if set to 7 days, the token will rotate 7 days before the expiration date, but only when ``terraform apply`` is run in that timeframe.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_access_token#rotate_before_days GroupAccessToken#rotate_before_days}
        '''
        result = self._values.get("rotate_before_days")
        assert result is not None, "Required property 'rotate_before_days' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GroupAccessTokenRotationConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GroupAccessTokenRotationConfigurationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.groupAccessToken.GroupAccessTokenRotationConfigurationOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31e0e5271f0dc41b7a63c8c1241eec6012e278aae827aea26715f35f195b5d10)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="expirationDaysInput")
    def expiration_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "expirationDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="rotateBeforeDaysInput")
    def rotate_before_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rotateBeforeDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="expirationDays")
    def expiration_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "expirationDays"))

    @expiration_days.setter
    def expiration_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70f9fe582c8aa40d083271ccd130426f0d58e92357bfcbd95fdc0b9f635c4fe3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expirationDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rotateBeforeDays")
    def rotate_before_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotateBeforeDays"))

    @rotate_before_days.setter
    def rotate_before_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22a597f705bbd6142ffe2b6be1b882b6f7612205744c6c55854fa3380d4419a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotateBeforeDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GroupAccessTokenRotationConfiguration]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GroupAccessTokenRotationConfiguration]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GroupAccessTokenRotationConfiguration]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4095d6657ec2419ffee7cd434cb24f9d782801dbdc537e7cfff467091fba19b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "GroupAccessToken",
    "GroupAccessTokenConfig",
    "GroupAccessTokenRotationConfiguration",
    "GroupAccessTokenRotationConfigurationOutputReference",
]

publication.publish()

def _typecheckingstub__dfa859d58b20f46c1ff11372120d8c420b300a7cd2b1c6434a2911b8c0daf212(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    group: builtins.str,
    name: builtins.str,
    scopes: typing.Sequence[builtins.str],
    access_level: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    expires_at: typing.Optional[builtins.str] = None,
    rotation_configuration: typing.Optional[typing.Union[GroupAccessTokenRotationConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    validate_past_expiration_date: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__2ae49a6a945065a47d08b3e502c96efe9180ab17f25b0faba500eaf870d25549(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a91be87bbdcf2ce01cd80fea821e7bf0b967a17ee991718d91683e7962a11e3c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32e98629b61be7b618497f7502f3c88a0685b31a353aad2044e299f49e6df582(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84d185b48954b46ef90c021b66859414cd3b3dc7d4928fe2f876b24b20134e56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__520226349e5588723212ab72e0b2fa079fe712523614cefdf20f5067521b83e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f36b194ee52180ae6579bd4f040e05637ca64c92fd8c3ffa9ffe94cc4f21963f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a9f6c0fda5dec57b9956bd4b4362aa8a7f2cb48e3b7334161d6e4ed488564c6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88e1a02ca28231e4fe89a2d9bdbeaa5ef18cdd5f89ea61c489f22c1217d145e3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__174d9318ac63dff4a67836b8aca5152d0b9cd326c18add5e4b9358c1250bb6d0(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    group: builtins.str,
    name: builtins.str,
    scopes: typing.Sequence[builtins.str],
    access_level: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    expires_at: typing.Optional[builtins.str] = None,
    rotation_configuration: typing.Optional[typing.Union[GroupAccessTokenRotationConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    validate_past_expiration_date: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30ae66e8be255fea0bb32e6458c74a606c48a7e39f6323a53b63d4d9a6e68b89(
    *,
    expiration_days: jsii.Number,
    rotate_before_days: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31e0e5271f0dc41b7a63c8c1241eec6012e278aae827aea26715f35f195b5d10(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70f9fe582c8aa40d083271ccd130426f0d58e92357bfcbd95fdc0b9f635c4fe3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22a597f705bbd6142ffe2b6be1b882b6f7612205744c6c55854fa3380d4419a4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4095d6657ec2419ffee7cd434cb24f9d782801dbdc537e7cfff467091fba19b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GroupAccessTokenRotationConfiguration]],
) -> None:
    """Type checking stubs"""
    pass
