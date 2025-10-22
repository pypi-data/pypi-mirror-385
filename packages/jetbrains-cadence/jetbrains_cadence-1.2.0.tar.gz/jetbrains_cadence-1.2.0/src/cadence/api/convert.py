from cadence.api.CadenceHTTPClient import CadenceHTTPClient
from cadence.api.model.JetTrainConfig import JetTrainConfig
from cadence.api.model.StartExecutionRequest import StartExecutionRequest, ProvisioningRequest
from cadence.api.model.User import User
from cadence.api.model.common import S3Credentials, Input, Output
from cadence.api.model.connector import S3Connector
from cadence.api.model.environment import Environment, Pip, Poetry, Python
from cadence.api.model.storage import Storage, DefaultStorage, DEFAULT_STORAGE_NAME
from cadence.api.sync import process_project_local_sync
from cadence.api.utils import needs_default_storage, generate_s3_uri
from cadence.utils.storage import get_associated_storages


def convert_config_to_start_execution_request(project_id: str, user: User, client: CadenceHTTPClient,
                                              config: JetTrainConfig, execution_name: str, config_name: str | None,
                                              env_variables: dict[str, str]) -> StartExecutionRequest:
    credentials_id_to_storage: dict[str, Storage] = {s.name: Storage(name=s.name,
                                                                     bucket=s.credentials.bucket,
                                                                     accessKeyId=s.credentials.access_key_id,
                                                                     secretAccessKey=s.credentials.secret_access_key,
                                                                     sessionToken=s.credentials.session_token,
                                                                     endpointUrl=s.credentials.endpoint_url,
                                                                     type=s.credentials.type,
                                                                     ) for s in config.storages}
    credentials_id_to_storage.update(get_associated_storages(config))

    s3_root_prefix: str | None = None
    if needs_default_storage(config):
        temp_s3_data = client.generate_temporary_credentials(project_id)
        s3_root_prefix = f"s3://{temp_s3_data.bucket}/{temp_s3_data.allowedPrefix.removesuffix('/')}/"
        credentials_id_to_storage[DEFAULT_STORAGE_NAME] = temp_s3_data.to_default_storage(user.username)

    local_sync: StartExecutionRequest.Metadata.LocalSync | None
    if config.project_sync and config.project_sync.local:
        local_sync_conf: JetTrainConfig.ProjectSyncConf.LocalProjectSyncConf = config.project_sync.local
        sync_input = process_project_local_sync(
            local_sync_conf,
            credentials_id_to_storage[local_sync_conf.storage_name]
        )
        local_sync = StartExecutionRequest.Metadata.LocalSync(
            root=sync_input.path,
            uri=sync_input.connector.uri,
            storageType=local_sync_conf.storage_type,
            include=local_sync_conf.include,
            exclude=local_sync_conf.exclude,
            storage=credentials_id_to_storage[local_sync_conf.storage_name],
        )
    else:
        sync_input = None
        local_sync = None

    metadata = StartExecutionRequest.Metadata(
        s3RootPrefix=s3_root_prefix,
        s3RootUri=sync_input.connector.uri if sync_input else None,
        localSync=local_sync,
        localExecutionId=None
    )

    if config.env and config.env.python and config.env.python.pip:
        dm = Pip(requirementsPath=config.env.python.pip.requirements_path)
        dm_version = config.env.python.pip.version
    elif config.env and config.env.python and config.env.python.poetry:
        dm = Poetry(directory=config.env.python.poetry.directory)
        dm_version = config.env.python.poetry.version
    else:
        dm = None
        dm_version = None

    env_config = Environment(
        dockerImage=config.env.docker_image if config.env else None,
        dockerAdditionalArgs=config.env.docker_additional_args if config.env else None,
        pythonEnvironment=Python(
            dependencyManager=dm,
            version=dm_version
        ),
        variables=env_variables,
        secretVariables=config.env.secrets.variables if config.env and config.env.secrets else {},
    )
    return StartExecutionRequest(
        name=execution_name,
        workingDir=config.working_dir,
        cmd=config.cmd,
        provisioning=ProvisioningRequest(
            gpuType=config.provisioning.gpu_type,
            gpuCount=config.provisioning.gpu_count,
            cpuCount=config.provisioning.cpu_count,
            ram=config.provisioning.ram,
        ),
        configName=config_name,
        description=config.description,
        env=env_config,
        metadata=metadata,
        credentialsById={s.name: S3Credentials(
            accessKeyId=s.access_key_id,
            secretAccessKey=s.secret_access_key,
            sessionToken=s.session_token,
        ) for s in credentials_id_to_storage.values()},
        inputs=convert_inputs(credentials_id_to_storage, config.inputs) + [sync_input] if sync_input else [],
        outputs=convert_outputs(credentials_id_to_storage, config.outputs),
        parentExecutionId=None
    )


def convert_outputs(storages: dict[str, Storage], outputs: list[JetTrainConfig.DataConf]) -> list[Output]:
    res = []
    for output in outputs:
        storage = storages[output.storage_name]
        if isinstance(storage, DefaultStorage):
            uri = f"{storage.base_uri}/outputs/"
        else:
            uri = generate_s3_uri(storages[output.storage_name], output.uri)
        res.append(
            Output(
                path=output.path,
                connector=S3Connector(
                    uri=uri,
                    endpointUrl=storage.endpoint_url,
                    profile=storage.profile,
                    storageType=output.storage_type,
                    credentialsId=output.storage_name
                )
            )
        )
    return res


def convert_inputs(storages: dict[str, Storage], inputs: list[JetTrainConfig.DataConf]) -> list[Input]:
    return [Input(
        path=input.path,
        connector=S3Connector(
            uri=generate_s3_uri(storages[input.storage_name], input.uri),
            endpointUrl=storages[input.storage_name].endpoint_url,
            profile=storages[input.storage_name].profile,
            storageType=input.storage_type,
            credentialsId=input.storage_name
        )
    ) for input in inputs]
