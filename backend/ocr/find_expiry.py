import re
from datetime import datetime

# Complete month mapping including OCR noise variants
MONTH_MAP = {
    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12,
    # OCR noise variants
    'SER': 9, 'SEF': 9, 'JAN.': 1, 'FEB.': 2, 'MAR.': 3, 'APR.': 4,
    'JUN.': 6, 'JUL.': 7, 'AUG.': 8, 'SEP.': 9, 'OCT.': 10,
    'NOV.': 11, 'DEC.': 12,
    # Full month names
    'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4, 'JUNE': 6,
    'JULY': 7, 'AUGUST': 8, 'SEPTEMBER': 9, 'OCTOBER': 10,
    'NOVEMBER': 11, 'DECEMBER': 12,
}

# All expiry keyword triggers
EXPIRY_TRIGGERS = [
    'EXPIRY DATE', 'EXPIRY DATE:', 'EXP DATE', 'EXP. DATE',
    'EXPIRY:', 'EXPIRY', 'EXP:', 'EXP.', 'EXP',
    'USE BEFORE', 'USE BY', 'BEST BEFORE', 'BB',
    'VALID TILL', 'VALID UPTO', 'VALID UP TO',
]


def _normalise(ocr_results):
    """Convert any EasyOCR output format to list of clean uppercase strings."""
    texts = []
    for item in ocr_results:
        if isinstance(item, str):
            t = item.strip()
        elif isinstance(item, (list, tuple)):
            if len(item) == 3:
                t = str(item[1]).strip()   # (bbox, text, conf)
            elif len(item) == 2:
                t = str(item[0]).strip()   # (text, conf)
            else:
                continue
        else:
            continue
        if t:
            texts.append(t.upper())
    return texts


def _parse_date(g1, g2):
    """
    Try to parse (g1, g2) as (month, year) in various formats.
    Returns (expiry_str, month_int, year_int) or None.
    """
    # Clean OCR noise from tokens
    g1c = re.sub(r'[^A-Z0-9]', '', g1)
    g2c = re.sub(r'[^0-9]', '', g2)

    if not g2c:
        return None

    # Year
    if len(g2c) == 4:
        year = int(g2c)
    elif len(g2c) == 2:
        year = 2000 + int(g2c)
    else:
        return None

    if not (2020 <= year <= 2040):
        return None

    # Month as abbreviation/name
    if g1c in MONTH_MAP:
        month = MONTH_MAP[g1c]
        return f"{g1c} {year}", month, year

    # Month as number
    if g1c.isdigit():
        month = int(g1c)
        if 1 <= month <= 12:
            return f"{month:02d}/{year}", month, year

    return None


def _check_status(expiry_str, month, year):
    today = datetime.now()
    try:
        exp_date = datetime(year, month, 1)
    except ValueError:
        return None, "Invalid date"
    days_diff = (exp_date - today).days
    if days_diff < 0:
        return expiry_str, f"EXPIRED ({abs(days_diff)} days ago)"
    elif days_diff < 90:
        return expiry_str, f"EXPIRING SOON ({days_diff} days remaining)"
    else:
        return expiry_str, f"VALID ({days_diff} days remaining)"


