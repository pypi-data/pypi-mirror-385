r'''
# `consul_acl_binding_rule`

Refer to the Terraform Registry for docs: [`consul_acl_binding_rule`](https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule).
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


class AclBindingRule(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.aclBindingRule.AclBindingRule",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule consul_acl_binding_rule}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        auth_method: builtins.str,
        bind_name: builtins.str,
        bind_type: builtins.str,
        bind_vars: typing.Optional[typing.Union["AclBindingRuleBindVars", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        selector: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule consul_acl_binding_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param auth_method: The name of the ACL auth method this rule apply. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#auth_method AclBindingRule#auth_method}
        :param bind_name: The name to bind to a token at login-time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#bind_name AclBindingRule#bind_name}
        :param bind_type: Specifies the way the binding rule affects a token created at login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#bind_type AclBindingRule#bind_type}
        :param bind_vars: bind_vars block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#bind_vars AclBindingRule#bind_vars}
        :param description: A free form human readable description of the binding rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#description AclBindingRule#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#id AclBindingRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: The namespace to create the binding rule within. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#namespace AclBindingRule#namespace}
        :param partition: The partition the ACL binding rule is associated with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#partition AclBindingRule#partition}
        :param selector: The expression used to match this rule against valid identities returned from an auth method validation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#selector AclBindingRule#selector}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5ec18a7b93baec752384cbca2d61e2b1059765ef74c3c09c1a58cdee04d6e2e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AclBindingRuleConfig(
            auth_method=auth_method,
            bind_name=bind_name,
            bind_type=bind_type,
            bind_vars=bind_vars,
            description=description,
            id=id,
            namespace=namespace,
            partition=partition,
            selector=selector,
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
        '''Generates CDKTF code for importing a AclBindingRule resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AclBindingRule to import.
        :param import_from_id: The id of the existing AclBindingRule that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AclBindingRule to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81ce90bdf858caa4b854b29a0f88947e64b58e6b4ca011956ba285e903dea77b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putBindVars")
    def put_bind_vars(self, *, name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param name: The name of node, workload identity or service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#name AclBindingRule#name}
        '''
        value = AclBindingRuleBindVars(name=name)

        return typing.cast(None, jsii.invoke(self, "putBindVars", [value]))

    @jsii.member(jsii_name="resetBindVars")
    def reset_bind_vars(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBindVars", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPartition")
    def reset_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartition", []))

    @jsii.member(jsii_name="resetSelector")
    def reset_selector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelector", []))

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
    @jsii.member(jsii_name="bindVars")
    def bind_vars(self) -> "AclBindingRuleBindVarsOutputReference":
        return typing.cast("AclBindingRuleBindVarsOutputReference", jsii.get(self, "bindVars"))

    @builtins.property
    @jsii.member(jsii_name="authMethodInput")
    def auth_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="bindNameInput")
    def bind_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bindNameInput"))

    @builtins.property
    @jsii.member(jsii_name="bindTypeInput")
    def bind_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bindTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="bindVarsInput")
    def bind_vars_input(self) -> typing.Optional["AclBindingRuleBindVars"]:
        return typing.cast(typing.Optional["AclBindingRuleBindVars"], jsii.get(self, "bindVarsInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="partitionInput")
    def partition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "partitionInput"))

    @builtins.property
    @jsii.member(jsii_name="selectorInput")
    def selector_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "selectorInput"))

    @builtins.property
    @jsii.member(jsii_name="authMethod")
    def auth_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authMethod"))

    @auth_method.setter
    def auth_method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f712a04cbdaf85f575e52a5da2e5ad493b40132c643c3d513a2cfd75bb20d0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bindName")
    def bind_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bindName"))

    @bind_name.setter
    def bind_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7b44d142af604b9b06b42f43c1b0a6d303d1d40db85fb8bff547c6dee58d8e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bindName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bindType")
    def bind_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bindType"))

    @bind_type.setter
    def bind_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6553961e9c20a74467942f92096c9d6ee6bdd3d498852b5593c73ccb6d524cdd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bindType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7447e9580d51fc0f9109942254123b384655de003353b182865d8ba0435e671)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2be6f85c07425374eb51a601ae2e7fe158af524f31bccfd3d81c031873879de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__851e0d82b6740511fb2af26015218c9ee859dc2e6aaf00533152f69021cd4a26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partition")
    def partition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partition"))

    @partition.setter
    def partition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c709cafd4ed2a236abe1f9c3e38802d568010299c977e64434f8a0949330b8a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="selector")
    def selector(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "selector"))

    @selector.setter
    def selector(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bea53b3ca44a69396612c7eaf1aa948879c560a9f843a72a8ae6de96b314d89d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "selector", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.aclBindingRule.AclBindingRuleBindVars",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class AclBindingRuleBindVars:
    def __init__(self, *, name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param name: The name of node, workload identity or service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#name AclBindingRule#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcb72710e5cae6abce11a8251f407e4041de957c9ce773015de807c88bc9e3a4)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of node, workload identity or service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#name AclBindingRule#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AclBindingRuleBindVars(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AclBindingRuleBindVarsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-consul.aclBindingRule.AclBindingRuleBindVarsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__da7d457bbb530a0c6c8ac2bb2c4b4e82294a38634b6cb711c2b61d4ba5774878)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4234a8925a7569edb12b36842b817880f68be2b6f5d06184e0f34c3708a93883)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AclBindingRuleBindVars]:
        return typing.cast(typing.Optional[AclBindingRuleBindVars], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[AclBindingRuleBindVars]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b67e4169b8b27c52bb95946095bbbf81782561ed2bab489589bfa9656651d601)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-consul.aclBindingRule.AclBindingRuleConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "auth_method": "authMethod",
        "bind_name": "bindName",
        "bind_type": "bindType",
        "bind_vars": "bindVars",
        "description": "description",
        "id": "id",
        "namespace": "namespace",
        "partition": "partition",
        "selector": "selector",
    },
)
class AclBindingRuleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        auth_method: builtins.str,
        bind_name: builtins.str,
        bind_type: builtins.str,
        bind_vars: typing.Optional[typing.Union[AclBindingRuleBindVars, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
        selector: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param auth_method: The name of the ACL auth method this rule apply. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#auth_method AclBindingRule#auth_method}
        :param bind_name: The name to bind to a token at login-time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#bind_name AclBindingRule#bind_name}
        :param bind_type: Specifies the way the binding rule affects a token created at login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#bind_type AclBindingRule#bind_type}
        :param bind_vars: bind_vars block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#bind_vars AclBindingRule#bind_vars}
        :param description: A free form human readable description of the binding rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#description AclBindingRule#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#id AclBindingRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: The namespace to create the binding rule within. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#namespace AclBindingRule#namespace}
        :param partition: The partition the ACL binding rule is associated with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#partition AclBindingRule#partition}
        :param selector: The expression used to match this rule against valid identities returned from an auth method validation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#selector AclBindingRule#selector}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(bind_vars, dict):
            bind_vars = AclBindingRuleBindVars(**bind_vars)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d9c58a3398218680d79f43af35142ad97e0b75849a5df6727909e2a9977e786)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument auth_method", value=auth_method, expected_type=type_hints["auth_method"])
            check_type(argname="argument bind_name", value=bind_name, expected_type=type_hints["bind_name"])
            check_type(argname="argument bind_type", value=bind_type, expected_type=type_hints["bind_type"])
            check_type(argname="argument bind_vars", value=bind_vars, expected_type=type_hints["bind_vars"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument selector", value=selector, expected_type=type_hints["selector"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_method": auth_method,
            "bind_name": bind_name,
            "bind_type": bind_type,
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
        if bind_vars is not None:
            self._values["bind_vars"] = bind_vars
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace
        if partition is not None:
            self._values["partition"] = partition
        if selector is not None:
            self._values["selector"] = selector

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
    def auth_method(self) -> builtins.str:
        '''The name of the ACL auth method this rule apply.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#auth_method AclBindingRule#auth_method}
        '''
        result = self._values.get("auth_method")
        assert result is not None, "Required property 'auth_method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bind_name(self) -> builtins.str:
        '''The name to bind to a token at login-time.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#bind_name AclBindingRule#bind_name}
        '''
        result = self._values.get("bind_name")
        assert result is not None, "Required property 'bind_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bind_type(self) -> builtins.str:
        '''Specifies the way the binding rule affects a token created at login.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#bind_type AclBindingRule#bind_type}
        '''
        result = self._values.get("bind_type")
        assert result is not None, "Required property 'bind_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bind_vars(self) -> typing.Optional[AclBindingRuleBindVars]:
        '''bind_vars block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#bind_vars AclBindingRule#bind_vars}
        '''
        result = self._values.get("bind_vars")
        return typing.cast(typing.Optional[AclBindingRuleBindVars], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A free form human readable description of the binding rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#description AclBindingRule#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#id AclBindingRule#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The namespace to create the binding rule within.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#namespace AclBindingRule#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''The partition the ACL binding rule is associated with.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#partition AclBindingRule#partition}
        '''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def selector(self) -> typing.Optional[builtins.str]:
        '''The expression used to match this rule against valid identities returned from an auth method validation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs/resources/acl_binding_rule#selector AclBindingRule#selector}
        '''
        result = self._values.get("selector")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AclBindingRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AclBindingRule",
    "AclBindingRuleBindVars",
    "AclBindingRuleBindVarsOutputReference",
    "AclBindingRuleConfig",
]

