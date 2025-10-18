r'''
# `consul_config_entry_service_resolver`

Refer to the Terraform Registry for docs: [`consul_config_entry_service_resolver`](https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver).
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


class ConfigEntryServiceResolver(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolver",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver consul_config_entry_service_resolver}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        connect_timeout: typing.Optional[builtins.str] = None,
        default_subset: typing.Optional[builtins.str] = None,
        failover: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverFailover", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        load_balancer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverLoadBalancer", typing.Dict[builtins.str, typing.Any]]]]] = None,
        meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        redirect: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverRedirect", typing.Dict[builtins.str, typing.Any]]]]] = None,
        request_timeout: typing.Optional[builtins.str] = None,
        subsets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverSubsets", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver consul_config_entry_service_resolver} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Specifies a name for the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#name ConfigEntryServiceResolver#name}
        :param connect_timeout: Specifies the timeout duration for establishing new network connections to this service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#connect_timeout ConfigEntryServiceResolver#connect_timeout}
        :param default_subset: Specifies a defined subset of service instances to use when no explicit subset is requested. If this parameter is not specified, Consul uses the unnamed default subset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#default_subset ConfigEntryServiceResolver#default_subset}
        :param failover: failover block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#failover ConfigEntryServiceResolver#failover}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#id ConfigEntryServiceResolver#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param load_balancer: load_balancer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#load_balancer ConfigEntryServiceResolver#load_balancer}
        :param meta: Specifies key-value pairs to add to the KV store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#meta ConfigEntryServiceResolver#meta}
        :param namespace: Specifies the namespace that the service resolver applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#namespace ConfigEntryServiceResolver#namespace}
        :param partition: Specifies the admin partition that the service resolver applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#partition ConfigEntryServiceResolver#partition}
        :param redirect: redirect block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#redirect ConfigEntryServiceResolver#redirect}
        :param request_timeout: Specifies the timeout duration for receiving an HTTP response from this service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#request_timeout ConfigEntryServiceResolver#request_timeout}
        :param subsets: subsets block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#subsets ConfigEntryServiceResolver#subsets}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4e61204e1ca5146b479dae508aa5bdcab93c240d2d8b6c85e044d636ac5d302)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigEntryServiceResolverConfig(
            name=name,
            connect_timeout=connect_timeout,
            default_subset=default_subset,
            failover=failover,
            id=id,
            load_balancer=load_balancer,
            meta=meta,
            namespace=namespace,
            partition=partition,
            redirect=redirect,
            request_timeout=request_timeout,
            subsets=subsets,
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
        '''Generates CDKTF code for importing a ConfigEntryServiceResolver resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ConfigEntryServiceResolver to import.
        :param import_from_id: The id of the existing ConfigEntryServiceResolver that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ConfigEntryServiceResolver to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__644888282661491b9541a685a0bcc48dfdb0a311aa490a3b878d8c7339d2b94d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putFailover")
    def put_failover(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverFailover", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff93d0b19f3a2a535edf706e3964712cfee593ddba308c95aa578aa780a8c58c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putFailover", [value]))

    @jsii.member(jsii_name="putLoadBalancer")
    def put_load_balancer(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverLoadBalancer", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a43c45354a31125790533011c5aa1d026c989410fc777fc22b66cef14a83e1de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLoadBalancer", [value]))

    @jsii.member(jsii_name="putRedirect")
    def put_redirect(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverRedirect", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e3a0526470e726ca34ca06269b6368193a58b2f778e9c2b2872d1250ce46fc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRedirect", [value]))

    @jsii.member(jsii_name="putSubsets")
    def put_subsets(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverSubsets", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c669e45cb44b4fe70ad5ed5373dd8b8b6bc65a445b9e84a9fb67d96cf2f3c82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSubsets", [value]))

    @jsii.member(jsii_name="resetConnectTimeout")
    def reset_connect_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectTimeout", []))

    @jsii.member(jsii_name="resetDefaultSubset")
    def reset_default_subset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultSubset", []))

    @jsii.member(jsii_name="resetFailover")
    def reset_failover(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailover", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLoadBalancer")
    def reset_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoadBalancer", []))

    @jsii.member(jsii_name="resetMeta")
    def reset_meta(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMeta", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPartition")
    def reset_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartition", []))

    @jsii.member(jsii_name="resetRedirect")
    def reset_redirect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirect", []))

    @jsii.member(jsii_name="resetRequestTimeout")
    def reset_request_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestTimeout", []))

    @jsii.member(jsii_name="resetSubsets")
    def reset_subsets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubsets", []))

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
    @jsii.member(jsii_name="failover")
    def failover(self) -> "ConfigEntryServiceResolverFailoverList":
        return typing.cast("ConfigEntryServiceResolverFailoverList", jsii.get(self, "failover"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(self) -> "ConfigEntryServiceResolverLoadBalancerList":
        return typing.cast("ConfigEntryServiceResolverLoadBalancerList", jsii.get(self, "loadBalancer"))

    @builtins.property
    @jsii.member(jsii_name="redirect")
    def redirect(self) -> "ConfigEntryServiceResolverRedirectList":
        return typing.cast("ConfigEntryServiceResolverRedirectList", jsii.get(self, "redirect"))

    @builtins.property
    @jsii.member(jsii_name="subsets")
    def subsets(self) -> "ConfigEntryServiceResolverSubsetsList":
        return typing.cast("ConfigEntryServiceResolverSubsetsList", jsii.get(self, "subsets"))

    @builtins.property
    @jsii.member(jsii_name="connectTimeoutInput")
    def connect_timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultSubsetInput")
    def default_subset_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultSubsetInput"))

    @builtins.property
    @jsii.member(jsii_name="failoverInput")
    def failover_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverFailover"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverFailover"]]], jsii.get(self, "failoverInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancerInput")
    def load_balancer_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancer"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancer"]]], jsii.get(self, "loadBalancerInput"))

    @builtins.property
    @jsii.member(jsii_name="metaInput")
    def meta_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "metaInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="partitionInput")
    def partition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "partitionInput"))

    @builtins.property
    @jsii.member(jsii_name="redirectInput")
    def redirect_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverRedirect"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverRedirect"]]], jsii.get(self, "redirectInput"))

    @builtins.property
    @jsii.member(jsii_name="requestTimeoutInput")
    def request_timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="subsetsInput")
    def subsets_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverSubsets"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverSubsets"]]], jsii.get(self, "subsetsInput"))

    @builtins.property
    @jsii.member(jsii_name="connectTimeout")
    def connect_timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectTimeout"))

    @connect_timeout.setter
    def connect_timeout(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31f46a94b7e34764b2ba92a52873ce4c10c149778e8385d70c35f41acc0c7e2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultSubset")
    def default_subset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultSubset"))

    @default_subset.setter
    def default_subset(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd46a66680ff65b6f0712fa19a0f59803d159b022fb7ac78d46aabb9f8d373b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultSubset", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__397f53a08ea3e418a58e08373eea28bc4830f9c886d130475bd94d030a235796)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="meta")
    def meta(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "meta"))

    @meta.setter
    def meta(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee75fa01d1e9e64ef2c9fe0bf0fad4c076e740daded2a596f620dbc3858a686d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "meta", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23678c1b95d7d8ae582ab473082c00e7dedf59f2f13ee79b126d4ccace505be4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb273b30b9e8f2eff2c6132ea4d14ced0308bf06c2ec708e7d4580c65aecde05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partition")
    def partition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partition"))

    @partition.setter
    def partition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05492437b3557a4be8267c0790b851479ef0061038376e912d23b64c02dcc5c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestTimeout")
    def request_timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestTimeout"))

    @request_timeout.setter
    def request_timeout(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cd88cb34ce92ba61c6a9a7ac64f6db84fd1460266821d54d5b8357c2a28b5cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestTimeout", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "connect_timeout": "connectTimeout",
        "default_subset": "defaultSubset",
        "failover": "failover",
        "id": "id",
        "load_balancer": "loadBalancer",
        "meta": "meta",
        "namespace": "namespace",
        "partition": "partition",
        "redirect": "redirect",
        "request_timeout": "requestTimeout",
        "subsets": "subsets",
    },
)
class ConfigEntryServiceResolverConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        connect_timeout: typing.Optional[builtins.str] = None,
        default_subset: typing.Optional[builtins.str] = None,
        failover: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverFailover", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        load_balancer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverLoadBalancer", typing.Dict[builtins.str, typing.Any]]]]] = None,
        meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        redirect: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverRedirect", typing.Dict[builtins.str, typing.Any]]]]] = None,
        request_timeout: typing.Optional[builtins.str] = None,
        subsets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverSubsets", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Specifies a name for the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#name ConfigEntryServiceResolver#name}
        :param connect_timeout: Specifies the timeout duration for establishing new network connections to this service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#connect_timeout ConfigEntryServiceResolver#connect_timeout}
        :param default_subset: Specifies a defined subset of service instances to use when no explicit subset is requested. If this parameter is not specified, Consul uses the unnamed default subset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#default_subset ConfigEntryServiceResolver#default_subset}
        :param failover: failover block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#failover ConfigEntryServiceResolver#failover}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#id ConfigEntryServiceResolver#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param load_balancer: load_balancer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#load_balancer ConfigEntryServiceResolver#load_balancer}
        :param meta: Specifies key-value pairs to add to the KV store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#meta ConfigEntryServiceResolver#meta}
        :param namespace: Specifies the namespace that the service resolver applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#namespace ConfigEntryServiceResolver#namespace}
        :param partition: Specifies the admin partition that the service resolver applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#partition ConfigEntryServiceResolver#partition}
        :param redirect: redirect block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#redirect ConfigEntryServiceResolver#redirect}
        :param request_timeout: Specifies the timeout duration for receiving an HTTP response from this service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#request_timeout ConfigEntryServiceResolver#request_timeout}
        :param subsets: subsets block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#subsets ConfigEntryServiceResolver#subsets}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c3c86986bf1ac196e611e841285caf3db9edabae57b668cb1112dd160dae46f)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument connect_timeout", value=connect_timeout, expected_type=type_hints["connect_timeout"])
            check_type(argname="argument default_subset", value=default_subset, expected_type=type_hints["default_subset"])
            check_type(argname="argument failover", value=failover, expected_type=type_hints["failover"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument load_balancer", value=load_balancer, expected_type=type_hints["load_balancer"])
            check_type(argname="argument meta", value=meta, expected_type=type_hints["meta"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument redirect", value=redirect, expected_type=type_hints["redirect"])
            check_type(argname="argument request_timeout", value=request_timeout, expected_type=type_hints["request_timeout"])
            check_type(argname="argument subsets", value=subsets, expected_type=type_hints["subsets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
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
        if connect_timeout is not None:
            self._values["connect_timeout"] = connect_timeout
        if default_subset is not None:
            self._values["default_subset"] = default_subset
        if failover is not None:
            self._values["failover"] = failover
        if id is not None:
            self._values["id"] = id
        if load_balancer is not None:
            self._values["load_balancer"] = load_balancer
        if meta is not None:
            self._values["meta"] = meta
        if namespace is not None:
            self._values["namespace"] = namespace
        if partition is not None:
            self._values["partition"] = partition
        if redirect is not None:
            self._values["redirect"] = redirect
        if request_timeout is not None:
            self._values["request_timeout"] = request_timeout
        if subsets is not None:
            self._values["subsets"] = subsets

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
    def name(self) -> builtins.str:
        '''Specifies a name for the configuration entry.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#name ConfigEntryServiceResolver#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def connect_timeout(self) -> typing.Optional[builtins.str]:
        '''Specifies the timeout duration for establishing new network connections to this service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#connect_timeout ConfigEntryServiceResolver#connect_timeout}
        '''
        result = self._values.get("connect_timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_subset(self) -> typing.Optional[builtins.str]:
        '''Specifies a defined subset of service instances to use when no explicit subset is requested.

        If this parameter is not specified, Consul uses the unnamed default subset.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#default_subset ConfigEntryServiceResolver#default_subset}
        '''
        result = self._values.get("default_subset")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def failover(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverFailover"]]]:
        '''failover block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#failover ConfigEntryServiceResolver#failover}
        '''
        result = self._values.get("failover")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverFailover"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#id ConfigEntryServiceResolver#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def load_balancer(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancer"]]]:
        '''load_balancer block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#load_balancer ConfigEntryServiceResolver#load_balancer}
        '''
        result = self._values.get("load_balancer")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancer"]]], result)

    @builtins.property
    def meta(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Specifies key-value pairs to add to the KV store.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#meta ConfigEntryServiceResolver#meta}
        '''
        result = self._values.get("meta")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Specifies the namespace that the service resolver applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#namespace ConfigEntryServiceResolver#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''Specifies the admin partition that the service resolver applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#partition ConfigEntryServiceResolver#partition}
        '''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redirect(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverRedirect"]]]:
        '''redirect block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#redirect ConfigEntryServiceResolver#redirect}
        '''
        result = self._values.get("redirect")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverRedirect"]]], result)

    @builtins.property
    def request_timeout(self) -> typing.Optional[builtins.str]:
        '''Specifies the timeout duration for receiving an HTTP response from this service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#request_timeout ConfigEntryServiceResolver#request_timeout}
        '''
        result = self._values.get("request_timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subsets(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverSubsets"]]]:
        '''subsets block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#subsets ConfigEntryServiceResolver#subsets}
        '''
        result = self._values.get("subsets")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverSubsets"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceResolverConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverFailover",
    jsii_struct_bases=[],
    name_mapping={
        "subset_name": "subsetName",
        "datacenters": "datacenters",
        "namespace": "namespace",
        "sameness_group": "samenessGroup",
        "service": "service",
        "service_subset": "serviceSubset",
        "targets": "targets",
    },
)
class ConfigEntryServiceResolverFailover:
    def __init__(
        self,
        *,
        subset_name: builtins.str,
        datacenters: typing.Optional[typing.Sequence[builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        sameness_group: typing.Optional[builtins.str] = None,
        service: typing.Optional[builtins.str] = None,
        service_subset: typing.Optional[builtins.str] = None,
        targets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverFailoverTargets", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param subset_name: Name of subset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#subset_name ConfigEntryServiceResolver#subset_name}
        :param datacenters: Specifies an ordered list of datacenters at the failover location to attempt connections to during a failover scenario. When Consul cannot establish a connection with the first datacenter in the list, it proceeds sequentially until establishing a connection with another datacenter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#datacenters ConfigEntryServiceResolver#datacenters}
        :param namespace: Specifies the namespace at the failover location where the failover services are deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#namespace ConfigEntryServiceResolver#namespace}
        :param sameness_group: Specifies the sameness group at the failover location where the failover services are deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#sameness_group ConfigEntryServiceResolver#sameness_group}
        :param service: Specifies the name of the service to resolve at the failover location during a failover scenario. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#service ConfigEntryServiceResolver#service}
        :param service_subset: Specifies the name of a subset of service instances to resolve at the failover location during a failover scenario. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#service_subset ConfigEntryServiceResolver#service_subset}
        :param targets: targets block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#targets ConfigEntryServiceResolver#targets}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c93d7fef4476028f513ce9938b70691eedb13d4d64b45a022dbaedf9b62f7006)
            check_type(argname="argument subset_name", value=subset_name, expected_type=type_hints["subset_name"])
            check_type(argname="argument datacenters", value=datacenters, expected_type=type_hints["datacenters"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument sameness_group", value=sameness_group, expected_type=type_hints["sameness_group"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument service_subset", value=service_subset, expected_type=type_hints["service_subset"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "subset_name": subset_name,
        }
        if datacenters is not None:
            self._values["datacenters"] = datacenters
        if namespace is not None:
            self._values["namespace"] = namespace
        if sameness_group is not None:
            self._values["sameness_group"] = sameness_group
        if service is not None:
            self._values["service"] = service
        if service_subset is not None:
            self._values["service_subset"] = service_subset
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def subset_name(self) -> builtins.str:
        '''Name of subset.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#subset_name ConfigEntryServiceResolver#subset_name}
        '''
        result = self._values.get("subset_name")
        assert result is not None, "Required property 'subset_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def datacenters(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies an ordered list of datacenters at the failover location to attempt connections to during a failover scenario.

        When Consul cannot establish a connection with the first datacenter in the list, it proceeds sequentially until establishing a connection with another datacenter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#datacenters ConfigEntryServiceResolver#datacenters}
        '''
        result = self._values.get("datacenters")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Specifies the namespace at the failover location where the failover services are deployed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#namespace ConfigEntryServiceResolver#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sameness_group(self) -> typing.Optional[builtins.str]:
        '''Specifies the sameness group at the failover location where the failover services are deployed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#sameness_group ConfigEntryServiceResolver#sameness_group}
        '''
        result = self._values.get("sameness_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of the service to resolve at the failover location during a failover scenario.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#service ConfigEntryServiceResolver#service}
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_subset(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of a subset of service instances to resolve at the failover location during a failover scenario.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#service_subset ConfigEntryServiceResolver#service_subset}
        '''
        result = self._values.get("service_subset")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def targets(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverFailoverTargets"]]]:
        '''targets block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#targets ConfigEntryServiceResolver#targets}
        '''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverFailoverTargets"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceResolverFailover(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceResolverFailoverList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverFailoverList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__db037a9fe39bdedd65653d64232ac321875f4f99257ead10f60b3a13f0802a67)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceResolverFailoverOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddb0dc77f9bdcfab344bef92ce9faac861cacb3614d80a960d808ca2683157b1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceResolverFailoverOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f943bf83e49b172eea8d9273b91a6a1feb6f8bb7cac00336bb3fdc1d1ba5904)
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
            type_hints = typing.get_type_hints(_typecheckingstub__38e633d116f0d87a560fb90afebc88757afd5c4a9682c83083778467ab95acde)
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
            type_hints = typing.get_type_hints(_typecheckingstub__589c4ed83beb6d130d48645ba64c319b149759ca251f90c5c66f4bfb925f79c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverFailover]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverFailover]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverFailover]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9280a191b0d62ca17de3e2d47e323fa943487b5b288fa48ba7f5a2d816103db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceResolverFailoverOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverFailoverOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__25973f6a80a9e3d6d8ec910c672fccea6b9b4a208bec32353fc65a340659b44a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putTargets")
    def put_targets(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverFailoverTargets", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d26c3640fd9e614a338ddf4ca15c554e807e38d726a0d35f776270929d9394ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTargets", [value]))

    @jsii.member(jsii_name="resetDatacenters")
    def reset_datacenters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatacenters", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetSamenessGroup")
    def reset_sameness_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSamenessGroup", []))

    @jsii.member(jsii_name="resetService")
    def reset_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetService", []))

    @jsii.member(jsii_name="resetServiceSubset")
    def reset_service_subset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceSubset", []))

    @jsii.member(jsii_name="resetTargets")
    def reset_targets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargets", []))

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(self) -> "ConfigEntryServiceResolverFailoverTargetsList":
        return typing.cast("ConfigEntryServiceResolverFailoverTargetsList", jsii.get(self, "targets"))

    @builtins.property
    @jsii.member(jsii_name="datacentersInput")
    def datacenters_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "datacentersInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="samenessGroupInput")
    def sameness_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "samenessGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceSubsetInput")
    def service_subset_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceSubsetInput"))

    @builtins.property
    @jsii.member(jsii_name="subsetNameInput")
    def subset_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subsetNameInput"))

    @builtins.property
    @jsii.member(jsii_name="targetsInput")
    def targets_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverFailoverTargets"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverFailoverTargets"]]], jsii.get(self, "targetsInput"))

    @builtins.property
    @jsii.member(jsii_name="datacenters")
    def datacenters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "datacenters"))

    @datacenters.setter
    def datacenters(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2816d1472c8428849c551e797caff0d31246920ab5575d82862fe3a0305b92f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c3628e9ad82c910b9cfe0c4fef8e3fa2eed9339ba16ade99e785ee4bb731002)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="samenessGroup")
    def sameness_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "samenessGroup"))

    @sameness_group.setter
    def sameness_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b1de8a7018aa4b61114b15ce53c35615c89c02ab557638ea9647eeddefa0efa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samenessGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0837d9cff945b4dafc8140296190ac85cceff4c883286243326d7d0583f038db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceSubset")
    def service_subset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceSubset"))

    @service_subset.setter
    def service_subset(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3be41cf0cb8cf92a199f1e1345a2084dc151d480b6839caefc4d5ccaa3e67acb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceSubset", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subsetName")
    def subset_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subsetName"))

    @subset_name.setter
    def subset_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7cbdf8506603b419bb59e2e445702e7281984526fd7256da76d7769ad932603)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subsetName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverFailover]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverFailover]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverFailover]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b1eb823bb0b3df3fdf22dfa8a32c209a8bc03fab9ca5ae2fe67a9af4b4e5552)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverFailoverTargets",
    jsii_struct_bases=[],
    name_mapping={
        "datacenter": "datacenter",
        "namespace": "namespace",
        "partition": "partition",
        "peer": "peer",
        "service": "service",
        "service_subset": "serviceSubset",
    },
)
class ConfigEntryServiceResolverFailoverTargets:
    def __init__(
        self,
        *,
        datacenter: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        peer: typing.Optional[builtins.str] = None,
        service: typing.Optional[builtins.str] = None,
        service_subset: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param datacenter: Specifies the WAN federated datacenter to use for the failover target. If empty, the current datacenter is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#datacenter ConfigEntryServiceResolver#datacenter}
        :param namespace: Specifies the namespace to use for the failover target. If empty, the default namespace is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#namespace ConfigEntryServiceResolver#namespace}
        :param partition: Specifies the admin partition within the same datacenter to use for the failover target. If empty, the default partition is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#partition ConfigEntryServiceResolver#partition}
        :param peer: Specifies the destination cluster peer to resolve the target service name from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#peer ConfigEntryServiceResolver#peer}
        :param service: Specifies the service name to use for the failover target. If empty, the current service name is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#service ConfigEntryServiceResolver#service}
        :param service_subset: Specifies the named subset to use for the failover target. If empty, the default subset for the requested service name is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#service_subset ConfigEntryServiceResolver#service_subset}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d43578245eaecadb59a500929089794964f72dd48b07dd30394e509a9a0bf0b4)
            check_type(argname="argument datacenter", value=datacenter, expected_type=type_hints["datacenter"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument peer", value=peer, expected_type=type_hints["peer"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument service_subset", value=service_subset, expected_type=type_hints["service_subset"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if datacenter is not None:
            self._values["datacenter"] = datacenter
        if namespace is not None:
            self._values["namespace"] = namespace
        if partition is not None:
            self._values["partition"] = partition
        if peer is not None:
            self._values["peer"] = peer
        if service is not None:
            self._values["service"] = service
        if service_subset is not None:
            self._values["service_subset"] = service_subset

    @builtins.property
    def datacenter(self) -> typing.Optional[builtins.str]:
        '''Specifies the WAN federated datacenter to use for the failover target. If empty, the current datacenter is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#datacenter ConfigEntryServiceResolver#datacenter}
        '''
        result = self._values.get("datacenter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Specifies the namespace to use for the failover target. If empty, the default namespace is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#namespace ConfigEntryServiceResolver#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''Specifies the admin partition within the same datacenter to use for the failover target.

        If empty, the default partition is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#partition ConfigEntryServiceResolver#partition}
        '''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def peer(self) -> typing.Optional[builtins.str]:
        '''Specifies the destination cluster peer to resolve the target service name from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#peer ConfigEntryServiceResolver#peer}
        '''
        result = self._values.get("peer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''Specifies the service name to use for the failover target. If empty, the current service name is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#service ConfigEntryServiceResolver#service}
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_subset(self) -> typing.Optional[builtins.str]:
        '''Specifies the named subset to use for the failover target.

        If empty, the default subset for the requested service name is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#service_subset ConfigEntryServiceResolver#service_subset}
        '''
        result = self._values.get("service_subset")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceResolverFailoverTargets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceResolverFailoverTargetsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverFailoverTargetsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4e4c6f6c340f3d5320754401bd86342d4b906620bf368e1bd1720aeee07c0354)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceResolverFailoverTargetsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e618d404d83e20d80f0b4d5c0e399c189b2218135ac6fc7dfb3b2b7611b05384)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceResolverFailoverTargetsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__882a023bd3be1dfaccf111a963a91bfa4f24c2f89e01cfe47b6143a777480a6a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a32241991ff2ffe519282ed042c83bf15e1ff5f41a7f4fa8a0b1922aa9c89068)
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
            type_hints = typing.get_type_hints(_typecheckingstub__edd5c824eed1d31e4242bf9c66fcb9388af287ebb4e2229e70b271f94ed61d2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverFailoverTargets]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverFailoverTargets]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverFailoverTargets]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ad3d01281f9714d1a99d24f8c75b6493bcef5e3caa4eed00c15e96610ecdc17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceResolverFailoverTargetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverFailoverTargetsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0badfbde83c63ea0a3363b0da30c4c3294cd7b52d6ec85bc06a1bd006a8ee1be)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDatacenter")
    def reset_datacenter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatacenter", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPartition")
    def reset_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartition", []))

    @jsii.member(jsii_name="resetPeer")
    def reset_peer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeer", []))

    @jsii.member(jsii_name="resetService")
    def reset_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetService", []))

    @jsii.member(jsii_name="resetServiceSubset")
    def reset_service_subset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceSubset", []))

    @builtins.property
    @jsii.member(jsii_name="datacenterInput")
    def datacenter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datacenterInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="partitionInput")
    def partition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "partitionInput"))

    @builtins.property
    @jsii.member(jsii_name="peerInput")
    def peer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "peerInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceSubsetInput")
    def service_subset_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceSubsetInput"))

    @builtins.property
    @jsii.member(jsii_name="datacenter")
    def datacenter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datacenter"))

    @datacenter.setter
    def datacenter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5732e4e927a7626f1ac9d33a3767c040bad4c3840b64ee984bbd3a72c5321566)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__773ffd503e61f0a74d785ca1d17aed7fa2c20997d4a31de22e35aee23ce2c916)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partition")
    def partition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partition"))

    @partition.setter
    def partition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac9da86ff866ba37242137598f5d69bd80da271ea82c027f499276d08d88e3d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="peer")
    def peer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "peer"))

    @peer.setter
    def peer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b82fc1aa25f5771bbc90b78148c7f3ee5067a11c86926b476e325ae146033f13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "peer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d9911a1449c46bfd8e9942f69941b804c5d51edffbd92610353f427ba7145ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceSubset")
    def service_subset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceSubset"))

    @service_subset.setter
    def service_subset(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3322413d1814f58e2d45145ab7cf14807b2213c3e7d4bf64df74a0f714eadff1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceSubset", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverFailoverTargets]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverFailoverTargets]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverFailoverTargets]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76ce4dfd5b6a732cfb3f78263cb33f48376bdc319ec1fb8feadeebef4a1cb3fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancer",
    jsii_struct_bases=[],
    name_mapping={
        "hash_policies": "hashPolicies",
        "least_request_config": "leastRequestConfig",
        "policy": "policy",
        "ring_hash_config": "ringHashConfig",
    },
)
class ConfigEntryServiceResolverLoadBalancer:
    def __init__(
        self,
        *,
        hash_policies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverLoadBalancerHashPolicies", typing.Dict[builtins.str, typing.Any]]]]] = None,
        least_request_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverLoadBalancerLeastRequestConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy: typing.Optional[builtins.str] = None,
        ring_hash_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverLoadBalancerRingHashConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param hash_policies: hash_policies block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#hash_policies ConfigEntryServiceResolver#hash_policies}
        :param least_request_config: least_request_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#least_request_config ConfigEntryServiceResolver#least_request_config}
        :param policy: Specifies the type of load balancing policy for selecting a host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#policy ConfigEntryServiceResolver#policy}
        :param ring_hash_config: ring_hash_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#ring_hash_config ConfigEntryServiceResolver#ring_hash_config}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__785184811e3ce743bfecb39f66f06c1839dd93cec7a9bbc01c9698782cb1556d)
            check_type(argname="argument hash_policies", value=hash_policies, expected_type=type_hints["hash_policies"])
            check_type(argname="argument least_request_config", value=least_request_config, expected_type=type_hints["least_request_config"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument ring_hash_config", value=ring_hash_config, expected_type=type_hints["ring_hash_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if hash_policies is not None:
            self._values["hash_policies"] = hash_policies
        if least_request_config is not None:
            self._values["least_request_config"] = least_request_config
        if policy is not None:
            self._values["policy"] = policy
        if ring_hash_config is not None:
            self._values["ring_hash_config"] = ring_hash_config

    @builtins.property
    def hash_policies(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancerHashPolicies"]]]:
        '''hash_policies block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#hash_policies ConfigEntryServiceResolver#hash_policies}
        '''
        result = self._values.get("hash_policies")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancerHashPolicies"]]], result)

    @builtins.property
    def least_request_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancerLeastRequestConfig"]]]:
        '''least_request_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#least_request_config ConfigEntryServiceResolver#least_request_config}
        '''
        result = self._values.get("least_request_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancerLeastRequestConfig"]]], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''Specifies the type of load balancing policy for selecting a host.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#policy ConfigEntryServiceResolver#policy}
        '''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ring_hash_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancerRingHashConfig"]]]:
        '''ring_hash_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#ring_hash_config ConfigEntryServiceResolver#ring_hash_config}
        '''
        result = self._values.get("ring_hash_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancerRingHashConfig"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceResolverLoadBalancer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerHashPolicies",
    jsii_struct_bases=[],
    name_mapping={
        "cookie_config": "cookieConfig",
        "field": "field",
        "field_value": "fieldValue",
        "source_ip": "sourceIp",
        "terminal": "terminal",
    },
)
class ConfigEntryServiceResolverLoadBalancerHashPolicies:
    def __init__(
        self,
        *,
        cookie_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        field: typing.Optional[builtins.str] = None,
        field_value: typing.Optional[builtins.str] = None,
        source_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        terminal: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param cookie_config: cookie_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#cookie_config ConfigEntryServiceResolver#cookie_config}
        :param field: Specifies the attribute type to hash on. You cannot specify the Field parameter if SourceIP is also configured. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#field ConfigEntryServiceResolver#field}
        :param field_value: Specifies the value to hash, such as a header name, cookie name, or a URL query parameter name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#field_value ConfigEntryServiceResolver#field_value}
        :param source_ip: Determines if the hash type should be source IP address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#source_ip ConfigEntryServiceResolver#source_ip}
        :param terminal: Determines if Consul should stop computing the hash when multiple hash policies are present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#terminal ConfigEntryServiceResolver#terminal}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf216f45f597388ebe92324aa4ba28bf2a62543200dde9e7759f7ccec1921727)
            check_type(argname="argument cookie_config", value=cookie_config, expected_type=type_hints["cookie_config"])
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument field_value", value=field_value, expected_type=type_hints["field_value"])
            check_type(argname="argument source_ip", value=source_ip, expected_type=type_hints["source_ip"])
            check_type(argname="argument terminal", value=terminal, expected_type=type_hints["terminal"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cookie_config is not None:
            self._values["cookie_config"] = cookie_config
        if field is not None:
            self._values["field"] = field
        if field_value is not None:
            self._values["field_value"] = field_value
        if source_ip is not None:
            self._values["source_ip"] = source_ip
        if terminal is not None:
            self._values["terminal"] = terminal

    @builtins.property
    def cookie_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig"]]]:
        '''cookie_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#cookie_config ConfigEntryServiceResolver#cookie_config}
        '''
        result = self._values.get("cookie_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig"]]], result)

    @builtins.property
    def field(self) -> typing.Optional[builtins.str]:
        '''Specifies the attribute type to hash on. You cannot specify the Field parameter if SourceIP is also configured.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#field ConfigEntryServiceResolver#field}
        '''
        result = self._values.get("field")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def field_value(self) -> typing.Optional[builtins.str]:
        '''Specifies the value to hash, such as a header name, cookie name, or a URL query parameter name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#field_value ConfigEntryServiceResolver#field_value}
        '''
        result = self._values.get("field_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_ip(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Determines if the hash type should be source IP address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#source_ip ConfigEntryServiceResolver#source_ip}
        '''
        result = self._values.get("source_ip")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def terminal(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Determines if Consul should stop computing the hash when multiple hash policies are present.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#terminal ConfigEntryServiceResolver#terminal}
        '''
        result = self._values.get("terminal")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceResolverLoadBalancerHashPolicies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig",
    jsii_struct_bases=[],
    name_mapping={"path": "path", "session": "session", "ttl": "ttl"},
)
class ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig:
    def __init__(
        self,
        *,
        path: typing.Optional[builtins.str] = None,
        session: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ttl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param path: Specifies the path to set for the cookie. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#path ConfigEntryServiceResolver#path}
        :param session: Directs Consul to generate a session cookie with no expiration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#session ConfigEntryServiceResolver#session}
        :param ttl: Specifies the TTL for generated cookies. Cannot be specified for session cookies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#ttl ConfigEntryServiceResolver#ttl}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__520c29a1858ef4c40eb33b9a08add2b4209d9272a94479d99f7ac49526dbfa8c)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument session", value=session, expected_type=type_hints["session"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if path is not None:
            self._values["path"] = path
        if session is not None:
            self._values["session"] = session
        if ttl is not None:
            self._values["ttl"] = ttl

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Specifies the path to set for the cookie.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#path ConfigEntryServiceResolver#path}
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Directs Consul to generate a session cookie with no expiration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#session ConfigEntryServiceResolver#session}
        '''
        result = self._values.get("session")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ttl(self) -> typing.Optional[builtins.str]:
        '''Specifies the TTL for generated cookies. Cannot be specified for session cookies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#ttl ConfigEntryServiceResolver#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bbd0fb70affa5b2216be881483e743f517e8a6c4e0e3d355a34144da204f7d94)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc2e55896ee8e4ac948073c57fa6d2660082178ceaf2111cc2ced0449ba20857)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac244c43d18e8af299b77e93fa3c96d80b7fd900b4bc31f82b83fbefdb463b58)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8ab0e8bafa3a30f4e8ba0babd7f7db3244b758aaaae9ced300f221e1f67b56f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__61f85549f1c14d7667fd90c97645acee6f0a443aaee13e6daf228f09b5294a5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cfc18545f9ce59fd61b5d7e8214e531d64a97bfb02960f5c122cb24f117beca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__61efd3974dcde4cd3ffe0dbf93c008357d7ebcb75c3bbfdd516bc5b0f8179b7d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetSession")
    def reset_session(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSession", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionInput")
    def session_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sessionInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25e96ed11056bc41dac99ef03923000ce4aeb68f249b3cba94981a4cc4ca4071)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="session")
    def session(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "session"))

    @session.setter
    def session(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0959bebf54c4453fc5ff077cd7ff6d5b10f81cde265666493537c2cf27403c70)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "session", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6fbd2f7295781e7d4edf99e92df98b63bcb44a2d0299e11291f543c196fc723)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba086ad951235bf7889e3fd01a7b4f50d9511e4ce89c7d925fbf33d274b10da8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceResolverLoadBalancerHashPoliciesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerHashPoliciesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__197e780c7e2dab806c0d5b41bcc028fd75eff41df5ffd45c6de089513976bd29)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceResolverLoadBalancerHashPoliciesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0199078feebcb9a21b8b902ce5b76086b6a564cf31f447b873472dffbcb55fe5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceResolverLoadBalancerHashPoliciesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85d6b08eb97c0f7d95d968eaf0fb39b39437fe5925e37cc1ed39125679999e0c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__860e40d00e475b92a56f61f51d0e67e6c9c6286049e03cccbb8e3c4699859e21)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f8f3ec5cc1c9dba4fb6479dec2a7e012df1c502d7bc99513a17b2bf3aa36efaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerHashPolicies]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerHashPolicies]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerHashPolicies]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0b99a0f97d912c8c809bb886985236d5eacbeb996320066cd8c68b39dd4a332)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceResolverLoadBalancerHashPoliciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerHashPoliciesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__18852a92871b31dbf206c71aea076412003a516a72eb89004e4f5dfc1a59ed1d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCookieConfig")
    def put_cookie_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f9f11dc2c8da6ca58e46e9f1698fe95af1f73068b612ebb1f770026c625fc45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCookieConfig", [value]))

    @jsii.member(jsii_name="resetCookieConfig")
    def reset_cookie_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCookieConfig", []))

    @jsii.member(jsii_name="resetField")
    def reset_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetField", []))

    @jsii.member(jsii_name="resetFieldValue")
    def reset_field_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFieldValue", []))

    @jsii.member(jsii_name="resetSourceIp")
    def reset_source_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceIp", []))

    @jsii.member(jsii_name="resetTerminal")
    def reset_terminal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminal", []))

    @builtins.property
    @jsii.member(jsii_name="cookieConfig")
    def cookie_config(
        self,
    ) -> ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfigList:
        return typing.cast(ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfigList, jsii.get(self, "cookieConfig"))

    @builtins.property
    @jsii.member(jsii_name="cookieConfigInput")
    def cookie_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig]]], jsii.get(self, "cookieConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="fieldInput")
    def field_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fieldInput"))

    @builtins.property
    @jsii.member(jsii_name="fieldValueInput")
    def field_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fieldValueInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceIpInput")
    def source_ip_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sourceIpInput"))

    @builtins.property
    @jsii.member(jsii_name="terminalInput")
    def terminal_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "terminalInput"))

    @builtins.property
    @jsii.member(jsii_name="field")
    def field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "field"))

    @field.setter
    def field(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c070975e257cb706c7185df2e898750f6a126973b938c57bb628988206207d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "field", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fieldValue")
    def field_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fieldValue"))

    @field_value.setter
    def field_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__694d7e04da2b4b3830ad8ac885ea455918c6af20342de5695b84789a1986f1ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fieldValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceIp")
    def source_ip(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "sourceIp"))

    @source_ip.setter
    def source_ip(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47b3efbdd84164b8a9914b7d0728a28e4ff0db397dc099df887af930be94d280)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terminal")
    def terminal(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "terminal"))

    @terminal.setter
    def terminal(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aae76a59694a3ecaeb0c7d0c37d3a006bd504eb6f76628b085234f4d3ccfc31e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terminal", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerHashPolicies]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerHashPolicies]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerHashPolicies]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d0670b0a17b66c79cbec081881c15176da2e3fe2c4602bd9f6e924fe27685ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerLeastRequestConfig",
    jsii_struct_bases=[],
    name_mapping={"choice_count": "choiceCount"},
)
class ConfigEntryServiceResolverLoadBalancerLeastRequestConfig:
    def __init__(self, *, choice_count: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param choice_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#choice_count ConfigEntryServiceResolver#choice_count}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7730de645dc46c9c7f14efa2f90370706f6bfa70fe5030f29b6a63d1b84efb92)
            check_type(argname="argument choice_count", value=choice_count, expected_type=type_hints["choice_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if choice_count is not None:
            self._values["choice_count"] = choice_count

    @builtins.property
    def choice_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#choice_count ConfigEntryServiceResolver#choice_count}.'''
        result = self._values.get("choice_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceResolverLoadBalancerLeastRequestConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceResolverLoadBalancerLeastRequestConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerLeastRequestConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__912d4ba0ec1975f288b3ec1bc19b2696b7f5cc20d3d461aa591d5f16edbf4d56)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceResolverLoadBalancerLeastRequestConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c1a9745b8d0ecac2c8bbc421dfa2408e1fc7c4b8a894b28e3e9b7ae09f69659)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceResolverLoadBalancerLeastRequestConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12cacd31267876c4108ead95b5aa5d47abbaf8c869117dd6ba63d487d9f02361)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd28f674637a8b2553c625f639682aae4997ed35d17db7e865709d02c2d13d71)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b67677b1c26c557ef94ec91e06a7f89379e6b727f644bdebb1c12fa7ac07d09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerLeastRequestConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerLeastRequestConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerLeastRequestConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77389b441d12fff9429014a692a435c8c1786827e9c0991dfbb9e519900e54a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceResolverLoadBalancerLeastRequestConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerLeastRequestConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab52adbc8edd57732a3bba734c0d412bf0d659ef58f8fe1687a5de56342a4863)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetChoiceCount")
    def reset_choice_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChoiceCount", []))

    @builtins.property
    @jsii.member(jsii_name="choiceCountInput")
    def choice_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "choiceCountInput"))

    @builtins.property
    @jsii.member(jsii_name="choiceCount")
    def choice_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "choiceCount"))

    @choice_count.setter
    def choice_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52c33f810e373e28435549584b5eadc8b931676e7207ea1e708113d84a1bbc83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "choiceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerLeastRequestConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerLeastRequestConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerLeastRequestConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d373c36a1814082e49938914f00476cb7d4a88875d678ef32f72976d631329d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceResolverLoadBalancerList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c0e8d196b38b34d6d71be584552ef58a603bb2ad483dd803b9d27d68ef27dde7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceResolverLoadBalancerOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eab5d1a50b7497c1af8248e4cd99be25658e98e25c56233ffb6ff6b64466279c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceResolverLoadBalancerOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faf78771c6b4a1ea3938c1746cf314873f0178e4d2ef00f7820a28e4a98536c3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c369c6993e2d0a4075c7332a96f3c2d19d35bb7174622510a04651eb915ee5bb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b6b6d13399e6c417dc5d0efeff7897430f3e19aa77f2c094863e1a8b17d1a723)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancer]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancer]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancer]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b06c67c050f3ab57c7045d6f2f57738e695ecbef8bec6fae3863717b7f55fbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceResolverLoadBalancerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb9e0c716c0d3195124cca9aa58271fc29921d47d8310404b46a513f3e0d67d0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putHashPolicies")
    def put_hash_policies(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancerHashPolicies, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a3a24f5214ec08615cb279dcdef51f6db10c012a23909bbf8dfdc58712b19d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putHashPolicies", [value]))

    @jsii.member(jsii_name="putLeastRequestConfig")
    def put_least_request_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancerLeastRequestConfig, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73ba3887d78ff401fe51d38755cae17cbe71eb3d251d948d6c880f02bc07f753)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLeastRequestConfig", [value]))

    @jsii.member(jsii_name="putRingHashConfig")
    def put_ring_hash_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceResolverLoadBalancerRingHashConfig", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a72ce1e3c29abd5bbadb3bd9a4bd41fe752ba777e1c8f272b84f7efd29c2cbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRingHashConfig", [value]))

    @jsii.member(jsii_name="resetHashPolicies")
    def reset_hash_policies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHashPolicies", []))

    @jsii.member(jsii_name="resetLeastRequestConfig")
    def reset_least_request_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLeastRequestConfig", []))

    @jsii.member(jsii_name="resetPolicy")
    def reset_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicy", []))

    @jsii.member(jsii_name="resetRingHashConfig")
    def reset_ring_hash_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRingHashConfig", []))

    @builtins.property
    @jsii.member(jsii_name="hashPolicies")
    def hash_policies(self) -> ConfigEntryServiceResolverLoadBalancerHashPoliciesList:
        return typing.cast(ConfigEntryServiceResolverLoadBalancerHashPoliciesList, jsii.get(self, "hashPolicies"))

    @builtins.property
    @jsii.member(jsii_name="leastRequestConfig")
    def least_request_config(
        self,
    ) -> ConfigEntryServiceResolverLoadBalancerLeastRequestConfigList:
        return typing.cast(ConfigEntryServiceResolverLoadBalancerLeastRequestConfigList, jsii.get(self, "leastRequestConfig"))

    @builtins.property
    @jsii.member(jsii_name="ringHashConfig")
    def ring_hash_config(
        self,
    ) -> "ConfigEntryServiceResolverLoadBalancerRingHashConfigList":
        return typing.cast("ConfigEntryServiceResolverLoadBalancerRingHashConfigList", jsii.get(self, "ringHashConfig"))

    @builtins.property
    @jsii.member(jsii_name="hashPoliciesInput")
    def hash_policies_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerHashPolicies]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerHashPolicies]]], jsii.get(self, "hashPoliciesInput"))

    @builtins.property
    @jsii.member(jsii_name="leastRequestConfigInput")
    def least_request_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerLeastRequestConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerLeastRequestConfig]]], jsii.get(self, "leastRequestConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property
    @jsii.member(jsii_name="ringHashConfigInput")
    def ring_hash_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancerRingHashConfig"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceResolverLoadBalancerRingHashConfig"]]], jsii.get(self, "ringHashConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__258cb7c39a8424a70846562ad33785c45a5e8e3e3820ed58b7af0bfe6fbbac81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancer]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancer]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancer]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b2bd533c6395ebf21be54af41b8a3fd2c0f09662df5f74c38f32af5946cba03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerRingHashConfig",
    jsii_struct_bases=[],
    name_mapping={
        "maximum_ring_size": "maximumRingSize",
        "minimum_ring_size": "minimumRingSize",
    },
)
class ConfigEntryServiceResolverLoadBalancerRingHashConfig:
    def __init__(
        self,
        *,
        maximum_ring_size: typing.Optional[jsii.Number] = None,
        minimum_ring_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param maximum_ring_size: Determines the maximum number of entries in the hash ring. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#maximum_ring_size ConfigEntryServiceResolver#maximum_ring_size}
        :param minimum_ring_size: Determines the minimum number of entries in the hash ring. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#minimum_ring_size ConfigEntryServiceResolver#minimum_ring_size}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dde521be14c757d476dc4696c0c56f23e95d8c0278cd61497fd71e39ca847e55)
            check_type(argname="argument maximum_ring_size", value=maximum_ring_size, expected_type=type_hints["maximum_ring_size"])
            check_type(argname="argument minimum_ring_size", value=minimum_ring_size, expected_type=type_hints["minimum_ring_size"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if maximum_ring_size is not None:
            self._values["maximum_ring_size"] = maximum_ring_size
        if minimum_ring_size is not None:
            self._values["minimum_ring_size"] = minimum_ring_size

    @builtins.property
    def maximum_ring_size(self) -> typing.Optional[jsii.Number]:
        '''Determines the maximum number of entries in the hash ring.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#maximum_ring_size ConfigEntryServiceResolver#maximum_ring_size}
        '''
        result = self._values.get("maximum_ring_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minimum_ring_size(self) -> typing.Optional[jsii.Number]:
        '''Determines the minimum number of entries in the hash ring.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#minimum_ring_size ConfigEntryServiceResolver#minimum_ring_size}
        '''
        result = self._values.get("minimum_ring_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceResolverLoadBalancerRingHashConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceResolverLoadBalancerRingHashConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerRingHashConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__69fe7a5e9b222bff37dc310fb19d47adaf3c663acdfd87952072542432a8984f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceResolverLoadBalancerRingHashConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bd4f10062186226aaebf0786759774dd913de524e05f2ca33a494833d78467b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceResolverLoadBalancerRingHashConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35d725a8741fe3ba351d5d42185c673495c2e67cef8fc412bffbf527819f198c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__babad4bb26e3a2cac62ff02151d0deb868d2e7df7fcb1b9c28a7c2b804acc2fb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4e157b4b87cfc492e4f414c8163cb98c31e1575b998a00ab23d1daf942710201)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerRingHashConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerRingHashConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerRingHashConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15e5674ebb36ea119a42bebd3662f1c037c2561ea83857768b3f8c91be2b210c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceResolverLoadBalancerRingHashConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverLoadBalancerRingHashConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__154ae9041739f420aa940704e21bd15db9ce7cfd2bb81a30bc21087a8b70bdb5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetMaximumRingSize")
    def reset_maximum_ring_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximumRingSize", []))

    @jsii.member(jsii_name="resetMinimumRingSize")
    def reset_minimum_ring_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumRingSize", []))

    @builtins.property
    @jsii.member(jsii_name="maximumRingSizeInput")
    def maximum_ring_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maximumRingSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumRingSizeInput")
    def minimum_ring_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minimumRingSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="maximumRingSize")
    def maximum_ring_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maximumRingSize"))

    @maximum_ring_size.setter
    def maximum_ring_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b93982ef8b7326b6c3b792579990421bfd815efdd233179783f7bbb44f51c83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maximumRingSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minimumRingSize")
    def minimum_ring_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minimumRingSize"))

    @minimum_ring_size.setter
    def minimum_ring_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfdcfbcbed51353543a0b98dc37469e618816aea812a3227270216cd97a8f08f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimumRingSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerRingHashConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerRingHashConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerRingHashConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__daef07ad1803867c9735db4bcb8d1c8ad247eaa00a16435cb9da5e78e64e5571)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverRedirect",
    jsii_struct_bases=[],
    name_mapping={
        "datacenter": "datacenter",
        "namespace": "namespace",
        "partition": "partition",
        "peer": "peer",
        "sameness_group": "samenessGroup",
        "service": "service",
        "service_subset": "serviceSubset",
    },
)
class ConfigEntryServiceResolverRedirect:
    def __init__(
        self,
        *,
        datacenter: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        peer: typing.Optional[builtins.str] = None,
        sameness_group: typing.Optional[builtins.str] = None,
        service: typing.Optional[builtins.str] = None,
        service_subset: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param datacenter: Specifies the datacenter at the redirect’s destination that resolves local upstream requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#datacenter ConfigEntryServiceResolver#datacenter}
        :param namespace: Specifies the namespace at the redirect’s destination that resolves local upstream requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#namespace ConfigEntryServiceResolver#namespace}
        :param partition: Specifies the admin partition at the redirect’s destination that resolves local upstream requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#partition ConfigEntryServiceResolver#partition}
        :param peer: Specifies the cluster with an active cluster peering connection at the redirect’s destination that resolves local upstream requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#peer ConfigEntryServiceResolver#peer}
        :param sameness_group: Specifies the sameness group at the redirect’s destination that resolves local upstream requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#sameness_group ConfigEntryServiceResolver#sameness_group}
        :param service: Specifies the name of a service at the redirect’s destination that resolves local upstream requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#service ConfigEntryServiceResolver#service}
        :param service_subset: Specifies the name of a subset of services at the redirect’s destination that resolves local upstream requests. If empty, the default subset is used. If specified, you must also specify at least one of the following in the same Redirect map: Service, Namespace, andDatacenter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#service_subset ConfigEntryServiceResolver#service_subset}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7f55d87c9408a50deb1789c69d81b0d675e7b253aa3714da8dd090a4497d36b)
            check_type(argname="argument datacenter", value=datacenter, expected_type=type_hints["datacenter"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument peer", value=peer, expected_type=type_hints["peer"])
            check_type(argname="argument sameness_group", value=sameness_group, expected_type=type_hints["sameness_group"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument service_subset", value=service_subset, expected_type=type_hints["service_subset"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if datacenter is not None:
            self._values["datacenter"] = datacenter
        if namespace is not None:
            self._values["namespace"] = namespace
        if partition is not None:
            self._values["partition"] = partition
        if peer is not None:
            self._values["peer"] = peer
        if sameness_group is not None:
            self._values["sameness_group"] = sameness_group
        if service is not None:
            self._values["service"] = service
        if service_subset is not None:
            self._values["service_subset"] = service_subset

    @builtins.property
    def datacenter(self) -> typing.Optional[builtins.str]:
        '''Specifies the datacenter at the redirect’s destination that resolves local upstream requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#datacenter ConfigEntryServiceResolver#datacenter}
        '''
        result = self._values.get("datacenter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Specifies the namespace at the redirect’s destination that resolves local upstream requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#namespace ConfigEntryServiceResolver#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''Specifies the admin partition at the redirect’s destination that resolves local upstream requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#partition ConfigEntryServiceResolver#partition}
        '''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def peer(self) -> typing.Optional[builtins.str]:
        '''Specifies the cluster with an active cluster peering connection at the redirect’s destination that resolves local upstream requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#peer ConfigEntryServiceResolver#peer}
        '''
        result = self._values.get("peer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sameness_group(self) -> typing.Optional[builtins.str]:
        '''Specifies the sameness group at the redirect’s destination that resolves local upstream requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#sameness_group ConfigEntryServiceResolver#sameness_group}
        '''
        result = self._values.get("sameness_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of a service at the redirect’s destination that resolves local upstream requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#service ConfigEntryServiceResolver#service}
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_subset(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of a subset of services at the redirect’s destination that resolves local upstream requests.

        If empty, the default subset is used. If specified, you must also specify at least one of the following in the same Redirect map: Service, Namespace, andDatacenter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#service_subset ConfigEntryServiceResolver#service_subset}
        '''
        result = self._values.get("service_subset")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceResolverRedirect(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceResolverRedirectList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverRedirectList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9f5d554f1bb4201b06d90ac6e4ae11818de1ed33a1538a9206cd55eddde3b04)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceResolverRedirectOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d610574f97c50bfa662e83749bf5bac0ef5fc6f9d02e107285fe997798b96c5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceResolverRedirectOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e2d5c4b9d58317d61307d410b49c394cbc49db3b985e6b9e2442c17b45e6a16)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d2a1fa6094d1c95d6c1ee670887fb2419eddb0f5dd926e758032e6fc6f06eae)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9a812f711728660104a892ae9acb9da7b0b3ca2e951c4c1f53c0a0eb02e41e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverRedirect]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverRedirect]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverRedirect]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b38d2385ce0c2d66cb7f0a9ff013e0e642a59f2ac7eab1109fd13b6fbcfc9d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceResolverRedirectOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverRedirectOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__45a06c5a50eb72bbced4324b7dfb31a31718eaac23af942e8d61ac20c8c13912)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDatacenter")
    def reset_datacenter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatacenter", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPartition")
    def reset_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartition", []))

    @jsii.member(jsii_name="resetPeer")
    def reset_peer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeer", []))

    @jsii.member(jsii_name="resetSamenessGroup")
    def reset_sameness_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSamenessGroup", []))

    @jsii.member(jsii_name="resetService")
    def reset_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetService", []))

    @jsii.member(jsii_name="resetServiceSubset")
    def reset_service_subset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceSubset", []))

    @builtins.property
    @jsii.member(jsii_name="datacenterInput")
    def datacenter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datacenterInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="partitionInput")
    def partition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "partitionInput"))

    @builtins.property
    @jsii.member(jsii_name="peerInput")
    def peer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "peerInput"))

    @builtins.property
    @jsii.member(jsii_name="samenessGroupInput")
    def sameness_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "samenessGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceSubsetInput")
    def service_subset_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceSubsetInput"))

    @builtins.property
    @jsii.member(jsii_name="datacenter")
    def datacenter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datacenter"))

    @datacenter.setter
    def datacenter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15cc3d948ca36351b1f8e04b895767171d9c9be805ab832bfab77442a841b3bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6ab2476a7a0c8efd4eec4e26e386164aece142c2f395b7630c9dfb015fa654f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partition")
    def partition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partition"))

    @partition.setter
    def partition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5aab30620ff614e04d2861e5fe9a34ced69a1bd61aa43c11b7e3ae3116cb667)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="peer")
    def peer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "peer"))

    @peer.setter
    def peer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be35673844348c88e52910982d61caea5b778022a91ee1f457b934e5f2848b28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "peer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="samenessGroup")
    def sameness_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "samenessGroup"))

    @sameness_group.setter
    def sameness_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a19b433dae567bb4b7c0cdf52808c6455e04dd0d936f36b07d054518cb5a767f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samenessGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ef22b98b1d53dc9ae388770b05f05c888938669bde96df24b801e6ff2877402)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceSubset")
    def service_subset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceSubset"))

    @service_subset.setter
    def service_subset(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__910f30e49224c0116e1a5dcbd849ce9e86fd5a86396478d439a25dc56ec6b358)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceSubset", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverRedirect]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverRedirect]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverRedirect]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6be3990bce47618cbd8628bab0c31e3b9ef602e4db0dec009f91eb03797ccee6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverSubsets",
    jsii_struct_bases=[],
    name_mapping={"filter": "filter", "name": "name", "only_passing": "onlyPassing"},
)
class ConfigEntryServiceResolverSubsets:
    def __init__(
        self,
        *,
        filter: builtins.str,
        name: builtins.str,
        only_passing: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        '''
        :param filter: Specifies an expression that filters the DNS elements of service instances that belong to the subset. If empty, all healthy instances of a service are returned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#filter ConfigEntryServiceResolver#filter}
        :param name: Name of subset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#name ConfigEntryServiceResolver#name}
        :param only_passing: Determines if instances that return a warning from a health check are allowed to resolve a request. When set to false, instances with passing and warning states are considered healthy. When set to true, only instances with a passing health check state are considered healthy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#only_passing ConfigEntryServiceResolver#only_passing}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27aa4158f840fb84ba100c5f73cc02ee4b9d62ebd6c3f580ff5300c6445a80ea)
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument only_passing", value=only_passing, expected_type=type_hints["only_passing"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "filter": filter,
            "name": name,
            "only_passing": only_passing,
        }

    @builtins.property
    def filter(self) -> builtins.str:
        '''Specifies an expression that filters the DNS elements of service instances that belong to the subset.

        If empty, all healthy instances of a service are returned.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#filter ConfigEntryServiceResolver#filter}
        '''
        result = self._values.get("filter")
        assert result is not None, "Required property 'filter' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of subset.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#name ConfigEntryServiceResolver#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def only_passing(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Determines if instances that return a warning from a health check are allowed to resolve a request.

        When set to false, instances with passing and warning states are considered healthy. When set to true, only instances with a passing health check state are considered healthy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_resolver#only_passing ConfigEntryServiceResolver#only_passing}
        '''
        result = self._values.get("only_passing")
        assert result is not None, "Required property 'only_passing' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceResolverSubsets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceResolverSubsetsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverSubsetsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2bc9693184bffbd9fe443ad907cfd3d8a4cfe3bc12570790238ed4d70d8df3a6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceResolverSubsetsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__119441bedcbd39c5eb1013754b204f741c62234cf2644782dc9e503cb2170370)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceResolverSubsetsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4feb035b1e3e26f6d89f05321e8df2a3de219b7841a03fb2ab6568586380868)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6f03014a92c5417762632c74b10c428d57691b6a93c923b6dbac4ff259c1fab7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__090c7c58b1da99f37f7bc5df0498a76e12b02ff9b224e20c6951c7a7371f0b04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverSubsets]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverSubsets]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverSubsets]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f15b278c583508fe27934489d9440192f9c58d07b4007044b6b868089f73d54d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceResolverSubsetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceResolver.ConfigEntryServiceResolverSubsetsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae0b22d7bc0fc57da9759d3ff129847652b1b8a50b63e9a2f9809495a8811a9f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="filterInput")
    def filter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filterInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="onlyPassingInput")
    def only_passing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "onlyPassingInput"))

    @builtins.property
    @jsii.member(jsii_name="filter")
    def filter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filter"))

    @filter.setter
    def filter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03b541bd61c3d3a75af478a45e1fa28345560c3d6644c1951a2141cd76c6acff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "filter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d71094a3f637da58e7f7aabfd3336baf5b45405f4449e770c4cb029e2379ff5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onlyPassing")
    def only_passing(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "onlyPassing"))

    @only_passing.setter
    def only_passing(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__977b7a26437d9e2f1904caec637bcfdfa22f1f553366bf6a9d6b6aaf1ca7f216)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onlyPassing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverSubsets]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverSubsets]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverSubsets]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6896b4091817dfcb5607fa8b1db4fa0d1058f5e03989fcd5cb90a9e3a192e8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ConfigEntryServiceResolver",
    "ConfigEntryServiceResolverConfig",
    "ConfigEntryServiceResolverFailover",
    "ConfigEntryServiceResolverFailoverList",
    "ConfigEntryServiceResolverFailoverOutputReference",
    "ConfigEntryServiceResolverFailoverTargets",
    "ConfigEntryServiceResolverFailoverTargetsList",
    "ConfigEntryServiceResolverFailoverTargetsOutputReference",
    "ConfigEntryServiceResolverLoadBalancer",
    "ConfigEntryServiceResolverLoadBalancerHashPolicies",
    "ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig",
    "ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfigList",
    "ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfigOutputReference",
    "ConfigEntryServiceResolverLoadBalancerHashPoliciesList",
    "ConfigEntryServiceResolverLoadBalancerHashPoliciesOutputReference",
    "ConfigEntryServiceResolverLoadBalancerLeastRequestConfig",
    "ConfigEntryServiceResolverLoadBalancerLeastRequestConfigList",
    "ConfigEntryServiceResolverLoadBalancerLeastRequestConfigOutputReference",
    "ConfigEntryServiceResolverLoadBalancerList",
    "ConfigEntryServiceResolverLoadBalancerOutputReference",
    "ConfigEntryServiceResolverLoadBalancerRingHashConfig",
    "ConfigEntryServiceResolverLoadBalancerRingHashConfigList",
    "ConfigEntryServiceResolverLoadBalancerRingHashConfigOutputReference",
    "ConfigEntryServiceResolverRedirect",
    "ConfigEntryServiceResolverRedirectList",
    "ConfigEntryServiceResolverRedirectOutputReference",
    "ConfigEntryServiceResolverSubsets",
    "ConfigEntryServiceResolverSubsetsList",
    "ConfigEntryServiceResolverSubsetsOutputReference",
]

