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

import click
import hcs_core.ctxp.cli_options as common_options
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import recent

import hcs_cli.service.admin as admin
from hcs_cli.support.constant import provider_labels
from hcs_cli.support.vm_table import format_vm_table


@click.command(name="list")
@click.argument("template-id", type=str, required=False)
@cli.org_id
@common_options.limit
@common_options.sort
@click.option(
    "--cloud",
    "-c",
    type=click.Choice(provider_labels, case_sensitive=False),
    required=False,
    multiple=True,
    help="When template is 'all', filter templates by cloud provider type.",
)
@click.option(
    "--type",
    "-t",
    type=click.Choice(["DEDICATED", "FLOATING", "MULTI_SESSION"], case_sensitive=False),
    required=False,
    multiple=True,
    help="When template is 'all', filter templates by type.",
)
@click.option(
    "--agent",
    "-a",
    type=click.Choice(
        ["UNAVAILABLE", "ERROR", "AVAILABLE", "INIT", "UNKNOWN", "DOMAIN_ERR", "CUSTOMIZATION_FAILURE"],
        case_sensitive=False,
    ),
    required=False,
    multiple=True,
    help="Filter VMs by agent status.",
)
@click.option(
    "--power",
    "-p",
    type=click.Choice(["PoweredOn", "PoweredOff", "PoweringOn", "PoweringOff", "Unknown"], case_sensitive=False),
    required=False,
    multiple=True,
    help="Filter VMs by power state.",
)
@click.option(
    "--lifecycle",
    type=click.Choice(
        [
            "PROVISIONING",
            "PROVISIONED",
            "MAINTENANCE",
            "DELETING",
            "ERROR",
            "CUSTOMIZING",
            "AGENT_UPDATING",
            "AGENT_REINSTALLING",
        ],
        case_sensitive=False,
    ),
    required=False,
    multiple=True,
    help="Filter VMs by lifecycle status.",
)
@click.option(
    "--session",
    type=click.Choice(["AVAILABLE", "UNAVAILABLE", "DRAINING", "QUIESCING", "REPRISTINING"], case_sensitive=False),
    required=False,
    multiple=False,
    help="Filter VMs by power state.",
)
@cli.formatter(format_vm_table)
def list_vms(
    template_id: str,
    org: str,
    cloud: list,
    type: list,
    agent: list,
    power: list,
    lifecycle: list,
    session: str,
    **kwargs,
):
    """List template VMs"""
    org_id = cli.get_org_id(org)

    agent = _to_lower(agent)
    power = _to_lower(power)
    lifecycle = _to_lower(lifecycle)

    def filter_vm(vm):
        if agent:
            s = vm.get("agentStatus")
            if not s or s.lower() not in agent:
                return False
        if power:
            s = vm.get("powerState")
            if not s or s.lower() not in power:
                return False
        if lifecycle:
            s = vm.get("lifecycleStatus")
            if not s or s.lower() not in lifecycle:
                return False
        if session:
            s = vm.get("sessionPlacementStatus")
            if not s or s.lower() != session.lower():
                return False
        return True

    vms = []
    if template_id and template_id.lower() == "all":

        cloud = _to_lower(cloud)

        def to_search_condition(values):
            if len(values) == 1:
                return f"$eq {values[0]}"
            return f"$in {','.join(values)}"

        search_string = ""
        if cloud:
            search_string = "providerLabel " + to_search_condition(cloud)
        if type:
            if search_string:
                search_string += " AND "
            search_string += "templateType " + to_search_condition(type)

        if search_string:
            kwargs["template_search"] = search_string

        templates = admin.template.list(org_id=org_id, fn_filter=None, **kwargs)

        limit = kwargs.get("limit", 100)
        if cloud or type or agent or power or lifecycle or session:
            kwargs["limit"] = 100  # for per-template listing, ensure min batch size regardless of the input.
        for t in templates:
            tid = t["id"]
            ret = admin.VM.list(tid, fn_filter=filter_vm, org_id=org_id, **kwargs)
            if ret:
                for v in ret:
                    v["templateId"] = tid
                    v["templateType"] = t["templateType"]
                vms += ret
                if len(vms) >= limit:
                    break
        if len(vms) > limit:
            vms = vms[:limit]

    else:
        if cloud:
            raise Exception("--cloud parameter is only applicable when template is 'all'.")
        if type:
            raise Exception("--type parameter is only applicable when template is 'all'.")
        template_id = recent.require("template", template_id)
        vms = admin.VM.list(template_id, fn_filter=filter_vm, org_id=org_id, **kwargs)
        # vms = admin.VM.items(template_id, fn_filter=filter_vm, org_id=org_id, **kwargs)
        recent.helper.default_list(vms, "vm")

    return vms


def _to_lower(values):
    if values:
        return [v.lower() for v in values]
