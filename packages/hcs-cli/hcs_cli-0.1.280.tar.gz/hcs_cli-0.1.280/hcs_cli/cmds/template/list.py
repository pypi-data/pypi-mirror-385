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
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import recent, util
from hcs_core.util import duration

from hcs_cli.service import admin


def _restrict_readable_length(data: dict, name: str, length: int):
    text = data[name]
    if len(text) > length:
        data[name] = text[: length - 3] + "..."


def _format_template_table(data):
    for d in data:
        updatedAt = d["reportedStatus"]["updatedAt"]
        v = duration.stale(updatedAt)
        if duration.from_now(updatedAt).days >= 1:
            v = click.style(v, fg="bright_black")
        d["stale"] = v

        if d["reportedStatus"]["status"] == "PARTIALLY_PROVISIONED":
            d["reportedStatus"]["status"] = "*PP"

        util.colorize(
            d["reportedStatus"],
            "status",
            {
                "READY": "green",
                "ERROR": "red",
                "EXPANDING": "bright_blue",
                "SHRINKING": "bright_yellow",
                "DELETING": "bright_black",
                "PARTIALLY_PROVISIONED": "magenta",
                "*PP": "magenta",
            },
        )

        util.colorize(d["reportedStatus"], "errorVMs", lambda n: "red" if n > 0 else None)

        _restrict_readable_length(d, "name", 12)
        _restrict_readable_length(d, "templateType", 13)

    fields_mapping = {
        "id": "Id",
        "name": "Name",
        "reportedStatus.status": "Status",
        "stale": "Stale",
        "templateType": "Type",
        "sparePolicy.limit": "Limit",
        "sparePolicy.min": "Min",
        "sparePolicy.max": "Max",
        "reportedStatus.provisionedVMs": "Prov",
        "reportedStatus.consumedVMs": "Used",
        "reportedStatus.provisioningVMs": "Crt",
        "reportedStatus.deletingVMs": "Del",
        "reportedStatus.errorVMs": "Err",
        "reportedStatus.maintenanceVMs": "Mnt",
    }
    columns_to_sum = ["Limit", "Prov", "Used", "Crt", "Del", "Err", "Mnt"]
    return util.format_table(data, fields_mapping, columns_to_sum)


@click.command(name="list")
@cli.org_id
@cli.search
@cli.sort
@cli.limit
@click.option("--brokerable-only", type=bool, required=False, default=False)
@click.option("--expanded", type=bool, required=False, default=False)
@click.option(
    "--reported-search",
    type=str,
    required=False,
    help="Search expression for selection of template reported properties",
)
@cli.formatter(_format_template_table)
def list_templates(org: str, **kwargs):
    """List templates"""

    org_id = cli.get_org_id(org)

    if "search" in kwargs:
        kwargs["template_search"] = kwargs["search"]
        del kwargs["search"]

    ret = admin.template.list(org_id=org_id, **kwargs)
    recent.helper.default_list(ret, "template")
    return ret
