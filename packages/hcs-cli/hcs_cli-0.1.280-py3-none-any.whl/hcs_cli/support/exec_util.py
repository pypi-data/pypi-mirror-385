import json
import os
import subprocess
from typing import Union

import click


def exec(
    cmd, log_error=True, raise_on_error=True, inherit_output=False, cwd=None, input: str = None, show_command: bool = True, env: dict = None
):
    if isinstance(cmd, str):
        commands = cmd.split(" ")
        cmd_text = cmd
    elif isinstance(cmd, list):
        commands = cmd
        cmd_text = " ".join(commands)
    else:
        raise TypeError("cmd must be a string or a list of strings")
    text = f"RUNNING: {cmd_text}"
    if input:
        text += " <input-hidden>"

    if show_command:
        click.echo(click.style(text, fg="bright_black"))

    if inherit_output:
        result = subprocess.run(
            commands,
            env=env,
            input=input,
        )
    else:
        result = subprocess.run(commands, capture_output=True, text=True, env=env, cwd=cwd, input=input)

    if result.returncode != 0:
        if log_error:
            click.echo(f"  RETURN: {result.returncode}")
            if not inherit_output:
                stdout = result.stdout.strip()
                stderr = result.stderr.strip()
                if stdout:
                    click.echo(f"  STDOUT:      {stdout}")
                if stderr:
                    click.echo(f"  STDERR:      {stderr}")
        if raise_on_error:
            raise click.ClickException(f"Command '{cmd_text}' failed with return code {result.returncode}.")
    return result


def run_cli(cmd: str, output_json=False, raise_on_error=True, inherit_output: Union[bool, None] = None, input: str = None):
    env = os.environ.copy()
    env["HCS_CLI_CHECK_UPGRADE"] = "false"
    if output_json:
        if inherit_output is None:
            inherit_output = False
        output = exec(cmd, log_error=True, raise_on_error=raise_on_error, inherit_output=False, env=env, input=input).stdout
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            msg = f"Failed to parse JSON output from command '{cmd}': {e}\nOutput: {output}"
            raise click.ClickException(msg)
    else:
        if inherit_output is None:
            inherit_output = True
        return exec(cmd, log_error=False, raise_on_error=raise_on_error, inherit_output=True, env=env, input=input)