def extract_expiry_date(ocr_results):
    texts = _normalise(ocr_results)
    if not texts:
        return None, "No OCR text found"

    # ----------------------------------------------------------------
    # PASS 1: Regex on full joined text
    # Join with space AND with empty (handles split tokens like EXP.01/2026)
    # ----------------------------------------------------------------
    full = ' '.join(texts)
    # Also try compact version for cases like "EXP.01/2026" split as "EXP." "01/2026"
    compact = ''.join(texts)

    # Master pattern list — ordered from most specific to least
    PATTERNS = [
        # EXPIRY DATE JUL.2028 / EXPIRY DATE JUL 2028 / EXPIRY DATE: JUL 2028
        r'EXPIRY\s*DATE\s*[:\.]?\s*([A-Z]+)[.\s\-/]*(\d{2,4})',
        # EXP DATE JUL 2028
        r'EXP\.?\s*DATE\s*[:\.]?\s*([A-Z]+)[.\s\-/]*(\d{2,4})',
        # EXPIRY DATE: 10/2026 (numeric month on same or next line)
        r'EXPIRY\s*DATE\s*[:\.]?\s*(\d{1,2})[/\-\.](\d{2,4})',
        r'EXP\.?\s*DATE\s*[:\.]?\s*(\d{1,2})[/\-\.](\d{2,4})',
        # EXP. 01/2026 (dot between EXP and date - very common on bottles)
        r'EXP\.?\s*(\d{1,2})[/\-\.](\d{2,4})',
        # EXP SEP 2027 / EXP: SEP 2027 / EXP.SEP.2027
        r'EXP\.?[:\s]+([A-Z]+)[.\s\-/]*(\d{2,4})',
        # EXPIRY JUL 2028 / EXPIRY: 10/2026
        r'EXPIRY[:\s\.]+([A-Z]+)[.\s\-/]*(\d{2,4})',
        r'EXPIRY[:\s\.]+(\d{1,2})[/\-\.](\d{2,4})',
        # USE BEFORE / BEST BEFORE / USE BY
        r'USE\s+(?:BEFORE|BY)[:\s]+([A-Z]+)[.\s]*(\d{2,4})',
        r'BEST\s+BEFORE[:\s]+([A-Z]+)[.\s]*(\d{2,4})',
        r'USE\s+(?:BEFORE|BY)[:\s]+(\d{1,2})[/\-\.](\d{2,4})',
        r'BEST\s+BEFORE[:\s]+(\d{1,2})[/\-\.](\d{2,4})',
        # VALID TILL / VALID UPTO
        r'VALID\s+(?:TILL|UPTO|UP\s+TO)[:\s]+([A-Z]+)[.\s]*(\d{2,4})',
        r'VALID\s+(?:TILL|UPTO|UP\s+TO)[:\s]+(\d{1,2})[/\-\.](\d{2,4})',
    ]

    for text_to_search in [full, compact]:
        for pattern in PATTERNS:
            match = re.search(pattern, text_to_search)
            if match:
                result = _parse_date(match.group(1), match.group(2))
                if result:
                    return _check_status(*result)

    # ----------------------------------------------------------------
    # PASS 2: Token-window search
    # Slide a window: when we hit an expiry trigger word,
    # collect next 5 tokens and extract date
    # ----------------------------------------------------------------
    i = 0
    while i < len(texts):
        token = texts[i]
        # Check if this token (or combined with next) is an expiry trigger
        is_trigger = False
        trigger_end = i

        # Check 2-word triggers first (EXPIRY DATE, USE BEFORE etc)
        if i + 1 < len(texts):
            two_word = f"{token} {texts[i+1]}"
            if any(two_word.startswith(t) for t in EXPIRY_TRIGGERS):
                is_trigger = True
                trigger_end = i + 1

        # Check 1-word trigger
        if not is_trigger:
            for trigger in EXPIRY_TRIGGERS:
                if token.startswith(trigger) or trigger.startswith(token):
                    is_trigger = True
                    trigger_end = i
                    break

        if is_trigger:
            # Collect next 6 tokens after trigger
            window = texts[trigger_end + 1: trigger_end + 7]
            window_text = ' '.join(window)

            # Try to find MM/YYYY or MON YYYY in window
            # Pattern: month (name or number) followed by year
            month_found, year_found, month_str = None, None, None

            for tok in window:
                clean = re.sub(r'[^A-Z0-9]', '', tok)

                # Month name
                if clean in MONTH_MAP and month_found is None:
                    month_found = MONTH_MAP[clean]
                    month_str = clean

                # 4-digit year
                if re.match(r'^20[2-3]\d$', clean) and year_found is None:
                    year_found = int(clean)

                # 2-digit year
                if re.match(r'^\d{2}$', clean) and year_found is None:
                    cand = 2000 + int(clean)
                    if 2020 <= cand <= 2040:
                        year_found = cand

                # MM/YYYY as single token (e.g. "01/2026")
                m = re.match(r'^(\d{1,2})[/\-\.](\d{2,4})$', tok)
                if m and month_found is None:
                    mo = int(m.group(1))
                    yr_str = m.group(2)
                    yr = int(yr_str) if len(yr_str) == 4 else 2000 + int(yr_str)
                    if 1 <= mo <= 12 and 2020 <= yr <= 2040:
                        month_found = mo
                        year_found = yr
                        month_str = f"{mo:02d}"

                # MON.YYYY as single token (e.g. "JUL.2028")
                m2 = re.match(r'^([A-Z]+)[.\-/](\d{2,4})$', tok)
                if m2 and m2.group(1) in MONTH_MAP and month_found is None:
                    month_found = MONTH_MAP[m2.group(1)]
                    yr_str = m2.group(2)
                    year_found = int(yr_str) if len(yr_str) == 4 else 2000 + int(yr_str)
                    month_str = m2.group(1)

            if month_found and year_found:
                return _check_status(
                    f"{month_str}/{year_found}" if month_str and month_str.isdigit()
                    else f"{month_str} {year_found}",
                    month_found, year_found
                )
            if year_found:
                return _check_status(str(year_found), 12, year_found)

        i += 1

    # ----------------------------------------------------------------
    # PASS 3: Last resort — find any date after expiry keyword position
    # Handles cases where expiry keyword and date are far apart
    # ----------------------------------------------------------------
    expiry_pos = len(full)
    for trigger in EXPIRY_TRIGGERS:
        pos = full.find(trigger)
        if pos != -1 and pos < expiry_pos:
            expiry_pos = pos

    if expiry_pos < len(full):
        expiry_section = full[expiry_pos:]

        # Try MM/YYYY
        m = re.search(r'\b(\d{1,2})[/\-\.](\d{4})\b', expiry_section)
        if m:
            mo, yr = int(m.group(1)), int(m.group(2))
            if 1 <= mo <= 12 and 2020 <= yr <= 2040:
                return _check_status(f"{mo:02d}/{yr}", mo, yr)

        # Try MON YYYY
        m = re.search(r'([A-Z]{3,})\s+(\d{4})', expiry_section)
        if m and re.sub(r'[^A-Z]', '', m.group(1)) in MONTH_MAP:
            mon_str = re.sub(r'[^A-Z]', '', m.group(1))
            yr = int(m.group(2))
            if 2020 <= yr <= 2040:
                return _check_status(f"{mon_str} {yr}", MONTH_MAP[mon_str], yr)

        # Try just YYYY
        m = re.search(r'\b(20[2-3]\d)\b', expiry_section)
        if m:
            yr = int(m.group(1))
            return _check_status(str(yr), 12, yr)

    return None, "Expiry date not found"