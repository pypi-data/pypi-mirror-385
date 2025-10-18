r'''
# `consul_config_entry_service_intentions`

Refer to the Terraform Registry for docs: [`consul_config_entry_service_intentions`](https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions).
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


class ConfigEntryServiceIntentions(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentions",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions consul_config_entry_service_intentions}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        jwt: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsJwt", typing.Dict[builtins.str, typing.Any]]]]] = None,
        meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        sources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsSources", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions consul_config_entry_service_intentions} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Specifies a name of the destination service for all intentions defined in the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#name ConfigEntryServiceIntentions#name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#id ConfigEntryServiceIntentions#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwt: jwt block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#jwt ConfigEntryServiceIntentions#jwt}
        :param meta: Specifies key-value pairs to add to the KV store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#meta ConfigEntryServiceIntentions#meta}
        :param namespace: Specifies the namespace to apply the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#namespace ConfigEntryServiceIntentions#namespace}
        :param partition: Specifies the admin partition to apply the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#partition ConfigEntryServiceIntentions#partition}
        :param sources: sources block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#sources ConfigEntryServiceIntentions#sources}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77bc94afe70e67c56279ee8192cbf3d56ae765117ea7b2e7fb920901ff080b67)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConfigEntryServiceIntentionsConfig(
            name=name,
            id=id,
            jwt=jwt,
            meta=meta,
            namespace=namespace,
            partition=partition,
            sources=sources,
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
        '''Generates CDKTF code for importing a ConfigEntryServiceIntentions resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ConfigEntryServiceIntentions to import.
        :param import_from_id: The id of the existing ConfigEntryServiceIntentions that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ConfigEntryServiceIntentions to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83e2263425aeab1f72e7445a230df4f6e121782c8f11b3121ce8f21ea89c7900)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putJwt")
    def put_jwt(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsJwt", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2c268ebe2fb2761293a2fd032b921fb397e056757e0160051493426f7a362e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putJwt", [value]))

    @jsii.member(jsii_name="putSources")
    def put_sources(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsSources", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a46c9b9a7af02f787e087c47bbc6446d1f303c94f63858fbc540b29868d9aba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSources", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetJwt")
    def reset_jwt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwt", []))

    @jsii.member(jsii_name="resetMeta")
    def reset_meta(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMeta", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPartition")
    def reset_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartition", []))

    @jsii.member(jsii_name="resetSources")
    def reset_sources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSources", []))

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
    @jsii.member(jsii_name="jwt")
    def jwt(self) -> "ConfigEntryServiceIntentionsJwtList":
        return typing.cast("ConfigEntryServiceIntentionsJwtList", jsii.get(self, "jwt"))

    @builtins.property
    @jsii.member(jsii_name="sources")
    def sources(self) -> "ConfigEntryServiceIntentionsSourcesList":
        return typing.cast("ConfigEntryServiceIntentionsSourcesList", jsii.get(self, "sources"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtInput")
    def jwt_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsJwt"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsJwt"]]], jsii.get(self, "jwtInput"))

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
    @jsii.member(jsii_name="sourcesInput")
    def sources_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsSources"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsSources"]]], jsii.get(self, "sourcesInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__235f9d0eb2b928ccb04a28e5873f2be0c7684dcc2bf3e6cb326e6e51dcced11b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="meta")
    def meta(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "meta"))

    @meta.setter
    def meta(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2737cd97fdd7cb11794053c87d75283e3c6e19bfd2e5eed4f091e19e6c5aab43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "meta", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43d2e14659a58fd49250a3d9b1bf03b24e31482b9e8c4169ab6862df588977a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dd54053d6c349b7c8d0db6c4284f415c9ee5164d9433792f81a70743c142fac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partition")
    def partition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partition"))

    @partition.setter
    def partition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9eb348f44fbd80c100e35f8cfc581f4d34d8505eb2d346a89b19cc7bc1ff9bdc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partition", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsConfig",
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
        "jwt": "jwt",
        "meta": "meta",
        "namespace": "namespace",
        "partition": "partition",
        "sources": "sources",
    },
)
class ConfigEntryServiceIntentionsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        jwt: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsJwt", typing.Dict[builtins.str, typing.Any]]]]] = None,
        meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        sources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsSources", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Specifies a name of the destination service for all intentions defined in the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#name ConfigEntryServiceIntentions#name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#id ConfigEntryServiceIntentions#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwt: jwt block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#jwt ConfigEntryServiceIntentions#jwt}
        :param meta: Specifies key-value pairs to add to the KV store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#meta ConfigEntryServiceIntentions#meta}
        :param namespace: Specifies the namespace to apply the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#namespace ConfigEntryServiceIntentions#namespace}
        :param partition: Specifies the admin partition to apply the configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#partition ConfigEntryServiceIntentions#partition}
        :param sources: sources block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#sources ConfigEntryServiceIntentions#sources}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d8efc5f37837cdd93c1b8c2a4c4f215b2690d40a6043f34002f5ed508afc3ea)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument jwt", value=jwt, expected_type=type_hints["jwt"])
            check_type(argname="argument meta", value=meta, expected_type=type_hints["meta"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument sources", value=sources, expected_type=type_hints["sources"])
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
        if jwt is not None:
            self._values["jwt"] = jwt
        if meta is not None:
            self._values["meta"] = meta
        if namespace is not None:
            self._values["namespace"] = namespace
        if partition is not None:
            self._values["partition"] = partition
        if sources is not None:
            self._values["sources"] = sources

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
        '''Specifies a name of the destination service for all intentions defined in the configuration entry.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#name ConfigEntryServiceIntentions#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#id ConfigEntryServiceIntentions#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsJwt"]]]:
        '''jwt block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#jwt ConfigEntryServiceIntentions#jwt}
        '''
        result = self._values.get("jwt")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsJwt"]]], result)

    @builtins.property
    def meta(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Specifies key-value pairs to add to the KV store.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#meta ConfigEntryServiceIntentions#meta}
        '''
        result = self._values.get("meta")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Specifies the namespace to apply the configuration entry.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#namespace ConfigEntryServiceIntentions#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''Specifies the admin partition to apply the configuration entry.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#partition ConfigEntryServiceIntentions#partition}
        '''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sources(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsSources"]]]:
        '''sources block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#sources ConfigEntryServiceIntentions#sources}
        '''
        result = self._values.get("sources")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsSources"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceIntentionsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsJwt",
    jsii_struct_bases=[],
    name_mapping={"providers": "providers"},
)
class ConfigEntryServiceIntentionsJwt:
    def __init__(
        self,
        *,
        providers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsJwtProviders", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param providers: providers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#providers ConfigEntryServiceIntentions#providers}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63c49b5b5141545e423667c657abac283e03161606ae81e1bb3ff58bb2ef9f86)
            check_type(argname="argument providers", value=providers, expected_type=type_hints["providers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if providers is not None:
            self._values["providers"] = providers

    @builtins.property
    def providers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsJwtProviders"]]]:
        '''providers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#providers ConfigEntryServiceIntentions#providers}
        '''
        result = self._values.get("providers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsJwtProviders"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceIntentionsJwt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceIntentionsJwtList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsJwtList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8f060ed324d88f23c7ca5bd0c0c4cfa6cd0a567895340400a31a31611039b24b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceIntentionsJwtOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__135f7dde4a3f5674a7bdae345c3a00ab42cc7c17ac7968d7490f20fb5d9d3236)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceIntentionsJwtOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59de32e022d01c8eacb8c64cb5ea029160e3330cc3a2f7140b0b72d05ccb28d7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__afee55e001489370507d6dea980e6a61444112139bb08a49827a774646afbd83)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b211dded1be554c3e21c92e1002dde4569a1195c98fe35bb8eb4efdab4b3c09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsJwt]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsJwt]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsJwt]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d338cd0edcd5e5609f16d1360c51c526731e634b915af627807c6abd7da845b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceIntentionsJwtOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsJwtOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a6677daa720ecfb26056df0f12d34a9b79b8dd0b69426c331b1ec3bdc5aa27e6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putProviders")
    def put_providers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsJwtProviders", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37e89cc395068ece3c171d6d3d5a4b807761004e882ea107ce29d144dd286906)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putProviders", [value]))

    @jsii.member(jsii_name="resetProviders")
    def reset_providers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProviders", []))

    @builtins.property
    @jsii.member(jsii_name="providers")
    def providers(self) -> "ConfigEntryServiceIntentionsJwtProvidersList":
        return typing.cast("ConfigEntryServiceIntentionsJwtProvidersList", jsii.get(self, "providers"))

    @builtins.property
    @jsii.member(jsii_name="providersInput")
    def providers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsJwtProviders"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsJwtProviders"]]], jsii.get(self, "providersInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsJwt]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsJwt]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsJwt]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca65bedc26cb986208013f962cae893a73df6b7fa89403aeea61d33360dea700)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsJwtProviders",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "verify_claims": "verifyClaims"},
)
class ConfigEntryServiceIntentionsJwtProviders:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        verify_claims: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsJwtProvidersVerifyClaims", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param name: Specifies the name of a JWT provider defined in the Name field of the jwt-provider configuration entry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#name ConfigEntryServiceIntentions#name}
        :param verify_claims: verify_claims block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#verify_claims ConfigEntryServiceIntentions#verify_claims}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51864cc551750cf4c05c575388bb618e65d9b1703b815e9fd0d06753587b64a3)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument verify_claims", value=verify_claims, expected_type=type_hints["verify_claims"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if verify_claims is not None:
            self._values["verify_claims"] = verify_claims

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of a JWT provider defined in the Name field of the jwt-provider configuration entry.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#name ConfigEntryServiceIntentions#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def verify_claims(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsJwtProvidersVerifyClaims"]]]:
        '''verify_claims block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#verify_claims ConfigEntryServiceIntentions#verify_claims}
        '''
        result = self._values.get("verify_claims")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsJwtProvidersVerifyClaims"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceIntentionsJwtProviders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceIntentionsJwtProvidersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsJwtProvidersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__18632d1457272dc0ede5e7ad0cfb8aa3002242db6d764db2aee9d3cc2c464525)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceIntentionsJwtProvidersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e830b0c47d0d2c65dde11b0265a73a4307620026c81c0da8b672705889d5bee4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceIntentionsJwtProvidersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b483d4731d9a2c25640f18e9637ca203e540a2b238e9e56f75db8d818410fffb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f90b7ee9f2406d619864a4a73647363493e337209fdb3bd08bd106c4b7192dd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__86bdb8b18dcaf25ea4c27b84d44c64d66a28b700648858b421fb93455300aa75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsJwtProviders]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsJwtProviders]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsJwtProviders]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a0429264ccc6ece5de2ad6e4391ca107717bd120222a6877f449775f411a473)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceIntentionsJwtProvidersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsJwtProvidersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__52f1b2ac617d01c29da7937e4df9c3088844b56a08735ca626a9b55b75c7ad94)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putVerifyClaims")
    def put_verify_claims(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsJwtProvidersVerifyClaims", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f077b63c76d5d1cd2767446006c30cb4c980714a01ec1ac69124fab50222abaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVerifyClaims", [value]))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetVerifyClaims")
    def reset_verify_claims(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerifyClaims", []))

    @builtins.property
    @jsii.member(jsii_name="verifyClaims")
    def verify_claims(
        self,
    ) -> "ConfigEntryServiceIntentionsJwtProvidersVerifyClaimsList":
        return typing.cast("ConfigEntryServiceIntentionsJwtProvidersVerifyClaimsList", jsii.get(self, "verifyClaims"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="verifyClaimsInput")
    def verify_claims_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsJwtProvidersVerifyClaims"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsJwtProvidersVerifyClaims"]]], jsii.get(self, "verifyClaimsInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30dc5ba22bbaa8aad20ebe815b1a441874552bd74594091e15c1399d9bcacab3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsJwtProviders]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsJwtProviders]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsJwtProviders]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7820d11aeeab30ae52a6411cc7c965deaf0ffe3908043edc711ec93218998b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsJwtProvidersVerifyClaims",
    jsii_struct_bases=[],
    name_mapping={"path": "path", "value": "value"},
)
class ConfigEntryServiceIntentionsJwtProvidersVerifyClaims:
    def __init__(
        self,
        *,
        path: typing.Optional[typing.Sequence[builtins.str]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param path: Specifies the path to the claim in the JSON web token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#path ConfigEntryServiceIntentions#path}
        :param value: Specifies the value to match on when verifying the the claim designated in path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#value ConfigEntryServiceIntentions#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8be826ede4b4a87021d2dd22d336e01121574da015126e009269e25ee530ed9d)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if path is not None:
            self._values["path"] = path
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def path(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the path to the claim in the JSON web token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#path ConfigEntryServiceIntentions#path}
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Specifies the value to match on when verifying the the claim designated in path.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#value ConfigEntryServiceIntentions#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceIntentionsJwtProvidersVerifyClaims(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceIntentionsJwtProvidersVerifyClaimsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsJwtProvidersVerifyClaimsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e0456ddfe9f0af4167ea0f53e084efb27325a3a0c5cd83edf16531553ef68a32)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceIntentionsJwtProvidersVerifyClaimsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07a31b96b113050dc55f8ba23a629e4d0ea89b46221d9588f80a388b5d4964b7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceIntentionsJwtProvidersVerifyClaimsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__844c9a5f4c6bc8755111d0e7df3779de96a20837691d871307d6563189045da9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__58dfd05d4135a16822d35e0e694135d21534fb21b8c787228928a0af1e411a81)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4f05b5c82765623f19f33f43bb8a30225ebc35645d74aa586ac7a15b0a5f3701)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsJwtProvidersVerifyClaims]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsJwtProvidersVerifyClaims]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsJwtProvidersVerifyClaims]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82d3a01bbc339cc671a5b2c8c2fa0f8b1c2f22fc874636566a49bb52cbbcaa4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceIntentionsJwtProvidersVerifyClaimsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsJwtProvidersVerifyClaimsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__12939c8fd1ac311814d0fe626294a8f1dcebaab5e1916216b185e78b8a3995d6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "path"))

    @path.setter
    def path(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4180dad3714cf1db4b2a8168e6d4395920030c24cfec73fe8a576a8343eecd62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23cd587a0b6ef4b178d752cb3b523a96c9d9b3d67d8b40069b217e9b9f422336)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsJwtProvidersVerifyClaims]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsJwtProvidersVerifyClaims]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsJwtProvidersVerifyClaims]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c197f1235bd84f7fdb864a1a87c30d1c1196db2d4b4dae9466527b21996285ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsSources",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "description": "description",
        "name": "name",
        "namespace": "namespace",
        "partition": "partition",
        "peer": "peer",
        "permissions": "permissions",
        "precedence": "precedence",
        "sameness_group": "samenessGroup",
        "type": "type",
    },
)
class ConfigEntryServiceIntentionsSources:
    def __init__(
        self,
        *,
        action: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        peer: typing.Optional[builtins.str] = None,
        permissions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsSourcesPermissions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        precedence: typing.Optional[jsii.Number] = None,
        sameness_group: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action: Specifies the action to take when the source sends traffic to the destination service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#action ConfigEntryServiceIntentions#action}
        :param description: Specifies a description of the intention. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#description ConfigEntryServiceIntentions#description}
        :param name: Specifies the name of the source that the intention allows or denies traffic from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#name ConfigEntryServiceIntentions#name}
        :param namespace: Specifies the traffic source namespace that the intention allows or denies traffic from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#namespace ConfigEntryServiceIntentions#namespace}
        :param partition: Specifies the name of an admin partition that the intention allows or denies traffic from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#partition ConfigEntryServiceIntentions#partition}
        :param peer: Specifies the name of a peered Consul cluster that the intention allows or denies traffic from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#peer ConfigEntryServiceIntentions#peer}
        :param permissions: permissions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#permissions ConfigEntryServiceIntentions#permissions}
        :param precedence: The Precedence field contains a read-only integer. Consul generates the value based on name configurations for the source and destination services. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#precedence ConfigEntryServiceIntentions#precedence}
        :param sameness_group: Specifies the name of a sameness group that the intention allows or denies traffic from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#sameness_group ConfigEntryServiceIntentions#sameness_group}
        :param type: Specifies the type of destination service that the configuration entry applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#type ConfigEntryServiceIntentions#type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__149af52b2a74ffb120b79301e463b9bdee277afc9d4d5141e32d26e8c2f87475)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument peer", value=peer, expected_type=type_hints["peer"])
            check_type(argname="argument permissions", value=permissions, expected_type=type_hints["permissions"])
            check_type(argname="argument precedence", value=precedence, expected_type=type_hints["precedence"])
            check_type(argname="argument sameness_group", value=sameness_group, expected_type=type_hints["sameness_group"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if action is not None:
            self._values["action"] = action
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if namespace is not None:
            self._values["namespace"] = namespace
        if partition is not None:
            self._values["partition"] = partition
        if peer is not None:
            self._values["peer"] = peer
        if permissions is not None:
            self._values["permissions"] = permissions
        if precedence is not None:
            self._values["precedence"] = precedence
        if sameness_group is not None:
            self._values["sameness_group"] = sameness_group
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def action(self) -> typing.Optional[builtins.str]:
        '''Specifies the action to take when the source sends traffic to the destination service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#action ConfigEntryServiceIntentions#action}
        '''
        result = self._values.get("action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Specifies a description of the intention.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#description ConfigEntryServiceIntentions#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of the source that the intention allows or denies traffic from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#name ConfigEntryServiceIntentions#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Specifies the traffic source namespace that the intention allows or denies traffic from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#namespace ConfigEntryServiceIntentions#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of an admin partition that the intention allows or denies traffic from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#partition ConfigEntryServiceIntentions#partition}
        '''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def peer(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of a peered Consul cluster that the intention allows or denies traffic from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#peer ConfigEntryServiceIntentions#peer}
        '''
        result = self._values.get("peer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsSourcesPermissions"]]]:
        '''permissions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#permissions ConfigEntryServiceIntentions#permissions}
        '''
        result = self._values.get("permissions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsSourcesPermissions"]]], result)

    @builtins.property
    def precedence(self) -> typing.Optional[jsii.Number]:
        '''The Precedence field contains a read-only integer.

        Consul generates the value based on name configurations for the source and destination services.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#precedence ConfigEntryServiceIntentions#precedence}
        '''
        result = self._values.get("precedence")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def sameness_group(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of a sameness group that the intention allows or denies traffic from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#sameness_group ConfigEntryServiceIntentions#sameness_group}
        '''
        result = self._values.get("sameness_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Specifies the type of destination service that the configuration entry applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#type ConfigEntryServiceIntentions#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceIntentionsSources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceIntentionsSourcesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsSourcesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c92177c262500c2c502aec5f99de37e1b97d737f49cf08bb687db6f1855be60f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceIntentionsSourcesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fda92cb8d3f4bb37ed36ec4e425b0db3b92f093117d24b17d262b9dd8d73a30a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceIntentionsSourcesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__821f868750b598490540278e7686c0848c78f5c57e4daf455afc543402a07332)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1494d816c499f51a661e2b2185de54529f10b8c702e5fb922ff66d1979b375d6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__167c9f7481a779051b4cf6d9d5dadb303c7fa0e600e0839adcbea1991b53bd01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSources]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSources]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSources]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ddff198bbe1af420769cf355f3a1341b99648ab7ae574069f8ae3b5f843c252)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceIntentionsSourcesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsSourcesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7ad681701b262145d167060b6d072ef6b2d6b22c836270c6d7b3a4364e16ceda)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putPermissions")
    def put_permissions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsSourcesPermissions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__051ce32296d494bcf33371b3749d54cf41a911e7fbabeb6ad96d462277b4b275)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPermissions", [value]))

    @jsii.member(jsii_name="resetAction")
    def reset_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAction", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPartition")
    def reset_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartition", []))

    @jsii.member(jsii_name="resetPeer")
    def reset_peer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeer", []))

    @jsii.member(jsii_name="resetPermissions")
    def reset_permissions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermissions", []))

    @jsii.member(jsii_name="resetPrecedence")
    def reset_precedence(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrecedence", []))

    @jsii.member(jsii_name="resetSamenessGroup")
    def reset_sameness_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSamenessGroup", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="permissions")
    def permissions(self) -> "ConfigEntryServiceIntentionsSourcesPermissionsList":
        return typing.cast("ConfigEntryServiceIntentionsSourcesPermissionsList", jsii.get(self, "permissions"))

    @builtins.property
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

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
    @jsii.member(jsii_name="peerInput")
    def peer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "peerInput"))

    @builtins.property
    @jsii.member(jsii_name="permissionsInput")
    def permissions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsSourcesPermissions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsSourcesPermissions"]]], jsii.get(self, "permissionsInput"))

    @builtins.property
    @jsii.member(jsii_name="precedenceInput")
    def precedence_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "precedenceInput"))

    @builtins.property
    @jsii.member(jsii_name="samenessGroupInput")
    def sameness_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "samenessGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccb4858e7eb4e7290e07c5dd89ff3395bc57495c0b0d056b3d915432bb75a4e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "action", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1329243e2b10b3e1cdc41a0b89c2915e4b4853cff5d37cb65afc58b79f81c050)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63504ed0aa3a04ddb52003e95f9879d3a1b07c6686f6da640b4eff9130351b1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__959c52dc05591bbfe88fa7d0c505123eff532586eef2b658c1f447ec59eada33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partition")
    def partition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partition"))

    @partition.setter
    def partition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01a60f9157674b78540c0742d18ec9be7149cf7b91605a824b5150dfb6f5cebe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="peer")
    def peer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "peer"))

    @peer.setter
    def peer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa2bae767a429f4b188dda5a2a1d94e33f3eab8a8a87258bd75e7641e9fcdede)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "peer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="precedence")
    def precedence(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "precedence"))

    @precedence.setter
    def precedence(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be44bf654c23a78414f408e5d96763530d83c18895771c8be596ca548782578f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "precedence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="samenessGroup")
    def sameness_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "samenessGroup"))

    @sameness_group.setter
    def sameness_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2aeaa751983012ae1142ae769393f9761b6051be64af0608ee546cf2bb16b037)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "samenessGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33b10c4cfe91b8e0f54e270daf716f7344d55a104110b4389b942a13d2e3a63a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSources]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSources]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSources]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__460d67c2619f86ccc3c6b46e7464c06ba9f41504f271f178f59a7c97b0c3d57c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsSourcesPermissions",
    jsii_struct_bases=[],
    name_mapping={"action": "action", "http": "http"},
)
class ConfigEntryServiceIntentionsSourcesPermissions:
    def __init__(
        self,
        *,
        action: builtins.str,
        http: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsSourcesPermissionsHttp", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param action: Specifies the action to take when the source sends traffic to the destination service. The value is either allow or deny. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#action ConfigEntryServiceIntentions#action}
        :param http: http block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#http ConfigEntryServiceIntentions#http}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__864be18fd12fc437d110aaa3f6efdda88e8bfa23c2cac80c9294a5966c607fff)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument http", value=http, expected_type=type_hints["http"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action": action,
            "http": http,
        }

    @builtins.property
    def action(self) -> builtins.str:
        '''Specifies the action to take when the source sends traffic to the destination service.

        The value is either allow or deny.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#action ConfigEntryServiceIntentions#action}
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def http(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsSourcesPermissionsHttp"]]:
        '''http block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#http ConfigEntryServiceIntentions#http}
        '''
        result = self._values.get("http")
        assert result is not None, "Required property 'http' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsSourcesPermissionsHttp"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceIntentionsSourcesPermissions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsSourcesPermissionsHttp",
    jsii_struct_bases=[],
    name_mapping={
        "headers": "headers",
        "methods": "methods",
        "path_exact": "pathExact",
        "path_prefix": "pathPrefix",
        "path_regex": "pathRegex",
    },
)
class ConfigEntryServiceIntentionsSourcesPermissionsHttp:
    def __init__(
        self,
        *,
        headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders", typing.Dict[builtins.str, typing.Any]]]]] = None,
        methods: typing.Optional[typing.Sequence[builtins.str]] = None,
        path_exact: typing.Optional[builtins.str] = None,
        path_prefix: typing.Optional[builtins.str] = None,
        path_regex: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param headers: headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#headers ConfigEntryServiceIntentions#headers}
        :param methods: Specifies a list of HTTP methods. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#methods ConfigEntryServiceIntentions#methods}
        :param path_exact: Specifies an exact path to match on the HTTP request path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#path_exact ConfigEntryServiceIntentions#path_exact}
        :param path_prefix: Specifies a path prefix to match on the HTTP request path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#path_prefix ConfigEntryServiceIntentions#path_prefix}
        :param path_regex: Defines a regular expression to match on the HTTP request path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#path_regex ConfigEntryServiceIntentions#path_regex}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60e848cf6c253263956414a215580514727cced528a9a0aeb565740b0b62a16e)
            check_type(argname="argument headers", value=headers, expected_type=type_hints["headers"])
            check_type(argname="argument methods", value=methods, expected_type=type_hints["methods"])
            check_type(argname="argument path_exact", value=path_exact, expected_type=type_hints["path_exact"])
            check_type(argname="argument path_prefix", value=path_prefix, expected_type=type_hints["path_prefix"])
            check_type(argname="argument path_regex", value=path_regex, expected_type=type_hints["path_regex"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if headers is not None:
            self._values["headers"] = headers
        if methods is not None:
            self._values["methods"] = methods
        if path_exact is not None:
            self._values["path_exact"] = path_exact
        if path_prefix is not None:
            self._values["path_prefix"] = path_prefix
        if path_regex is not None:
            self._values["path_regex"] = path_regex

    @builtins.property
    def headers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders"]]]:
        '''headers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#headers ConfigEntryServiceIntentions#headers}
        '''
        result = self._values.get("headers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders"]]], result)

    @builtins.property
    def methods(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies a list of HTTP methods.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#methods ConfigEntryServiceIntentions#methods}
        '''
        result = self._values.get("methods")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def path_exact(self) -> typing.Optional[builtins.str]:
        '''Specifies an exact path to match on the HTTP request path.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#path_exact ConfigEntryServiceIntentions#path_exact}
        '''
        result = self._values.get("path_exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path_prefix(self) -> typing.Optional[builtins.str]:
        '''Specifies a path prefix to match on the HTTP request path.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#path_prefix ConfigEntryServiceIntentions#path_prefix}
        '''
        result = self._values.get("path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path_regex(self) -> typing.Optional[builtins.str]:
        '''Defines a regular expression to match on the HTTP request path.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#path_regex ConfigEntryServiceIntentions#path_regex}
        '''
        result = self._values.get("path_regex")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceIntentionsSourcesPermissionsHttp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "exact": "exact",
        "invert": "invert",
        "prefix": "prefix",
        "present": "present",
        "regex": "regex",
        "suffix": "suffix",
    },
)
class ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders:
    def __init__(
        self,
        *,
        name: builtins.str,
        exact: typing.Optional[builtins.str] = None,
        invert: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        prefix: typing.Optional[builtins.str] = None,
        present: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        regex: typing.Optional[builtins.str] = None,
        suffix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Specifies the name of the header to match. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#name ConfigEntryServiceIntentions#name}
        :param exact: Specifies a value for the header key set in the Name field. If the request header value matches the Exact value, Consul applies the permission. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#exact ConfigEntryServiceIntentions#exact}
        :param invert: Inverts the matching logic configured in the Header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#invert ConfigEntryServiceIntentions#invert}
        :param prefix: Specifies a prefix value for the header key set in the Name field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#prefix ConfigEntryServiceIntentions#prefix}
        :param present: Enables a match if the header configured in the Name field appears in the request. Consul matches on any value as long as the header key appears in the request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#present ConfigEntryServiceIntentions#present}
        :param regex: Specifies a regular expression pattern as the value for the header key set in the Name field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#regex ConfigEntryServiceIntentions#regex}
        :param suffix: Specifies a suffix value for the header key set in the Name field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#suffix ConfigEntryServiceIntentions#suffix}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96b92620236b3e0eb7ba182f564382e45085cc56d9cae9fb3b394e5fe5a82987)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument exact", value=exact, expected_type=type_hints["exact"])
            check_type(argname="argument invert", value=invert, expected_type=type_hints["invert"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument present", value=present, expected_type=type_hints["present"])
            check_type(argname="argument regex", value=regex, expected_type=type_hints["regex"])
            check_type(argname="argument suffix", value=suffix, expected_type=type_hints["suffix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if exact is not None:
            self._values["exact"] = exact
        if invert is not None:
            self._values["invert"] = invert
        if prefix is not None:
            self._values["prefix"] = prefix
        if present is not None:
            self._values["present"] = present
        if regex is not None:
            self._values["regex"] = regex
        if suffix is not None:
            self._values["suffix"] = suffix

    @builtins.property
    def name(self) -> builtins.str:
        '''Specifies the name of the header to match.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#name ConfigEntryServiceIntentions#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def exact(self) -> typing.Optional[builtins.str]:
        '''Specifies a value for the header key set in the Name field.

        If the request header value matches the Exact value, Consul applies the permission.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#exact ConfigEntryServiceIntentions#exact}
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invert(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Inverts the matching logic configured in the Header.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#invert ConfigEntryServiceIntentions#invert}
        '''
        result = self._values.get("invert")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Specifies a prefix value for the header key set in the Name field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#prefix ConfigEntryServiceIntentions#prefix}
        '''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def present(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables a match if the header configured in the Name field appears in the request.

        Consul matches on any value as long as the header key appears in the request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#present ConfigEntryServiceIntentions#present}
        '''
        result = self._values.get("present")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def regex(self) -> typing.Optional[builtins.str]:
        '''Specifies a regular expression pattern as the value for the header key set in the Name field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#regex ConfigEntryServiceIntentions#regex}
        '''
        result = self._values.get("regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suffix(self) -> typing.Optional[builtins.str]:
        '''Specifies a suffix value for the header key set in the Name field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/config_entry_service_intentions#suffix ConfigEntryServiceIntentions#suffix}
        '''
        result = self._values.get("suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigEntryServiceIntentionsSourcesPermissionsHttpHeadersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsSourcesPermissionsHttpHeadersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__32117f74bd2261e5b6096e5a84612de10867a9be18bf42ffda4aa4128ecf8a53)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceIntentionsSourcesPermissionsHttpHeadersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b885d1b99a564f9647f201af14054fc5d0171912fbe2081e814f745343692a1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceIntentionsSourcesPermissionsHttpHeadersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d5a89ad2b195087c19149dbaf16156cdc1dc38b1034a663e61ca66564cd39d7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf304813077e2302ff7d95df717845f6e9baa411fa81f4ae7642a1b6830357cd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f395c478075421e351108f291722a6bbc65c0fa29df73d015793252fedb2ea64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7297152bc3b06bf29023cbbd372882da569a704f003a9e9c37adae830191605d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceIntentionsSourcesPermissionsHttpHeadersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsSourcesPermissionsHttpHeadersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f84db72b215e59f592b2b8b3d7342d1b5545f15c92446b3103ec5211e05795a6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bdd46e5f00ca941ec6ef945a67435e309116a0cdd86b725d7097ed57a324cfd0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf6d42b1becb1c556e9238b21321c8913086011a152a815bd76aefccde46bb3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "invert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4f6a7872c51ed8a81bd001086710881b55727045beebd8f51eb58ec71d8f268)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63b2ce9d88d6be3755db76f4a9aa92cc19a7b2db9f2e1e4e260b9be3422a4460)
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
            type_hints = typing.get_type_hints(_typecheckingstub__38723c0c121b84438c3cc01c09470b2840f67f386e6f0571bf383c55b6902c17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "present", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regex")
    def regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regex"))

    @regex.setter
    def regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bb034c4e3ebcc7adcd3f8a221bcd87609e28e3da03694678f0d54aa55b19d49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="suffix")
    def suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "suffix"))

    @suffix.setter
    def suffix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__070d135f3d128b75a37ef60f2b7569449eb4a49b4323d3f04f6f3c250c749b05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "suffix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d063ab4c3a44b02b74901982eddd51af3817c506175524c80e9d0ccbb6e9becb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceIntentionsSourcesPermissionsHttpList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsSourcesPermissionsHttpList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4b6e2e4384048ca56e3eff86865899587b3485cc1b409c6bbaa26470f6a6bef6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceIntentionsSourcesPermissionsHttpOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecd0ed647334719e6dc83b10cc7fe0e8db1eeaf8614798c3b8694173ae275238)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceIntentionsSourcesPermissionsHttpOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0631c1bf087b2eb57521f39f0cc34a7bb3dc2710149a98406868baec45e2ccb3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bac7c3c6b25ec31145127eae6b5fbf109570cca1163c69bf97810ee24f6ca4b6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__733851ced64ebb772d9e5fa64d01c9b4cc294afedeff603d6056f81078dde9fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissionsHttp]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissionsHttp]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissionsHttp]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b4f355f432ce0fe1b9a071911f3be866fecc9c87e4ce897691ed38082385560)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceIntentionsSourcesPermissionsHttpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsSourcesPermissionsHttpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa59b206b55e769d5329c465fd79b25199937561ff8dd851b38450fb028e13c3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putHeaders")
    def put_headers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52a03fd0b96de60491cc894ccff420df1cb66f4905c82277e334d3aba620b38a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putHeaders", [value]))

    @jsii.member(jsii_name="resetHeaders")
    def reset_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaders", []))

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

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> ConfigEntryServiceIntentionsSourcesPermissionsHttpHeadersList:
        return typing.cast(ConfigEntryServiceIntentionsSourcesPermissionsHttpHeadersList, jsii.get(self, "headers"))

    @builtins.property
    @jsii.member(jsii_name="headersInput")
    def headers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders]]], jsii.get(self, "headersInput"))

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
    @jsii.member(jsii_name="methods")
    def methods(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "methods"))

    @methods.setter
    def methods(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f893c11ebba3196ca9026ee3ada7902ef82c828bc18f8ec943db300fbc86ff2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "methods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathExact")
    def path_exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathExact"))

    @path_exact.setter
    def path_exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff68c04c96235f6f35eb2e1778593e179abced2660e61b116b58399e78795c06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathExact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathPrefix")
    def path_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathPrefix"))

    @path_prefix.setter
    def path_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43242902566c737268fe77bf6087e36ea79ca6d4cf387ed8b1b3e30919a225f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathPrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathRegex")
    def path_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathRegex"))

    @path_regex.setter
    def path_regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6455f618567a3d87d1fb3bde7a63462dbd95bbfcf18a549c7572127c7525505)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSourcesPermissionsHttp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSourcesPermissionsHttp]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSourcesPermissionsHttp]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d7b14d9e12f2cd2159b4fdc34501bd0f79404536fa402b24d5aefcc48c97283)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceIntentionsSourcesPermissionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsSourcesPermissionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__399dd2bb7a8d2ed54ee8e3f71932af70030b36ecd1e699ad76716990b5172ed0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ConfigEntryServiceIntentionsSourcesPermissionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9b727286e7f5b43b0b5da5eb4df406d918a66f2aa77377d203cd4c736de59a7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ConfigEntryServiceIntentionsSourcesPermissionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5ab7e2b31122ef47ed6a129742c74fb250494e8fa1e84c7cb3be2539738572e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec1fcd958734ebccab7fed056b4a2d7820842d93758b1a8720fd0fe94cc81f64)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3e5035dad068cfe5164714464d0c1d2da12d69015e2989a3563d8287d89be475)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2683acc68dfb8becc6e81a48e45b4b9bfdb911831ff2fb380b43adf7a986f285)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ConfigEntryServiceIntentionsSourcesPermissionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.configEntryServiceIntentions.ConfigEntryServiceIntentionsSourcesPermissionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7773a0d0e40c48378583b2b1808a2e8f07360dd59deae769cd9cbcb1fea7b516)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putHttp")
    def put_http(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsSourcesPermissionsHttp, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ab0fc5352f24689dab6574608a98129b05c72c19dcbca657e669ee644c8e703)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putHttp", [value]))

    @builtins.property
    @jsii.member(jsii_name="http")
    def http(self) -> ConfigEntryServiceIntentionsSourcesPermissionsHttpList:
        return typing.cast(ConfigEntryServiceIntentionsSourcesPermissionsHttpList, jsii.get(self, "http"))

    @builtins.property
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property
    @jsii.member(jsii_name="httpInput")
    def http_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissionsHttp]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissionsHttp]]], jsii.get(self, "httpInput"))

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6afaa2eede80137562e8249b4a1cd17bcbd3a013d51288e655b244e9a81fdb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "action", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSourcesPermissions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSourcesPermissions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSourcesPermissions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85aade8192059941a69062f9f77d91440134890be1f816f740d7cffb4c1e7431)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ConfigEntryServiceIntentions",
    "ConfigEntryServiceIntentionsConfig",
    "ConfigEntryServiceIntentionsJwt",
    "ConfigEntryServiceIntentionsJwtList",
    "ConfigEntryServiceIntentionsJwtOutputReference",
    "ConfigEntryServiceIntentionsJwtProviders",
    "ConfigEntryServiceIntentionsJwtProvidersList",
    "ConfigEntryServiceIntentionsJwtProvidersOutputReference",
    "ConfigEntryServiceIntentionsJwtProvidersVerifyClaims",
    "ConfigEntryServiceIntentionsJwtProvidersVerifyClaimsList",
    "ConfigEntryServiceIntentionsJwtProvidersVerifyClaimsOutputReference",
    "ConfigEntryServiceIntentionsSources",
    "ConfigEntryServiceIntentionsSourcesList",
    "ConfigEntryServiceIntentionsSourcesOutputReference",
    "ConfigEntryServiceIntentionsSourcesPermissions",
    "ConfigEntryServiceIntentionsSourcesPermissionsHttp",
    "ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders",
    "ConfigEntryServiceIntentionsSourcesPermissionsHttpHeadersList",
    "ConfigEntryServiceIntentionsSourcesPermissionsHttpHeadersOutputReference",
    "ConfigEntryServiceIntentionsSourcesPermissionsHttpList",
    "ConfigEntryServiceIntentionsSourcesPermissionsHttpOutputReference",
    "ConfigEntryServiceIntentionsSourcesPermissionsList",
    "ConfigEntryServiceIntentionsSourcesPermissionsOutputReference",
]

publication.publish()

def _typecheckingstub__77bc94afe70e67c56279ee8192cbf3d56ae765117ea7b2e7fb920901ff080b67(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    jwt: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsJwt, typing.Dict[builtins.str, typing.Any]]]]] = None,
    meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    sources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsSources, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__83e2263425aeab1f72e7445a230df4f6e121782c8f11b3121ce8f21ea89c7900(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2c268ebe2fb2761293a2fd032b921fb397e056757e0160051493426f7a362e6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsJwt, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a46c9b9a7af02f787e087c47bbc6446d1f303c94f63858fbc540b29868d9aba(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsSources, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__235f9d0eb2b928ccb04a28e5873f2be0c7684dcc2bf3e6cb326e6e51dcced11b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2737cd97fdd7cb11794053c87d75283e3c6e19bfd2e5eed4f091e19e6c5aab43(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43d2e14659a58fd49250a3d9b1bf03b24e31482b9e8c4169ab6862df588977a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dd54053d6c349b7c8d0db6c4284f415c9ee5164d9433792f81a70743c142fac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9eb348f44fbd80c100e35f8cfc581f4d34d8505eb2d346a89b19cc7bc1ff9bdc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d8efc5f37837cdd93c1b8c2a4c4f215b2690d40a6043f34002f5ed508afc3ea(
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
    jwt: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsJwt, typing.Dict[builtins.str, typing.Any]]]]] = None,
    meta: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    sources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsSources, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63c49b5b5141545e423667c657abac283e03161606ae81e1bb3ff58bb2ef9f86(
    *,
    providers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsJwtProviders, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f060ed324d88f23c7ca5bd0c0c4cfa6cd0a567895340400a31a31611039b24b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__135f7dde4a3f5674a7bdae345c3a00ab42cc7c17ac7968d7490f20fb5d9d3236(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59de32e022d01c8eacb8c64cb5ea029160e3330cc3a2f7140b0b72d05ccb28d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afee55e001489370507d6dea980e6a61444112139bb08a49827a774646afbd83(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b211dded1be554c3e21c92e1002dde4569a1195c98fe35bb8eb4efdab4b3c09(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d338cd0edcd5e5609f16d1360c51c526731e634b915af627807c6abd7da845b0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsJwt]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6677daa720ecfb26056df0f12d34a9b79b8dd0b69426c331b1ec3bdc5aa27e6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37e89cc395068ece3c171d6d3d5a4b807761004e882ea107ce29d144dd286906(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsJwtProviders, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca65bedc26cb986208013f962cae893a73df6b7fa89403aeea61d33360dea700(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsJwt]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51864cc551750cf4c05c575388bb618e65d9b1703b815e9fd0d06753587b64a3(
    *,
    name: typing.Optional[builtins.str] = None,
    verify_claims: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsJwtProvidersVerifyClaims, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18632d1457272dc0ede5e7ad0cfb8aa3002242db6d764db2aee9d3cc2c464525(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e830b0c47d0d2c65dde11b0265a73a4307620026c81c0da8b672705889d5bee4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b483d4731d9a2c25640f18e9637ca203e540a2b238e9e56f75db8d818410fffb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f90b7ee9f2406d619864a4a73647363493e337209fdb3bd08bd106c4b7192dd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86bdb8b18dcaf25ea4c27b84d44c64d66a28b700648858b421fb93455300aa75(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a0429264ccc6ece5de2ad6e4391ca107717bd120222a6877f449775f411a473(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsJwtProviders]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52f1b2ac617d01c29da7937e4df9c3088844b56a08735ca626a9b55b75c7ad94(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f077b63c76d5d1cd2767446006c30cb4c980714a01ec1ac69124fab50222abaa(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsJwtProvidersVerifyClaims, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30dc5ba22bbaa8aad20ebe815b1a441874552bd74594091e15c1399d9bcacab3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7820d11aeeab30ae52a6411cc7c965deaf0ffe3908043edc711ec93218998b2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsJwtProviders]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8be826ede4b4a87021d2dd22d336e01121574da015126e009269e25ee530ed9d(
    *,
    path: typing.Optional[typing.Sequence[builtins.str]] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0456ddfe9f0af4167ea0f53e084efb27325a3a0c5cd83edf16531553ef68a32(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07a31b96b113050dc55f8ba23a629e4d0ea89b46221d9588f80a388b5d4964b7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__844c9a5f4c6bc8755111d0e7df3779de96a20837691d871307d6563189045da9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58dfd05d4135a16822d35e0e694135d21534fb21b8c787228928a0af1e411a81(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f05b5c82765623f19f33f43bb8a30225ebc35645d74aa586ac7a15b0a5f3701(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82d3a01bbc339cc671a5b2c8c2fa0f8b1c2f22fc874636566a49bb52cbbcaa4d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsJwtProvidersVerifyClaims]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12939c8fd1ac311814d0fe626294a8f1dcebaab5e1916216b185e78b8a3995d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4180dad3714cf1db4b2a8168e6d4395920030c24cfec73fe8a576a8343eecd62(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23cd587a0b6ef4b178d752cb3b523a96c9d9b3d67d8b40069b217e9b9f422336(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c197f1235bd84f7fdb864a1a87c30d1c1196db2d4b4dae9466527b21996285ca(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsJwtProvidersVerifyClaims]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__149af52b2a74ffb120b79301e463b9bdee277afc9d4d5141e32d26e8c2f87475(
    *,
    action: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    peer: typing.Optional[builtins.str] = None,
    permissions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsSourcesPermissions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    precedence: typing.Optional[jsii.Number] = None,
    sameness_group: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c92177c262500c2c502aec5f99de37e1b97d737f49cf08bb687db6f1855be60f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fda92cb8d3f4bb37ed36ec4e425b0db3b92f093117d24b17d262b9dd8d73a30a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__821f868750b598490540278e7686c0848c78f5c57e4daf455afc543402a07332(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1494d816c499f51a661e2b2185de54529f10b8c702e5fb922ff66d1979b375d6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__167c9f7481a779051b4cf6d9d5dadb303c7fa0e600e0839adcbea1991b53bd01(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ddff198bbe1af420769cf355f3a1341b99648ab7ae574069f8ae3b5f843c252(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSources]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ad681701b262145d167060b6d072ef6b2d6b22c836270c6d7b3a4364e16ceda(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__051ce32296d494bcf33371b3749d54cf41a911e7fbabeb6ad96d462277b4b275(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsSourcesPermissions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccb4858e7eb4e7290e07c5dd89ff3395bc57495c0b0d056b3d915432bb75a4e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1329243e2b10b3e1cdc41a0b89c2915e4b4853cff5d37cb65afc58b79f81c050(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63504ed0aa3a04ddb52003e95f9879d3a1b07c6686f6da640b4eff9130351b1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__959c52dc05591bbfe88fa7d0c505123eff532586eef2b658c1f447ec59eada33(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01a60f9157674b78540c0742d18ec9be7149cf7b91605a824b5150dfb6f5cebe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa2bae767a429f4b188dda5a2a1d94e33f3eab8a8a87258bd75e7641e9fcdede(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be44bf654c23a78414f408e5d96763530d83c18895771c8be596ca548782578f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2aeaa751983012ae1142ae769393f9761b6051be64af0608ee546cf2bb16b037(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33b10c4cfe91b8e0f54e270daf716f7344d55a104110b4389b942a13d2e3a63a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__460d67c2619f86ccc3c6b46e7464c06ba9f41504f271f178f59a7c97b0c3d57c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSources]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__864be18fd12fc437d110aaa3f6efdda88e8bfa23c2cac80c9294a5966c607fff(
    *,
    action: builtins.str,
    http: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsSourcesPermissionsHttp, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60e848cf6c253263956414a215580514727cced528a9a0aeb565740b0b62a16e(
    *,
    headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders, typing.Dict[builtins.str, typing.Any]]]]] = None,
    methods: typing.Optional[typing.Sequence[builtins.str]] = None,
    path_exact: typing.Optional[builtins.str] = None,
    path_prefix: typing.Optional[builtins.str] = None,
    path_regex: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96b92620236b3e0eb7ba182f564382e45085cc56d9cae9fb3b394e5fe5a82987(
    *,
    name: builtins.str,
    exact: typing.Optional[builtins.str] = None,
    invert: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    prefix: typing.Optional[builtins.str] = None,
    present: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    regex: typing.Optional[builtins.str] = None,
    suffix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32117f74bd2261e5b6096e5a84612de10867a9be18bf42ffda4aa4128ecf8a53(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b885d1b99a564f9647f201af14054fc5d0171912fbe2081e814f745343692a1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d5a89ad2b195087c19149dbaf16156cdc1dc38b1034a663e61ca66564cd39d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf304813077e2302ff7d95df717845f6e9baa411fa81f4ae7642a1b6830357cd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f395c478075421e351108f291722a6bbc65c0fa29df73d015793252fedb2ea64(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7297152bc3b06bf29023cbbd372882da569a704f003a9e9c37adae830191605d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f84db72b215e59f592b2b8b3d7342d1b5545f15c92446b3103ec5211e05795a6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdd46e5f00ca941ec6ef945a67435e309116a0cdd86b725d7097ed57a324cfd0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf6d42b1becb1c556e9238b21321c8913086011a152a815bd76aefccde46bb3e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4f6a7872c51ed8a81bd001086710881b55727045beebd8f51eb58ec71d8f268(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63b2ce9d88d6be3755db76f4a9aa92cc19a7b2db9f2e1e4e260b9be3422a4460(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38723c0c121b84438c3cc01c09470b2840f67f386e6f0571bf383c55b6902c17(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bb034c4e3ebcc7adcd3f8a221bcd87609e28e3da03694678f0d54aa55b19d49(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__070d135f3d128b75a37ef60f2b7569449eb4a49b4323d3f04f6f3c250c749b05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d063ab4c3a44b02b74901982eddd51af3817c506175524c80e9d0ccbb6e9becb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b6e2e4384048ca56e3eff86865899587b3485cc1b409c6bbaa26470f6a6bef6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecd0ed647334719e6dc83b10cc7fe0e8db1eeaf8614798c3b8694173ae275238(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0631c1bf087b2eb57521f39f0cc34a7bb3dc2710149a98406868baec45e2ccb3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bac7c3c6b25ec31145127eae6b5fbf109570cca1163c69bf97810ee24f6ca4b6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__733851ced64ebb772d9e5fa64d01c9b4cc294afedeff603d6056f81078dde9fa(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b4f355f432ce0fe1b9a071911f3be866fecc9c87e4ce897691ed38082385560(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissionsHttp]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa59b206b55e769d5329c465fd79b25199937561ff8dd851b38450fb028e13c3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52a03fd0b96de60491cc894ccff420df1cb66f4905c82277e334d3aba620b38a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsSourcesPermissionsHttpHeaders, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f893c11ebba3196ca9026ee3ada7902ef82c828bc18f8ec943db300fbc86ff2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff68c04c96235f6f35eb2e1778593e179abced2660e61b116b58399e78795c06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43242902566c737268fe77bf6087e36ea79ca6d4cf387ed8b1b3e30919a225f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6455f618567a3d87d1fb3bde7a63462dbd95bbfcf18a549c7572127c7525505(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d7b14d9e12f2cd2159b4fdc34501bd0f79404536fa402b24d5aefcc48c97283(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSourcesPermissionsHttp]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__399dd2bb7a8d2ed54ee8e3f71932af70030b36ecd1e699ad76716990b5172ed0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9b727286e7f5b43b0b5da5eb4df406d918a66f2aa77377d203cd4c736de59a7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5ab7e2b31122ef47ed6a129742c74fb250494e8fa1e84c7cb3be2539738572e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec1fcd958734ebccab7fed056b4a2d7820842d93758b1a8720fd0fe94cc81f64(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e5035dad068cfe5164714464d0c1d2da12d69015e2989a3563d8287d89be475(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2683acc68dfb8becc6e81a48e45b4b9bfdb911831ff2fb380b43adf7a986f285(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ConfigEntryServiceIntentionsSourcesPermissions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7773a0d0e40c48378583b2b1808a2e8f07360dd59deae769cd9cbcb1fea7b516(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ab0fc5352f24689dab6574608a98129b05c72c19dcbca657e669ee644c8e703(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ConfigEntryServiceIntentionsSourcesPermissionsHttp, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6afaa2eede80137562e8249b4a1cd17bcbd3a013d51288e655b244e9a81fdb0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85aade8192059941a69062f9f77d91440134890be1f816f740d7cffb4c1e7431(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ConfigEntryServiceIntentionsSourcesPermissions]],
) -> None:
    """Type checking stubs"""
    pass
