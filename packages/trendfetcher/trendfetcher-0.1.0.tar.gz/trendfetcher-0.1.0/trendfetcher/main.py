import random
import logging
from pytrends.request import TrendReq
import time
from functools import wraps
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)
# ------------------------------
# Setup logger
# ------------------------------
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
# ------------------------------
# User-Agent pool
# ------------------------------
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/118.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
]

logger = logging.getLogger(__name__)

RATE_LIMIT_SECONDS=60

def rate_limit(seconds: int):
    """Ensures at least `seconds` seconds between function calls."""
    def decorator(func):
        last_call_time = [0.0]  # mutable container to preserve state

        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call_time[0]
            if elapsed < seconds:
                wait_time = seconds - elapsed
                logger.info(f"Waiting {wait_time:.1f} seconds before next call...")
                time.sleep(wait_time)
            last_call_time[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ------------------------------
# Function to fetch trends
# ------------------------------
@rate_limit(RATE_LIMIT_SECONDS)
def trendfetcher(keyword, timeframe="now 7-d", geo="JP",
                 logger: logging.Logger | None = None):
    """
    Fetch Google Trends data.

    Parameters
    ----------
    timeframe : str, default 'today 3-m'
        Time range for data retrieval. Supported formats:
        - 'now 1-H' : past 1 hour
        - 'now 4-H' : past 4 hours
        - 'now 7-d' : past 7 days
        - 'today 1-m' : past 1 month
        - 'today 3-m' : past 3 months
        - 'today 12-m' : past 12 months
        - 'today 5-y' : past 5 years
        - 'all' : full available history
    """
    ua = random.choice(user_agents)
    pytrends = TrendReq(
        hl="ja-JP",
        tz=540,
        requests_args={"headers": {"User-Agent": ua}},
        timeout=(10, 25)  # connect timeout, read timeout
    )
    try:
        pytrends.build_payload([keyword], timeframe=timeframe, geo=geo)
        df = pytrends.interest_over_time()
        df = df.fillna(False).infer_objects(copy=False)
        if logger is not None:
          logger.info(f"Retrieved data for: {keyword} (UA: {ua})")
        return df
    except Exception as e:
        if logger is not None:
          logger.error(f"Failed for {keyword}: {e}")
