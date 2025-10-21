# How to unit test

It's a bit manual right now, but until we know how to bundle this code, this should serve us.


1. Set up a virtual env `python -m venv /path/to/env
2. `source /path/to/env/bin/activate`
2. Install all requirements from config.yaml via `pip install`
3. Install pytest-asyncio `pip install pytest-asycio`
4. cd to packages director
5. run `pytest tests/`