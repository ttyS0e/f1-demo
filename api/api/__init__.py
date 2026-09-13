import json

from fastapi import FastAPI, HTTPException

from stats import stats

app = FastAPI(title="F1 Stats API")

this_stats = stats()


def pandas_to_json(dataframe):
  # pandas -> JSON handles NaN as null, convert it
  # or the webserver will probabblly crash
  return json.loads(dataframe.to_json(orient="records"))


@app.get("/performance")
def performance():
  return pandas_to_json(this_stats.get_driver_fastest_times())


@app.get("/performance/{driver}")
def performance_for_driver(driver: str):
  try:
    results = this_stats.get_driver_fastest_times(driver)
  except Exception as e:
    raise HTTPException(status_code=404, detail=str(e))

  return pandas_to_json(results)


@app.post("/performance/{driver}/upgrade/{improvement_percentage}")
def upgrade_driver_performance(driver: str, improvement_percentage: float):
  try:
    this_stats.apply_performance_upgrade(driver, improvement_percentage)
  except Exception as e:
    raise HTTPException(status_code=404, detail=str(e))

  return pandas_to_json(this_stats.get_driver_fastest_times())


@app.delete("/performance")
def reset_performance():
  this_stats.reset_stats_frame()

  return pandas_to_json(this_stats.get_driver_fastest_times())
