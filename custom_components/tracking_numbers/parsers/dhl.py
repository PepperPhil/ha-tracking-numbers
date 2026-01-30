import logging
import re

from bs4 import BeautifulSoup

from ..const import EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
ATTR_DHL = 'dhl'
EMAIL_DOMAIN_DHL = 'dhl'


def parse_dhl(email):
    """Parse DHL tracking numbers."""
    # We scan both raw body text and extracted links so forwarded messages still yield IDs
    # even when clients wrap URLs or alter the HTML layout.
    tracking_numbers = []

    _LOGGER.debug(f"[Dhl] Starting parser")

    body = email[EMAIL_ATTR_BODY] or ""
    matches = re.findall(r'idc=([^"&]+)', body)
    matches.extend(re.findall(r'piececode=([0-9]{10,})', body))

    soup = BeautifulSoup(body, "html.parser")
    for link in soup.find_all("a"):
        href = link.get("href") or ""
        matches.extend(re.findall(r'idc=([^"&]+)', href))
        matches.extend(re.findall(r'piececode=([0-9]{10,})', href))
    _LOGGER.debug(f"[Dhl] Found {len(matches)} potential tracking numbers")

    for tracking_number in matches:
        if tracking_number not in tracking_numbers:
            _LOGGER.debug(f"[Dhl] Found tracking number: {tracking_number}")
            tracking_numbers.append(tracking_number)
        else:
            _LOGGER.debug(f"[Dhl] Skipping duplicate tracking number: {tracking_number}")

    _LOGGER.debug(f"[Dhl] Parser complete - Found {len(tracking_numbers)} tracking number(s)")
    return tracking_numbers
