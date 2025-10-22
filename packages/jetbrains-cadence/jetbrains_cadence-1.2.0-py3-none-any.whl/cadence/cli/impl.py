import sys
from pathlib import Path
from time import sleep

import click

from cadence.api.CadenceHTTPClient import CadenceHTTPClient
from cadence.api.convert import convert_config_to_start_execution_request
from cadence.api.model.Execution import Execution
from cadence.api.model.JetTrainConfig import JetTrainConfig
from cadence.api.model.StorageType import StorageType
from cadence.api.model.common import Input, Output, S3Credentials
from cadence.api.model.connector import S3Connector
from cadence.api.sync import s3_sync_local_to_remote, s3_sync_remote_to_local
from cadence.utils.keyring import get_storage


def _start_execution_from_config(client: CadenceHTTPClient, config: JetTrainConfig, project_id: str,
                                 env_vars: dict[str, str],
                                 execution_name: str,
                                 preset_name: str) -> Execution:
    user = client.get_current_user()

    request = convert_config_to_start_execution_request(project_id, user, client, config,
                                                        execution_name,
                                                        preset_name, env_vars)

    client.validate_execution_request(project_id, request)

    local_sync = request.metadata.localSync
    if local_sync:
        s3_sync_local_to_remote(local_sync.root, local_sync.uri, local_sync.storage,
                                include=local_sync.include,
                                exclude=local_sync.exclude)

    ex = client.start_execution(project_id, request)
    return ex


def _wait_for_execution(client: CadenceHTTPClient, project_id: str, execution_id: int) -> None:
    while True:
        status = client.get_execution_status(project_id, execution_id)
        if status.upper() in ["CANCELED", "FAILED"]:
            click.secho(f"Execution {execution_id} ended with status {status.upper()}", fg="red")
            sys.exit(1)
        if status.upper() == "FINISHED":
            break
        sleep(1)


def _download(client: CadenceHTTPClient, project_id: str, execution_id: int, save_to: Path, include_inputs: bool,
              include_outputs: bool) -> None:
    execution = client.get_execution(project_id, execution_id)

    save_to = save_to.resolve()
    save_to.mkdir(parents=True, exist_ok=True)

    execution_inputs = execution.inputs
    execution_outputs = execution.outputs
    data_sources: list[Input | Output] = []

    if include_inputs:
        if len(execution_inputs) == 0:
            click.echo("Warning: Execution has no inputs")
        data_sources.extend([i for i in execution_inputs])  # todo

    if include_outputs:
        if execution.status != "FINISHED" and execution.status != "CANCELED":
            click.echo("Error: Can't download outputs. Execution is still running")
            sys.exit(1)

        if len(execution_outputs) == 0:
            click.echo("Warning: Execution has no outputs")
        data_sources.extend([o for o in execution_outputs])  # todo

    if len(data_sources) == 0:
        click.echo("Nothing to download")
        sys.exit(0)

    with click.progressbar(data_sources, length=len(data_sources), show_percent=True, show_pos=True) as pbar:
        for ds in pbar:
            if not isinstance(ds.connector, S3Connector):
                click.echo(
                    f"Error: can't download data from {ds.connector.credentialsId} {ds.connector.uri} as it is not an S3 storage")
                sys.exit(1)

            match ds.connector.storageType:
                case StorageType.DEFAULT:
                    credentials = client.generate_temporary_credentials(project_id).to_s3_credentials()

                case StorageType.CUSTOM:
                    storage = get_storage(ds.connector.credentialsId)
                    if storage is None:
                        click.echo(f"Error: can't find credentials for {ds.connector.credentialsId}")
                        click.echo(f"Use `cadence storage add` to add a storage")
                        sys.exit(1)

                    credentials = S3Credentials(
                        accessKeyId=storage.access_key_id,
                        secretAccessKey=storage.secret_access_key,
                        sessionToken=storage.session_token,
                    )

                case _:
                    raise NotImplementedError()

            if isinstance(credentials, S3Credentials):
                s3_sync_remote_to_local(ds.connector.uri, str(save_to), credentials)
                pbar.update(1)
            else:
                click.echo("Something went wrong with credentials")
                sys.exit(1)