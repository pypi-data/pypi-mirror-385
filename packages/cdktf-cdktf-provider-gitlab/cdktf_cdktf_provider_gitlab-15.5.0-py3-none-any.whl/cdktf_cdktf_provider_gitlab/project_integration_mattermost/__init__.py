r'''
# `gitlab_project_integration_mattermost`

Refer to the Terraform Registry for docs: [`gitlab_project_integration_mattermost`](https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost).
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


class ProjectIntegrationMattermost(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.projectIntegrationMattermost.ProjectIntegrationMattermost",
):
    '''Represents a {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost gitlab_project_integration_mattermost}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        project: builtins.str,
        webhook: builtins.str,
        branches_to_be_notified: typing.Optional[builtins.str] = None,
        confidential_issue_channel: typing.Optional[builtins.str] = None,
        confidential_issues_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        confidential_note_channel: typing.Optional[builtins.str] = None,
        confidential_note_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        issue_channel: typing.Optional[builtins.str] = None,
        issues_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        merge_request_channel: typing.Optional[builtins.str] = None,
        merge_requests_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        note_channel: typing.Optional[builtins.str] = None,
        note_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        notify_only_broken_pipelines: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pipeline_channel: typing.Optional[builtins.str] = None,
        pipeline_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        push_channel: typing.Optional[builtins.str] = None,
        push_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag_push_channel: typing.Optional[builtins.str] = None,
        tag_push_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
        wiki_page_channel: typing.Optional[builtins.str] = None,
        wiki_page_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost gitlab_project_integration_mattermost} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param project: ID of the project you want to activate integration on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#project ProjectIntegrationMattermost#project}
        :param webhook: Webhook URL (Example, https://mattermost.yourdomain.com/hooks/...). This value cannot be imported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#webhook ProjectIntegrationMattermost#webhook}
        :param branches_to_be_notified: Branches to send notifications for. Valid options are "all", "default", "protected", and "default_and_protected". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#branches_to_be_notified ProjectIntegrationMattermost#branches_to_be_notified}
        :param confidential_issue_channel: The name of the channel to receive confidential issue events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#confidential_issue_channel ProjectIntegrationMattermost#confidential_issue_channel}
        :param confidential_issues_events: Enable notifications for confidential issues events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#confidential_issues_events ProjectIntegrationMattermost#confidential_issues_events}
        :param confidential_note_channel: The name of the channel to receive confidential note events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#confidential_note_channel ProjectIntegrationMattermost#confidential_note_channel}
        :param confidential_note_events: Enable notifications for confidential note events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#confidential_note_events ProjectIntegrationMattermost#confidential_note_events}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#id ProjectIntegrationMattermost#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issue_channel: The name of the channel to receive issue events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#issue_channel ProjectIntegrationMattermost#issue_channel}
        :param issues_events: Enable notifications for issues events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#issues_events ProjectIntegrationMattermost#issues_events}
        :param merge_request_channel: The name of the channel to receive merge request events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#merge_request_channel ProjectIntegrationMattermost#merge_request_channel}
        :param merge_requests_events: Enable notifications for merge requests events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#merge_requests_events ProjectIntegrationMattermost#merge_requests_events}
        :param note_channel: The name of the channel to receive note events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#note_channel ProjectIntegrationMattermost#note_channel}
        :param note_events: Enable notifications for note events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#note_events ProjectIntegrationMattermost#note_events}
        :param notify_only_broken_pipelines: Send notifications for broken pipelines. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#notify_only_broken_pipelines ProjectIntegrationMattermost#notify_only_broken_pipelines}
        :param pipeline_channel: The name of the channel to receive pipeline events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#pipeline_channel ProjectIntegrationMattermost#pipeline_channel}
        :param pipeline_events: Enable notifications for pipeline events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#pipeline_events ProjectIntegrationMattermost#pipeline_events}
        :param push_channel: The name of the channel to receive push events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#push_channel ProjectIntegrationMattermost#push_channel}
        :param push_events: Enable notifications for push events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#push_events ProjectIntegrationMattermost#push_events}
        :param tag_push_channel: The name of the channel to receive tag push events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#tag_push_channel ProjectIntegrationMattermost#tag_push_channel}
        :param tag_push_events: Enable notifications for tag push events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#tag_push_events ProjectIntegrationMattermost#tag_push_events}
        :param username: Username to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#username ProjectIntegrationMattermost#username}
        :param wiki_page_channel: The name of the channel to receive wiki page events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#wiki_page_channel ProjectIntegrationMattermost#wiki_page_channel}
        :param wiki_page_events: Enable notifications for wiki page events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#wiki_page_events ProjectIntegrationMattermost#wiki_page_events}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed190c66c0caf7b9a2bcfe9441c342f179c91e8715b16824316082b2f4e4bb86)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProjectIntegrationMattermostConfig(
            project=project,
            webhook=webhook,
            branches_to_be_notified=branches_to_be_notified,
            confidential_issue_channel=confidential_issue_channel,
            confidential_issues_events=confidential_issues_events,
            confidential_note_channel=confidential_note_channel,
            confidential_note_events=confidential_note_events,
            id=id,
            issue_channel=issue_channel,
            issues_events=issues_events,
            merge_request_channel=merge_request_channel,
            merge_requests_events=merge_requests_events,
            note_channel=note_channel,
            note_events=note_events,
            notify_only_broken_pipelines=notify_only_broken_pipelines,
            pipeline_channel=pipeline_channel,
            pipeline_events=pipeline_events,
            push_channel=push_channel,
            push_events=push_events,
            tag_push_channel=tag_push_channel,
            tag_push_events=tag_push_events,
            username=username,
            wiki_page_channel=wiki_page_channel,
            wiki_page_events=wiki_page_events,
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
        '''Generates CDKTF code for importing a ProjectIntegrationMattermost resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProjectIntegrationMattermost to import.
        :param import_from_id: The id of the existing ProjectIntegrationMattermost that should be imported. Refer to the {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProjectIntegrationMattermost to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52535f01074850e51c1d320a623b011a293f4e431076cc2dd36450eba52e2131)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBranchesToBeNotified")
    def reset_branches_to_be_notified(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBranchesToBeNotified", []))

    @jsii.member(jsii_name="resetConfidentialIssueChannel")
    def reset_confidential_issue_channel(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfidentialIssueChannel", []))

    @jsii.member(jsii_name="resetConfidentialIssuesEvents")
    def reset_confidential_issues_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfidentialIssuesEvents", []))

    @jsii.member(jsii_name="resetConfidentialNoteChannel")
    def reset_confidential_note_channel(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfidentialNoteChannel", []))

    @jsii.member(jsii_name="resetConfidentialNoteEvents")
    def reset_confidential_note_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfidentialNoteEvents", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIssueChannel")
    def reset_issue_channel(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIssueChannel", []))

    @jsii.member(jsii_name="resetIssuesEvents")
    def reset_issues_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIssuesEvents", []))

    @jsii.member(jsii_name="resetMergeRequestChannel")
    def reset_merge_request_channel(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMergeRequestChannel", []))

    @jsii.member(jsii_name="resetMergeRequestsEvents")
    def reset_merge_requests_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMergeRequestsEvents", []))

    @jsii.member(jsii_name="resetNoteChannel")
    def reset_note_channel(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoteChannel", []))

    @jsii.member(jsii_name="resetNoteEvents")
    def reset_note_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoteEvents", []))

    @jsii.member(jsii_name="resetNotifyOnlyBrokenPipelines")
    def reset_notify_only_broken_pipelines(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotifyOnlyBrokenPipelines", []))

    @jsii.member(jsii_name="resetPipelineChannel")
    def reset_pipeline_channel(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPipelineChannel", []))

    @jsii.member(jsii_name="resetPipelineEvents")
    def reset_pipeline_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPipelineEvents", []))

    @jsii.member(jsii_name="resetPushChannel")
    def reset_push_channel(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPushChannel", []))

    @jsii.member(jsii_name="resetPushEvents")
    def reset_push_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPushEvents", []))

    @jsii.member(jsii_name="resetTagPushChannel")
    def reset_tag_push_channel(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagPushChannel", []))

    @jsii.member(jsii_name="resetTagPushEvents")
    def reset_tag_push_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagPushEvents", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetWikiPageChannel")
    def reset_wiki_page_channel(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWikiPageChannel", []))

    @jsii.member(jsii_name="resetWikiPageEvents")
    def reset_wiki_page_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWikiPageEvents", []))

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
    @jsii.member(jsii_name="branchesToBeNotifiedInput")
    def branches_to_be_notified_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "branchesToBeNotifiedInput"))

    @builtins.property
    @jsii.member(jsii_name="confidentialIssueChannelInput")
    def confidential_issue_channel_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "confidentialIssueChannelInput"))

    @builtins.property
    @jsii.member(jsii_name="confidentialIssuesEventsInput")
    def confidential_issues_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "confidentialIssuesEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="confidentialNoteChannelInput")
    def confidential_note_channel_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "confidentialNoteChannelInput"))

    @builtins.property
    @jsii.member(jsii_name="confidentialNoteEventsInput")
    def confidential_note_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "confidentialNoteEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="issueChannelInput")
    def issue_channel_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issueChannelInput"))

    @builtins.property
    @jsii.member(jsii_name="issuesEventsInput")
    def issues_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "issuesEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="mergeRequestChannelInput")
    def merge_request_channel_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mergeRequestChannelInput"))

    @builtins.property
    @jsii.member(jsii_name="mergeRequestsEventsInput")
    def merge_requests_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "mergeRequestsEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="noteChannelInput")
    def note_channel_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "noteChannelInput"))

    @builtins.property
    @jsii.member(jsii_name="noteEventsInput")
    def note_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "noteEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="notifyOnlyBrokenPipelinesInput")
    def notify_only_broken_pipelines_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "notifyOnlyBrokenPipelinesInput"))

    @builtins.property
    @jsii.member(jsii_name="pipelineChannelInput")
    def pipeline_channel_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pipelineChannelInput"))

    @builtins.property
    @jsii.member(jsii_name="pipelineEventsInput")
    def pipeline_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pipelineEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="projectInput")
    def project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectInput"))

    @builtins.property
    @jsii.member(jsii_name="pushChannelInput")
    def push_channel_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pushChannelInput"))

    @builtins.property
    @jsii.member(jsii_name="pushEventsInput")
    def push_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pushEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="tagPushChannelInput")
    def tag_push_channel_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagPushChannelInput"))

    @builtins.property
    @jsii.member(jsii_name="tagPushEventsInput")
    def tag_push_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tagPushEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="webhookInput")
    def webhook_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "webhookInput"))

    @builtins.property
    @jsii.member(jsii_name="wikiPageChannelInput")
    def wiki_page_channel_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "wikiPageChannelInput"))

    @builtins.property
    @jsii.member(jsii_name="wikiPageEventsInput")
    def wiki_page_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "wikiPageEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="branchesToBeNotified")
    def branches_to_be_notified(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "branchesToBeNotified"))

    @branches_to_be_notified.setter
    def branches_to_be_notified(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bed4851453031cd1e5a4db52cd688fa5ee1cb22b73bb86fdd6f04280053562c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "branchesToBeNotified", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="confidentialIssueChannel")
    def confidential_issue_channel(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "confidentialIssueChannel"))

    @confidential_issue_channel.setter
    def confidential_issue_channel(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cadc7d8f4051655c3b8a75fe37b2e7f7e25037437d95f9936e3f5c5a746f5660)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confidentialIssueChannel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="confidentialIssuesEvents")
    def confidential_issues_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "confidentialIssuesEvents"))

    @confidential_issues_events.setter
    def confidential_issues_events(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3496ca82d97f7fdf7c0130ad5899bd06edfc3a965a33b35ef3f7616ecc1e43de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confidentialIssuesEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="confidentialNoteChannel")
    def confidential_note_channel(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "confidentialNoteChannel"))

    @confidential_note_channel.setter
    def confidential_note_channel(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6be55997ce98bab5bf8a73a7e890ae3d566d05438212fe4794d74daa6507e38f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confidentialNoteChannel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="confidentialNoteEvents")
    def confidential_note_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "confidentialNoteEvents"))

    @confidential_note_events.setter
    def confidential_note_events(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaf8feba2f1b26327c4ab3ff5e76963e78a300acedbeab4b8f24704795ec8f62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confidentialNoteEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c741ce8031b6b3ca4145bf5a70e4b49fe97adab28134a226417d92b7603c837)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issueChannel")
    def issue_channel(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issueChannel"))

    @issue_channel.setter
    def issue_channel(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afe596738e9cc6643732a1376a2a6f6ebb3c769f0389b30d57f31264589a9a82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issueChannel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issuesEvents")
    def issues_events(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "issuesEvents"))

    @issues_events.setter
    def issues_events(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__437d5256191113da7cff4045e3ae7dad33f560630f62c2386fad27c9a416e524)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuesEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mergeRequestChannel")
    def merge_request_channel(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mergeRequestChannel"))

    @merge_request_channel.setter
    def merge_request_channel(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51a5f23739309e217c9d7878b629b63138ed0c1e1e63c624cd3f8f89896d27fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mergeRequestChannel", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__69e6aabefbf06dbb35b640fcbf0b882f1ecca8e642cef6a90c3a9d0921df0aac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mergeRequestsEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="noteChannel")
    def note_channel(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "noteChannel"))

    @note_channel.setter
    def note_channel(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a43f2fffddc310dcc5a841ba7d49d45be781bc462b1617629ea54f97983a2bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "noteChannel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="noteEvents")
    def note_events(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "noteEvents"))

    @note_events.setter
    def note_events(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98a92243389e7772c8644d4267448920fa5701187d1e2997a715210d09d34312)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "noteEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notifyOnlyBrokenPipelines")
    def notify_only_broken_pipelines(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "notifyOnlyBrokenPipelines"))

    @notify_only_broken_pipelines.setter
    def notify_only_broken_pipelines(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d9abd8305b22ef1de70f45ca068f6de2babeb0035d52a63feaf812940d558e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notifyOnlyBrokenPipelines", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pipelineChannel")
    def pipeline_channel(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineChannel"))

    @pipeline_channel.setter
    def pipeline_channel(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e560d133f9533de80cb038cdf7bf7254833de23c5edb04063079f2310d3dd63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pipelineChannel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pipelineEvents")
    def pipeline_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "pipelineEvents"))

    @pipeline_events.setter
    def pipeline_events(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__259fe440fea09b59729ee630c8750c5ca990bf58ee1a97b3c443c6ff25830d5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pipelineEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f589eedb3c4593cdc7e2687d1e135494057d1455d68ba9f82261f87f575f42c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pushChannel")
    def push_channel(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pushChannel"))

    @push_channel.setter
    def push_channel(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e655df312a8162cac2ed729de2784e359c33bcfcc8e4b2233a8024b54c16210f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pushChannel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pushEvents")
    def push_events(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "pushEvents"))

    @push_events.setter
    def push_events(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d12aef4929d70f546d8d3aee94dbb3a575b046677d8b1e9d765080bc47f2072a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pushEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tagPushChannel")
    def tag_push_channel(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagPushChannel"))

    @tag_push_channel.setter
    def tag_push_channel(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46f654e96ebae0b0441b53ef2db027dbe5f2caa287ffd5c044c6bcf011adf173)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagPushChannel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tagPushEvents")
    def tag_push_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tagPushEvents"))

    @tag_push_events.setter
    def tag_push_events(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3671f650eaf95073ccd4ea353cd0e31267dfb619515dba078d6b1ab7dd86cf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagPushEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a0e618f5a23aa1c25a05e74de0ad164e0b94098e76075afd05dd658ec4a230b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="webhook")
    def webhook(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webhook"))

    @webhook.setter
    def webhook(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e19764bd76474119998ffc3a2b974a0dba1ce611a35088c7c7a94c2d661aae22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webhook", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wikiPageChannel")
    def wiki_page_channel(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wikiPageChannel"))

    @wiki_page_channel.setter
    def wiki_page_channel(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce5df303a9010550f536cec9385827759406dc5b0d7885ea665f0b85ccec454a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wikiPageChannel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wikiPageEvents")
    def wiki_page_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "wikiPageEvents"))

    @wiki_page_events.setter
    def wiki_page_events(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bc098192fd0684af18bb150b9f96ae6d6662a4e92d27d90e4f69c5ba075a6b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wikiPageEvents", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.projectIntegrationMattermost.ProjectIntegrationMattermostConfig",
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
        "webhook": "webhook",
        "branches_to_be_notified": "branchesToBeNotified",
        "confidential_issue_channel": "confidentialIssueChannel",
        "confidential_issues_events": "confidentialIssuesEvents",
        "confidential_note_channel": "confidentialNoteChannel",
        "confidential_note_events": "confidentialNoteEvents",
        "id": "id",
        "issue_channel": "issueChannel",
        "issues_events": "issuesEvents",
        "merge_request_channel": "mergeRequestChannel",
        "merge_requests_events": "mergeRequestsEvents",
        "note_channel": "noteChannel",
        "note_events": "noteEvents",
        "notify_only_broken_pipelines": "notifyOnlyBrokenPipelines",
        "pipeline_channel": "pipelineChannel",
        "pipeline_events": "pipelineEvents",
        "push_channel": "pushChannel",
        "push_events": "pushEvents",
        "tag_push_channel": "tagPushChannel",
        "tag_push_events": "tagPushEvents",
        "username": "username",
        "wiki_page_channel": "wikiPageChannel",
        "wiki_page_events": "wikiPageEvents",
    },
)
class ProjectIntegrationMattermostConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        webhook: builtins.str,
        branches_to_be_notified: typing.Optional[builtins.str] = None,
        confidential_issue_channel: typing.Optional[builtins.str] = None,
        confidential_issues_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        confidential_note_channel: typing.Optional[builtins.str] = None,
        confidential_note_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        issue_channel: typing.Optional[builtins.str] = None,
        issues_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        merge_request_channel: typing.Optional[builtins.str] = None,
        merge_requests_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        note_channel: typing.Optional[builtins.str] = None,
        note_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        notify_only_broken_pipelines: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pipeline_channel: typing.Optional[builtins.str] = None,
        pipeline_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        push_channel: typing.Optional[builtins.str] = None,
        push_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tag_push_channel: typing.Optional[builtins.str] = None,
        tag_push_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
        wiki_page_channel: typing.Optional[builtins.str] = None,
        wiki_page_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param project: ID of the project you want to activate integration on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#project ProjectIntegrationMattermost#project}
        :param webhook: Webhook URL (Example, https://mattermost.yourdomain.com/hooks/...). This value cannot be imported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#webhook ProjectIntegrationMattermost#webhook}
        :param branches_to_be_notified: Branches to send notifications for. Valid options are "all", "default", "protected", and "default_and_protected". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#branches_to_be_notified ProjectIntegrationMattermost#branches_to_be_notified}
        :param confidential_issue_channel: The name of the channel to receive confidential issue events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#confidential_issue_channel ProjectIntegrationMattermost#confidential_issue_channel}
        :param confidential_issues_events: Enable notifications for confidential issues events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#confidential_issues_events ProjectIntegrationMattermost#confidential_issues_events}
        :param confidential_note_channel: The name of the channel to receive confidential note events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#confidential_note_channel ProjectIntegrationMattermost#confidential_note_channel}
        :param confidential_note_events: Enable notifications for confidential note events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#confidential_note_events ProjectIntegrationMattermost#confidential_note_events}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#id ProjectIntegrationMattermost#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issue_channel: The name of the channel to receive issue events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#issue_channel ProjectIntegrationMattermost#issue_channel}
        :param issues_events: Enable notifications for issues events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#issues_events ProjectIntegrationMattermost#issues_events}
        :param merge_request_channel: The name of the channel to receive merge request events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#merge_request_channel ProjectIntegrationMattermost#merge_request_channel}
        :param merge_requests_events: Enable notifications for merge requests events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#merge_requests_events ProjectIntegrationMattermost#merge_requests_events}
        :param note_channel: The name of the channel to receive note events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#note_channel ProjectIntegrationMattermost#note_channel}
        :param note_events: Enable notifications for note events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#note_events ProjectIntegrationMattermost#note_events}
        :param notify_only_broken_pipelines: Send notifications for broken pipelines. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#notify_only_broken_pipelines ProjectIntegrationMattermost#notify_only_broken_pipelines}
        :param pipeline_channel: The name of the channel to receive pipeline events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#pipeline_channel ProjectIntegrationMattermost#pipeline_channel}
        :param pipeline_events: Enable notifications for pipeline events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#pipeline_events ProjectIntegrationMattermost#pipeline_events}
        :param push_channel: The name of the channel to receive push events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#push_channel ProjectIntegrationMattermost#push_channel}
        :param push_events: Enable notifications for push events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#push_events ProjectIntegrationMattermost#push_events}
        :param tag_push_channel: The name of the channel to receive tag push events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#tag_push_channel ProjectIntegrationMattermost#tag_push_channel}
        :param tag_push_events: Enable notifications for tag push events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#tag_push_events ProjectIntegrationMattermost#tag_push_events}
        :param username: Username to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#username ProjectIntegrationMattermost#username}
        :param wiki_page_channel: The name of the channel to receive wiki page events notifications. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#wiki_page_channel ProjectIntegrationMattermost#wiki_page_channel}
        :param wiki_page_events: Enable notifications for wiki page events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#wiki_page_events ProjectIntegrationMattermost#wiki_page_events}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__299323036042fe27bde22965dff5800679766187a552dc34ef2985ea1b537bcb)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument webhook", value=webhook, expected_type=type_hints["webhook"])
            check_type(argname="argument branches_to_be_notified", value=branches_to_be_notified, expected_type=type_hints["branches_to_be_notified"])
            check_type(argname="argument confidential_issue_channel", value=confidential_issue_channel, expected_type=type_hints["confidential_issue_channel"])
            check_type(argname="argument confidential_issues_events", value=confidential_issues_events, expected_type=type_hints["confidential_issues_events"])
            check_type(argname="argument confidential_note_channel", value=confidential_note_channel, expected_type=type_hints["confidential_note_channel"])
            check_type(argname="argument confidential_note_events", value=confidential_note_events, expected_type=type_hints["confidential_note_events"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument issue_channel", value=issue_channel, expected_type=type_hints["issue_channel"])
            check_type(argname="argument issues_events", value=issues_events, expected_type=type_hints["issues_events"])
            check_type(argname="argument merge_request_channel", value=merge_request_channel, expected_type=type_hints["merge_request_channel"])
            check_type(argname="argument merge_requests_events", value=merge_requests_events, expected_type=type_hints["merge_requests_events"])
            check_type(argname="argument note_channel", value=note_channel, expected_type=type_hints["note_channel"])
            check_type(argname="argument note_events", value=note_events, expected_type=type_hints["note_events"])
            check_type(argname="argument notify_only_broken_pipelines", value=notify_only_broken_pipelines, expected_type=type_hints["notify_only_broken_pipelines"])
            check_type(argname="argument pipeline_channel", value=pipeline_channel, expected_type=type_hints["pipeline_channel"])
            check_type(argname="argument pipeline_events", value=pipeline_events, expected_type=type_hints["pipeline_events"])
            check_type(argname="argument push_channel", value=push_channel, expected_type=type_hints["push_channel"])
            check_type(argname="argument push_events", value=push_events, expected_type=type_hints["push_events"])
            check_type(argname="argument tag_push_channel", value=tag_push_channel, expected_type=type_hints["tag_push_channel"])
            check_type(argname="argument tag_push_events", value=tag_push_events, expected_type=type_hints["tag_push_events"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument wiki_page_channel", value=wiki_page_channel, expected_type=type_hints["wiki_page_channel"])
            check_type(argname="argument wiki_page_events", value=wiki_page_events, expected_type=type_hints["wiki_page_events"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "project": project,
            "webhook": webhook,
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
        if branches_to_be_notified is not None:
            self._values["branches_to_be_notified"] = branches_to_be_notified
        if confidential_issue_channel is not None:
            self._values["confidential_issue_channel"] = confidential_issue_channel
        if confidential_issues_events is not None:
            self._values["confidential_issues_events"] = confidential_issues_events
        if confidential_note_channel is not None:
            self._values["confidential_note_channel"] = confidential_note_channel
        if confidential_note_events is not None:
            self._values["confidential_note_events"] = confidential_note_events
        if id is not None:
            self._values["id"] = id
        if issue_channel is not None:
            self._values["issue_channel"] = issue_channel
        if issues_events is not None:
            self._values["issues_events"] = issues_events
        if merge_request_channel is not None:
            self._values["merge_request_channel"] = merge_request_channel
        if merge_requests_events is not None:
            self._values["merge_requests_events"] = merge_requests_events
        if note_channel is not None:
            self._values["note_channel"] = note_channel
        if note_events is not None:
            self._values["note_events"] = note_events
        if notify_only_broken_pipelines is not None:
            self._values["notify_only_broken_pipelines"] = notify_only_broken_pipelines
        if pipeline_channel is not None:
            self._values["pipeline_channel"] = pipeline_channel
        if pipeline_events is not None:
            self._values["pipeline_events"] = pipeline_events
        if push_channel is not None:
            self._values["push_channel"] = push_channel
        if push_events is not None:
            self._values["push_events"] = push_events
        if tag_push_channel is not None:
            self._values["tag_push_channel"] = tag_push_channel
        if tag_push_events is not None:
            self._values["tag_push_events"] = tag_push_events
        if username is not None:
            self._values["username"] = username
        if wiki_page_channel is not None:
            self._values["wiki_page_channel"] = wiki_page_channel
        if wiki_page_events is not None:
            self._values["wiki_page_events"] = wiki_page_events

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
        '''ID of the project you want to activate integration on.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#project ProjectIntegrationMattermost#project}
        '''
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def webhook(self) -> builtins.str:
        '''Webhook URL (Example, https://mattermost.yourdomain.com/hooks/...). This value cannot be imported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#webhook ProjectIntegrationMattermost#webhook}
        '''
        result = self._values.get("webhook")
        assert result is not None, "Required property 'webhook' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branches_to_be_notified(self) -> typing.Optional[builtins.str]:
        '''Branches to send notifications for. Valid options are "all", "default", "protected", and "default_and_protected".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#branches_to_be_notified ProjectIntegrationMattermost#branches_to_be_notified}
        '''
        result = self._values.get("branches_to_be_notified")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def confidential_issue_channel(self) -> typing.Optional[builtins.str]:
        '''The name of the channel to receive confidential issue events notifications.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#confidential_issue_channel ProjectIntegrationMattermost#confidential_issue_channel}
        '''
        result = self._values.get("confidential_issue_channel")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def confidential_issues_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable notifications for confidential issues events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#confidential_issues_events ProjectIntegrationMattermost#confidential_issues_events}
        '''
        result = self._values.get("confidential_issues_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def confidential_note_channel(self) -> typing.Optional[builtins.str]:
        '''The name of the channel to receive confidential note events notifications.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#confidential_note_channel ProjectIntegrationMattermost#confidential_note_channel}
        '''
        result = self._values.get("confidential_note_channel")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def confidential_note_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable notifications for confidential note events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#confidential_note_events ProjectIntegrationMattermost#confidential_note_events}
        '''
        result = self._values.get("confidential_note_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#id ProjectIntegrationMattermost#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def issue_channel(self) -> typing.Optional[builtins.str]:
        '''The name of the channel to receive issue events notifications.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#issue_channel ProjectIntegrationMattermost#issue_channel}
        '''
        result = self._values.get("issue_channel")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def issues_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable notifications for issues events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#issues_events ProjectIntegrationMattermost#issues_events}
        '''
        result = self._values.get("issues_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def merge_request_channel(self) -> typing.Optional[builtins.str]:
        '''The name of the channel to receive merge request events notifications.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#merge_request_channel ProjectIntegrationMattermost#merge_request_channel}
        '''
        result = self._values.get("merge_request_channel")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def merge_requests_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable notifications for merge requests events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#merge_requests_events ProjectIntegrationMattermost#merge_requests_events}
        '''
        result = self._values.get("merge_requests_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def note_channel(self) -> typing.Optional[builtins.str]:
        '''The name of the channel to receive note events notifications.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#note_channel ProjectIntegrationMattermost#note_channel}
        '''
        result = self._values.get("note_channel")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def note_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable notifications for note events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#note_events ProjectIntegrationMattermost#note_events}
        '''
        result = self._values.get("note_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def notify_only_broken_pipelines(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Send notifications for broken pipelines.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#notify_only_broken_pipelines ProjectIntegrationMattermost#notify_only_broken_pipelines}
        '''
        result = self._values.get("notify_only_broken_pipelines")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def pipeline_channel(self) -> typing.Optional[builtins.str]:
        '''The name of the channel to receive pipeline events notifications.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#pipeline_channel ProjectIntegrationMattermost#pipeline_channel}
        '''
        result = self._values.get("pipeline_channel")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pipeline_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable notifications for pipeline events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#pipeline_events ProjectIntegrationMattermost#pipeline_events}
        '''
        result = self._values.get("pipeline_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def push_channel(self) -> typing.Optional[builtins.str]:
        '''The name of the channel to receive push events notifications.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#push_channel ProjectIntegrationMattermost#push_channel}
        '''
        result = self._values.get("push_channel")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def push_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable notifications for push events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#push_events ProjectIntegrationMattermost#push_events}
        '''
        result = self._values.get("push_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tag_push_channel(self) -> typing.Optional[builtins.str]:
        '''The name of the channel to receive tag push events notifications.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#tag_push_channel ProjectIntegrationMattermost#tag_push_channel}
        '''
        result = self._values.get("tag_push_channel")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_push_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable notifications for tag push events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#tag_push_events ProjectIntegrationMattermost#tag_push_events}
        '''
        result = self._values.get("tag_push_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Username to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#username ProjectIntegrationMattermost#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wiki_page_channel(self) -> typing.Optional[builtins.str]:
        '''The name of the channel to receive wiki page events notifications.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#wiki_page_channel ProjectIntegrationMattermost#wiki_page_channel}
        '''
        result = self._values.get("wiki_page_channel")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wiki_page_events(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable notifications for wiki page events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_mattermost#wiki_page_events ProjectIntegrationMattermost#wiki_page_events}
        '''
        result = self._values.get("wiki_page_events")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectIntegrationMattermostConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProjectIntegrationMattermost",
    "ProjectIntegrationMattermostConfig",
]

publication.publish()

def _typecheckingstub__ed190c66c0caf7b9a2bcfe9441c342f179c91e8715b16824316082b2f4e4bb86(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    project: builtins.str,
    webhook: builtins.str,
    branches_to_be_notified: typing.Optional[builtins.str] = None,
    confidential_issue_channel: typing.Optional[builtins.str] = None,
    confidential_issues_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    confidential_note_channel: typing.Optional[builtins.str] = None,
    confidential_note_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    issue_channel: typing.Optional[builtins.str] = None,
    issues_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    merge_request_channel: typing.Optional[builtins.str] = None,
    merge_requests_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    note_channel: typing.Optional[builtins.str] = None,
    note_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    notify_only_broken_pipelines: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    pipeline_channel: typing.Optional[builtins.str] = None,
    pipeline_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    push_channel: typing.Optional[builtins.str] = None,
    push_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tag_push_channel: typing.Optional[builtins.str] = None,
    tag_push_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    username: typing.Optional[builtins.str] = None,
    wiki_page_channel: typing.Optional[builtins.str] = None,
    wiki_page_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__52535f01074850e51c1d320a623b011a293f4e431076cc2dd36450eba52e2131(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bed4851453031cd1e5a4db52cd688fa5ee1cb22b73bb86fdd6f04280053562c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cadc7d8f4051655c3b8a75fe37b2e7f7e25037437d95f9936e3f5c5a746f5660(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3496ca82d97f7fdf7c0130ad5899bd06edfc3a965a33b35ef3f7616ecc1e43de(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6be55997ce98bab5bf8a73a7e890ae3d566d05438212fe4794d74daa6507e38f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaf8feba2f1b26327c4ab3ff5e76963e78a300acedbeab4b8f24704795ec8f62(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c741ce8031b6b3ca4145bf5a70e4b49fe97adab28134a226417d92b7603c837(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afe596738e9cc6643732a1376a2a6f6ebb3c769f0389b30d57f31264589a9a82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__437d5256191113da7cff4045e3ae7dad33f560630f62c2386fad27c9a416e524(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51a5f23739309e217c9d7878b629b63138ed0c1e1e63c624cd3f8f89896d27fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69e6aabefbf06dbb35b640fcbf0b882f1ecca8e642cef6a90c3a9d0921df0aac(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a43f2fffddc310dcc5a841ba7d49d45be781bc462b1617629ea54f97983a2bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98a92243389e7772c8644d4267448920fa5701187d1e2997a715210d09d34312(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d9abd8305b22ef1de70f45ca068f6de2babeb0035d52a63feaf812940d558e4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e560d133f9533de80cb038cdf7bf7254833de23c5edb04063079f2310d3dd63(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__259fe440fea09b59729ee630c8750c5ca990bf58ee1a97b3c443c6ff25830d5b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f589eedb3c4593cdc7e2687d1e135494057d1455d68ba9f82261f87f575f42c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e655df312a8162cac2ed729de2784e359c33bcfcc8e4b2233a8024b54c16210f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d12aef4929d70f546d8d3aee94dbb3a575b046677d8b1e9d765080bc47f2072a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46f654e96ebae0b0441b53ef2db027dbe5f2caa287ffd5c044c6bcf011adf173(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3671f650eaf95073ccd4ea353cd0e31267dfb619515dba078d6b1ab7dd86cf8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a0e618f5a23aa1c25a05e74de0ad164e0b94098e76075afd05dd658ec4a230b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e19764bd76474119998ffc3a2b974a0dba1ce611a35088c7c7a94c2d661aae22(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce5df303a9010550f536cec9385827759406dc5b0d7885ea665f0b85ccec454a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bc098192fd0684af18bb150b9f96ae6d6662a4e92d27d90e4f69c5ba075a6b5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__299323036042fe27bde22965dff5800679766187a552dc34ef2985ea1b537bcb(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    project: builtins.str,
    webhook: builtins.str,
    branches_to_be_notified: typing.Optional[builtins.str] = None,
    confidential_issue_channel: typing.Optional[builtins.str] = None,
    confidential_issues_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    confidential_note_channel: typing.Optional[builtins.str] = None,
    confidential_note_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    issue_channel: typing.Optional[builtins.str] = None,
    issues_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    merge_request_channel: typing.Optional[builtins.str] = None,
    merge_requests_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    note_channel: typing.Optional[builtins.str] = None,
    note_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    notify_only_broken_pipelines: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    pipeline_channel: typing.Optional[builtins.str] = None,
    pipeline_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    push_channel: typing.Optional[builtins.str] = None,
    push_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tag_push_channel: typing.Optional[builtins.str] = None,
    tag_push_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    username: typing.Optional[builtins.str] = None,
    wiki_page_channel: typing.Optional[builtins.str] = None,
    wiki_page_events: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
