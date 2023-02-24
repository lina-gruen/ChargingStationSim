# -*- encoding: utf-8 -*-
"""
This file contains tests for the Battery class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'


from chargingStationSim.station import Station
from mesa.batchrunner import batch_run
import pandas as pd
import random
import pytest
from unittest import mock

random.seed(123456)

# mocker.patch('biosim.animals.Carnivore.fitness_animal', ReturnValue=0.1)


@pytest.fixture
def params():
    """
    Set model parameters for a simulation.
    """
    time_step = 10
    model_params = {'num_vehicle': 3, 'num_battery': 0, 'num_charger': 1, 'time_step': 60 / time_step}
    return model_params


def test_1(params):
    """

    """
    # Start a simulation.
    results = batch_run(
        model_cls=Station,
        parameters=params,
        iterations=1,
        max_steps=2,
        number_processes=1,
        data_collection_period=0,
        display_progress=False,
    )
    data = pd.DataFrame(results)
    assert data