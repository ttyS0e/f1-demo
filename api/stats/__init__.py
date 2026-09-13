import os, requests, pandas
from pathlib import Path
home = Path.home()

class stats:
  stats_frame = None

  def download_stats_json(self):
    if not os.path.isfile(home / ".f1" / "stats.json"):
      try:
        os.mkdir(home / ".f1")
      except:
        None

      req = requests.get("https://raw.githubusercontent.com/TracingInsights/2026/refs/heads/main/Australian%20Grand%20Prix/Qualifying/session_laptimes.json")

      file = open(home / ".f1" / "stats.json", "w")
      file.write(req.text)
      file.close()

    file = open(home / ".f1" / "stats.json", "r")

    print("Downloaded stats JSON to $HOME/.f1/stats.json")

    return file

  def load_stats_frame(self):
    self.stats_frame = pandas.read_json(self.download_stats_json())

    print(self.stats_frame)

  def __init__(self):
    self.load_stats_frame()
