r'''
# `consul_prepared_query`

Refer to the Terraform Registry for docs: [`consul_prepared_query`](https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query).
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


class PreparedQuery(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.preparedQuery.PreparedQuery",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query consul_prepared_query}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        service: builtins.str,
        connect: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        datacenter: typing.Optional[builtins.str] = None,
        dns: typing.Optional[typing.Union["PreparedQueryDns", typing.Dict[builtins.str, typing.Any]]] = None,
        failover: typing.Optional[typing.Union["PreparedQueryFailover", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        ignore_check_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        near: typing.Optional[builtins.str] = None,
        node_meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        only_passing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        session: typing.Optional[builtins.str] = None,
        stored_token: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        template: typing.Optional[typing.Union["PreparedQueryTemplate", typing.Dict[builtins.str, typing.Any]]] = None,
        token: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query consul_prepared_query} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the prepared query. Used to identify the prepared query during requests. Can be specified as an empty string to configure the query as a catch-all. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#name PreparedQuery#name}
        :param service: The name of the service to query. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#service PreparedQuery#service}
        :param connect: When ``true`` the prepared query will return connect proxy services for a queried service. Conditions such as ``tags`` in the prepared query will be matched against the proxy service. Defaults to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#connect PreparedQuery#connect}
        :param datacenter: The datacenter to use. This overrides the agent's default datacenter and the datacenter in the provider setup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#datacenter PreparedQuery#datacenter}
        :param dns: dns block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#dns PreparedQuery#dns}
        :param failover: failover block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#failover PreparedQuery#failover}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#id PreparedQuery#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ignore_check_ids: Specifies a list of check IDs that should be ignored when filtering unhealthy instances. This is mostly useful in an emergency or as a temporary measure when a health check is found to be unreliable. Being able to ignore it in centrally-defined queries can be simpler than de-registering the check as an interim solution until the check can be fixed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#ignore_check_ids PreparedQuery#ignore_check_ids}
        :param near: Allows specifying the name of a node to sort results near using Consul's distance sorting and network coordinates. The magic ``_agent`` value can be used to always sort nearest the node servicing the request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#near PreparedQuery#near}
        :param node_meta: Specifies a list of user-defined key/value pairs that will be used for filtering the query results to nodes with the given metadata values present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#node_meta PreparedQuery#node_meta}
        :param only_passing: When ``true``, the prepared query will only return nodes with passing health checks in the result. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#only_passing PreparedQuery#only_passing}
        :param service_meta: Specifies a list of user-defined key/value pairs that will be used for filtering the query results to services with the given metadata values present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#service_meta PreparedQuery#service_meta}
        :param session: The name of the Consul session to tie this query's lifetime to. This is an advanced parameter that should not be used without a complete understanding of Consul sessions and the implications of their use (it is recommended to leave this blank in nearly all cases). If this parameter is omitted the query will not expire. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#session PreparedQuery#session}
        :param stored_token: The ACL token to store with the prepared query. This token will be used by default whenever the query is executed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#stored_token PreparedQuery#stored_token}
        :param tags: The list of required and/or disallowed tags. If a tag is in this list it must be present. If the tag is preceded with a "!" then it is disallowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#tags PreparedQuery#tags}
        :param template: template block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#template PreparedQuery#template}
        :param token: The ACL token to use when saving the prepared query. This overrides the token that the agent provides by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#token PreparedQuery#token}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99e532a129a505dc05ffa3a569215997c782a04b22ebf07a72e65f25acf2d3cb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PreparedQueryConfig(
            name=name,
            service=service,
            connect=connect,
            datacenter=datacenter,
            dns=dns,
            failover=failover,
            id=id,
            ignore_check_ids=ignore_check_ids,
            near=near,
            node_meta=node_meta,
            only_passing=only_passing,
            service_meta=service_meta,
            session=session,
            stored_token=stored_token,
            tags=tags,
            template=template,
            token=token,
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
        '''Generates CDKTF code for importing a PreparedQuery resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PreparedQuery to import.
        :param import_from_id: The id of the existing PreparedQuery that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PreparedQuery to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd91f6ba0ba27a982817837317b32a39054c2b3b2fde6e7fd1885ab58daaf9ab)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putDns")
    def put_dns(self, *, ttl: typing.Optional[builtins.str] = None) -> None:
        '''
        :param ttl: The TTL to send when returning DNS results. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#ttl PreparedQuery#ttl}
        '''
        value = PreparedQueryDns(ttl=ttl)

        return typing.cast(None, jsii.invoke(self, "putDns", [value]))

    @jsii.member(jsii_name="putFailover")
    def put_failover(
        self,
        *,
        datacenters: typing.Optional[typing.Sequence[builtins.str]] = None,
        nearest_n: typing.Optional[jsii.Number] = None,
        targets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PreparedQueryFailoverTargets", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param datacenters: Remote datacenters to return results from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#datacenters PreparedQuery#datacenters}
        :param nearest_n: Return results from this many datacenters, sorted in ascending order of estimated RTT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#nearest_n PreparedQuery#nearest_n}
        :param targets: targets block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#targets PreparedQuery#targets}
        '''
        value = PreparedQueryFailover(
            datacenters=datacenters, nearest_n=nearest_n, targets=targets
        )

        return typing.cast(None, jsii.invoke(self, "putFailover", [value]))

    @jsii.member(jsii_name="putTemplate")
    def put_template(
        self,
        *,
        regexp: builtins.str,
        type: builtins.str,
        remove_empty_tags: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param regexp: The regular expression to match with. When using ``name_prefix_match``, this regex is applied against the query name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#regexp PreparedQuery#regexp}
        :param type: The type of template matching to perform. Currently only ``name_prefix_match`` is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#type PreparedQuery#type}
        :param remove_empty_tags: If set to true, will cause the tags list inside the service structure to be stripped of any empty strings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#remove_empty_tags PreparedQuery#remove_empty_tags}
        '''
        value = PreparedQueryTemplate(
            regexp=regexp, type=type, remove_empty_tags=remove_empty_tags
        )

        return typing.cast(None, jsii.invoke(self, "putTemplate", [value]))

    @jsii.member(jsii_name="resetConnect")
    def reset_connect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnect", []))

    @jsii.member(jsii_name="resetDatacenter")
    def reset_datacenter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatacenter", []))

    @jsii.member(jsii_name="resetDns")
    def reset_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDns", []))

    @jsii.member(jsii_name="resetFailover")
    def reset_failover(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailover", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIgnoreCheckIds")
    def reset_ignore_check_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreCheckIds", []))

    @jsii.member(jsii_name="resetNear")
    def reset_near(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNear", []))

    @jsii.member(jsii_name="resetNodeMeta")
    def reset_node_meta(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeMeta", []))

    @jsii.member(jsii_name="resetOnlyPassing")
    def reset_only_passing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnlyPassing", []))

    @jsii.member(jsii_name="resetServiceMeta")
    def reset_service_meta(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceMeta", []))

    @jsii.member(jsii_name="resetSession")
    def reset_session(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSession", []))

    @jsii.member(jsii_name="resetStoredToken")
    def reset_stored_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStoredToken", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTemplate")
    def reset_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemplate", []))

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
    @jsii.member(jsii_name="dns")
    def dns(self) -> "PreparedQueryDnsOutputReference":
        return typing.cast("PreparedQueryDnsOutputReference", jsii.get(self, "dns"))

    @builtins.property
    @jsii.member(jsii_name="failover")
    def failover(self) -> "PreparedQueryFailoverOutputReference":
        return typing.cast("PreparedQueryFailoverOutputReference", jsii.get(self, "failover"))

    @builtins.property
    @jsii.member(jsii_name="template")
    def template(self) -> "PreparedQueryTemplateOutputReference":
        return typing.cast("PreparedQueryTemplateOutputReference", jsii.get(self, "template"))

    @builtins.property
    @jsii.member(jsii_name="connectInput")
    def connect_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "connectInput"))

    @builtins.property
    @jsii.member(jsii_name="datacenterInput")
    def datacenter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datacenterInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsInput")
    def dns_input(self) -> typing.Optional["PreparedQueryDns"]:
        return typing.cast(typing.Optional["PreparedQueryDns"], jsii.get(self, "dnsInput"))

    @builtins.property
    @jsii.member(jsii_name="failoverInput")
    def failover_input(self) -> typing.Optional["PreparedQueryFailover"]:
        return typing.cast(typing.Optional["PreparedQueryFailover"], jsii.get(self, "failoverInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ignoreCheckIdsInput")
    def ignore_check_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ignoreCheckIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="nearInput")
    def near_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nearInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeMetaInput")
    def node_meta_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "nodeMetaInput"))

    @builtins.property
    @jsii.member(jsii_name="onlyPassingInput")
    def only_passing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "onlyPassingInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceMetaInput")
    def service_meta_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "serviceMetaInput"))

    @builtins.property
    @jsii.member(jsii_name="sessionInput")
    def session_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sessionInput"))

    @builtins.property
    @jsii.member(jsii_name="storedTokenInput")
    def stored_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storedTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="templateInput")
    def template_input(self) -> typing.Optional["PreparedQueryTemplate"]:
        return typing.cast(typing.Optional["PreparedQueryTemplate"], jsii.get(self, "templateInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenInput"))

    @builtins.property
    @jsii.member(jsii_name="connect")
    def connect(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "connect"))

    @connect.setter
    def connect(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01a3866d0746f4ed14030d30a60cbc7bb622f09e5571b372df0ab48ca16b253e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connect", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datacenter")
    def datacenter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datacenter"))

    @datacenter.setter
    def datacenter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d31ad77c41f38e42298597910fd85652a1e9864dc00a60e903b5f5ea057626c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84f52f66b7d0c31bff2fbebd0d73164c75173bdc25b93d42572e368f5ecc512d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ignoreCheckIds")
    def ignore_check_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ignoreCheckIds"))

    @ignore_check_ids.setter
    def ignore_check_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a16037e6caae7868826f460ef1f973460ddff116666b922468402425a5e1c7b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreCheckIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcfbaa26c75ee042c68054d86214007ef90f37db336effbeb5561668397d55f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="near")
    def near(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "near"))

    @near.setter
    def near(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1c8d2d14436eb75f665c008c14bf79137832efc0e608526b45988bd37210ebf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "near", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeMeta")
    def node_meta(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "nodeMeta"))

    @node_meta.setter
    def node_meta(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2468c5a103939f60964cc371625b50075bbd9d83a42b21f26e67fe4fad2e9829)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeMeta", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__dad8f9c2791bb4a1d55a808470d59973f5bc9e25f8c901c980eec8d3b4e90cdb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onlyPassing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__221b43652e72fc8a5eb3e56f64583aa8807d53fa5bf9e3e5fd79414d8304e991)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceMeta")
    def service_meta(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "serviceMeta"))

    @service_meta.setter
    def service_meta(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55abf30dd954cd64bd303c83dde921e62312435a2eeeee22607b4a1e47bdda30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceMeta", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="session")
    def session(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "session"))

    @session.setter
    def session(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__984b3830cb34af84c2e1035d6749bebee5f2facba8045150ae891fcf8cf7256c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "session", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storedToken")
    def stored_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storedToken"))

    @stored_token.setter
    def stored_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44fa364998096dc9a2cfa82ce7cab21745066412625af980275a09258d9a54e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storedToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__412f89276c8fb9f3d18dfd7a8790cd9da725212ef69c7170cb198d425612a27c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "token"))

    @token.setter
    def token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca7f79806b9b0e6c9a28650f7a42d9fd4822efb34642f5eeaa61c64d55cfb111)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.preparedQuery.PreparedQueryConfig",
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
        "service": "service",
        "connect": "connect",
        "datacenter": "datacenter",
        "dns": "dns",
        "failover": "failover",
        "id": "id",
        "ignore_check_ids": "ignoreCheckIds",
        "near": "near",
        "node_meta": "nodeMeta",
        "only_passing": "onlyPassing",
        "service_meta": "serviceMeta",
        "session": "session",
        "stored_token": "storedToken",
        "tags": "tags",
        "template": "template",
        "token": "token",
    },
)
class PreparedQueryConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        service: builtins.str,
        connect: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        datacenter: typing.Optional[builtins.str] = None,
        dns: typing.Optional[typing.Union["PreparedQueryDns", typing.Dict[builtins.str, typing.Any]]] = None,
        failover: typing.Optional[typing.Union["PreparedQueryFailover", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        ignore_check_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        near: typing.Optional[builtins.str] = None,
        node_meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        only_passing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        session: typing.Optional[builtins.str] = None,
        stored_token: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        template: typing.Optional[typing.Union["PreparedQueryTemplate", typing.Dict[builtins.str, typing.Any]]] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: The name of the prepared query. Used to identify the prepared query during requests. Can be specified as an empty string to configure the query as a catch-all. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#name PreparedQuery#name}
        :param service: The name of the service to query. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#service PreparedQuery#service}
        :param connect: When ``true`` the prepared query will return connect proxy services for a queried service. Conditions such as ``tags`` in the prepared query will be matched against the proxy service. Defaults to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#connect PreparedQuery#connect}
        :param datacenter: The datacenter to use. This overrides the agent's default datacenter and the datacenter in the provider setup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#datacenter PreparedQuery#datacenter}
        :param dns: dns block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#dns PreparedQuery#dns}
        :param failover: failover block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#failover PreparedQuery#failover}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#id PreparedQuery#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ignore_check_ids: Specifies a list of check IDs that should be ignored when filtering unhealthy instances. This is mostly useful in an emergency or as a temporary measure when a health check is found to be unreliable. Being able to ignore it in centrally-defined queries can be simpler than de-registering the check as an interim solution until the check can be fixed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#ignore_check_ids PreparedQuery#ignore_check_ids}
        :param near: Allows specifying the name of a node to sort results near using Consul's distance sorting and network coordinates. The magic ``_agent`` value can be used to always sort nearest the node servicing the request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#near PreparedQuery#near}
        :param node_meta: Specifies a list of user-defined key/value pairs that will be used for filtering the query results to nodes with the given metadata values present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#node_meta PreparedQuery#node_meta}
        :param only_passing: When ``true``, the prepared query will only return nodes with passing health checks in the result. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#only_passing PreparedQuery#only_passing}
        :param service_meta: Specifies a list of user-defined key/value pairs that will be used for filtering the query results to services with the given metadata values present. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#service_meta PreparedQuery#service_meta}
        :param session: The name of the Consul session to tie this query's lifetime to. This is an advanced parameter that should not be used without a complete understanding of Consul sessions and the implications of their use (it is recommended to leave this blank in nearly all cases). If this parameter is omitted the query will not expire. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#session PreparedQuery#session}
        :param stored_token: The ACL token to store with the prepared query. This token will be used by default whenever the query is executed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#stored_token PreparedQuery#stored_token}
        :param tags: The list of required and/or disallowed tags. If a tag is in this list it must be present. If the tag is preceded with a "!" then it is disallowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#tags PreparedQuery#tags}
        :param template: template block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#template PreparedQuery#template}
        :param token: The ACL token to use when saving the prepared query. This overrides the token that the agent provides by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#token PreparedQuery#token}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(dns, dict):
            dns = PreparedQueryDns(**dns)
        if isinstance(failover, dict):
            failover = PreparedQueryFailover(**failover)
        if isinstance(template, dict):
            template = PreparedQueryTemplate(**template)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd607de3de1a184899ceae0299d73e4fe6931ba2c55ab6779d6ef3da4a673657)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument connect", value=connect, expected_type=type_hints["connect"])
            check_type(argname="argument datacenter", value=datacenter, expected_type=type_hints["datacenter"])
            check_type(argname="argument dns", value=dns, expected_type=type_hints["dns"])
            check_type(argname="argument failover", value=failover, expected_type=type_hints["failover"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ignore_check_ids", value=ignore_check_ids, expected_type=type_hints["ignore_check_ids"])
            check_type(argname="argument near", value=near, expected_type=type_hints["near"])
            check_type(argname="argument node_meta", value=node_meta, expected_type=type_hints["node_meta"])
            check_type(argname="argument only_passing", value=only_passing, expected_type=type_hints["only_passing"])
            check_type(argname="argument service_meta", value=service_meta, expected_type=type_hints["service_meta"])
            check_type(argname="argument session", value=session, expected_type=type_hints["session"])
            check_type(argname="argument stored_token", value=stored_token, expected_type=type_hints["stored_token"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument template", value=template, expected_type=type_hints["template"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "service": service,
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
        if connect is not None:
            self._values["connect"] = connect
        if datacenter is not None:
            self._values["datacenter"] = datacenter
        if dns is not None:
            self._values["dns"] = dns
        if failover is not None:
            self._values["failover"] = failover
        if id is not None:
            self._values["id"] = id
        if ignore_check_ids is not None:
            self._values["ignore_check_ids"] = ignore_check_ids
        if near is not None:
            self._values["near"] = near
        if node_meta is not None:
            self._values["node_meta"] = node_meta
        if only_passing is not None:
            self._values["only_passing"] = only_passing
        if service_meta is not None:
            self._values["service_meta"] = service_meta
        if session is not None:
            self._values["session"] = session
        if stored_token is not None:
            self._values["stored_token"] = stored_token
        if tags is not None:
            self._values["tags"] = tags
        if template is not None:
            self._values["template"] = template
        if token is not None:
            self._values["token"] = token

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
        '''The name of the prepared query.

        Used to identify the prepared query during requests. Can be specified as an empty string to configure the query as a catch-all.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#name PreparedQuery#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service(self) -> builtins.str:
        '''The name of the service to query.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#service PreparedQuery#service}
        '''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def connect(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When ``true`` the prepared query will return connect proxy services for a queried service.

        Conditions such as ``tags`` in the prepared query will be matched against the proxy service. Defaults to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#connect PreparedQuery#connect}
        '''
        result = self._values.get("connect")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def datacenter(self) -> typing.Optional[builtins.str]:
        '''The datacenter to use. This overrides the agent's default datacenter and the datacenter in the provider setup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#datacenter PreparedQuery#datacenter}
        '''
        result = self._values.get("datacenter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dns(self) -> typing.Optional["PreparedQueryDns"]:
        '''dns block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#dns PreparedQuery#dns}
        '''
        result = self._values.get("dns")
        return typing.cast(typing.Optional["PreparedQueryDns"], result)

    @builtins.property
    def failover(self) -> typing.Optional["PreparedQueryFailover"]:
        '''failover block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#failover PreparedQuery#failover}
        '''
        result = self._values.get("failover")
        return typing.cast(typing.Optional["PreparedQueryFailover"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#id PreparedQuery#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_check_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies a list of check IDs that should be ignored when filtering unhealthy instances.

        This is mostly useful in an emergency or as a temporary measure when a health check is found to be unreliable. Being able to ignore it in centrally-defined queries can be simpler than de-registering the check as an interim solution until the check can be fixed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#ignore_check_ids PreparedQuery#ignore_check_ids}
        '''
        result = self._values.get("ignore_check_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def near(self) -> typing.Optional[builtins.str]:
        '''Allows specifying the name of a node to sort results near using Consul's distance sorting and network coordinates.

        The magic ``_agent`` value can be used to always sort nearest the node servicing the request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#near PreparedQuery#near}
        '''
        result = self._values.get("near")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_meta(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Specifies a list of user-defined key/value pairs that will be used for filtering the query results to nodes with the given metadata values present.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#node_meta PreparedQuery#node_meta}
        '''
        result = self._values.get("node_meta")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def only_passing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When ``true``, the prepared query will only return nodes with passing health checks in the result.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#only_passing PreparedQuery#only_passing}
        '''
        result = self._values.get("only_passing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def service_meta(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Specifies a list of user-defined key/value pairs that will be used for filtering the query results to services with the given metadata values present.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#service_meta PreparedQuery#service_meta}
        '''
        result = self._values.get("service_meta")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def session(self) -> typing.Optional[builtins.str]:
        '''The name of the Consul session to tie this query's lifetime to.

        This is an advanced parameter that should not be used without a complete understanding of Consul sessions and the implications of their use (it is recommended to leave this blank in nearly all cases).  If this parameter is omitted the query will not expire.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#session PreparedQuery#session}
        '''
        result = self._values.get("session")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stored_token(self) -> typing.Optional[builtins.str]:
        '''The ACL token to store with the prepared query.

        This token will be used by default whenever the query is executed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#stored_token PreparedQuery#stored_token}
        '''
        result = self._values.get("stored_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of required and/or disallowed tags.

        If a tag is in this list it must be present.  If the tag is preceded with a "!" then it is disallowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#tags PreparedQuery#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def template(self) -> typing.Optional["PreparedQueryTemplate"]:
        '''template block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#template PreparedQuery#template}
        '''
        result = self._values.get("template")
        return typing.cast(typing.Optional["PreparedQueryTemplate"], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''The ACL token to use when saving the prepared query.

        This overrides the token that the agent provides by default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#token PreparedQuery#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PreparedQueryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.preparedQuery.PreparedQueryDns",
    jsii_struct_bases=[],
    name_mapping={"ttl": "ttl"},
)
class PreparedQueryDns:
    def __init__(self, *, ttl: typing.Optional[builtins.str] = None) -> None:
        '''
        :param ttl: The TTL to send when returning DNS results. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#ttl PreparedQuery#ttl}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e613b493cfdf3038223000eb18c4c984e57ecf298cb220801c7e3c27ef8faf78)
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ttl is not None:
            self._values["ttl"] = ttl

    @builtins.property
    def ttl(self) -> typing.Optional[builtins.str]:
        '''The TTL to send when returning DNS results.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#ttl PreparedQuery#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PreparedQueryDns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PreparedQueryDnsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.preparedQuery.PreparedQueryDnsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b158359fcbf848c33fc563e5226a63b7ba2685339575172970cffcd61b3d586a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a31c017c3bb103842c8e8f45c571e20a4f008856932d2ee83886864f39a7b1b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PreparedQueryDns]:
        return typing.cast(typing.Optional[PreparedQueryDns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PreparedQueryDns]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b77826ce67481292a2422b6b12f90539826f4e44f03710d16901cf9ec9303a0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.preparedQuery.PreparedQueryFailover",
    jsii_struct_bases=[],
    name_mapping={
        "datacenters": "datacenters",
        "nearest_n": "nearestN",
        "targets": "targets",
    },
)
class PreparedQueryFailover:
    def __init__(
        self,
        *,
        datacenters: typing.Optional[typing.Sequence[builtins.str]] = None,
        nearest_n: typing.Optional[jsii.Number] = None,
        targets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PreparedQueryFailoverTargets", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param datacenters: Remote datacenters to return results from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#datacenters PreparedQuery#datacenters}
        :param nearest_n: Return results from this many datacenters, sorted in ascending order of estimated RTT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#nearest_n PreparedQuery#nearest_n}
        :param targets: targets block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#targets PreparedQuery#targets}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15176f855aab72a53b2bd15b9edc4c41c4dd9060f8b13d1544d45f6465e5029f)
            check_type(argname="argument datacenters", value=datacenters, expected_type=type_hints["datacenters"])
            check_type(argname="argument nearest_n", value=nearest_n, expected_type=type_hints["nearest_n"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if datacenters is not None:
            self._values["datacenters"] = datacenters
        if nearest_n is not None:
            self._values["nearest_n"] = nearest_n
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def datacenters(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Remote datacenters to return results from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#datacenters PreparedQuery#datacenters}
        '''
        result = self._values.get("datacenters")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def nearest_n(self) -> typing.Optional[jsii.Number]:
        '''Return results from this many datacenters, sorted in ascending order of estimated RTT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#nearest_n PreparedQuery#nearest_n}
        '''
        result = self._values.get("nearest_n")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def targets(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PreparedQueryFailoverTargets"]]]:
        '''targets block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#targets PreparedQuery#targets}
        '''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PreparedQueryFailoverTargets"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PreparedQueryFailover(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PreparedQueryFailoverOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.preparedQuery.PreparedQueryFailoverOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dc3ca9044b9cda08f5f3697c3108c39c1cea6888b9d197407e1ee2ca70ea84a9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTargets")
    def put_targets(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PreparedQueryFailoverTargets", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67a1e35e6a2566b25b9473759d706ea2cc347132914b8cd572e72378df715827)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTargets", [value]))

    @jsii.member(jsii_name="resetDatacenters")
    def reset_datacenters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatacenters", []))

    @jsii.member(jsii_name="resetNearestN")
    def reset_nearest_n(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNearestN", []))

    @jsii.member(jsii_name="resetTargets")
    def reset_targets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargets", []))

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(self) -> "PreparedQueryFailoverTargetsList":
        return typing.cast("PreparedQueryFailoverTargetsList", jsii.get(self, "targets"))

    @builtins.property
    @jsii.member(jsii_name="datacentersInput")
    def datacenters_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "datacentersInput"))

    @builtins.property
    @jsii.member(jsii_name="nearestNInput")
    def nearest_n_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nearestNInput"))

    @builtins.property
    @jsii.member(jsii_name="targetsInput")
    def targets_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PreparedQueryFailoverTargets"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PreparedQueryFailoverTargets"]]], jsii.get(self, "targetsInput"))

    @builtins.property
    @jsii.member(jsii_name="datacenters")
    def datacenters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "datacenters"))

    @datacenters.setter
    def datacenters(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13b30900c8049f622af45cf6b3460306d01d01c811226e00994f579d323b6619)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nearestN")
    def nearest_n(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nearestN"))

    @nearest_n.setter
    def nearest_n(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b54effac3e853a82effd96717b90b874ccd3e748422d0c1fed3c84501407b2e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nearestN", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PreparedQueryFailover]:
        return typing.cast(typing.Optional[PreparedQueryFailover], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PreparedQueryFailover]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df77d490ed98762ba9480ac4321c15d633d3b42fabdb1e73b3cac17c10952864)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.preparedQuery.PreparedQueryFailoverTargets",
    jsii_struct_bases=[],
    name_mapping={"datacenter": "datacenter", "peer": "peer"},
)
class PreparedQueryFailoverTargets:
    def __init__(
        self,
        *,
        datacenter: typing.Optional[builtins.str] = None,
        peer: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param datacenter: Specifies a WAN federated datacenter to forward the query to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#datacenter PreparedQuery#datacenter}
        :param peer: Specifies a cluster peer to use for failover. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#peer PreparedQuery#peer}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bb59963da7c4a625520ca0b67d5c36bebb3fcaf5fe2d4cdd64cbbe2a173d5f9)
            check_type(argname="argument datacenter", value=datacenter, expected_type=type_hints["datacenter"])
            check_type(argname="argument peer", value=peer, expected_type=type_hints["peer"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if datacenter is not None:
            self._values["datacenter"] = datacenter
        if peer is not None:
            self._values["peer"] = peer

    @builtins.property
    def datacenter(self) -> typing.Optional[builtins.str]:
        '''Specifies a WAN federated datacenter to forward the query to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#datacenter PreparedQuery#datacenter}
        '''
        result = self._values.get("datacenter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def peer(self) -> typing.Optional[builtins.str]:
        '''Specifies a cluster peer to use for failover.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#peer PreparedQuery#peer}
        '''
        result = self._values.get("peer")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PreparedQueryFailoverTargets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PreparedQueryFailoverTargetsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.preparedQuery.PreparedQueryFailoverTargetsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e610c038070f143dec40ce0fc90e1414714f19545c2641027e89b8cf41651166)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "PreparedQueryFailoverTargetsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e18088fe02d2a837ca3cdebb3c5b2965a69680a9edf8d51ad4e21127a3434d6d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PreparedQueryFailoverTargetsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89e65813fd5d809f4ea3057c9601e0f93dd2e08665fb79e76e2969127a85dcb7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__28880063dbb922e19633f13ab3775f3d697169dc5b3616e111eb231fc73736cc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c4d6978c00bb1f0256b4deb370b249b7800d1864421398439074e79e03b55f77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PreparedQueryFailoverTargets]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PreparedQueryFailoverTargets]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PreparedQueryFailoverTargets]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f44039ce6de3be1624cb277f74359e1c84712b881dcc24c61050a981d3cecf26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PreparedQueryFailoverTargetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.preparedQuery.PreparedQueryFailoverTargetsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3ceb5c6ab530f884149b6a0d19e8be41789971800e4bb583f3b082db78163c40)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDatacenter")
    def reset_datacenter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatacenter", []))

    @jsii.member(jsii_name="resetPeer")
    def reset_peer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeer", []))

    @builtins.property
    @jsii.member(jsii_name="datacenterInput")
    def datacenter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datacenterInput"))

    @builtins.property
    @jsii.member(jsii_name="peerInput")
    def peer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "peerInput"))

    @builtins.property
    @jsii.member(jsii_name="datacenter")
    def datacenter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datacenter"))

    @datacenter.setter
    def datacenter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb115466bb2e16b4e078e61d6fa3934ec8d5709dde66babcef3af854dc2449c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="peer")
    def peer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "peer"))

    @peer.setter
    def peer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc90d2582da9fd273dd675593970b8c935fb4f512a96bb9e4eb978d4b1afb2cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "peer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PreparedQueryFailoverTargets]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PreparedQueryFailoverTargets]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PreparedQueryFailoverTargets]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8b7787e65759b0e82f4eee7d2d34d1dd6f9b4133539476f7e1880d92566c08c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.preparedQuery.PreparedQueryTemplate",
    jsii_struct_bases=[],
    name_mapping={
        "regexp": "regexp",
        "type": "type",
        "remove_empty_tags": "removeEmptyTags",
    },
)
class PreparedQueryTemplate:
    def __init__(
        self,
        *,
        regexp: builtins.str,
        type: builtins.str,
        remove_empty_tags: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param regexp: The regular expression to match with. When using ``name_prefix_match``, this regex is applied against the query name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#regexp PreparedQuery#regexp}
        :param type: The type of template matching to perform. Currently only ``name_prefix_match`` is supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#type PreparedQuery#type}
        :param remove_empty_tags: If set to true, will cause the tags list inside the service structure to be stripped of any empty strings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#remove_empty_tags PreparedQuery#remove_empty_tags}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5861c4b7ed36804d4cbd3b3cf1cdf91db1d5495c8308af6098c9d75c5f88cc93)
            check_type(argname="argument regexp", value=regexp, expected_type=type_hints["regexp"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument remove_empty_tags", value=remove_empty_tags, expected_type=type_hints["remove_empty_tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "regexp": regexp,
            "type": type,
        }
        if remove_empty_tags is not None:
            self._values["remove_empty_tags"] = remove_empty_tags

    @builtins.property
    def regexp(self) -> builtins.str:
        '''The regular expression to match with. When using ``name_prefix_match``, this regex is applied against the query name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#regexp PreparedQuery#regexp}
        '''
        result = self._values.get("regexp")
        assert result is not None, "Required property 'regexp' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of template matching to perform. Currently only ``name_prefix_match`` is supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#type PreparedQuery#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def remove_empty_tags(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, will cause the tags list inside the service structure to be stripped of any empty strings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/prepared_query#remove_empty_tags PreparedQuery#remove_empty_tags}
        '''
        result = self._values.get("remove_empty_tags")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PreparedQueryTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PreparedQueryTemplateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.preparedQuery.PreparedQueryTemplateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c606b7cc9a779c076a6a657cf618cc72763db04c365c238d2fc5efe08a41b21c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetRemoveEmptyTags")
    def reset_remove_empty_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemoveEmptyTags", []))

    @builtins.property
    @jsii.member(jsii_name="regexpInput")
    def regexp_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regexpInput"))

    @builtins.property
    @jsii.member(jsii_name="removeEmptyTagsInput")
    def remove_empty_tags_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "removeEmptyTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="regexp")
    def regexp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regexp"))

    @regexp.setter
    def regexp(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2be9f69aea4cb91b82ef8eec17dd1da676c824cf625dc64c0a11209b85b8afa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regexp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="removeEmptyTags")
    def remove_empty_tags(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "removeEmptyTags"))

    @remove_empty_tags.setter
    def remove_empty_tags(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20d249d8de5d2a279b0e91faf1043e39e2067effcd6c86f577e011b6a3967805)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "removeEmptyTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23b9a0d753a9859c08d7eff3e56138539029988e66c25381547c5f5678fe30ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PreparedQueryTemplate]:
        return typing.cast(typing.Optional[PreparedQueryTemplate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PreparedQueryTemplate]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d62d6d2d8edeabef0af908dc9f35e2d413a248e65c727527a31b97e6fd9fbd9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "PreparedQuery",
    "PreparedQueryConfig",
    "PreparedQueryDns",
    "PreparedQueryDnsOutputReference",
    "PreparedQueryFailover",
    "PreparedQueryFailoverOutputReference",
    "PreparedQueryFailoverTargets",
    "PreparedQueryFailoverTargetsList",
    "PreparedQueryFailoverTargetsOutputReference",
    "PreparedQueryTemplate",
    "PreparedQueryTemplateOutputReference",
]

publication.publish()

def _typecheckingstub__99e532a129a505dc05ffa3a569215997c782a04b22ebf07a72e65f25acf2d3cb(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    service: builtins.str,
    connect: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    datacenter: typing.Optional[builtins.str] = None,
    dns: typing.Optional[typing.Union[PreparedQueryDns, typing.Dict[builtins.str, typing.Any]]] = None,
    failover: typing.Optional[typing.Union[PreparedQueryFailover, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    ignore_check_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    near: typing.Optional[builtins.str] = None,
    node_meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    only_passing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    service_meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    session: typing.Optional[builtins.str] = None,
    stored_token: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    template: typing.Optional[typing.Union[PreparedQueryTemplate, typing.Dict[builtins.str, typing.Any]]] = None,
    token: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__dd91f6ba0ba27a982817837317b32a39054c2b3b2fde6e7fd1885ab58daaf9ab(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01a3866d0746f4ed14030d30a60cbc7bb622f09e5571b372df0ab48ca16b253e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d31ad77c41f38e42298597910fd85652a1e9864dc00a60e903b5f5ea057626c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84f52f66b7d0c31bff2fbebd0d73164c75173bdc25b93d42572e368f5ecc512d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a16037e6caae7868826f460ef1f973460ddff116666b922468402425a5e1c7b6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcfbaa26c75ee042c68054d86214007ef90f37db336effbeb5561668397d55f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1c8d2d14436eb75f665c008c14bf79137832efc0e608526b45988bd37210ebf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2468c5a103939f60964cc371625b50075bbd9d83a42b21f26e67fe4fad2e9829(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dad8f9c2791bb4a1d55a808470d59973f5bc9e25f8c901c980eec8d3b4e90cdb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__221b43652e72fc8a5eb3e56f64583aa8807d53fa5bf9e3e5fd79414d8304e991(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55abf30dd954cd64bd303c83dde921e62312435a2eeeee22607b4a1e47bdda30(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__984b3830cb34af84c2e1035d6749bebee5f2facba8045150ae891fcf8cf7256c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44fa364998096dc9a2cfa82ce7cab21745066412625af980275a09258d9a54e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__412f89276c8fb9f3d18dfd7a8790cd9da725212ef69c7170cb198d425612a27c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca7f79806b9b0e6c9a28650f7a42d9fd4822efb34642f5eeaa61c64d55cfb111(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd607de3de1a184899ceae0299d73e4fe6931ba2c55ab6779d6ef3da4a673657(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    service: builtins.str,
    connect: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    datacenter: typing.Optional[builtins.str] = None,
    dns: typing.Optional[typing.Union[PreparedQueryDns, typing.Dict[builtins.str, typing.Any]]] = None,
    failover: typing.Optional[typing.Union[PreparedQueryFailover, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    ignore_check_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    near: typing.Optional[builtins.str] = None,
    node_meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    only_passing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    service_meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    session: typing.Optional[builtins.str] = None,
    stored_token: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    template: typing.Optional[typing.Union[PreparedQueryTemplate, typing.Dict[builtins.str, typing.Any]]] = None,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e613b493cfdf3038223000eb18c4c984e57ecf298cb220801c7e3c27ef8faf78(
    *,
    ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b158359fcbf848c33fc563e5226a63b7ba2685339575172970cffcd61b3d586a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a31c017c3bb103842c8e8f45c571e20a4f008856932d2ee83886864f39a7b1b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b77826ce67481292a2422b6b12f90539826f4e44f03710d16901cf9ec9303a0d(
    value: typing.Optional[PreparedQueryDns],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15176f855aab72a53b2bd15b9edc4c41c4dd9060f8b13d1544d45f6465e5029f(
    *,
    datacenters: typing.Optional[typing.Sequence[builtins.str]] = None,
    nearest_n: typing.Optional[jsii.Number] = None,
    targets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PreparedQueryFailoverTargets, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc3ca9044b9cda08f5f3697c3108c39c1cea6888b9d197407e1ee2ca70ea84a9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67a1e35e6a2566b25b9473759d706ea2cc347132914b8cd572e72378df715827(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PreparedQueryFailoverTargets, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13b30900c8049f622af45cf6b3460306d01d01c811226e00994f579d323b6619(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b54effac3e853a82effd96717b90b874ccd3e748422d0c1fed3c84501407b2e6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df77d490ed98762ba9480ac4321c15d633d3b42fabdb1e73b3cac17c10952864(
    value: typing.Optional[PreparedQueryFailover],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bb59963da7c4a625520ca0b67d5c36bebb3fcaf5fe2d4cdd64cbbe2a173d5f9(
    *,
    datacenter: typing.Optional[builtins.str] = None,
    peer: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e610c038070f143dec40ce0fc90e1414714f19545c2641027e89b8cf41651166(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e18088fe02d2a837ca3cdebb3c5b2965a69680a9edf8d51ad4e21127a3434d6d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89e65813fd5d809f4ea3057c9601e0f93dd2e08665fb79e76e2969127a85dcb7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28880063dbb922e19633f13ab3775f3d697169dc5b3616e111eb231fc73736cc(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4d6978c00bb1f0256b4deb370b249b7800d1864421398439074e79e03b55f77(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f44039ce6de3be1624cb277f74359e1c84712b881dcc24c61050a981d3cecf26(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PreparedQueryFailoverTargets]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ceb5c6ab530f884149b6a0d19e8be41789971800e4bb583f3b082db78163c40(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb115466bb2e16b4e078e61d6fa3934ec8d5709dde66babcef3af854dc2449c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc90d2582da9fd273dd675593970b8c935fb4f512a96bb9e4eb978d4b1afb2cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8b7787e65759b0e82f4eee7d2d34d1dd6f9b4133539476f7e1880d92566c08c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PreparedQueryFailoverTargets]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5861c4b7ed36804d4cbd3b3cf1cdf91db1d5495c8308af6098c9d75c5f88cc93(
    *,
    regexp: builtins.str,
    type: builtins.str,
    remove_empty_tags: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c606b7cc9a779c076a6a657cf618cc72763db04c365c238d2fc5efe08a41b21c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2be9f69aea4cb91b82ef8eec17dd1da676c824cf625dc64c0a11209b85b8afa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20d249d8de5d2a279b0e91faf1043e39e2067effcd6c86f577e011b6a3967805(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23b9a0d753a9859c08d7eff3e56138539029988e66c25381547c5f5678fe30ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d62d6d2d8edeabef0af908dc9f35e2d413a248e65c727527a31b97e6fd9fbd9f(
    value: typing.Optional[PreparedQueryTemplate],
) -> None:
    """Type checking stubs"""
    pass
