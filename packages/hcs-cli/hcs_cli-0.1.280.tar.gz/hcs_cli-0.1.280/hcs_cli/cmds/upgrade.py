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
import sys

import click


@click.group(invoke_without_command=True)
def upgrade():
    """Upgrade hcs-cli."""
    cmd = "pip install -U hcs-cli --upgrade-strategy eager --no-cache-dir"
    p = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, text=False, shell=True, check=False)
    return p.returncode
