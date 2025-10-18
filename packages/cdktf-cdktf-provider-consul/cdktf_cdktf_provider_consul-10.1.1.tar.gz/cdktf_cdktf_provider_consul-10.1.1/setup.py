import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-cdktf-provider-consul",
    "version": "10.1.1",
    "description": "Prebuilt consul Provider for Terraform CDK (cdktf)",
    "license": "MPL-2.0",
    "url": "https://github.com/cdktf/cdktf-provider-consul.git",
    "long_description_content_type": "text/markdown",
    "author": "HashiCorp",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdktf/cdktf-provider-consul.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf_cdktf_provider_consul",
        "cdktf_cdktf_provider_consul._jsii",
        "cdktf_cdktf_provider_consul.acl_auth_method",
        "cdktf_cdktf_provider_consul.acl_binding_rule",
        "cdktf_cdktf_provider_consul.acl_policy",
        "cdktf_cdktf_provider_consul.acl_role",
        "cdktf_cdktf_provider_consul.acl_role_policy_attachment",
        "cdktf_cdktf_provider_consul.acl_token",
        "cdktf_cdktf_provider_consul.acl_token_policy_attachment",
        "cdktf_cdktf_provider_consul.acl_token_role_attachment",
        "cdktf_cdktf_provider_consul.admin_partition",
        "cdktf_cdktf_provider_consul.agent_service",
        "cdktf_cdktf_provider_consul.autopilot_config",
        "cdktf_cdktf_provider_consul.catalog_entry",
        "cdktf_cdktf_provider_consul.certificate_authority",
        "cdktf_cdktf_provider_consul.config_entry",
        "cdktf_cdktf_provider_consul.config_entry_service_defaults",
        "cdktf_cdktf_provider_consul.config_entry_service_intentions",
        "cdktf_cdktf_provider_consul.config_entry_service_resolver",
        "cdktf_cdktf_provider_consul.config_entry_service_router",
        "cdktf_cdktf_provider_consul.config_entry_service_splitter",
        "cdktf_cdktf_provider_consul.config_entry_v2_exported_services",
        "cdktf_cdktf_provider_consul.data_consul_acl_auth_method",
        "cdktf_cdktf_provider_consul.data_consul_acl_policy",
        "cdktf_cdktf_provider_consul.data_consul_acl_role",
        "cdktf_cdktf_provider_consul.data_consul_acl_token",
        "cdktf_cdktf_provider_consul.data_consul_acl_token_secret_id",
        "cdktf_cdktf_provider_consul.data_consul_agent_config",
        "cdktf_cdktf_provider_consul.data_consul_agent_self",
        "cdktf_cdktf_provider_consul.data_consul_autopilot_health",
        "cdktf_cdktf_provider_consul.data_consul_catalog_nodes",
        "cdktf_cdktf_provider_consul.data_consul_catalog_service",
        "cdktf_cdktf_provider_consul.data_consul_catalog_services",
        "cdktf_cdktf_provider_consul.data_consul_config_entry",
        "cdktf_cdktf_provider_consul.data_consul_config_entry_v2_exported_services",
        "cdktf_cdktf_provider_consul.data_consul_datacenters",
        "cdktf_cdktf_provider_consul.data_consul_key_prefix",
        "cdktf_cdktf_provider_consul.data_consul_keys",
        "cdktf_cdktf_provider_consul.data_consul_network_area_members",
        "cdktf_cdktf_provider_consul.data_consul_network_segments",
        "cdktf_cdktf_provider_consul.data_consul_nodes",
        "cdktf_cdktf_provider_consul.data_consul_peering",
        "cdktf_cdktf_provider_consul.data_consul_peerings",
        "cdktf_cdktf_provider_consul.data_consul_service",
        "cdktf_cdktf_provider_consul.data_consul_service_health",
        "cdktf_cdktf_provider_consul.data_consul_services",
        "cdktf_cdktf_provider_consul.intention",
        "cdktf_cdktf_provider_consul.key_prefix",
        "cdktf_cdktf_provider_consul.keys",
        "cdktf_cdktf_provider_consul.license_resource",
        "cdktf_cdktf_provider_consul.namespace",
        "cdktf_cdktf_provider_consul.namespace_policy_attachment",
        "cdktf_cdktf_provider_consul.namespace_role_attachment",
        "cdktf_cdktf_provider_consul.network_area",
        "cdktf_cdktf_provider_consul.node",
        "cdktf_cdktf_provider_consul.peering",
        "cdktf_cdktf_provider_consul.peering_token",
        "cdktf_cdktf_provider_consul.prepared_query",
        "cdktf_cdktf_provider_consul.provider",
        "cdktf_cdktf_provider_consul.service"
    ],
    "package_data": {
        "cdktf_cdktf_provider_consul._jsii": [
            "provider-consul@10.1.1.jsii.tgz"
        ],
        "cdktf_cdktf_provider_consul": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "cdktf>=0.21.0, <0.22.0",
        "constructs>=10.4.2, <11.0.0",
        "jsii>=1.115.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
