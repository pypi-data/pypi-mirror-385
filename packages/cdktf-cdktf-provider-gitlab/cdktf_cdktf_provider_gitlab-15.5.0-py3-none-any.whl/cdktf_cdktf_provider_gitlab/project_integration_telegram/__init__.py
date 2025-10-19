r'''
# `gitlab_project_integration_telegram`

Refer to the Terraform Registry for docs: [`gitlab_project_integration_telegram`](https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram).
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


class ProjectIntegrationTelegram(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.projectIntegrationTelegram.ProjectIntegrationTelegram",
):
    '''Represents a {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram gitlab_project_integration_telegram}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        confidential_issues_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        confidential_note_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        issues_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        merge_requests_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        note_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        pipeline_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        project: builtins.str,
        push_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        room: builtins.str,
        tag_push_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        token: builtins.str,
        wiki_page_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        branches_to_be_notified: typing.Optional[builtins.str] = None,
        notify_only_broken_pipelines: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram gitlab_project_integration_telegram} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param confidential_issues_events: Enable notifications for confidential issues events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#confidential_issues_events ProjectIntegrationTelegram#confidential_issues_events}
        :param confidential_note_events: Enable notifications for confidential note events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#confidential_note_events ProjectIntegrationTelegram#confidential_note_events}
        :param issues_events: Enable notifications for issues events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#issues_events ProjectIntegrationTelegram#issues_events}
        :param merge_requests_events: Enable notifications for merge requests events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#merge_requests_events ProjectIntegrationTelegram#merge_requests_events}
        :param note_events: Enable notifications for note events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#note_events ProjectIntegrationTelegram#note_events}
        :param pipeline_events: Enable notifications for pipeline events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#pipeline_events ProjectIntegrationTelegram#pipeline_events}
        :param project: The ID or full path of the project to integrate with Telegram. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#project ProjectIntegrationTelegram#project}
        :param push_events: Enable notifications for push events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#push_events ProjectIntegrationTelegram#push_events}
        :param room: Unique identifier for the target chat or the username of the target channel (in the format ``@channelusername``). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#room ProjectIntegrationTelegram#room}
        :param tag_push_events: Enable notifications for tag push events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#tag_push_events ProjectIntegrationTelegram#tag_push_events}
        :param token: The Telegram bot token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#token ProjectIntegrationTelegram#token}
        :param wiki_page_events: Enable notifications for wiki page events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#wiki_page_events ProjectIntegrationTelegram#wiki_page_events}
        :param branches_to_be_notified: Branches to send notifications for. Valid options are ``all``, ``default``, ``protected``, ``default_and_protected``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#branches_to_be_notified ProjectIntegrationTelegram#branches_to_be_notified}
        :param notify_only_broken_pipelines: Send notifications for broken pipelines. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#notify_only_broken_pipelines ProjectIntegrationTelegram#notify_only_broken_pipelines}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ade7356749ea479a356c791d36cb1efae8f94fe5cd75bda8c68302d04ae6f7ed)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ProjectIntegrationTelegramConfig(
            confidential_issues_events=confidential_issues_events,
            confidential_note_events=confidential_note_events,
            issues_events=issues_events,
            merge_requests_events=merge_requests_events,
            note_events=note_events,
            pipeline_events=pipeline_events,
            project=project,
            push_events=push_events,
            room=room,
            tag_push_events=tag_push_events,
            token=token,
            wiki_page_events=wiki_page_events,
            branches_to_be_notified=branches_to_be_notified,
            notify_only_broken_pipelines=notify_only_broken_pipelines,
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
        '''Generates CDKTF code for importing a ProjectIntegrationTelegram resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProjectIntegrationTelegram to import.
        :param import_from_id: The id of the existing ProjectIntegrationTelegram that should be imported. Refer to the {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProjectIntegrationTelegram to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f8e5189052dde8f59f39953c7cbb3d2f05acd82132ce4b9027b068742017321)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBranchesToBeNotified")
    def reset_branches_to_be_notified(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBranchesToBeNotified", []))

    @jsii.member(jsii_name="resetNotifyOnlyBrokenPipelines")
    def reset_notify_only_broken_pipelines(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotifyOnlyBrokenPipelines", []))

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
    @jsii.member(jsii_name="branchesToBeNotifiedInput")
    def branches_to_be_notified_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "branchesToBeNotifiedInput"))

    @builtins.property
    @jsii.member(jsii_name="confidentialIssuesEventsInput")
    def confidential_issues_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "confidentialIssuesEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="confidentialNoteEventsInput")
    def confidential_note_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "confidentialNoteEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="issuesEventsInput")
    def issues_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "issuesEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="mergeRequestsEventsInput")
    def merge_requests_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "mergeRequestsEventsInput"))

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
    @jsii.member(jsii_name="pushEventsInput")
    def push_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pushEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="roomInput")
    def room_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roomInput"))

    @builtins.property
    @jsii.member(jsii_name="tagPushEventsInput")
    def tag_push_events_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tagPushEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__ad1bb2f3b8fbfa667a943c34b213b32cd24a2e54ea584f553e8af5e0e3e9c68c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "branchesToBeNotified", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__731498b6ece2434330998f05282700e8c3b377b8da1b0a7da64bf521284e6c7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confidentialIssuesEvents", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__55a70d8118a544a967c7cf535295e733bbac0ff543ef1fbb480caee209c7fe45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confidentialNoteEvents", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__3351c8976fc5579e25d4bca9a8eb9ce48cdb33b9ed0f79967839b91bfca699ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuesEvents", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__6e6e9bf5b972626b53ceea509f24aa30f1700fedf892f2edbd0a9dd036c1bdba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mergeRequestsEvents", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__8700c5b01093d036069fe2b9ccd01496d9275076fbb65043725bab0f508157d1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d210de3e42fffe5ed9a5a185e3f727b90ab9dede5ffc5b524c8a973c07c7a10b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notifyOnlyBrokenPipelines", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__754d94d80f111dde9bbca654a111638a9338f3897ae3067df8fb6c41624907fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pipelineEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "project"))

    @project.setter
    def project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d5c81600254b13671f13364ee601b03632f09eb022d7774c285c8a09afd4d48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "project", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__8c87d98cfc2c04b57948450d81eea12bb29effa3bbe4c3883cd3eac303e8b28a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pushEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="room")
    def room(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "room"))

    @room.setter
    def room(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cd56d8f2214c2975647b71103893ae39358c7ea25c7c3675e9e8ef8ceecf020)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "room", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__78b2983c266008d0f169e83728d303f38730935be19cc1d04e12b819ab96f8ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagPushEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "token"))

    @token.setter
    def token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7bfdcb816d223021329ebcbdb2550ce61a28216e707e0cf85ad2c9454c79a76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__0b0e06352352c47578420b68291958832344a870e06dcafdeaeb458bc473112e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wikiPageEvents", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.projectIntegrationTelegram.ProjectIntegrationTelegramConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "confidential_issues_events": "confidentialIssuesEvents",
        "confidential_note_events": "confidentialNoteEvents",
        "issues_events": "issuesEvents",
        "merge_requests_events": "mergeRequestsEvents",
        "note_events": "noteEvents",
        "pipeline_events": "pipelineEvents",
        "project": "project",
        "push_events": "pushEvents",
        "room": "room",
        "tag_push_events": "tagPushEvents",
        "token": "token",
        "wiki_page_events": "wikiPageEvents",
        "branches_to_be_notified": "branchesToBeNotified",
        "notify_only_broken_pipelines": "notifyOnlyBrokenPipelines",
    },
)
class ProjectIntegrationTelegramConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        confidential_issues_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        confidential_note_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        issues_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        merge_requests_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        note_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        pipeline_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        project: builtins.str,
        push_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        room: builtins.str,
        tag_push_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        token: builtins.str,
        wiki_page_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        branches_to_be_notified: typing.Optional[builtins.str] = None,
        notify_only_broken_pipelines: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param confidential_issues_events: Enable notifications for confidential issues events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#confidential_issues_events ProjectIntegrationTelegram#confidential_issues_events}
        :param confidential_note_events: Enable notifications for confidential note events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#confidential_note_events ProjectIntegrationTelegram#confidential_note_events}
        :param issues_events: Enable notifications for issues events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#issues_events ProjectIntegrationTelegram#issues_events}
        :param merge_requests_events: Enable notifications for merge requests events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#merge_requests_events ProjectIntegrationTelegram#merge_requests_events}
        :param note_events: Enable notifications for note events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#note_events ProjectIntegrationTelegram#note_events}
        :param pipeline_events: Enable notifications for pipeline events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#pipeline_events ProjectIntegrationTelegram#pipeline_events}
        :param project: The ID or full path of the project to integrate with Telegram. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#project ProjectIntegrationTelegram#project}
        :param push_events: Enable notifications for push events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#push_events ProjectIntegrationTelegram#push_events}
        :param room: Unique identifier for the target chat or the username of the target channel (in the format ``@channelusername``). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#room ProjectIntegrationTelegram#room}
        :param tag_push_events: Enable notifications for tag push events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#tag_push_events ProjectIntegrationTelegram#tag_push_events}
        :param token: The Telegram bot token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#token ProjectIntegrationTelegram#token}
        :param wiki_page_events: Enable notifications for wiki page events. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#wiki_page_events ProjectIntegrationTelegram#wiki_page_events}
        :param branches_to_be_notified: Branches to send notifications for. Valid options are ``all``, ``default``, ``protected``, ``default_and_protected``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#branches_to_be_notified ProjectIntegrationTelegram#branches_to_be_notified}
        :param notify_only_broken_pipelines: Send notifications for broken pipelines. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#notify_only_broken_pipelines ProjectIntegrationTelegram#notify_only_broken_pipelines}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__011a50abd07b371912b66e95c4da2ad3b77b1e87ad4ba6b0115d5ca93216df22)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument confidential_issues_events", value=confidential_issues_events, expected_type=type_hints["confidential_issues_events"])
            check_type(argname="argument confidential_note_events", value=confidential_note_events, expected_type=type_hints["confidential_note_events"])
            check_type(argname="argument issues_events", value=issues_events, expected_type=type_hints["issues_events"])
            check_type(argname="argument merge_requests_events", value=merge_requests_events, expected_type=type_hints["merge_requests_events"])
            check_type(argname="argument note_events", value=note_events, expected_type=type_hints["note_events"])
            check_type(argname="argument pipeline_events", value=pipeline_events, expected_type=type_hints["pipeline_events"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument push_events", value=push_events, expected_type=type_hints["push_events"])
            check_type(argname="argument room", value=room, expected_type=type_hints["room"])
            check_type(argname="argument tag_push_events", value=tag_push_events, expected_type=type_hints["tag_push_events"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
            check_type(argname="argument wiki_page_events", value=wiki_page_events, expected_type=type_hints["wiki_page_events"])
            check_type(argname="argument branches_to_be_notified", value=branches_to_be_notified, expected_type=type_hints["branches_to_be_notified"])
            check_type(argname="argument notify_only_broken_pipelines", value=notify_only_broken_pipelines, expected_type=type_hints["notify_only_broken_pipelines"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "confidential_issues_events": confidential_issues_events,
            "confidential_note_events": confidential_note_events,
            "issues_events": issues_events,
            "merge_requests_events": merge_requests_events,
            "note_events": note_events,
            "pipeline_events": pipeline_events,
            "project": project,
            "push_events": push_events,
            "room": room,
            "tag_push_events": tag_push_events,
            "token": token,
            "wiki_page_events": wiki_page_events,
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
        if notify_only_broken_pipelines is not None:
            self._values["notify_only_broken_pipelines"] = notify_only_broken_pipelines

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
    def confidential_issues_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Enable notifications for confidential issues events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#confidential_issues_events ProjectIntegrationTelegram#confidential_issues_events}
        '''
        result = self._values.get("confidential_issues_events")
        assert result is not None, "Required property 'confidential_issues_events' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def confidential_note_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Enable notifications for confidential note events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#confidential_note_events ProjectIntegrationTelegram#confidential_note_events}
        '''
        result = self._values.get("confidential_note_events")
        assert result is not None, "Required property 'confidential_note_events' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def issues_events(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Enable notifications for issues events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#issues_events ProjectIntegrationTelegram#issues_events}
        '''
        result = self._values.get("issues_events")
        assert result is not None, "Required property 'issues_events' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def merge_requests_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Enable notifications for merge requests events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#merge_requests_events ProjectIntegrationTelegram#merge_requests_events}
        '''
        result = self._values.get("merge_requests_events")
        assert result is not None, "Required property 'merge_requests_events' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def note_events(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Enable notifications for note events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#note_events ProjectIntegrationTelegram#note_events}
        '''
        result = self._values.get("note_events")
        assert result is not None, "Required property 'note_events' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def pipeline_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Enable notifications for pipeline events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#pipeline_events ProjectIntegrationTelegram#pipeline_events}
        '''
        result = self._values.get("pipeline_events")
        assert result is not None, "Required property 'pipeline_events' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def project(self) -> builtins.str:
        '''The ID or full path of the project to integrate with Telegram.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#project ProjectIntegrationTelegram#project}
        '''
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def push_events(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Enable notifications for push events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#push_events ProjectIntegrationTelegram#push_events}
        '''
        result = self._values.get("push_events")
        assert result is not None, "Required property 'push_events' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def room(self) -> builtins.str:
        '''Unique identifier for the target chat or the username of the target channel (in the format ``@channelusername``).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#room ProjectIntegrationTelegram#room}
        '''
        result = self._values.get("room")
        assert result is not None, "Required property 'room' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tag_push_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Enable notifications for tag push events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#tag_push_events ProjectIntegrationTelegram#tag_push_events}
        '''
        result = self._values.get("tag_push_events")
        assert result is not None, "Required property 'tag_push_events' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def token(self) -> builtins.str:
        '''The Telegram bot token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#token ProjectIntegrationTelegram#token}
        '''
        result = self._values.get("token")
        assert result is not None, "Required property 'token' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def wiki_page_events(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Enable notifications for wiki page events.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#wiki_page_events ProjectIntegrationTelegram#wiki_page_events}
        '''
        result = self._values.get("wiki_page_events")
        assert result is not None, "Required property 'wiki_page_events' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def branches_to_be_notified(self) -> typing.Optional[builtins.str]:
        '''Branches to send notifications for. Valid options are ``all``, ``default``, ``protected``, ``default_and_protected``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#branches_to_be_notified ProjectIntegrationTelegram#branches_to_be_notified}
        '''
        result = self._values.get("branches_to_be_notified")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notify_only_broken_pipelines(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Send notifications for broken pipelines.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/project_integration_telegram#notify_only_broken_pipelines ProjectIntegrationTelegram#notify_only_broken_pipelines}
        '''
        result = self._values.get("notify_only_broken_pipelines")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectIntegrationTelegramConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProjectIntegrationTelegram",
    "ProjectIntegrationTelegramConfig",
]

publication.publish()

def _typecheckingstub__ade7356749ea479a356c791d36cb1efae8f94fe5cd75bda8c68302d04ae6f7ed(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    confidential_issues_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    confidential_note_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    issues_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    merge_requests_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    note_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    pipeline_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    project: builtins.str,
    push_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    room: builtins.str,
    tag_push_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    token: builtins.str,
    wiki_page_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    branches_to_be_notified: typing.Optional[builtins.str] = None,
    notify_only_broken_pipelines: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__7f8e5189052dde8f59f39953c7cbb3d2f05acd82132ce4b9027b068742017321(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad1bb2f3b8fbfa667a943c34b213b32cd24a2e54ea584f553e8af5e0e3e9c68c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__731498b6ece2434330998f05282700e8c3b377b8da1b0a7da64bf521284e6c7e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55a70d8118a544a967c7cf535295e733bbac0ff543ef1fbb480caee209c7fe45(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3351c8976fc5579e25d4bca9a8eb9ce48cdb33b9ed0f79967839b91bfca699ea(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e6e9bf5b972626b53ceea509f24aa30f1700fedf892f2edbd0a9dd036c1bdba(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8700c5b01093d036069fe2b9ccd01496d9275076fbb65043725bab0f508157d1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d210de3e42fffe5ed9a5a185e3f727b90ab9dede5ffc5b524c8a973c07c7a10b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__754d94d80f111dde9bbca654a111638a9338f3897ae3067df8fb6c41624907fe(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d5c81600254b13671f13364ee601b03632f09eb022d7774c285c8a09afd4d48(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c87d98cfc2c04b57948450d81eea12bb29effa3bbe4c3883cd3eac303e8b28a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cd56d8f2214c2975647b71103893ae39358c7ea25c7c3675e9e8ef8ceecf020(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78b2983c266008d0f169e83728d303f38730935be19cc1d04e12b819ab96f8ef(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7bfdcb816d223021329ebcbdb2550ce61a28216e707e0cf85ad2c9454c79a76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b0e06352352c47578420b68291958832344a870e06dcafdeaeb458bc473112e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__011a50abd07b371912b66e95c4da2ad3b77b1e87ad4ba6b0115d5ca93216df22(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    confidential_issues_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    confidential_note_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    issues_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    merge_requests_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    note_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    pipeline_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    project: builtins.str,
    push_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    room: builtins.str,
    tag_push_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    token: builtins.str,
    wiki_page_events: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    branches_to_be_notified: typing.Optional[builtins.str] = None,
    notify_only_broken_pipelines: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
