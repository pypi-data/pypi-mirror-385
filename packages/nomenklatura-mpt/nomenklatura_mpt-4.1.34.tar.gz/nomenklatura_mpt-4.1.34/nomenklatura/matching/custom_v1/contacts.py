"""Contact matching functions (email, phone) for custom_v1 algorithm"""
from followthemoney import E
from followthemoney.types import registry

from nomenklatura.matching.types import FtResult, ScoringConfig
from nomenklatura.matching.util import type_pair, FNUL


def custom_email_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """
    Match email addresses between entities.
    Applies to both Person and Organization entities.
    """
    query_emails, result_emails = type_pair(query, result, registry.email)

    if not query_emails or not result_emails:
        return FtResult(score=FNUL, detail=None)

    common = query_emails.intersection(result_emails)
    if len(common) > 0:
        emails_str = ", ".join(sorted(common)[:3])  # Show first 3
        if len(common) > 3:
            emails_str += f" (+{len(common) - 3} more)"
        detail = f"Matched emails: {emails_str}"
        return FtResult(score=1.0, detail=detail)

    return FtResult(score=FNUL, detail=None)


def custom_phone_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """
    Match phone numbers between entities.
    Applies to both Person and Organization entities.
    """
    query_phones, result_phones = type_pair(query, result, registry.phone)

    if not query_phones or not result_phones:
        return FtResult(score=FNUL, detail=None)

    common = query_phones.intersection(result_phones)
    if len(common) > 0:
        phones_str = ", ".join(sorted(common)[:3])  # Show first 3
        if len(common) > 3:
            phones_str += f" (+{len(common) - 3} more)"
        detail = f"Matched phones: {phones_str}"
        return FtResult(score=1.0, detail=detail)

    return FtResult(score=FNUL, detail=None)
