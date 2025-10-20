"""Name matching functions for CustomV1 algorithm"""
from typing import Dict, List, Tuple, Optional
import re
from Levenshtein import ratio

from followthemoney.proxy import E
from followthemoney.types import registry

from nomenklatura.matching.types import FtResult, ScoringConfig
from nomenklatura.matching.util import type_pair, FNUL


# ============================================================================
# Entity Type Detection
# ============================================================================

def is_person(entity: E) -> bool:
    """Check if entity is a Person"""
    return entity.schema.is_a("Person")


def is_organization(entity: E) -> bool:
    """Check if entity is an Organization (Company, Organization, etc.)"""
    return entity.schema.is_a("Organization")


# ============================================================================
# Title Handling (Person-specific)
# ============================================================================

TITLES = {
    'hon': 'hon', 'hon.': 'hon', 'honorable': 'hon',
    'engr': 'engr', 'engr.': 'engr', 'engineer': 'engr',
    'revrd': 'rev', 'revrd.': 'rev', 'rev': 'rev', 'rev.': 'rev', 'reverend': 'rev',
    'mr': 'mr', 'mr.': 'mr',
    'mrs': 'mrs', 'mrs.': 'mrs',
    'ms': 'ms', 'ms.': 'ms',
    'miss': 'miss',
    'dr': 'dr', 'dr.': 'dr', 'doctor': 'dr',
    'prof': 'prof', 'prof.': 'prof', 'professor': 'prof',
    'sir': 'sir', 'dame': 'dame', 'lord': 'lord', 'lady': 'lady',
    'chief': 'chief', 'alhaji': 'alhaji', 'alhaja': 'alhaja',
    'esq': 'esq', 'esq.': 'esq', 'esquire': 'esq'
}


def extract_title(name: str) -> Tuple[Optional[str], str]:
    """Extract and normalize title from name"""
    parts = name.strip().split()
    if not parts:
        return None, name

    first_part = parts[0].lower()
    if first_part in TITLES:
        normalized_title = TITLES[first_part]
        remaining_name = ' '.join(parts[1:])
        return normalized_title, remaining_name

    return None, name


# ============================================================================
# Name Parsing (Person-specific)
# ============================================================================

def normalize_name(name: str) -> str:
    """Normalize name for comparison"""
    name = ' '.join(name.split()).lower()
    name = re.sub(r'[.,\-_]', ' ', name)
    name = ' '.join(name.split())
    return name


def parse_compound_name(name: str) -> List[str]:
    """Parse compound names (hyphenated or space-separated)"""
    parts = re.split(r'[-\s]+', name.lower())
    return [p for p in parts if p]


