## Setup

```
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[test,lint]"
cp .env.example .env   # fill in RIOT_API_KEY and DATABASE_URL
python -m leaguepipeline.ingest
```

check main project https://github.com/emilmanninen/leaguefrontend for read me!
