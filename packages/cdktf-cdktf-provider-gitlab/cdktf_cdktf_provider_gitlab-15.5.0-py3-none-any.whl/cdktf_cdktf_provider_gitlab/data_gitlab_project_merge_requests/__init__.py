r'''
# `data_gitlab_project_merge_requests`

Refer to the Terraform Registry for docs: [`data_gitlab_project_merge_requests`](https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests).
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


class DataGitlabProjectMergeRequests(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequests",
):
    '''Represents a {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests gitlab_project_merge_requests}.'''

    def __init__(
        self,
        scope_: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        project: builtins.str,
        author_id: typing.Optional[jsii.Number] = None,
        author_username: typing.Optional[builtins.str] = None,
        created_after: typing.Optional[builtins.str] = None,
        created_before: typing.Optional[builtins.str] = None,
        iids: typing.Optional[typing.Sequence[jsii.Number]] = None,
        milestone: typing.Optional[builtins.str] = None,
        my_reaction_emoji: typing.Optional[builtins.str] = None,
        order_by: typing.Optional[builtins.str] = None,
        reviewer_username: typing.Optional[builtins.str] = None,
        scope: typing.Optional[builtins.str] = None,
        search: typing.Optional[builtins.str] = None,
        sort: typing.Optional[builtins.str] = None,
        source_branch: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        target_branch: typing.Optional[builtins.str] = None,
        updated_after: typing.Optional[builtins.str] = None,
        updated_before: typing.Optional[builtins.str] = None,
        wip: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests gitlab_project_merge_requests} Data Source.

        :param scope_: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param project: The ID or path of the project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#project DataGitlabProjectMergeRequests#project}
        :param author_id: Return merge requests created by the given user ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#author_id DataGitlabProjectMergeRequests#author_id}
        :param author_username: Return merge requests created by the given username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#author_username DataGitlabProjectMergeRequests#author_username}
        :param created_after: Return merge requests created after the given time. Expected in RFC3339 format (2006-01-02T15:04:05Z). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#created_after DataGitlabProjectMergeRequests#created_after}
        :param created_before: Return merge requests created before the given time. Expected in RFC3339 format (2006-01-02T15:04:05Z). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#created_before DataGitlabProjectMergeRequests#created_before}
        :param iids: The unique internal IDs of the merge requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#iids DataGitlabProjectMergeRequests#iids}
        :param milestone: Return only merge requests for a specific milestone. ``None`` returns merge requests with no milestone. ``Any`` returns merge requests that have an assigned milestone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#milestone DataGitlabProjectMergeRequests#milestone}
        :param my_reaction_emoji: Return merge requests reacted to by the authenticated user with the given emoji. ``None`` returns issues not given a reaction. ``Any`` returns issues given at least one reaction. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#my_reaction_emoji DataGitlabProjectMergeRequests#my_reaction_emoji}
        :param order_by: Return requests ordered by ``created_at``, ``title`` or ``updated_at``. Default is ``created_at``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#order_by DataGitlabProjectMergeRequests#order_by}
        :param reviewer_username: Return merge requests reviewed by the given username. ``None`` returns merge requests with no reviews. ``Any`` returns merge requests with any reviewer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#reviewer_username DataGitlabProjectMergeRequests#reviewer_username}
        :param scope: Return merge requests for the given scope: ``created_by_me``, ``assigned_to_me``, or ``all``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#scope DataGitlabProjectMergeRequests#scope}
        :param search: Search merge requests against their ``title`` or ``description``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#search DataGitlabProjectMergeRequests#search}
        :param sort: Return requests sorted in ``asc`` or ``desc`` order. Default is ``desc``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#sort DataGitlabProjectMergeRequests#sort}
        :param source_branch: Return merge requests with the given source branch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#source_branch DataGitlabProjectMergeRequests#source_branch}
        :param state: Return all merge requests (all) or just those that are opened, closed, locked, or merged. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#state DataGitlabProjectMergeRequests#state}
        :param target_branch: Return merge requests with the given target branch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#target_branch DataGitlabProjectMergeRequests#target_branch}
        :param updated_after: Return merge requests updated after the given time. Expected in RFC3339 format (2006-01-02T15:04:05Z). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#updated_after DataGitlabProjectMergeRequests#updated_after}
        :param updated_before: Return merge requests updated before the given time. Expected in RFC3339 format (2006-01-02T15:04:05Z). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#updated_before DataGitlabProjectMergeRequests#updated_before}
        :param wip: Filter merge requests against their wip status. ``yes`` to return only draft merge requests, ``no`` to return non-draft merge requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#wip DataGitlabProjectMergeRequests#wip}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bb091d0b95be2485a22fd00fb265fcba670b7f1cef77b2544bca851bf6de0d6)
            check_type(argname="argument scope_", value=scope_, expected_type=type_hints["scope_"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataGitlabProjectMergeRequestsConfig(
            project=project,
            author_id=author_id,
            author_username=author_username,
            created_after=created_after,
            created_before=created_before,
            iids=iids,
            milestone=milestone,
            my_reaction_emoji=my_reaction_emoji,
            order_by=order_by,
            reviewer_username=reviewer_username,
            scope=scope,
            search=search,
            sort=sort,
            source_branch=source_branch,
            state=state,
            target_branch=target_branch,
            updated_after=updated_after,
            updated_before=updated_before,
            wip=wip,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope_, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a DataGitlabProjectMergeRequests resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataGitlabProjectMergeRequests to import.
        :param import_from_id: The id of the existing DataGitlabProjectMergeRequests that should be imported. Refer to the {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataGitlabProjectMergeRequests to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20c09809e1abe65f2971ba67e1886becdaf006f4c79d3d4e1525a71502e7f651)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAuthorId")
    def reset_author_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthorId", []))

    @jsii.member(jsii_name="resetAuthorUsername")
    def reset_author_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthorUsername", []))

    @jsii.member(jsii_name="resetCreatedAfter")
    def reset_created_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAfter", []))

    @jsii.member(jsii_name="resetCreatedBefore")
    def reset_created_before(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBefore", []))

    @jsii.member(jsii_name="resetIids")
    def reset_iids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIids", []))

    @jsii.member(jsii_name="resetMilestone")
    def reset_milestone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMilestone", []))

    @jsii.member(jsii_name="resetMyReactionEmoji")
    def reset_my_reaction_emoji(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMyReactionEmoji", []))

    @jsii.member(jsii_name="resetOrderBy")
    def reset_order_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrderBy", []))

    @jsii.member(jsii_name="resetReviewerUsername")
    def reset_reviewer_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReviewerUsername", []))

    @jsii.member(jsii_name="resetScope")
    def reset_scope(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScope", []))

    @jsii.member(jsii_name="resetSearch")
    def reset_search(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSearch", []))

    @jsii.member(jsii_name="resetSort")
    def reset_sort(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSort", []))

    @jsii.member(jsii_name="resetSourceBranch")
    def reset_source_branch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceBranch", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

    @jsii.member(jsii_name="resetTargetBranch")
    def reset_target_branch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetBranch", []))

    @jsii.member(jsii_name="resetUpdatedAfter")
    def reset_updated_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedAfter", []))

    @jsii.member(jsii_name="resetUpdatedBefore")
    def reset_updated_before(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatedBefore", []))

    @jsii.member(jsii_name="resetWip")
    def reset_wip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWip", []))

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
    @jsii.member(jsii_name="mergeRequests")
    def merge_requests(self) -> "DataGitlabProjectMergeRequestsMergeRequestsList":
        return typing.cast("DataGitlabProjectMergeRequestsMergeRequestsList", jsii.get(self, "mergeRequests"))

    @builtins.property
    @jsii.member(jsii_name="authorIdInput")
    def author_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "authorIdInput"))

    @builtins.property
    @jsii.member(jsii_name="authorUsernameInput")
    def author_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorUsernameInput"))

    @builtins.property
    @jsii.member(jsii_name="createdAfterInput")
    def created_after_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAfterInput"))

    @builtins.property
    @jsii.member(jsii_name="createdBeforeInput")
    def created_before_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdBeforeInput"))

    @builtins.property
    @jsii.member(jsii_name="iidsInput")
    def iids_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "iidsInput"))

    @builtins.property
    @jsii.member(jsii_name="milestoneInput")
    def milestone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "milestoneInput"))

    @builtins.property
    @jsii.member(jsii_name="myReactionEmojiInput")
    def my_reaction_emoji_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "myReactionEmojiInput"))

    @builtins.property
    @jsii.member(jsii_name="orderByInput")
    def order_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "orderByInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="reviewerUsernameInput")
    def reviewer_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reviewerUsernameInput"))

    @builtins.property
    @jsii.member(jsii_name="scopeInput")
    def scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scopeInput"))

    @builtins.property
    @jsii.member(jsii_name="searchInput")
    def search_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "searchInput"))

    @builtins.property
    @jsii.member(jsii_name="sortInput")
    def sort_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sortInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceBranchInput")
    def source_branch_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceBranchInput"))

    @builtins.property
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property
    @jsii.member(jsii_name="targetBranchInput")
    def target_branch_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetBranchInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedAfterInput")
    def updated_after_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updatedAfterInput"))

    @builtins.property
    @jsii.member(jsii_name="updatedBeforeInput")
    def updated_before_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updatedBeforeInput"))

    @builtins.property
    @jsii.member(jsii_name="wipInput")
    def wip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "wipInput"))

    @builtins.property
    @jsii.member(jsii_name="authorId")
    def author_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "authorId"))

    @author_id.setter
    def author_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ee8de5bf56a4e65561d87295befa38bdc06da6f8cb082c94192313692e4f548)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authorId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authorUsername")
    def author_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorUsername"))

    @author_username.setter
    def author_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9efa43b04bebdb0a67b09f84f90f63da8459dab969eaa742c8f545b4bfdfcf60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authorUsername", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdAfter")
    def created_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAfter"))

    @created_after.setter
    def created_after(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f25f749b04c68345f689b9b1bdf586167a27d1975ab2304fa9fa0da5db736b97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdBefore")
    def created_before(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBefore"))

    @created_before.setter
    def created_before(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01e595852005604bb625ab5ed0cc545bc376a6011337336c4f595006219c4784)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBefore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iids")
    def iids(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "iids"))

    @iids.setter
    def iids(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__778e55fe5a8353b9df6219dfdd27357c3965b7f6350d81250c280c0c5e4f611e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iids", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="milestone")
    def milestone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "milestone"))

    @milestone.setter
    def milestone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__826e41d1ac4d443e7094c1caffaf6a24c7b4773c3f696c601db5c00a610663f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "milestone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="myReactionEmoji")
    def my_reaction_emoji(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "myReactionEmoji"))

    @my_reaction_emoji.setter
    def my_reaction_emoji(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99884ae8e6e5db238c2a41ddf41a245738a3f0ae07ab2b948bdffafe486f716c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "myReactionEmoji", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="orderBy")
    def order_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "orderBy"))

    @order_by.setter
    def order_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04b32ee29f63f298dbf7b2a6b9353536d9d1796b9fc15ddf8f4753509336ff18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "orderBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b9f1d3cc7b649e04dc27c9dd5822a866b9cf38881bd8aa40d075f755d496e4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reviewerUsername")
    def reviewer_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reviewerUsername"))

    @reviewer_username.setter
    def reviewer_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e42377f0366da6464fc0c86417aa1670afa1fbf46db25c9eb6fbda4b75f162b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reviewerUsername", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c65c66d954d6f128f778f1adf6def3d0c50695aa1bc9e7f224deb368930f6ff3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scope", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="search")
    def search(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "search"))

    @search.setter
    def search(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6688017cb5bc90c1ede332ac77cef30ab6334a39da07e2767f2dd507a3260908)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "search", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sort")
    def sort(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sort"))

    @sort.setter
    def sort(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ee32fa31473f5de0b9de74015998233c7b75b81f485271b511b8b83000910d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceBranch")
    def source_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceBranch"))

    @source_branch.setter
    def source_branch(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec3486bebcdf26df55b5b3de268938dc50e64f320c27864195894ddd6b437be3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceBranch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39f742f24ea4843410f3f089ce1616dbb4aa30d0573b39f8da237d7f3156206f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "state", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetBranch")
    def target_branch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetBranch"))

    @target_branch.setter
    def target_branch(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f2f7d37180efd2ffaada620e6a8b886f457fd60bedbb613a0ea9b548be62b53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetBranch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedAfter")
    def updated_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAfter"))

    @updated_after.setter
    def updated_after(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__334feb88e9d97a7e1bc039e2f00229fe9de5035942f4ac9b9a24df41f3af1c1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updatedBefore")
    def updated_before(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedBefore"))

    @updated_before.setter
    def updated_before(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05ce02c67caed9de555b1f1a90fdf81fb84cac084d819d96e52adb8292eb1ec9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updatedBefore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wip")
    def wip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wip"))

    @wip.setter
    def wip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba10ab059c7a8525b40f1235f911e674798413e0d5755728ab6ac7d0a803eb87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wip", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequestsConfig",
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
        "author_id": "authorId",
        "author_username": "authorUsername",
        "created_after": "createdAfter",
        "created_before": "createdBefore",
        "iids": "iids",
        "milestone": "milestone",
        "my_reaction_emoji": "myReactionEmoji",
        "order_by": "orderBy",
        "reviewer_username": "reviewerUsername",
        "scope": "scope",
        "search": "search",
        "sort": "sort",
        "source_branch": "sourceBranch",
        "state": "state",
        "target_branch": "targetBranch",
        "updated_after": "updatedAfter",
        "updated_before": "updatedBefore",
        "wip": "wip",
    },
)
class DataGitlabProjectMergeRequestsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        author_id: typing.Optional[jsii.Number] = None,
        author_username: typing.Optional[builtins.str] = None,
        created_after: typing.Optional[builtins.str] = None,
        created_before: typing.Optional[builtins.str] = None,
        iids: typing.Optional[typing.Sequence[jsii.Number]] = None,
        milestone: typing.Optional[builtins.str] = None,
        my_reaction_emoji: typing.Optional[builtins.str] = None,
        order_by: typing.Optional[builtins.str] = None,
        reviewer_username: typing.Optional[builtins.str] = None,
        scope: typing.Optional[builtins.str] = None,
        search: typing.Optional[builtins.str] = None,
        sort: typing.Optional[builtins.str] = None,
        source_branch: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        target_branch: typing.Optional[builtins.str] = None,
        updated_after: typing.Optional[builtins.str] = None,
        updated_before: typing.Optional[builtins.str] = None,
        wip: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param project: The ID or path of the project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#project DataGitlabProjectMergeRequests#project}
        :param author_id: Return merge requests created by the given user ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#author_id DataGitlabProjectMergeRequests#author_id}
        :param author_username: Return merge requests created by the given username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#author_username DataGitlabProjectMergeRequests#author_username}
        :param created_after: Return merge requests created after the given time. Expected in RFC3339 format (2006-01-02T15:04:05Z). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#created_after DataGitlabProjectMergeRequests#created_after}
        :param created_before: Return merge requests created before the given time. Expected in RFC3339 format (2006-01-02T15:04:05Z). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#created_before DataGitlabProjectMergeRequests#created_before}
        :param iids: The unique internal IDs of the merge requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#iids DataGitlabProjectMergeRequests#iids}
        :param milestone: Return only merge requests for a specific milestone. ``None`` returns merge requests with no milestone. ``Any`` returns merge requests that have an assigned milestone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#milestone DataGitlabProjectMergeRequests#milestone}
        :param my_reaction_emoji: Return merge requests reacted to by the authenticated user with the given emoji. ``None`` returns issues not given a reaction. ``Any`` returns issues given at least one reaction. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#my_reaction_emoji DataGitlabProjectMergeRequests#my_reaction_emoji}
        :param order_by: Return requests ordered by ``created_at``, ``title`` or ``updated_at``. Default is ``created_at``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#order_by DataGitlabProjectMergeRequests#order_by}
        :param reviewer_username: Return merge requests reviewed by the given username. ``None`` returns merge requests with no reviews. ``Any`` returns merge requests with any reviewer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#reviewer_username DataGitlabProjectMergeRequests#reviewer_username}
        :param scope: Return merge requests for the given scope: ``created_by_me``, ``assigned_to_me``, or ``all``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#scope DataGitlabProjectMergeRequests#scope}
        :param search: Search merge requests against their ``title`` or ``description``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#search DataGitlabProjectMergeRequests#search}
        :param sort: Return requests sorted in ``asc`` or ``desc`` order. Default is ``desc``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#sort DataGitlabProjectMergeRequests#sort}
        :param source_branch: Return merge requests with the given source branch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#source_branch DataGitlabProjectMergeRequests#source_branch}
        :param state: Return all merge requests (all) or just those that are opened, closed, locked, or merged. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#state DataGitlabProjectMergeRequests#state}
        :param target_branch: Return merge requests with the given target branch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#target_branch DataGitlabProjectMergeRequests#target_branch}
        :param updated_after: Return merge requests updated after the given time. Expected in RFC3339 format (2006-01-02T15:04:05Z). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#updated_after DataGitlabProjectMergeRequests#updated_after}
        :param updated_before: Return merge requests updated before the given time. Expected in RFC3339 format (2006-01-02T15:04:05Z). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#updated_before DataGitlabProjectMergeRequests#updated_before}
        :param wip: Filter merge requests against their wip status. ``yes`` to return only draft merge requests, ``no`` to return non-draft merge requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#wip DataGitlabProjectMergeRequests#wip}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64d614f3339412a80d705c2591244cdacfbc471003ff4e9f8aec16bbc71d081b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument author_id", value=author_id, expected_type=type_hints["author_id"])
            check_type(argname="argument author_username", value=author_username, expected_type=type_hints["author_username"])
            check_type(argname="argument created_after", value=created_after, expected_type=type_hints["created_after"])
            check_type(argname="argument created_before", value=created_before, expected_type=type_hints["created_before"])
            check_type(argname="argument iids", value=iids, expected_type=type_hints["iids"])
            check_type(argname="argument milestone", value=milestone, expected_type=type_hints["milestone"])
            check_type(argname="argument my_reaction_emoji", value=my_reaction_emoji, expected_type=type_hints["my_reaction_emoji"])
            check_type(argname="argument order_by", value=order_by, expected_type=type_hints["order_by"])
            check_type(argname="argument reviewer_username", value=reviewer_username, expected_type=type_hints["reviewer_username"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument search", value=search, expected_type=type_hints["search"])
            check_type(argname="argument sort", value=sort, expected_type=type_hints["sort"])
            check_type(argname="argument source_branch", value=source_branch, expected_type=type_hints["source_branch"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
            check_type(argname="argument target_branch", value=target_branch, expected_type=type_hints["target_branch"])
            check_type(argname="argument updated_after", value=updated_after, expected_type=type_hints["updated_after"])
            check_type(argname="argument updated_before", value=updated_before, expected_type=type_hints["updated_before"])
            check_type(argname="argument wip", value=wip, expected_type=type_hints["wip"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "project": project,
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
        if author_id is not None:
            self._values["author_id"] = author_id
        if author_username is not None:
            self._values["author_username"] = author_username
        if created_after is not None:
            self._values["created_after"] = created_after
        if created_before is not None:
            self._values["created_before"] = created_before
        if iids is not None:
            self._values["iids"] = iids
        if milestone is not None:
            self._values["milestone"] = milestone
        if my_reaction_emoji is not None:
            self._values["my_reaction_emoji"] = my_reaction_emoji
        if order_by is not None:
            self._values["order_by"] = order_by
        if reviewer_username is not None:
            self._values["reviewer_username"] = reviewer_username
        if scope is not None:
            self._values["scope"] = scope
        if search is not None:
            self._values["search"] = search
        if sort is not None:
            self._values["sort"] = sort
        if source_branch is not None:
            self._values["source_branch"] = source_branch
        if state is not None:
            self._values["state"] = state
        if target_branch is not None:
            self._values["target_branch"] = target_branch
        if updated_after is not None:
            self._values["updated_after"] = updated_after
        if updated_before is not None:
            self._values["updated_before"] = updated_before
        if wip is not None:
            self._values["wip"] = wip

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
        '''The ID or path of the project.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#project DataGitlabProjectMergeRequests#project}
        '''
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def author_id(self) -> typing.Optional[jsii.Number]:
        '''Return merge requests created by the given user ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#author_id DataGitlabProjectMergeRequests#author_id}
        '''
        result = self._values.get("author_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def author_username(self) -> typing.Optional[builtins.str]:
        '''Return merge requests created by the given username.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#author_username DataGitlabProjectMergeRequests#author_username}
        '''
        result = self._values.get("author_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_after(self) -> typing.Optional[builtins.str]:
        '''Return merge requests created after the given time. Expected in RFC3339 format (2006-01-02T15:04:05Z).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#created_after DataGitlabProjectMergeRequests#created_after}
        '''
        result = self._values.get("created_after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_before(self) -> typing.Optional[builtins.str]:
        '''Return merge requests created before the given time. Expected in RFC3339 format (2006-01-02T15:04:05Z).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#created_before DataGitlabProjectMergeRequests#created_before}
        '''
        result = self._values.get("created_before")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iids(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''The unique internal IDs of the merge requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#iids DataGitlabProjectMergeRequests#iids}
        '''
        result = self._values.get("iids")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def milestone(self) -> typing.Optional[builtins.str]:
        '''Return only merge requests for a specific milestone.

        ``None`` returns merge requests with no milestone. ``Any`` returns merge requests that have an assigned milestone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#milestone DataGitlabProjectMergeRequests#milestone}
        '''
        result = self._values.get("milestone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def my_reaction_emoji(self) -> typing.Optional[builtins.str]:
        '''Return merge requests reacted to by the authenticated user with the given emoji.

        ``None`` returns issues not given a reaction. ``Any`` returns issues given at least one reaction.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#my_reaction_emoji DataGitlabProjectMergeRequests#my_reaction_emoji}
        '''
        result = self._values.get("my_reaction_emoji")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def order_by(self) -> typing.Optional[builtins.str]:
        '''Return requests ordered by ``created_at``, ``title`` or ``updated_at``. Default is ``created_at``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#order_by DataGitlabProjectMergeRequests#order_by}
        '''
        result = self._values.get("order_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def reviewer_username(self) -> typing.Optional[builtins.str]:
        '''Return merge requests reviewed by the given username.

        ``None`` returns merge requests with no reviews. ``Any`` returns merge requests with any reviewer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#reviewer_username DataGitlabProjectMergeRequests#reviewer_username}
        '''
        result = self._values.get("reviewer_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scope(self) -> typing.Optional[builtins.str]:
        '''Return merge requests for the given scope: ``created_by_me``, ``assigned_to_me``, or ``all``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#scope DataGitlabProjectMergeRequests#scope}
        '''
        result = self._values.get("scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def search(self) -> typing.Optional[builtins.str]:
        '''Search merge requests against their ``title`` or ``description``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#search DataGitlabProjectMergeRequests#search}
        '''
        result = self._values.get("search")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sort(self) -> typing.Optional[builtins.str]:
        '''Return requests sorted in ``asc`` or ``desc`` order. Default is ``desc``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#sort DataGitlabProjectMergeRequests#sort}
        '''
        result = self._values.get("sort")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_branch(self) -> typing.Optional[builtins.str]:
        '''Return merge requests with the given source branch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#source_branch DataGitlabProjectMergeRequests#source_branch}
        '''
        result = self._values.get("source_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Return all merge requests (all) or just those that are opened, closed, locked, or merged.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#state DataGitlabProjectMergeRequests#state}
        '''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_branch(self) -> typing.Optional[builtins.str]:
        '''Return merge requests with the given target branch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#target_branch DataGitlabProjectMergeRequests#target_branch}
        '''
        result = self._values.get("target_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_after(self) -> typing.Optional[builtins.str]:
        '''Return merge requests updated after the given time. Expected in RFC3339 format (2006-01-02T15:04:05Z).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#updated_after DataGitlabProjectMergeRequests#updated_after}
        '''
        result = self._values.get("updated_after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_before(self) -> typing.Optional[builtins.str]:
        '''Return merge requests updated before the given time. Expected in RFC3339 format (2006-01-02T15:04:05Z).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#updated_before DataGitlabProjectMergeRequests#updated_before}
        '''
        result = self._values.get("updated_before")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wip(self) -> typing.Optional[builtins.str]:
        '''Filter merge requests against their wip status.

        ``yes`` to return only draft merge requests, ``no`` to return non-draft merge requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/data-sources/project_merge_requests#wip DataGitlabProjectMergeRequests#wip}
        '''
        result = self._values.get("wip")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGitlabProjectMergeRequestsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequestsMergeRequests",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataGitlabProjectMergeRequestsMergeRequests:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGitlabProjectMergeRequestsMergeRequests(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequestsMergeRequestsAssignee",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataGitlabProjectMergeRequestsMergeRequestsAssignee:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGitlabProjectMergeRequestsMergeRequestsAssignee(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGitlabProjectMergeRequestsMergeRequestsAssigneeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequestsMergeRequestsAssigneeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__75b804b889ffe957c1a9ed47c0ad04af9eff2aadee1ee6646f7cd2ac6499d9a2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="avatarUrl")
    def avatar_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "avatarUrl"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @builtins.property
    @jsii.member(jsii_name="webUrl")
    def web_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webUrl"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsAssignee]:
        return typing.cast(typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsAssignee], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsAssignee],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__750cadef11a78edf7c27d989f23d9a47f8d7df7513de19bc2926db88ab3a0315)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequestsMergeRequestsAssignees",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataGitlabProjectMergeRequestsMergeRequestsAssignees:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGitlabProjectMergeRequestsMergeRequestsAssignees(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGitlabProjectMergeRequestsMergeRequestsAssigneesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequestsMergeRequestsAssigneesList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8f56c0882cab85b08ad86af671b02026ecc952ced283dcd6e1e85bbecd399ea)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataGitlabProjectMergeRequestsMergeRequestsAssigneesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87199165a3a8992677dd91c0fe3f377a0e224785500ea5bb5a9382801b0eebc9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataGitlabProjectMergeRequestsMergeRequestsAssigneesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a944c09f34986e42146489522afe39df14ade2518c59e8d725a9b213b502aeb8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3c6a0195959269ea1220944d19cb2c27f9576a7b6eaa1724a6fe98e97aa18a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c5d36aefe3d25f91c8d2cc5bd3cca502bc2bc093d6207499e7eb395294aff50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataGitlabProjectMergeRequestsMergeRequestsAssigneesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequestsMergeRequestsAssigneesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bab55ee270c7c739f71bbbd0fa5f1bfd73ac501b58457de646d0266b26839378)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="avatarUrl")
    def avatar_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "avatarUrl"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @builtins.property
    @jsii.member(jsii_name="webUrl")
    def web_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webUrl"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsAssignees]:
        return typing.cast(typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsAssignees], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsAssignees],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e82f104a9efe6d682aa982b710fd80851b626a454b43f2d41b52e2602f92d57e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequestsMergeRequestsAuthor",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataGitlabProjectMergeRequestsMergeRequestsAuthor:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGitlabProjectMergeRequestsMergeRequestsAuthor(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGitlabProjectMergeRequestsMergeRequestsAuthorOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequestsMergeRequestsAuthorOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0f8c894499aff77694332ac7d5b5b96aa7df29628b1fd00badc018da62b2e5e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="avatarUrl")
    def avatar_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "avatarUrl"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @builtins.property
    @jsii.member(jsii_name="webUrl")
    def web_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webUrl"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsAuthor]:
        return typing.cast(typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsAuthor], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsAuthor],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4a322700ecebd12e25b95a11e9c127cf2cd7eebe6a87a6dc61d63c4b836ee71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequestsMergeRequestsClosedBy",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataGitlabProjectMergeRequestsMergeRequestsClosedBy:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGitlabProjectMergeRequestsMergeRequestsClosedBy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGitlabProjectMergeRequestsMergeRequestsClosedByOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequestsMergeRequestsClosedByOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e270e720c993053cfe52f61e6e92bd2a5f049c17b02ec6684472e854222fd1c0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="avatarUrl")
    def avatar_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "avatarUrl"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @builtins.property
    @jsii.member(jsii_name="webUrl")
    def web_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webUrl"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsClosedBy]:
        return typing.cast(typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsClosedBy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsClosedBy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c472b4626502c2a32489569754515ddac413e3d8e844c10d0e02299ecea42590)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataGitlabProjectMergeRequestsMergeRequestsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequestsMergeRequestsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad891e4ac174b402dd665416af3b5073875fd43a02086a64965ea79718797af5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataGitlabProjectMergeRequestsMergeRequestsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb22b77b1be4437bed39a2054e2262877a4c37d3b6d7f0290f724238ca09d123)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataGitlabProjectMergeRequestsMergeRequestsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57c8c36be5ebaaaccc981d0321ca9b91e597aafb68d130f53d1ea38a0f87aff4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51c16c0d38ba1be80598bd509e70fa7d9de3399ee37318df9ab1e3697bebf54c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0919ce930d7390a4549266678962bb052dcd1a43cce1d074d371673a8f49b5ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataGitlabProjectMergeRequestsMergeRequestsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.dataGitlabProjectMergeRequests.DataGitlabProjectMergeRequestsMergeRequestsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d212c5f1bc8188e1ef0e7f0688ed5d53ab5c3fdd53b8e51b9e39f11f6e96b09e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="assignee")
    def assignee(
        self,
    ) -> DataGitlabProjectMergeRequestsMergeRequestsAssigneeOutputReference:
        return typing.cast(DataGitlabProjectMergeRequestsMergeRequestsAssigneeOutputReference, jsii.get(self, "assignee"))

    @builtins.property
    @jsii.member(jsii_name="assignees")
    def assignees(self) -> DataGitlabProjectMergeRequestsMergeRequestsAssigneesList:
        return typing.cast(DataGitlabProjectMergeRequestsMergeRequestsAssigneesList, jsii.get(self, "assignees"))

    @builtins.property
    @jsii.member(jsii_name="author")
    def author(
        self,
    ) -> DataGitlabProjectMergeRequestsMergeRequestsAuthorOutputReference:
        return typing.cast(DataGitlabProjectMergeRequestsMergeRequestsAuthorOutputReference, jsii.get(self, "author"))

    @builtins.property
    @jsii.member(jsii_name="blockingDiscussionsResolved")
    def blocking_discussions_resolved(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "blockingDiscussionsResolved"))

    @builtins.property
    @jsii.member(jsii_name="closedAt")
    def closed_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "closedAt"))

    @builtins.property
    @jsii.member(jsii_name="closedBy")
    def closed_by(
        self,
    ) -> DataGitlabProjectMergeRequestsMergeRequestsClosedByOutputReference:
        return typing.cast(DataGitlabProjectMergeRequestsMergeRequestsClosedByOutputReference, jsii.get(self, "closedBy"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="iid")
    def iid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iid"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataGitlabProjectMergeRequestsMergeRequests]:
        return typing.cast(typing.Optional[DataGitlabProjectMergeRequestsMergeRequests], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataGitlabProjectMergeRequestsMergeRequests],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6156cacdf820c12b106554e21946a2355019c7e165e6687623b809ca1d473298)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataGitlabProjectMergeRequests",
    "DataGitlabProjectMergeRequestsConfig",
    "DataGitlabProjectMergeRequestsMergeRequests",
    "DataGitlabProjectMergeRequestsMergeRequestsAssignee",
    "DataGitlabProjectMergeRequestsMergeRequestsAssigneeOutputReference",
    "DataGitlabProjectMergeRequestsMergeRequestsAssignees",
    "DataGitlabProjectMergeRequestsMergeRequestsAssigneesList",
    "DataGitlabProjectMergeRequestsMergeRequestsAssigneesOutputReference",
    "DataGitlabProjectMergeRequestsMergeRequestsAuthor",
    "DataGitlabProjectMergeRequestsMergeRequestsAuthorOutputReference",
    "DataGitlabProjectMergeRequestsMergeRequestsClosedBy",
    "DataGitlabProjectMergeRequestsMergeRequestsClosedByOutputReference",
    "DataGitlabProjectMergeRequestsMergeRequestsList",
    "DataGitlabProjectMergeRequestsMergeRequestsOutputReference",
]

publication.publish()

def _typecheckingstub__3bb091d0b95be2485a22fd00fb265fcba670b7f1cef77b2544bca851bf6de0d6(
    scope_: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    project: builtins.str,
    author_id: typing.Optional[jsii.Number] = None,
    author_username: typing.Optional[builtins.str] = None,
    created_after: typing.Optional[builtins.str] = None,
    created_before: typing.Optional[builtins.str] = None,
    iids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    milestone: typing.Optional[builtins.str] = None,
    my_reaction_emoji: typing.Optional[builtins.str] = None,
    order_by: typing.Optional[builtins.str] = None,
    reviewer_username: typing.Optional[builtins.str] = None,
    scope: typing.Optional[builtins.str] = None,
    search: typing.Optional[builtins.str] = None,
    sort: typing.Optional[builtins.str] = None,
    source_branch: typing.Optional[builtins.str] = None,
    state: typing.Optional[builtins.str] = None,
    target_branch: typing.Optional[builtins.str] = None,
    updated_after: typing.Optional[builtins.str] = None,
    updated_before: typing.Optional[builtins.str] = None,
    wip: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__20c09809e1abe65f2971ba67e1886becdaf006f4c79d3d4e1525a71502e7f651(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ee8de5bf56a4e65561d87295befa38bdc06da6f8cb082c94192313692e4f548(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9efa43b04bebdb0a67b09f84f90f63da8459dab969eaa742c8f545b4bfdfcf60(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f25f749b04c68345f689b9b1bdf586167a27d1975ab2304fa9fa0da5db736b97(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01e595852005604bb625ab5ed0cc545bc376a6011337336c4f595006219c4784(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__778e55fe5a8353b9df6219dfdd27357c3965b7f6350d81250c280c0c5e4f611e(
    value: typing.List[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__826e41d1ac4d443e7094c1caffaf6a24c7b4773c3f696c601db5c00a610663f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99884ae8e6e5db238c2a41ddf41a245738a3f0ae07ab2b948bdffafe486f716c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04b32ee29f63f298dbf7b2a6b9353536d9d1796b9fc15ddf8f4753509336ff18(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b9f1d3cc7b649e04dc27c9dd5822a866b9cf38881bd8aa40d075f755d496e4a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e42377f0366da6464fc0c86417aa1670afa1fbf46db25c9eb6fbda4b75f162b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c65c66d954d6f128f778f1adf6def3d0c50695aa1bc9e7f224deb368930f6ff3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6688017cb5bc90c1ede332ac77cef30ab6334a39da07e2767f2dd507a3260908(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ee32fa31473f5de0b9de74015998233c7b75b81f485271b511b8b83000910d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec3486bebcdf26df55b5b3de268938dc50e64f320c27864195894ddd6b437be3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39f742f24ea4843410f3f089ce1616dbb4aa30d0573b39f8da237d7f3156206f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f2f7d37180efd2ffaada620e6a8b886f457fd60bedbb613a0ea9b548be62b53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__334feb88e9d97a7e1bc039e2f00229fe9de5035942f4ac9b9a24df41f3af1c1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05ce02c67caed9de555b1f1a90fdf81fb84cac084d819d96e52adb8292eb1ec9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba10ab059c7a8525b40f1235f911e674798413e0d5755728ab6ac7d0a803eb87(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64d614f3339412a80d705c2591244cdacfbc471003ff4e9f8aec16bbc71d081b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    project: builtins.str,
    author_id: typing.Optional[jsii.Number] = None,
    author_username: typing.Optional[builtins.str] = None,
    created_after: typing.Optional[builtins.str] = None,
    created_before: typing.Optional[builtins.str] = None,
    iids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    milestone: typing.Optional[builtins.str] = None,
    my_reaction_emoji: typing.Optional[builtins.str] = None,
    order_by: typing.Optional[builtins.str] = None,
    reviewer_username: typing.Optional[builtins.str] = None,
    scope: typing.Optional[builtins.str] = None,
    search: typing.Optional[builtins.str] = None,
    sort: typing.Optional[builtins.str] = None,
    source_branch: typing.Optional[builtins.str] = None,
    state: typing.Optional[builtins.str] = None,
    target_branch: typing.Optional[builtins.str] = None,
    updated_after: typing.Optional[builtins.str] = None,
    updated_before: typing.Optional[builtins.str] = None,
    wip: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75b804b889ffe957c1a9ed47c0ad04af9eff2aadee1ee6646f7cd2ac6499d9a2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__750cadef11a78edf7c27d989f23d9a47f8d7df7513de19bc2926db88ab3a0315(
    value: typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsAssignee],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8f56c0882cab85b08ad86af671b02026ecc952ced283dcd6e1e85bbecd399ea(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87199165a3a8992677dd91c0fe3f377a0e224785500ea5bb5a9382801b0eebc9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a944c09f34986e42146489522afe39df14ade2518c59e8d725a9b213b502aeb8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3c6a0195959269ea1220944d19cb2c27f9576a7b6eaa1724a6fe98e97aa18a8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c5d36aefe3d25f91c8d2cc5bd3cca502bc2bc093d6207499e7eb395294aff50(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bab55ee270c7c739f71bbbd0fa5f1bfd73ac501b58457de646d0266b26839378(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e82f104a9efe6d682aa982b710fd80851b626a454b43f2d41b52e2602f92d57e(
    value: typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsAssignees],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0f8c894499aff77694332ac7d5b5b96aa7df29628b1fd00badc018da62b2e5e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4a322700ecebd12e25b95a11e9c127cf2cd7eebe6a87a6dc61d63c4b836ee71(
    value: typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsAuthor],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e270e720c993053cfe52f61e6e92bd2a5f049c17b02ec6684472e854222fd1c0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c472b4626502c2a32489569754515ddac413e3d8e844c10d0e02299ecea42590(
    value: typing.Optional[DataGitlabProjectMergeRequestsMergeRequestsClosedBy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad891e4ac174b402dd665416af3b5073875fd43a02086a64965ea79718797af5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb22b77b1be4437bed39a2054e2262877a4c37d3b6d7f0290f724238ca09d123(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57c8c36be5ebaaaccc981d0321ca9b91e597aafb68d130f53d1ea38a0f87aff4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51c16c0d38ba1be80598bd509e70fa7d9de3399ee37318df9ab1e3697bebf54c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0919ce930d7390a4549266678962bb052dcd1a43cce1d074d371673a8f49b5ee(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d212c5f1bc8188e1ef0e7f0688ed5d53ab5c3fdd53b8e51b9e39f11f6e96b09e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6156cacdf820c12b106554e21946a2355019c7e165e6687623b809ca1d473298(
    value: typing.Optional[DataGitlabProjectMergeRequestsMergeRequests],
) -> None:
    """Type checking stubs"""
    pass
