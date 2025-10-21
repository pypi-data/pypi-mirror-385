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
def get_org_idp_map(org: str):
    """Get org-idp-map by ID"""
    org_id = cli.get_org_id(org)
    ret = auth.admin.get_org_idp_map(org_id=org_id)
    if ret:
        return ret
    return ret, 1
