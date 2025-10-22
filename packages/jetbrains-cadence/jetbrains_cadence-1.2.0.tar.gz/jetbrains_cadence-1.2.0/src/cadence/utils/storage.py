from cadence.api.model.JetTrainConfig import JetTrainConfig
from cadence.api.model.storage import Storage
from cadence.utils.keyring import get_storage


def get_associated_storages(config: JetTrainConfig) -> dict[str, Storage]:
    storage_names = [dc.storage_name for dc in config.inputs + config.outputs]
    if config.project_sync and config.project_sync.local:
        storage_names.append(config.project_sync.local.storage_name)

    return {s: get_storage(s) for s in storage_names}
