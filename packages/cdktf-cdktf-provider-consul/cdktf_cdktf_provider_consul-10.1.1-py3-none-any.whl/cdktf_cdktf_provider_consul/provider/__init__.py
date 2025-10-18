r'''
# `provider`

Refer to the Terraform Registry for docs: [`consul`](https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs).
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


class ConsulProvider(
    _cdktf_9a9027ec.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.provider.ConsulProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs consul}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        address: typing.Optional[builtins.str] = None,
        alias: typing.Optional[builtins.str] = None,
        auth_jwt: typing.Optional[typing.Union["ConsulProviderAuthJwt", typing.Dict[builtins.str, typing.Any]]] = None,
        ca_file: typing.Optional[builtins.str] = None,
        ca_path: typing.Optional[builtins.str] = None,
        ca_pem: typing.Optional[builtins.str] = None,
        cert_file: typing.Optional[builtins.str] = None,
        cert_pem: typing.Optional[builtins.str] = None,
        datacenter: typing.Optional[builtins.str] = None,
        header: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConsulProviderHeader", typing.Dict[builtins.str, typing.Any]]]]] = None,
        http_auth: typing.Optional[builtins.str] = None,
        insecure_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        key_file: typing.Optional[builtins.str] = None,
        key_pem: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        scheme: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs consul} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param address: The HTTP(S) API address of the agent to use. Defaults to "127.0.0.1:8500". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#address ConsulProvider#address}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#alias ConsulProvider#alias}
        :param auth_jwt: auth_jwt block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#auth_jwt ConsulProvider#auth_jwt}
        :param ca_file: A path to a PEM-encoded certificate authority used to verify the remote agent's certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#ca_file ConsulProvider#ca_file}
        :param ca_path: A path to a directory of PEM-encoded certificate authority files to use to check the authenticity of client and server connections. Can also be specified with the ``CONSUL_CAPATH`` environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#ca_path ConsulProvider#ca_path}
        :param ca_pem: PEM-encoded certificate authority used to verify the remote agent's certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#ca_pem ConsulProvider#ca_pem}
        :param cert_file: A path to a PEM-encoded certificate provided to the remote agent; requires use of ``key_file`` or ``key_pem``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#cert_file ConsulProvider#cert_file}
        :param cert_pem: PEM-encoded certificate provided to the remote agent; requires use of ``key_file`` or ``key_pem``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#cert_pem ConsulProvider#cert_pem}
        :param datacenter: The datacenter to use. Defaults to that of the agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#datacenter ConsulProvider#datacenter}
        :param header: header block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#header ConsulProvider#header}
        :param http_auth: HTTP Basic Authentication credentials to be used when communicating with Consul, in the format of either ``user`` or ``user:pass``. This may also be specified using the ``CONSUL_HTTP_AUTH`` environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#http_auth ConsulProvider#http_auth}
        :param insecure_https: Boolean value to disable SSL certificate verification; setting this value to true is not recommended for production use. Only use this with scheme set to "https". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#insecure_https ConsulProvider#insecure_https}
        :param key_file: A path to a PEM-encoded private key, required if ``cert_file`` or ``cert_pem`` is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#key_file ConsulProvider#key_file}
        :param key_pem: PEM-encoded private key, required if ``cert_file`` or ``cert_pem`` is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#key_pem ConsulProvider#key_pem}
        :param namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#namespace ConsulProvider#namespace}.
        :param scheme: The URL scheme of the agent to use ("http" or "https"). Defaults to "http". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#scheme ConsulProvider#scheme}
        :param token: The ACL token to use by default when making requests to the agent. Can also be specified with ``CONSUL_HTTP_TOKEN`` or ``CONSUL_TOKEN`` as an environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#token ConsulProvider#token}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f01d2ac117a5791857628dec9a6e218bc037f587cc46a52b64dbd7a716bdf2cc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ConsulProviderConfig(
            address=address,
            alias=alias,
            auth_jwt=auth_jwt,
            ca_file=ca_file,
            ca_path=ca_path,
            ca_pem=ca_pem,
            cert_file=cert_file,
            cert_pem=cert_pem,
            datacenter=datacenter,
            header=header,
            http_auth=http_auth,
            insecure_https=insecure_https,
            key_file=key_file,
            key_pem=key_pem,
            namespace=namespace,
            scheme=scheme,
            token=token,
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
        '''Generates CDKTF code for importing a ConsulProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ConsulProvider to import.
        :param import_from_id: The id of the existing ConsulProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ConsulProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a02dfd811f5f69afba9370db2fa8c1d7ffb4442219651591e8cbc84271760ca)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAddress")
    def reset_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddress", []))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetAuthJwt")
    def reset_auth_jwt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthJwt", []))

    @jsii.member(jsii_name="resetCaFile")
    def reset_ca_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaFile", []))

    @jsii.member(jsii_name="resetCaPath")
    def reset_ca_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaPath", []))

    @jsii.member(jsii_name="resetCaPem")
    def reset_ca_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaPem", []))

    @jsii.member(jsii_name="resetCertFile")
    def reset_cert_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertFile", []))

    @jsii.member(jsii_name="resetCertPem")
    def reset_cert_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertPem", []))

    @jsii.member(jsii_name="resetDatacenter")
    def reset_datacenter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatacenter", []))

    @jsii.member(jsii_name="resetHeader")
    def reset_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeader", []))

    @jsii.member(jsii_name="resetHttpAuth")
    def reset_http_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpAuth", []))

    @jsii.member(jsii_name="resetInsecureHttps")
    def reset_insecure_https(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureHttps", []))

    @jsii.member(jsii_name="resetKeyFile")
    def reset_key_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyFile", []))

    @jsii.member(jsii_name="resetKeyPem")
    def reset_key_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyPem", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetScheme")
    def reset_scheme(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScheme", []))

    @jsii.member(jsii_name="resetToken")
    def reset_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToken", []))

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
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="authJwtInput")
    def auth_jwt_input(self) -> typing.Optional["ConsulProviderAuthJwt"]:
        return typing.cast(typing.Optional["ConsulProviderAuthJwt"], jsii.get(self, "authJwtInput"))

    @builtins.property
    @jsii.member(jsii_name="caFileInput")
    def ca_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caFileInput"))

    @builtins.property
    @jsii.member(jsii_name="caPathInput")
    def ca_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caPathInput"))

    @builtins.property
    @jsii.member(jsii_name="caPemInput")
    def ca_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caPemInput"))

    @builtins.property
    @jsii.member(jsii_name="certFileInput")
    def cert_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certFileInput"))

    @builtins.property
    @jsii.member(jsii_name="certPemInput")
    def cert_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certPemInput"))

    @builtins.property
    @jsii.member(jsii_name="datacenterInput")
    def datacenter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datacenterInput"))

    @builtins.property
    @jsii.member(jsii_name="headerInput")
    def header_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConsulProviderHeader"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConsulProviderHeader"]]], jsii.get(self, "headerInput"))

    @builtins.property
    @jsii.member(jsii_name="httpAuthInput")
    def http_auth_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpAuthInput"))

    @builtins.property
    @jsii.member(jsii_name="insecureHttpsInput")
    def insecure_https_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "insecureHttpsInput"))

    @builtins.property
    @jsii.member(jsii_name="keyFileInput")
    def key_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyFileInput"))

    @builtins.property
    @jsii.member(jsii_name="keyPemInput")
    def key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyPemInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="schemeInput")
    def scheme_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemeInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "address"))

    @address.setter
    def address(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24f93ec6493c397b156fff8622da294105b6035b2aba6b3da864bf1a9a10647d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20821dfb3d569cb9534d057b15190e2db5b14ca3650b3ed9d4c8a57fcf1b6c5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authJwt")
    def auth_jwt(self) -> typing.Optional["ConsulProviderAuthJwt"]:
        return typing.cast(typing.Optional["ConsulProviderAuthJwt"], jsii.get(self, "authJwt"))

    @auth_jwt.setter
    def auth_jwt(self, value: typing.Optional["ConsulProviderAuthJwt"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f58e32bbe60b8e3628c70b66338ba811a86c3dd4873cf8c1b2bf945fdbeb70a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authJwt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="caFile")
    def ca_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caFile"))

    @ca_file.setter
    def ca_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2f8c31966207f96108c3f0565edad5753e28dffab16e831cee172d9dc527267)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="caPath")
    def ca_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caPath"))

    @ca_path.setter
    def ca_path(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__400a48a953773a182a6cb610f5827b0a4f477bb91da104bfa80ba33509456b76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="caPem")
    def ca_pem(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caPem"))

    @ca_pem.setter
    def ca_pem(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba22e6a2677ddcf0b0d2fa28fa8c5b3e6df58f04b474e2d919db283606d354f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caPem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certFile")
    def cert_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certFile"))

    @cert_file.setter
    def cert_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb912a78b3b441a1215b6456d756a502b5f0882b2062fea78a720d6d204ae192)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certPem")
    def cert_pem(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certPem"))

    @cert_pem.setter
    def cert_pem(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f9902375b4a84dddc96dfe319f74f9b65737ca725e390849413ec8797a32bbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certPem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datacenter")
    def datacenter(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datacenter"))

    @datacenter.setter
    def datacenter(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd9184c76aad6d3794208829ba9a97e96917430f6ed5147aa57085449819c80b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="header")
    def header(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConsulProviderHeader"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConsulProviderHeader"]]], jsii.get(self, "header"))

    @header.setter
    def header(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConsulProviderHeader"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__949c040d59bebf336e62daca4feca35132069baa86465b73e7da7b4f23bddefc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "header", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpAuth")
    def http_auth(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpAuth"))

    @http_auth.setter
    def http_auth(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__646afb54df3dfa50ba3b4d9338f69213987e40dce6101705378ccf49411a7b4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpAuth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="insecureHttps")
    def insecure_https(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "insecureHttps"))

    @insecure_https.setter
    def insecure_https(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8f2f0af31fb2cd672e03a564892f000eb278bcc37cdd54d3053810052ad4436)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "insecureHttps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyFile")
    def key_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyFile"))

    @key_file.setter
    def key_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3aa900f8734290f5816279340328a25ee18d4ca90b5544b56cf36b106f2ffdd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyPem")
    def key_pem(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyPem"))

    @key_pem.setter
    def key_pem(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__467468cc619aa20650458e33d1f7fe6ca8e695dcf8647c4ae0c3bec40c1471b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyPem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10fdedd49d6e24d4e47dec42429ebce329f69900dbe93cc5450dd7bb3273248a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scheme")
    def scheme(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scheme"))

    @scheme.setter
    def scheme(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dca3c956703d785fc999d8d2e68a9f6230911cb03a430838ef61181a8b13bac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scheme", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "token"))

    @token.setter
    def token(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3734f2e620ffcd5a2e5b9620424dbe0e2307f3bec1d8d17339fa225a4fb932a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.provider.ConsulProviderAuthJwt",
    jsii_struct_bases=[],
    name_mapping={
        "auth_method": "authMethod",
        "bearer_token": "bearerToken",
        "meta": "meta",
        "use_terraform_cloud_workload_identity": "useTerraformCloudWorkloadIdentity",
    },
)
class ConsulProviderAuthJwt:
    def __init__(
        self,
        *,
        auth_method: builtins.str,
        bearer_token: typing.Optional[builtins.str] = None,
        meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        use_terraform_cloud_workload_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param auth_method: The name of the auth method to use for login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#auth_method ConsulProvider#auth_method}
        :param bearer_token: The bearer token to present to the auth method during login for authentication purposes. For the Kubernetes auth method this is a `Service Account Token (JWT) <https://kubernetes.io/docs/reference/access-authn-authz/authentication/#service-account-tokens>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#bearer_token ConsulProvider#bearer_token}
        :param meta: Specifies arbitrary KV metadata linked to the token. Can be useful to track origins. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#meta ConsulProvider#meta}
        :param use_terraform_cloud_workload_identity: Whether to use a `Terraform Workload Identity token <https://developer.hashicorp.com/terraform/cloud-docs/workspaces/dynamic-provider-credentials/workload-identity-tokens>`_. The token will be read from the ``TFC_WORKLOAD_IDENTITY_TOKEN`` environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#use_terraform_cloud_workload_identity ConsulProvider#use_terraform_cloud_workload_identity}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa61b3d14c47714ce9c473ef8e59138ddc55decfdbc20c683b154bf73b03a614)
            check_type(argname="argument auth_method", value=auth_method, expected_type=type_hints["auth_method"])
            check_type(argname="argument bearer_token", value=bearer_token, expected_type=type_hints["bearer_token"])
            check_type(argname="argument meta", value=meta, expected_type=type_hints["meta"])
            check_type(argname="argument use_terraform_cloud_workload_identity", value=use_terraform_cloud_workload_identity, expected_type=type_hints["use_terraform_cloud_workload_identity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_method": auth_method,
        }
        if bearer_token is not None:
            self._values["bearer_token"] = bearer_token
        if meta is not None:
            self._values["meta"] = meta
        if use_terraform_cloud_workload_identity is not None:
            self._values["use_terraform_cloud_workload_identity"] = use_terraform_cloud_workload_identity

    @builtins.property
    def auth_method(self) -> builtins.str:
        '''The name of the auth method to use for login.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#auth_method ConsulProvider#auth_method}
        '''
        result = self._values.get("auth_method")
        assert result is not None, "Required property 'auth_method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bearer_token(self) -> typing.Optional[builtins.str]:
        '''The bearer token to present to the auth method during login for authentication purposes.

        For the Kubernetes auth method this is a `Service Account Token (JWT) <https://kubernetes.io/docs/reference/access-authn-authz/authentication/#service-account-tokens>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#bearer_token ConsulProvider#bearer_token}
        '''
        result = self._values.get("bearer_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def meta(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Specifies arbitrary KV metadata linked to the token. Can be useful to track origins.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#meta ConsulProvider#meta}
        '''
        result = self._values.get("meta")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def use_terraform_cloud_workload_identity(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to use a `Terraform Workload Identity token <https://developer.hashicorp.com/terraform/cloud-docs/workspaces/dynamic-provider-credentials/workload-identity-tokens>`_. The token will be read from the ``TFC_WORKLOAD_IDENTITY_TOKEN`` environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#use_terraform_cloud_workload_identity ConsulProvider#use_terraform_cloud_workload_identity}
        '''
        result = self._values.get("use_terraform_cloud_workload_identity")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConsulProviderAuthJwt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.provider.ConsulProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "address": "address",
        "alias": "alias",
        "auth_jwt": "authJwt",
        "ca_file": "caFile",
        "ca_path": "caPath",
        "ca_pem": "caPem",
        "cert_file": "certFile",
        "cert_pem": "certPem",
        "datacenter": "datacenter",
        "header": "header",
        "http_auth": "httpAuth",
        "insecure_https": "insecureHttps",
        "key_file": "keyFile",
        "key_pem": "keyPem",
        "namespace": "namespace",
        "scheme": "scheme",
        "token": "token",
    },
)
class ConsulProviderConfig:
    def __init__(
        self,
        *,
        address: typing.Optional[builtins.str] = None,
        alias: typing.Optional[builtins.str] = None,
        auth_jwt: typing.Optional[typing.Union[ConsulProviderAuthJwt, typing.Dict[builtins.str, typing.Any]]] = None,
        ca_file: typing.Optional[builtins.str] = None,
        ca_path: typing.Optional[builtins.str] = None,
        ca_pem: typing.Optional[builtins.str] = None,
        cert_file: typing.Optional[builtins.str] = None,
        cert_pem: typing.Optional[builtins.str] = None,
        datacenter: typing.Optional[builtins.str] = None,
        header: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConsulProviderHeader", typing.Dict[builtins.str, typing.Any]]]]] = None,
        http_auth: typing.Optional[builtins.str] = None,
        insecure_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        key_file: typing.Optional[builtins.str] = None,
        key_pem: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        scheme: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address: The HTTP(S) API address of the agent to use. Defaults to "127.0.0.1:8500". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#address ConsulProvider#address}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#alias ConsulProvider#alias}
        :param auth_jwt: auth_jwt block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#auth_jwt ConsulProvider#auth_jwt}
        :param ca_file: A path to a PEM-encoded certificate authority used to verify the remote agent's certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#ca_file ConsulProvider#ca_file}
        :param ca_path: A path to a directory of PEM-encoded certificate authority files to use to check the authenticity of client and server connections. Can also be specified with the ``CONSUL_CAPATH`` environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#ca_path ConsulProvider#ca_path}
        :param ca_pem: PEM-encoded certificate authority used to verify the remote agent's certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#ca_pem ConsulProvider#ca_pem}
        :param cert_file: A path to a PEM-encoded certificate provided to the remote agent; requires use of ``key_file`` or ``key_pem``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#cert_file ConsulProvider#cert_file}
        :param cert_pem: PEM-encoded certificate provided to the remote agent; requires use of ``key_file`` or ``key_pem``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#cert_pem ConsulProvider#cert_pem}
        :param datacenter: The datacenter to use. Defaults to that of the agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#datacenter ConsulProvider#datacenter}
        :param header: header block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#header ConsulProvider#header}
        :param http_auth: HTTP Basic Authentication credentials to be used when communicating with Consul, in the format of either ``user`` or ``user:pass``. This may also be specified using the ``CONSUL_HTTP_AUTH`` environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#http_auth ConsulProvider#http_auth}
        :param insecure_https: Boolean value to disable SSL certificate verification; setting this value to true is not recommended for production use. Only use this with scheme set to "https". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#insecure_https ConsulProvider#insecure_https}
        :param key_file: A path to a PEM-encoded private key, required if ``cert_file`` or ``cert_pem`` is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#key_file ConsulProvider#key_file}
        :param key_pem: PEM-encoded private key, required if ``cert_file`` or ``cert_pem`` is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#key_pem ConsulProvider#key_pem}
        :param namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#namespace ConsulProvider#namespace}.
        :param scheme: The URL scheme of the agent to use ("http" or "https"). Defaults to "http". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#scheme ConsulProvider#scheme}
        :param token: The ACL token to use by default when making requests to the agent. Can also be specified with ``CONSUL_HTTP_TOKEN`` or ``CONSUL_TOKEN`` as an environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#token ConsulProvider#token}
        '''
        if isinstance(auth_jwt, dict):
            auth_jwt = ConsulProviderAuthJwt(**auth_jwt)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b1d3bcb43ba4c50910ed19df2baf0bb2e7fdd5f41bf4a825bf9a2497d60db07)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument auth_jwt", value=auth_jwt, expected_type=type_hints["auth_jwt"])
            check_type(argname="argument ca_file", value=ca_file, expected_type=type_hints["ca_file"])
            check_type(argname="argument ca_path", value=ca_path, expected_type=type_hints["ca_path"])
            check_type(argname="argument ca_pem", value=ca_pem, expected_type=type_hints["ca_pem"])
            check_type(argname="argument cert_file", value=cert_file, expected_type=type_hints["cert_file"])
            check_type(argname="argument cert_pem", value=cert_pem, expected_type=type_hints["cert_pem"])
            check_type(argname="argument datacenter", value=datacenter, expected_type=type_hints["datacenter"])
            check_type(argname="argument header", value=header, expected_type=type_hints["header"])
            check_type(argname="argument http_auth", value=http_auth, expected_type=type_hints["http_auth"])
            check_type(argname="argument insecure_https", value=insecure_https, expected_type=type_hints["insecure_https"])
            check_type(argname="argument key_file", value=key_file, expected_type=type_hints["key_file"])
            check_type(argname="argument key_pem", value=key_pem, expected_type=type_hints["key_pem"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument scheme", value=scheme, expected_type=type_hints["scheme"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if address is not None:
            self._values["address"] = address
        if alias is not None:
            self._values["alias"] = alias
        if auth_jwt is not None:
            self._values["auth_jwt"] = auth_jwt
        if ca_file is not None:
            self._values["ca_file"] = ca_file
        if ca_path is not None:
            self._values["ca_path"] = ca_path
        if ca_pem is not None:
            self._values["ca_pem"] = ca_pem
        if cert_file is not None:
            self._values["cert_file"] = cert_file
        if cert_pem is not None:
            self._values["cert_pem"] = cert_pem
        if datacenter is not None:
            self._values["datacenter"] = datacenter
        if header is not None:
            self._values["header"] = header
        if http_auth is not None:
            self._values["http_auth"] = http_auth
        if insecure_https is not None:
            self._values["insecure_https"] = insecure_https
        if key_file is not None:
            self._values["key_file"] = key_file
        if key_pem is not None:
            self._values["key_pem"] = key_pem
        if namespace is not None:
            self._values["namespace"] = namespace
        if scheme is not None:
            self._values["scheme"] = scheme
        if token is not None:
            self._values["token"] = token

    @builtins.property
    def address(self) -> typing.Optional[builtins.str]:
        '''The HTTP(S) API address of the agent to use. Defaults to "127.0.0.1:8500".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#address ConsulProvider#address}
        '''
        result = self._values.get("address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#alias ConsulProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_jwt(self) -> typing.Optional[ConsulProviderAuthJwt]:
        '''auth_jwt block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#auth_jwt ConsulProvider#auth_jwt}
        '''
        result = self._values.get("auth_jwt")
        return typing.cast(typing.Optional[ConsulProviderAuthJwt], result)

    @builtins.property
    def ca_file(self) -> typing.Optional[builtins.str]:
        '''A path to a PEM-encoded certificate authority used to verify the remote agent's certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#ca_file ConsulProvider#ca_file}
        '''
        result = self._values.get("ca_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ca_path(self) -> typing.Optional[builtins.str]:
        '''A path to a directory of PEM-encoded certificate authority files to use to check the authenticity of client and server connections.

        Can also be specified with the ``CONSUL_CAPATH`` environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#ca_path ConsulProvider#ca_path}
        '''
        result = self._values.get("ca_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ca_pem(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded certificate authority used to verify the remote agent's certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#ca_pem ConsulProvider#ca_pem}
        '''
        result = self._values.get("ca_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_file(self) -> typing.Optional[builtins.str]:
        '''A path to a PEM-encoded certificate provided to the remote agent; requires use of ``key_file`` or ``key_pem``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#cert_file ConsulProvider#cert_file}
        '''
        result = self._values.get("cert_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_pem(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded certificate provided to the remote agent; requires use of ``key_file`` or ``key_pem``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#cert_pem ConsulProvider#cert_pem}
        '''
        result = self._values.get("cert_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datacenter(self) -> typing.Optional[builtins.str]:
        '''The datacenter to use. Defaults to that of the agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#datacenter ConsulProvider#datacenter}
        '''
        result = self._values.get("datacenter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def header(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConsulProviderHeader"]]]:
        '''header block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#header ConsulProvider#header}
        '''
        result = self._values.get("header")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConsulProviderHeader"]]], result)

    @builtins.property
    def http_auth(self) -> typing.Optional[builtins.str]:
        '''HTTP Basic Authentication credentials to be used when communicating with Consul, in the format of either ``user`` or ``user:pass``.

        This may also be specified using the ``CONSUL_HTTP_AUTH`` environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#http_auth ConsulProvider#http_auth}
        '''
        result = self._values.get("http_auth")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insecure_https(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Boolean value to disable SSL certificate verification;

        setting this value to true is not recommended for production use. Only use this with scheme set to "https".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#insecure_https ConsulProvider#insecure_https}
        '''
        result = self._values.get("insecure_https")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def key_file(self) -> typing.Optional[builtins.str]:
        '''A path to a PEM-encoded private key, required if ``cert_file`` or ``cert_pem`` is specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#key_file ConsulProvider#key_file}
        '''
        result = self._values.get("key_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_pem(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded private key, required if ``cert_file`` or ``cert_pem`` is specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#key_pem ConsulProvider#key_pem}
        '''
        result = self._values.get("key_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#namespace ConsulProvider#namespace}.'''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scheme(self) -> typing.Optional[builtins.str]:
        '''The URL scheme of the agent to use ("http" or "https"). Defaults to "http".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#scheme ConsulProvider#scheme}
        '''
        result = self._values.get("scheme")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''The ACL token to use by default when making requests to the agent.

        Can also be specified with ``CONSUL_HTTP_TOKEN`` or ``CONSUL_TOKEN`` as an environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#token ConsulProvider#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConsulProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.provider.ConsulProviderHeader",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class ConsulProviderHeader:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: The name of the header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#name ConsulProvider#name}
        :param value: The value of the header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#value ConsulProvider#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__639c6fe0ecdefeae3c3e7d334e962a054c6a340bcde089da84861f4f52b5951e)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the header.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#name ConsulProvider#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''The value of the header.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs#value ConsulProvider#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConsulProviderHeader(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ConsulProvider",
    "ConsulProviderAuthJwt",
    "ConsulProviderConfig",
    "ConsulProviderHeader",
]

publication.publish()

def _typecheckingstub__f01d2ac117a5791857628dec9a6e218bc037f587cc46a52b64dbd7a716bdf2cc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    address: typing.Optional[builtins.str] = None,
    alias: typing.Optional[builtins.str] = None,
    auth_jwt: typing.Optional[typing.Union[ConsulProviderAuthJwt, typing.Dict[builtins.str, typing.Any]]] = None,
    ca_file: typing.Optional[builtins.str] = None,
    ca_path: typing.Optional[builtins.str] = None,
    ca_pem: typing.Optional[builtins.str] = None,
    cert_file: typing.Optional[builtins.str] = None,
    cert_pem: typing.Optional[builtins.str] = None,
    datacenter: typing.Optional[builtins.str] = None,
    header: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConsulProviderHeader, typing.Dict[builtins.str, typing.Any]]]]] = None,
    http_auth: typing.Optional[builtins.str] = None,
    insecure_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    key_file: typing.Optional[builtins.str] = None,
    key_pem: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    scheme: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a02dfd811f5f69afba9370db2fa8c1d7ffb4442219651591e8cbc84271760ca(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24f93ec6493c397b156fff8622da294105b6035b2aba6b3da864bf1a9a10647d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20821dfb3d569cb9534d057b15190e2db5b14ca3650b3ed9d4c8a57fcf1b6c5c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f58e32bbe60b8e3628c70b66338ba811a86c3dd4873cf8c1b2bf945fdbeb70a(
    value: typing.Optional[ConsulProviderAuthJwt],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2f8c31966207f96108c3f0565edad5753e28dffab16e831cee172d9dc527267(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__400a48a953773a182a6cb610f5827b0a4f477bb91da104bfa80ba33509456b76(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba22e6a2677ddcf0b0d2fa28fa8c5b3e6df58f04b474e2d919db283606d354f1(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb912a78b3b441a1215b6456d756a502b5f0882b2062fea78a720d6d204ae192(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f9902375b4a84dddc96dfe319f74f9b65737ca725e390849413ec8797a32bbc(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd9184c76aad6d3794208829ba9a97e96917430f6ed5147aa57085449819c80b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__949c040d59bebf336e62daca4feca35132069baa86465b73e7da7b4f23bddefc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConsulProviderHeader]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__646afb54df3dfa50ba3b4d9338f69213987e40dce6101705378ccf49411a7b4b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8f2f0af31fb2cd672e03a564892f000eb278bcc37cdd54d3053810052ad4436(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3aa900f8734290f5816279340328a25ee18d4ca90b5544b56cf36b106f2ffdd(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__467468cc619aa20650458e33d1f7fe6ca8e695dcf8647c4ae0c3bec40c1471b7(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10fdedd49d6e24d4e47dec42429ebce329f69900dbe93cc5450dd7bb3273248a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dca3c956703d785fc999d8d2e68a9f6230911cb03a430838ef61181a8b13bac(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3734f2e620ffcd5a2e5b9620424dbe0e2307f3bec1d8d17339fa225a4fb932a0(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa61b3d14c47714ce9c473ef8e59138ddc55decfdbc20c683b154bf73b03a614(
    *,
    auth_method: builtins.str,
    bearer_token: typing.Optional[builtins.str] = None,
    meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    use_terraform_cloud_workload_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b1d3bcb43ba4c50910ed19df2baf0bb2e7fdd5f41bf4a825bf9a2497d60db07(
    *,
    address: typing.Optional[builtins.str] = None,
    alias: typing.Optional[builtins.str] = None,
    auth_jwt: typing.Optional[typing.Union[ConsulProviderAuthJwt, typing.Dict[builtins.str, typing.Any]]] = None,
    ca_file: typing.Optional[builtins.str] = None,
    ca_path: typing.Optional[builtins.str] = None,
    ca_pem: typing.Optional[builtins.str] = None,
    cert_file: typing.Optional[builtins.str] = None,
    cert_pem: typing.Optional[builtins.str] = None,
    datacenter: typing.Optional[builtins.str] = None,
    header: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConsulProviderHeader, typing.Dict[builtins.str, typing.Any]]]]] = None,
    http_auth: typing.Optional[builtins.str] = None,
    insecure_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    key_file: typing.Optional[builtins.str] = None,
    key_pem: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    scheme: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__639c6fe0ecdefeae3c3e7d334e962a054c6a340bcde089da84861f4f52b5951e(
    *,
    name: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
