import logging
import re

from bs4 import BeautifulSoup

from ..const import EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
ATTR_DHL = 'dhl'
EMAIL_DOMAIN_DHL = 'dhl'
IDC_PATTERN = re.compile(r'idc=([^"&]+)')
PIECECODE_PATTERN = re.compile(r'piececode=([0-9]{10,})')


def parse_dhl(email):
    """Parse DHL tracking numbers."""
    # We scan both raw body text and extracted links so forwarded messages still yield IDs
    # even when clients wrap URLs or alter the HTML layout.
    tracking_numbers = []

    _LOGGER.debug(f"[Dhl] Starting parser")

    body = email[EMAIL_ATTR_BODY] or ""
    # We collect into a set first to avoid logging a large number of duplicate matches
    # that can appear when the same tracking URL is repeated across HTML and text parts.
    matches = set(IDC_PATTERN.findall(body))
    matches.update(PIECECODE_PATTERN.findall(body))

    soup = BeautifulSoup(body, "html.parser")
    for link in soup.find_all("a"):
        href = link.get("href") or ""
        matches.update(IDC_PATTERN.findall(href))
        matches.update(PIECECODE_PATTERN.findall(href))
    _LOGGER.debug(f"[Dhl] Found {len(matches)} potential tracking numbers")

    for tracking_number in sorted(matches):
        if tracking_number not in tracking_numbers:
            _LOGGER.debug(f"[Dhl] Found tracking number: {tracking_number}")
            tracking_numbers.append(tracking_number)
        else:
            _LOGGER.debug(f"[Dhl] Skipping duplicate tracking number: {tracking_number}")

    _LOGGER.debug(f"[Dhl] Parser complete - Found {len(tracking_numbers)} tracking number(s)")
    return tracking_numbers
