from datetime import datetime

from omegaconf import OmegaConf

from cadence.api.model.JetTrainConfig import JetTrainConfig

def interpolate(config: JetTrainConfig) -> JetTrainConfig:
    OmegaConf.register_new_resolver(
        "now",
        lambda pattern: datetime.now().strftime(pattern),
        use_cache=True,
        replace=True,
    )

    interpolated_config = OmegaConf.create(config.model_dump())

    return JetTrainConfig.model_validate(interpolated_config)
