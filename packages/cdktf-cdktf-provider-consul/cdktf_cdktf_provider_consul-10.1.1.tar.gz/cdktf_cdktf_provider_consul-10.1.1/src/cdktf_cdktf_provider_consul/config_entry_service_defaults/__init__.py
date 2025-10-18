r'''
# `consul_config_entry_service_defaults`

Refer to the Terraform Registry for docs: [`consul_config_entry_service_defaults`](https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults).
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


class ConfigEntryServiceDefaults(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaults",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults consul_config_entry_service_defaults}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        expose: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsExpose", typing.Dict[builtins.str, typing.Any]]]],
        name: builtins.str,
        protocol: builtins.str,
        balance_inbound_connections: typing.Optional[builtins.str] = None,
        destination: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsDestination", typing.Dict[builtins.str, typing.Any]]]]] = None,
        envoy_extensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsEnvoyExtensions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        external_sni: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        local_connect_timeout_ms: typing.Optional[jsii.Number] = None,
        local_request_timeout_ms: typing.Optional[jsii.Number] = None,
        max_inbound_connections: typing.Optional[jsii.Number] = None,
        mesh_gateway: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsMeshGateway", typing.Dict[builtins.str, typing.Any]]]]] = None,
        meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        mode: typing.Optional[builtins.str] = None,
        mutual_tls_mode: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        transparent_proxy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsTransparentProxy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        upstream_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults consul_config_entry_service_defaults} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param expose: expose block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#expose ConfigEntryServiceDefaults#expose}
        :param name: Specifies the name of the service you are setting the defaults for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#name ConfigEntryServiceDefaults#name}
        :param protocol: Specifies the default protocol for the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#protocol ConfigEntryServiceDefaults#protocol}
        :param balance_inbound_connections: Specifies the strategy for allocating inbound connections to the service across Envoy proxy threads. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#balance_inbound_connections ConfigEntryServiceDefaults#balance_inbound_connections}
        :param destination: destination block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#destination ConfigEntryServiceDefaults#destination}
        :param envoy_extensions: envoy_extensions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#envoy_extensions ConfigEntryServiceDefaults#envoy_extensions}
        :param external_sni: Specifies the TLS server name indication (SNI) when federating with an external system. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#external_sni ConfigEntryServiceDefaults#external_sni}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#id ConfigEntryServiceDefaults#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param local_connect_timeout_ms: Specifies the number of milliseconds allowed for establishing connections to the local application instance before timing out. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#local_connect_timeout_ms ConfigEntryServiceDefaults#local_connect_timeout_ms}
        :param local_request_timeout_ms: Specifies the timeout for HTTP requests to the local application instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#local_request_timeout_ms ConfigEntryServiceDefaults#local_request_timeout_ms}
        :param max_inbound_connections: Specifies the maximum number of concurrent inbound connections to each service instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_inbound_connections ConfigEntryServiceDefaults#max_inbound_connections}
        :param mesh_gateway: mesh_gateway block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mesh_gateway ConfigEntryServiceDefaults#mesh_gateway}
        :param meta: Specifies a set of custom key-value pairs to add to the Consul KV store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#meta ConfigEntryServiceDefaults#meta}
        :param mode: Specifies a mode for how the service directs inbound and outbound traffic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mode ConfigEntryServiceDefaults#mode}
        :param mutual_tls_mode: Controls whether mutual TLS is required for incoming connections to this service. This setting is only supported for services with transparent proxy enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mutual_tls_mode ConfigEntryServiceDefaults#mutual_tls_mode}
        :param namespace: Specifies the Consul namespace that the configuration entry applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#namespace ConfigEntryServiceDefaults#namespace}
        :param partition: Specifies the name of the name of the Consul admin partition that the configuration entry applies to. Refer to Admin Partitions for additional information. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#partition ConfigEntryServiceDefaults#partition}
        :param transparent_proxy: transparent_proxy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#transparent_proxy ConfigEntryServiceDefaults#transparent_proxy}
        :param upstream_config: upstream_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#upstream_config ConfigEntryServiceDefaults#upstream_config}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__103b5138df57859f622f0e85dd58e8f15aa4ef62b4f6202d4fbf13705e3e7709)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigEntryServiceDefaultsConfig(
            expose=expose,
            name=name,
            protocol=protocol,
            balance_inbound_connections=balance_inbound_connections,
            destination=destination,
            envoy_extensions=envoy_extensions,
            external_sni=external_sni,
            id=id,
            local_connect_timeout_ms=local_connect_timeout_ms,
            local_request_timeout_ms=local_request_timeout_ms,
            max_inbound_connections=max_inbound_connections,
            mesh_gateway=mesh_gateway,
            meta=meta,
            mode=mode,
            mutual_tls_mode=mutual_tls_mode,
            namespace=namespace,
            partition=partition,
            transparent_proxy=transparent_proxy,
            upstream_config=upstream_config,
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
        '''Generates CDKTF code for importing a ConfigEntryServiceDefaults resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ConfigEntryServiceDefaults to import.
        :param import_from_id: The id of the existing ConfigEntryServiceDefaults that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ConfigEntryServiceDefaults to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__488baec34fb666dc15bac618da890ab9554e0aec38f3156eeb6d1bbc86690880)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putDestination")
    def put_destination(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsDestination", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6257b635e58ed9073ae40b2a11d39754e09b12fd9919449f578087256edf51c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDestination", [value]))

    @jsii.member(jsii_name="putEnvoyExtensions")
    def put_envoy_extensions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsEnvoyExtensions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41312dbb2ff66b2b18c6624f295eb4ddd1a320be82cfda52ba88cfa83b366efd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEnvoyExtensions", [value]))

    @jsii.member(jsii_name="putExpose")
    def put_expose(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsExpose", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95edae8672158774ea9f85d8eeb825374031a35a0710b226922c137844385434)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putExpose", [value]))

    @jsii.member(jsii_name="putMeshGateway")
    def put_mesh_gateway(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsMeshGateway", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b64dd2572570a8ef77201ebe329ccfffb41b8516acda75cf5d6821df955e66d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMeshGateway", [value]))

    @jsii.member(jsii_name="putTransparentProxy")
    def put_transparent_proxy(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsTransparentProxy", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91ba5006733111f92c3f6b26b3c1f6825e2f978fa43f707de17e7c64ab0512aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTransparentProxy", [value]))

    @jsii.member(jsii_name="putUpstreamConfig")
    def put_upstream_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfig", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0be20b8da1f36860fc84d4e6ddb13adbf1179abf24b6bcbda496840f60b4e950)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putUpstreamConfig", [value]))

    @jsii.member(jsii_name="resetBalanceInboundConnections")
    def reset_balance_inbound_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBalanceInboundConnections", []))

    @jsii.member(jsii_name="resetDestination")
    def reset_destination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestination", []))

    @jsii.member(jsii_name="resetEnvoyExtensions")
    def reset_envoy_extensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvoyExtensions", []))

    @jsii.member(jsii_name="resetExternalSni")
    def reset_external_sni(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalSni", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLocalConnectTimeoutMs")
    def reset_local_connect_timeout_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocalConnectTimeoutMs", []))

    @jsii.member(jsii_name="resetLocalRequestTimeoutMs")
    def reset_local_request_timeout_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocalRequestTimeoutMs", []))

    @jsii.member(jsii_name="resetMaxInboundConnections")
    def reset_max_inbound_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxInboundConnections", []))

    @jsii.member(jsii_name="resetMeshGateway")
    def reset_mesh_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMeshGateway", []))

    @jsii.member(jsii_name="resetMeta")
    def reset_meta(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMeta", []))

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetMutualTlsMode")
    def reset_mutual_tls_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMutualTlsMode", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPartition")
    def reset_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartition", []))

    @jsii.member(jsii_name="resetTransparentProxy")
    def reset_transparent_proxy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTransparentProxy", []))

    @jsii.member(jsii_name="resetUpstreamConfig")
    def reset_upstream_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpstreamConfig", []))

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
    @jsii.member(jsii_name="destination")
    def destination(self) -> "ConfigEntryServiceDefaultsDestinationList":
        return typing.cast("ConfigEntryServiceDefaultsDestinationList", jsii.get(self, "destination"))

    @builtins.property
    @jsii.member(jsii_name="envoyExtensions")
    def envoy_extensions(self) -> "ConfigEntryServiceDefaultsEnvoyExtensionsList":
        return typing.cast("ConfigEntryServiceDefaultsEnvoyExtensionsList", jsii.get(self, "envoyExtensions"))

    @builtins.property
    @jsii.member(jsii_name="expose")
    def expose(self) -> "ConfigEntryServiceDefaultsExposeList":
        return typing.cast("ConfigEntryServiceDefaultsExposeList", jsii.get(self, "expose"))

    @builtins.property
    @jsii.member(jsii_name="meshGateway")
    def mesh_gateway(self) -> "ConfigEntryServiceDefaultsMeshGatewayList":
        return typing.cast("ConfigEntryServiceDefaultsMeshGatewayList", jsii.get(self, "meshGateway"))

    @builtins.property
    @jsii.member(jsii_name="transparentProxy")
    def transparent_proxy(self) -> "ConfigEntryServiceDefaultsTransparentProxyList":
        return typing.cast("ConfigEntryServiceDefaultsTransparentProxyList", jsii.get(self, "transparentProxy"))

    @builtins.property
    @jsii.member(jsii_name="upstreamConfig")
    def upstream_config(self) -> "ConfigEntryServiceDefaultsUpstreamConfigList":
        return typing.cast("ConfigEntryServiceDefaultsUpstreamConfigList", jsii.get(self, "upstreamConfig"))

    @builtins.property
    @jsii.member(jsii_name="balanceInboundConnectionsInput")
    def balance_inbound_connections_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "balanceInboundConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsDestination"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsDestination"]]], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="envoyExtensionsInput")
    def envoy_extensions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsEnvoyExtensions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsEnvoyExtensions"]]], jsii.get(self, "envoyExtensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="exposeInput")
    def expose_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsExpose"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsExpose"]]], jsii.get(self, "exposeInput"))

    @builtins.property
    @jsii.member(jsii_name="externalSniInput")
    def external_sni_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalSniInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="localConnectTimeoutMsInput")
    def local_connect_timeout_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "localConnectTimeoutMsInput"))

    @builtins.property
    @jsii.member(jsii_name="localRequestTimeoutMsInput")
    def local_request_timeout_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "localRequestTimeoutMsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxInboundConnectionsInput")
    def max_inbound_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxInboundConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="meshGatewayInput")
    def mesh_gateway_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsMeshGateway"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsMeshGateway"]]], jsii.get(self, "meshGatewayInput"))

    @builtins.property
    @jsii.member(jsii_name="metaInput")
    def meta_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "metaInput"))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="mutualTlsModeInput")
    def mutual_tls_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mutualTlsModeInput"))

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
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="transparentProxyInput")
    def transparent_proxy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsTransparentProxy"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsTransparentProxy"]]], jsii.get(self, "transparentProxyInput"))

    @builtins.property
    @jsii.member(jsii_name="upstreamConfigInput")
    def upstream_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfig"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfig"]]], jsii.get(self, "upstreamConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="balanceInboundConnections")
    def balance_inbound_connections(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "balanceInboundConnections"))

    @balance_inbound_connections.setter
    def balance_inbound_connections(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f730fdda2239f58f33863a456e625cc8f6bb3fc69df62e17c01249b3a4a8d0c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "balanceInboundConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="externalSni")
    def external_sni(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalSni"))

    @external_sni.setter
    def external_sni(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e0af6e3975fad1afaa297ee28884a74ea4bcab3da09d0fce2687d72d79261cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "externalSni", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6985c8af1482454a62a0c43a76052e3dab11c285819cedaf6671bd41c00afff0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localConnectTimeoutMs")
    def local_connect_timeout_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "localConnectTimeoutMs"))

    @local_connect_timeout_ms.setter
    def local_connect_timeout_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13b3c0a776460d23971f7ae3a5bf49e48e3473e36352dc54b1a962783723b98d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localConnectTimeoutMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localRequestTimeoutMs")
    def local_request_timeout_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "localRequestTimeoutMs"))

    @local_request_timeout_ms.setter
    def local_request_timeout_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__498e8455f588b4a744b8080859f30fa0a4de1af900bc781f8217a2e535767db3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localRequestTimeoutMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxInboundConnections")
    def max_inbound_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxInboundConnections"))

    @max_inbound_connections.setter
    def max_inbound_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f905ee692913be163dcf489cedab8add9675498e6fb8c57287033e9315019a0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxInboundConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="meta")
    def meta(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "meta"))

    @meta.setter
    def meta(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__398871b5b5ae6e28b8d7e507908908dd54e1112c1105c9115e71945ed6d7ddf1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "meta", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__640cd22463d572d4394b3a4584b67b713dcc392e811303499ede935f86bc3e38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mutualTlsMode")
    def mutual_tls_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mutualTlsMode"))

    @mutual_tls_mode.setter
    def mutual_tls_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc22ffa66c273d55520022f38c5f6aa2abdebd1b79304ca5e056dea5d3f27b1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mutualTlsMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__420967af8246f765995a64120f5ef7f09dd307b7a0c07ac87d215825f42e6f58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb4fb6e8bb7879e69d012ba472ed43846ba60ebdca5fcccba82efb451bc54207)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partition")
    def partition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partition"))

    @partition.setter
    def partition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__906f9e716b2cb4a4bdf68167c898b98cbaddc53a3a8937d46c71ca72151d15a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2355093cba566e5b9ea77f7187e8d157171d439a93abd5ad937c50f4a75b3fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "expose": "expose",
        "name": "name",
        "protocol": "protocol",
        "balance_inbound_connections": "balanceInboundConnections",
        "destination": "destination",
        "envoy_extensions": "envoyExtensions",
        "external_sni": "externalSni",
        "id": "id",
        "local_connect_timeout_ms": "localConnectTimeoutMs",
        "local_request_timeout_ms": "localRequestTimeoutMs",
        "max_inbound_connections": "maxInboundConnections",
        "mesh_gateway": "meshGateway",
        "meta": "meta",
        "mode": "mode",
        "mutual_tls_mode": "mutualTlsMode",
        "namespace": "namespace",
        "partition": "partition",
        "transparent_proxy": "transparentProxy",
        "upstream_config": "upstreamConfig",
    },
)
class ConfigEntryServiceDefaultsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        expose: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsExpose", typing.Dict[builtins.str, typing.Any]]]],
        name: builtins.str,
        protocol: builtins.str,
        balance_inbound_connections: typing.Optional[builtins.str] = None,
        destination: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsDestination", typing.Dict[builtins.str, typing.Any]]]]] = None,
        envoy_extensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsEnvoyExtensions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        external_sni: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        local_connect_timeout_ms: typing.Optional[jsii.Number] = None,
        local_request_timeout_ms: typing.Optional[jsii.Number] = None,
        max_inbound_connections: typing.Optional[jsii.Number] = None,
        mesh_gateway: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsMeshGateway", typing.Dict[builtins.str, typing.Any]]]]] = None,
        meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        mode: typing.Optional[builtins.str] = None,
        mutual_tls_mode: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        transparent_proxy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsTransparentProxy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        upstream_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param expose: expose block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#expose ConfigEntryServiceDefaults#expose}
        :param name: Specifies the name of the service you are setting the defaults for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#name ConfigEntryServiceDefaults#name}
        :param protocol: Specifies the default protocol for the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#protocol ConfigEntryServiceDefaults#protocol}
        :param balance_inbound_connections: Specifies the strategy for allocating inbound connections to the service across Envoy proxy threads. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#balance_inbound_connections ConfigEntryServiceDefaults#balance_inbound_connections}
        :param destination: destination block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#destination ConfigEntryServiceDefaults#destination}
        :param envoy_extensions: envoy_extensions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#envoy_extensions ConfigEntryServiceDefaults#envoy_extensions}
        :param external_sni: Specifies the TLS server name indication (SNI) when federating with an external system. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#external_sni ConfigEntryServiceDefaults#external_sni}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#id ConfigEntryServiceDefaults#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param local_connect_timeout_ms: Specifies the number of milliseconds allowed for establishing connections to the local application instance before timing out. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#local_connect_timeout_ms ConfigEntryServiceDefaults#local_connect_timeout_ms}
        :param local_request_timeout_ms: Specifies the timeout for HTTP requests to the local application instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#local_request_timeout_ms ConfigEntryServiceDefaults#local_request_timeout_ms}
        :param max_inbound_connections: Specifies the maximum number of concurrent inbound connections to each service instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_inbound_connections ConfigEntryServiceDefaults#max_inbound_connections}
        :param mesh_gateway: mesh_gateway block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mesh_gateway ConfigEntryServiceDefaults#mesh_gateway}
        :param meta: Specifies a set of custom key-value pairs to add to the Consul KV store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#meta ConfigEntryServiceDefaults#meta}
        :param mode: Specifies a mode for how the service directs inbound and outbound traffic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mode ConfigEntryServiceDefaults#mode}
        :param mutual_tls_mode: Controls whether mutual TLS is required for incoming connections to this service. This setting is only supported for services with transparent proxy enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mutual_tls_mode ConfigEntryServiceDefaults#mutual_tls_mode}
        :param namespace: Specifies the Consul namespace that the configuration entry applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#namespace ConfigEntryServiceDefaults#namespace}
        :param partition: Specifies the name of the name of the Consul admin partition that the configuration entry applies to. Refer to Admin Partitions for additional information. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#partition ConfigEntryServiceDefaults#partition}
        :param transparent_proxy: transparent_proxy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#transparent_proxy ConfigEntryServiceDefaults#transparent_proxy}
        :param upstream_config: upstream_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#upstream_config ConfigEntryServiceDefaults#upstream_config}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00af784d1d6c1e03b72befbd87250cb7cf5d5be485d5e2346becc6648c2f6cf2)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument expose", value=expose, expected_type=type_hints["expose"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument balance_inbound_connections", value=balance_inbound_connections, expected_type=type_hints["balance_inbound_connections"])
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument envoy_extensions", value=envoy_extensions, expected_type=type_hints["envoy_extensions"])
            check_type(argname="argument external_sni", value=external_sni, expected_type=type_hints["external_sni"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument local_connect_timeout_ms", value=local_connect_timeout_ms, expected_type=type_hints["local_connect_timeout_ms"])
            check_type(argname="argument local_request_timeout_ms", value=local_request_timeout_ms, expected_type=type_hints["local_request_timeout_ms"])
            check_type(argname="argument max_inbound_connections", value=max_inbound_connections, expected_type=type_hints["max_inbound_connections"])
            check_type(argname="argument mesh_gateway", value=mesh_gateway, expected_type=type_hints["mesh_gateway"])
            check_type(argname="argument meta", value=meta, expected_type=type_hints["meta"])
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument mutual_tls_mode", value=mutual_tls_mode, expected_type=type_hints["mutual_tls_mode"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument transparent_proxy", value=transparent_proxy, expected_type=type_hints["transparent_proxy"])
            check_type(argname="argument upstream_config", value=upstream_config, expected_type=type_hints["upstream_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "expose": expose,
            "name": name,
            "protocol": protocol,
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
        if balance_inbound_connections is not None:
            self._values["balance_inbound_connections"] = balance_inbound_connections
        if destination is not None:
            self._values["destination"] = destination
        if envoy_extensions is not None:
            self._values["envoy_extensions"] = envoy_extensions
        if external_sni is not None:
            self._values["external_sni"] = external_sni
        if id is not None:
            self._values["id"] = id
        if local_connect_timeout_ms is not None:
            self._values["local_connect_timeout_ms"] = local_connect_timeout_ms
        if local_request_timeout_ms is not None:
            self._values["local_request_timeout_ms"] = local_request_timeout_ms
        if max_inbound_connections is not None:
            self._values["max_inbound_connections"] = max_inbound_connections
        if mesh_gateway is not None:
            self._values["mesh_gateway"] = mesh_gateway
        if meta is not None:
            self._values["meta"] = meta
        if mode is not None:
            self._values["mode"] = mode
        if mutual_tls_mode is not None:
            self._values["mutual_tls_mode"] = mutual_tls_mode
        if namespace is not None:
            self._values["namespace"] = namespace
        if partition is not None:
            self._values["partition"] = partition
        if transparent_proxy is not None:
            self._values["transparent_proxy"] = transparent_proxy
        if upstream_config is not None:
            self._values["upstream_config"] = upstream_config

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
    def expose(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsExpose"]]:
        '''expose block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#expose ConfigEntryServiceDefaults#expose}
        '''
        result = self._values.get("expose")
        assert result is not None, "Required property 'expose' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsExpose"]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Specifies the name of the service you are setting the defaults for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#name ConfigEntryServiceDefaults#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def protocol(self) -> builtins.str:
        '''Specifies the default protocol for the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#protocol ConfigEntryServiceDefaults#protocol}
        '''
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def balance_inbound_connections(self) -> typing.Optional[builtins.str]:
        '''Specifies the strategy for allocating inbound connections to the service across Envoy proxy threads.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#balance_inbound_connections ConfigEntryServiceDefaults#balance_inbound_connections}
        '''
        result = self._values.get("balance_inbound_connections")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsDestination"]]]:
        '''destination block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#destination ConfigEntryServiceDefaults#destination}
        '''
        result = self._values.get("destination")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsDestination"]]], result)

    @builtins.property
    def envoy_extensions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsEnvoyExtensions"]]]:
        '''envoy_extensions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#envoy_extensions ConfigEntryServiceDefaults#envoy_extensions}
        '''
        result = self._values.get("envoy_extensions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsEnvoyExtensions"]]], result)

    @builtins.property
    def external_sni(self) -> typing.Optional[builtins.str]:
        '''Specifies the TLS server name indication (SNI) when federating with an external system.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#external_sni ConfigEntryServiceDefaults#external_sni}
        '''
        result = self._values.get("external_sni")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#id ConfigEntryServiceDefaults#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local_connect_timeout_ms(self) -> typing.Optional[jsii.Number]:
        '''Specifies the number of milliseconds allowed for establishing connections to the local application instance before timing out.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#local_connect_timeout_ms ConfigEntryServiceDefaults#local_connect_timeout_ms}
        '''
        result = self._values.get("local_connect_timeout_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def local_request_timeout_ms(self) -> typing.Optional[jsii.Number]:
        '''Specifies the timeout for HTTP requests to the local application instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#local_request_timeout_ms ConfigEntryServiceDefaults#local_request_timeout_ms}
        '''
        result = self._values.get("local_request_timeout_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_inbound_connections(self) -> typing.Optional[jsii.Number]:
        '''Specifies the maximum number of concurrent inbound connections to each service instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_inbound_connections ConfigEntryServiceDefaults#max_inbound_connections}
        '''
        result = self._values.get("max_inbound_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def mesh_gateway(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsMeshGateway"]]]:
        '''mesh_gateway block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mesh_gateway ConfigEntryServiceDefaults#mesh_gateway}
        '''
        result = self._values.get("mesh_gateway")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsMeshGateway"]]], result)

    @builtins.property
    def meta(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Specifies a set of custom key-value pairs to add to the Consul KV store.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#meta ConfigEntryServiceDefaults#meta}
        '''
        result = self._values.get("meta")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Specifies a mode for how the service directs inbound and outbound traffic.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mode ConfigEntryServiceDefaults#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mutual_tls_mode(self) -> typing.Optional[builtins.str]:
        '''Controls whether mutual TLS is required for incoming connections to this service.

        This setting is only supported for services with transparent proxy enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mutual_tls_mode ConfigEntryServiceDefaults#mutual_tls_mode}
        '''
        result = self._values.get("mutual_tls_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Specifies the Consul namespace that the configuration entry applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#namespace ConfigEntryServiceDefaults#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of the name of the Consul admin partition that the configuration entry applies to.

        Refer to Admin Partitions for additional information.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#partition ConfigEntryServiceDefaults#partition}
        '''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transparent_proxy(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsTransparentProxy"]]]:
        '''transparent_proxy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#transparent_proxy ConfigEntryServiceDefaults#transparent_proxy}
        '''
        result = self._values.get("transparent_proxy")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsTransparentProxy"]]], result)

    @builtins.property
    def upstream_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfig"]]]:
        '''upstream_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#upstream_config ConfigEntryServiceDefaults#upstream_config}
        '''
        result = self._values.get("upstream_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfig"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsDestination",
    jsii_struct_bases=[],
    name_mapping={"addresses": "addresses", "port": "port"},
)
class ConfigEntryServiceDefaultsDestination:
    def __init__(
        self,
        *,
        addresses: typing.Sequence[builtins.str],
        port: jsii.Number,
    ) -> None:
        '''
        :param addresses: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#addresses ConfigEntryServiceDefaults#addresses}.
        :param port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#port ConfigEntryServiceDefaults#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb23bb4bcfd37b9e002f9b38ec7d1122f28f6580a35b15ad66f3b62bcd2e0fb3)
            check_type(argname="argument addresses", value=addresses, expected_type=type_hints["addresses"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "addresses": addresses,
            "port": port,
        }

    @builtins.property
    def addresses(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#addresses ConfigEntryServiceDefaults#addresses}.'''
        result = self._values.get("addresses")
        assert result is not None, "Required property 'addresses' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#port ConfigEntryServiceDefaults#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceDefaultsDestinationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsDestinationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__90429b8bfa45a1c469fa2c7e681ab5412bfa0c6d888b7d12f42d0e3083b545df)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsDestinationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__340d36957354c53c3a8eea886448378dfd19455a8979a7b73c72069ac018c66c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsDestinationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98cfbd0fb71f9894be9f1a633fb4bd7c5f6e71364d79f48b5bafadc5284fa6a6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1b4e8f92eb74d3543626879ef145f296d25b838e7c728cb3a2abc74e4fa03e01)
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
            type_hints = typing.get_type_hints(_typecheckingstub__be9cbb529bd18e04392e0c27aa2c39be790a25e342d41135849be82012a9c7f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsDestination]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsDestination]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsDestination]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__725c78b46e8ef9f4eccceae1fee9ccbc0768ba719be9b39e7e0f7c65ed9ffb6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsDestinationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsDestinationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b3bc9174d7aeaa20ce9ec7051ea47a40f49e4845825210c909ba49283f882a4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="addressesInput")
    def addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "addressesInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="addresses")
    def addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "addresses"))

    @addresses.setter
    def addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c06a15022b169c0ee8f19c8f20ae74beb41c8899b331439586d09f325cae46bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addresses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f4201ebe1b10cd1d8ef075087a10d91d87ebefa424903029aa2d2871e22c06b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsDestination]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsDestination]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsDestination]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61d9ba5533539843316ae57fba15c129b437d728289296e29fe7b83adf3f41cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsEnvoyExtensions",
    jsii_struct_bases=[],
    name_mapping={
        "arguments": "arguments",
        "consul_version": "consulVersion",
        "envoy_version": "envoyVersion",
        "name": "name",
        "required": "required",
    },
)
class ConfigEntryServiceDefaultsEnvoyExtensions:
    def __init__(
        self,
        *,
        arguments: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        consul_version: typing.Optional[builtins.str] = None,
        envoy_version: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param arguments: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#arguments ConfigEntryServiceDefaults#arguments}.
        :param consul_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#consul_version ConfigEntryServiceDefaults#consul_version}.
        :param envoy_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#envoy_version ConfigEntryServiceDefaults#envoy_version}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#name ConfigEntryServiceDefaults#name}.
        :param required: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#required ConfigEntryServiceDefaults#required}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b6b539f50a2af306483c5b22c8c19d4bb2b4e4ee37ad779579e26a872f248c8)
            check_type(argname="argument arguments", value=arguments, expected_type=type_hints["arguments"])
            check_type(argname="argument consul_version", value=consul_version, expected_type=type_hints["consul_version"])
            check_type(argname="argument envoy_version", value=envoy_version, expected_type=type_hints["envoy_version"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if arguments is not None:
            self._values["arguments"] = arguments
        if consul_version is not None:
            self._values["consul_version"] = consul_version
        if envoy_version is not None:
            self._values["envoy_version"] = envoy_version
        if name is not None:
            self._values["name"] = name
        if required is not None:
            self._values["required"] = required

    @builtins.property
    def arguments(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#arguments ConfigEntryServiceDefaults#arguments}.'''
        result = self._values.get("arguments")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def consul_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#consul_version ConfigEntryServiceDefaults#consul_version}.'''
        result = self._values.get("consul_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def envoy_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#envoy_version ConfigEntryServiceDefaults#envoy_version}.'''
        result = self._values.get("envoy_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#name ConfigEntryServiceDefaults#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#required ConfigEntryServiceDefaults#required}.'''
        result = self._values.get("required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsEnvoyExtensions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceDefaultsEnvoyExtensionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsEnvoyExtensionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5179e9cf80f7d47f65a6427b82fde2742a5488714c9bdc2b73f065d5f9a88bce)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsEnvoyExtensionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1901da79e20935b72ab1fa2853cad4b4279e0d93f64c5e6a1db8b3a517d1e1bd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsEnvoyExtensionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1374d959e3e1cec5c5d758fab0965138fe1e846cb924a27679a95486e3f19915)
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
            type_hints = typing.get_type_hints(_typecheckingstub__32fe0164434ba2faa93479fd60ab379f287d1b6194af16c538273522bdcf43a9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a0e1e7c6b959f92d30965c8493d67dbeaf6cfd116faab54ebc12b380d5444190)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsEnvoyExtensions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsEnvoyExtensions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsEnvoyExtensions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b308b496a9e38c0c60841530ebf851747a693bbea9c55d13f6fe392e0899523)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsEnvoyExtensionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsEnvoyExtensionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d6c52aa48384828900c58eb31865b2e4243715159adc099099a65271b42a91d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetArguments")
    def reset_arguments(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArguments", []))

    @jsii.member(jsii_name="resetConsulVersion")
    def reset_consul_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConsulVersion", []))

    @jsii.member(jsii_name="resetEnvoyVersion")
    def reset_envoy_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvoyVersion", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetRequired")
    def reset_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequired", []))

    @builtins.property
    @jsii.member(jsii_name="argumentsInput")
    def arguments_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "argumentsInput"))

    @builtins.property
    @jsii.member(jsii_name="consulVersionInput")
    def consul_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "consulVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="envoyVersionInput")
    def envoy_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "envoyVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredInput")
    def required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requiredInput"))

    @builtins.property
    @jsii.member(jsii_name="arguments")
    def arguments(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "arguments"))

    @arguments.setter
    def arguments(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9a42dc1641977311728f511b2a3ab9048098ecd8f9b9f0b8c75ac2995780575)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "arguments", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="consulVersion")
    def consul_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "consulVersion"))

    @consul_version.setter
    def consul_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3211918f7ddbfaf4e4e7658be6fc8290d037dbb6ec5a40f92db74291a071ae43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "consulVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="envoyVersion")
    def envoy_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "envoyVersion"))

    @envoy_version.setter
    def envoy_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__600f53b960796c2d8b3b12adf555e8d19e6bf75730242b246e14b26afef2c551)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "envoyVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3448e660cfe56c7fdf6850a52bcb130c1a8292a8d8a540ea0789f5fa339dab8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="required")
    def required(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "required"))

    @required.setter
    def required(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c410c614ec65ddf05045bdcc6a980bd8153dff5309c9cbe2fe211da63f9ab47b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "required", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsEnvoyExtensions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsEnvoyExtensions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsEnvoyExtensions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66582135e432884594dfa5d49fedfa7bb53c59d0637b886e96c772ca9bdbda35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsExpose",
    jsii_struct_bases=[],
    name_mapping={"checks": "checks", "paths": "paths"},
)
class ConfigEntryServiceDefaultsExpose:
    def __init__(
        self,
        *,
        checks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        paths: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsExposePaths", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param checks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#checks ConfigEntryServiceDefaults#checks}.
        :param paths: paths block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#paths ConfigEntryServiceDefaults#paths}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d6a57fd7f5a954ce72b46f67cacbd5085b9c92a2193194522f6cf74cf3dc955)
            check_type(argname="argument checks", value=checks, expected_type=type_hints["checks"])
            check_type(argname="argument paths", value=paths, expected_type=type_hints["paths"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if checks is not None:
            self._values["checks"] = checks
        if paths is not None:
            self._values["paths"] = paths

    @builtins.property
    def checks(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#checks ConfigEntryServiceDefaults#checks}.'''
        result = self._values.get("checks")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def paths(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsExposePaths"]]]:
        '''paths block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#paths ConfigEntryServiceDefaults#paths}
        '''
        result = self._values.get("paths")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsExposePaths"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsExpose(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceDefaultsExposeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsExposeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__82dac5c1cd3d1389f7feb2c73ad1762485629996abf9b778ce0d23cb8b722b0b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsExposeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6be5ad771d78feccdf0a019da5f939b2f2787358b62b9efa160e5fa229372b6d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsExposeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87e8ea0815d6592d0d7eff7fa9fb7bba3cd3b83255e1073db841ae7476645a3d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa8281592452b7dd410721e3e40b649486a890f244dcfee5402d34f8a74258e0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__babf51f57a2bad6165f5a60dfa71e9e96cb88853e8b3b1bddc6fa3aa91cce0eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsExpose]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsExpose]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsExpose]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eec24632ed9833d7b3317300b8f4669929d71ef0babec0438037637ebca0e370)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsExposeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsExposeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e72b8aa1edf7f1940844f61779ae9cdc10c574fb71b9f602bd195a8160608b3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putPaths")
    def put_paths(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsExposePaths", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d4bf64e051fec41fd966197c972eb54b8adfed5ea65f4ddc3e0839acf0c6228)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPaths", [value]))

    @jsii.member(jsii_name="resetChecks")
    def reset_checks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChecks", []))

    @jsii.member(jsii_name="resetPaths")
    def reset_paths(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPaths", []))

    @builtins.property
    @jsii.member(jsii_name="paths")
    def paths(self) -> "ConfigEntryServiceDefaultsExposePathsList":
        return typing.cast("ConfigEntryServiceDefaultsExposePathsList", jsii.get(self, "paths"))

    @builtins.property
    @jsii.member(jsii_name="checksInput")
    def checks_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "checksInput"))

    @builtins.property
    @jsii.member(jsii_name="pathsInput")
    def paths_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsExposePaths"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsExposePaths"]]], jsii.get(self, "pathsInput"))

    @builtins.property
    @jsii.member(jsii_name="checks")
    def checks(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "checks"))

    @checks.setter
    def checks(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c97712c6284e62fe83651f02300175debd67145ff56ae2e4064e86026de1e755)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "checks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsExpose]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsExpose]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsExpose]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f07cc7dc35dd485d5e74f7799824c8c8789f70fb1590b058e269f49bf3a2d1e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsExposePaths",
    jsii_struct_bases=[],
    name_mapping={
        "listener_port": "listenerPort",
        "local_path_port": "localPathPort",
        "path": "path",
        "protocol": "protocol",
    },
)
class ConfigEntryServiceDefaultsExposePaths:
    def __init__(
        self,
        *,
        listener_port: typing.Optional[jsii.Number] = None,
        local_path_port: typing.Optional[jsii.Number] = None,
        path: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param listener_port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#listener_port ConfigEntryServiceDefaults#listener_port}.
        :param local_path_port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#local_path_port ConfigEntryServiceDefaults#local_path_port}.
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#path ConfigEntryServiceDefaults#path}.
        :param protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#protocol ConfigEntryServiceDefaults#protocol}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb28049575f77108d6e1f0eb3448601cf66416c310f01a7324406c6a54a6c3ab)
            check_type(argname="argument listener_port", value=listener_port, expected_type=type_hints["listener_port"])
            check_type(argname="argument local_path_port", value=local_path_port, expected_type=type_hints["local_path_port"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if listener_port is not None:
            self._values["listener_port"] = listener_port
        if local_path_port is not None:
            self._values["local_path_port"] = local_path_port
        if path is not None:
            self._values["path"] = path
        if protocol is not None:
            self._values["protocol"] = protocol

    @builtins.property
    def listener_port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#listener_port ConfigEntryServiceDefaults#listener_port}.'''
        result = self._values.get("listener_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def local_path_port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#local_path_port ConfigEntryServiceDefaults#local_path_port}.'''
        result = self._values.get("local_path_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#path ConfigEntryServiceDefaults#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#protocol ConfigEntryServiceDefaults#protocol}.'''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsExposePaths(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceDefaultsExposePathsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsExposePathsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__25b38c331ba8461b1ad68e09532eb952ecb2dfef8a9208021f0b69b090dfc05a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsExposePathsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5eb2836ec2928fa311234d2ed4296899be13fa359fab496896db01ef1ac69ae4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsExposePathsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4aea165c33756ff4aefde309b428488824360102a2001b473ef2c03fad86884d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__654209b9beda891a5fb21c53db4c027b29516805732a5feaf4762ad0f96c1508)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4002364ec4378135cd1d6b5b4a981328c30d3c41885e76228308c700f9c7ac29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsExposePaths]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsExposePaths]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsExposePaths]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78c799d047f14214bef8a8181f93634d335b6102f6744dd3e17734f79b3d79b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsExposePathsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsExposePathsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad95893bdb1093e8616ddf4a24e2ba856ab711cb11ac13f5b385240defd2e9c1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetListenerPort")
    def reset_listener_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetListenerPort", []))

    @jsii.member(jsii_name="resetLocalPathPort")
    def reset_local_path_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocalPathPort", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetProtocol")
    def reset_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocol", []))

    @builtins.property
    @jsii.member(jsii_name="listenerPortInput")
    def listener_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "listenerPortInput"))

    @builtins.property
    @jsii.member(jsii_name="localPathPortInput")
    def local_path_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "localPathPortInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="listenerPort")
    def listener_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "listenerPort"))

    @listener_port.setter
    def listener_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5519b60251b46a9af7d828a4e30db0b5deb2aee10e9cf155d319af8181fb9255)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "listenerPort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localPathPort")
    def local_path_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "localPathPort"))

    @local_path_port.setter
    def local_path_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7918dd3298679cefaaec279c773e9da70955334d08cadc3248edffedd8479ce3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localPathPort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4de97b5d48a7945e00e6ebb5e8b19f47b76e9bb6e566c8a945450ad448b3193b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e4886aeebf2a93252ade71530d91ea96a169495ede41fe519db0907792267dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsExposePaths]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsExposePaths]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsExposePaths]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d74aee6b41e39b3c54404f5d956b8542ac048973436e44c9455cc2166e6bbcc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsMeshGateway",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode"},
)
class ConfigEntryServiceDefaultsMeshGateway:
    def __init__(self, *, mode: builtins.str) -> None:
        '''
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mode ConfigEntryServiceDefaults#mode}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e831bd84addc4bdb8adb1775be7a9fd810e08becda905097b7746261840d39b)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "mode": mode,
        }

    @builtins.property
    def mode(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mode ConfigEntryServiceDefaults#mode}.'''
        result = self._values.get("mode")
        assert result is not None, "Required property 'mode' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsMeshGateway(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceDefaultsMeshGatewayList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsMeshGatewayList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac3e6b9ac8c7295102076817aa6f76ecdf14b52a2813620b2744f2bfc937b6ca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsMeshGatewayOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a3aab0e8333ae0b75c4e66897da0e3a5c7a48f8939c6003ec96dd9cbfb62710)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsMeshGatewayOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e15f80e83a0d5d2f06dcba03e41aa562c1dbcf0f06b2e65525c2254c32ccafdd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6664a833902cde924082d86e9bb85c9e0a38ffc009697d6509ee0fb29a935435)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f106f3fe05208fbe895f2070d7d7bb5af03189d2a0232d44b0529d4b21751849)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsMeshGateway]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsMeshGateway]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsMeshGateway]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__534e8dfc5dbf9b30ee1605240449409a89d4fe88b434e665c6da6df8fa2c73a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsMeshGatewayOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsMeshGatewayOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c42c9e6464a0652fca62e573029d546fce3b5d8b33b230865f548da3b266c6a8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c904bd3bd9303030ac99786decd3c7dff9914282fb86e1fa20e5c00d4391b8cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsMeshGateway]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsMeshGateway]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsMeshGateway]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93119fa38a4334efada2df94f50c5f900ef9904392b64840de1f2d729156899d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsTransparentProxy",
    jsii_struct_bases=[],
    name_mapping={
        "dialed_directly": "dialedDirectly",
        "outbound_listener_port": "outboundListenerPort",
    },
)
class ConfigEntryServiceDefaultsTransparentProxy:
    def __init__(
        self,
        *,
        dialed_directly: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        outbound_listener_port: jsii.Number,
    ) -> None:
        '''
        :param dialed_directly: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#dialed_directly ConfigEntryServiceDefaults#dialed_directly}.
        :param outbound_listener_port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#outbound_listener_port ConfigEntryServiceDefaults#outbound_listener_port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__330b96e3084a1de6fda549b58a9a28c140d1723fefbfdf40dc8a6f8e73b1433a)
            check_type(argname="argument dialed_directly", value=dialed_directly, expected_type=type_hints["dialed_directly"])
            check_type(argname="argument outbound_listener_port", value=outbound_listener_port, expected_type=type_hints["outbound_listener_port"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dialed_directly": dialed_directly,
            "outbound_listener_port": outbound_listener_port,
        }

    @builtins.property
    def dialed_directly(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#dialed_directly ConfigEntryServiceDefaults#dialed_directly}.'''
        result = self._values.get("dialed_directly")
        assert result is not None, "Required property 'dialed_directly' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def outbound_listener_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#outbound_listener_port ConfigEntryServiceDefaults#outbound_listener_port}.'''
        result = self._values.get("outbound_listener_port")
        assert result is not None, "Required property 'outbound_listener_port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsTransparentProxy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceDefaultsTransparentProxyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsTransparentProxyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa3c1165cfcec0d86b9edc347b2cd7085f5a9860ecd12698b43acbc49a58569e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsTransparentProxyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0262c0b0370a5de48fe1f9c11bd5ec7bfa395321d3afeebf8cb0861565985195)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsTransparentProxyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f41523c88b6e9872167d2f6d0e7a0c23fac03efa906d98551b070556c1477a91)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1ff78ecbc6cb2e518eb14e779f13cd690b57c6c517d5d6796692ad061f588e53)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6258cf10bbc7f84bb69034c742c1e401e755284fff9f6ffcb68b40f2e9dc5ae2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsTransparentProxy]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsTransparentProxy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsTransparentProxy]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d437c9105b5c2f6e009dc57a7ce3c9774fb9ed0852379815ae1498caa4f85929)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsTransparentProxyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsTransparentProxyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a6350efe9c9e285b33f4a4956562817a442d91835a3e27789a36e3dde31fd013)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="dialedDirectlyInput")
    def dialed_directly_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dialedDirectlyInput"))

    @builtins.property
    @jsii.member(jsii_name="outboundListenerPortInput")
    def outbound_listener_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "outboundListenerPortInput"))

    @builtins.property
    @jsii.member(jsii_name="dialedDirectly")
    def dialed_directly(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dialedDirectly"))

    @dialed_directly.setter
    def dialed_directly(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__825902608d812bab7bc9ecb16d811ddaaf10ff19285bbf36544e61ab4a925fab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dialedDirectly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="outboundListenerPort")
    def outbound_listener_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "outboundListenerPort"))

    @outbound_listener_port.setter
    def outbound_listener_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e64afa724288800ec318c258bba74d20f44056ed688559b0a82fdd5dfd121492)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outboundListenerPort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsTransparentProxy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsTransparentProxy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsTransparentProxy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__886377c0e6071467d3ca34b0a67cb7d4679f093639303e62c9d143d8d9e48b6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfig",
    jsii_struct_bases=[],
    name_mapping={"defaults": "defaults", "overrides": "overrides"},
)
class ConfigEntryServiceDefaultsUpstreamConfig:
    def __init__(
        self,
        *,
        defaults: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfigDefaults", typing.Dict[builtins.str, typing.Any]]]]] = None,
        overrides: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfigOverrides", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param defaults: defaults block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#defaults ConfigEntryServiceDefaults#defaults}
        :param overrides: overrides block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#overrides ConfigEntryServiceDefaults#overrides}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a9d2091e0bdd200f238cfc0f1a7e7c917c3d7640ac28bbb5e1446f3ecc0df0f)
            check_type(argname="argument defaults", value=defaults, expected_type=type_hints["defaults"])
            check_type(argname="argument overrides", value=overrides, expected_type=type_hints["overrides"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if defaults is not None:
            self._values["defaults"] = defaults
        if overrides is not None:
            self._values["overrides"] = overrides

    @builtins.property
    def defaults(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigDefaults"]]]:
        '''defaults block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#defaults ConfigEntryServiceDefaults#defaults}
        '''
        result = self._values.get("defaults")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigDefaults"]]], result)

    @builtins.property
    def overrides(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigOverrides"]]]:
        '''overrides block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#overrides ConfigEntryServiceDefaults#overrides}
        '''
        result = self._values.get("overrides")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigOverrides"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsUpstreamConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigDefaults",
    jsii_struct_bases=[],
    name_mapping={
        "balance_outbound_connections": "balanceOutboundConnections",
        "connect_timeout_ms": "connectTimeoutMs",
        "limits": "limits",
        "mesh_gateway": "meshGateway",
        "passive_health_check": "passiveHealthCheck",
        "protocol": "protocol",
    },
)
class ConfigEntryServiceDefaultsUpstreamConfigDefaults:
    def __init__(
        self,
        *,
        balance_outbound_connections: typing.Optional[builtins.str] = None,
        connect_timeout_ms: typing.Optional[jsii.Number] = None,
        limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        mesh_gateway: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway", typing.Dict[builtins.str, typing.Any]]]]] = None,
        passive_health_check: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck", typing.Dict[builtins.str, typing.Any]]]]] = None,
        protocol: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param balance_outbound_connections: Sets the strategy for allocating outbound connections from upstreams across Envoy proxy threads. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#balance_outbound_connections ConfigEntryServiceDefaults#balance_outbound_connections}
        :param connect_timeout_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#connect_timeout_ms ConfigEntryServiceDefaults#connect_timeout_ms}.
        :param limits: limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#limits ConfigEntryServiceDefaults#limits}
        :param mesh_gateway: mesh_gateway block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mesh_gateway ConfigEntryServiceDefaults#mesh_gateway}
        :param passive_health_check: passive_health_check block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#passive_health_check ConfigEntryServiceDefaults#passive_health_check}
        :param protocol: Specifies the default protocol for the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#protocol ConfigEntryServiceDefaults#protocol}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c0f11deb789c9da973360d2fa3454d7328342fe3311eae9fbcefe810e618dc6)
            check_type(argname="argument balance_outbound_connections", value=balance_outbound_connections, expected_type=type_hints["balance_outbound_connections"])
            check_type(argname="argument connect_timeout_ms", value=connect_timeout_ms, expected_type=type_hints["connect_timeout_ms"])
            check_type(argname="argument limits", value=limits, expected_type=type_hints["limits"])
            check_type(argname="argument mesh_gateway", value=mesh_gateway, expected_type=type_hints["mesh_gateway"])
            check_type(argname="argument passive_health_check", value=passive_health_check, expected_type=type_hints["passive_health_check"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if balance_outbound_connections is not None:
            self._values["balance_outbound_connections"] = balance_outbound_connections
        if connect_timeout_ms is not None:
            self._values["connect_timeout_ms"] = connect_timeout_ms
        if limits is not None:
            self._values["limits"] = limits
        if mesh_gateway is not None:
            self._values["mesh_gateway"] = mesh_gateway
        if passive_health_check is not None:
            self._values["passive_health_check"] = passive_health_check
        if protocol is not None:
            self._values["protocol"] = protocol

    @builtins.property
    def balance_outbound_connections(self) -> typing.Optional[builtins.str]:
        '''Sets the strategy for allocating outbound connections from upstreams across Envoy proxy threads.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#balance_outbound_connections ConfigEntryServiceDefaults#balance_outbound_connections}
        '''
        result = self._values.get("balance_outbound_connections")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connect_timeout_ms(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#connect_timeout_ms ConfigEntryServiceDefaults#connect_timeout_ms}.'''
        result = self._values.get("connect_timeout_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def limits(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits"]]]:
        '''limits block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#limits ConfigEntryServiceDefaults#limits}
        '''
        result = self._values.get("limits")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits"]]], result)

    @builtins.property
    def mesh_gateway(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway"]]]:
        '''mesh_gateway block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mesh_gateway ConfigEntryServiceDefaults#mesh_gateway}
        '''
        result = self._values.get("mesh_gateway")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway"]]], result)

    @builtins.property
    def passive_health_check(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck"]]]:
        '''passive_health_check block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#passive_health_check ConfigEntryServiceDefaults#passive_health_check}
        '''
        result = self._values.get("passive_health_check")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck"]]], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''Specifies the default protocol for the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#protocol ConfigEntryServiceDefaults#protocol}
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsUpstreamConfigDefaults(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits",
    jsii_struct_bases=[],
    name_mapping={
        "max_concurrent_requests": "maxConcurrentRequests",
        "max_connections": "maxConnections",
        "max_pending_requests": "maxPendingRequests",
    },
)
class ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits:
    def __init__(
        self,
        *,
        max_concurrent_requests: typing.Optional[jsii.Number] = None,
        max_connections: typing.Optional[jsii.Number] = None,
        max_pending_requests: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_concurrent_requests: Specifies the maximum number of concurrent requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_concurrent_requests ConfigEntryServiceDefaults#max_concurrent_requests}
        :param max_connections: Specifies the maximum number of connections a service instance can establish against the upstream. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_connections ConfigEntryServiceDefaults#max_connections}
        :param max_pending_requests: Specifies the maximum number of requests that are queued while waiting for a connection to establish. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_pending_requests ConfigEntryServiceDefaults#max_pending_requests}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff568a80f5f3f605d973413b31938c57426701978c6cdb018e2752f492140d28)
            check_type(argname="argument max_concurrent_requests", value=max_concurrent_requests, expected_type=type_hints["max_concurrent_requests"])
            check_type(argname="argument max_connections", value=max_connections, expected_type=type_hints["max_connections"])
            check_type(argname="argument max_pending_requests", value=max_pending_requests, expected_type=type_hints["max_pending_requests"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_concurrent_requests is not None:
            self._values["max_concurrent_requests"] = max_concurrent_requests
        if max_connections is not None:
            self._values["max_connections"] = max_connections
        if max_pending_requests is not None:
            self._values["max_pending_requests"] = max_pending_requests

    @builtins.property
    def max_concurrent_requests(self) -> typing.Optional[jsii.Number]:
        '''Specifies the maximum number of concurrent requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_concurrent_requests ConfigEntryServiceDefaults#max_concurrent_requests}
        '''
        result = self._values.get("max_concurrent_requests")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_connections(self) -> typing.Optional[jsii.Number]:
        '''Specifies the maximum number of connections a service instance can establish against the upstream.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_connections ConfigEntryServiceDefaults#max_connections}
        '''
        result = self._values.get("max_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_pending_requests(self) -> typing.Optional[jsii.Number]:
        '''Specifies the maximum number of requests that are queued while waiting for a connection to establish.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_pending_requests ConfigEntryServiceDefaults#max_pending_requests}
        '''
        result = self._values.get("max_pending_requests")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimitsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimitsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1cf7b3e1472f5ade4bc60d672e90ef8d610bebcad85d84b57b34a0ec4afec411)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimitsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53b22a2ad4c7985cac8957a5874506a7b371afcceb83c40ff7c7ba177bf2cb01)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimitsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ceb833ca7875a9d56683f07f0ed9146fa0382bec5bd7aa0427feeb1c93e1e30a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d441e82634228170ad8e1e47e505f89fc384f589bc75857beb67363251e28676)
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
            type_hints = typing.get_type_hints(_typecheckingstub__56ad63cf507b8f5c2a312739a1bf4c6c3dff1ea567cfba66e66411fe895eba12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1887d5380811e1cc71c49629b3c1f6ab745f9bd7ae28ea59b14fee7e36a8fb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__638d5d7093eb2cb17ac3a3540b88060577e6e33bc1b97c3ed1dab3d0ff92ede1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetMaxConcurrentRequests")
    def reset_max_concurrent_requests(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConcurrentRequests", []))

    @jsii.member(jsii_name="resetMaxConnections")
    def reset_max_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnections", []))

    @jsii.member(jsii_name="resetMaxPendingRequests")
    def reset_max_pending_requests(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPendingRequests", []))

    @builtins.property
    @jsii.member(jsii_name="maxConcurrentRequestsInput")
    def max_concurrent_requests_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConcurrentRequestsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionsInput")
    def max_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxPendingRequestsInput")
    def max_pending_requests_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPendingRequestsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConcurrentRequests")
    def max_concurrent_requests(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConcurrentRequests"))

    @max_concurrent_requests.setter
    def max_concurrent_requests(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2f5df822a2e66eca5c7c7dc920dc081e5168bf56f7000b293d8808aae370aee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConcurrentRequests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnections")
    def max_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnections"))

    @max_connections.setter
    def max_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a09640149eb7230253257c9444b7a49c552ec36b37e5aa30c31d7a0f75a829c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxPendingRequests")
    def max_pending_requests(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPendingRequests"))

    @max_pending_requests.setter
    def max_pending_requests(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff534aff6583b6d3208a82d7a22cb8c641a81d8a7de5f0ac54c317698013a328)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxPendingRequests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7ccfaa9f4e43a0365465df795745af11d618fdd13cc3d25de8e71d4e2e92dbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsUpstreamConfigDefaultsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigDefaultsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__05a4a342bf3e5fb48f6c7e0e44aca20ed1d603855ec3b6f1808306f8d83097c8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsUpstreamConfigDefaultsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80f890a3626bc1a8f4b267a6caf1981a3f79712e66b97dc8b17c1f93d91a6ebc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsUpstreamConfigDefaultsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d256a92e52b4722e59b11220e76f833531f763dc07e36651f6a7cc735d2f414d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3ceb5e538162a2e23cc6566fb9e726c5005ed5f378c24c6de067b686da65f00)
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
            type_hints = typing.get_type_hints(_typecheckingstub__044648bc5a1b6e0c0b3d2915826f209d1db2e64ebc8734c9bbd01aa911682f7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaults]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaults]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaults]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ee252cc3a47d092aca35baa9a69aa15fbdb19fad631ecc94a9472db710729d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode"},
)
class ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway:
    def __init__(self, *, mode: typing.Optional[builtins.str] = None) -> None:
        '''
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mode ConfigEntryServiceDefaults#mode}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a00ee6085bd9e94e4b05a7f1ff74f51e7ac48003580cc5082d21f88f31a1bdf8)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mode ConfigEntryServiceDefaults#mode}.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGatewayList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGatewayList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e7e093badf68ef9726d530a2a76996a1f788cb373bfd8a143437bc53419bc7be)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGatewayOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e2b75db490d6e72579393999d9a5c7688c488bd161c961f812677caecef4c05)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGatewayOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2db8b2dbbb87e9557892b87660f27571aaa279d073ce115f3075b5a47661b2b4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e839d206ef76dfcd3d2cc68fb1ed1d610ae9f9becde061566f15e1b13849ac33)
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
            type_hints = typing.get_type_hints(_typecheckingstub__47a58027fd59adac8c35a8cbddd0bc79475f2dc7081be49770be64dc99e8e60d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4b70a4fea2ff1f7e1322d8f89753dae13e5bf7a78886b9ca69c9be417930709)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGatewayOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGatewayOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b830a3b001289b660d2e82ba6be569f1d23215f70cec3a25b8c01af297d5a930)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aeced4960d4ffe798d35d0a1ad9839f2d759ac21bc1f2f263306aa044a292d42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73f0636a93b8e3a55b391012957fe1ef9bcda068a1f0b9b8258ba5fa6746bc5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsUpstreamConfigDefaultsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigDefaultsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd16a2f56307210c16a7e2268da9018fb3783f10a9cab7cf4782039a9790bb2b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putLimits")
    def put_limits(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02518937086ad33ca22c070dd3df9d43e6dda12ad0b6182c7477837fe6d85005)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLimits", [value]))

    @jsii.member(jsii_name="putMeshGateway")
    def put_mesh_gateway(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__baf3e66c22f3580c4e62897c9950b0fe79e24b87d01f24d1fdc359ab8307036a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMeshGateway", [value]))

    @jsii.member(jsii_name="putPassiveHealthCheck")
    def put_passive_health_check(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47c5d4da72a43e56e5b79cd1eed2a57672546e4370ecbced655f55f2546339d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPassiveHealthCheck", [value]))

    @jsii.member(jsii_name="resetBalanceOutboundConnections")
    def reset_balance_outbound_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBalanceOutboundConnections", []))

    @jsii.member(jsii_name="resetConnectTimeoutMs")
    def reset_connect_timeout_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectTimeoutMs", []))

    @jsii.member(jsii_name="resetLimits")
    def reset_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLimits", []))

    @jsii.member(jsii_name="resetMeshGateway")
    def reset_mesh_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMeshGateway", []))

    @jsii.member(jsii_name="resetPassiveHealthCheck")
    def reset_passive_health_check(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassiveHealthCheck", []))

    @jsii.member(jsii_name="resetProtocol")
    def reset_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocol", []))

    @builtins.property
    @jsii.member(jsii_name="limits")
    def limits(self) -> ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimitsList:
        return typing.cast(ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimitsList, jsii.get(self, "limits"))

    @builtins.property
    @jsii.member(jsii_name="meshGateway")
    def mesh_gateway(
        self,
    ) -> ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGatewayList:
        return typing.cast(ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGatewayList, jsii.get(self, "meshGateway"))

    @builtins.property
    @jsii.member(jsii_name="passiveHealthCheck")
    def passive_health_check(
        self,
    ) -> "ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheckList":
        return typing.cast("ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheckList", jsii.get(self, "passiveHealthCheck"))

    @builtins.property
    @jsii.member(jsii_name="balanceOutboundConnectionsInput")
    def balance_outbound_connections_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "balanceOutboundConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="connectTimeoutMsInput")
    def connect_timeout_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "connectTimeoutMsInput"))

    @builtins.property
    @jsii.member(jsii_name="limitsInput")
    def limits_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits]]], jsii.get(self, "limitsInput"))

    @builtins.property
    @jsii.member(jsii_name="meshGatewayInput")
    def mesh_gateway_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway]]], jsii.get(self, "meshGatewayInput"))

    @builtins.property
    @jsii.member(jsii_name="passiveHealthCheckInput")
    def passive_health_check_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck"]]], jsii.get(self, "passiveHealthCheckInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="balanceOutboundConnections")
    def balance_outbound_connections(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "balanceOutboundConnections"))

    @balance_outbound_connections.setter
    def balance_outbound_connections(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77b8799e65dd48b73832e0b757f185e44d917bd78b0831789d7cf5c24b61b062)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "balanceOutboundConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectTimeoutMs")
    def connect_timeout_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "connectTimeoutMs"))

    @connect_timeout_ms.setter
    def connect_timeout_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cc651f65cf6829062964e570232fc909524f9fb3e202dfe896ffccff963e2b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectTimeoutMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94f985f0b48ead2217807e0bd6c87981ae664eedc167515df4fe095f801fe11b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaults]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaults]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaults]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f36b762530f649ccfdfaa181f13649754c96d9be25a171d4e77c5c2a83380335)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck",
    jsii_struct_bases=[],
    name_mapping={
        "base_ejection_time": "baseEjectionTime",
        "enforcing_consecutive5_xx": "enforcingConsecutive5Xx",
        "interval": "interval",
        "max_ejection_percent": "maxEjectionPercent",
        "max_failures": "maxFailures",
    },
)
class ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck:
    def __init__(
        self,
        *,
        base_ejection_time: typing.Optional[builtins.str] = None,
        enforcing_consecutive5_xx: typing.Optional[jsii.Number] = None,
        interval: typing.Optional[builtins.str] = None,
        max_ejection_percent: typing.Optional[jsii.Number] = None,
        max_failures: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param base_ejection_time: Specifies the minimum amount of time that an ejected host must remain outside the cluster before rejoining. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#base_ejection_time ConfigEntryServiceDefaults#base_ejection_time}
        :param enforcing_consecutive5_xx: Specifies a percentage that indicates how many times out of 100 that Consul ejects the host when it detects an outlier status. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#enforcing_consecutive_5xx ConfigEntryServiceDefaults#enforcing_consecutive_5xx}
        :param interval: Specifies the time between checks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#interval ConfigEntryServiceDefaults#interval}
        :param max_ejection_percent: Specifies the maximum percentage of an upstream cluster that Consul ejects when the proxy reports an outlier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_ejection_percent ConfigEntryServiceDefaults#max_ejection_percent}
        :param max_failures: Specifies the number of consecutive failures allowed per check interval. If exceeded, Consul removes the host from the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_failures ConfigEntryServiceDefaults#max_failures}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11b2deaaf603afabdda39a2388decdd694dba65233b1332b41483be7e596a6d5)
            check_type(argname="argument base_ejection_time", value=base_ejection_time, expected_type=type_hints["base_ejection_time"])
            check_type(argname="argument enforcing_consecutive5_xx", value=enforcing_consecutive5_xx, expected_type=type_hints["enforcing_consecutive5_xx"])
            check_type(argname="argument interval", value=interval, expected_type=type_hints["interval"])
            check_type(argname="argument max_ejection_percent", value=max_ejection_percent, expected_type=type_hints["max_ejection_percent"])
            check_type(argname="argument max_failures", value=max_failures, expected_type=type_hints["max_failures"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if base_ejection_time is not None:
            self._values["base_ejection_time"] = base_ejection_time
        if enforcing_consecutive5_xx is not None:
            self._values["enforcing_consecutive5_xx"] = enforcing_consecutive5_xx
        if interval is not None:
            self._values["interval"] = interval
        if max_ejection_percent is not None:
            self._values["max_ejection_percent"] = max_ejection_percent
        if max_failures is not None:
            self._values["max_failures"] = max_failures

    @builtins.property
    def base_ejection_time(self) -> typing.Optional[builtins.str]:
        '''Specifies the minimum amount of time that an ejected host must remain outside the cluster before rejoining.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#base_ejection_time ConfigEntryServiceDefaults#base_ejection_time}
        '''
        result = self._values.get("base_ejection_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enforcing_consecutive5_xx(self) -> typing.Optional[jsii.Number]:
        '''Specifies a percentage that indicates how many times out of 100 that Consul ejects the host when it detects an outlier status.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#enforcing_consecutive_5xx ConfigEntryServiceDefaults#enforcing_consecutive_5xx}
        '''
        result = self._values.get("enforcing_consecutive5_xx")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interval(self) -> typing.Optional[builtins.str]:
        '''Specifies the time between checks.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#interval ConfigEntryServiceDefaults#interval}
        '''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_ejection_percent(self) -> typing.Optional[jsii.Number]:
        '''Specifies the maximum percentage of an upstream cluster that Consul ejects when the proxy reports an outlier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_ejection_percent ConfigEntryServiceDefaults#max_ejection_percent}
        '''
        result = self._values.get("max_ejection_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_failures(self) -> typing.Optional[jsii.Number]:
        '''Specifies the number of consecutive failures allowed per check interval.

        If exceeded, Consul removes the host from the load balancer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_failures ConfigEntryServiceDefaults#max_failures}
        '''
        result = self._values.get("max_failures")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheckList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheckList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ccea6a3db6a0fcee263c689a57611c6cd15efe95bc7bc17240ceca861943a050)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheckOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17ad115e30990111987714c00590b0d226ff666724cb973d39a93e080a6679be)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheckOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e9e223f9eee88ad20c3bd1360bafd6c06c6e7772ee9bb5e0982cf990e7946c7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__94139cce8723c9cd92ffb5b2d52a516842e3d0331368429e8fbf77eaf4295143)
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
            type_hints = typing.get_type_hints(_typecheckingstub__695293ff8f371c9d66e6c20b3bd2d1d47fd7804dd5648230ee83496539f33579)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb42f05adfe5eecf3ee8a5ab0d383a5b411bc3dd2e7f142d3aaa8fb87cb2a998)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheckOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheckOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__150a8ed5abaebee4e8b404e9226ba7ad65e9b68a2b53896d653e7e1419eed8d6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetBaseEjectionTime")
    def reset_base_ejection_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaseEjectionTime", []))

    @jsii.member(jsii_name="resetEnforcingConsecutive5Xx")
    def reset_enforcing_consecutive5_xx(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforcingConsecutive5Xx", []))

    @jsii.member(jsii_name="resetInterval")
    def reset_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterval", []))

    @jsii.member(jsii_name="resetMaxEjectionPercent")
    def reset_max_ejection_percent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxEjectionPercent", []))

    @jsii.member(jsii_name="resetMaxFailures")
    def reset_max_failures(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxFailures", []))

    @builtins.property
    @jsii.member(jsii_name="baseEjectionTimeInput")
    def base_ejection_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseEjectionTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="enforcingConsecutive5XxInput")
    def enforcing_consecutive5_xx_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "enforcingConsecutive5XxInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalInput"))

    @builtins.property
    @jsii.member(jsii_name="maxEjectionPercentInput")
    def max_ejection_percent_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxEjectionPercentInput"))

    @builtins.property
    @jsii.member(jsii_name="maxFailuresInput")
    def max_failures_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxFailuresInput"))

    @builtins.property
    @jsii.member(jsii_name="baseEjectionTime")
    def base_ejection_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseEjectionTime"))

    @base_ejection_time.setter
    def base_ejection_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a43f7bf19b49b3b404cacfe6738d4ca7585ddc51bcb2924ea7b6edf80e8cb611)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseEjectionTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enforcingConsecutive5Xx")
    def enforcing_consecutive5_xx(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "enforcingConsecutive5Xx"))

    @enforcing_consecutive5_xx.setter
    def enforcing_consecutive5_xx(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c7d6cdb99fc9242faa53d99e2a90754a31d5254bf8bf699c548b6272b80bc0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforcingConsecutive5Xx", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="interval")
    def interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3b67ab4827d7eddbce6eb6541f66850a8f1a80bbd48a8bf968584fe70161538)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "interval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxEjectionPercent")
    def max_ejection_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxEjectionPercent"))

    @max_ejection_percent.setter
    def max_ejection_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a78301ea819845ab9d067fd3de91d1a5ab99ac04946ec1fe973835b1e7f79962)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxEjectionPercent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxFailures")
    def max_failures(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxFailures"))

    @max_failures.setter
    def max_failures(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38f368a370683ad7bc9f447c3be68ce1b6a10dd9f290fe8873d7527f801a3a85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxFailures", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b732185f8c4dc97c8ffea2842ccc517052791cae17a5e3f23bc634bfa9a0490)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsUpstreamConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4b75e945fddc4d687907a7b3c746bbf5c955384682149bad8711b8739a58dfdc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsUpstreamConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47e9c2201aef57be720e8fdcebfe675c875fe7023c2b6d74abbe499ae4df7ec4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsUpstreamConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75afc77954094ce320f277564670f4d6dd5b353aabe834f9d7df8ef576a7eeed)
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
            type_hints = typing.get_type_hints(_typecheckingstub__027b715ac365b5fa7c593ab1fdea6db4f255e2a02027909652f1049f0779397e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4ab8247536af76da9bc5b727e64449ddee0ed72e021e0c1a9a2f4de404273e0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86d2433b092819de505447467bd8474f2b1d81963edae5a90b56f5afc64c7c77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsUpstreamConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__03848903920380c21dc7bf91ff45f82c04dcbe46fce38307629384097632877a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putDefaults")
    def put_defaults(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigDefaults, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8a100793e2f6278b2d750921cbc3f6a2bfccbbe0b5c85f9d32498d5498c6648)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDefaults", [value]))

    @jsii.member(jsii_name="putOverrides")
    def put_overrides(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfigOverrides", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__551836c97a270dcf4a8c1429360c2638eead5d852047e74a9c4af857ef8e7471)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putOverrides", [value]))

    @jsii.member(jsii_name="resetDefaults")
    def reset_defaults(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaults", []))

    @jsii.member(jsii_name="resetOverrides")
    def reset_overrides(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverrides", []))

    @builtins.property
    @jsii.member(jsii_name="defaults")
    def defaults(self) -> ConfigEntryServiceDefaultsUpstreamConfigDefaultsList:
        return typing.cast(ConfigEntryServiceDefaultsUpstreamConfigDefaultsList, jsii.get(self, "defaults"))

    @builtins.property
    @jsii.member(jsii_name="overrides")
    def overrides(self) -> "ConfigEntryServiceDefaultsUpstreamConfigOverridesList":
        return typing.cast("ConfigEntryServiceDefaultsUpstreamConfigOverridesList", jsii.get(self, "overrides"))

    @builtins.property
    @jsii.member(jsii_name="defaultsInput")
    def defaults_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaults]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaults]]], jsii.get(self, "defaultsInput"))

    @builtins.property
    @jsii.member(jsii_name="overridesInput")
    def overrides_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigOverrides"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigOverrides"]]], jsii.get(self, "overridesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dd9221fd0e484de8368c9a1252ea860dfcca6bfc071d2b2529b0e552669b7ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigOverrides",
    jsii_struct_bases=[],
    name_mapping={
        "balance_outbound_connections": "balanceOutboundConnections",
        "connect_timeout_ms": "connectTimeoutMs",
        "envoy_listener_json": "envoyListenerJson",
        "limits": "limits",
        "mesh_gateway": "meshGateway",
        "name": "name",
        "namespace": "namespace",
        "partition": "partition",
        "passive_health_check": "passiveHealthCheck",
        "peer": "peer",
        "protocol": "protocol",
    },
)
class ConfigEntryServiceDefaultsUpstreamConfigOverrides:
    def __init__(
        self,
        *,
        balance_outbound_connections: typing.Optional[builtins.str] = None,
        connect_timeout_ms: typing.Optional[jsii.Number] = None,
        envoy_listener_json: typing.Optional[builtins.str] = None,
        limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        mesh_gateway: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        passive_health_check: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck", typing.Dict[builtins.str, typing.Any]]]]] = None,
        peer: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param balance_outbound_connections: Sets the strategy for allocating outbound connections from upstreams across Envoy proxy threads. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#balance_outbound_connections ConfigEntryServiceDefaults#balance_outbound_connections}
        :param connect_timeout_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#connect_timeout_ms ConfigEntryServiceDefaults#connect_timeout_ms}.
        :param envoy_listener_json: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#envoy_listener_json ConfigEntryServiceDefaults#envoy_listener_json}.
        :param limits: limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#limits ConfigEntryServiceDefaults#limits}
        :param mesh_gateway: mesh_gateway block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mesh_gateway ConfigEntryServiceDefaults#mesh_gateway}
        :param name: Specifies the name of the service you are setting the defaults for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#name ConfigEntryServiceDefaults#name}
        :param namespace: Specifies the namespace containing the upstream service that the configuration applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#namespace ConfigEntryServiceDefaults#namespace}
        :param partition: Specifies the name of the name of the Consul admin partition that the configuration entry applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#partition ConfigEntryServiceDefaults#partition}
        :param passive_health_check: passive_health_check block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#passive_health_check ConfigEntryServiceDefaults#passive_health_check}
        :param peer: Specifies the peer name of the upstream service that the configuration applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#peer ConfigEntryServiceDefaults#peer}
        :param protocol: Specifies the default protocol for the service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#protocol ConfigEntryServiceDefaults#protocol}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be11e8956bc2a39e79dd12b10853cb936a1157b2d365fec88b73a99522db3ef6)
            check_type(argname="argument balance_outbound_connections", value=balance_outbound_connections, expected_type=type_hints["balance_outbound_connections"])
            check_type(argname="argument connect_timeout_ms", value=connect_timeout_ms, expected_type=type_hints["connect_timeout_ms"])
            check_type(argname="argument envoy_listener_json", value=envoy_listener_json, expected_type=type_hints["envoy_listener_json"])
            check_type(argname="argument limits", value=limits, expected_type=type_hints["limits"])
            check_type(argname="argument mesh_gateway", value=mesh_gateway, expected_type=type_hints["mesh_gateway"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument passive_health_check", value=passive_health_check, expected_type=type_hints["passive_health_check"])
            check_type(argname="argument peer", value=peer, expected_type=type_hints["peer"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if balance_outbound_connections is not None:
            self._values["balance_outbound_connections"] = balance_outbound_connections
        if connect_timeout_ms is not None:
            self._values["connect_timeout_ms"] = connect_timeout_ms
        if envoy_listener_json is not None:
            self._values["envoy_listener_json"] = envoy_listener_json
        if limits is not None:
            self._values["limits"] = limits
        if mesh_gateway is not None:
            self._values["mesh_gateway"] = mesh_gateway
        if name is not None:
            self._values["name"] = name
        if namespace is not None:
            self._values["namespace"] = namespace
        if partition is not None:
            self._values["partition"] = partition
        if passive_health_check is not None:
            self._values["passive_health_check"] = passive_health_check
        if peer is not None:
            self._values["peer"] = peer
        if protocol is not None:
            self._values["protocol"] = protocol

    @builtins.property
    def balance_outbound_connections(self) -> typing.Optional[builtins.str]:
        '''Sets the strategy for allocating outbound connections from upstreams across Envoy proxy threads.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#balance_outbound_connections ConfigEntryServiceDefaults#balance_outbound_connections}
        '''
        result = self._values.get("balance_outbound_connections")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connect_timeout_ms(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#connect_timeout_ms ConfigEntryServiceDefaults#connect_timeout_ms}.'''
        result = self._values.get("connect_timeout_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def envoy_listener_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#envoy_listener_json ConfigEntryServiceDefaults#envoy_listener_json}.'''
        result = self._values.get("envoy_listener_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def limits(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits"]]]:
        '''limits block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#limits ConfigEntryServiceDefaults#limits}
        '''
        result = self._values.get("limits")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits"]]], result)

    @builtins.property
    def mesh_gateway(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway"]]]:
        '''mesh_gateway block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mesh_gateway ConfigEntryServiceDefaults#mesh_gateway}
        '''
        result = self._values.get("mesh_gateway")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway"]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of the service you are setting the defaults for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#name ConfigEntryServiceDefaults#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Specifies the namespace containing the upstream service that the configuration applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#namespace ConfigEntryServiceDefaults#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of the name of the Consul admin partition that the configuration entry applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#partition ConfigEntryServiceDefaults#partition}
        '''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def passive_health_check(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck"]]]:
        '''passive_health_check block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#passive_health_check ConfigEntryServiceDefaults#passive_health_check}
        '''
        result = self._values.get("passive_health_check")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck"]]], result)

    @builtins.property
    def peer(self) -> typing.Optional[builtins.str]:
        '''Specifies the peer name of the upstream service that the configuration applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#peer ConfigEntryServiceDefaults#peer}
        '''
        result = self._values.get("peer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''Specifies the default protocol for the service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#protocol ConfigEntryServiceDefaults#protocol}
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsUpstreamConfigOverrides(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits",
    jsii_struct_bases=[],
    name_mapping={
        "max_concurrent_requests": "maxConcurrentRequests",
        "max_connections": "maxConnections",
        "max_pending_requests": "maxPendingRequests",
    },
)
class ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits:
    def __init__(
        self,
        *,
        max_concurrent_requests: typing.Optional[jsii.Number] = None,
        max_connections: typing.Optional[jsii.Number] = None,
        max_pending_requests: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_concurrent_requests: Specifies the maximum number of concurrent requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_concurrent_requests ConfigEntryServiceDefaults#max_concurrent_requests}
        :param max_connections: Specifies the maximum number of connections a service instance can establish against the upstream. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_connections ConfigEntryServiceDefaults#max_connections}
        :param max_pending_requests: Specifies the maximum number of requests that are queued while waiting for a connection to establish. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_pending_requests ConfigEntryServiceDefaults#max_pending_requests}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcdccf01e9e981cd2fd0a201d750e8b3917e4748b3de87bc9e282b3a2847e050)
            check_type(argname="argument max_concurrent_requests", value=max_concurrent_requests, expected_type=type_hints["max_concurrent_requests"])
            check_type(argname="argument max_connections", value=max_connections, expected_type=type_hints["max_connections"])
            check_type(argname="argument max_pending_requests", value=max_pending_requests, expected_type=type_hints["max_pending_requests"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_concurrent_requests is not None:
            self._values["max_concurrent_requests"] = max_concurrent_requests
        if max_connections is not None:
            self._values["max_connections"] = max_connections
        if max_pending_requests is not None:
            self._values["max_pending_requests"] = max_pending_requests

    @builtins.property
    def max_concurrent_requests(self) -> typing.Optional[jsii.Number]:
        '''Specifies the maximum number of concurrent requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_concurrent_requests ConfigEntryServiceDefaults#max_concurrent_requests}
        '''
        result = self._values.get("max_concurrent_requests")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_connections(self) -> typing.Optional[jsii.Number]:
        '''Specifies the maximum number of connections a service instance can establish against the upstream.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_connections ConfigEntryServiceDefaults#max_connections}
        '''
        result = self._values.get("max_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_pending_requests(self) -> typing.Optional[jsii.Number]:
        '''Specifies the maximum number of requests that are queued while waiting for a connection to establish.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_pending_requests ConfigEntryServiceDefaults#max_pending_requests}
        '''
        result = self._values.get("max_pending_requests")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceDefaultsUpstreamConfigOverridesLimitsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigOverridesLimitsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1353690ade6e287da59fdaa50297ceae7f9216b8395a065ca33258be095f58e3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsUpstreamConfigOverridesLimitsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c48ef6c7018f50f1a815580f0467f2c4914f65626c2e0473ec81d6effd416eaf)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsUpstreamConfigOverridesLimitsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2345dd1c5c7131769754713c2deaee6e9a85cde6d1093bbfe25f9e7660a2599)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b7cdc9aee241ae3c735a3abaa07dac43764da954ae48266ac05254fc4eb15a0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7deb3d73ff2a388dfe6d6066ddd1175fb36759ad390d0195390a96e9e89fd6cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4731fa6909209f9b6bfb5d6bbcd750e927dc05fc47dcd733a8b6a290e7cf3136)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsUpstreamConfigOverridesLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigOverridesLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb22b0ff5bc27a347800b5b44fa90377105ec4e8e273259b9e9570e927901f47)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetMaxConcurrentRequests")
    def reset_max_concurrent_requests(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConcurrentRequests", []))

    @jsii.member(jsii_name="resetMaxConnections")
    def reset_max_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnections", []))

    @jsii.member(jsii_name="resetMaxPendingRequests")
    def reset_max_pending_requests(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPendingRequests", []))

    @builtins.property
    @jsii.member(jsii_name="maxConcurrentRequestsInput")
    def max_concurrent_requests_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConcurrentRequestsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionsInput")
    def max_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxPendingRequestsInput")
    def max_pending_requests_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPendingRequestsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConcurrentRequests")
    def max_concurrent_requests(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConcurrentRequests"))

    @max_concurrent_requests.setter
    def max_concurrent_requests(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd076d9b6630154b943fda3d4c1057126fc3792fef7f36312ab264813ba1c61b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConcurrentRequests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnections")
    def max_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnections"))

    @max_connections.setter
    def max_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__457048927b75b2d02bd99e215eda48b2c6636c04e89bf0fbfe3321e414e6c8f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxPendingRequests")
    def max_pending_requests(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPendingRequests"))

    @max_pending_requests.setter
    def max_pending_requests(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c23c5c060e025f22554ef94cf58c662dbeb8823fef971dcbd9d3d6b320d04ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxPendingRequests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__585e2d07fb02cb8fcccdfd3b21582f7beff35b74aed6cf189467be3b835ab123)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsUpstreamConfigOverridesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigOverridesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6b08f07e00c7bd72715be520c1655c5a111f3a9a6393fd0b11c6812ae3306ebc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsUpstreamConfigOverridesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57c81e206e4475884afa1893299a38f8412bfe489ee109f406a10513bdc8a7cf)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsUpstreamConfigOverridesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d48de7412e2f0ef30298c3739e4d40bf0078ae20be066929db4c2835ad4880d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5eb0aab1fac706c087dbe6623e321380387c50ee095457e0a0fea403309cd0e1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d6e8487f5b122beca62225dfffafd5f3c50d0df1d02a4e71706067974a9b0dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverrides]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverrides]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverrides]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39849825db875875be363c275d8184e81c05357abee8976f096327353a3d8473)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode"},
)
class ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway:
    def __init__(self, *, mode: typing.Optional[builtins.str] = None) -> None:
        '''
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mode ConfigEntryServiceDefaults#mode}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a14680ecc4f130e398019b3294ac11add4d8a163dd44b1f665ca852b6f6d4ee)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#mode ConfigEntryServiceDefaults#mode}.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGatewayList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGatewayList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1f995b14150af8ba86ac2a0a7db67f05a308d14453aedb1556d126dfb75fcae6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGatewayOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27ca91ec20e0fc0a68a0a5a9c971ae2bf4452a2bb13f98a6ba4961efea9808f6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGatewayOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b16e22f3ed81c9c108f586033a6328d110ae9169778a196babe532f2e05b541a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c27f86659360bcce9daae19eef570a276542ca733ba3702aebb6772b7545f5b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__37e579c6a276b0f90694fec64eb73764c4348005fa653dabe0a506d41dcdf4ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f86d0fa52348f110a2961c73d9419a5eed5aa18a5657c2e3f079c09273a5fc3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGatewayOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGatewayOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3a7284e7ae609d5a684e08b50cf1a0b382ac7413ce570a3bcd620c22cbc7f921)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5eefcfba368ad40a1041f194563baa4fee3456774cd7e5d2fbd878e6ab2187f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4bb12ee8fdf985907d1a9d42b667d578deae5ac9b2980cfe6f703e0e0ab589c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsUpstreamConfigOverridesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigOverridesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f5ef2a024992b7b69fc68753b9560c248ad9beb062d2cfa0ec83ca1d481cba62)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putLimits")
    def put_limits(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80a2ccdeb4cea8fb0dfba014696f82d12e96322046e52565e766ef60df2f32f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLimits", [value]))

    @jsii.member(jsii_name="putMeshGateway")
    def put_mesh_gateway(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f279269a646cf7d1c091802d6fa105547dc8fe660284d10ba56edd44f1362794)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMeshGateway", [value]))

    @jsii.member(jsii_name="putPassiveHealthCheck")
    def put_passive_health_check(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28a043298c47db0e57f4504abf3966baa03ea6683a17b4ba186118cbdf0a855f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPassiveHealthCheck", [value]))

    @jsii.member(jsii_name="resetBalanceOutboundConnections")
    def reset_balance_outbound_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBalanceOutboundConnections", []))

    @jsii.member(jsii_name="resetConnectTimeoutMs")
    def reset_connect_timeout_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectTimeoutMs", []))

    @jsii.member(jsii_name="resetEnvoyListenerJson")
    def reset_envoy_listener_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvoyListenerJson", []))

    @jsii.member(jsii_name="resetLimits")
    def reset_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLimits", []))

    @jsii.member(jsii_name="resetMeshGateway")
    def reset_mesh_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMeshGateway", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPartition")
    def reset_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartition", []))

    @jsii.member(jsii_name="resetPassiveHealthCheck")
    def reset_passive_health_check(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassiveHealthCheck", []))

    @jsii.member(jsii_name="resetPeer")
    def reset_peer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeer", []))

    @jsii.member(jsii_name="resetProtocol")
    def reset_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocol", []))

    @builtins.property
    @jsii.member(jsii_name="limits")
    def limits(self) -> ConfigEntryServiceDefaultsUpstreamConfigOverridesLimitsList:
        return typing.cast(ConfigEntryServiceDefaultsUpstreamConfigOverridesLimitsList, jsii.get(self, "limits"))

    @builtins.property
    @jsii.member(jsii_name="meshGateway")
    def mesh_gateway(
        self,
    ) -> ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGatewayList:
        return typing.cast(ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGatewayList, jsii.get(self, "meshGateway"))

    @builtins.property
    @jsii.member(jsii_name="passiveHealthCheck")
    def passive_health_check(
        self,
    ) -> "ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheckList":
        return typing.cast("ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheckList", jsii.get(self, "passiveHealthCheck"))

    @builtins.property
    @jsii.member(jsii_name="balanceOutboundConnectionsInput")
    def balance_outbound_connections_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "balanceOutboundConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="connectTimeoutMsInput")
    def connect_timeout_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "connectTimeoutMsInput"))

    @builtins.property
    @jsii.member(jsii_name="envoyListenerJsonInput")
    def envoy_listener_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "envoyListenerJsonInput"))

    @builtins.property
    @jsii.member(jsii_name="limitsInput")
    def limits_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits]]], jsii.get(self, "limitsInput"))

    @builtins.property
    @jsii.member(jsii_name="meshGatewayInput")
    def mesh_gateway_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway]]], jsii.get(self, "meshGatewayInput"))

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
    @jsii.member(jsii_name="passiveHealthCheckInput")
    def passive_health_check_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck"]]], jsii.get(self, "passiveHealthCheckInput"))

    @builtins.property
    @jsii.member(jsii_name="peerInput")
    def peer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "peerInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="balanceOutboundConnections")
    def balance_outbound_connections(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "balanceOutboundConnections"))

    @balance_outbound_connections.setter
    def balance_outbound_connections(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__746756de17d5d35cba5feccc875e4523a7a9eb613075d22f3d99a62b36502af1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "balanceOutboundConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectTimeoutMs")
    def connect_timeout_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "connectTimeoutMs"))

    @connect_timeout_ms.setter
    def connect_timeout_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16f6615b366a1e90228893f4657402608e8f910e7b19357b7f6f3d40196a95ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectTimeoutMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="envoyListenerJson")
    def envoy_listener_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "envoyListenerJson"))

    @envoy_listener_json.setter
    def envoy_listener_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cfcaedff72dd2ec83135bb25a2e7b66b68e26c3d40b2436a686a3a234499d12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "envoyListenerJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01a73d4957766d63527acf5ffff87c24ead01478d56310bbb19e242ff8db2572)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e04928d79b783ad8fdc5da37de78e3d13b29def43a8ebe0025072451dd0d1852)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partition")
    def partition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partition"))

    @partition.setter
    def partition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9928b75fea33554acf207d4d23444c0960c293db35816f64963be40212647364)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="peer")
    def peer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "peer"))

    @peer.setter
    def peer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8789087d9d94758c8c8435309c4074e0b928725faa3f7349e7a94ea4b8f2dc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "peer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d2a0a3756bd77434f57ce1a2b725298479348c4a749748bbc6ab7e88435a615)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverrides]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverrides]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverrides]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c102a21a160bfe89febb22b00141a21f56df0081cbdfd5914b5df9b8424153c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck",
    jsii_struct_bases=[],
    name_mapping={
        "base_ejection_time": "baseEjectionTime",
        "enforcing_consecutive5_xx": "enforcingConsecutive5Xx",
        "interval": "interval",
        "max_ejection_percent": "maxEjectionPercent",
        "max_failures": "maxFailures",
    },
)
class ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck:
    def __init__(
        self,
        *,
        base_ejection_time: typing.Optional[builtins.str] = None,
        enforcing_consecutive5_xx: typing.Optional[jsii.Number] = None,
        interval: typing.Optional[builtins.str] = None,
        max_ejection_percent: typing.Optional[jsii.Number] = None,
        max_failures: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param base_ejection_time: Specifies the minimum amount of time that an ejected host must remain outside the cluster before rejoining. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#base_ejection_time ConfigEntryServiceDefaults#base_ejection_time}
        :param enforcing_consecutive5_xx: Specifies a percentage that indicates how many times out of 100 that Consul ejects the host when it detects an outlier status. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#enforcing_consecutive_5xx ConfigEntryServiceDefaults#enforcing_consecutive_5xx}
        :param interval: Specifies the time between checks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#interval ConfigEntryServiceDefaults#interval}
        :param max_ejection_percent: Specifies the maximum percentage of an upstream cluster that Consul ejects when the proxy reports an outlier. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_ejection_percent ConfigEntryServiceDefaults#max_ejection_percent}
        :param max_failures: Specifies the number of consecutive failures allowed per check interval. If exceeded, Consul removes the host from the load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_failures ConfigEntryServiceDefaults#max_failures}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f83af2df5cf5a6a06b3610f4969a7b7f165a16042a7dfab2602d1853d9d0f2e)
            check_type(argname="argument base_ejection_time", value=base_ejection_time, expected_type=type_hints["base_ejection_time"])
            check_type(argname="argument enforcing_consecutive5_xx", value=enforcing_consecutive5_xx, expected_type=type_hints["enforcing_consecutive5_xx"])
            check_type(argname="argument interval", value=interval, expected_type=type_hints["interval"])
            check_type(argname="argument max_ejection_percent", value=max_ejection_percent, expected_type=type_hints["max_ejection_percent"])
            check_type(argname="argument max_failures", value=max_failures, expected_type=type_hints["max_failures"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if base_ejection_time is not None:
            self._values["base_ejection_time"] = base_ejection_time
        if enforcing_consecutive5_xx is not None:
            self._values["enforcing_consecutive5_xx"] = enforcing_consecutive5_xx
        if interval is not None:
            self._values["interval"] = interval
        if max_ejection_percent is not None:
            self._values["max_ejection_percent"] = max_ejection_percent
        if max_failures is not None:
            self._values["max_failures"] = max_failures

    @builtins.property
    def base_ejection_time(self) -> typing.Optional[builtins.str]:
        '''Specifies the minimum amount of time that an ejected host must remain outside the cluster before rejoining.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#base_ejection_time ConfigEntryServiceDefaults#base_ejection_time}
        '''
        result = self._values.get("base_ejection_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enforcing_consecutive5_xx(self) -> typing.Optional[jsii.Number]:
        '''Specifies a percentage that indicates how many times out of 100 that Consul ejects the host when it detects an outlier status.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#enforcing_consecutive_5xx ConfigEntryServiceDefaults#enforcing_consecutive_5xx}
        '''
        result = self._values.get("enforcing_consecutive5_xx")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interval(self) -> typing.Optional[builtins.str]:
        '''Specifies the time between checks.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#interval ConfigEntryServiceDefaults#interval}
        '''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_ejection_percent(self) -> typing.Optional[jsii.Number]:
        '''Specifies the maximum percentage of an upstream cluster that Consul ejects when the proxy reports an outlier.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_ejection_percent ConfigEntryServiceDefaults#max_ejection_percent}
        '''
        result = self._values.get("max_ejection_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_failures(self) -> typing.Optional[jsii.Number]:
        '''Specifies the number of consecutive failures allowed per check interval.

        If exceeded, Consul removes the host from the load balancer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_defaults#max_failures ConfigEntryServiceDefaults#max_failures}
        '''
        result = self._values.get("max_failures")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheckList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheckList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cc4f12c354df1e903bbf8fc087b9788df331ad99697801b937dd386947cda15f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheckOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ad72d21e57d0e3fa692ebc6092f0ecf783a97d87af609a56d6e6ed1a1ba4a6a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheckOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e07a55093d1db0b5d38fd258e32d0212a434b06b3089244948aa44fa8d2c46fe)
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
            type_hints = typing.get_type_hints(_typecheckingstub__44ee9d2e364a07356170ea3b769e1d2690f9b29784cfb7f0652db24724a83a55)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f4475c57a44121effa935292011c938126ae80d46ced6a6ca08a75714ef8047d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe38e4473a21a84afa426ae03c76bc679d1a5d500c0caef8a6e461b708e2666a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheckOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceDefaults.ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheckOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fa5fda93d4eb0f755e6a30dfc2d1a7db46f9d6ca02e2e2a39988dfc67a7c1b3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetBaseEjectionTime")
    def reset_base_ejection_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaseEjectionTime", []))

    @jsii.member(jsii_name="resetEnforcingConsecutive5Xx")
    def reset_enforcing_consecutive5_xx(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforcingConsecutive5Xx", []))

    @jsii.member(jsii_name="resetInterval")
    def reset_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterval", []))

    @jsii.member(jsii_name="resetMaxEjectionPercent")
    def reset_max_ejection_percent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxEjectionPercent", []))

    @jsii.member(jsii_name="resetMaxFailures")
    def reset_max_failures(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxFailures", []))

    @builtins.property
    @jsii.member(jsii_name="baseEjectionTimeInput")
    def base_ejection_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseEjectionTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="enforcingConsecutive5XxInput")
    def enforcing_consecutive5_xx_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "enforcingConsecutive5XxInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalInput"))

    @builtins.property
    @jsii.member(jsii_name="maxEjectionPercentInput")
    def max_ejection_percent_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxEjectionPercentInput"))

    @builtins.property
    @jsii.member(jsii_name="maxFailuresInput")
    def max_failures_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxFailuresInput"))

    @builtins.property
    @jsii.member(jsii_name="baseEjectionTime")
    def base_ejection_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseEjectionTime"))

    @base_ejection_time.setter
    def base_ejection_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b74457005f8fd5ba7d96eaee8f711340e50e0fadb4b261058723257b20c157f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseEjectionTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enforcingConsecutive5Xx")
    def enforcing_consecutive5_xx(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "enforcingConsecutive5Xx"))

    @enforcing_consecutive5_xx.setter
    def enforcing_consecutive5_xx(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfad7a39742f159f16d092e32c41f19cbec25377787b803285abd7878b1b9165)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforcingConsecutive5Xx", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="interval")
    def interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8197674106bd2afddd8eb8ce25e91b21cd7382ed320cdd4167d6f0d809c218e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "interval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxEjectionPercent")
    def max_ejection_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxEjectionPercent"))

    @max_ejection_percent.setter
    def max_ejection_percent(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62b802316e78b0cfe1f6873579e41d9cdcc42264fff1a591b1e194647832d789)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxEjectionPercent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxFailures")
    def max_failures(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxFailures"))

    @max_failures.setter
    def max_failures(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea646a9dae1ec733258d752f49e1062e00a67e8f31ffc5697f297ec6e08c58d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxFailures", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c30251b0fec461489929eae1d55520660833960de594d11cf559360c30158d4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ConfigEntryServiceDefaults",
    "ConfigEntryServiceDefaultsConfig",
    "ConfigEntryServiceDefaultsDestination",
    "ConfigEntryServiceDefaultsDestinationList",
    "ConfigEntryServiceDefaultsDestinationOutputReference",
    "ConfigEntryServiceDefaultsEnvoyExtensions",
    "ConfigEntryServiceDefaultsEnvoyExtensionsList",
    "ConfigEntryServiceDefaultsEnvoyExtensionsOutputReference",
    "ConfigEntryServiceDefaultsExpose",
    "ConfigEntryServiceDefaultsExposeList",
    "ConfigEntryServiceDefaultsExposeOutputReference",
    "ConfigEntryServiceDefaultsExposePaths",
    "ConfigEntryServiceDefaultsExposePathsList",
    "ConfigEntryServiceDefaultsExposePathsOutputReference",
    "ConfigEntryServiceDefaultsMeshGateway",
    "ConfigEntryServiceDefaultsMeshGatewayList",
    "ConfigEntryServiceDefaultsMeshGatewayOutputReference",
    "ConfigEntryServiceDefaultsTransparentProxy",
    "ConfigEntryServiceDefaultsTransparentProxyList",
    "ConfigEntryServiceDefaultsTransparentProxyOutputReference",
    "ConfigEntryServiceDefaultsUpstreamConfig",
    "ConfigEntryServiceDefaultsUpstreamConfigDefaults",
    "ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits",
    "ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimitsList",
    "ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimitsOutputReference",
    "ConfigEntryServiceDefaultsUpstreamConfigDefaultsList",
    "ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway",
    "ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGatewayList",
    "ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGatewayOutputReference",
    "ConfigEntryServiceDefaultsUpstreamConfigDefaultsOutputReference",
    "ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck",
    "ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheckList",
    "ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheckOutputReference",
    "ConfigEntryServiceDefaultsUpstreamConfigList",
    "ConfigEntryServiceDefaultsUpstreamConfigOutputReference",
    "ConfigEntryServiceDefaultsUpstreamConfigOverrides",
    "ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits",
    "ConfigEntryServiceDefaultsUpstreamConfigOverridesLimitsList",
    "ConfigEntryServiceDefaultsUpstreamConfigOverridesLimitsOutputReference",
    "ConfigEntryServiceDefaultsUpstreamConfigOverridesList",
    "ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway",
    "ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGatewayList",
    "ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGatewayOutputReference",
    "ConfigEntryServiceDefaultsUpstreamConfigOverridesOutputReference",
    "ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck",
    "ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheckList",
    "ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheckOutputReference",
]

publication.publish()

def _typecheckingstub__103b5138df57859f622f0e85dd58e8f15aa4ef62b4f6202d4fbf13705e3e7709(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    expose: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsExpose, typing.Dict[builtins.str, typing.Any]]]],
    name: builtins.str,
    protocol: builtins.str,
    balance_inbound_connections: typing.Optional[builtins.str] = None,
    destination: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsDestination, typing.Dict[builtins.str, typing.Any]]]]] = None,
    envoy_extensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsEnvoyExtensions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    external_sni: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    local_connect_timeout_ms: typing.Optional[jsii.Number] = None,
    local_request_timeout_ms: typing.Optional[jsii.Number] = None,
    max_inbound_connections: typing.Optional[jsii.Number] = None,
    mesh_gateway: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsMeshGateway, typing.Dict[builtins.str, typing.Any]]]]] = None,
    meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    mode: typing.Optional[builtins.str] = None,
    mutual_tls_mode: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    transparent_proxy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsTransparentProxy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    upstream_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__488baec34fb666dc15bac618da890ab9554e0aec38f3156eeb6d1bbc86690880(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6257b635e58ed9073ae40b2a11d39754e09b12fd9919449f578087256edf51c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsDestination, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41312dbb2ff66b2b18c6624f295eb4ddd1a320be82cfda52ba88cfa83b366efd(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsEnvoyExtensions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95edae8672158774ea9f85d8eeb825374031a35a0710b226922c137844385434(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsExpose, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b64dd2572570a8ef77201ebe329ccfffb41b8516acda75cf5d6821df955e66d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsMeshGateway, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91ba5006733111f92c3f6b26b3c1f6825e2f978fa43f707de17e7c64ab0512aa(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsTransparentProxy, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0be20b8da1f36860fc84d4e6ddb13adbf1179abf24b6bcbda496840f60b4e950(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f730fdda2239f58f33863a456e625cc8f6bb3fc69df62e17c01249b3a4a8d0c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e0af6e3975fad1afaa297ee28884a74ea4bcab3da09d0fce2687d72d79261cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6985c8af1482454a62a0c43a76052e3dab11c285819cedaf6671bd41c00afff0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13b3c0a776460d23971f7ae3a5bf49e48e3473e36352dc54b1a962783723b98d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__498e8455f588b4a744b8080859f30fa0a4de1af900bc781f8217a2e535767db3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f905ee692913be163dcf489cedab8add9675498e6fb8c57287033e9315019a0e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__398871b5b5ae6e28b8d7e507908908dd54e1112c1105c9115e71945ed6d7ddf1(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__640cd22463d572d4394b3a4584b67b713dcc392e811303499ede935f86bc3e38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc22ffa66c273d55520022f38c5f6aa2abdebd1b79304ca5e056dea5d3f27b1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__420967af8246f765995a64120f5ef7f09dd307b7a0c07ac87d215825f42e6f58(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb4fb6e8bb7879e69d012ba472ed43846ba60ebdca5fcccba82efb451bc54207(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__906f9e716b2cb4a4bdf68167c898b98cbaddc53a3a8937d46c71ca72151d15a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2355093cba566e5b9ea77f7187e8d157171d439a93abd5ad937c50f4a75b3fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00af784d1d6c1e03b72befbd87250cb7cf5d5be485d5e2346becc6648c2f6cf2(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    expose: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsExpose, typing.Dict[builtins.str, typing.Any]]]],
    name: builtins.str,
    protocol: builtins.str,
    balance_inbound_connections: typing.Optional[builtins.str] = None,
    destination: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsDestination, typing.Dict[builtins.str, typing.Any]]]]] = None,
    envoy_extensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsEnvoyExtensions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    external_sni: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    local_connect_timeout_ms: typing.Optional[jsii.Number] = None,
    local_request_timeout_ms: typing.Optional[jsii.Number] = None,
    max_inbound_connections: typing.Optional[jsii.Number] = None,
    mesh_gateway: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsMeshGateway, typing.Dict[builtins.str, typing.Any]]]]] = None,
    meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    mode: typing.Optional[builtins.str] = None,
    mutual_tls_mode: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    transparent_proxy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsTransparentProxy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    upstream_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb23bb4bcfd37b9e002f9b38ec7d1122f28f6580a35b15ad66f3b62bcd2e0fb3(
    *,
    addresses: typing.Sequence[builtins.str],
    port: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90429b8bfa45a1c469fa2c7e681ab5412bfa0c6d888b7d12f42d0e3083b545df(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__340d36957354c53c3a8eea886448378dfd19455a8979a7b73c72069ac018c66c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98cfbd0fb71f9894be9f1a633fb4bd7c5f6e71364d79f48b5bafadc5284fa6a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b4e8f92eb74d3543626879ef145f296d25b838e7c728cb3a2abc74e4fa03e01(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be9cbb529bd18e04392e0c27aa2c39be790a25e342d41135849be82012a9c7f5(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__725c78b46e8ef9f4eccceae1fee9ccbc0768ba719be9b39e7e0f7c65ed9ffb6d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsDestination]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b3bc9174d7aeaa20ce9ec7051ea47a40f49e4845825210c909ba49283f882a4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c06a15022b169c0ee8f19c8f20ae74beb41c8899b331439586d09f325cae46bf(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f4201ebe1b10cd1d8ef075087a10d91d87ebefa424903029aa2d2871e22c06b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61d9ba5533539843316ae57fba15c129b437d728289296e29fe7b83adf3f41cc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsDestination]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b6b539f50a2af306483c5b22c8c19d4bb2b4e4ee37ad779579e26a872f248c8(
    *,
    arguments: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    consul_version: typing.Optional[builtins.str] = None,
    envoy_version: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5179e9cf80f7d47f65a6427b82fde2742a5488714c9bdc2b73f065d5f9a88bce(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1901da79e20935b72ab1fa2853cad4b4279e0d93f64c5e6a1db8b3a517d1e1bd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1374d959e3e1cec5c5d758fab0965138fe1e846cb924a27679a95486e3f19915(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32fe0164434ba2faa93479fd60ab379f287d1b6194af16c538273522bdcf43a9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0e1e7c6b959f92d30965c8493d67dbeaf6cfd116faab54ebc12b380d5444190(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b308b496a9e38c0c60841530ebf851747a693bbea9c55d13f6fe392e0899523(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsEnvoyExtensions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d6c52aa48384828900c58eb31865b2e4243715159adc099099a65271b42a91d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9a42dc1641977311728f511b2a3ab9048098ecd8f9b9f0b8c75ac2995780575(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3211918f7ddbfaf4e4e7658be6fc8290d037dbb6ec5a40f92db74291a071ae43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__600f53b960796c2d8b3b12adf555e8d19e6bf75730242b246e14b26afef2c551(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3448e660cfe56c7fdf6850a52bcb130c1a8292a8d8a540ea0789f5fa339dab8b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c410c614ec65ddf05045bdcc6a980bd8153dff5309c9cbe2fe211da63f9ab47b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66582135e432884594dfa5d49fedfa7bb53c59d0637b886e96c772ca9bdbda35(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsEnvoyExtensions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d6a57fd7f5a954ce72b46f67cacbd5085b9c92a2193194522f6cf74cf3dc955(
    *,
    checks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    paths: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsExposePaths, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82dac5c1cd3d1389f7feb2c73ad1762485629996abf9b778ce0d23cb8b722b0b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6be5ad771d78feccdf0a019da5f939b2f2787358b62b9efa160e5fa229372b6d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87e8ea0815d6592d0d7eff7fa9fb7bba3cd3b83255e1073db841ae7476645a3d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa8281592452b7dd410721e3e40b649486a890f244dcfee5402d34f8a74258e0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__babf51f57a2bad6165f5a60dfa71e9e96cb88853e8b3b1bddc6fa3aa91cce0eb(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eec24632ed9833d7b3317300b8f4669929d71ef0babec0438037637ebca0e370(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsExpose]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e72b8aa1edf7f1940844f61779ae9cdc10c574fb71b9f602bd195a8160608b3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d4bf64e051fec41fd966197c972eb54b8adfed5ea65f4ddc3e0839acf0c6228(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsExposePaths, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c97712c6284e62fe83651f02300175debd67145ff56ae2e4064e86026de1e755(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f07cc7dc35dd485d5e74f7799824c8c8789f70fb1590b058e269f49bf3a2d1e4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsExpose]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb28049575f77108d6e1f0eb3448601cf66416c310f01a7324406c6a54a6c3ab(
    *,
    listener_port: typing.Optional[jsii.Number] = None,
    local_path_port: typing.Optional[jsii.Number] = None,
    path: typing.Optional[builtins.str] = None,
    protocol: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25b38c331ba8461b1ad68e09532eb952ecb2dfef8a9208021f0b69b090dfc05a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eb2836ec2928fa311234d2ed4296899be13fa359fab496896db01ef1ac69ae4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aea165c33756ff4aefde309b428488824360102a2001b473ef2c03fad86884d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__654209b9beda891a5fb21c53db4c027b29516805732a5feaf4762ad0f96c1508(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4002364ec4378135cd1d6b5b4a981328c30d3c41885e76228308c700f9c7ac29(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78c799d047f14214bef8a8181f93634d335b6102f6744dd3e17734f79b3d79b4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsExposePaths]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad95893bdb1093e8616ddf4a24e2ba856ab711cb11ac13f5b385240defd2e9c1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5519b60251b46a9af7d828a4e30db0b5deb2aee10e9cf155d319af8181fb9255(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7918dd3298679cefaaec279c773e9da70955334d08cadc3248edffedd8479ce3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4de97b5d48a7945e00e6ebb5e8b19f47b76e9bb6e566c8a945450ad448b3193b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e4886aeebf2a93252ade71530d91ea96a169495ede41fe519db0907792267dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d74aee6b41e39b3c54404f5d956b8542ac048973436e44c9455cc2166e6bbcc0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsExposePaths]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e831bd84addc4bdb8adb1775be7a9fd810e08becda905097b7746261840d39b(
    *,
    mode: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac3e6b9ac8c7295102076817aa6f76ecdf14b52a2813620b2744f2bfc937b6ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a3aab0e8333ae0b75c4e66897da0e3a5c7a48f8939c6003ec96dd9cbfb62710(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e15f80e83a0d5d2f06dcba03e41aa562c1dbcf0f06b2e65525c2254c32ccafdd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6664a833902cde924082d86e9bb85c9e0a38ffc009697d6509ee0fb29a935435(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f106f3fe05208fbe895f2070d7d7bb5af03189d2a0232d44b0529d4b21751849(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__534e8dfc5dbf9b30ee1605240449409a89d4fe88b434e665c6da6df8fa2c73a5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsMeshGateway]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c42c9e6464a0652fca62e573029d546fce3b5d8b33b230865f548da3b266c6a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c904bd3bd9303030ac99786decd3c7dff9914282fb86e1fa20e5c00d4391b8cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93119fa38a4334efada2df94f50c5f900ef9904392b64840de1f2d729156899d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsMeshGateway]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__330b96e3084a1de6fda549b58a9a28c140d1723fefbfdf40dc8a6f8e73b1433a(
    *,
    dialed_directly: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    outbound_listener_port: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa3c1165cfcec0d86b9edc347b2cd7085f5a9860ecd12698b43acbc49a58569e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0262c0b0370a5de48fe1f9c11bd5ec7bfa395321d3afeebf8cb0861565985195(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f41523c88b6e9872167d2f6d0e7a0c23fac03efa906d98551b070556c1477a91(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ff78ecbc6cb2e518eb14e779f13cd690b57c6c517d5d6796692ad061f588e53(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6258cf10bbc7f84bb69034c742c1e401e755284fff9f6ffcb68b40f2e9dc5ae2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d437c9105b5c2f6e009dc57a7ce3c9774fb9ed0852379815ae1498caa4f85929(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsTransparentProxy]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6350efe9c9e285b33f4a4956562817a442d91835a3e27789a36e3dde31fd013(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__825902608d812bab7bc9ecb16d811ddaaf10ff19285bbf36544e61ab4a925fab(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e64afa724288800ec318c258bba74d20f44056ed688559b0a82fdd5dfd121492(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__886377c0e6071467d3ca34b0a67cb7d4679f093639303e62c9d143d8d9e48b6a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsTransparentProxy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a9d2091e0bdd200f238cfc0f1a7e7c917c3d7640ac28bbb5e1446f3ecc0df0f(
    *,
    defaults: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigDefaults, typing.Dict[builtins.str, typing.Any]]]]] = None,
    overrides: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigOverrides, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c0f11deb789c9da973360d2fa3454d7328342fe3311eae9fbcefe810e618dc6(
    *,
    balance_outbound_connections: typing.Optional[builtins.str] = None,
    connect_timeout_ms: typing.Optional[jsii.Number] = None,
    limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits, typing.Dict[builtins.str, typing.Any]]]]] = None,
    mesh_gateway: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway, typing.Dict[builtins.str, typing.Any]]]]] = None,
    passive_health_check: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck, typing.Dict[builtins.str, typing.Any]]]]] = None,
    protocol: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff568a80f5f3f605d973413b31938c57426701978c6cdb018e2752f492140d28(
    *,
    max_concurrent_requests: typing.Optional[jsii.Number] = None,
    max_connections: typing.Optional[jsii.Number] = None,
    max_pending_requests: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cf7b3e1472f5ade4bc60d672e90ef8d610bebcad85d84b57b34a0ec4afec411(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53b22a2ad4c7985cac8957a5874506a7b371afcceb83c40ff7c7ba177bf2cb01(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ceb833ca7875a9d56683f07f0ed9146fa0382bec5bd7aa0427feeb1c93e1e30a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d441e82634228170ad8e1e47e505f89fc384f589bc75857beb67363251e28676(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56ad63cf507b8f5c2a312739a1bf4c6c3dff1ea567cfba66e66411fe895eba12(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1887d5380811e1cc71c49629b3c1f6ab745f9bd7ae28ea59b14fee7e36a8fb3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__638d5d7093eb2cb17ac3a3540b88060577e6e33bc1b97c3ed1dab3d0ff92ede1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2f5df822a2e66eca5c7c7dc920dc081e5168bf56f7000b293d8808aae370aee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a09640149eb7230253257c9444b7a49c552ec36b37e5aa30c31d7a0f75a829c6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff534aff6583b6d3208a82d7a22cb8c641a81d8a7de5f0ac54c317698013a328(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7ccfaa9f4e43a0365465df795745af11d618fdd13cc3d25de8e71d4e2e92dbb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05a4a342bf3e5fb48f6c7e0e44aca20ed1d603855ec3b6f1808306f8d83097c8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80f890a3626bc1a8f4b267a6caf1981a3f79712e66b97dc8b17c1f93d91a6ebc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d256a92e52b4722e59b11220e76f833531f763dc07e36651f6a7cc735d2f414d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3ceb5e538162a2e23cc6566fb9e726c5005ed5f378c24c6de067b686da65f00(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__044648bc5a1b6e0c0b3d2915826f209d1db2e64ebc8734c9bbd01aa911682f7d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ee252cc3a47d092aca35baa9a69aa15fbdb19fad631ecc94a9472db710729d9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaults]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a00ee6085bd9e94e4b05a7f1ff74f51e7ac48003580cc5082d21f88f31a1bdf8(
    *,
    mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7e093badf68ef9726d530a2a76996a1f788cb373bfd8a143437bc53419bc7be(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e2b75db490d6e72579393999d9a5c7688c488bd161c961f812677caecef4c05(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2db8b2dbbb87e9557892b87660f27571aaa279d073ce115f3075b5a47661b2b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e839d206ef76dfcd3d2cc68fb1ed1d610ae9f9becde061566f15e1b13849ac33(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47a58027fd59adac8c35a8cbddd0bc79475f2dc7081be49770be64dc99e8e60d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4b70a4fea2ff1f7e1322d8f89753dae13e5bf7a78886b9ca69c9be417930709(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b830a3b001289b660d2e82ba6be569f1d23215f70cec3a25b8c01af297d5a930(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aeced4960d4ffe798d35d0a1ad9839f2d759ac21bc1f2f263306aa044a292d42(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73f0636a93b8e3a55b391012957fe1ef9bcda068a1f0b9b8258ba5fa6746bc5f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd16a2f56307210c16a7e2268da9018fb3783f10a9cab7cf4782039a9790bb2b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02518937086ad33ca22c070dd3df9d43e6dda12ad0b6182c7477837fe6d85005(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigDefaultsLimits, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baf3e66c22f3580c4e62897c9950b0fe79e24b87d01f24d1fdc359ab8307036a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigDefaultsMeshGateway, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47c5d4da72a43e56e5b79cd1eed2a57672546e4370ecbced655f55f2546339d0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77b8799e65dd48b73832e0b757f185e44d917bd78b0831789d7cf5c24b61b062(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cc651f65cf6829062964e570232fc909524f9fb3e202dfe896ffccff963e2b7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94f985f0b48ead2217807e0bd6c87981ae664eedc167515df4fe095f801fe11b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f36b762530f649ccfdfaa181f13649754c96d9be25a171d4e77c5c2a83380335(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaults]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11b2deaaf603afabdda39a2388decdd694dba65233b1332b41483be7e596a6d5(
    *,
    base_ejection_time: typing.Optional[builtins.str] = None,
    enforcing_consecutive5_xx: typing.Optional[jsii.Number] = None,
    interval: typing.Optional[builtins.str] = None,
    max_ejection_percent: typing.Optional[jsii.Number] = None,
    max_failures: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccea6a3db6a0fcee263c689a57611c6cd15efe95bc7bc17240ceca861943a050(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17ad115e30990111987714c00590b0d226ff666724cb973d39a93e080a6679be(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e9e223f9eee88ad20c3bd1360bafd6c06c6e7772ee9bb5e0982cf990e7946c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94139cce8723c9cd92ffb5b2d52a516842e3d0331368429e8fbf77eaf4295143(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__695293ff8f371c9d66e6c20b3bd2d1d47fd7804dd5648230ee83496539f33579(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb42f05adfe5eecf3ee8a5ab0d383a5b411bc3dd2e7f142d3aaa8fb87cb2a998(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__150a8ed5abaebee4e8b404e9226ba7ad65e9b68a2b53896d653e7e1419eed8d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a43f7bf19b49b3b404cacfe6738d4ca7585ddc51bcb2924ea7b6edf80e8cb611(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c7d6cdb99fc9242faa53d99e2a90754a31d5254bf8bf699c548b6272b80bc0d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3b67ab4827d7eddbce6eb6541f66850a8f1a80bbd48a8bf968584fe70161538(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a78301ea819845ab9d067fd3de91d1a5ab99ac04946ec1fe973835b1e7f79962(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38f368a370683ad7bc9f447c3be68ce1b6a10dd9f290fe8873d7527f801a3a85(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b732185f8c4dc97c8ffea2842ccc517052791cae17a5e3f23bc634bfa9a0490(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigDefaultsPassiveHealthCheck]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b75e945fddc4d687907a7b3c746bbf5c955384682149bad8711b8739a58dfdc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47e9c2201aef57be720e8fdcebfe675c875fe7023c2b6d74abbe499ae4df7ec4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75afc77954094ce320f277564670f4d6dd5b353aabe834f9d7df8ef576a7eeed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__027b715ac365b5fa7c593ab1fdea6db4f255e2a02027909652f1049f0779397e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ab8247536af76da9bc5b727e64449ddee0ed72e021e0c1a9a2f4de404273e0a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86d2433b092819de505447467bd8474f2b1d81963edae5a90b56f5afc64c7c77(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03848903920380c21dc7bf91ff45f82c04dcbe46fce38307629384097632877a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8a100793e2f6278b2d750921cbc3f6a2bfccbbe0b5c85f9d32498d5498c6648(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigDefaults, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__551836c97a270dcf4a8c1429360c2638eead5d852047e74a9c4af857ef8e7471(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigOverrides, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dd9221fd0e484de8368c9a1252ea860dfcca6bfc071d2b2529b0e552669b7ca(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be11e8956bc2a39e79dd12b10853cb936a1157b2d365fec88b73a99522db3ef6(
    *,
    balance_outbound_connections: typing.Optional[builtins.str] = None,
    connect_timeout_ms: typing.Optional[jsii.Number] = None,
    envoy_listener_json: typing.Optional[builtins.str] = None,
    limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits, typing.Dict[builtins.str, typing.Any]]]]] = None,
    mesh_gateway: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    passive_health_check: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck, typing.Dict[builtins.str, typing.Any]]]]] = None,
    peer: typing.Optional[builtins.str] = None,
    protocol: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcdccf01e9e981cd2fd0a201d750e8b3917e4748b3de87bc9e282b3a2847e050(
    *,
    max_concurrent_requests: typing.Optional[jsii.Number] = None,
    max_connections: typing.Optional[jsii.Number] = None,
    max_pending_requests: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1353690ade6e287da59fdaa50297ceae7f9216b8395a065ca33258be095f58e3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c48ef6c7018f50f1a815580f0467f2c4914f65626c2e0473ec81d6effd416eaf(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2345dd1c5c7131769754713c2deaee6e9a85cde6d1093bbfe25f9e7660a2599(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b7cdc9aee241ae3c735a3abaa07dac43764da954ae48266ac05254fc4eb15a0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7deb3d73ff2a388dfe6d6066ddd1175fb36759ad390d0195390a96e9e89fd6cd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4731fa6909209f9b6bfb5d6bbcd750e927dc05fc47dcd733a8b6a290e7cf3136(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb22b0ff5bc27a347800b5b44fa90377105ec4e8e273259b9e9570e927901f47(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd076d9b6630154b943fda3d4c1057126fc3792fef7f36312ab264813ba1c61b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__457048927b75b2d02bd99e215eda48b2c6636c04e89bf0fbfe3321e414e6c8f9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c23c5c060e025f22554ef94cf58c662dbeb8823fef971dcbd9d3d6b320d04ac(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__585e2d07fb02cb8fcccdfd3b21582f7beff35b74aed6cf189467be3b835ab123(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b08f07e00c7bd72715be520c1655c5a111f3a9a6393fd0b11c6812ae3306ebc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57c81e206e4475884afa1893299a38f8412bfe489ee109f406a10513bdc8a7cf(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d48de7412e2f0ef30298c3739e4d40bf0078ae20be066929db4c2835ad4880d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eb0aab1fac706c087dbe6623e321380387c50ee095457e0a0fea403309cd0e1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d6e8487f5b122beca62225dfffafd5f3c50d0df1d02a4e71706067974a9b0dc(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39849825db875875be363c275d8184e81c05357abee8976f096327353a3d8473(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverrides]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a14680ecc4f130e398019b3294ac11add4d8a163dd44b1f665ca852b6f6d4ee(
    *,
    mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f995b14150af8ba86ac2a0a7db67f05a308d14453aedb1556d126dfb75fcae6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27ca91ec20e0fc0a68a0a5a9c971ae2bf4452a2bb13f98a6ba4961efea9808f6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b16e22f3ed81c9c108f586033a6328d110ae9169778a196babe532f2e05b541a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c27f86659360bcce9daae19eef570a276542ca733ba3702aebb6772b7545f5b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37e579c6a276b0f90694fec64eb73764c4348005fa653dabe0a506d41dcdf4ee(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f86d0fa52348f110a2961c73d9419a5eed5aa18a5657c2e3f079c09273a5fc3f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a7284e7ae609d5a684e08b50cf1a0b382ac7413ce570a3bcd620c22cbc7f921(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5eefcfba368ad40a1041f194563baa4fee3456774cd7e5d2fbd878e6ab2187f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4bb12ee8fdf985907d1a9d42b667d578deae5ac9b2980cfe6f703e0e0ab589c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5ef2a024992b7b69fc68753b9560c248ad9beb062d2cfa0ec83ca1d481cba62(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80a2ccdeb4cea8fb0dfba014696f82d12e96322046e52565e766ef60df2f32f2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigOverridesLimits, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f279269a646cf7d1c091802d6fa105547dc8fe660284d10ba56edd44f1362794(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigOverridesMeshGateway, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28a043298c47db0e57f4504abf3966baa03ea6683a17b4ba186118cbdf0a855f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__746756de17d5d35cba5feccc875e4523a7a9eb613075d22f3d99a62b36502af1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16f6615b366a1e90228893f4657402608e8f910e7b19357b7f6f3d40196a95ac(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cfcaedff72dd2ec83135bb25a2e7b66b68e26c3d40b2436a686a3a234499d12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01a73d4957766d63527acf5ffff87c24ead01478d56310bbb19e242ff8db2572(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e04928d79b783ad8fdc5da37de78e3d13b29def43a8ebe0025072451dd0d1852(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9928b75fea33554acf207d4d23444c0960c293db35816f64963be40212647364(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8789087d9d94758c8c8435309c4074e0b928725faa3f7349e7a94ea4b8f2dc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d2a0a3756bd77434f57ce1a2b725298479348c4a749748bbc6ab7e88435a615(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c102a21a160bfe89febb22b00141a21f56df0081cbdfd5914b5df9b8424153c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverrides]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f83af2df5cf5a6a06b3610f4969a7b7f165a16042a7dfab2602d1853d9d0f2e(
    *,
    base_ejection_time: typing.Optional[builtins.str] = None,
    enforcing_consecutive5_xx: typing.Optional[jsii.Number] = None,
    interval: typing.Optional[builtins.str] = None,
    max_ejection_percent: typing.Optional[jsii.Number] = None,
    max_failures: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc4f12c354df1e903bbf8fc087b9788df331ad99697801b937dd386947cda15f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ad72d21e57d0e3fa692ebc6092f0ecf783a97d87af609a56d6e6ed1a1ba4a6a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e07a55093d1db0b5d38fd258e32d0212a434b06b3089244948aa44fa8d2c46fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44ee9d2e364a07356170ea3b769e1d2690f9b29784cfb7f0652db24724a83a55(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4475c57a44121effa935292011c938126ae80d46ced6a6ca08a75714ef8047d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe38e4473a21a84afa426ae03c76bc679d1a5d500c0caef8a6e461b708e2666a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fa5fda93d4eb0f755e6a30dfc2d1a7db46f9d6ca02e2e2a39988dfc67a7c1b3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b74457005f8fd5ba7d96eaee8f711340e50e0fadb4b261058723257b20c157f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfad7a39742f159f16d092e32c41f19cbec25377787b803285abd7878b1b9165(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8197674106bd2afddd8eb8ce25e91b21cd7382ed320cdd4167d6f0d809c218e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62b802316e78b0cfe1f6873579e41d9cdcc42264fff1a591b1e194647832d789(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea646a9dae1ec733258d752f49e1062e00a67e8f31ffc5697f297ec6e08c58d9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c30251b0fec461489929eae1d55520660833960de594d11cf559360c30158d4a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceDefaultsUpstreamConfigOverridesPassiveHealthCheck]],
) -> None:
    """Type checking stubs"""
    pass
