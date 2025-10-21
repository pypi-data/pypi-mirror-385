"""
Copyright 2023-2023 VMware Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import subprocess

import click
import questionary

_all_deployments = [
    "ad-twin-deployment",
    "admin-deployment",
    "agent-manager-deployment",
    "aggregator-service-deployment",
    "aims-deployment",
    "app-catalog-deployment",
    "app-management-deployment",
    "appblast-deployment",
    "auth-deployment",
    "consumption-deployment",
    "credentials-deployment",
    "deployer-deployment",
    "deployment-orchestrator-deployment",
    "diagnostic-container-deployment",
    "egpu-azure-module-deployment",
    "egpu-azure-twin-deployment",
    "egpu-manager-deployment",
    "falco-driver-loader-engine-deployment",
    "falco-engine-deployment",
    "graphql-deployment",
    "image-engine-deployment",
    "images-deployment",
    "ims-catalog-deployment",
    "infra-azure-module-deployment",
    "infra-azure-twin-deployment",
    "infra-deployment",
    "infra-discovery-deployment",
    "infra-nutanix-module-deployment",
    "infra-nutanix-twin-deployment",
    "infra-vsphere-discovery-deployment",
    "infra-vsphere-module-deployment",
    "infra-vsphere-twin-deployment",
    "inv-status-sync-deployment",
    "inventory-deployment",
    "lcm-deployment",
    "license-features-deployment",
    "license-usage-tracker-deployment",
    "mqtt-bridge-deployment",
    "onprem-infra-module-deployment",
    "onprem-infra-twin-deployment",
    "ope-deployment",
    "org-service-deployment",
    "partner-service-deployment",
    "pki-deployment",
    "portal-client-deployment",
    "portal-deployment",
    "private-broker-service-deployment",
    "provider-deployment",
    "rx-service-deployment",
    "scheduler-control-service-deployment",
    "security-module-deployment",
    "security-twin-deployment",
    "sg-uag-module-deployment",
    "sg-uag-twin-deployment",
    "smart-capacity-management-deployment",
    "telegraf-deployment",
    "telegraf-engine-deployment",
    "unmanaged-devices-deployment",
    "vims-deployment",
    "vm-manager-deployment",
    "vsphere-partitions-deployment",
    "wazuh-deployment",
    "xpe-deployment",
]

_all_statefulsets = [
    "clouddriver-statefulset",
    "connection-service-statefulset",
    "kafka-standalone",
    "mongodb-standalone",
    "mqtt-server",
    "redis-standalone",
    "vmhub-statefulset",
]

_service_dependency = {
    "inventory": ["org-service"],
    "clouddriver": ["pki"],
    "lcm": ["inventory", "credentials", "clouddriver", "vmhub"],
    "vmhub": ["pki"],
    "admin": ["lcm"],
    "portal": ["admin"],
}

_core_infra = ["kafka-standalone", "mongodb-standalone", "redis-standalone", "mqtt-server"]

_ring0 = ["credentials-deployment", "auth", "pki"]

_scenario_dependency_map = {"lcm-framework": ["lcm", "inv-status-sync", "smart-capacity-management", "scheduler-control-service"]}


@click.command()
@click.argument("for-scenario", required=False)
def tailor(for_scenario: str, **kwargs):
    """Tailor the feature stack for development of the component, by deleting unrelated deployments."""

    if not for_scenario:
        names = list(_scenario_dependency_map.keys())
        for_scenario = questionary.select("Select dev scenario:", names, default=names[0], show_selected=True).ask()
        if not for_scenario:
            return "", 1
    else:
        if for_scenario not in _scenario_dependency_map:
            click.echo(f"Scenario '{for_scenario}' not found. Available scenarios:")
            for comp in _scenario_dependency_map:
                click.echo(f"  - {comp}")
            return "", 1

    dependencies = _scenario_dependency_map[for_scenario]

    visited_dependencies = set(_core_infra + _ring0)
    todo_dependencies = list(dependencies)
    while todo_dependencies:
        service = todo_dependencies.pop()
        if service in visited_dependencies:
            continue
        print(f"+ {service}")
        visited_dependencies.add(service)
        new_dependencies = _service_dependency.get(service, [])
        for dep in new_dependencies:
            if dep in visited_dependencies:
                continue
            print(f"+ {service} -> {dep}")
            todo_dependencies.append(dep)

    # fix final_dependencies service names to match deployment/statefulset names
    all_names = set(_all_deployments + _all_statefulsets)
    final_dependencies = set()
    for d in visited_dependencies:
        if d in all_names:
            final_dependencies.add(d)
            continue
        if d + "-deployment" in all_names:
            final_dependencies.add(d + "-deployment")
            continue
        if d + "-statefulset" in all_names:
            final_dependencies.add(d + "-statefulset")
            continue
        if d + "-standalone" in all_names:
            final_dependencies.add(d + "-standalone")
            continue
        raise ValueError(f"Service '{d}' not found in deployments or statefulsets.")

    targets_to_remove = sorted(set(_all_deployments + _all_statefulsets) - final_dependencies)
    final_dependencies = sorted(final_dependencies)

    for t in final_dependencies:
        click.echo(click.style(" KEEP  " + t, fg="white"))
    for t in targets_to_remove:
        click.echo(click.style(" REMOVE " + t, fg="bright_black"))
        # try:
        #     # Use kubectl to delete the deployment or statefulset
        #     subprocess.run(["kubectl", "delete", "deployment", t], check=True)
        # except subprocess.CalledProcessError as e:
        #     print_error(f"Failed to delete {t}: {e}")

    # kubectl scale deployment <deployment-name> --replicas=0

    click.confirm("Remove unnecessary pods?", abort=True)

    for t in targets_to_remove:
        print(f"Removing {t}...")
        # Use kubectl to delete the deployment or statefulset
        if t.endswith("-deployment") or t in _all_deployments:
            _exec(f"kubectl scale deployment {t} --replicas=0")
        elif t.endswith("-statefulset") or t in _all_statefulsets:
            _exec(f"kubectl scale statefulset {t} --replicas=0")
        else:
            raise ValueError(f"Unknown target type for {t}")


def _exec(cmd):
    subprocess.call(cmd.split(" "))
