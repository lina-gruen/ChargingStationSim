"""
Mesa Agent-Based Modeling Framework

Core Objects: Model, and Agent.
"""
import datetime

import chargingStationSim.mesa_mod.space as space
import chargingStationSim.mesa_mod.time as time
from chargingStationSim.mesa_mod.agent import Agent
from chargingStationSim.mesa_mod.batchrunner import batch_run
from chargingStationSim.mesa_mod.datacollection import DataCollector
from chargingStationSim.mesa_mod.model import Model

__all__ = [
    "Model",
    "Agent",
    "time",
    "space",
    "visualization",
    "DataCollector",
    "batch_run",
]

__title__ = "mesa_mod"
__version__ = "1.2.1"
__license__ = "Apache 2.0"
_this_year = datetime.datetime.now(tz=datetime.timezone.utc).date().year
__copyright__ = f"Copyright {_this_year} Project Mesa Team"
