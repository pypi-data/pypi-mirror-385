r'''
# `gitlab_project_integration_jira`

Refer to the Terraform Registry for docs: [`gitlab_project_integration_jira`](https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira).
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


class ProjectIntegrationJira(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.projectIntegrationJira.ProjectIntegrationJira",
):
    '''Represents a {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira gitlab_project_integration_jira}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        password: builtins.str,
        project: builtins.str,
        url: builtins.str,
        api_url: typing.Optional[builtins.str] = None,
        comment_on_event_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        commit_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        issues_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        jira_auth_type: typing.Optional[jsii.Number] = None,
        jira_issue_prefix: typing.Optional[builtins.str] = None,
        jira_issue_regex: typing.Optional[builtins.str] = None,
        jira_issue_transition_automatic: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        jira_issue_transition_id: typing.Optional[builtins.str] = None,
        merge_requests_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        project_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        use_inherited_settings: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira gitlab_project_integration_jira} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param password: The Jira API token, password, or personal access token to be used with Jira. When your authentication method is basic (jira_auth_type is 0), use an API token for Jira Cloud or a password for Jira Data Center or Jira Server. When your authentication method is a Jira personal access token (jira_auth_type is 1), use the personal access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#password ProjectIntegrationJira#password}
        :param project: ID of the project you want to activate integration on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#project ProjectIntegrationJira#project}
        :param url: The URL to the JIRA project which is being linked to this GitLab project. For example, https://jira.example.com. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#url ProjectIntegrationJira#url}
        :param api_url: The base URL to the Jira instance API. Web URL value is used if not set. For example, https://jira-api.example.com. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#api_url ProjectIntegrationJira#api_url}
        :param comment_on_event_enabled: Enable comments inside Jira issues on each GitLab event (commit / merge request). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#comment_on_event_enabled ProjectIntegrationJira#comment_on_event_enabled}
        :param commit_events: Enable notifications for commit events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#commit_events ProjectIntegrationJira#commit_events}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#id ProjectIntegrationJira#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issues_enabled: Enable viewing Jira issues in GitLab. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#issues_enabled ProjectIntegrationJira#issues_enabled}
        :param jira_auth_type: The authentication method to be used with Jira. 0 means Basic Authentication. 1 means Jira personal access token. Defaults to 0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_auth_type ProjectIntegrationJira#jira_auth_type}
        :param jira_issue_prefix: Prefix to match Jira issue keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_issue_prefix ProjectIntegrationJira#jira_issue_prefix}
        :param jira_issue_regex: Regular expression to match Jira issue keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_issue_regex ProjectIntegrationJira#jira_issue_regex}
        :param jira_issue_transition_automatic: Enable automatic issue transitions. Takes precedence over jira_issue_transition_id if enabled. Defaults to false. This value cannot be imported, and will not perform drift detection if changed outside Terraform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_issue_transition_automatic ProjectIntegrationJira#jira_issue_transition_automatic}
        :param jira_issue_transition_id: The ID of a transition that moves issues to a closed state. You can find this number under the JIRA workflow administration (Administration > Issues > Workflows) by selecting View under Operations of the desired workflow of your project. By default, this ID is set to 2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_issue_transition_id ProjectIntegrationJira#jira_issue_transition_id}
        :param merge_requests_events: Enable notifications for merge request events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#merge_requests_events ProjectIntegrationJira#merge_requests_events}
        :param project_keys: Keys of Jira projects. When issues_enabled is true, this setting specifies which Jira projects to view issues from in GitLab. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#project_keys ProjectIntegrationJira#project_keys}
        :param use_inherited_settings: Indicates whether or not to inherit default settings. Defaults to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#use_inherited_settings ProjectIntegrationJira#use_inherited_settings}
        :param username: The email or username to be used with Jira. For Jira Cloud use an email, for Jira Data Center and Jira Server use a username. Required when using Basic authentication (jira_auth_type is 0). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#username ProjectIntegrationJira#username}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b34e7c02e9a52bea39080dd72b60a9f7c7cd3c5ff44e7ecbd44c904e4a59b9d4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProjectIntegrationJiraConfig(
            password=password,
            project=project,
            url=url,
            api_url=api_url,
            comment_on_event_enabled=comment_on_event_enabled,
            commit_events=commit_events,
            id=id,
            issues_enabled=issues_enabled,
            jira_auth_type=jira_auth_type,
            jira_issue_prefix=jira_issue_prefix,
            jira_issue_regex=jira_issue_regex,
            jira_issue_transition_automatic=jira_issue_transition_automatic,
            jira_issue_transition_id=jira_issue_transition_id,
            merge_requests_events=merge_requests_events,
            project_keys=project_keys,
            use_inherited_settings=use_inherited_settings,
            username=username,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a ProjectIntegrationJira resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProjectIntegrationJira to import.
        :param import_from_id: The id of the existing ProjectIntegrationJira that should be imported. Refer to the {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProjectIntegrationJira to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f45f6f8b0e3895fddd801c59d0fa3e82c928537c2cd35ad48ab6d7c1646b7fa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetApiUrl")
    def reset_api_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiUrl", []))

    @jsii.member(jsii_name="resetCommentOnEventEnabled")
    def reset_comment_on_event_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommentOnEventEnabled", []))

    @jsii.member(jsii_name="resetCommitEvents")
    def reset_commit_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommitEvents", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIssuesEnabled")
    def reset_issues_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIssuesEnabled", []))

    @jsii.member(jsii_name="resetJiraAuthType")
    def reset_jira_auth_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJiraAuthType", []))

    @jsii.member(jsii_name="resetJiraIssuePrefix")
    def reset_jira_issue_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJiraIssuePrefix", []))

    @jsii.member(jsii_name="resetJiraIssueRegex")
    def reset_jira_issue_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJiraIssueRegex", []))

    @jsii.member(jsii_name="resetJiraIssueTransitionAutomatic")
    def reset_jira_issue_transition_automatic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJiraIssueTransitionAutomatic", []))

    @jsii.member(jsii_name="resetJiraIssueTransitionId")
    def reset_jira_issue_transition_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJiraIssueTransitionId", []))

    @jsii.member(jsii_name="resetMergeRequestsEvents")
    def reset_merge_requests_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMergeRequestsEvents", []))

    @jsii.member(jsii_name="resetProjectKeys")
    def reset_project_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectKeys", []))

    @jsii.member(jsii_name="resetUseInheritedSettings")
    def reset_use_inherited_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseInheritedSettings", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

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
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="apiUrlInput")
    def api_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="commentOnEventEnabledInput")
    def comment_on_event_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "commentOnEventEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="commitEventsInput")
    def commit_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "commitEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="issuesEnabledInput")
    def issues_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "issuesEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="jiraAuthTypeInput")
    def jira_auth_type_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "jiraAuthTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="jiraIssuePrefixInput")
    def jira_issue_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jiraIssuePrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="jiraIssueRegexInput")
    def jira_issue_regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jiraIssueRegexInput"))

    @builtins.property
    @jsii.member(jsii_name="jiraIssueTransitionAutomaticInput")
    def jira_issue_transition_automatic_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "jiraIssueTransitionAutomaticInput"))

    @builtins.property
    @jsii.member(jsii_name="jiraIssueTransitionIdInput")
    def jira_issue_transition_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jiraIssueTransitionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="mergeRequestsEventsInput")
    def merge_requests_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "mergeRequestsEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="projectKeysInput")
    def project_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "projectKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="useInheritedSettingsInput")
    def use_inherited_settings_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useInheritedSettingsInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="apiUrl")
    def api_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiUrl"))

    @api_url.setter
    def api_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43c34a45760881dc347185c7f350c540738ba0ecb17ccc8cefd4d430f753ab73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="commentOnEventEnabled")
    def comment_on_event_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "commentOnEventEnabled"))

    @comment_on_event_enabled.setter
    def comment_on_event_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e812fb66dc1209201211bf37ad211c8ded6626dc49abc0616154e182e1ac6941)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commentOnEventEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="commitEvents")
    def commit_events(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "commitEvents"))

    @commit_events.setter
    def commit_events(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b8929ba62728d8e496f38e83255204ffd57d3b69724667d0493c5b28d19b5ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commitEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cba068caef367ade69c2a7c09c3a2ccde1eaba85714a1f1229b4a939dd2cf003)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issuesEnabled")
    def issues_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "issuesEnabled"))

    @issues_enabled.setter
    def issues_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e24464dcbfe73068125cf73d024c134a8079332f862ea9e47cb93fe659fb80a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuesEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jiraAuthType")
    def jira_auth_type(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "jiraAuthType"))

    @jira_auth_type.setter
    def jira_auth_type(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67169cb9b1c5159eafd88d63537252a2302fde8a6ea687430fb2078bc6afd97b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jiraAuthType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jiraIssuePrefix")
    def jira_issue_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jiraIssuePrefix"))

    @jira_issue_prefix.setter
    def jira_issue_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb5b56fc0937c167fe82f4125b8a9abd1c81b6f8c311122576ac2ad6a0dcf001)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jiraIssuePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jiraIssueRegex")
    def jira_issue_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jiraIssueRegex"))

    @jira_issue_regex.setter
    def jira_issue_regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b8fbfcba37879fdc1a3e8330031e1cc6c6cc32a16dc75d4f11c79ef00c49e1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jiraIssueRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jiraIssueTransitionAutomatic")
    def jira_issue_transition_automatic(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "jiraIssueTransitionAutomatic"))

    @jira_issue_transition_automatic.setter
    def jira_issue_transition_automatic(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__017e86986b9732194d89f2908e184550037da9855d8540974c117623dab4300b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jiraIssueTransitionAutomatic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jiraIssueTransitionId")
    def jira_issue_transition_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jiraIssueTransitionId"))

    @jira_issue_transition_id.setter
    def jira_issue_transition_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce4f3a4268c2d508b44e69f6b28bca3aa42c1200c5206a73f815c0183b5d0ec3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jiraIssueTransitionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mergeRequestsEvents")
    def merge_requests_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "mergeRequestsEvents"))

    @merge_requests_events.setter
    def merge_requests_events(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c5b6660ca9e8d5955eadc5964f25a5681e9060c4b09753ecd5e0aba7f11ab76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mergeRequestsEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c35cd48b91cad46c1a98218fcc7622c49838633ccc8dfaa99bbe3cf16cdaf7dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01145a198edb4de4beb9cfc4020acb39a18551c278cc1be5a73301cccd497f2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectKeys")
    def project_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "projectKeys"))

    @project_keys.setter
    def project_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d92b9506c92d0a546dae0a2945dc268d013d6b94684c049ed82ff263b879080f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ad86f1cd92a81bfa53b8239cfe757a4dafdf4e8bfd754e4d7bf5696dae0cf1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useInheritedSettings")
    def use_inherited_settings(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useInheritedSettings"))

    @use_inherited_settings.setter
    def use_inherited_settings(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b65cad4d667ba709a14d4e2d15e891eb4bc4e2005d1a19dd8880662ed970552)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useInheritedSettings", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ac86c118e6d7f8bc223035b49482fa0d6adb30773a4b08baadb48d83556cc6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.projectIntegrationJira.ProjectIntegrationJiraConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "password": "password",
        "project": "project",
        "url": "url",
        "api_url": "apiUrl",
        "comment_on_event_enabled": "commentOnEventEnabled",
        "commit_events": "commitEvents",
        "id": "id",
        "issues_enabled": "issuesEnabled",
        "jira_auth_type": "jiraAuthType",
        "jira_issue_prefix": "jiraIssuePrefix",
        "jira_issue_regex": "jiraIssueRegex",
        "jira_issue_transition_automatic": "jiraIssueTransitionAutomatic",
        "jira_issue_transition_id": "jiraIssueTransitionId",
        "merge_requests_events": "mergeRequestsEvents",
        "project_keys": "projectKeys",
        "use_inherited_settings": "useInheritedSettings",
        "username": "username",
    },
)
class ProjectIntegrationJiraConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        password: builtins.str,
        project: builtins.str,
        url: builtins.str,
        api_url: typing.Optional[builtins.str] = None,
        comment_on_event_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        commit_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        issues_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        jira_auth_type: typing.Optional[jsii.Number] = None,
        jira_issue_prefix: typing.Optional[builtins.str] = None,
        jira_issue_regex: typing.Optional[builtins.str] = None,
        jira_issue_transition_automatic: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        jira_issue_transition_id: typing.Optional[builtins.str] = None,
        merge_requests_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        project_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        use_inherited_settings: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param password: The Jira API token, password, or personal access token to be used with Jira. When your authentication method is basic (jira_auth_type is 0), use an API token for Jira Cloud or a password for Jira Data Center or Jira Server. When your authentication method is a Jira personal access token (jira_auth_type is 1), use the personal access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#password ProjectIntegrationJira#password}
        :param project: ID of the project you want to activate integration on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#project ProjectIntegrationJira#project}
        :param url: The URL to the JIRA project which is being linked to this GitLab project. For example, https://jira.example.com. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#url ProjectIntegrationJira#url}
        :param api_url: The base URL to the Jira instance API. Web URL value is used if not set. For example, https://jira-api.example.com. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#api_url ProjectIntegrationJira#api_url}
        :param comment_on_event_enabled: Enable comments inside Jira issues on each GitLab event (commit / merge request). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#comment_on_event_enabled ProjectIntegrationJira#comment_on_event_enabled}
        :param commit_events: Enable notifications for commit events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#commit_events ProjectIntegrationJira#commit_events}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#id ProjectIntegrationJira#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issues_enabled: Enable viewing Jira issues in GitLab. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#issues_enabled ProjectIntegrationJira#issues_enabled}
        :param jira_auth_type: The authentication method to be used with Jira. 0 means Basic Authentication. 1 means Jira personal access token. Defaults to 0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_auth_type ProjectIntegrationJira#jira_auth_type}
        :param jira_issue_prefix: Prefix to match Jira issue keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_issue_prefix ProjectIntegrationJira#jira_issue_prefix}
        :param jira_issue_regex: Regular expression to match Jira issue keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_issue_regex ProjectIntegrationJira#jira_issue_regex}
        :param jira_issue_transition_automatic: Enable automatic issue transitions. Takes precedence over jira_issue_transition_id if enabled. Defaults to false. This value cannot be imported, and will not perform drift detection if changed outside Terraform. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_issue_transition_automatic ProjectIntegrationJira#jira_issue_transition_automatic}
        :param jira_issue_transition_id: The ID of a transition that moves issues to a closed state. You can find this number under the JIRA workflow administration (Administration > Issues > Workflows) by selecting View under Operations of the desired workflow of your project. By default, this ID is set to 2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_issue_transition_id ProjectIntegrationJira#jira_issue_transition_id}
        :param merge_requests_events: Enable notifications for merge request events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#merge_requests_events ProjectIntegrationJira#merge_requests_events}
        :param project_keys: Keys of Jira projects. When issues_enabled is true, this setting specifies which Jira projects to view issues from in GitLab. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#project_keys ProjectIntegrationJira#project_keys}
        :param use_inherited_settings: Indicates whether or not to inherit default settings. Defaults to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#use_inherited_settings ProjectIntegrationJira#use_inherited_settings}
        :param username: The email or username to be used with Jira. For Jira Cloud use an email, for Jira Data Center and Jira Server use a username. Required when using Basic authentication (jira_auth_type is 0). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#username ProjectIntegrationJira#username}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8b8a33750c735b9c4b942367d26aa9dd80fc5ecaaafa038cb868f6e43da6ce5)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument api_url", value=api_url, expected_type=type_hints["api_url"])
            check_type(argname="argument comment_on_event_enabled", value=comment_on_event_enabled, expected_type=type_hints["comment_on_event_enabled"])
            check_type(argname="argument commit_events", value=commit_events, expected_type=type_hints["commit_events"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument issues_enabled", value=issues_enabled, expected_type=type_hints["issues_enabled"])
            check_type(argname="argument jira_auth_type", value=jira_auth_type, expected_type=type_hints["jira_auth_type"])
            check_type(argname="argument jira_issue_prefix", value=jira_issue_prefix, expected_type=type_hints["jira_issue_prefix"])
            check_type(argname="argument jira_issue_regex", value=jira_issue_regex, expected_type=type_hints["jira_issue_regex"])
            check_type(argname="argument jira_issue_transition_automatic", value=jira_issue_transition_automatic, expected_type=type_hints["jira_issue_transition_automatic"])
            check_type(argname="argument jira_issue_transition_id", value=jira_issue_transition_id, expected_type=type_hints["jira_issue_transition_id"])
            check_type(argname="argument merge_requests_events", value=merge_requests_events, expected_type=type_hints["merge_requests_events"])
            check_type(argname="argument project_keys", value=project_keys, expected_type=type_hints["project_keys"])
            check_type(argname="argument use_inherited_settings", value=use_inherited_settings, expected_type=type_hints["use_inherited_settings"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password": password,
            "project": project,
            "url": url,
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
        if api_url is not None:
            self._values["api_url"] = api_url
        if comment_on_event_enabled is not None:
            self._values["comment_on_event_enabled"] = comment_on_event_enabled
        if commit_events is not None:
            self._values["commit_events"] = commit_events
        if id is not None:
            self._values["id"] = id
        if issues_enabled is not None:
            self._values["issues_enabled"] = issues_enabled
        if jira_auth_type is not None:
            self._values["jira_auth_type"] = jira_auth_type
        if jira_issue_prefix is not None:
            self._values["jira_issue_prefix"] = jira_issue_prefix
        if jira_issue_regex is not None:
            self._values["jira_issue_regex"] = jira_issue_regex
        if jira_issue_transition_automatic is not None:
            self._values["jira_issue_transition_automatic"] = jira_issue_transition_automatic
        if jira_issue_transition_id is not None:
            self._values["jira_issue_transition_id"] = jira_issue_transition_id
        if merge_requests_events is not None:
            self._values["merge_requests_events"] = merge_requests_events
        if project_keys is not None:
            self._values["project_keys"] = project_keys
        if use_inherited_settings is not None:
            self._values["use_inherited_settings"] = use_inherited_settings
        if username is not None:
            self._values["username"] = username

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
    def password(self) -> builtins.str:
        '''The Jira API token, password, or personal access token to be used with Jira.

        When your authentication method is basic (jira_auth_type is 0), use an API token for Jira Cloud or a password for Jira Data Center or Jira Server. When your authentication method is a Jira personal access token (jira_auth_type is 1), use the personal access token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#password ProjectIntegrationJira#password}
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project(self) -> builtins.str:
        '''ID of the project you want to activate integration on.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#project ProjectIntegrationJira#project}
        '''
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def url(self) -> builtins.str:
        '''The URL to the JIRA project which is being linked to this GitLab project. For example, https://jira.example.com.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#url ProjectIntegrationJira#url}
        '''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_url(self) -> typing.Optional[builtins.str]:
        '''The base URL to the Jira instance API. Web URL value is used if not set. For example, https://jira-api.example.com.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#api_url ProjectIntegrationJira#api_url}
        '''
        result = self._values.get("api_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def comment_on_event_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable comments inside Jira issues on each GitLab event (commit / merge request).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#comment_on_event_enabled ProjectIntegrationJira#comment_on_event_enabled}
        '''
        result = self._values.get("comment_on_event_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def commit_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable notifications for commit events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#commit_events ProjectIntegrationJira#commit_events}
        '''
        result = self._values.get("commit_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#id ProjectIntegrationJira#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def issues_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable viewing Jira issues in GitLab.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#issues_enabled ProjectIntegrationJira#issues_enabled}
        '''
        result = self._values.get("issues_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def jira_auth_type(self) -> typing.Optional[jsii.Number]:
        '''The authentication method to be used with Jira.

        0 means Basic Authentication. 1 means Jira personal access token. Defaults to 0.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_auth_type ProjectIntegrationJira#jira_auth_type}
        '''
        result = self._values.get("jira_auth_type")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def jira_issue_prefix(self) -> typing.Optional[builtins.str]:
        '''Prefix to match Jira issue keys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_issue_prefix ProjectIntegrationJira#jira_issue_prefix}
        '''
        result = self._values.get("jira_issue_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jira_issue_regex(self) -> typing.Optional[builtins.str]:
        '''Regular expression to match Jira issue keys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_issue_regex ProjectIntegrationJira#jira_issue_regex}
        '''
        result = self._values.get("jira_issue_regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jira_issue_transition_automatic(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable automatic issue transitions.

        Takes precedence over jira_issue_transition_id if enabled. Defaults to false. This value cannot be imported, and will not perform drift detection if changed outside Terraform.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_issue_transition_automatic ProjectIntegrationJira#jira_issue_transition_automatic}
        '''
        result = self._values.get("jira_issue_transition_automatic")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def jira_issue_transition_id(self) -> typing.Optional[builtins.str]:
        '''The ID of a transition that moves issues to a closed state.

        You can find this number under the JIRA workflow administration (Administration > Issues > Workflows) by selecting View under Operations of the desired workflow of your project. By default, this ID is set to 2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#jira_issue_transition_id ProjectIntegrationJira#jira_issue_transition_id}
        '''
        result = self._values.get("jira_issue_transition_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def merge_requests_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable notifications for merge request events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#merge_requests_events ProjectIntegrationJira#merge_requests_events}
        '''
        result = self._values.get("merge_requests_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def project_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Keys of Jira projects.

        When issues_enabled is true, this setting specifies which Jira projects to view issues from in GitLab.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#project_keys ProjectIntegrationJira#project_keys}
        '''
        result = self._values.get("project_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def use_inherited_settings(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether or not to inherit default settings. Defaults to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#use_inherited_settings ProjectIntegrationJira#use_inherited_settings}
        '''
        result = self._values.get("use_inherited_settings")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The email or username to be used with Jira.

        For Jira Cloud use an email, for Jira Data Center and Jira Server use a username. Required when using Basic authentication (jira_auth_type is 0).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_jira#username ProjectIntegrationJira#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectIntegrationJiraConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProjectIntegrationJira",
    "ProjectIntegrationJiraConfig",
]

publication.publish()

def _typecheckingstub__b34e7c02e9a52bea39080dd72b60a9f7c7cd3c5ff44e7ecbd44c904e4a59b9d4(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    password: builtins.str,
    project: builtins.str,
    url: builtins.str,
    api_url: typing.Optional[builtins.str] = None,
    comment_on_event_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    commit_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    issues_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    jira_auth_type: typing.Optional[jsii.Number] = None,
    jira_issue_prefix: typing.Optional[builtins.str] = None,
    jira_issue_regex: typing.Optional[builtins.str] = None,
    jira_issue_transition_automatic: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    jira_issue_transition_id: typing.Optional[builtins.str] = None,
    merge_requests_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    project_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    use_inherited_settings: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    username: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__3f45f6f8b0e3895fddd801c59d0fa3e82c928537c2cd35ad48ab6d7c1646b7fa(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43c34a45760881dc347185c7f350c540738ba0ecb17ccc8cefd4d430f753ab73(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e812fb66dc1209201211bf37ad211c8ded6626dc49abc0616154e182e1ac6941(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b8929ba62728d8e496f38e83255204ffd57d3b69724667d0493c5b28d19b5ba(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cba068caef367ade69c2a7c09c3a2ccde1eaba85714a1f1229b4a939dd2cf003(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e24464dcbfe73068125cf73d024c134a8079332f862ea9e47cb93fe659fb80a6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67169cb9b1c5159eafd88d63537252a2302fde8a6ea687430fb2078bc6afd97b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb5b56fc0937c167fe82f4125b8a9abd1c81b6f8c311122576ac2ad6a0dcf001(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b8fbfcba37879fdc1a3e8330031e1cc6c6cc32a16dc75d4f11c79ef00c49e1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__017e86986b9732194d89f2908e184550037da9855d8540974c117623dab4300b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce4f3a4268c2d508b44e69f6b28bca3aa42c1200c5206a73f815c0183b5d0ec3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c5b6660ca9e8d5955eadc5964f25a5681e9060c4b09753ecd5e0aba7f11ab76(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c35cd48b91cad46c1a98218fcc7622c49838633ccc8dfaa99bbe3cf16cdaf7dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01145a198edb4de4beb9cfc4020acb39a18551c278cc1be5a73301cccd497f2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d92b9506c92d0a546dae0a2945dc268d013d6b94684c049ed82ff263b879080f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ad86f1cd92a81bfa53b8239cfe757a4dafdf4e8bfd754e4d7bf5696dae0cf1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b65cad4d667ba709a14d4e2d15e891eb4bc4e2005d1a19dd8880662ed970552(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ac86c118e6d7f8bc223035b49482fa0d6adb30773a4b08baadb48d83556cc6b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8b8a33750c735b9c4b942367d26aa9dd80fc5ecaaafa038cb868f6e43da6ce5(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    password: builtins.str,
    project: builtins.str,
    url: builtins.str,
    api_url: typing.Optional[builtins.str] = None,
    comment_on_event_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    commit_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    issues_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    jira_auth_type: typing.Optional[jsii.Number] = None,
    jira_issue_prefix: typing.Optional[builtins.str] = None,
    jira_issue_regex: typing.Optional[builtins.str] = None,
    jira_issue_transition_automatic: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    jira_issue_transition_id: typing.Optional[builtins.str] = None,
    merge_requests_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    project_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    use_inherited_settings: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
