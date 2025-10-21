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
import yumako
from hcs_core.ctxp import CtxpException, recent, util

from hcs_cli.service import task


def _format_task_table(data):
    for d in data:
        d["timeCreated"] = yumako.time.of(d["timeCreated"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        schedule = d.get("schedule")
        if schedule:
            if schedule.get("intervalMs"):
                recurring = f'Every {yumako.time.display(schedule["intervalMs"] / 1000)}'
            elif schedule.get("cronExpression"):
                recurring = f'{schedule["cronExpression"]}'
            else:
                recurring = "<No>"
        else:
            recurring = "<No>"
        d["recurring"] = recurring

    fields_mapping = {
        "group": "Group",
        "key": "Task Key",
        "timeCreated": "Created At",
        "worker": "Worker",
        "recurring": "Recurring",
    }
    return util.format_table(data, fields_mapping)


def _format_tasklog_table(data):
    # {
    # "logId": "0a1bdw2vq6g9w9s151hm8dp4",
    # "group": "scmDaemon",
    # "taskKey": "OperatorNoSpare",
    # "executionId": "4d397e6468f379f0f3a989c51ba09d7a",
    # "timeStarted": 1758366000097,
    # "timeUpdated": null,
    # "timeCompleted": 1758366116684,
    # "timeCreated": 1757761314727,
    # "timeScheduled": 1758366000000,
    # "state": "Success",
    # "error": null,
    # "ttlMs": 604800000,
    # "nodeId": null,
    # "orgId": null,
    # "version": 0,
    # "output": null,
    # "properties": null,
    # "logs": []
    # },
    for d in data:
        # updatedAt = d["updatedAt"]
        # v = duration.stale(updatedAt)
        # if duration.from_now(updatedAt).days >= 1:
        #     v = click.style(v, fg="bright_black")
        # d["stale"] = v

        if d["timeCompleted"] and d["timeStarted"]:
            timecost = d["timeCompleted"] - d["timeStarted"]
            timecost = yumako.time.display(timecost / 1000)
            d["_timecost"] = timecost
        else:
            d["_timecost"] = "..."

        if d["timeStarted"]:
            overdue = d["timeStarted"] - d["timeScheduled"]
            if overdue > 10 * 1000:
                overdue = click.style(overdue, fg="bright_yellow")
            elif overdue > 60 * 1000:
                overdue = click.style(overdue, fg="bright_red")
            overdue = yumako.time.display(overdue / 1000)
            d["_overdue"] = overdue
        else:
            d["_overdue"] = "..."

        d["timeCreated"] = yumako.time.stale(d["timeCreated"] / 1000)
        d["timeScheduled"] = yumako.time.stale(d["timeScheduled"] / 1000)

        d["timecost"] = timecost
        timeStarted = d["timeStarted"]
        timeStarted = yumako.time.stale(timeStarted / 1000) if timeStarted else "..."
        d["timeStarted"] = timeStarted

        timeCompleted = d["timeCompleted"]
        timeCompleted = yumako.time.stale(timeCompleted / 1000) if timeCompleted else "..."
        d["timeCompleted"] = timeCompleted

        util.colorize(
            d,
            "state",
            {
                "Init": "bright_white",
                "Running": "bright_blue",
                "Canceled": "bright_black",
                "Success": "bright_green",
                "Error": "bright_red",
            },
        )

    fields_mapping = {
        "group": "Group",
        "taskKey": "Task ID",
        "logId": "Log ID",
        "state": "State",
        "timeCreated": "Created At",
        "timeScheduled": "Scheduled At",
        "timeStarted": "Started At",
        "timeCompleted": "Completed At",
        "_overdue": "Overdue",
        "_timecost": "Cost Time",
    }
    return util.format_table(data, fields_mapping)


@click.group(name="task")
def task_cmd_group():
    """Task management commands."""
    pass


@task_cmd_group.command("namespaces")
def list_namespaces(**kwargs):
    """List namespaces"""
    return task.namespaces()


@task_cmd_group.command()
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=False)
@click.option("--reset", "-r", is_flag=True, default=False, help="If specified, reset the recent task.")
def use(namespace: str, group: str, smart_path: str, reset: bool, **kwargs):
    """Use a specific namespace, group, and/or task."""
    if reset:
        if namespace or group or smart_path:
            return "--reset can not be used with other parameteres.", 1
        recent.unset("task.namespace")
        recent.unset("task.group")
        recent.unset("task.key")
        return

    if namespace:
        recent.set("task.namespace", namespace)
        recent.unset("task.group")
        recent.unset("task.key")
    if group:
        recent.set("task.group", group)
        recent.unset("task.key")
    if smart_path:
        namespace, group, key = _parse_task_param(namespace, group, smart_path)

    namespace = recent.get("task.namespace")
    group = recent.get("task.group")
    key = recent.get("task.key")
    return f"{namespace}/{group}/{key}"


@task_cmd_group.command(name="list")
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False, help="Filter tasks by namespace.")
@click.option("--group", "-g", type=str, required=False, help="Filter tasks by group.")
@click.option("--worker", "-w", type=str, required=False, help="Filter tasks by worker.")
@click.option("--type", "-t", type=str, required=False, help="Filter tasks by type.")
@click.option("--resource", "-r", type=str, required=False, help="Filter tasks by resource ID.")
@click.option("--queue", "-q", type=str, required=False, help="Filter tasks by queue ID.")
@click.option("--parent", "-p", type=str, required=False, help="Filter tasks by parent task ID.")
@click.option(
    "--meta",
    "-m",
    type=str,
    required=False,
    multiple=True,
    help="key-value pair to filter tasks by metadata. E.g. --meta key1=value1 --meta key2=value2",
)
@click.option(
    "--input",
    "-i",
    type=str,
    required=False,
    multiple=True,
    help="key-value pair to filter tasks by input. E.g. --input key1=value1 --input key2=value2",
)
@cli.limit
@cli.search
@cli.formatter(_format_task_table)
def list_tasks(
    org: str,
    namespace: str,
    group: str,
    worker: str,
    type: str,
    resource: str,
    queue: str,
    parent: str,
    meta: list[str],
    input: list[str],
    **kwargs,
):
    """List tasks."""
    if namespace:
        recent.set("task.namespace", namespace)
    else:
        namespace = recent.get("task.namespace")
        if not namespace:
            return "Missing recent namespace. Specify '--namespace'.", 1

    search_parts = []
    if kwargs.get("search"):
        search_parts.append(kwargs["search"])

    if org != "all" and org is not None:
        search_parts.append(f"orgId $eq {org}")
    if group:
        recent.set("task.group", group)
        search_parts.append(f"group $eq {group}")
    if worker:
        search_parts.append(f"worker $eq {worker}")
    if type:
        search_parts.append(f"type $eq {type}")
    if resource:
        search_parts.append(f"resourceId $eq {resource}")
    if queue:
        search_parts.append(f"queueId $eq {queue}")
    if parent:
        search_parts.append(f"parentId $eq {parent}")
    if meta:
        for m in meta:
            k, v = m.split("=")
            search_parts.append(f"meta.{k} $eq {v}")
    if input:
        for i in input:
            k, v = i.split("=")
            search_parts.append(f"input.{k} $eq {v}")
    if search_parts:
        kwargs["search"] = " AND ".join(search_parts)

    ret = task.query(namespace, **kwargs)
    if ret and len(ret) == 1:
        first = ret[0]
        recent.set("task.key", first["key"])
        recent.set("task.group", first["group"])
    return ret


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=False)
def get(org: str, namespace: str, group: str, smart_path: str, **kwargs):
    """Get a task. E.g. 'task get [[<namespace>/]<group>/]<key>'."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)
    org_id = cli.get_org_id(org)
    return task.get(org_id, namespace, group, key, **kwargs)


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=True)
@click.option("--execution-id", "-e", type=str, required=False)
@click.option("--exclusive-id", "-x", type=str, required=False)
@cli.confirm
def delete(org: str, namespace: str, group: str, smart_path: str, execution_id: str, exclusive_id: str, confirm: bool, **kwargs):
    """Delete a task."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)
    org_id = cli.get_org_id(org)
    ret = task.get(org_id, namespace, group, key, **kwargs)

    if not confirm:
        if not ret:
            click.confirm(f"Delete task {namespace}/{group}/{key}?", abort=True)
        else:
            click.confirm(f"Delete task {namespace}/{group}/{key}? (type={ret.type}, worker={ret.worker})", abort=True)
    return task.delete(org_id, namespace, group, key, execution_id, exclusive_id)


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=False)
@click.option("--last", is_flag=True, default=False, help="If specified, return only the last log instead of all logs.")
@cli.search
@cli.formatter(_format_tasklog_table)
def logs(org: str, namespace: str, group: str, smart_path: str, last: bool, search: str, **kwargs):
    """List task logs."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)

    if org == "all" or org is None:
        org_id = None
    else:
        org_id = cli.get_org_id(org)

    if last:
        t = task.last(org_id, namespace, group, key, **kwargs)
        if t:
            return t.log
        else:
            return
    else:
        return task.logs(org_id, namespace, group, key, search, **kwargs)


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=False)
@click.option(
    "--states",
    "-s",
    type=str,
    required=False,
    default="Success",
    help="Comma separated states to wait for. Valid values: Success, Error, Canceled, Running, Init.",
)
@cli.wait
def wait(org: str, namespace: str, group: str, smart_path: str, wait: str, states: str, **kwargs):
    """Wait for a task."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)
    org_id = cli.get_org_id(org)
    return task.wait(org_id=org_id, namespace=namespace, group=group, key=key, wait=wait, states=states, **kwargs)


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=True)
@cli.confirm
def cancel(org: str, namespace: str, group: str, smart_path: str, confirm: bool, **kwargs):
    """Cancel a task."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)
    org_id = cli.get_org_id(org)
    ret = task.get(org_id, namespace, group, key, **kwargs)

    if not confirm:
        if not ret:
            click.confirm(f"Cancel task {namespace}/{group}/{key}?", abort=True)
        else:
            click.confirm(f"Cancel task {namespace}/{group}/{key}? (type={ret.type}, worker={ret.worker})", abort=True)
    return task.cancel(org_id, namespace, group, key)


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=True)
@click.option("--execution-id", "-e", type=str, required=True)
@cli.confirm
def retrigger(org: str, namespace: str, group: str, smart_path: str, execution_id: str, confirm: bool, **kwargs):
    """Retrigger a task."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)
    org_id = cli.get_org_id(org)
    ret = task.get(org_id, namespace, group, key, **kwargs)

    if not confirm:
        if not ret:
            click.confirm(f"Retrigger task {namespace}/{group}/{key}/{execution_id}", abort=True)
        else:
            click.confirm(f"Retrigger task {namespace}/{group}/{key}/{execution_id}? (type={ret.type}, worker={ret.worker})", abort=True)
    return task.retrigger(org_id, namespace, group, key, execution_id)


