r'''
# `gitlab_application_appearance`

Refer to the Terraform Registry for docs: [`gitlab_application_appearance`](https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance).
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


class ApplicationAppearance(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-gitlab.applicationAppearance.ApplicationAppearance",
):
    '''Represents a {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance gitlab_application_appearance}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        email_header_and_footer_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        footer_message: typing.Optional[builtins.str] = None,
        header_message: typing.Optional[builtins.str] = None,
        keep_settings_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        member_guidelines: typing.Optional[builtins.str] = None,
        message_background_color: typing.Optional[builtins.str] = None,
        message_font_color: typing.Optional[builtins.str] = None,
        new_project_guidelines: typing.Optional[builtins.str] = None,
        profile_image_guidelines: typing.Optional[builtins.str] = None,
        pwa_description: typing.Optional[builtins.str] = None,
        pwa_name: typing.Optional[builtins.str] = None,
        pwa_short_name: typing.Optional[builtins.str] = None,
        title: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance gitlab_application_appearance} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param description: Markdown text shown on the sign-in and sign-up page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#description ApplicationAppearance#description}
        :param email_header_and_footer_enabled: Add header and footer to all outgoing emails if enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#email_header_and_footer_enabled ApplicationAppearance#email_header_and_footer_enabled}
        :param footer_message: Message in the system footer bar. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#footer_message ApplicationAppearance#footer_message}
        :param header_message: Message in the system header bar. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#header_message ApplicationAppearance#header_message}
        :param keep_settings_on_destroy: Set to true if the appearance settings should not be reset to their pre-terraform defaults on destroy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#keep_settings_on_destroy ApplicationAppearance#keep_settings_on_destroy}
        :param member_guidelines: Markdown text shown on the group or project member page for users with permission to change members. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#member_guidelines ApplicationAppearance#member_guidelines}
        :param message_background_color: Background color for the system header or footer bar, in CSS hex notation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#message_background_color ApplicationAppearance#message_background_color}
        :param message_font_color: Font color for the system header or footer bar, in CSS hex notation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#message_font_color ApplicationAppearance#message_font_color}
        :param new_project_guidelines: Markdown text shown on the new project page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#new_project_guidelines ApplicationAppearance#new_project_guidelines}
        :param profile_image_guidelines: Markdown text shown on the profile page below the Public Avatar. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#profile_image_guidelines ApplicationAppearance#profile_image_guidelines}
        :param pwa_description: An explanation of what the Progressive Web App does. Used for the attribute ``description`` in ``manifest.json``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#pwa_description ApplicationAppearance#pwa_description}
        :param pwa_name: Full name of the Progressive Web App. Used for the attribute ``name`` in ``manifest.json``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#pwa_name ApplicationAppearance#pwa_name}
        :param pwa_short_name: Short name for Progressive Web App. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#pwa_short_name ApplicationAppearance#pwa_short_name}
        :param title: Application title on the sign-in and sign-up page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#title ApplicationAppearance#title}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75be706ee29d45cb52265b14ef68eddd8322d805d88e1c85b861d4a5fb042584)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ApplicationAppearanceConfig(
            description=description,
            email_header_and_footer_enabled=email_header_and_footer_enabled,
            footer_message=footer_message,
            header_message=header_message,
            keep_settings_on_destroy=keep_settings_on_destroy,
            member_guidelines=member_guidelines,
            message_background_color=message_background_color,
            message_font_color=message_font_color,
            new_project_guidelines=new_project_guidelines,
            profile_image_guidelines=profile_image_guidelines,
            pwa_description=pwa_description,
            pwa_name=pwa_name,
            pwa_short_name=pwa_short_name,
            title=title,
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
        '''Generates CDKTF code for importing a ApplicationAppearance resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ApplicationAppearance to import.
        :param import_from_id: The id of the existing ApplicationAppearance that should be imported. Refer to the {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ApplicationAppearance to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a42d295f5b82cbec3c50d2921a6f1d55be1b0cdf384f0f323d619a1bf9f45c76)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEmailHeaderAndFooterEnabled")
    def reset_email_header_and_footer_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailHeaderAndFooterEnabled", []))

    @jsii.member(jsii_name="resetFooterMessage")
    def reset_footer_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFooterMessage", []))

    @jsii.member(jsii_name="resetHeaderMessage")
    def reset_header_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaderMessage", []))

    @jsii.member(jsii_name="resetKeepSettingsOnDestroy")
    def reset_keep_settings_on_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepSettingsOnDestroy", []))

    @jsii.member(jsii_name="resetMemberGuidelines")
    def reset_member_guidelines(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemberGuidelines", []))

    @jsii.member(jsii_name="resetMessageBackgroundColor")
    def reset_message_background_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageBackgroundColor", []))

    @jsii.member(jsii_name="resetMessageFontColor")
    def reset_message_font_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageFontColor", []))

    @jsii.member(jsii_name="resetNewProjectGuidelines")
    def reset_new_project_guidelines(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewProjectGuidelines", []))

    @jsii.member(jsii_name="resetProfileImageGuidelines")
    def reset_profile_image_guidelines(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProfileImageGuidelines", []))

    @jsii.member(jsii_name="resetPwaDescription")
    def reset_pwa_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPwaDescription", []))

    @jsii.member(jsii_name="resetPwaName")
    def reset_pwa_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPwaName", []))

    @jsii.member(jsii_name="resetPwaShortName")
    def reset_pwa_short_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPwaShortName", []))

    @jsii.member(jsii_name="resetTitle")
    def reset_title(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTitle", []))

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
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="emailHeaderAndFooterEnabledInput")
    def email_header_and_footer_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "emailHeaderAndFooterEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="footerMessageInput")
    def footer_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "footerMessageInput"))

    @builtins.property
    @jsii.member(jsii_name="headerMessageInput")
    def header_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headerMessageInput"))

    @builtins.property
    @jsii.member(jsii_name="keepSettingsOnDestroyInput")
    def keep_settings_on_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "keepSettingsOnDestroyInput"))

    @builtins.property
    @jsii.member(jsii_name="memberGuidelinesInput")
    def member_guidelines_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "memberGuidelinesInput"))

    @builtins.property
    @jsii.member(jsii_name="messageBackgroundColorInput")
    def message_background_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageBackgroundColorInput"))

    @builtins.property
    @jsii.member(jsii_name="messageFontColorInput")
    def message_font_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageFontColorInput"))

    @builtins.property
    @jsii.member(jsii_name="newProjectGuidelinesInput")
    def new_project_guidelines_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "newProjectGuidelinesInput"))

    @builtins.property
    @jsii.member(jsii_name="profileImageGuidelinesInput")
    def profile_image_guidelines_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profileImageGuidelinesInput"))

    @builtins.property
    @jsii.member(jsii_name="pwaDescriptionInput")
    def pwa_description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pwaDescriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="pwaNameInput")
    def pwa_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pwaNameInput"))

    @builtins.property
    @jsii.member(jsii_name="pwaShortNameInput")
    def pwa_short_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pwaShortNameInput"))

    @builtins.property
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f86658296a42402cdb981e6a3a7870df570e182c2906a3b9ad0cd80c4fa098ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailHeaderAndFooterEnabled")
    def email_header_and_footer_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "emailHeaderAndFooterEnabled"))

    @email_header_and_footer_enabled.setter
    def email_header_and_footer_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aecd7603211ede0d0109c954f48a22e7115451dbe1be8f6345c4313a588e5339)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailHeaderAndFooterEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="footerMessage")
    def footer_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "footerMessage"))

    @footer_message.setter
    def footer_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ba1068a98d2f6fc9961a2cb831a7d07861a43a31ee0481cf77cbe4900f87a44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "footerMessage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headerMessage")
    def header_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerMessage"))

    @header_message.setter
    def header_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2469eac5a1c4fa8ad6ec3e72e11e794be60153ad51b9c6f3681f0b0bbd5c2c47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headerMessage", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__39b57277b3bf82924ce9f3cc23ba265ace95cf2c175003a520450c7e39f53abb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keepSettingsOnDestroy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memberGuidelines")
    def member_guidelines(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "memberGuidelines"))

    @member_guidelines.setter
    def member_guidelines(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__328b7fa04d135049e9944d9e44cb7b8c4a57adbec36ae72b9bd588ebe0462554)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memberGuidelines", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="messageBackgroundColor")
    def message_background_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageBackgroundColor"))

    @message_background_color.setter
    def message_background_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a2baaf636f44d8bbcae20fa4353ca92de485f9753461ccdf3c4849b50f4ec46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "messageBackgroundColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="messageFontColor")
    def message_font_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageFontColor"))

    @message_font_color.setter
    def message_font_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae7833b4de8d3afffce971be05a27dae38c8b17cc41582db289919a1d887c9bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "messageFontColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="newProjectGuidelines")
    def new_project_guidelines(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "newProjectGuidelines"))

    @new_project_guidelines.setter
    def new_project_guidelines(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc4a5fd123a3dc5a673c31621471c840a3d0f76912eafe0a5cabc008e21b6706)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newProjectGuidelines", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="profileImageGuidelines")
    def profile_image_guidelines(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profileImageGuidelines"))

    @profile_image_guidelines.setter
    def profile_image_guidelines(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8efd2b0a0ef33958021bda1010c56138ae05a7e32cc80eec6c1ddd0123e724b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "profileImageGuidelines", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pwaDescription")
    def pwa_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pwaDescription"))

    @pwa_description.setter
    def pwa_description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0c2c32566b636d6c0d150cb607b1c4bddacee21cdc6811ad9d889393fcb000f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pwaDescription", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pwaName")
    def pwa_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pwaName"))

    @pwa_name.setter
    def pwa_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90f11503fd7df848f092ff4922d75bac3179eba313224df1dabe28ea2e092b71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pwaName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pwaShortName")
    def pwa_short_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pwaShortName"))

    @pwa_short_name.setter
    def pwa_short_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e07ad920ebe90bdbfb712bf1dd42625b796420e45a3a5f0179a2936cbfa4875)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pwaShortName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95cb5ef44d1c6b82eebd9fea94abcd1c8806be8d56d241fc3d8ed0d3192cf7ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "title", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-gitlab.applicationAppearance.ApplicationAppearanceConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "description": "description",
        "email_header_and_footer_enabled": "emailHeaderAndFooterEnabled",
        "footer_message": "footerMessage",
        "header_message": "headerMessage",
        "keep_settings_on_destroy": "keepSettingsOnDestroy",
        "member_guidelines": "memberGuidelines",
        "message_background_color": "messageBackgroundColor",
        "message_font_color": "messageFontColor",
        "new_project_guidelines": "newProjectGuidelines",
        "profile_image_guidelines": "profileImageGuidelines",
        "pwa_description": "pwaDescription",
        "pwa_name": "pwaName",
        "pwa_short_name": "pwaShortName",
        "title": "title",
    },
)
class ApplicationAppearanceConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        description: typing.Optional[builtins.str] = None,
        email_header_and_footer_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        footer_message: typing.Optional[builtins.str] = None,
        header_message: typing.Optional[builtins.str] = None,
        keep_settings_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        member_guidelines: typing.Optional[builtins.str] = None,
        message_background_color: typing.Optional[builtins.str] = None,
        message_font_color: typing.Optional[builtins.str] = None,
        new_project_guidelines: typing.Optional[builtins.str] = None,
        profile_image_guidelines: typing.Optional[builtins.str] = None,
        pwa_description: typing.Optional[builtins.str] = None,
        pwa_name: typing.Optional[builtins.str] = None,
        pwa_short_name: typing.Optional[builtins.str] = None,
        title: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param description: Markdown text shown on the sign-in and sign-up page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#description ApplicationAppearance#description}
        :param email_header_and_footer_enabled: Add header and footer to all outgoing emails if enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#email_header_and_footer_enabled ApplicationAppearance#email_header_and_footer_enabled}
        :param footer_message: Message in the system footer bar. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#footer_message ApplicationAppearance#footer_message}
        :param header_message: Message in the system header bar. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#header_message ApplicationAppearance#header_message}
        :param keep_settings_on_destroy: Set to true if the appearance settings should not be reset to their pre-terraform defaults on destroy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#keep_settings_on_destroy ApplicationAppearance#keep_settings_on_destroy}
        :param member_guidelines: Markdown text shown on the group or project member page for users with permission to change members. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#member_guidelines ApplicationAppearance#member_guidelines}
        :param message_background_color: Background color for the system header or footer bar, in CSS hex notation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#message_background_color ApplicationAppearance#message_background_color}
        :param message_font_color: Font color for the system header or footer bar, in CSS hex notation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#message_font_color ApplicationAppearance#message_font_color}
        :param new_project_guidelines: Markdown text shown on the new project page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#new_project_guidelines ApplicationAppearance#new_project_guidelines}
        :param profile_image_guidelines: Markdown text shown on the profile page below the Public Avatar. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#profile_image_guidelines ApplicationAppearance#profile_image_guidelines}
        :param pwa_description: An explanation of what the Progressive Web App does. Used for the attribute ``description`` in ``manifest.json``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#pwa_description ApplicationAppearance#pwa_description}
        :param pwa_name: Full name of the Progressive Web App. Used for the attribute ``name`` in ``manifest.json``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#pwa_name ApplicationAppearance#pwa_name}
        :param pwa_short_name: Short name for Progressive Web App. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#pwa_short_name ApplicationAppearance#pwa_short_name}
        :param title: Application title on the sign-in and sign-up page. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#title ApplicationAppearance#title}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4266c51baf51ff6a1c70291f85e0cff02cd796f0b4ecf71ec9c2ea711232e826)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument email_header_and_footer_enabled", value=email_header_and_footer_enabled, expected_type=type_hints["email_header_and_footer_enabled"])
            check_type(argname="argument footer_message", value=footer_message, expected_type=type_hints["footer_message"])
            check_type(argname="argument header_message", value=header_message, expected_type=type_hints["header_message"])
            check_type(argname="argument keep_settings_on_destroy", value=keep_settings_on_destroy, expected_type=type_hints["keep_settings_on_destroy"])
            check_type(argname="argument member_guidelines", value=member_guidelines, expected_type=type_hints["member_guidelines"])
            check_type(argname="argument message_background_color", value=message_background_color, expected_type=type_hints["message_background_color"])
            check_type(argname="argument message_font_color", value=message_font_color, expected_type=type_hints["message_font_color"])
            check_type(argname="argument new_project_guidelines", value=new_project_guidelines, expected_type=type_hints["new_project_guidelines"])
            check_type(argname="argument profile_image_guidelines", value=profile_image_guidelines, expected_type=type_hints["profile_image_guidelines"])
            check_type(argname="argument pwa_description", value=pwa_description, expected_type=type_hints["pwa_description"])
            check_type(argname="argument pwa_name", value=pwa_name, expected_type=type_hints["pwa_name"])
            check_type(argname="argument pwa_short_name", value=pwa_short_name, expected_type=type_hints["pwa_short_name"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
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
        if description is not None:
            self._values["description"] = description
        if email_header_and_footer_enabled is not None:
            self._values["email_header_and_footer_enabled"] = email_header_and_footer_enabled
        if footer_message is not None:
            self._values["footer_message"] = footer_message
        if header_message is not None:
            self._values["header_message"] = header_message
        if keep_settings_on_destroy is not None:
            self._values["keep_settings_on_destroy"] = keep_settings_on_destroy
        if member_guidelines is not None:
            self._values["member_guidelines"] = member_guidelines
        if message_background_color is not None:
            self._values["message_background_color"] = message_background_color
        if message_font_color is not None:
            self._values["message_font_color"] = message_font_color
        if new_project_guidelines is not None:
            self._values["new_project_guidelines"] = new_project_guidelines
        if profile_image_guidelines is not None:
            self._values["profile_image_guidelines"] = profile_image_guidelines
        if pwa_description is not None:
            self._values["pwa_description"] = pwa_description
        if pwa_name is not None:
            self._values["pwa_name"] = pwa_name
        if pwa_short_name is not None:
            self._values["pwa_short_name"] = pwa_short_name
        if title is not None:
            self._values["title"] = title

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
    def description(self) -> typing.Optional[builtins.str]:
        '''Markdown text shown on the sign-in and sign-up page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#description ApplicationAppearance#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_header_and_footer_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Add header and footer to all outgoing emails if enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#email_header_and_footer_enabled ApplicationAppearance#email_header_and_footer_enabled}
        '''
        result = self._values.get("email_header_and_footer_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def footer_message(self) -> typing.Optional[builtins.str]:
        '''Message in the system footer bar.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#footer_message ApplicationAppearance#footer_message}
        '''
        result = self._values.get("footer_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def header_message(self) -> typing.Optional[builtins.str]:
        '''Message in the system header bar.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#header_message ApplicationAppearance#header_message}
        '''
        result = self._values.get("header_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keep_settings_on_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true if the appearance settings should not be reset to their pre-terraform defaults on destroy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#keep_settings_on_destroy ApplicationAppearance#keep_settings_on_destroy}
        '''
        result = self._values.get("keep_settings_on_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def member_guidelines(self) -> typing.Optional[builtins.str]:
        '''Markdown text shown on the group or project member page for users with permission to change members.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#member_guidelines ApplicationAppearance#member_guidelines}
        '''
        result = self._values.get("member_guidelines")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_background_color(self) -> typing.Optional[builtins.str]:
        '''Background color for the system header or footer bar, in CSS hex notation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#message_background_color ApplicationAppearance#message_background_color}
        '''
        result = self._values.get("message_background_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_font_color(self) -> typing.Optional[builtins.str]:
        '''Font color for the system header or footer bar, in CSS hex notation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#message_font_color ApplicationAppearance#message_font_color}
        '''
        result = self._values.get("message_font_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def new_project_guidelines(self) -> typing.Optional[builtins.str]:
        '''Markdown text shown on the new project page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#new_project_guidelines ApplicationAppearance#new_project_guidelines}
        '''
        result = self._values.get("new_project_guidelines")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def profile_image_guidelines(self) -> typing.Optional[builtins.str]:
        '''Markdown text shown on the profile page below the Public Avatar.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#profile_image_guidelines ApplicationAppearance#profile_image_guidelines}
        '''
        result = self._values.get("profile_image_guidelines")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pwa_description(self) -> typing.Optional[builtins.str]:
        '''An explanation of what the Progressive Web App does. Used for the attribute ``description`` in ``manifest.json``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#pwa_description ApplicationAppearance#pwa_description}
        '''
        result = self._values.get("pwa_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pwa_name(self) -> typing.Optional[builtins.str]:
        '''Full name of the Progressive Web App. Used for the attribute ``name`` in ``manifest.json``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#pwa_name ApplicationAppearance#pwa_name}
        '''
        result = self._values.get("pwa_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pwa_short_name(self) -> typing.Optional[builtins.str]:
        '''Short name for Progressive Web App.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#pwa_short_name ApplicationAppearance#pwa_short_name}
        '''
        result = self._values.get("pwa_short_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def title(self) -> typing.Optional[builtins.str]:
        '''Application title on the sign-in and sign-up page.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/gitlabhq/gitlab/18.5.0/docs/resources/application_appearance#title ApplicationAppearance#title}
        '''
        result = self._values.get("title")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationAppearanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApplicationAppearance",
    "ApplicationAppearanceConfig",
]

publication.publish()

def _typecheckingstub__75be706ee29d45cb52265b14ef68eddd8322d805d88e1c85b861d4a5fb042584(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    email_header_and_footer_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    footer_message: typing.Optional[builtins.str] = None,
    header_message: typing.Optional[builtins.str] = None,
    keep_settings_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    member_guidelines: typing.Optional[builtins.str] = None,
    message_background_color: typing.Optional[builtins.str] = None,
    message_font_color: typing.Optional[builtins.str] = None,
    new_project_guidelines: typing.Optional[builtins.str] = None,
    profile_image_guidelines: typing.Optional[builtins.str] = None,
    pwa_description: typing.Optional[builtins.str] = None,
    pwa_name: typing.Optional[builtins.str] = None,
    pwa_short_name: typing.Optional[builtins.str] = None,
    title: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__a42d295f5b82cbec3c50d2921a6f1d55be1b0cdf384f0f323d619a1bf9f45c76(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f86658296a42402cdb981e6a3a7870df570e182c2906a3b9ad0cd80c4fa098ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aecd7603211ede0d0109c954f48a22e7115451dbe1be8f6345c4313a588e5339(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ba1068a98d2f6fc9961a2cb831a7d07861a43a31ee0481cf77cbe4900f87a44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2469eac5a1c4fa8ad6ec3e72e11e794be60153ad51b9c6f3681f0b0bbd5c2c47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39b57277b3bf82924ce9f3cc23ba265ace95cf2c175003a520450c7e39f53abb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__328b7fa04d135049e9944d9e44cb7b8c4a57adbec36ae72b9bd588ebe0462554(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a2baaf636f44d8bbcae20fa4353ca92de485f9753461ccdf3c4849b50f4ec46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae7833b4de8d3afffce971be05a27dae38c8b17cc41582db289919a1d887c9bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc4a5fd123a3dc5a673c31621471c840a3d0f76912eafe0a5cabc008e21b6706(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8efd2b0a0ef33958021bda1010c56138ae05a7e32cc80eec6c1ddd0123e724b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0c2c32566b636d6c0d150cb607b1c4bddacee21cdc6811ad9d889393fcb000f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90f11503fd7df848f092ff4922d75bac3179eba313224df1dabe28ea2e092b71(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e07ad920ebe90bdbfb712bf1dd42625b796420e45a3a5f0179a2936cbfa4875(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95cb5ef44d1c6b82eebd9fea94abcd1c8806be8d56d241fc3d8ed0d3192cf7ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4266c51baf51ff6a1c70291f85e0cff02cd796f0b4ecf71ec9c2ea711232e826(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    email_header_and_footer_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    footer_message: typing.Optional[builtins.str] = None,
    header_message: typing.Optional[builtins.str] = None,
    keep_settings_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    member_guidelines: typing.Optional[builtins.str] = None,
    message_background_color: typing.Optional[builtins.str] = None,
    message_font_color: typing.Optional[builtins.str] = None,
    new_project_guidelines: typing.Optional[builtins.str] = None,
    profile_image_guidelines: typing.Optional[builtins.str] = None,
    pwa_description: typing.Optional[builtins.str] = None,
    pwa_name: typing.Optional[builtins.str] = None,
    pwa_short_name: typing.Optional[builtins.str] = None,
    title: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
