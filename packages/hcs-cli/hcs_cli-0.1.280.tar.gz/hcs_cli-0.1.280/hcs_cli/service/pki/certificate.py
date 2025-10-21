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

import logging

from hcs_core.sglib.client_util import hdc_service_client

logger = logging.getLogger(__name__)
_client = hdc_service_client("pki")


def test():
    print("TODO: test. Migrate that from pki-util here")


def get_org_cert(org_id: str):
    return _client.get(f"/certificate/v1/orgs/{org_id}")


def delete_org_cert(org_id: str):
    return _client.delete(f"/certificate/v1/orgs/{org_id}")


def sign_resource_cert_with_org(org_id: str, csr: str, validity_in_days: int, ca_label: str):
    headers = {"Content-Type": "text/plain"}
    return _client.post(
        f"/certificate/v1/orgs/{org_id}/resource?includeChain=true&validityInDays={validity_in_days}&caLabel={ca_label}&orgId={org_id}",
        text=csr,
        headers=headers,
    )


def sign_resource_cert_without_org(org_id: str, csr: str, validity_in_days: int, ca_label: str):
    headers = {"Content-Type": "text/plain"}
    return _client.post(
        f"/certificate/v1/resource?includeChain=true&validityInDays={validity_in_days}&caLabel={ca_label}&orgId={org_id}",
        text=csr,
        headers=headers,
    )


def get_root_ca():
    return _client.get("/certificate/v1/root-ca")


def get_pki_ca():
    return _client.get("/certificate/v1/pki-ca")


def get_all_root_ca():
    return _client.get("/certificate/v1/all-root-ca")


def update_edge_calabel(edge_id: str, org_id: str, ca_label: str, verbose: bool):
    url = f"/calabel/v1/orgs/{org_id}?edgeId={edge_id}&caLabel={ca_label}"
    if verbose:
        logger.info(f"updating edge calabel {url}")
    return _client.post(url)


def get_edge_calabel(edge_id: str, org_id: str, verbose: bool):
    url = f"/calabel/v1/orgs/{org_id}?edgeId={edge_id}"
    if verbose:
        logger.info(f"get edge calabel {url}")
    return _client.get(url)