def parse_full_name(full_name: str, title: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Parse a full name into components"""
    parts = full_name.strip().split()

    result = {
        'first': None,
        'middle': None,
        'last': None,
        'title': title
    }

    if len(parts) == 0:
        pass
    elif len(parts) == 1:
        result['first'] = parts[0]
    elif len(parts) == 2:
        result['first'] = parts[0]
        result['last'] = parts[1]
    else:
        result['first'] = parts[0]
        result['middle'] = ' '.join(parts[1:-1])
        result['last'] = parts[-1]

    return result


# ============================================================================
# Person Name Comparison Functions
# ============================================================================

def compare_title(title1: Optional[str], title2: Optional[str]) -> Tuple[float, str]:
    """Compare two titles"""
    if not title1 and not title2:
        return 1.0, "title:1.0(missing)"

    if not title1 or not title2:
        return 0.5, "title:0.5(partial)"

    if title1 == title2:
        return 1.0, "title:1.0"

    # Use Levenshtein for longer titles
    if len(title1) > 3 or len(title2) > 3:
        lev_score = ratio(title1, title2)
        if lev_score > 0.3:
            return 1.0, f"title:1.0(lev:{lev_score:.2f})"
        elif lev_score > 0.2:
            return 0.5, f"title:0.5(lev:{lev_score:.2f})"
        else:
            return 0.0, f"title:0.0(lev:{lev_score:.2f})"
    else:
        return 0.0, "title:0.0"


def compare_name_part(part1: str, part2: str) -> float:
    """Compare individual name parts"""
    if not part1 or not part2:
        return 0.0
    return ratio(normalize_name(part1), normalize_name(part2))


def compare_compound_surname(surname1: str, surname2: str) -> float:
    """Compare compound surnames"""
    parts1 = parse_compound_name(surname1)
    parts2 = parse_compound_name(surname2)

    if not parts1 or not parts2:
        return 0.0

    if len(parts1) > 1 or len(parts2) > 1:
        last1 = parts1[-1]
        return max(ratio(last1, p2) for p2 in parts2)
    else:
        return compare_name_part(surname1, surname2)


def compare_person_names_dual_approach(name1: str, name2: str) -> Tuple[float, str]:
    """
    Compare person names using dual approach and return max:
    1. Full name Levenshtein
    2. Sum of parts
    """
    # Extract titles
    title1, name1_clean = extract_title(name1)
    title2, name2_clean = extract_title(name2)

    # Approach 1: Full name Levenshtein
    full_score = ratio(normalize_name(name1_clean), normalize_name(name2_clean))

    # Approach 2: Sum of parts
    parsed1 = parse_full_name(name1_clean, title1)
    parsed2 = parse_full_name(name2_clean, title2)

    parts_score = 0.0
    details = []

    # Title (0.05)
    title_score, title_detail = compare_title(parsed1['title'], parsed2['title'])
    parts_score += title_score * 0.05
    details.append(title_detail)

    # Firstname (0.30)
    if parsed1['first'] and parsed2['first']:
        first_score = compare_name_part(parsed1['first'], parsed2['first'])
        parts_score += first_score * 0.30
        details.append(f"first:{first_score:.2f}")

    # Middlename (0.15)
    if parsed1['middle'] and parsed2['middle']:
        middle_score = compare_name_part(parsed1['middle'], parsed2['middle'])
        parts_score += middle_score * 0.15
        details.append(f"middle:{middle_score:.2f}")
    else:
        parts_score += 1.0 * 0.15
        details.append("middle:1.0(missing)")

    # Surname (0.50)
    if parsed1['last'] and parsed2['last']:
        surname_score = compare_compound_surname(parsed1['last'], parsed2['last'])
        parts_score += surname_score * 0.50
        details.append(f"surname:{surname_score:.2f}")

    # Return max
    if full_score > parts_score:
        return full_score, f"Full name match: {name1_clean} ~ {name2_clean}"
    else:
        return parts_score, f"Parts match: {' + '.join(details)}"


# ============================================================================
# Organization Name Comparison Functions
# ============================================================================

def normalize_org_name(name: str) -> str:
    """Normalize organization name for comparison"""
    name = name.lower()
    # Remove common suffixes
    suffixes = [
        'ltd', 'limited', 'inc', 'incorporated', 'corp', 'corporation',
        'llc', 'plc', 'sa', 'gmbh', 'ag', 'nv', 'bv', 'co', 'company',
        'pty', 'proprietary', 'holdings', 'group', 'enterprises'
    ]

    for suffix in suffixes:
        # Remove suffix with various punctuation
        name = re.sub(rf'\b{suffix}\.?\b', '', name, flags=re.IGNORECASE)

    # Remove punctuation and extra spaces
    name = re.sub(r'[.,\-_&()]', ' ', name)
    name = ' '.join(name.split())

    return name.strip()


def compare_organization_names(name1: str, name2: str) -> Tuple[float, str]:
    """
    Compare organization names using simple Levenshtein
    Organizations don't have first/middle/last names, so just compare full names
    """
    norm1 = normalize_org_name(name1)
    norm2 = normalize_org_name(name2)

    if not norm1 or not norm2:
        return 0.0, "Empty organization name"

    score = ratio(norm1, norm2)
    return score, f"Organization name: {norm1} ~ {norm2}"


# ============================================================================
# Feature Functions
# ============================================================================

def custom_name_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """
    Match names - handles both Person and Organization entities
    - Person: Dual-approach (full name + parts)
    - Organization: Simple full name comparison
    """
    query_names, result_names = type_pair(query, result, registry.name)
    if not query_names or not result_names:
        return FtResult(score=FNUL, detail=None)

    # Check if both are same type
    query_is_person = is_person(query)
    result_is_person = is_person(result)
    query_is_org = is_organization(query)
    result_is_org = is_organization(result)

    # If different entity types, return FNUL (shouldn't match Person to Organization)
    if (query_is_person and result_is_org) or (query_is_org and result_is_person):
        return FtResult(score=FNUL, detail="Different entity types")

    best_score, best_detail = FNUL, None

    for q_name in query_names:
        for r_name in result_names:
            if query_is_person and result_is_person:
                # Person matching: dual approach
                score, detail = compare_person_names_dual_approach(q_name, r_name)
            elif query_is_org and result_is_org:
                # Organization matching: simple comparison
                score, detail = compare_organization_names(q_name, r_name)
            else:
                # Generic matching for other types
                score = ratio(normalize_name(q_name), normalize_name(r_name))
                detail = f"Generic name match: {q_name} ~ {r_name}"

            if score > best_score:
                best_score, best_detail = score, detail

    return FtResult(score=best_score, detail=best_detail)


def custom_surname_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Match surnames - only applicable to Person entities"""
    if not (is_person(query) and is_person(result)):
        return FtResult(score=FNUL, detail="Not Person entities")

    query_names, result_names = type_pair(query, result, registry.name)
    if not query_names or not result_names:
        return FtResult(score=FNUL, detail=None)

    best_score, best_detail = FNUL, None
    for q_name in query_names:
        for r_name in result_names:
            _, q_clean = extract_title(q_name)
            _, r_clean = extract_title(r_name)

            q_parsed = parse_full_name(q_clean)
            r_parsed = parse_full_name(r_clean)

            if not q_parsed['last'] or not r_parsed['last']:
                continue

            # Exact match
            if normalize_name(q_parsed['last']) == normalize_name(r_parsed['last']):
                return FtResult(score=1.0, detail=f"Exact surname match: {q_parsed['last']}")

            score = compare_compound_surname(q_parsed['last'], r_parsed['last'])
            if score > best_score:
                best_score = score
                best_detail = f"Surname: {q_parsed['last']} ~ {r_parsed['last']}"

    return FtResult(score=best_score, detail=best_detail)


def custom_firstname_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Match first names - only applicable to Person entities"""
    if not (is_person(query) and is_person(result)):
        return FtResult(score=FNUL, detail="Not Person entities")

    query_names, result_names = type_pair(query, result, registry.name)
    if not query_names or not result_names:
        return FtResult(score=FNUL, detail=None)

    best_score, best_detail = FNUL, None
    for q_name in query_names:
        for r_name in result_names:
            _, q_clean = extract_title(q_name)
            _, r_clean = extract_title(r_name)

            q_parsed = parse_full_name(q_clean)
            r_parsed = parse_full_name(r_clean)

            if not q_parsed['first'] or not r_parsed['first']:
                continue

            # Exact match
            if normalize_name(q_parsed['first']) == normalize_name(r_parsed['first']):
                return FtResult(score=1.0, detail=f"Exact firstname match: {q_parsed['first']}")

            score = compare_name_part(q_parsed['first'], r_parsed['first'])
            if score > best_score:
                best_score = score
                best_detail = f"Firstname: {q_parsed['first']} ~ {r_parsed['first']}"

    return FtResult(score=best_score, detail=best_detail)


def custom_middlename_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Match middle names - only applicable to Person entities"""
    if not (is_person(query) and is_person(result)):
        return FtResult(score=FNUL, detail="Not Person entities")

    query_names, result_names = type_pair(query, result, registry.name)
    if not query_names or not result_names:
        return FtResult(score=FNUL, detail=None)

    best_score, best_detail = FNUL, None
    for q_name in query_names:
        for r_name in result_names:
            _, q_clean = extract_title(q_name)
            _, r_clean = extract_title(r_name)

            q_parsed = parse_full_name(q_clean)
            r_parsed = parse_full_name(r_clean)

            if not q_parsed['middle'] or not r_parsed['middle']:
                continue

            # Exact match
            if normalize_name(q_parsed['middle']) == normalize_name(r_parsed['middle']):
                return FtResult(score=1.0, detail=f"Exact middlename match: {q_parsed['middle']}")

            score = compare_name_part(q_parsed['middle'], r_parsed['middle'])
            if score > best_score:
                best_score = score
                best_detail = f"Middlename: {q_parsed['middle']} ~ {r_parsed['middle']}"

    return FtResult(score=best_score, detail=best_detail)


def custom_title_mismatch(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Penalty for title mismatch - only applicable to Person entities"""
    if not (is_person(query) and is_person(result)):
        return FtResult(score=0.0, detail="Not Person entities")

    query_names, result_names = type_pair(query, result, registry.name)
    if not query_names or not result_names:
        return FtResult(score=0.0, detail=None)

    q_title, r_title = None, None
    for q_name in query_names:
        q_title, _ = extract_title(q_name)
        if q_title:
            break

    for r_name in result_names:
        r_title, _ = extract_title(r_name)
        if r_title:
            break

    if q_title and r_title and q_title != r_title:
        return FtResult(score=1.0, detail=f"Title mismatch: {q_title} vs {r_title}")

    return FtResult(score=0.0, detail=None)
