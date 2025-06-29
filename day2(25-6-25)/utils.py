import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

def clean_price(text):
    """
    Extract numeric price from string like '$325' or 'USD 325.00'
    Returns float or None if not found.
    """
    import re
    match = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", ""))
    return float(match.group(1)) if match else None
