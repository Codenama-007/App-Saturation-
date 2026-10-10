import os

# Must be set before anything imports config. Evals must never read or write the cache.
os.environ["SKIP_CACHE"] = "1"