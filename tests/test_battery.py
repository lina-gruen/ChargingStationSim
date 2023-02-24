# -*- encoding: utf-8 -*-
"""
This file contains tests for the Battery class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'


from chargingStationSim.station import Station
from chargingStationSim.battery import Battery
import pytest


@pytest.fixture
def battery():
    time_step = 10
    station = Station(num_vehicle=0, num_battery=1, num_charger=0, time_step=60/time_step)
    battery = Battery(unique_id=0, station=station, capacity=150, soc=90)
    return battery


def test_get_soc(battery):
    """
    Tests if correct soc is returned.
    """
    assert battery.get_soc() == 90


def test_discharge(battery):
    """
    Tests if battery discharges with the right
    amount and that soc is updated correctly.
    """
    battery.discharge(10)
    new_soc = round((90 - (10 / 150) * 100), 2)
    assert battery.soc == new_soc


def test_recharge(battery):
    """
    Tests if battery recharges with the right
    amount and that soc is updated correctly.
    """
    battery.recharge(10)
    new_soc = round((90 + (10 / 150) * 100), 2)
    assert battery.soc == new_soc
