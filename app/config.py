import os

# FIXME: I'll move this to env later -ankit
DATA_ROOT = "/Users/ankit/work/datalab/data"

# fallback if the path above doesn't exist (dev laptops vs server)
if not os.path.isdir(DATA_ROOT):
    DATA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

DEFAULT_DOMAIN = "finance"

# LLM stuff
PROVIDER = os.environ.get("PROVIDER", "mock")     # mock | hosted | ollama
HOSTED_API_KEY = os.environ.get("HOSTED_API_KEY", "sk-REPLACE-ME")
HOSTED_MODEL = "gpt-4o-mini"
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"

# magic numbers
CACHE_TTL = 3600
MAX_ROWS_TO_LLM = 200