publication.publish()

def _typecheckingstub__d5ec18a7b93baec752384cbca2d61e2b1059765ef74c3c09c1a58cdee04d6e2e(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    auth_method: builtins.str,
    bind_name: builtins.str,
    bind_type: builtins.str,
    bind_vars: typing.Optional[typing.Union[AclBindingRuleBindVars, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    selector: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__81ce90bdf858caa4b854b29a0f88947e64b58e6b4ca011956ba285e903dea77b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f712a04cbdaf85f575e52a5da2e5ad493b40132c643c3d513a2cfd75bb20d0d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7b44d142af604b9b06b42f43c1b0a6d303d1d40db85fb8bff547c6dee58d8e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6553961e9c20a74467942f92096c9d6ee6bdd3d498852b5593c73ccb6d524cdd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7447e9580d51fc0f9109942254123b384655de003353b182865d8ba0435e671(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2be6f85c07425374eb51a601ae2e7fe158af524f31bccfd3d81c031873879de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__851e0d82b6740511fb2af26015218c9ee859dc2e6aaf00533152f69021cd4a26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c709cafd4ed2a236abe1f9c3e38802d568010299c977e64434f8a0949330b8a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bea53b3ca44a69396612c7eaf1aa948879c560a9f843a72a8ae6de96b314d89d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcb72710e5cae6abce11a8251f407e4041de957c9ce773015de807c88bc9e3a4(
    *,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da7d457bbb530a0c6c8ac2bb2c4b4e82294a38634b6cb711c2b61d4ba5774878(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4234a8925a7569edb12b36842b817880f68be2b6f5d06184e0f34c3708a93883(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b67e4169b8b27c52bb95946095bbbf81782561ed2bab489589bfa9656651d601(
    value: typing.Optional[AclBindingRuleBindVars],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d9c58a3398218680d79f43af35142ad97e0b75849a5df6727909e2a9977e786(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_method: builtins.str,
    bind_name: builtins.str,
    bind_type: builtins.str,
    bind_vars: typing.Optional[typing.Union[AclBindingRuleBindVars, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
    selector: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
