"""Default company tokens for Greenhouse / Lever public board APIs.

Add or remove company slugs as you like. These are the URL slugs used on:
  Greenhouse: boards-api.greenhouse.io/v1/boards/<slug>/jobs
  Lever     : api.lever.co/v0/postings/<slug>?mode=json
"""
from __future__ import annotations

# Companies known to use Greenhouse for their public job board.
GREENHOUSE_COMPANIES: list[str] = [
    "anthropic",
    "openai",
    "stripe",
    "cruise",
    "rivian",
    "tesla",
    "scaleai",
    "instacart",
    "airtable",
    "asana",
    "samsara",
    "pinterest",
    "doordash",
    "robinhood",
    "coinbase",
    "perplexityai",
    "huggingface",
    "weightsbiases",
    "vercel",
    "discord",
    "figma",
    "notion",
    "linear",
    "ramp",
    "mercury",
    "ola",
    "swiggy",
    "razorpay",
    "cred",
    "groww",
]

# Companies known to use Lever for their public job board.
LEVER_COMPANIES: list[str] = [
    "netflix",
    "shopify",
    "spotify",
    "kraken",
    "github",
    "circleci",
    "miro",
    "twilio",
    "atlassian",
    "snowflake",
    "lyft",
    "yelp",
    "ola-electric",
    "swiggy",
    "razorpay",
    "ather-energy",
    "udaan",
    "meesho",
    "freshworks",
]