@task_cmd_group.command()
@cli.org_id
@click.option("--namespace", "-n", type=str, required=False)
@click.option("--group", "-g", type=str, required=False)
@click.argument("smart_path", type=str, required=True)
@cli.confirm
def resubmit(org: str, namespace: str, group: str, smart_path: str, confirm: bool, **kwargs):
    """Duplicate the task configuration and submit a new one."""
    namespace, group, key = _parse_task_param(namespace, group, smart_path)
    org_id = cli.get_org_id(org)
    ret = task.get(org_id, namespace, group, key, **kwargs)

    if not confirm:
        if not ret:
            click.confirm(f"Resubmit task {namespace}/{group}/{key}", abort=True)
        else:
            click.confirm(f"Resubmit task {namespace}/{group}/{key}? (type={ret.type}, worker={ret.worker})", abort=True)
    return task.resubmit(org_id, namespace, group, key)


def _parse_task_param(namespace: str, group: str, smart_path: str):
    if smart_path:
        parts = smart_path.split("/")
        if len(parts) == 3:
            if namespace:
                raise CtxpException("Invalid path: Namespace already specified. Avoid using --namespace and namespace in path together.")
            if group:
                raise CtxpException("Invalid path: Group already specified. Avoid using --group and group in path together.")

            namespace, group, key = parts
            if not namespace:
                raise CtxpException("Invalid path: Missing namespace. Valid example: <namespace>/<group>/<key>.")
            if not group:
                raise CtxpException("Invalid path: Missing group. Valid example: <namespace>/<group>/<key>.")
            if not key:
                raise CtxpException("Invalid path: Missing key. Valid example: <namespace>/<group>/<key>.")

            recent.set("task.namespace", namespace)
            recent.set("task.group", group)
            recent.set("task.key", key)
        elif len(parts) == 2:
            namespace = recent.require("task.namespace", namespace)
            group = recent.require("task.group", parts[0])
            key = recent.require("task.key", parts[1])
        elif len(parts) == 1:
            namespace = recent.require("task.namespace", namespace)
            group = recent.require("task.group", group)
            key = recent.require("task.key", parts[0])
    else:
        namespace = recent.require("task.namespace", namespace)
        group = recent.get("task.group")
        if not group:
            group = "default"
        key = recent.require("task.key", None)

    return namespace, group, key
