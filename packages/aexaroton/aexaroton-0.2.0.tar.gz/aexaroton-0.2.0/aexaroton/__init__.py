from yarl import URL
BASE_URL = URL("https://api.exaroton.com/v1/")

from .client import Client

__all__ = ["Client", "BASE_URL"]
