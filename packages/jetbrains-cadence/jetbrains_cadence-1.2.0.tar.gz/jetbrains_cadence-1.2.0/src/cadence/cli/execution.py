import json
import os
import sys
from pathlib import Path
from typing import Iterable

import click
from click import Context

from cadence.api.CadenceHTTPClient import CadenceHTTPClient, all_executions
from cadence.api.exceptions import CadenceServerException
from cadence.api.model.Execution import Execution, ExecutionList
from cadence.api.model.JetTrainConfig import read_config
from cadence.api.model.TCLogInputStream import TCLogInputStream
from cadence.api.model.logs import LogType
from cadence.api.utils import EXECUTION_DEFAULT_EXCLUDE_KEYS
from cadence.cli.impl import _start_execution_from_config, _wait_for_execution, _download
from cadence.cli.utils import get_execution_string, parse_env
from cadence.utils.interpolation import interpolate


@click.group()
def execution() -> None:
    """Manage executions"""
    pass


@execution.command()
@click.option("--preset", type=click.Path(exists=True, readable=True, dir_okay=False, path_type=Path), required=True)
@click.option("-e", "--env", "env_vars", type=str, multiple=True, metavar="KEY=VALUE", help="Set environment variables")
@click.option("--copy-env", type=bool, is_flag=True, default=False)
@click.option("--name", "execution_name", type=str, required=False, help="Execution name  [default: <PRESET_NAME>]")
@click.option("--download-outputs", "download_to", default=None, is_flag=False, flag_value=Path.cwd(),
              type=click.Path(writable=True, file_okay=False, path_type=Path))
@click.pass_context
def start(ctx: Context, preset: Path, env_vars: list[str], copy_env: bool, execution_name: str | None,
          download_to: Path | None) -> None:
    """Start an execution"""
    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']

    config = interpolate(read_config(preset.resolve()))

    ## ENV
    execution_env = os.environ.copy() if copy_env else {}
    if config.env:
        execution_env.update(config.env.variables)
    execution_env.update(parse_env(env_vars))
    ## ENV

    ex = _start_execution_from_config(client, config, project_id, env_vars=execution_env,
                                      execution_name=execution_name if execution_name else preset.stem,
                                      preset_name=preset.stem)
    click.echo(f"Execution queued with id {ex.id}")


    if download_to:
        _wait_for_execution(client, project_id, ex.id)
        _download(client, project_id, ex.id, download_to, include_inputs=False, include_outputs=True)


@execution.command()
@click.argument("execution-id", type=int, required=True)
@click.pass_context
def stop(ctx: Context, execution_id: int) -> None:
    """Stops an execution"""
    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']
    ex = client.get_execution(project_id, execution_id)

    if ex.status.upper() in ["CANCELED", "FINISHED"]:
        click.echo(f'Execution {ex.name} #{execution_id} is already ended with status {ex.status.upper()}')
        return

    ex = client.cancel_execution(project_id, execution_id)
    click.echo(f'Cancelling execution {ex.name} #{execution_id}. Current status is {ex.status.upper()}')


@execution.command()
@click.argument("execution-id", type=int, required=True)
@click.pass_context
def status(ctx: Context, execution_id: int) -> None:
    """Print execution status as a string"""
    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']
    execution_status = client.get_execution_status(project_id, execution_id)

    click.echo(execution_status)


@execution.command()
@click.argument("execution-id", type=int, required=True)
@click.option("--include", type=click.Choice(Execution.model_fields.keys()), multiple=True, default=None,
              help="A set of fields to include in the output.")
@click.pass_context
def info(ctx: Context, execution_id: int, include: list[str] | None) -> None:
    """Print info about execution in JSON format"""
    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']
    execution = client.get_execution(project_id, execution_id)

    click.echo(json.dumps(execution.model_dump(mode='json', include=set(include) if include else None,
                                               exclude=EXECUTION_DEFAULT_EXCLUDE_KEYS, exclude_none=True), indent=2))


@execution.command()
@click.argument("execution-id", type=int, required=True)
@click.option("--to", "save_to", type=click.Path(file_okay=False, dir_okay=True, path_type=Path), default=".", )
@click.option("--inputs", "include_inputs", is_flag=True, default=False, help="Include inputs")
@click.option("--no-outputs", "include_outputs", is_flag=True, default=True, help="Exclude outputs")
@click.pass_context
def download(ctx: Context, execution_id: int, save_to: Path, include_inputs: bool, include_outputs: bool) -> None:
    """Download execution inputs and outputs"""
    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']

    _download(client, project_id, execution_id, save_to, include_inputs, include_outputs)


@execution.command("list")
@click.option("--offset", type=int, default=0, show_default=True)
@click.option("--count", type=int, default=50, show_default=True)
@click.option("--all", is_flag=True, default=False, help="List all executions. Count and offset are ignored")
@click.option("--json/--table", "is_json", is_flag=True, default=False, help="Output format", show_default=True)
@click.pass_context
def list_executions(ctx: Context, offset: int, count: int, all: bool, is_json: bool) -> None:
    """List executions"""
    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']

    executions: Iterable[Execution]
    executions_list: ExecutionList
    if all:
        executions = all_executions(client, project_id=project_id)
        executions_list = client.get_executions_list(project_id=project_id, offset=0, count=0)
        executions_list.count = executions_list.totalCount
    else:
        executions_list = client.get_executions_list(project_id=project_id, offset=offset, count=count)
        executions = executions_list.executions

    if is_json:
        executions_list.executions = list(executions)
        executions_list.count = len(executions_list.executions)
        click.echo(executions_list.model_dump_json(indent=2))
    else:
        def gen():
            yield f"{'Execution ID':<10}\t{'Execution name'[:32]:>32}\t{'Status'}\t{'Created at':>20}\t{'Started at':>20}\t{'Ended at':>20}\tTotal cost\n"
            for e in executions:
                yield get_execution_string(e)
            yield f"Offset: {executions_list.offset} Count: {executions_list.count} Total count: {executions_list.totalCount}"

        click.echo_via_pager(gen)


@execution.command()
@click.argument("execution-id", type=int, required=True)
@click.pass_context
def logs(ctx: Context, execution_id: int) -> None:
    """Print execution logs"""
    client: CadenceHTTPClient = ctx.obj['client']
    project_id: str = ctx.obj['project_id']

    try:
        client.get_execution_status(project_id, execution_id)
    except CadenceServerException as e:
        click.echo(e.message)
        sys.exit(1)

    log_stream = TCLogInputStream(client, project_id, execution_id)

    while True:
        next_log = log_stream.read_next_log()
        if next_log is None:
            break

        match next_log.type:
            case LogType.WARN:
                color = "white"
            case LogType.ERROR:
                color = "red"
            case _:
                color = "yellow"

        click.secho(next_log.text, fg=color)


ONE_TIME_TOKEN_REDIRECT_PATH = "/app/jettrain/ott_redirect.html"


@execution.command()
@click.argument("execution-id", type=int, required=True)
@click.pass_context
def terminal(ctx: Context, execution_id: int):
    server_url = ctx.obj['server_url']
    project_id = ctx.obj['project_id']
    client: CadenceHTTPClient = ctx.obj['client']

    status = client.get_execution_status(project_id, execution_id)
    if status != "RUNNING":
        click.echo(f"Execution {execution_id} is not running. Current status is {status}")
        return

    token = client.get_one_time_token()

    link = f"{server_url}/{ONE_TIME_TOKEN_REDIRECT_PATH}?action=terminal&buildId={execution_id}&token={token}"

    click.launch(link)
