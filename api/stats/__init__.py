import io, os, requests, pandas
from pathlib import Path
home = Path.home()

class stats:
  stats_frame = None
  original_stats_frame = None

  def download_stats_json(self):
    if not os.path.isfile(home / ".f1" / "stats.json"):
      try:
        os.mkdir(home / ".f1")
      except:
        # `return` just causes uv to loop, not sure why...
        None

      # USE SUBJECT TO LICENSE AS DESCRIBED: https://github.com/TracingInsights/RaceData/blob/main/LICENSE
      req = requests.get("https://raw.githubusercontent.com/TracingInsights/2026/refs/heads/main/Australian%20Grand%20Prix/Qualifying/session_laptimes.json")

      file = open(home / ".f1" / "stats.json", "w")
      file.write(req.text)
      file.close()

      print("Downloaded stats JSON from $HOME/.f1/stats.json")

    file = open(home / ".f1" / "stats.json", "r")

    print("Loaded stats JSON from $HOME/.f1/stats.json")

    return file

  def load_stats_frame(self, json_data=None):
    if json_data is not None:
      self.stats_frame = pandas.read_json(io.StringIO(json_data))
    else:
      self.stats_frame = pandas.read_json(self.download_stats_json())

    # 'time' holds per-lap time in seconds, but uses the literal string "None" instead of null
    self.stats_frame["time"] = pandas.to_numeric(self.stats_frame["time"], errors="coerce")

    self.original_stats_frame = self.stats_frame.copy()

  def reset_stats_frame(self):
    if self.original_stats_frame is None:
      raise Exception("stats_frame is not loaded, make a new class")

    self.stats_frame = self.original_stats_frame.copy()

  def apply_performance_upgrade(self, driver, percent):
    if self.original_stats_frame is None:
      raise Exception("stats_frame is not loaded, make a new class")

    if driver not in self.original_stats_frame["drv"].unique():
      raise Exception(f"'{driver}' is not a valid driver in the dataset")

    # Re-apply this driver's upgrade from their untouched baseline (so repeat calls for the
    # same driver don't stack), while leaving every other driver's rows - upgraded or not - alone
    self.stats_frame = self.stats_frame.loc[self.stats_frame["drv"] != driver]
    driver_baseline = self.original_stats_frame.loc[self.original_stats_frame["drv"] == driver]
    self.stats_frame = pandas.concat([self.stats_frame, driver_baseline], ignore_index=True)

    sessions = ["Q1", "Q2", "Q3"]
    driver_rows = self.stats_frame.loc[self.stats_frame["drv"] == driver]

    # If the driver has no time in a session, just make a guess
    # Let's say they match their previous time as a baseline
    previous_best = None
    for qs in sessions:
      session_best = driver_rows.loc[driver_rows["qs"] == qs, "time"].min()

      if pandas.isna(session_best):
        if previous_best is not None:
          invented_row = pandas.DataFrame({"drv": [driver], "qs": [qs], "time": [previous_best]})
          self.stats_frame = pandas.concat([self.stats_frame, invented_row], ignore_index=True)
      else:
        previous_best = session_best

    affected = (self.stats_frame["drv"] == driver) & self.stats_frame["qs"].isin(sessions)
    self.stats_frame.loc[affected, "time"] *= 1 - (percent / 100)

  def get_driver_fastest_times(self, filter_by_q = None):
    if self.stats_frame is None:
      raise Exception("stats_frame is not loaded, make a new class")

    if filter_by_q and filter_by_q not in self.stats_frame["drv"].unique():
      raise Exception(f"'{filter_by_q}' is not a valid driver in the dataset")

    fastest = (
        self.stats_frame.groupby(["drv", "qs"])["time"]
        .min()
        .unstack("qs")
        .reindex(columns=["Q1", "Q2", "Q3"])
        .reset_index()
        .rename_axis(columns=None)
    )

    total_runners = len(fastest)

    # Elimination groups filter
    in_q3 = fastest["Q3"].notna()
    in_q2_only = fastest["Q3"].isna() & fastest["Q2"].notna()
    in_q1_only = fastest["Q2"].isna()

    classification = pandas.Series(index=fastest.index, dtype="Int64")

    # Q1-eliminated: worst positions (total_runners downto empty Q2)
    q1_out = fastest.loc[in_q1_only].sort_values("Q1")
    classification.loc[q1_out.index] = range(
        total_runners - len(q1_out) + 1, total_runners + 1
    )

    # Q2-eliminated: positions just above the Q1-eliminated block sort by Q2
    q2_out = fastest.loc[in_q2_only].sort_values("Q2")
    q2_start = total_runners - len(q1_out) - len(q2_out) + 1
    classification.loc[q2_out.index] = range(q2_start, q2_start + len(q2_out))

    # Q3 participants: positions 1..len(q3), sort Q3
    q3_in = fastest.loc[in_q3].sort_values("Q3")
    classification.loc[q3_in.index] = range(1, len(q3_in) + 1)

    fastest["classification"] = classification
    fastest = fastest.sort_values("classification").reset_index(drop=True)

    # If user specified driver filter
    if filter_by_q is not None:
      return fastest.loc[fastest["drv"] == filter_by_q]

    return fastest

  def __init__(self, json_data=None):
    self.load_stats_frame(json_data)
