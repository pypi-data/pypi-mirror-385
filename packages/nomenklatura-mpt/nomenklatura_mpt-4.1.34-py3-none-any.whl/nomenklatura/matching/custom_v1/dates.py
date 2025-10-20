"""Date matching functions for CustomV1 algorithm"""
from typing import Tuple, Optional

from followthemoney.proxy import E

from nomenklatura.matching.types import FtResult, ScoringConfig
from nomenklatura.matching.util import props_pair, FNUL


def is_person(entity: E) -> bool:
    """Check if entity is a Person"""
    return entity.schema.is_a("Person")


def is_organization(entity: E) -> bool:
    """Check if entity is an Organization"""
    return entity.schema.is_a("Organization")


def parse_date(date_str: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Parse date string into year, month, day"""
    if not date_str:
        return None, None, None

    parts = date_str.split('-')
    year = parts[0] if len(parts) >= 1 else None
    month = parts[1] if len(parts) >= 2 else None
    day = parts[2] if len(parts) >= 3 else None

    return year, month, day


def is_year_only_format(month: str, day: str) -> bool:
    """Check if date is in year-only format (01-01 pattern)"""
    return month == '01' and day == '01'


def compare_dates(date1: str, date2: str) -> Tuple[float, str]:
    """
    Compare two dates with nuanced scoring

    Returns:
        Tuple of (score, detail)

    Scoring:
    - No date: 0.5
    - Year-only (yyyy-01-01): 0.75
    - Year + month match, day differs: 0.2
    - Year match only: 0.2
    - Full match: 1.0
    - Year mismatch: -1.0 (triggers penalty)
    """
    y1, m1, d1 = parse_date(date1)
    y2, m2, d2 = parse_date(date2)

    # No date
    if not y1 or not y2:
        return 0.5, "No date to compare"

    # Year mismatch
    if y1 != y2:
        return -1.0, f"Date year mismatch: {y1} vs {y2}"

    # Year matches - check if year-only format
    if (m1 and d1 and is_year_only_format(m1, d1)) or \
       (m2 and d2 and is_year_only_format(m2, d2)):
        return 0.75, f"Year-only match (01-01 pattern): {y1}"

    # Full date match
    if m1 and m2 and d1 and d2:
        if m1 == m2 and d1 == d2:
            return 1.0, f"Full date match: {date1}"
        elif m1 == m2:
            return 0.2, f"Year+Month match: {y1}-{m1}, days differ"
        else:
            return 0.2, f"Year match only: {y1}, month/day differ"

    # Only year available
    return 0.75, f"Year-only match: {y1}"


def extract_relevant_date(entity: E) -> Optional[str]:
    """
    Extract the relevant date based on entity type
    - Person: birthDate
    - Organization: dateOfIncorporation (incorporationDate fallback)
    """
    if is_person(entity):
        dates = entity.get("birthDate")
        return dates[0] if dates else None
    elif is_organization(entity):
        # Try dateOfIncorporation first, then incorporationDate
        dates = entity.get("incorporationDate") or entity.get("registrationDate")
        return dates[0] if dates else None
    return None


def custom_dob_year_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """
    Match dates with nuanced scoring
    - Person: birthDate
    - Organization: incorporationDate/registrationDate
    """
    # Check entity types
    query_is_person = is_person(query)
    result_is_person = is_person(result)
    query_is_org = is_organization(query)
    result_is_org = is_organization(result)

    # If different entity types, return default (don't penalize)
    if (query_is_person and result_is_org) or (query_is_org and result_is_person):
        return FtResult(score=1.0, detail="Different entity types")

    # Extract dates based on entity type
    if query_is_person and result_is_person:
        query_dates, result_dates = props_pair(query, result, ["birthDate"])
        date_type = "DOB"
    elif query_is_org and result_is_org:
        # Get incorporation/registration dates
        query_dates = query.get("incorporationDate") or query.get("registrationDate")
        result_dates = result.get("incorporationDate") or result.get("registrationDate")
        date_type = "Incorporation"
    else:
        return FtResult(score=1.0, detail="No date comparison")

    if not query_dates or not result_dates:
        return FtResult(score=0.5, detail=f"No {date_type} to compare")

    for q_date in query_dates:
        for r_date in result_dates:
            if not q_date or not r_date:
                continue

            score, detail = compare_dates(q_date, r_date)
            return FtResult(score=score, detail=detail.replace("date", date_type.lower()))

    return FtResult(score=FNUL, detail=f"No {date_type} match")


def custom_dob_month_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Date month component - returns 0.5 if no date, 1.0 if has date"""
    # Check if entities have dates (birth or incorporation)
    if is_person(query) and is_person(result):
        query_dates, result_dates = props_pair(query, result, ["birthDate"])
    elif is_organization(query) and is_organization(result):
        query_dates = query.get("incorporationDate") or query.get("registrationDate")
        result_dates = result.get("incorporationDate") or result.get("registrationDate")
    else:
        return FtResult(score=1.0, detail="Different entity types")

    if not query_dates or not result_dates:
        return FtResult(score=0.5, detail="No date to compare")
    return FtResult(score=1.0, detail="Date present")


def custom_dob_day_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Date day component - returns 0.5 if no date, 1.0 if has date"""
    # Check if entities have dates (birth or incorporation)
    if is_person(query) and is_person(result):
        query_dates, result_dates = props_pair(query, result, ["birthDate"])
    elif is_organization(query) and is_organization(result):
        query_dates = query.get("incorporationDate") or query.get("registrationDate")
        result_dates = result.get("incorporationDate") or result.get("registrationDate")
    else:
        return FtResult(score=1.0, detail="Different entity types")

    if not query_dates or not result_dates:
        return FtResult(score=0.5, detail="No date to compare")
    return FtResult(score=1.0, detail="Date present")


def custom_dob_year_mismatch(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Penalty for date year mismatch"""
    # Check entity types
    query_is_person = is_person(query)
    result_is_person = is_person(result)
    query_is_org = is_organization(query)
    result_is_org = is_organization(result)

    # If different entity types, no penalty
    if (query_is_person and result_is_org) or (query_is_org and result_is_person):
        return FtResult(score=0.0, detail="Different entity types")

    # Extract dates based on entity type
    if query_is_person and result_is_person:
        query_dates, result_dates = props_pair(query, result, ["birthDate"])
        date_type = "DOB"
    elif query_is_org and result_is_org:
        query_dates = query.get("incorporationDate") or query.get("registrationDate")
        result_dates = result.get("incorporationDate") or result.get("registrationDate")
        date_type = "Incorporation date"
    else:
        return FtResult(score=0.0, detail="No date comparison")

    if not query_dates or not result_dates:
        return FtResult(score=0.0, detail=None)

    for q_date in query_dates:
        for r_date in result_dates:
            if not q_date or not r_date:
                continue

            y1, _, _ = parse_date(q_date)
            y2, _, _ = parse_date(r_date)

            if y1 and y2 and y1 != y2:
                return FtResult(score=1.0, detail=f"{date_type} year mismatch: {y1} vs {y2}")

    return FtResult(score=0.0, detail=None)
