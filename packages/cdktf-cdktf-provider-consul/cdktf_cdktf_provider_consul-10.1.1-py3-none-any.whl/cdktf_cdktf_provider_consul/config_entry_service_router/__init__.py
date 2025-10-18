r'''
# `consul_config_entry_service_router`

Refer to the Terraform Registry for docs: [`consul_config_entry_service_router`](https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router).
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


class ConfigEntryServiceRouter(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouter",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router consul_config_entry_service_router}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceRouterRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router consul_config_entry_service_router} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Specifies a name for the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#name ConfigEntryServiceRouter#name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#id ConfigEntryServiceRouter#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param meta: Specifies key-value pairs to add to the KV store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#meta ConfigEntryServiceRouter#meta}
        :param namespace: Specifies the namespace to apply the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#namespace ConfigEntryServiceRouter#namespace}
        :param partition: Specifies the admin partition to apply the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#partition ConfigEntryServiceRouter#partition}
        :param routes: routes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#routes ConfigEntryServiceRouter#routes}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc4bd28f48c7eb9ce005a75a3fc4694fd361848541cd22bff3e04ceefc54685d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigEntryServiceRouterConfig(
            name=name,
            id=id,
            meta=meta,
            namespace=namespace,
            partition=partition,
            routes=routes,
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
        '''Generates CDKTF code for importing a ConfigEntryServiceRouter resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ConfigEntryServiceRouter to import.
        :param import_from_id: The id of the existing ConfigEntryServiceRouter that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ConfigEntryServiceRouter to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ffbd434231779519b6374e49970f88f3846afc56ee921522aa624010463de71)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putRoutes")
    def put_routes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceRouterRoutes", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be7c1535be502c93299a701151767a2b7b3da9454f80ca4bf4d67b6d2b86d4ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRoutes", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMeta")
    def reset_meta(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMeta", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPartition")
    def reset_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartition", []))

    @jsii.member(jsii_name="resetRoutes")
    def reset_routes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoutes", []))

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
    @jsii.member(jsii_name="routes")
    def routes(self) -> "ConfigEntryServiceRouterRoutesList":
        return typing.cast("ConfigEntryServiceRouterRoutesList", jsii.get(self, "routes"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

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
    @jsii.member(jsii_name="routesInput")
    def routes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceRouterRoutes"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceRouterRoutes"]]], jsii.get(self, "routesInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0676af542542b823ec4033b0af3941fe430fb4ae9e2dfdc8f07ab59b911d9c96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="meta")
    def meta(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "meta"))

    @meta.setter
    def meta(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a314f352ac59babcfb0d4e84ce50f9364bd001691ebd06338956996b64671e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "meta", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11f2a1c0c1cbbb7f6864f64742d4b8ef7b79e8372f5402a0411c678b639e274f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67fd12976f37299873b7fa015b284a3ddc4c6bc9074f487c13e92e8b23d85ca0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partition")
    def partition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partition"))

    @partition.setter
    def partition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96e14066d718ad07d11660956936f0b9671147adb929993db4398f79a09cf6b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partition", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterConfig",
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
        "id": "id",
        "meta": "meta",
        "namespace": "namespace",
        "partition": "partition",
        "routes": "routes",
    },
)
class ConfigEntryServiceRouterConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        id: typing.Optional[builtins.str] = None,
        meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceRouterRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Specifies a name for the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#name ConfigEntryServiceRouter#name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#id ConfigEntryServiceRouter#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param meta: Specifies key-value pairs to add to the KV store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#meta ConfigEntryServiceRouter#meta}
        :param namespace: Specifies the namespace to apply the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#namespace ConfigEntryServiceRouter#namespace}
        :param partition: Specifies the admin partition to apply the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#partition ConfigEntryServiceRouter#partition}
        :param routes: routes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#routes ConfigEntryServiceRouter#routes}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87c26c66def50e9b47026757204a56c6df07d976ff89ba51c2c9cdf22d1f49de)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument meta", value=meta, expected_type=type_hints["meta"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument routes", value=routes, expected_type=type_hints["routes"])
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
        if id is not None:
            self._values["id"] = id
        if meta is not None:
            self._values["meta"] = meta
        if namespace is not None:
            self._values["namespace"] = namespace
        if partition is not None:
            self._values["partition"] = partition
        if routes is not None:
            self._values["routes"] = routes

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#name ConfigEntryServiceRouter#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#id ConfigEntryServiceRouter#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def meta(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Specifies key-value pairs to add to the KV store.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#meta ConfigEntryServiceRouter#meta}
        '''
        result = self._values.get("meta")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Specifies the namespace to apply the configuration entry.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#namespace ConfigEntryServiceRouter#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''Specifies the admin partition to apply the configuration entry.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#partition ConfigEntryServiceRouter#partition}
        '''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def routes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceRouterRoutes"]]]:
        '''routes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#routes ConfigEntryServiceRouter#routes}
        '''
        result = self._values.get("routes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceRouterRoutes"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceRouterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutes",
    jsii_struct_bases=[],
    name_mapping={"destination": "destination", "match": "match"},
)
class ConfigEntryServiceRouterRoutes:
    def __init__(
        self,
        *,
        destination: typing.Optional[typing.Union["ConfigEntryServiceRouterRoutesDestination", typing.Dict[builtins.str, typing.Any]]] = None,
        match: typing.Optional[typing.Union["ConfigEntryServiceRouterRoutesMatch", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param destination: destination block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#destination ConfigEntryServiceRouter#destination}
        :param match: match block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#match ConfigEntryServiceRouter#match}
        '''
        if isinstance(destination, dict):
            destination = ConfigEntryServiceRouterRoutesDestination(**destination)
        if isinstance(match, dict):
            match = ConfigEntryServiceRouterRoutesMatch(**match)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27b1744829f94d3e6e9164d8dc8da7e74e33b1c5cb58c11b87e8a82a0e73def7)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument match", value=match, expected_type=type_hints["match"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if destination is not None:
            self._values["destination"] = destination
        if match is not None:
            self._values["match"] = match

    @builtins.property
    def destination(
        self,
    ) -> typing.Optional["ConfigEntryServiceRouterRoutesDestination"]:
        '''destination block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#destination ConfigEntryServiceRouter#destination}
        '''
        result = self._values.get("destination")
        return typing.cast(typing.Optional["ConfigEntryServiceRouterRoutesDestination"], result)

    @builtins.property
    def match(self) -> typing.Optional["ConfigEntryServiceRouterRoutesMatch"]:
        '''match block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#match ConfigEntryServiceRouter#match}
        '''
        result = self._values.get("match")
        return typing.cast(typing.Optional["ConfigEntryServiceRouterRoutesMatch"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceRouterRoutes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesDestination",
    jsii_struct_bases=[],
    name_mapping={
        "idle_timeout": "idleTimeout",
        "namespace": "namespace",
        "num_retries": "numRetries",
        "partition": "partition",
        "prefix_rewrite": "prefixRewrite",
        "request_headers": "requestHeaders",
        "request_timeout": "requestTimeout",
        "response_headers": "responseHeaders",
        "retry_on": "retryOn",
        "retry_on_connect_failure": "retryOnConnectFailure",
        "retry_on_status_codes": "retryOnStatusCodes",
        "service": "service",
        "service_subset": "serviceSubset",
    },
)
class ConfigEntryServiceRouterRoutesDestination:
    def __init__(
        self,
        *,
        idle_timeout: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        num_retries: typing.Optional[jsii.Number] = None,
        partition: typing.Optional[builtins.str] = None,
        prefix_rewrite: typing.Optional[builtins.str] = None,
        request_headers: typing.Optional[typing.Union["ConfigEntryServiceRouterRoutesDestinationRequestHeaders", typing.Dict[builtins.str, typing.Any]]] = None,
        request_timeout: typing.Optional[builtins.str] = None,
        response_headers: typing.Optional[typing.Union["ConfigEntryServiceRouterRoutesDestinationResponseHeaders", typing.Dict[builtins.str, typing.Any]]] = None,
        retry_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        retry_on_connect_failure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        retry_on_status_codes: typing.Optional[typing.Sequence[jsii.Number]] = None,
        service: typing.Optional[builtins.str] = None,
        service_subset: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param idle_timeout: Specifies the total amount of time permitted for the request stream to be idle. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#idle_timeout ConfigEntryServiceRouter#idle_timeout}
        :param namespace: Specifies the Consul namespace to resolve the service from instead of the current namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#namespace ConfigEntryServiceRouter#namespace}
        :param num_retries: Specifies the number of times to retry the request when a retry condition occurs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#num_retries ConfigEntryServiceRouter#num_retries}
        :param partition: Specifies the Consul admin partition to resolve the service from instead of the current partition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#partition ConfigEntryServiceRouter#partition}
        :param prefix_rewrite: Specifies rewrites to the HTTP request path before proxying it to its final destination. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#prefix_rewrite ConfigEntryServiceRouter#prefix_rewrite}
        :param request_headers: request_headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#request_headers ConfigEntryServiceRouter#request_headers}
        :param request_timeout: Specifies the total amount of time permitted for the entire downstream request to be processed, including retry attempts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#request_timeout ConfigEntryServiceRouter#request_timeout}
        :param response_headers: response_headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#response_headers ConfigEntryServiceRouter#response_headers}
        :param retry_on: Specifies a list of conditions for Consul to retry requests based on the response from an upstream service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#retry_on ConfigEntryServiceRouter#retry_on}
        :param retry_on_connect_failure: Specifies that connection failure errors that trigger a retry request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#retry_on_connect_failure ConfigEntryServiceRouter#retry_on_connect_failure}
        :param retry_on_status_codes: Specifies a list of integers for HTTP response status codes that trigger a retry request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#retry_on_status_codes ConfigEntryServiceRouter#retry_on_status_codes}
        :param service: Specifies the name of the service to resolve. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#service ConfigEntryServiceRouter#service}
        :param service_subset: Specifies a named subset of the given service to resolve instead of the one defined as that service's ``default_subset`` in the service resolver configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#service_subset ConfigEntryServiceRouter#service_subset}
        '''
        if isinstance(request_headers, dict):
            request_headers = ConfigEntryServiceRouterRoutesDestinationRequestHeaders(**request_headers)
        if isinstance(response_headers, dict):
            response_headers = ConfigEntryServiceRouterRoutesDestinationResponseHeaders(**response_headers)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f348a97204293a80af2540eca14e70002c6b72a83aad9cd41672f41755a2b017)
            check_type(argname="argument idle_timeout", value=idle_timeout, expected_type=type_hints["idle_timeout"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument num_retries", value=num_retries, expected_type=type_hints["num_retries"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument prefix_rewrite", value=prefix_rewrite, expected_type=type_hints["prefix_rewrite"])
            check_type(argname="argument request_headers", value=request_headers, expected_type=type_hints["request_headers"])
            check_type(argname="argument request_timeout", value=request_timeout, expected_type=type_hints["request_timeout"])
            check_type(argname="argument response_headers", value=response_headers, expected_type=type_hints["response_headers"])
            check_type(argname="argument retry_on", value=retry_on, expected_type=type_hints["retry_on"])
            check_type(argname="argument retry_on_connect_failure", value=retry_on_connect_failure, expected_type=type_hints["retry_on_connect_failure"])
            check_type(argname="argument retry_on_status_codes", value=retry_on_status_codes, expected_type=type_hints["retry_on_status_codes"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument service_subset", value=service_subset, expected_type=type_hints["service_subset"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if idle_timeout is not None:
            self._values["idle_timeout"] = idle_timeout
        if namespace is not None:
            self._values["namespace"] = namespace
        if num_retries is not None:
            self._values["num_retries"] = num_retries
        if partition is not None:
            self._values["partition"] = partition
        if prefix_rewrite is not None:
            self._values["prefix_rewrite"] = prefix_rewrite
        if request_headers is not None:
            self._values["request_headers"] = request_headers
        if request_timeout is not None:
            self._values["request_timeout"] = request_timeout
        if response_headers is not None:
            self._values["response_headers"] = response_headers
        if retry_on is not None:
            self._values["retry_on"] = retry_on
        if retry_on_connect_failure is not None:
            self._values["retry_on_connect_failure"] = retry_on_connect_failure
        if retry_on_status_codes is not None:
            self._values["retry_on_status_codes"] = retry_on_status_codes
        if service is not None:
            self._values["service"] = service
        if service_subset is not None:
            self._values["service_subset"] = service_subset

    @builtins.property
    def idle_timeout(self) -> typing.Optional[builtins.str]:
        '''Specifies the total amount of time permitted for the request stream to be idle.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#idle_timeout ConfigEntryServiceRouter#idle_timeout}
        '''
        result = self._values.get("idle_timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Specifies the Consul namespace to resolve the service from instead of the current namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#namespace ConfigEntryServiceRouter#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def num_retries(self) -> typing.Optional[jsii.Number]:
        '''Specifies the number of times to retry the request when a retry condition occurs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#num_retries ConfigEntryServiceRouter#num_retries}
        '''
        result = self._values.get("num_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''Specifies the Consul admin partition to resolve the service from instead of the current partition.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#partition ConfigEntryServiceRouter#partition}
        '''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix_rewrite(self) -> typing.Optional[builtins.str]:
        '''Specifies rewrites to the HTTP request path before proxying it to its final destination.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#prefix_rewrite ConfigEntryServiceRouter#prefix_rewrite}
        '''
        result = self._values.get("prefix_rewrite")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_headers(
        self,
    ) -> typing.Optional["ConfigEntryServiceRouterRoutesDestinationRequestHeaders"]:
        '''request_headers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#request_headers ConfigEntryServiceRouter#request_headers}
        '''
        result = self._values.get("request_headers")
        return typing.cast(typing.Optional["ConfigEntryServiceRouterRoutesDestinationRequestHeaders"], result)

    @builtins.property
    def request_timeout(self) -> typing.Optional[builtins.str]:
        '''Specifies the total amount of time permitted for the entire downstream request to be processed, including retry attempts.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#request_timeout ConfigEntryServiceRouter#request_timeout}
        '''
        result = self._values.get("request_timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def response_headers(
        self,
    ) -> typing.Optional["ConfigEntryServiceRouterRoutesDestinationResponseHeaders"]:
        '''response_headers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#response_headers ConfigEntryServiceRouter#response_headers}
        '''
        result = self._values.get("response_headers")
        return typing.cast(typing.Optional["ConfigEntryServiceRouterRoutesDestinationResponseHeaders"], result)

    @builtins.property
    def retry_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies a list of conditions for Consul to retry requests based on the response from an upstream service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#retry_on ConfigEntryServiceRouter#retry_on}
        '''
        result = self._values.get("retry_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def retry_on_connect_failure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies that connection failure errors that trigger a retry request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#retry_on_connect_failure ConfigEntryServiceRouter#retry_on_connect_failure}
        '''
        result = self._values.get("retry_on_connect_failure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def retry_on_status_codes(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Specifies a list of integers for HTTP response status codes that trigger a retry request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#retry_on_status_codes ConfigEntryServiceRouter#retry_on_status_codes}
        '''
        result = self._values.get("retry_on_status_codes")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of the service to resolve.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#service ConfigEntryServiceRouter#service}
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_subset(self) -> typing.Optional[builtins.str]:
        '''Specifies a named subset of the given service to resolve instead of the one defined as that service's ``default_subset`` in the service resolver configuration entry.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#service_subset ConfigEntryServiceRouter#service_subset}
        '''
        result = self._values.get("service_subset")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceRouterRoutesDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceRouterRoutesDestinationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesDestinationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae3dd844e8d915c99b603a252ad7bdbc7bfb7fbba961785bc9d0ca9518744682)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRequestHeaders")
    def put_request_headers(
        self,
        *,
        add: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        remove: typing.Optional[typing.Sequence[builtins.str]] = None,
        set: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param add: Defines a set of key-value pairs to add to the header. Use header names as the keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#add ConfigEntryServiceRouter#add}
        :param remove: Defines a list of headers to remove. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#remove ConfigEntryServiceRouter#remove}
        :param set: Defines a set of key-value pairs to add to the request header or to replace existing header values with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#set ConfigEntryServiceRouter#set}
        '''
        value = ConfigEntryServiceRouterRoutesDestinationRequestHeaders(
            add=add, remove=remove, set=set
        )

        return typing.cast(None, jsii.invoke(self, "putRequestHeaders", [value]))

    @jsii.member(jsii_name="putResponseHeaders")
    def put_response_headers(
        self,
        *,
        add: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        remove: typing.Optional[typing.Sequence[builtins.str]] = None,
        set: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param add: Defines a set of key-value pairs to add to the header. Use header names as the keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#add ConfigEntryServiceRouter#add}
        :param remove: Defines a list of headers to remove. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#remove ConfigEntryServiceRouter#remove}
        :param set: Defines a set of key-value pairs to add to the response header or to replace existing header values with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#set ConfigEntryServiceRouter#set}
        '''
        value = ConfigEntryServiceRouterRoutesDestinationResponseHeaders(
            add=add, remove=remove, set=set
        )

        return typing.cast(None, jsii.invoke(self, "putResponseHeaders", [value]))

    @jsii.member(jsii_name="resetIdleTimeout")
    def reset_idle_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdleTimeout", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNumRetries")
    def reset_num_retries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumRetries", []))

    @jsii.member(jsii_name="resetPartition")
    def reset_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartition", []))

    @jsii.member(jsii_name="resetPrefixRewrite")
    def reset_prefix_rewrite(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefixRewrite", []))

    @jsii.member(jsii_name="resetRequestHeaders")
    def reset_request_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestHeaders", []))

    @jsii.member(jsii_name="resetRequestTimeout")
    def reset_request_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestTimeout", []))

    @jsii.member(jsii_name="resetResponseHeaders")
    def reset_response_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseHeaders", []))

    @jsii.member(jsii_name="resetRetryOn")
    def reset_retry_on(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryOn", []))

    @jsii.member(jsii_name="resetRetryOnConnectFailure")
    def reset_retry_on_connect_failure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryOnConnectFailure", []))

    @jsii.member(jsii_name="resetRetryOnStatusCodes")
    def reset_retry_on_status_codes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryOnStatusCodes", []))

    @jsii.member(jsii_name="resetService")
    def reset_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetService", []))

    @jsii.member(jsii_name="resetServiceSubset")
    def reset_service_subset(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceSubset", []))

    @builtins.property
    @jsii.member(jsii_name="requestHeaders")
    def request_headers(
        self,
    ) -> "ConfigEntryServiceRouterRoutesDestinationRequestHeadersOutputReference":
        return typing.cast("ConfigEntryServiceRouterRoutesDestinationRequestHeadersOutputReference", jsii.get(self, "requestHeaders"))

    @builtins.property
    @jsii.member(jsii_name="responseHeaders")
    def response_headers(
        self,
    ) -> "ConfigEntryServiceRouterRoutesDestinationResponseHeadersOutputReference":
        return typing.cast("ConfigEntryServiceRouterRoutesDestinationResponseHeadersOutputReference", jsii.get(self, "responseHeaders"))

    @builtins.property
    @jsii.member(jsii_name="idleTimeoutInput")
    def idle_timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idleTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="numRetriesInput")
    def num_retries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numRetriesInput"))

    @builtins.property
    @jsii.member(jsii_name="partitionInput")
    def partition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "partitionInput"))

    @builtins.property
    @jsii.member(jsii_name="prefixRewriteInput")
    def prefix_rewrite_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixRewriteInput"))

    @builtins.property
    @jsii.member(jsii_name="requestHeadersInput")
    def request_headers_input(
        self,
    ) -> typing.Optional["ConfigEntryServiceRouterRoutesDestinationRequestHeaders"]:
        return typing.cast(typing.Optional["ConfigEntryServiceRouterRoutesDestinationRequestHeaders"], jsii.get(self, "requestHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="requestTimeoutInput")
    def request_timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="responseHeadersInput")
    def response_headers_input(
        self,
    ) -> typing.Optional["ConfigEntryServiceRouterRoutesDestinationResponseHeaders"]:
        return typing.cast(typing.Optional["ConfigEntryServiceRouterRoutesDestinationResponseHeaders"], jsii.get(self, "responseHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="retryOnConnectFailureInput")
    def retry_on_connect_failure_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "retryOnConnectFailureInput"))

    @builtins.property
    @jsii.member(jsii_name="retryOnInput")
    def retry_on_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "retryOnInput"))

    @builtins.property
    @jsii.member(jsii_name="retryOnStatusCodesInput")
    def retry_on_status_codes_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "retryOnStatusCodesInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceSubsetInput")
    def service_subset_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceSubsetInput"))

    @builtins.property
    @jsii.member(jsii_name="idleTimeout")
    def idle_timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idleTimeout"))

    @idle_timeout.setter
    def idle_timeout(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e6bcbc99794c6e58416a7d6d4263721ba66875de32b200b64d553fb06ae6251)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idleTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f79e7921269b52b3aae35d7fda0ea61e89d7749e0e5e6282f55b85695cd7e1e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numRetries")
    def num_retries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numRetries"))

    @num_retries.setter
    def num_retries(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ecb0f1002efcc723b7305ea070410e01815f7d626ef88c935ca9b833cc84805)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numRetries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partition")
    def partition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partition"))

    @partition.setter
    def partition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9268f10d56fdcb25299df51da51162d75abdd0d40e484dcf1d6fb3ee4f377f10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prefixRewrite")
    def prefix_rewrite(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefixRewrite"))

    @prefix_rewrite.setter
    def prefix_rewrite(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9d75bfde3498cf869638c2e90f331da008a29cc293e6ae6a6983b4354e00192)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefixRewrite", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestTimeout")
    def request_timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestTimeout"))

    @request_timeout.setter
    def request_timeout(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66b683529080fd370ebd1b26d178475a3a8bf98044636080f4a2805899ec1ffd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retryOn")
    def retry_on(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "retryOn"))

    @retry_on.setter
    def retry_on(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d26a86087e4ab40bb82363446d9e3b36b4f3e67f9c5f6fb28a00cf84ddbcb24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retryOn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retryOnConnectFailure")
    def retry_on_connect_failure(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "retryOnConnectFailure"))

    @retry_on_connect_failure.setter
    def retry_on_connect_failure(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3a4cd58e7c47a6b4e3186d99d2c9cd15dc97c4cc92a47cd55169b3160818c8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retryOnConnectFailure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retryOnStatusCodes")
    def retry_on_status_codes(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "retryOnStatusCodes"))

    @retry_on_status_codes.setter
    def retry_on_status_codes(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c36181ef8204c897210b8cf9133121433c20a884f3e93d380fe05b1859d71ee6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retryOnStatusCodes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6842c80a83c52e24e7e259f72b627cad84bda16dc2766952e711330b636b5ef3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "service", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceSubset")
    def service_subset(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceSubset"))

    @service_subset.setter
    def service_subset(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ec749ac74c4c0d277847a2576a538b7aff8c11cc9ff9144721852c4a694377e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceSubset", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ConfigEntryServiceRouterRoutesDestination]:
        return typing.cast(typing.Optional[ConfigEntryServiceRouterRoutesDestination], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ConfigEntryServiceRouterRoutesDestination],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c01ad4e4bcf32883b12b0dcbe9517fb32f64a290dbaa8990e2cf9bb7ea2b8778)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesDestinationRequestHeaders",
    jsii_struct_bases=[],
    name_mapping={"add": "add", "remove": "remove", "set": "set"},
)
class ConfigEntryServiceRouterRoutesDestinationRequestHeaders:
    def __init__(
        self,
        *,
        add: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        remove: typing.Optional[typing.Sequence[builtins.str]] = None,
        set: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param add: Defines a set of key-value pairs to add to the header. Use header names as the keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#add ConfigEntryServiceRouter#add}
        :param remove: Defines a list of headers to remove. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#remove ConfigEntryServiceRouter#remove}
        :param set: Defines a set of key-value pairs to add to the request header or to replace existing header values with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#set ConfigEntryServiceRouter#set}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7b5558a8414ce324e4d599aa93400ab12550e54ef0aa1496f897502ab13349e)
            check_type(argname="argument add", value=add, expected_type=type_hints["add"])
            check_type(argname="argument remove", value=remove, expected_type=type_hints["remove"])
            check_type(argname="argument set", value=set, expected_type=type_hints["set"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if add is not None:
            self._values["add"] = add
        if remove is not None:
            self._values["remove"] = remove
        if set is not None:
            self._values["set"] = set

    @builtins.property
    def add(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Defines a set of key-value pairs to add to the header. Use header names as the keys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#add ConfigEntryServiceRouter#add}
        '''
        result = self._values.get("add")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def remove(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Defines a list of headers to remove.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#remove ConfigEntryServiceRouter#remove}
        '''
        result = self._values.get("remove")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def set(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Defines a set of key-value pairs to add to the request header or to replace existing header values with.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#set ConfigEntryServiceRouter#set}
        '''
        result = self._values.get("set")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceRouterRoutesDestinationRequestHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceRouterRoutesDestinationRequestHeadersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesDestinationRequestHeadersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c198d80b2e722f08d494b9ad1c07c7fb1ba15aeb35a8376cf7a01a14c404d36)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAdd")
    def reset_add(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdd", []))

    @jsii.member(jsii_name="resetRemove")
    def reset_remove(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemove", []))

    @jsii.member(jsii_name="resetSet")
    def reset_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSet", []))

    @builtins.property
    @jsii.member(jsii_name="addInput")
    def add_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "addInput"))

    @builtins.property
    @jsii.member(jsii_name="removeInput")
    def remove_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "removeInput"))

    @builtins.property
    @jsii.member(jsii_name="setInput")
    def set_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "setInput"))

    @builtins.property
    @jsii.member(jsii_name="add")
    def add(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "add"))

    @add.setter
    def add(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f77891bc05682bcb842ce8ca7c1e0b1a849360cc9ea5d9e1b5cfe620688fd7ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "add", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="remove")
    def remove(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "remove"))

    @remove.setter
    def remove(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab3c2595b35a522bedda24626782464ee975b05c1dd8995afdf0e1f348139eac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "remove", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="set")
    def set(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "set"))

    @set.setter
    def set(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16f9622ef35feeaeffaf57616c14456a10a4030b2ddd443a382643500a50333c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "set", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ConfigEntryServiceRouterRoutesDestinationRequestHeaders]:
        return typing.cast(typing.Optional[ConfigEntryServiceRouterRoutesDestinationRequestHeaders], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ConfigEntryServiceRouterRoutesDestinationRequestHeaders],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79a0d37629b173c610f64e292135b95c247b2f56ce34e4e59fbb1bd4bd6558f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesDestinationResponseHeaders",
    jsii_struct_bases=[],
    name_mapping={"add": "add", "remove": "remove", "set": "set"},
)
class ConfigEntryServiceRouterRoutesDestinationResponseHeaders:
    def __init__(
        self,
        *,
        add: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        remove: typing.Optional[typing.Sequence[builtins.str]] = None,
        set: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param add: Defines a set of key-value pairs to add to the header. Use header names as the keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#add ConfigEntryServiceRouter#add}
        :param remove: Defines a list of headers to remove. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#remove ConfigEntryServiceRouter#remove}
        :param set: Defines a set of key-value pairs to add to the response header or to replace existing header values with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#set ConfigEntryServiceRouter#set}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a7898ef052c68c22686693e1f2dbf9e238afb7ea56d290b82f83a40c6cede46)
            check_type(argname="argument add", value=add, expected_type=type_hints["add"])
            check_type(argname="argument remove", value=remove, expected_type=type_hints["remove"])
            check_type(argname="argument set", value=set, expected_type=type_hints["set"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if add is not None:
            self._values["add"] = add
        if remove is not None:
            self._values["remove"] = remove
        if set is not None:
            self._values["set"] = set

    @builtins.property
    def add(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Defines a set of key-value pairs to add to the header. Use header names as the keys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#add ConfigEntryServiceRouter#add}
        '''
        result = self._values.get("add")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def remove(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Defines a list of headers to remove.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#remove ConfigEntryServiceRouter#remove}
        '''
        result = self._values.get("remove")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def set(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Defines a set of key-value pairs to add to the response header or to replace existing header values with.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#set ConfigEntryServiceRouter#set}
        '''
        result = self._values.get("set")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceRouterRoutesDestinationResponseHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceRouterRoutesDestinationResponseHeadersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesDestinationResponseHeadersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__98e51d0967f91422384f81bf21e0a761b5c0677f6d0dc214ef80dbb2cb523518)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAdd")
    def reset_add(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdd", []))

    @jsii.member(jsii_name="resetRemove")
    def reset_remove(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemove", []))

    @jsii.member(jsii_name="resetSet")
    def reset_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSet", []))

    @builtins.property
    @jsii.member(jsii_name="addInput")
    def add_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "addInput"))

    @builtins.property
    @jsii.member(jsii_name="removeInput")
    def remove_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "removeInput"))

    @builtins.property
    @jsii.member(jsii_name="setInput")
    def set_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "setInput"))

    @builtins.property
    @jsii.member(jsii_name="add")
    def add(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "add"))

    @add.setter
    def add(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d61cd9956d392515215e01cc0354421a8901fa0e44d30eb2499358c370653dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "add", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="remove")
    def remove(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "remove"))

    @remove.setter
    def remove(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9471a9a52e7261d3d7cbf713f642d5a6d258a7135927c7915268f2b9fa473a59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "remove", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="set")
    def set(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "set"))

    @set.setter
    def set(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__574c543d6d4d4ecc23c03a489f401e12bef914c76b429569336f320721628760)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "set", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ConfigEntryServiceRouterRoutesDestinationResponseHeaders]:
        return typing.cast(typing.Optional[ConfigEntryServiceRouterRoutesDestinationResponseHeaders], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ConfigEntryServiceRouterRoutesDestinationResponseHeaders],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae30736c427470d59df0cd6a14d0f77eb44257057bcbe027232dc33f15008845)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceRouterRoutesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0a20df7c02fdce63843c4f43e2f412121645f9dc1e92c607614e9bf109e7931b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceRouterRoutesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1eb8eaaa229cddb1f73f8a3b547eff7a2abb6d8cc4cc88c60a543bcd93e3c52b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceRouterRoutesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74e9081b6c0d38013719ad1392f78843f79c28a540322c85ca8ef5a4281fe900)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bb8cb9980597290a129def75c1b675150f1072e43f91fb00b7c9723b2b1b4a35)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e8f4df70a824a476e964169d8d97bfb5805ba6fe78bab987a78b8ade3618ea0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutes]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutes]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutes]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e052e332fd57d7052c20246b93b031984c5edef673c8d9cb10ff89232ce7c009)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesMatch",
    jsii_struct_bases=[],
    name_mapping={"http": "http"},
)
class ConfigEntryServiceRouterRoutesMatch:
    def __init__(
        self,
        *,
        http: typing.Optional[typing.Union["ConfigEntryServiceRouterRoutesMatchHttp", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param http: http block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#http ConfigEntryServiceRouter#http}
        '''
        if isinstance(http, dict):
            http = ConfigEntryServiceRouterRoutesMatchHttp(**http)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e6375246cd2e21a0163b27f98a9f4fa6021a979933061b7b7f74462552663af)
            check_type(argname="argument http", value=http, expected_type=type_hints["http"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if http is not None:
            self._values["http"] = http

    @builtins.property
    def http(self) -> typing.Optional["ConfigEntryServiceRouterRoutesMatchHttp"]:
        '''http block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#http ConfigEntryServiceRouter#http}
        '''
        result = self._values.get("http")
        return typing.cast(typing.Optional["ConfigEntryServiceRouterRoutesMatchHttp"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceRouterRoutesMatch(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesMatchHttp",
    jsii_struct_bases=[],
    name_mapping={
        "header": "header",
        "methods": "methods",
        "path_exact": "pathExact",
        "path_prefix": "pathPrefix",
        "path_regex": "pathRegex",
        "query_param": "queryParam",
    },
)
class ConfigEntryServiceRouterRoutesMatchHttp:
    def __init__(
        self,
        *,
        header: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceRouterRoutesMatchHttpHeader", typing.Dict[builtins.str, typing.Any]]]]] = None,
        methods: typing.Optional[typing.Sequence[builtins.str]] = None,
        path_exact: typing.Optional[builtins.str] = None,
        path_prefix: typing.Optional[builtins.str] = None,
        path_regex: typing.Optional[builtins.str] = None,
        query_param: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceRouterRoutesMatchHttpQueryParam", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param header: header block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#header ConfigEntryServiceRouter#header}
        :param methods: Specifies HTTP methods that the match applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#methods ConfigEntryServiceRouter#methods}
        :param path_exact: Specifies the exact path to match on the HTTP request path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#path_exact ConfigEntryServiceRouter#path_exact}
        :param path_prefix: Specifies the path prefix to match on the HTTP request path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#path_prefix ConfigEntryServiceRouter#path_prefix}
        :param path_regex: Specifies a regular expression to match on the HTTP request path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#path_regex ConfigEntryServiceRouter#path_regex}
        :param query_param: query_param block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#query_param ConfigEntryServiceRouter#query_param}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46ed5bef545c5dd01b3c07c19cde3add14ddbe5dcb22d010bad90a8bec8a0a0c)
            check_type(argname="argument header", value=header, expected_type=type_hints["header"])
            check_type(argname="argument methods", value=methods, expected_type=type_hints["methods"])
            check_type(argname="argument path_exact", value=path_exact, expected_type=type_hints["path_exact"])
            check_type(argname="argument path_prefix", value=path_prefix, expected_type=type_hints["path_prefix"])
            check_type(argname="argument path_regex", value=path_regex, expected_type=type_hints["path_regex"])
            check_type(argname="argument query_param", value=query_param, expected_type=type_hints["query_param"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if header is not None:
            self._values["header"] = header
        if methods is not None:
            self._values["methods"] = methods
        if path_exact is not None:
            self._values["path_exact"] = path_exact
        if path_prefix is not None:
            self._values["path_prefix"] = path_prefix
        if path_regex is not None:
            self._values["path_regex"] = path_regex
        if query_param is not None:
            self._values["query_param"] = query_param

    @builtins.property
    def header(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceRouterRoutesMatchHttpHeader"]]]:
        '''header block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#header ConfigEntryServiceRouter#header}
        '''
        result = self._values.get("header")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceRouterRoutesMatchHttpHeader"]]], result)

    @builtins.property
    def methods(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies HTTP methods that the match applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#methods ConfigEntryServiceRouter#methods}
        '''
        result = self._values.get("methods")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def path_exact(self) -> typing.Optional[builtins.str]:
        '''Specifies the exact path to match on the HTTP request path.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#path_exact ConfigEntryServiceRouter#path_exact}
        '''
        result = self._values.get("path_exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path_prefix(self) -> typing.Optional[builtins.str]:
        '''Specifies the path prefix to match on the HTTP request path.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#path_prefix ConfigEntryServiceRouter#path_prefix}
        '''
        result = self._values.get("path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path_regex(self) -> typing.Optional[builtins.str]:
        '''Specifies a regular expression to match on the HTTP request path.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#path_regex ConfigEntryServiceRouter#path_regex}
        '''
        result = self._values.get("path_regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def query_param(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceRouterRoutesMatchHttpQueryParam"]]]:
        '''query_param block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#query_param ConfigEntryServiceRouter#query_param}
        '''
        result = self._values.get("query_param")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceRouterRoutesMatchHttpQueryParam"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceRouterRoutesMatchHttp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesMatchHttpHeader",
    jsii_struct_bases=[],
    name_mapping={
        "exact": "exact",
        "invert": "invert",
        "name": "name",
        "prefix": "prefix",
        "present": "present",
        "regex": "regex",
        "suffix": "suffix",
    },
)
class ConfigEntryServiceRouterRoutesMatchHttpHeader:
    def __init__(
        self,
        *,
        exact: typing.Optional[builtins.str] = None,
        invert: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        present: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        regex: typing.Optional[builtins.str] = None,
        suffix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param exact: Specifies that a request matches when the header with the given name is this exact value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#exact ConfigEntryServiceRouter#exact}
        :param invert: Specifies that the logic for the HTTP header match should be inverted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#invert ConfigEntryServiceRouter#invert}
        :param name: Specifies the name of the HTTP header to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#name ConfigEntryServiceRouter#name}
        :param prefix: Specifies that a request matches when the header with the given name has this prefix. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#prefix ConfigEntryServiceRouter#prefix}
        :param present: Specifies that a request matches when the value in the ``name`` argument is present anywhere in the HTTP header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#present ConfigEntryServiceRouter#present}
        :param regex: Specifies that a request matches when the header with the given name matches this regular expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#regex ConfigEntryServiceRouter#regex}
        :param suffix: Specifies that a request matches when the header with the given name has this suffix. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#suffix ConfigEntryServiceRouter#suffix}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5738ecafaf92959d66953d4607dc76edffe927755131708d32dd91829df72994)
            check_type(argname="argument exact", value=exact, expected_type=type_hints["exact"])
            check_type(argname="argument invert", value=invert, expected_type=type_hints["invert"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument present", value=present, expected_type=type_hints["present"])
            check_type(argname="argument regex", value=regex, expected_type=type_hints["regex"])
            check_type(argname="argument suffix", value=suffix, expected_type=type_hints["suffix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exact is not None:
            self._values["exact"] = exact
        if invert is not None:
            self._values["invert"] = invert
        if name is not None:
            self._values["name"] = name
        if prefix is not None:
            self._values["prefix"] = prefix
        if present is not None:
            self._values["present"] = present
        if regex is not None:
            self._values["regex"] = regex
        if suffix is not None:
            self._values["suffix"] = suffix

    @builtins.property
    def exact(self) -> typing.Optional[builtins.str]:
        '''Specifies that a request matches when the header with the given name is this exact value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#exact ConfigEntryServiceRouter#exact}
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invert(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies that the logic for the HTTP header match should be inverted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#invert ConfigEntryServiceRouter#invert}
        '''
        result = self._values.get("invert")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of the HTTP header to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#name ConfigEntryServiceRouter#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Specifies that a request matches when the header with the given name has this prefix.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#prefix ConfigEntryServiceRouter#prefix}
        '''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def present(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies that a request matches when the value in the ``name`` argument is present anywhere in the HTTP header.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#present ConfigEntryServiceRouter#present}
        '''
        result = self._values.get("present")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def regex(self) -> typing.Optional[builtins.str]:
        '''Specifies that a request matches when the header with the given name matches this regular expression.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#regex ConfigEntryServiceRouter#regex}
        '''
        result = self._values.get("regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suffix(self) -> typing.Optional[builtins.str]:
        '''Specifies that a request matches when the header with the given name has this suffix.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#suffix ConfigEntryServiceRouter#suffix}
        '''
        result = self._values.get("suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceRouterRoutesMatchHttpHeader(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceRouterRoutesMatchHttpHeaderList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesMatchHttpHeaderList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b149c5ccd312779b571dab53fb009d515bed9f2fc3e40714dba12229141be656)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceRouterRoutesMatchHttpHeaderOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e1ddc09e64fe3796ba077ccd8510b22a237535cf8765b4e5dbbba3168e463ed)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceRouterRoutesMatchHttpHeaderOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bbe4e6b80bbca2e34f1a0c3f50de5433e8c9a2bd5b841f87f7e18249efa3a51)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad40388ccad8c89b2d4d6470d0eeab0245e7603168ebe0f85301e988baf194bf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8686337696b6633f12626b4418aa0466db26311e78e93ab64bb6e1857d7e593a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutesMatchHttpHeader]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutesMatchHttpHeader]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutesMatchHttpHeader]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7670431478d31712d1f3ca521c17c6c8eff59569f7832e9b86f7610bf1b8722)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceRouterRoutesMatchHttpHeaderOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesMatchHttpHeaderOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f64db1a0b93457346c41c6bacbd6b025aa4f65dc94b162ed6c6401da4e8392f1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetExact")
    def reset_exact(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExact", []))

    @jsii.member(jsii_name="resetInvert")
    def reset_invert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInvert", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetPresent")
    def reset_present(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPresent", []))

    @jsii.member(jsii_name="resetRegex")
    def reset_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegex", []))

    @jsii.member(jsii_name="resetSuffix")
    def reset_suffix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuffix", []))

    @builtins.property
    @jsii.member(jsii_name="exactInput")
    def exact_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "exactInput"))

    @builtins.property
    @jsii.member(jsii_name="invertInput")
    def invert_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "invertInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property
    @jsii.member(jsii_name="presentInput")
    def present_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "presentInput"))

    @builtins.property
    @jsii.member(jsii_name="regexInput")
    def regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regexInput"))

    @builtins.property
    @jsii.member(jsii_name="suffixInput")
    def suffix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "suffixInput"))

    @builtins.property
    @jsii.member(jsii_name="exact")
    def exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exact"))

    @exact.setter
    def exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b24a654bd1755b15400e89c8a25abeb4927892e847cd637c05848f3c00343ce1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="invert")
    def invert(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "invert"))

    @invert.setter
    def invert(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f284167742d74767c64a366c12e93c4cac778a220a16b3090af2d224952dc6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "invert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9ad1331b46e61f64ae20c140f25c1c56d6b2b9c1511c62e164b5e09bc2c9174)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4849403e4594e6f68ebcfa48682b8d4890234d2c95b921a993aa3dbf1c811963)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="present")
    def present(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "present"))

    @present.setter
    def present(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58dc3f56017404b20739ab7f07c1b1caa2520bf2947555988af56826bdcbc735)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "present", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regex")
    def regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regex"))

    @regex.setter
    def regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acbbc14d5327b51d41cce03f1981e6331eb67592e1e07307d3e112d6ba6fc19b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="suffix")
    def suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "suffix"))

    @suffix.setter
    def suffix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5a1429c841cc6c56f6df598cdef0877911eeb6b8c290b287c5885bc6fa6affb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "suffix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceRouterRoutesMatchHttpHeader]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceRouterRoutesMatchHttpHeader]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceRouterRoutesMatchHttpHeader]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d67e317a7e7bf5914f6ba4cfee662fb014de6bad1fccad9b5d0cbe3be65ac8e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceRouterRoutesMatchHttpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesMatchHttpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7e1aa7bc0b50743de9c7b00cf31be2ce38ca303e8b5ea270eb03ed553ddee44)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putHeader")
    def put_header(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceRouterRoutesMatchHttpHeader, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9168e50ee2be03d7b6fadfea36da6a3d0576b07b89b0a03919ed4aa861619698)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putHeader", [value]))

    @jsii.member(jsii_name="putQueryParam")
    def put_query_param(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceRouterRoutesMatchHttpQueryParam", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cb472fea0aaf83caf2cdcd2963d4ab8c8394796ff2aecbccd29bcfef9b60755)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putQueryParam", [value]))

    @jsii.member(jsii_name="resetHeader")
    def reset_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeader", []))

    @jsii.member(jsii_name="resetMethods")
    def reset_methods(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMethods", []))

    @jsii.member(jsii_name="resetPathExact")
    def reset_path_exact(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPathExact", []))

    @jsii.member(jsii_name="resetPathPrefix")
    def reset_path_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPathPrefix", []))

    @jsii.member(jsii_name="resetPathRegex")
    def reset_path_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPathRegex", []))

    @jsii.member(jsii_name="resetQueryParam")
    def reset_query_param(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryParam", []))

    @builtins.property
    @jsii.member(jsii_name="header")
    def header(self) -> ConfigEntryServiceRouterRoutesMatchHttpHeaderList:
        return typing.cast(ConfigEntryServiceRouterRoutesMatchHttpHeaderList, jsii.get(self, "header"))

    @builtins.property
    @jsii.member(jsii_name="queryParam")
    def query_param(self) -> "ConfigEntryServiceRouterRoutesMatchHttpQueryParamList":
        return typing.cast("ConfigEntryServiceRouterRoutesMatchHttpQueryParamList", jsii.get(self, "queryParam"))

    @builtins.property
    @jsii.member(jsii_name="headerInput")
    def header_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutesMatchHttpHeader]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutesMatchHttpHeader]]], jsii.get(self, "headerInput"))

    @builtins.property
    @jsii.member(jsii_name="methodsInput")
    def methods_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "methodsInput"))

    @builtins.property
    @jsii.member(jsii_name="pathExactInput")
    def path_exact_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathExactInput"))

    @builtins.property
    @jsii.member(jsii_name="pathPrefixInput")
    def path_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathPrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="pathRegexInput")
    def path_regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathRegexInput"))

    @builtins.property
    @jsii.member(jsii_name="queryParamInput")
    def query_param_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceRouterRoutesMatchHttpQueryParam"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceRouterRoutesMatchHttpQueryParam"]]], jsii.get(self, "queryParamInput"))

    @builtins.property
    @jsii.member(jsii_name="methods")
    def methods(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "methods"))

    @methods.setter
    def methods(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e175483dbc7cd7288ad3f30e85bf1fde0414a3439d4514fda54f65538bb31d52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "methods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathExact")
    def path_exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathExact"))

    @path_exact.setter
    def path_exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29b510c1a2187d414f25b85a624960c808f806d0d37158fd7abe7109e2df41ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathExact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathPrefix")
    def path_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathPrefix"))

    @path_prefix.setter
    def path_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ee298bbb04ec046444bb2165b24e18d960b82b1cc13801d21871d82f04f1bd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathPrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathRegex")
    def path_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathRegex"))

    @path_regex.setter
    def path_regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40544bcca574b3fe5791646af3549dfb2557dd8ad95a185fb1b74f8883c1475f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ConfigEntryServiceRouterRoutesMatchHttp]:
        return typing.cast(typing.Optional[ConfigEntryServiceRouterRoutesMatchHttp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ConfigEntryServiceRouterRoutesMatchHttp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4beee85ff47e8b0df13fbb238759aed963885904970f058f1e5ba70ee6bf8309)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesMatchHttpQueryParam",
    jsii_struct_bases=[],
    name_mapping={
        "exact": "exact",
        "name": "name",
        "present": "present",
        "regex": "regex",
    },
)
class ConfigEntryServiceRouterRoutesMatchHttpQueryParam:
    def __init__(
        self,
        *,
        exact: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        present: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        regex: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param exact: Specifies that a request matches when the query parameter with the given name is this exact value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#exact ConfigEntryServiceRouter#exact}
        :param name: Specifies the name of the HTTP query parameter to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#name ConfigEntryServiceRouter#name}
        :param present: Specifies that a request matches when the value in the ``name`` argument is present anywhere in the HTTP query parameter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#present ConfigEntryServiceRouter#present}
        :param regex: Specifies that a request matches when the query parameter with the given name matches this regular expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#regex ConfigEntryServiceRouter#regex}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__012a857f72f98b5a2d8732a4f6c74e32c4f0ce835873d52c2648daa8645e3c1c)
            check_type(argname="argument exact", value=exact, expected_type=type_hints["exact"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument present", value=present, expected_type=type_hints["present"])
            check_type(argname="argument regex", value=regex, expected_type=type_hints["regex"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exact is not None:
            self._values["exact"] = exact
        if name is not None:
            self._values["name"] = name
        if present is not None:
            self._values["present"] = present
        if regex is not None:
            self._values["regex"] = regex

    @builtins.property
    def exact(self) -> typing.Optional[builtins.str]:
        '''Specifies that a request matches when the query parameter with the given name is this exact value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#exact ConfigEntryServiceRouter#exact}
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of the HTTP query parameter to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#name ConfigEntryServiceRouter#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def present(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies that a request matches when the value in the ``name`` argument is present anywhere in the HTTP query parameter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#present ConfigEntryServiceRouter#present}
        '''
        result = self._values.get("present")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def regex(self) -> typing.Optional[builtins.str]:
        '''Specifies that a request matches when the query parameter with the given name matches this regular expression.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#regex ConfigEntryServiceRouter#regex}
        '''
        result = self._values.get("regex")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceRouterRoutesMatchHttpQueryParam(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceRouterRoutesMatchHttpQueryParamList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesMatchHttpQueryParamList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2e20f0b4191593c84f010b89be110c1ad34ecbe054519239eeba27b05aa3334)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceRouterRoutesMatchHttpQueryParamOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4ed436cd03ff6e9fe2e24aa45bb37a71491d3a2bdfe4ce6c71e44f6683dac7e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceRouterRoutesMatchHttpQueryParamOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0466afdbd48dee7612c276c70f270e3607eb5d12d37de8e30fe64ebf879032e2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ebad889f1e4459998339343dfc6e9a2079527f9c6e9faef7c9cfe0b476958687)
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
            type_hints = typing.get_type_hints(_typecheckingstub__16a1187852ed855255009a3a6ee48a5095b700d23bac7ed5f1fc2145ab3e2645)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutesMatchHttpQueryParam]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutesMatchHttpQueryParam]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutesMatchHttpQueryParam]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b24fa31e563f7d83c5be1ddcf90821762312bf023e0a460671c50d05c2ab914e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceRouterRoutesMatchHttpQueryParamOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesMatchHttpQueryParamOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae697a9889f3ce819460413eae1d23ff5ef5e87eb0549dc2dc548cc9bd5ee4e3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetExact")
    def reset_exact(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExact", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPresent")
    def reset_present(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPresent", []))

    @jsii.member(jsii_name="resetRegex")
    def reset_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegex", []))

    @builtins.property
    @jsii.member(jsii_name="exactInput")
    def exact_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "exactInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="presentInput")
    def present_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "presentInput"))

    @builtins.property
    @jsii.member(jsii_name="regexInput")
    def regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regexInput"))

    @builtins.property
    @jsii.member(jsii_name="exact")
    def exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exact"))

    @exact.setter
    def exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6dfd556e50e857749dd626aa24d8df244122502ae08717a90a0e3df6c333cc25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a8818de253d52c68b1b1f4180a953cc0b05af61807537f573f2287ec6f5fa42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="present")
    def present(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "present"))

    @present.setter
    def present(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__833b3cb6c0df345c521bcf16d4d140cdd3eca0493cb5160a5be91aeb4d7727aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "present", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regex")
    def regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regex"))

    @regex.setter
    def regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccf6b48fa49bac3cb5d209051611028784733669b7758b3202230c7e3a67972c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceRouterRoutesMatchHttpQueryParam]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceRouterRoutesMatchHttpQueryParam]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceRouterRoutesMatchHttpQueryParam]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8fdb1ffc45e1be61a76c6a7d9b6548b8df7972497a198e8db65b41622356682)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceRouterRoutesMatchOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesMatchOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__90ca9133c7cb31840050ca74279a037973977bb05da4d81d307b01c466f9976b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putHttp")
    def put_http(
        self,
        *,
        header: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceRouterRoutesMatchHttpHeader, typing.Dict[builtins.str, typing.Any]]]]] = None,
        methods: typing.Optional[typing.Sequence[builtins.str]] = None,
        path_exact: typing.Optional[builtins.str] = None,
        path_prefix: typing.Optional[builtins.str] = None,
        path_regex: typing.Optional[builtins.str] = None,
        query_param: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceRouterRoutesMatchHttpQueryParam, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param header: header block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#header ConfigEntryServiceRouter#header}
        :param methods: Specifies HTTP methods that the match applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#methods ConfigEntryServiceRouter#methods}
        :param path_exact: Specifies the exact path to match on the HTTP request path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#path_exact ConfigEntryServiceRouter#path_exact}
        :param path_prefix: Specifies the path prefix to match on the HTTP request path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#path_prefix ConfigEntryServiceRouter#path_prefix}
        :param path_regex: Specifies a regular expression to match on the HTTP request path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#path_regex ConfigEntryServiceRouter#path_regex}
        :param query_param: query_param block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#query_param ConfigEntryServiceRouter#query_param}
        '''
        value = ConfigEntryServiceRouterRoutesMatchHttp(
            header=header,
            methods=methods,
            path_exact=path_exact,
            path_prefix=path_prefix,
            path_regex=path_regex,
            query_param=query_param,
        )

        return typing.cast(None, jsii.invoke(self, "putHttp", [value]))

    @jsii.member(jsii_name="resetHttp")
    def reset_http(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttp", []))

    @builtins.property
    @jsii.member(jsii_name="http")
    def http(self) -> ConfigEntryServiceRouterRoutesMatchHttpOutputReference:
        return typing.cast(ConfigEntryServiceRouterRoutesMatchHttpOutputReference, jsii.get(self, "http"))

    @builtins.property
    @jsii.member(jsii_name="httpInput")
    def http_input(self) -> typing.Optional[ConfigEntryServiceRouterRoutesMatchHttp]:
        return typing.cast(typing.Optional[ConfigEntryServiceRouterRoutesMatchHttp], jsii.get(self, "httpInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ConfigEntryServiceRouterRoutesMatch]:
        return typing.cast(typing.Optional[ConfigEntryServiceRouterRoutesMatch], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ConfigEntryServiceRouterRoutesMatch],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92b5b0ed725c907b599408802d900a92cc7cdc2ead4ce2d1bb41a2f1f92fd59d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceRouterRoutesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceRouter.ConfigEntryServiceRouterRoutesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3e9bd40d04bb65cbef02d2d5f97d431afad7149c10e79f0cd194be4d4ef18613)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putDestination")
    def put_destination(
        self,
        *,
        idle_timeout: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        num_retries: typing.Optional[jsii.Number] = None,
        partition: typing.Optional[builtins.str] = None,
        prefix_rewrite: typing.Optional[builtins.str] = None,
        request_headers: typing.Optional[typing.Union[ConfigEntryServiceRouterRoutesDestinationRequestHeaders, typing.Dict[builtins.str, typing.Any]]] = None,
        request_timeout: typing.Optional[builtins.str] = None,
        response_headers: typing.Optional[typing.Union[ConfigEntryServiceRouterRoutesDestinationResponseHeaders, typing.Dict[builtins.str, typing.Any]]] = None,
        retry_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        retry_on_connect_failure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        retry_on_status_codes: typing.Optional[typing.Sequence[jsii.Number]] = None,
        service: typing.Optional[builtins.str] = None,
        service_subset: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param idle_timeout: Specifies the total amount of time permitted for the request stream to be idle. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#idle_timeout ConfigEntryServiceRouter#idle_timeout}
        :param namespace: Specifies the Consul namespace to resolve the service from instead of the current namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#namespace ConfigEntryServiceRouter#namespace}
        :param num_retries: Specifies the number of times to retry the request when a retry condition occurs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#num_retries ConfigEntryServiceRouter#num_retries}
        :param partition: Specifies the Consul admin partition to resolve the service from instead of the current partition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#partition ConfigEntryServiceRouter#partition}
        :param prefix_rewrite: Specifies rewrites to the HTTP request path before proxying it to its final destination. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#prefix_rewrite ConfigEntryServiceRouter#prefix_rewrite}
        :param request_headers: request_headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#request_headers ConfigEntryServiceRouter#request_headers}
        :param request_timeout: Specifies the total amount of time permitted for the entire downstream request to be processed, including retry attempts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#request_timeout ConfigEntryServiceRouter#request_timeout}
        :param response_headers: response_headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#response_headers ConfigEntryServiceRouter#response_headers}
        :param retry_on: Specifies a list of conditions for Consul to retry requests based on the response from an upstream service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#retry_on ConfigEntryServiceRouter#retry_on}
        :param retry_on_connect_failure: Specifies that connection failure errors that trigger a retry request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#retry_on_connect_failure ConfigEntryServiceRouter#retry_on_connect_failure}
        :param retry_on_status_codes: Specifies a list of integers for HTTP response status codes that trigger a retry request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#retry_on_status_codes ConfigEntryServiceRouter#retry_on_status_codes}
        :param service: Specifies the name of the service to resolve. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#service ConfigEntryServiceRouter#service}
        :param service_subset: Specifies a named subset of the given service to resolve instead of the one defined as that service's ``default_subset`` in the service resolver configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#service_subset ConfigEntryServiceRouter#service_subset}
        '''
        value = ConfigEntryServiceRouterRoutesDestination(
            idle_timeout=idle_timeout,
            namespace=namespace,
            num_retries=num_retries,
            partition=partition,
            prefix_rewrite=prefix_rewrite,
            request_headers=request_headers,
            request_timeout=request_timeout,
            response_headers=response_headers,
            retry_on=retry_on,
            retry_on_connect_failure=retry_on_connect_failure,
            retry_on_status_codes=retry_on_status_codes,
            service=service,
            service_subset=service_subset,
        )

        return typing.cast(None, jsii.invoke(self, "putDestination", [value]))

    @jsii.member(jsii_name="putMatch")
    def put_match(
        self,
        *,
        http: typing.Optional[typing.Union[ConfigEntryServiceRouterRoutesMatchHttp, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param http: http block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_router#http ConfigEntryServiceRouter#http}
        '''
        value = ConfigEntryServiceRouterRoutesMatch(http=http)

        return typing.cast(None, jsii.invoke(self, "putMatch", [value]))

    @jsii.member(jsii_name="resetDestination")
    def reset_destination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestination", []))

    @jsii.member(jsii_name="resetMatch")
    def reset_match(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMatch", []))

    @builtins.property
    @jsii.member(jsii_name="destination")
    def destination(self) -> ConfigEntryServiceRouterRoutesDestinationOutputReference:
        return typing.cast(ConfigEntryServiceRouterRoutesDestinationOutputReference, jsii.get(self, "destination"))

    @builtins.property
    @jsii.member(jsii_name="match")
    def match(self) -> ConfigEntryServiceRouterRoutesMatchOutputReference:
        return typing.cast(ConfigEntryServiceRouterRoutesMatchOutputReference, jsii.get(self, "match"))

    @builtins.property
    @jsii.member(jsii_name="destinationInput")
    def destination_input(
        self,
    ) -> typing.Optional[ConfigEntryServiceRouterRoutesDestination]:
        return typing.cast(typing.Optional[ConfigEntryServiceRouterRoutesDestination], jsii.get(self, "destinationInput"))

    @builtins.property
    @jsii.member(jsii_name="matchInput")
    def match_input(self) -> typing.Optional[ConfigEntryServiceRouterRoutesMatch]:
        return typing.cast(typing.Optional[ConfigEntryServiceRouterRoutesMatch], jsii.get(self, "matchInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceRouterRoutes]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceRouterRoutes]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceRouterRoutes]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46597cd89a8afd2301d26e1907d5815299d5293b760db6a9505e1ae27e4b9514)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ConfigEntryServiceRouter",
    "ConfigEntryServiceRouterConfig",
    "ConfigEntryServiceRouterRoutes",
    "ConfigEntryServiceRouterRoutesDestination",
    "ConfigEntryServiceRouterRoutesDestinationOutputReference",
    "ConfigEntryServiceRouterRoutesDestinationRequestHeaders",
    "ConfigEntryServiceRouterRoutesDestinationRequestHeadersOutputReference",
    "ConfigEntryServiceRouterRoutesDestinationResponseHeaders",
    "ConfigEntryServiceRouterRoutesDestinationResponseHeadersOutputReference",
    "ConfigEntryServiceRouterRoutesList",
    "ConfigEntryServiceRouterRoutesMatch",
    "ConfigEntryServiceRouterRoutesMatchHttp",
    "ConfigEntryServiceRouterRoutesMatchHttpHeader",
    "ConfigEntryServiceRouterRoutesMatchHttpHeaderList",
    "ConfigEntryServiceRouterRoutesMatchHttpHeaderOutputReference",
    "ConfigEntryServiceRouterRoutesMatchHttpOutputReference",
    "ConfigEntryServiceRouterRoutesMatchHttpQueryParam",
    "ConfigEntryServiceRouterRoutesMatchHttpQueryParamList",
    "ConfigEntryServiceRouterRoutesMatchHttpQueryParamOutputReference",
    "ConfigEntryServiceRouterRoutesMatchOutputReference",
    "ConfigEntryServiceRouterRoutesOutputReference",
]

publication.publish()

def _typecheckingstub__cc4bd28f48c7eb9ce005a75a3fc4694fd361848541cd22bff3e04ceefc54685d(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceRouterRoutes, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__9ffbd434231779519b6374e49970f88f3846afc56ee921522aa624010463de71(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be7c1535be502c93299a701151767a2b7b3da9454f80ca4bf4d67b6d2b86d4ef(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceRouterRoutes, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0676af542542b823ec4033b0af3941fe430fb4ae9e2dfdc8f07ab59b911d9c96(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a314f352ac59babcfb0d4e84ce50f9364bd001691ebd06338956996b64671e5(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11f2a1c0c1cbbb7f6864f64742d4b8ef7b79e8372f5402a0411c678b639e274f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67fd12976f37299873b7fa015b284a3ddc4c6bc9074f487c13e92e8b23d85ca0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96e14066d718ad07d11660956936f0b9671147adb929993db4398f79a09cf6b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87c26c66def50e9b47026757204a56c6df07d976ff89ba51c2c9cdf22d1f49de(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceRouterRoutes, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27b1744829f94d3e6e9164d8dc8da7e74e33b1c5cb58c11b87e8a82a0e73def7(
    *,
    destination: typing.Optional[typing.Union[ConfigEntryServiceRouterRoutesDestination, typing.Dict[builtins.str, typing.Any]]] = None,
    match: typing.Optional[typing.Union[ConfigEntryServiceRouterRoutesMatch, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f348a97204293a80af2540eca14e70002c6b72a83aad9cd41672f41755a2b017(
    *,
    idle_timeout: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    num_retries: typing.Optional[jsii.Number] = None,
    partition: typing.Optional[builtins.str] = None,
    prefix_rewrite: typing.Optional[builtins.str] = None,
    request_headers: typing.Optional[typing.Union[ConfigEntryServiceRouterRoutesDestinationRequestHeaders, typing.Dict[builtins.str, typing.Any]]] = None,
    request_timeout: typing.Optional[builtins.str] = None,
    response_headers: typing.Optional[typing.Union[ConfigEntryServiceRouterRoutesDestinationResponseHeaders, typing.Dict[builtins.str, typing.Any]]] = None,
    retry_on: typing.Optional[typing.Sequence[builtins.str]] = None,
    retry_on_connect_failure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    retry_on_status_codes: typing.Optional[typing.Sequence[jsii.Number]] = None,
    service: typing.Optional[builtins.str] = None,
    service_subset: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae3dd844e8d915c99b603a252ad7bdbc7bfb7fbba961785bc9d0ca9518744682(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e6bcbc99794c6e58416a7d6d4263721ba66875de32b200b64d553fb06ae6251(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f79e7921269b52b3aae35d7fda0ea61e89d7749e0e5e6282f55b85695cd7e1e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ecb0f1002efcc723b7305ea070410e01815f7d626ef88c935ca9b833cc84805(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9268f10d56fdcb25299df51da51162d75abdd0d40e484dcf1d6fb3ee4f377f10(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9d75bfde3498cf869638c2e90f331da008a29cc293e6ae6a6983b4354e00192(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66b683529080fd370ebd1b26d178475a3a8bf98044636080f4a2805899ec1ffd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d26a86087e4ab40bb82363446d9e3b36b4f3e67f9c5f6fb28a00cf84ddbcb24(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3a4cd58e7c47a6b4e3186d99d2c9cd15dc97c4cc92a47cd55169b3160818c8d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c36181ef8204c897210b8cf9133121433c20a884f3e93d380fe05b1859d71ee6(
    value: typing.List[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6842c80a83c52e24e7e259f72b627cad84bda16dc2766952e711330b636b5ef3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ec749ac74c4c0d277847a2576a538b7aff8c11cc9ff9144721852c4a694377e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c01ad4e4bcf32883b12b0dcbe9517fb32f64a290dbaa8990e2cf9bb7ea2b8778(
    value: typing.Optional[ConfigEntryServiceRouterRoutesDestination],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7b5558a8414ce324e4d599aa93400ab12550e54ef0aa1496f897502ab13349e(
    *,
    add: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    remove: typing.Optional[typing.Sequence[builtins.str]] = None,
    set: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c198d80b2e722f08d494b9ad1c07c7fb1ba15aeb35a8376cf7a01a14c404d36(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f77891bc05682bcb842ce8ca7c1e0b1a849360cc9ea5d9e1b5cfe620688fd7ee(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab3c2595b35a522bedda24626782464ee975b05c1dd8995afdf0e1f348139eac(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16f9622ef35feeaeffaf57616c14456a10a4030b2ddd443a382643500a50333c(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79a0d37629b173c610f64e292135b95c247b2f56ce34e4e59fbb1bd4bd6558f5(
    value: typing.Optional[ConfigEntryServiceRouterRoutesDestinationRequestHeaders],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a7898ef052c68c22686693e1f2dbf9e238afb7ea56d290b82f83a40c6cede46(
    *,
    add: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    remove: typing.Optional[typing.Sequence[builtins.str]] = None,
    set: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98e51d0967f91422384f81bf21e0a761b5c0677f6d0dc214ef80dbb2cb523518(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d61cd9956d392515215e01cc0354421a8901fa0e44d30eb2499358c370653dd(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9471a9a52e7261d3d7cbf713f642d5a6d258a7135927c7915268f2b9fa473a59(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__574c543d6d4d4ecc23c03a489f401e12bef914c76b429569336f320721628760(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae30736c427470d59df0cd6a14d0f77eb44257057bcbe027232dc33f15008845(
    value: typing.Optional[ConfigEntryServiceRouterRoutesDestinationResponseHeaders],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a20df7c02fdce63843c4f43e2f412121645f9dc1e92c607614e9bf109e7931b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eb8eaaa229cddb1f73f8a3b547eff7a2abb6d8cc4cc88c60a543bcd93e3c52b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74e9081b6c0d38013719ad1392f78843f79c28a540322c85ca8ef5a4281fe900(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb8cb9980597290a129def75c1b675150f1072e43f91fb00b7c9723b2b1b4a35(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e8f4df70a824a476e964169d8d97bfb5805ba6fe78bab987a78b8ade3618ea0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e052e332fd57d7052c20246b93b031984c5edef673c8d9cb10ff89232ce7c009(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutes]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e6375246cd2e21a0163b27f98a9f4fa6021a979933061b7b7f74462552663af(
    *,
    http: typing.Optional[typing.Union[ConfigEntryServiceRouterRoutesMatchHttp, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46ed5bef545c5dd01b3c07c19cde3add14ddbe5dcb22d010bad90a8bec8a0a0c(
    *,
    header: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceRouterRoutesMatchHttpHeader, typing.Dict[builtins.str, typing.Any]]]]] = None,
    methods: typing.Optional[typing.Sequence[builtins.str]] = None,
    path_exact: typing.Optional[builtins.str] = None,
    path_prefix: typing.Optional[builtins.str] = None,
    path_regex: typing.Optional[builtins.str] = None,
    query_param: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceRouterRoutesMatchHttpQueryParam, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5738ecafaf92959d66953d4607dc76edffe927755131708d32dd91829df72994(
    *,
    exact: typing.Optional[builtins.str] = None,
    invert: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    prefix: typing.Optional[builtins.str] = None,
    present: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    regex: typing.Optional[builtins.str] = None,
    suffix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b149c5ccd312779b571dab53fb009d515bed9f2fc3e40714dba12229141be656(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e1ddc09e64fe3796ba077ccd8510b22a237535cf8765b4e5dbbba3168e463ed(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bbe4e6b80bbca2e34f1a0c3f50de5433e8c9a2bd5b841f87f7e18249efa3a51(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad40388ccad8c89b2d4d6470d0eeab0245e7603168ebe0f85301e988baf194bf(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8686337696b6633f12626b4418aa0466db26311e78e93ab64bb6e1857d7e593a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7670431478d31712d1f3ca521c17c6c8eff59569f7832e9b86f7610bf1b8722(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutesMatchHttpHeader]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f64db1a0b93457346c41c6bacbd6b025aa4f65dc94b162ed6c6401da4e8392f1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b24a654bd1755b15400e89c8a25abeb4927892e847cd637c05848f3c00343ce1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f284167742d74767c64a366c12e93c4cac778a220a16b3090af2d224952dc6e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9ad1331b46e61f64ae20c140f25c1c56d6b2b9c1511c62e164b5e09bc2c9174(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4849403e4594e6f68ebcfa48682b8d4890234d2c95b921a993aa3dbf1c811963(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58dc3f56017404b20739ab7f07c1b1caa2520bf2947555988af56826bdcbc735(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acbbc14d5327b51d41cce03f1981e6331eb67592e1e07307d3e112d6ba6fc19b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5a1429c841cc6c56f6df598cdef0877911eeb6b8c290b287c5885bc6fa6affb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d67e317a7e7bf5914f6ba4cfee662fb014de6bad1fccad9b5d0cbe3be65ac8e1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceRouterRoutesMatchHttpHeader]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7e1aa7bc0b50743de9c7b00cf31be2ce38ca303e8b5ea270eb03ed553ddee44(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9168e50ee2be03d7b6fadfea36da6a3d0576b07b89b0a03919ed4aa861619698(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceRouterRoutesMatchHttpHeader, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cb472fea0aaf83caf2cdcd2963d4ab8c8394796ff2aecbccd29bcfef9b60755(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceRouterRoutesMatchHttpQueryParam, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e175483dbc7cd7288ad3f30e85bf1fde0414a3439d4514fda54f65538bb31d52(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29b510c1a2187d414f25b85a624960c808f806d0d37158fd7abe7109e2df41ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ee298bbb04ec046444bb2165b24e18d960b82b1cc13801d21871d82f04f1bd3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40544bcca574b3fe5791646af3549dfb2557dd8ad95a185fb1b74f8883c1475f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4beee85ff47e8b0df13fbb238759aed963885904970f058f1e5ba70ee6bf8309(
    value: typing.Optional[ConfigEntryServiceRouterRoutesMatchHttp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__012a857f72f98b5a2d8732a4f6c74e32c4f0ce835873d52c2648daa8645e3c1c(
    *,
    exact: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    present: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    regex: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2e20f0b4191593c84f010b89be110c1ad34ecbe054519239eeba27b05aa3334(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4ed436cd03ff6e9fe2e24aa45bb37a71491d3a2bdfe4ce6c71e44f6683dac7e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0466afdbd48dee7612c276c70f270e3607eb5d12d37de8e30fe64ebf879032e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebad889f1e4459998339343dfc6e9a2079527f9c6e9faef7c9cfe0b476958687(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16a1187852ed855255009a3a6ee48a5095b700d23bac7ed5f1fc2145ab3e2645(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b24fa31e563f7d83c5be1ddcf90821762312bf023e0a460671c50d05c2ab914e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceRouterRoutesMatchHttpQueryParam]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae697a9889f3ce819460413eae1d23ff5ef5e87eb0549dc2dc548cc9bd5ee4e3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dfd556e50e857749dd626aa24d8df244122502ae08717a90a0e3df6c333cc25(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a8818de253d52c68b1b1f4180a953cc0b05af61807537f573f2287ec6f5fa42(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__833b3cb6c0df345c521bcf16d4d140cdd3eca0493cb5160a5be91aeb4d7727aa(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccf6b48fa49bac3cb5d209051611028784733669b7758b3202230c7e3a67972c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8fdb1ffc45e1be61a76c6a7d9b6548b8df7972497a198e8db65b41622356682(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceRouterRoutesMatchHttpQueryParam]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90ca9133c7cb31840050ca74279a037973977bb05da4d81d307b01c466f9976b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92b5b0ed725c907b599408802d900a92cc7cdc2ead4ce2d1bb41a2f1f92fd59d(
    value: typing.Optional[ConfigEntryServiceRouterRoutesMatch],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e9bd40d04bb65cbef02d2d5f97d431afad7149c10e79f0cd194be4d4ef18613(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46597cd89a8afd2301d26e1907d5815299d5293b760db6a9505e1ae27e4b9514(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceRouterRoutes]],
) -> None:
    """Type checking stubs"""
    pass
