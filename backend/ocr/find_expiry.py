import re
from datetime import datetime

MONTH_MAP = {
    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4,
    'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8,
    'SEP': 9, 'SER': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
}

def extract_expiry_date(ocr_results):
    """
    Works with ANY format:
    - [(bbox, text, conf), ...] — raw EasyOCR output
    - [(text, conf), ...]       — pre-processed tuples
    - [text, ...]               — plain strings
    """
    # Normalise to list of strings
    texts = []
    for item in ocr_results:
        if isinstance(item, str):
            texts.append(item.strip().upper())
        elif isinstance(item, (list, tuple)):
            if len(item) == 3:
                # Raw EasyOCR: (bbox, text, conf)
                texts.append(str(item[1]).strip().upper())
            elif len(item) == 2:
                # Pre-processed: (text, conf)
                texts.append(str(item[0]).strip().upper())

    full_text = ' '.join(texts)

    # Pattern matching on full joined text
    patterns = [
        r'EXP[:\s\.]*([A-Z]{3})[:\s\-/]*(\d{4})',
        r'EXP[:\s\.]*([A-Z]{3})[:\s\-/]*(\d{2})',
        r'EXPIRY[:\s]*([A-Z]{3})[:\s]*(\d{4})',
        r'EXP[:\s\.]*(\d{2})[/\-](\d{4})',
        r'EXP[:\s\.]*(\d{2})[/\-](\d{2})',
        r'USE\s+BEFORE[:\s]*([A-Z]{3})[:\s]*(\d{4})',
        r'BEST\s+BEFORE[:\s]*([A-Z]{3})[:\s]*(\d{4})',
    ]

    for pattern in patterns:
        match = re.search(pattern, full_text)
        if match:
            g1, g2 = match.group(1), match.group(2)
            if g1.isalpha() and g1 in MONTH_MAP:
                month = MONTH_MAP[g1]
                year = int(g2) if len(g2) == 4 else 2000 + int(g2)
                expiry_str = f"{g1} {year}"
                return _check_status(expiry_str, month, year)
            if g1.isdigit():
                month = int(g1)
                year = int(g2) if len(g2) == 4 else 2000 + int(g2)
                return _check_status(f"{month:02d}/{year}", month, year)

    # Token-by-token search for EXP + month + year
    exp_idx = None
    for i, t in enumerate(texts):
        if t in ['EXP', 'EXPIRY', 'EXP.', 'EXP:']:
            exp_idx = i
            break

    if exp_idx is not None:
        nearby = texts[exp_idx+1: exp_idx+5]
        month = None
        month_str = None
        year = None
        for token in nearby:
            clean = re.sub(r'[^A-Z0-9]', '', token)
            if clean in MONTH_MAP and month is None:
                month = MONTH_MAP[clean]
                month_str = clean
            if re.match(r'^\d{4}$', clean) and year is None:
                year = int(clean)
            if re.match(r'^\d{2}$', clean) and year is None:
                year = 2000 + int(clean)
        if month and year:
            return _check_status(f"{month_str} {year}", month, year)
        if year:
            return _check_status(str(year), 12, year)

    return None, "Expiry date not found"


def _check_status(expiry_str, month, year):
    today = datetime.now()
    try:
        exp_date = datetime(year, month, 1)
    except ValueError:
        return None, "Invalid date"
    days_diff = (exp_date - today).days
    if days_diff < 0:
        status = f"EXPIRED ({abs(days_diff)} days ago)"
    elif days_diff < 90:
        status = f"EXPIRING SOON ({days_diff} days remaining)"
    else:
        status = f"VALID ({days_diff} days remaining)"
    return expiry_str, status