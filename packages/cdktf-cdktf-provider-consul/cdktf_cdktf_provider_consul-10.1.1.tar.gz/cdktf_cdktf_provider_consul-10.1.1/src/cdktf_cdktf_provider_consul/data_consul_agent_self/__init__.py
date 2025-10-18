r'''
# `data_consul_agent_self`

Refer to the Terraform Registry for docs: [`data_consul_agent_self`](https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/data-sources/agent_self).
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


class DataConsulAgentSelf(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.dataConsulAgentSelf.DataConsulAgentSelf",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/data-sources/agent_self consul_agent_self}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/data-sources/agent_self consul_agent_self} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ceb2919d771c515a6f77280d38fdcda6bcb936f83ebe2091bf276c2b90a66de1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataConsulAgentSelfConfig(
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
        '''Generates CDKTF code for importing a DataConsulAgentSelf resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataConsulAgentSelf to import.
        :param import_from_id: The id of the existing DataConsulAgentSelf that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/data-sources/agent_self#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataConsulAgentSelf to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a30a10fe9f5f09401549dc6b26271c77ba99ae5482dd81ae0d71657d5a38520)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

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
    @jsii.member(jsii_name="aclDatacenter")
    def acl_datacenter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aclDatacenter"))

    @builtins.property
    @jsii.member(jsii_name="aclDefaultPolicy")
    def acl_default_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aclDefaultPolicy"))

    @builtins.property
    @jsii.member(jsii_name="aclDisabledTtl")
    def acl_disabled_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aclDisabledTtl"))

    @builtins.property
    @jsii.member(jsii_name="aclDownPolicy")
    def acl_down_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aclDownPolicy"))

    @builtins.property
    @jsii.member(jsii_name="aclEnforce08Semantics")
    def acl_enforce08_semantics(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "aclEnforce08Semantics"))

    @builtins.property
    @jsii.member(jsii_name="aclTtl")
    def acl_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aclTtl"))

    @builtins.property
    @jsii.member(jsii_name="addresses")
    def addresses(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "addresses"))

    @builtins.property
    @jsii.member(jsii_name="advertiseAddr")
    def advertise_addr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "advertiseAddr"))

    @builtins.property
    @jsii.member(jsii_name="advertiseAddrs")
    def advertise_addrs(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "advertiseAddrs"))

    @builtins.property
    @jsii.member(jsii_name="advertiseAddrWan")
    def advertise_addr_wan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "advertiseAddrWan"))

    @builtins.property
    @jsii.member(jsii_name="atlasJoin")
    def atlas_join(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "atlasJoin"))

    @builtins.property
    @jsii.member(jsii_name="bindAddr")
    def bind_addr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bindAddr"))

    @builtins.property
    @jsii.member(jsii_name="bootstrapExpect")
    def bootstrap_expect(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bootstrapExpect"))

    @builtins.property
    @jsii.member(jsii_name="bootstrapMode")
    def bootstrap_mode(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "bootstrapMode"))

    @builtins.property
    @jsii.member(jsii_name="checkDeregisterIntervalMin")
    def check_deregister_interval_min(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "checkDeregisterIntervalMin"))

    @builtins.property
    @jsii.member(jsii_name="checkReapInterval")
    def check_reap_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "checkReapInterval"))

    @builtins.property
    @jsii.member(jsii_name="checkUpdateInterval")
    def check_update_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "checkUpdateInterval"))

    @builtins.property
    @jsii.member(jsii_name="clientAddr")
    def client_addr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientAddr"))

    @builtins.property
    @jsii.member(jsii_name="datacenter")
    def datacenter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datacenter"))

    @builtins.property
    @jsii.member(jsii_name="dataDir")
    def data_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataDir"))

    @builtins.property
    @jsii.member(jsii_name="devMode")
    def dev_mode(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "devMode"))

    @builtins.property
    @jsii.member(jsii_name="dns")
    def dns(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "dns"))

    @builtins.property
    @jsii.member(jsii_name="dnsRecursors")
    def dns_recursors(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsRecursors"))

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @builtins.property
    @jsii.member(jsii_name="enableAnonymousSignature")
    def enable_anonymous_signature(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enableAnonymousSignature"))

    @builtins.property
    @jsii.member(jsii_name="enableCoordinates")
    def enable_coordinates(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enableCoordinates"))

    @builtins.property
    @jsii.member(jsii_name="enableDebug")
    def enable_debug(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enableDebug"))

    @builtins.property
    @jsii.member(jsii_name="enableRemoteExec")
    def enable_remote_exec(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enableRemoteExec"))

    @builtins.property
    @jsii.member(jsii_name="enableSyslog")
    def enable_syslog(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enableSyslog"))

    @builtins.property
    @jsii.member(jsii_name="enableUi")
    def enable_ui(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enableUi"))

    @builtins.property
    @jsii.member(jsii_name="enableUpdateCheck")
    def enable_update_check(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enableUpdateCheck"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="leaveOnInt")
    def leave_on_int(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "leaveOnInt"))

    @builtins.property
    @jsii.member(jsii_name="leaveOnTerm")
    def leave_on_term(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "leaveOnTerm"))

    @builtins.property
    @jsii.member(jsii_name="logLevel")
    def log_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logLevel"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="performance")
    def performance(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "performance"))

    @builtins.property
    @jsii.member(jsii_name="pidFile")
    def pid_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pidFile"))

    @builtins.property
    @jsii.member(jsii_name="ports")
    def ports(self) -> _cdktf_9a9027ec.NumberMap:
        return typing.cast(_cdktf_9a9027ec.NumberMap, jsii.get(self, "ports"))

    @builtins.property
    @jsii.member(jsii_name="protocolVersion")
    def protocol_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "protocolVersion"))

    @builtins.property
    @jsii.member(jsii_name="reconnectTimeoutLan")
    def reconnect_timeout_lan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reconnectTimeoutLan"))

    @builtins.property
    @jsii.member(jsii_name="reconnectTimeoutWan")
    def reconnect_timeout_wan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reconnectTimeoutWan"))

    @builtins.property
    @jsii.member(jsii_name="rejoinAfterLeave")
    def rejoin_after_leave(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "rejoinAfterLeave"))

    @builtins.property
    @jsii.member(jsii_name="retryJoin")
    def retry_join(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "retryJoin"))

    @builtins.property
    @jsii.member(jsii_name="retryJoinEc2")
    def retry_join_ec2(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "retryJoinEc2"))

    @builtins.property
    @jsii.member(jsii_name="retryJoinGce")
    def retry_join_gce(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "retryJoinGce"))

    @builtins.property
    @jsii.member(jsii_name="retryJoinWan")
    def retry_join_wan(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "retryJoinWan"))

    @builtins.property
    @jsii.member(jsii_name="retryMaxAttempts")
    def retry_max_attempts(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retryMaxAttempts"))

    @builtins.property
    @jsii.member(jsii_name="retryMaxAttemptsWan")
    def retry_max_attempts_wan(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retryMaxAttemptsWan"))

    @builtins.property
    @jsii.member(jsii_name="serfLanBindAddr")
    def serf_lan_bind_addr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serfLanBindAddr"))

    @builtins.property
    @jsii.member(jsii_name="serfWanBindAddr")
    def serf_wan_bind_addr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serfWanBindAddr"))

    @builtins.property
    @jsii.member(jsii_name="serverMode")
    def server_mode(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "serverMode"))

    @builtins.property
    @jsii.member(jsii_name="serverName")
    def server_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverName"))

    @builtins.property
    @jsii.member(jsii_name="sessionTtlMin")
    def session_ttl_min(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionTtlMin"))

    @builtins.property
    @jsii.member(jsii_name="startJoin")
    def start_join(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "startJoin"))

    @builtins.property
    @jsii.member(jsii_name="startJoinWan")
    def start_join_wan(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "startJoinWan"))

    @builtins.property
    @jsii.member(jsii_name="syslogFacility")
    def syslog_facility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "syslogFacility"))

    @builtins.property
    @jsii.member(jsii_name="taggedAddresses")
    def tagged_addresses(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "taggedAddresses"))

    @builtins.property
    @jsii.member(jsii_name="telemetry")
    def telemetry(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "telemetry"))

    @builtins.property
    @jsii.member(jsii_name="tlsCaFile")
    def tls_ca_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCaFile"))

    @builtins.property
    @jsii.member(jsii_name="tlsCertFile")
    def tls_cert_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCertFile"))

    @builtins.property
    @jsii.member(jsii_name="tlsKeyFile")
    def tls_key_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsKeyFile"))

    @builtins.property
    @jsii.member(jsii_name="tlsMinVersion")
    def tls_min_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsMinVersion"))

    @builtins.property
    @jsii.member(jsii_name="tlsVerifyIncoming")
    def tls_verify_incoming(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "tlsVerifyIncoming"))

    @builtins.property
    @jsii.member(jsii_name="tlsVerifyOutgoing")
    def tls_verify_outgoing(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "tlsVerifyOutgoing"))

    @builtins.property
    @jsii.member(jsii_name="tlsVerifyServerHostname")
    def tls_verify_server_hostname(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "tlsVerifyServerHostname"))

    @builtins.property
    @jsii.member(jsii_name="translateWanAddrs")
    def translate_wan_addrs(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "translateWanAddrs"))

    @builtins.property
    @jsii.member(jsii_name="uiDir")
    def ui_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uiDir"))

    @builtins.property
    @jsii.member(jsii_name="unixSockets")
    def unix_sockets(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "unixSockets"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="versionPrerelease")
    def version_prerelease(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionPrerelease"))

    @builtins.property
    @jsii.member(jsii_name="versionRevision")
    def version_revision(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionRevision"))


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.dataConsulAgentSelf.DataConsulAgentSelfConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
    },
)
class DataConsulAgentSelfConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f06f438f96be8a2031d62ac5978c1268dd18ed643c593d4b220448e0105be8f1)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
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

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataConsulAgentSelfConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataConsulAgentSelf",
    "DataConsulAgentSelfConfig",
]

publication.publish()

def _typecheckingstub__ceb2919d771c515a6f77280d38fdcda6bcb936f83ebe2091bf276c2b90a66de1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
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

def _typecheckingstub__3a30a10fe9f5f09401549dc6b26271c77ba99ae5482dd81ae0d71657d5a38520(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f06f438f96be8a2031d62ac5978c1268dd18ed643c593d4b220448e0105be8f1(
    *,
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
