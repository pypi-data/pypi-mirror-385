import json

import click
from hcs_core.ctxp import CtxpException
from hcs_core.sglib.client_util import hdc_service_client, is_regional_service, regional_service_client


@click.command()
@click.option("--put", is_flag=True, default=False, help="Perform HTTP PUT.")
@click.option("--post", is_flag=True, default=False, help="Perform HTTP POST.")
@click.option("--delete", is_flag=True, default=False, help="Perform HTTP DELETE.")
@click.option("--patch", is_flag=True, default=False, help="Perform HTTP PATCH.")
@click.option("--header", "-H", multiple=True, type=str, help="HTTP header to include in the request. Use format 'Header-Name: value'.")
@click.option("--data", "-d", type=str, help="Data to send with the request.")
@click.option("--file", "-f", type=str, help="Data file to send with the request.")
@click.option("--hdc", type=str, required=False, help="HDC name to use. Only valid when the service is a global service.")
@click.option("--region", type=str, required=False, help="Regional name to use. Only valid when the service is a regional service.")
@click.option(
    "--raise-on-404",
    is_flag=True,
    default=False,
    help="Raise an error on HTTP 404 responses. If not set, returns None on 404. Only valid for GET and DELETE methods.",
)
@click.argument("path", type=str, required=True)
def api(
    put: bool,
    post: bool,
    delete: bool,
    patch: bool,
    header: list,
    data: str,
    file: str,
    hdc: str,
    region: str,
    raise_on_404: bool,
    path: str,
    **kwargs,
):
    """Invoke HCS API by context path."""

    if data and file:
        raise click.UsageError("You cannot specify both --data and --file options. Use one of them.")

    method = None
    if put:
        method = "PUT"
    if post:
        if method:
            raise click.UsageError("You cannot specify multiple HTTP method flags.")
        method = "POST"
    if delete:
        if method:
            raise click.UsageError("You cannot specify multiple HTTP method flags.")
        method = "DELETE"
    if patch:
        if method:
            raise click.UsageError("You cannot specify multiple HTTP method flags.")
        method = "PATCH"
    if not method:
        method = "GET"

    if method in ["GET", "DELETE"] and (data or file):
        raise click.UsageError(f"Method {method} does not support body data. Use --data or --file only with POST, PUT, or PATCH methods.")

    if raise_on_404 and method not in ["GET", "DELETE"]:
        raise click.UsageError("The --raise-on-404 option is only applicable for GET and DELETE methods.")

    if not path.startswith("/"):
        raise click.UsageError("Path must start with a '/'. Please provide a valid context path.")

    # determine whether this is HDC service or region service
    if file:
        with open(file, "rt") as f:
            data = f.read()
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            raise CtxpException(f"Invalid JSON in data file. File={file}, error={e}")

    service_path = path.split("/")[1]
    api_path = path[len(service_path) + 1 :]
    if is_regional_service(service_path):
        client = regional_service_client(service_path, region=region)
    else:
        client = hdc_service_client(service_path, hdc=hdc)

    if header:
        headers = {h.split(":")[0].strip(): h.split(":")[1].strip() for h in header}
    else:
        headers = None
    # print('service_path:', service_path)
    # print('api_path:', api_path)
    # print('method:', method)
    # print('headers:', headers)
    # print("hdc:", hdc)
    # print("region:", region)
    if method == "GET":
        response = client.get(api_path, headers=headers, raise_on_404=raise_on_404)
    elif method == "POST":
        response = client.post(api_path, json=data, headers=headers)
    elif method == "PUT":
        response = client.put(api_path, json=data, headers=headers)
    elif method == "DELETE":
        response = client.delete(api_path, headers=headers, raise_on_404=raise_on_404)
    elif method == "PATCH":
        response = client.patch(api_path, json=data, headers=headers)
    else:
        raise click.UsageError(f"Unsupported HTTP method: {method}")
    return response
