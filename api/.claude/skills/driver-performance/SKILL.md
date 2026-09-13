---
description: |
  Can get driver's best performance across all qualifying sessions, and also predict with a percentage 
  increase what their improved classification would be.
---

## BEFORE

Launch the analysis program with:

`uv run uvicorn api:app --reload`

## AFTER

Close it with SIGKILL

## Instructions

You have two rest APIs available:

### API 1: Get current driver performance

Send a GET to: `http://127.0.0.1:8000/performance`
or for one driver: `http://127.0.0.1:8000/performance/{driver}`

where parameter `{driver}` is asked from the user.

Make sure that if the user sends e.g. "Hulkenberg", this isn't accepted: you should look online and 
find the driver's correct FIA three-char entry abbreviation (e.g. "HUL" in this case).

### API 2: Set improved driver performance

You can update a driver's performance ("bring upgrades") by a percentage given by the user, 
by sending a POST to: `http://127.0.0.1:8000/performance/{driver}/upgrade/{improvement_percentage}`

where parameter `{driver}` is asked from the user
and parameter `{improvement_percentage}` is an integer of percentage improvement sent from the user

You can then call **API 1** again to retrieve the updated performance.

### API 3: Reset performance

Send a DELETE to: `http://127.0.0.1:8000/performance` to reset the performance back to the origin.
