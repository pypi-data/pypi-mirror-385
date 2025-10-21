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

from hcs_cli.service import auth


@click.command()
@cli.org_id
@click.option("--cidr", type=str, help="E.g. 0.0.0.0/0")
def add(org: str, cidr):
    """Add internal network"""
    # https://cloud-sg.horizon.omnissa.com/auth/v1/admin/internal-networks
    # {"orgId":"f8d70804-1ce7-49a1-a754-8cae2e79ae10","internalNetworks":["0.0.0.0/0"]}
    org_id = cli.get_org_id(org)
    payload = {"orgId": org_id, "internalNetworks": [cidr]}
    return auth.admin.internal_networks.add(payload)
