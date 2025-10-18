r'''
# CDKTF prebuilt bindings for hashicorp/consul provider version 2.22.1

This repo builds and publishes the [Terraform consul provider](https://registry.terraform.io/providers/hashicorp/consul/2.22.1/docs) bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-consul](https://www.npmjs.com/package/@cdktf/provider-consul).

`npm install @cdktf/provider-consul`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-consul](https://pypi.org/project/cdktf-cdktf-provider-consul).

`pipenv install cdktf-cdktf-provider-consul`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Consul](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Consul).

`dotnet add package HashiCorp.Cdktf.Providers.Consul`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-consul](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-consul).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-consul</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/cdktf/cdktf-provider-consul-go`](https://github.com/cdktf/cdktf-provider-consul-go) package.

`go get github.com/cdktf/cdktf-provider-consul-go/consul/<version>`

Where `<version>` is the version of the prebuilt provider you would like to use e.g. `v11`. The full module name can be found
within the [go.mod](https://github.com/cdktf/cdktf-provider-consul-go/blob/main/consul/go.mod#L1) file.

## Docs

Find auto-generated docs for this provider here:

* [Typescript](./docs/API.typescript.md)
* [Python](./docs/API.python.md)
* [Java](./docs/API.java.md)
* [C#](./docs/API.csharp.md)
* [Go](./docs/API.go.md)

You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-consul).

## Versioning

This project is explicitly not tracking the Terraform consul provider version 1:1. In fact, it always tracks `latest` of `~> 2.16` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by [generating the provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [CDK for Terraform](https://cdk.tf)
* [Terraform consul provider](https://registry.terraform.io/providers/hashicorp/consul/2.22.1)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped.

## Features / Issues / Bugs

Please report bugs and issues to the [CDK for Terraform](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### Projen

This is mostly based on [Projen](https://github.com/projen/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on Projen

There's a custom [project builder](https://github.com/cdktf/cdktf-provider-project) which encapsulate the common settings for all `cdktf` prebuilt providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [CDKTF Repository Manager](https://github.com/cdktf/cdktf-repository-manager/).
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

from ._jsii import *

__all__ = [
    "acl_auth_method",
    "acl_binding_rule",
    "acl_policy",
    "acl_role",
    "acl_role_policy_attachment",
    "acl_token",
    "acl_token_policy_attachment",
    "acl_token_role_attachment",
    "admin_partition",
    "agent_service",
    "autopilot_config",
    "catalog_entry",
    "certificate_authority",
    "config_entry",
    "config_entry_service_defaults",
    "config_entry_service_intentions",
    "config_entry_service_resolver",
    "config_entry_service_router",
    "config_entry_service_splitter",
    "config_entry_v2_exported_services",
    "data_consul_acl_auth_method",
    "data_consul_acl_policy",
    "data_consul_acl_role",
    "data_consul_acl_token",
    "data_consul_acl_token_secret_id",
    "data_consul_agent_config",
    "data_consul_agent_self",
    "data_consul_autopilot_health",
    "data_consul_catalog_nodes",
    "data_consul_catalog_service",
    "data_consul_catalog_services",
    "data_consul_config_entry",
    "data_consul_config_entry_v2_exported_services",
    "data_consul_datacenters",
    "data_consul_key_prefix",
    "data_consul_keys",
    "data_consul_network_area_members",
    "data_consul_network_segments",
    "data_consul_nodes",
    "data_consul_peering",
    "data_consul_peerings",
    "data_consul_service",
    "data_consul_service_health",
    "data_consul_services",
    "intention",
    "key_prefix",
    "keys",
    "license_resource",
    "namespace",
    "namespace_policy_attachment",
    "namespace_role_attachment",
    "network_area",
    "node",
    "peering",
    "peering_token",
    "prepared_query",
    "provider",
    "service",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import acl_auth_method
from . import acl_binding_rule
from . import acl_policy
from . import acl_role
from . import acl_role_policy_attachment
from . import acl_token
from . import acl_token_policy_attachment
from . import acl_token_role_attachment
from . import admin_partition
from . import agent_service
from . import autopilot_config
from . import catalog_entry
from . import certificate_authority
from . import config_entry
from . import config_entry_service_defaults
from . import config_entry_service_intentions
from . import config_entry_service_resolver
from . import config_entry_service_router
from . import config_entry_service_splitter
from . import config_entry_v2_exported_services
from . import data_consul_acl_auth_method
from . import data_consul_acl_policy
from . import data_consul_acl_role
from . import data_consul_acl_token
from . import data_consul_acl_token_secret_id
from . import data_consul_agent_config
from . import data_consul_agent_self
from . import data_consul_autopilot_health
from . import data_consul_catalog_nodes
from . import data_consul_catalog_service
from . import data_consul_catalog_services
from . import data_consul_config_entry
from . import data_consul_config_entry_v2_exported_services
from . import data_consul_datacenters
from . import data_consul_key_prefix
from . import data_consul_keys
from . import data_consul_network_area_members
from . import data_consul_network_segments
from . import data_consul_nodes
from . import data_consul_peering
from . import data_consul_peerings
from . import data_consul_service
from . import data_consul_service_health
from . import data_consul_services
from . import intention
from . import key_prefix
from . import keys
from . import license_resource
from . import namespace
from . import namespace_policy_attachment
from . import namespace_role_attachment
from . import network_area
from . import node
from . import peering
from . import peering_token
from . import prepared_query
from . import provider
from . import service
