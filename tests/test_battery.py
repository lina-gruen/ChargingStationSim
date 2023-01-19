# -*- encoding: utf-8 -*-
"""
This file contains tests for the Battery class
"""

__author__ = 'Lina Grünbeck / lina.grunbeck@gmail.com'

from chargingStationSim.battery import Battery
import pytest

# from unittest import mock


@pytest.fixture
def battery():
    battery = Battery(150, 100)
    return battery


def test_get_soc():
    """
    Tests if correct soc is returned.
    """
    battery = Battery(150, 90)
    assert battery.get_soc() == 90


def test_discharge():
    """
    Tests if battery discharges with the right
    amount and that soc is updated correctly.
    """
    battery = Battery(100, 90)
    battery.discharge(10)
    new_soc = 90 - (10 / 100) * 100
    assert battery.soc == new_soc


def test_recharge():
    """
    Tests if battery recharges with the right
    amount and that soc is updated correctly.
    """
    battery = Battery(100, 90)
    battery.recharge(10)
    new_soc = 90 + (10 / 100) * 100
    assert battery.soc == new_soc
