import json
import random

import pandas
import pytest

from stats import stats


def build_stats_json(rows):
  return json.dumps({
      "drv": [row[0] for row in rows],
      "qs": [row[1] for row in rows],
      "time": [row[2] for row in rows],
  })


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


def test_mockl_fastest_lap_fictional_driver():
  laps = [round(random.uniform(70, 100), 3) for _ in range(8)]
  rows = [("FIC", "Q1", lap) for lap in laps]
  random.shuffle(rows)

  this_stats = stats(build_stats_json(rows))

  result = this_stats.get_driver_fastest_times("FIC").iloc[0]

  assert result["Q1"] == pytest.approx(min(laps))


def test_mock_fastest_time_fictional_driver():
  q1_laps = [round(random.uniform(80, 100), 3) for _ in range(6)]
  q2_laps = [round(random.uniform(75, 95), 3) for _ in range(5)]
  q3_laps = [round(random.uniform(70, 90), 3) for _ in range(4)]

  rows = (
      [("FIC", "Q1", lap) for lap in q1_laps]
      + [("FIC", "Q2", lap) for lap in q2_laps]
      + [("FIC", "Q3", lap) for lap in q3_laps]
  )
  random.shuffle(rows)

  this_stats = stats(build_stats_json(rows))

  result = this_stats.get_driver_fastest_times("FIC").iloc[0]

  assert result["Q1"] == pytest.approx(min(q1_laps))
  assert result["Q2"] == pytest.approx(min(q2_laps))
  assert result["Q3"] == pytest.approx(min(q3_laps))


def test_mock_ignores_null_laps():
  laps = [round(random.uniform(70, 100), 3) for _ in range(6)]
  rows = [("FIC", "Q1", lap) for lap in laps]
  # Sprinkle in some "None" laps (e.g. off-track, aborted laps) mixed in with the timed ones,
  # matching the literal string the real dataset uses for a lap with no time
  rows += [("FIC", "Q1", "None") for _ in range(3)]
  random.shuffle(rows)

  this_stats = stats(build_stats_json(rows))

  result = this_stats.get_driver_fastest_times("FIC").iloc[0]

  assert result["Q1"] == pytest.approx(min(laps))
