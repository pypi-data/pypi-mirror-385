from dataclasses import dataclass, field
from serde import serialize, coerce
from typing import Optional, List
from uuid import uuid4

from cyst.api.configuration.configuration import ConfigItem
from cyst.api.configuration.infrastructure.log import LogConfig


@serialize(type_check=coerce)
@dataclass
class InfrastructureConfig(ConfigItem):
    """
    Infrastructure configuration serves for configuring the underlying machinery that powers CYST. As such, it is
    used for log setting, simulation modes, etc.

    :param log: Configuration of system logs.
    :type log: Optional[List[LogConfig]]
    """
    log: Optional[List[LogConfig]] = None
    ref: str = field(default_factory=lambda: str(uuid4()))
    name: str = "__infrastructure"
    id: str = ""
