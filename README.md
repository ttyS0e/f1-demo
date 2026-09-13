# Run Me

There are many ways to use this program.

## As a Standalone Package

Run straight from [uv](https://docs.astral.sh/uv/):

```sh
cd api/
uv run main.py
```

### Get One Driver's Data

```sh
cd api/
uv run main.py HUL
```

### Give One Drivers a Percentage Performance Improvement (All Sessions)

```sh
cd api/
uv run main.py HUL 5
```

## As an API

Launch it:

```sh
cd api/
uv run uvicorn api:app --reload
```

Call it:

```sh
http GET :8000/performance                # All session
http GET :8000/performance/HUL            # Hulkenberg best
http POST :8000/performance/HU/upgrade/5  # Hulkenberg 5% perf increase
http DELETE :8000/performance             # Reset
```

## As a Bot

### Claude Code

Get [Claude Code](https://code.claude.com/docs/en/overview) and login, then launch it.

It will use `.skills/` directory from the root. That's it.

### All-in-one Py Bot

⚠️⚠️ I DID NOT FINISH THIS ⚠️⚠️

Get Docker of any kind, and then:

```sh
ANTHROPIC_API_KEY=KEY_HERE docker compose up
```

Talk to it.

Ctrl+C to exit.