publication.publish()

def _typecheckingstub__c4e61204e1ca5146b479dae508aa5bdcab93c240d2d8b6c85e044d636ac5d302(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    connect_timeout: typing.Optional[builtins.str] = None,
    default_subset: typing.Optional[builtins.str] = None,
    failover: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverFailover, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    load_balancer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancer, typing.Dict[builtins.str, typing.Any]]]]] = None,
    meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    redirect: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverRedirect, typing.Dict[builtins.str, typing.Any]]]]] = None,
    request_timeout: typing.Optional[builtins.str] = None,
    subsets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverSubsets, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__644888282661491b9541a685a0bcc48dfdb0a311aa490a3b878d8c7339d2b94d(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff93d0b19f3a2a535edf706e3964712cfee593ddba308c95aa578aa780a8c58c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverFailover, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a43c45354a31125790533011c5aa1d026c989410fc777fc22b66cef14a83e1de(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancer, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e3a0526470e726ca34ca06269b6368193a58b2f778e9c2b2872d1250ce46fc2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverRedirect, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c669e45cb44b4fe70ad5ed5373dd8b8b6bc65a445b9e84a9fb67d96cf2f3c82(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverSubsets, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31f46a94b7e34764b2ba92a52873ce4c10c149778e8385d70c35f41acc0c7e2b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd46a66680ff65b6f0712fa19a0f59803d159b022fb7ac78d46aabb9f8d373b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__397f53a08ea3e418a58e08373eea28bc4830f9c886d130475bd94d030a235796(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee75fa01d1e9e64ef2c9fe0bf0fad4c076e740daded2a596f620dbc3858a686d(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23678c1b95d7d8ae582ab473082c00e7dedf59f2f13ee79b126d4ccace505be4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb273b30b9e8f2eff2c6132ea4d14ced0308bf06c2ec708e7d4580c65aecde05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05492437b3557a4be8267c0790b851479ef0061038376e912d23b64c02dcc5c6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cd88cb34ce92ba61c6a9a7ac64f6db84fd1460266821d54d5b8357c2a28b5cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c3c86986bf1ac196e611e841285caf3db9edabae57b668cb1112dd160dae46f(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    connect_timeout: typing.Optional[builtins.str] = None,
    default_subset: typing.Optional[builtins.str] = None,
    failover: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverFailover, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    load_balancer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancer, typing.Dict[builtins.str, typing.Any]]]]] = None,
    meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    redirect: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverRedirect, typing.Dict[builtins.str, typing.Any]]]]] = None,
    request_timeout: typing.Optional[builtins.str] = None,
    subsets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverSubsets, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c93d7fef4476028f513ce9938b70691eedb13d4d64b45a022dbaedf9b62f7006(
    *,
    subset_name: builtins.str,
    datacenters: typing.Optional[typing.Sequence[builtins.str]] = None,
    namespace: typing.Optional[builtins.str] = None,
    sameness_group: typing.Optional[builtins.str] = None,
    service: typing.Optional[builtins.str] = None,
    service_subset: typing.Optional[builtins.str] = None,
    targets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverFailoverTargets, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db037a9fe39bdedd65653d64232ac321875f4f99257ead10f60b3a13f0802a67(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddb0dc77f9bdcfab344bef92ce9faac861cacb3614d80a960d808ca2683157b1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f943bf83e49b172eea8d9273b91a6a1feb6f8bb7cac00336bb3fdc1d1ba5904(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38e633d116f0d87a560fb90afebc88757afd5c4a9682c83083778467ab95acde(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__589c4ed83beb6d130d48645ba64c319b149759ca251f90c5c66f4bfb925f79c8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9280a191b0d62ca17de3e2d47e323fa943487b5b288fa48ba7f5a2d816103db(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverFailover]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25973f6a80a9e3d6d8ec910c672fccea6b9b4a208bec32353fc65a340659b44a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d26c3640fd9e614a338ddf4ca15c554e807e38d726a0d35f776270929d9394ab(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverFailoverTargets, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2816d1472c8428849c551e797caff0d31246920ab5575d82862fe3a0305b92f1(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c3628e9ad82c910b9cfe0c4fef8e3fa2eed9339ba16ade99e785ee4bb731002(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b1de8a7018aa4b61114b15ce53c35615c89c02ab557638ea9647eeddefa0efa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0837d9cff945b4dafc8140296190ac85cceff4c883286243326d7d0583f038db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3be41cf0cb8cf92a199f1e1345a2084dc151d480b6839caefc4d5ccaa3e67acb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7cbdf8506603b419bb59e2e445702e7281984526fd7256da76d7769ad932603(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b1eb823bb0b3df3fdf22dfa8a32c209a8bc03fab9ca5ae2fe67a9af4b4e5552(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverFailover]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d43578245eaecadb59a500929089794964f72dd48b07dd30394e509a9a0bf0b4(
    *,
    datacenter: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    peer: typing.Optional[builtins.str] = None,
    service: typing.Optional[builtins.str] = None,
    service_subset: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e4c6f6c340f3d5320754401bd86342d4b906620bf368e1bd1720aeee07c0354(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e618d404d83e20d80f0b4d5c0e399c189b2218135ac6fc7dfb3b2b7611b05384(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__882a023bd3be1dfaccf111a963a91bfa4f24c2f89e01cfe47b6143a777480a6a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a32241991ff2ffe519282ed042c83bf15e1ff5f41a7f4fa8a0b1922aa9c89068(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edd5c824eed1d31e4242bf9c66fcb9388af287ebb4e2229e70b271f94ed61d2d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ad3d01281f9714d1a99d24f8c75b6493bcef5e3caa4eed00c15e96610ecdc17(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverFailoverTargets]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0badfbde83c63ea0a3363b0da30c4c3294cd7b52d6ec85bc06a1bd006a8ee1be(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5732e4e927a7626f1ac9d33a3767c040bad4c3840b64ee984bbd3a72c5321566(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__773ffd503e61f0a74d785ca1d17aed7fa2c20997d4a31de22e35aee23ce2c916(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac9da86ff866ba37242137598f5d69bd80da271ea82c027f499276d08d88e3d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b82fc1aa25f5771bbc90b78148c7f3ee5067a11c86926b476e325ae146033f13(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d9911a1449c46bfd8e9942f69941b804c5d51edffbd92610353f427ba7145ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3322413d1814f58e2d45145ab7cf14807b2213c3e7d4bf64df74a0f714eadff1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76ce4dfd5b6a732cfb3f78263cb33f48376bdc319ec1fb8feadeebef4a1cb3fa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverFailoverTargets]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__785184811e3ce743bfecb39f66f06c1839dd93cec7a9bbc01c9698782cb1556d(
    *,
    hash_policies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancerHashPolicies, typing.Dict[builtins.str, typing.Any]]]]] = None,
    least_request_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancerLeastRequestConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy: typing.Optional[builtins.str] = None,
    ring_hash_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancerRingHashConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf216f45f597388ebe92324aa4ba28bf2a62543200dde9e7759f7ccec1921727(
    *,
    cookie_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    field: typing.Optional[builtins.str] = None,
    field_value: typing.Optional[builtins.str] = None,
    source_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    terminal: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__520c29a1858ef4c40eb33b9a08add2b4209d9272a94479d99f7ac49526dbfa8c(
    *,
    path: typing.Optional[builtins.str] = None,
    session: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbd0fb70affa5b2216be881483e743f517e8a6c4e0e3d355a34144da204f7d94(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc2e55896ee8e4ac948073c57fa6d2660082178ceaf2111cc2ced0449ba20857(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac244c43d18e8af299b77e93fa3c96d80b7fd900b4bc31f82b83fbefdb463b58(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8ab0e8bafa3a30f4e8ba0babd7f7db3244b758aaaae9ced300f221e1f67b56f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61f85549f1c14d7667fd90c97645acee6f0a443aaee13e6daf228f09b5294a5b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cfc18545f9ce59fd61b5d7e8214e531d64a97bfb02960f5c122cb24f117beca(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61efd3974dcde4cd3ffe0dbf93c008357d7ebcb75c3bbfdd516bc5b0f8179b7d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25e96ed11056bc41dac99ef03923000ce4aeb68f249b3cba94981a4cc4ca4071(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0959bebf54c4453fc5ff077cd7ff6d5b10f81cde265666493537c2cf27403c70(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6fbd2f7295781e7d4edf99e92df98b63bcb44a2d0299e11291f543c196fc723(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba086ad951235bf7889e3fd01a7b4f50d9511e4ce89c7d925fbf33d274b10da8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__197e780c7e2dab806c0d5b41bcc028fd75eff41df5ffd45c6de089513976bd29(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0199078feebcb9a21b8b902ce5b76086b6a564cf31f447b873472dffbcb55fe5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85d6b08eb97c0f7d95d968eaf0fb39b39437fe5925e37cc1ed39125679999e0c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__860e40d00e475b92a56f61f51d0e67e6c9c6286049e03cccbb8e3c4699859e21(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8f3ec5cc1c9dba4fb6479dec2a7e012df1c502d7bc99513a17b2bf3aa36efaf(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0b99a0f97d912c8c809bb886985236d5eacbeb996320066cd8c68b39dd4a332(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerHashPolicies]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18852a92871b31dbf206c71aea076412003a516a72eb89004e4f5dfc1a59ed1d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f9f11dc2c8da6ca58e46e9f1698fe95af1f73068b612ebb1f770026c625fc45(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancerHashPoliciesCookieConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c070975e257cb706c7185df2e898750f6a126973b938c57bb628988206207d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__694d7e04da2b4b3830ad8ac885ea455918c6af20342de5695b84789a1986f1ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47b3efbdd84164b8a9914b7d0728a28e4ff0db397dc099df887af930be94d280(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aae76a59694a3ecaeb0c7d0c37d3a006bd504eb6f76628b085234f4d3ccfc31e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d0670b0a17b66c79cbec081881c15176da2e3fe2c4602bd9f6e924fe27685ba(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerHashPolicies]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7730de645dc46c9c7f14efa2f90370706f6bfa70fe5030f29b6a63d1b84efb92(
    *,
    choice_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__912d4ba0ec1975f288b3ec1bc19b2696b7f5cc20d3d461aa591d5f16edbf4d56(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c1a9745b8d0ecac2c8bbc421dfa2408e1fc7c4b8a894b28e3e9b7ae09f69659(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12cacd31267876c4108ead95b5aa5d47abbaf8c869117dd6ba63d487d9f02361(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd28f674637a8b2553c625f639682aae4997ed35d17db7e865709d02c2d13d71(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b67677b1c26c557ef94ec91e06a7f89379e6b727f644bdebb1c12fa7ac07d09(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77389b441d12fff9429014a692a435c8c1786827e9c0991dfbb9e519900e54a8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerLeastRequestConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab52adbc8edd57732a3bba734c0d412bf0d659ef58f8fe1687a5de56342a4863(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52c33f810e373e28435549584b5eadc8b931676e7207ea1e708113d84a1bbc83(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d373c36a1814082e49938914f00476cb7d4a88875d678ef32f72976d631329d2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerLeastRequestConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0e8d196b38b34d6d71be584552ef58a603bb2ad483dd803b9d27d68ef27dde7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eab5d1a50b7497c1af8248e4cd99be25658e98e25c56233ffb6ff6b64466279c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faf78771c6b4a1ea3938c1746cf314873f0178e4d2ef00f7820a28e4a98536c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c369c6993e2d0a4075c7332a96f3c2d19d35bb7174622510a04651eb915ee5bb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6b6d13399e6c417dc5d0efeff7897430f3e19aa77f2c094863e1a8b17d1a723(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b06c67c050f3ab57c7045d6f2f57738e695ecbef8bec6fae3863717b7f55fbf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancer]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb9e0c716c0d3195124cca9aa58271fc29921d47d8310404b46a513f3e0d67d0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a3a24f5214ec08615cb279dcdef51f6db10c012a23909bbf8dfdc58712b19d7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancerHashPolicies, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73ba3887d78ff401fe51d38755cae17cbe71eb3d251d948d6c880f02bc07f753(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancerLeastRequestConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a72ce1e3c29abd5bbadb3bd9a4bd41fe752ba777e1c8f272b84f7efd29c2cbc(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceResolverLoadBalancerRingHashConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__258cb7c39a8424a70846562ad33785c45a5e8e3e3820ed58b7af0bfe6fbbac81(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b2bd533c6395ebf21be54af41b8a3fd2c0f09662df5f74c38f32af5946cba03(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancer]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dde521be14c757d476dc4696c0c56f23e95d8c0278cd61497fd71e39ca847e55(
    *,
    maximum_ring_size: typing.Optional[jsii.Number] = None,
    minimum_ring_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69fe7a5e9b222bff37dc310fb19d47adaf3c663acdfd87952072542432a8984f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bd4f10062186226aaebf0786759774dd913de524e05f2ca33a494833d78467b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35d725a8741fe3ba351d5d42185c673495c2e67cef8fc412bffbf527819f198c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__babad4bb26e3a2cac62ff02151d0deb868d2e7df7fcb1b9c28a7c2b804acc2fb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e157b4b87cfc492e4f414c8163cb98c31e1575b998a00ab23d1daf942710201(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15e5674ebb36ea119a42bebd3662f1c037c2561ea83857768b3f8c91be2b210c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverLoadBalancerRingHashConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__154ae9041739f420aa940704e21bd15db9ce7cfd2bb81a30bc21087a8b70bdb5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b93982ef8b7326b6c3b792579990421bfd815efdd233179783f7bbb44f51c83(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfdcfbcbed51353543a0b98dc37469e618816aea812a3227270216cd97a8f08f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daef07ad1803867c9735db4bcb8d1c8ad247eaa00a16435cb9da5e78e64e5571(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverLoadBalancerRingHashConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7f55d87c9408a50deb1789c69d81b0d675e7b253aa3714da8dd090a4497d36b(
    *,
    datacenter: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    peer: typing.Optional[builtins.str] = None,
    sameness_group: typing.Optional[builtins.str] = None,
    service: typing.Optional[builtins.str] = None,
    service_subset: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9f5d554f1bb4201b06d90ac6e4ae11818de1ed33a1538a9206cd55eddde3b04(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d610574f97c50bfa662e83749bf5bac0ef5fc6f9d02e107285fe997798b96c5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e2d5c4b9d58317d61307d410b49c394cbc49db3b985e6b9e2442c17b45e6a16(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d2a1fa6094d1c95d6c1ee670887fb2419eddb0f5dd926e758032e6fc6f06eae(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9a812f711728660104a892ae9acb9da7b0b3ca2e951c4c1f53c0a0eb02e41e6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b38d2385ce0c2d66cb7f0a9ff013e0e642a59f2ac7eab1109fd13b6fbcfc9d1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverRedirect]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45a06c5a50eb72bbced4324b7dfb31a31718eaac23af942e8d61ac20c8c13912(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15cc3d948ca36351b1f8e04b895767171d9c9be805ab832bfab77442a841b3bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6ab2476a7a0c8efd4eec4e26e386164aece142c2f395b7630c9dfb015fa654f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5aab30620ff614e04d2861e5fe9a34ced69a1bd61aa43c11b7e3ae3116cb667(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be35673844348c88e52910982d61caea5b778022a91ee1f457b934e5f2848b28(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a19b433dae567bb4b7c0cdf52808c6455e04dd0d936f36b07d054518cb5a767f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ef22b98b1d53dc9ae388770b05f05c888938669bde96df24b801e6ff2877402(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__910f30e49224c0116e1a5dcbd849ce9e86fd5a86396478d439a25dc56ec6b358(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6be3990bce47618cbd8628bab0c31e3b9ef602e4db0dec009f91eb03797ccee6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverRedirect]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27aa4158f840fb84ba100c5f73cc02ee4b9d62ebd6c3f580ff5300c6445a80ea(
    *,
    filter: builtins.str,
    name: builtins.str,
    only_passing: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bc9693184bffbd9fe443ad907cfd3d8a4cfe3bc12570790238ed4d70d8df3a6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__119441bedcbd39c5eb1013754b204f741c62234cf2644782dc9e503cb2170370(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4feb035b1e3e26f6d89f05321e8df2a3de219b7841a03fb2ab6568586380868(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f03014a92c5417762632c74b10c428d57691b6a93c923b6dbac4ff259c1fab7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__090c7c58b1da99f37f7bc5df0498a76e12b02ff9b224e20c6951c7a7371f0b04(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f15b278c583508fe27934489d9440192f9c58d07b4007044b6b868089f73d54d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceResolverSubsets]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae0b22d7bc0fc57da9759d3ff129847652b1b8a50b63e9a2f9809495a8811a9f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03b541bd61c3d3a75af478a45e1fa28345560c3d6644c1951a2141cd76c6acff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d71094a3f637da58e7f7aabfd3336baf5b45405f4449e770c4cb029e2379ff5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__977b7a26437d9e2f1904caec637bcfdfa22f1f553366bf6a9d6b6aaf1ca7f216(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6896b4091817dfcb5607fa8b1db4fa0d1058f5e03989fcd5cb90a9e3a192e8b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceResolverSubsets]],
) -> None:
    """Type checking stubs"""
    pass
