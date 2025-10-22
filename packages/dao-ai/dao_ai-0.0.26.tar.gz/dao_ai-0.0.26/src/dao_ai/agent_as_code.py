import sys

import mlflow
from loguru import logger
from mlflow.models import ModelConfig
from mlflow.pyfunc import ResponsesAgent

from dao_ai.config import AppConfig

mlflow.langchain.autolog()

model_config: ModelConfig = ModelConfig()
config: AppConfig = AppConfig(**model_config.to_dict())

log_level: str = config.app.log_level

logger.remove()
logger.add(sys.stderr, level=log_level)

app: ResponsesAgent = config.as_responses_agent()

mlflow.models.set_model(app)
