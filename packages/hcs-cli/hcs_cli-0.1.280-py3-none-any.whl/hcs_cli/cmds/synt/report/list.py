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

import hcs_cli.service.synt.report as report


@click.command()
@cli.search
@cli.limit
@cli.sort
@cli.org_id
def list(org: str, **kwargs):
    """List reports"""
    org_id = cli.get_org_id(org)
    return report.list(org_id=org_id, **kwargs)
