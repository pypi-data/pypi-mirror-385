r'''
# `gitlab_group_level_mr_approvals`

Refer to the Terraform Registry for docs: [`gitlab_group_level_mr_approvals`](https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals).
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


class GroupLevelMrApprovals(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.groupLevelMrApprovals.GroupLevelMrApprovals",
):
    '''Represents a {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals gitlab_group_level_mr_approvals}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        group: builtins.str,
        allow_author_approval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_committer_approval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_overrides_to_approver_list_per_merge_request: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        keep_settings_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        require_reauthentication_to_approve: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        retain_approvals_on_push: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals gitlab_group_level_mr_approvals} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param group: The ID or URL-encoded path of the group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#group GroupLevelMrApprovals#group}
        :param allow_author_approval: Allow or prevent authors from self approving merge requests; ``true`` means authors can self approve. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#allow_author_approval GroupLevelMrApprovals#allow_author_approval}
        :param allow_committer_approval: Allow or prevent committers from self approving merge requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#allow_committer_approval GroupLevelMrApprovals#allow_committer_approval}
        :param allow_overrides_to_approver_list_per_merge_request: Allow or prevent overriding approvers per merge request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#allow_overrides_to_approver_list_per_merge_request GroupLevelMrApprovals#allow_overrides_to_approver_list_per_merge_request}
        :param keep_settings_on_destroy: Set to true if the group merge request approval settings should not be reset to their pre-terraform defaults on destroy. You will need to apply the resource with the new setting before destroying the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#keep_settings_on_destroy GroupLevelMrApprovals#keep_settings_on_destroy}
        :param require_reauthentication_to_approve: Require approver to authenticate before adding the approval. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#require_reauthentication_to_approve GroupLevelMrApprovals#require_reauthentication_to_approve}
        :param retain_approvals_on_push: Retain approval count on a new push. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#retain_approvals_on_push GroupLevelMrApprovals#retain_approvals_on_push}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da76e3f7fc9a297e6a20f8e6f94ebd21dacaa0a4c6cf4cbdf644db184e26adfe)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = GroupLevelMrApprovalsConfig(
            group=group,
            allow_author_approval=allow_author_approval,
            allow_committer_approval=allow_committer_approval,
            allow_overrides_to_approver_list_per_merge_request=allow_overrides_to_approver_list_per_merge_request,
            keep_settings_on_destroy=keep_settings_on_destroy,
            require_reauthentication_to_approve=require_reauthentication_to_approve,
            retain_approvals_on_push=retain_approvals_on_push,
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
        '''Generates CDKTF code for importing a GroupLevelMrApprovals resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GroupLevelMrApprovals to import.
        :param import_from_id: The id of the existing GroupLevelMrApprovals that should be imported. Refer to the {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GroupLevelMrApprovals to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec16edbdef2be80c4d3e72b362e2b025dd9455ccb873e060f4931116aa407847)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAllowAuthorApproval")
    def reset_allow_author_approval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowAuthorApproval", []))

    @jsii.member(jsii_name="resetAllowCommitterApproval")
    def reset_allow_committer_approval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowCommitterApproval", []))

    @jsii.member(jsii_name="resetAllowOverridesToApproverListPerMergeRequest")
    def reset_allow_overrides_to_approver_list_per_merge_request(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowOverridesToApproverListPerMergeRequest", []))

    @jsii.member(jsii_name="resetKeepSettingsOnDestroy")
    def reset_keep_settings_on_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepSettingsOnDestroy", []))

    @jsii.member(jsii_name="resetRequireReauthenticationToApprove")
    def reset_require_reauthentication_to_approve(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireReauthenticationToApprove", []))

    @jsii.member(jsii_name="resetRetainApprovalsOnPush")
    def reset_retain_approvals_on_push(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetainApprovalsOnPush", []))

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
    @jsii.member(jsii_name="allowAuthorApprovalInput")
    def allow_author_approval_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowAuthorApprovalInput"))

    @builtins.property
    @jsii.member(jsii_name="allowCommitterApprovalInput")
    def allow_committer_approval_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowCommitterApprovalInput"))

    @builtins.property
    @jsii.member(jsii_name="allowOverridesToApproverListPerMergeRequestInput")
    def allow_overrides_to_approver_list_per_merge_request_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowOverridesToApproverListPerMergeRequestInput"))

    @builtins.property
    @jsii.member(jsii_name="groupInput")
    def group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupInput"))

    @builtins.property
    @jsii.member(jsii_name="keepSettingsOnDestroyInput")
    def keep_settings_on_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "keepSettingsOnDestroyInput"))

    @builtins.property
    @jsii.member(jsii_name="requireReauthenticationToApproveInput")
    def require_reauthentication_to_approve_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requireReauthenticationToApproveInput"))

    @builtins.property
    @jsii.member(jsii_name="retainApprovalsOnPushInput")
    def retain_approvals_on_push_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "retainApprovalsOnPushInput"))

    @builtins.property
    @jsii.member(jsii_name="allowAuthorApproval")
    def allow_author_approval(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowAuthorApproval"))

    @allow_author_approval.setter
    def allow_author_approval(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77616a41d134fdd20f47c1e9c089a4128ba251bbd4db3d0575ff1f4a44872bde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowAuthorApproval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowCommitterApproval")
    def allow_committer_approval(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowCommitterApproval"))

    @allow_committer_approval.setter
    def allow_committer_approval(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a1dabf763234ad11ae82e0b0a8af2dff293341e6e925138e75e89960921a75b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowCommitterApproval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowOverridesToApproverListPerMergeRequest")
    def allow_overrides_to_approver_list_per_merge_request(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowOverridesToApproverListPerMergeRequest"))

    @allow_overrides_to_approver_list_per_merge_request.setter
    def allow_overrides_to_approver_list_per_merge_request(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acb938d9f4de6d0f580421f5b624a4cb7262074b8de2a34e3e0d186cea985100)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowOverridesToApproverListPerMergeRequest", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "group"))

    @group.setter
    def group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b9b912b5d0cd9279af1dfee4335c66d6441b94e992bd586a1abd4bc8658a288)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "group", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keepSettingsOnDestroy")
    def keep_settings_on_destroy(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "keepSettingsOnDestroy"))

    @keep_settings_on_destroy.setter
    def keep_settings_on_destroy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2ced04a1c98bd7afbcfa63435b6aa81a85f3628e690a97db1c5e73aa68c9577)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keepSettingsOnDestroy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requireReauthenticationToApprove")
    def require_reauthentication_to_approve(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "requireReauthenticationToApprove"))

    @require_reauthentication_to_approve.setter
    def require_reauthentication_to_approve(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50fe3f821ef709f53841e83a0b1925a00162176562c839f533a20f085cd4030f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requireReauthenticationToApprove", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retainApprovalsOnPush")
    def retain_approvals_on_push(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "retainApprovalsOnPush"))

    @retain_approvals_on_push.setter
    def retain_approvals_on_push(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__737ab5a9147161ae420e4da059ac45bccf32d9b1cceca35914bf7bc791800796)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retainApprovalsOnPush", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.groupLevelMrApprovals.GroupLevelMrApprovalsConfig",
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
        "allow_author_approval": "allowAuthorApproval",
        "allow_committer_approval": "allowCommitterApproval",
        "allow_overrides_to_approver_list_per_merge_request": "allowOverridesToApproverListPerMergeRequest",
        "keep_settings_on_destroy": "keepSettingsOnDestroy",
        "require_reauthentication_to_approve": "requireReauthenticationToApprove",
        "retain_approvals_on_push": "retainApprovalsOnPush",
    },
)
class GroupLevelMrApprovalsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        allow_author_approval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_committer_approval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_overrides_to_approver_list_per_merge_request: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        keep_settings_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        require_reauthentication_to_approve: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        retain_approvals_on_push: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param group: The ID or URL-encoded path of the group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#group GroupLevelMrApprovals#group}
        :param allow_author_approval: Allow or prevent authors from self approving merge requests; ``true`` means authors can self approve. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#allow_author_approval GroupLevelMrApprovals#allow_author_approval}
        :param allow_committer_approval: Allow or prevent committers from self approving merge requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#allow_committer_approval GroupLevelMrApprovals#allow_committer_approval}
        :param allow_overrides_to_approver_list_per_merge_request: Allow or prevent overriding approvers per merge request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#allow_overrides_to_approver_list_per_merge_request GroupLevelMrApprovals#allow_overrides_to_approver_list_per_merge_request}
        :param keep_settings_on_destroy: Set to true if the group merge request approval settings should not be reset to their pre-terraform defaults on destroy. You will need to apply the resource with the new setting before destroying the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#keep_settings_on_destroy GroupLevelMrApprovals#keep_settings_on_destroy}
        :param require_reauthentication_to_approve: Require approver to authenticate before adding the approval. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#require_reauthentication_to_approve GroupLevelMrApprovals#require_reauthentication_to_approve}
        :param retain_approvals_on_push: Retain approval count on a new push. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#retain_approvals_on_push GroupLevelMrApprovals#retain_approvals_on_push}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab896240851807d098faeeb9f02fec71028123720f1b303a34ab55ab30b15aaa)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
            check_type(argname="argument allow_author_approval", value=allow_author_approval, expected_type=type_hints["allow_author_approval"])
            check_type(argname="argument allow_committer_approval", value=allow_committer_approval, expected_type=type_hints["allow_committer_approval"])
            check_type(argname="argument allow_overrides_to_approver_list_per_merge_request", value=allow_overrides_to_approver_list_per_merge_request, expected_type=type_hints["allow_overrides_to_approver_list_per_merge_request"])
            check_type(argname="argument keep_settings_on_destroy", value=keep_settings_on_destroy, expected_type=type_hints["keep_settings_on_destroy"])
            check_type(argname="argument require_reauthentication_to_approve", value=require_reauthentication_to_approve, expected_type=type_hints["require_reauthentication_to_approve"])
            check_type(argname="argument retain_approvals_on_push", value=retain_approvals_on_push, expected_type=type_hints["retain_approvals_on_push"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "group": group,
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
        if allow_author_approval is not None:
            self._values["allow_author_approval"] = allow_author_approval
        if allow_committer_approval is not None:
            self._values["allow_committer_approval"] = allow_committer_approval
        if allow_overrides_to_approver_list_per_merge_request is not None:
            self._values["allow_overrides_to_approver_list_per_merge_request"] = allow_overrides_to_approver_list_per_merge_request
        if keep_settings_on_destroy is not None:
            self._values["keep_settings_on_destroy"] = keep_settings_on_destroy
        if require_reauthentication_to_approve is not None:
            self._values["require_reauthentication_to_approve"] = require_reauthentication_to_approve
        if retain_approvals_on_push is not None:
            self._values["retain_approvals_on_push"] = retain_approvals_on_push

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
        '''The ID or URL-encoded path of the group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#group GroupLevelMrApprovals#group}
        '''
        result = self._values.get("group")
        assert result is not None, "Required property 'group' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_author_approval(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow or prevent authors from self approving merge requests; ``true`` means authors can self approve.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#allow_author_approval GroupLevelMrApprovals#allow_author_approval}
        '''
        result = self._values.get("allow_author_approval")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_committer_approval(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow or prevent committers from self approving merge requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#allow_committer_approval GroupLevelMrApprovals#allow_committer_approval}
        '''
        result = self._values.get("allow_committer_approval")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_overrides_to_approver_list_per_merge_request(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow or prevent overriding approvers per merge request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#allow_overrides_to_approver_list_per_merge_request GroupLevelMrApprovals#allow_overrides_to_approver_list_per_merge_request}
        '''
        result = self._values.get("allow_overrides_to_approver_list_per_merge_request")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def keep_settings_on_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true if the group merge request approval settings should not be reset to their pre-terraform defaults on destroy.

        You will need to apply the resource with the new setting before destroying the resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#keep_settings_on_destroy GroupLevelMrApprovals#keep_settings_on_destroy}
        '''
        result = self._values.get("keep_settings_on_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def require_reauthentication_to_approve(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Require approver to authenticate before adding the approval.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#require_reauthentication_to_approve GroupLevelMrApprovals#require_reauthentication_to_approve}
        '''
        result = self._values.get("require_reauthentication_to_approve")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def retain_approvals_on_push(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Retain approval count on a new push.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/group_level_mr_approvals#retain_approvals_on_push GroupLevelMrApprovals#retain_approvals_on_push}
        '''
        result = self._values.get("retain_approvals_on_push")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GroupLevelMrApprovalsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GroupLevelMrApprovals",
    "GroupLevelMrApprovalsConfig",
]

publication.publish()

def _typecheckingstub__da76e3f7fc9a297e6a20f8e6f94ebd21dacaa0a4c6cf4cbdf644db184e26adfe(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    group: builtins.str,
    allow_author_approval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_committer_approval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_overrides_to_approver_list_per_merge_request: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    keep_settings_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    require_reauthentication_to_approve: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    retain_approvals_on_push: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__ec16edbdef2be80c4d3e72b362e2b025dd9455ccb873e060f4931116aa407847(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77616a41d134fdd20f47c1e9c089a4128ba251bbd4db3d0575ff1f4a44872bde(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a1dabf763234ad11ae82e0b0a8af2dff293341e6e925138e75e89960921a75b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acb938d9f4de6d0f580421f5b624a4cb7262074b8de2a34e3e0d186cea985100(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b9b912b5d0cd9279af1dfee4335c66d6441b94e992bd586a1abd4bc8658a288(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2ced04a1c98bd7afbcfa63435b6aa81a85f3628e690a97db1c5e73aa68c9577(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50fe3f821ef709f53841e83a0b1925a00162176562c839f533a20f085cd4030f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__737ab5a9147161ae420e4da059ac45bccf32d9b1cceca35914bf7bc791800796(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab896240851807d098faeeb9f02fec71028123720f1b303a34ab55ab30b15aaa(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    group: builtins.str,
    allow_author_approval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_committer_approval: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_overrides_to_approver_list_per_merge_request: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    keep_settings_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    require_reauthentication_to_approve: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    retain_approvals_on_push: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
