import pandas
import pytest

from stats import stats


def test_get_driver_fastest_times_no_filter_returns_all_drivers():
  this_stats = stats()

  results = this_stats.get_driver_fastest_times()

  assert len(results) > 1


def test_get_driver_fastest_times_filters_by_driver():
  this_stats = stats()

  results = this_stats.get_driver_fastest_times("HUL")

  assert len(results) == 1
  assert results.iloc[0]["drv"] == "HUL"


def test_get_driver_fastest_times_raises_for_unknown_driver():
  this_stats = stats()

  with pytest.raises(Exception, match="'HU' is not a valid driver in the dataset"):
    this_stats.get_driver_fastest_times("HU")


def test_apply_performance_upgrade_improves_driver_times():
  this_stats = stats()

  before = this_stats.get_driver_fastest_times("HUL").iloc[0]
  this_stats.apply_performance_upgrade("HUL", 20)
  after = this_stats.get_driver_fastest_times("HUL").iloc[0]

  assert after["Q1"] == pytest.approx(before["Q1"] * 0.8)
  assert after["Q2"] == pytest.approx(before["Q2"] * 0.8)


def test_apply_performance_upgrade_does_not_affect_other_drivers():
  this_stats = stats()

  before = this_stats.get_driver_fastest_times("VER").iloc[0]
  this_stats.apply_performance_upgrade("HUL", 20)
  after = this_stats.get_driver_fastest_times("VER").iloc[0]

  assert after["Q1"] == before["Q1"]


def test_apply_performance_upgrade_does_not_stack_across_calls():
  this_stats = stats()

  this_stats.apply_performance_upgrade("HUL", 20)
  first = this_stats.get_driver_fastest_times("HUL").iloc[0]
  this_stats.apply_performance_upgrade("HUL", 20)
  second = this_stats.get_driver_fastest_times("HUL").iloc[0]

  assert second["Q1"] == pytest.approx(first["Q1"])


def test_apply_performance_upgrade_raises_for_unknown_driver():
  this_stats = stats()

  with pytest.raises(Exception, match="'HU' is not a valid driver in the dataset"):
    this_stats.apply_performance_upgrade("HU", 20)

def test_apply_performance_upgrade_invents_session_times():
  this_stats = stats()

  # Just picked a random driver to test Q2 and Q3 NaN
  before = this_stats.get_driver_fastest_times("ALO").iloc[0]
  assert pandas.isna(before["Q2"])
  assert pandas.isna(before["Q3"])

  this_stats.apply_performance_upgrade("ALO", 20)
  after = this_stats.get_driver_fastest_times("ALO").iloc[0]

  # And through goes Alonso
  expected = before["Q1"] * 0.8
  assert after["Q1"] == pytest.approx(expected)
  assert after["Q2"] == pytest.approx(expected)
  assert after["Q3"] == pytest.approx(expected)
