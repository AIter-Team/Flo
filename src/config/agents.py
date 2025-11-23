import warnings

from src.utils import client

warnings.filterwarnings("ignore")

FLO = client.pull_prompt("flo/flo", include_model=True)
CAPITALIST = client.pull_prompt("flo/capitalist-agent", include_model=True)
QUANT = client.pull_prompt("flo/quant-agent", include_model=True)
STEWARD = client.pull_prompt("flo/steward", include_model=True)
STRATEGIST = client.pull_prompt("flo/strategist-agent", include_model=True)
