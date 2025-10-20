"""Identifier matching functions (tax ID, registration numbers) for custom_v1 algorithm"""
from rigour.ids import StrictFormat
from followthemoney import E
from followthemoney.types import registry

from nomenklatura.matching.types import FtResult, ScoringConfig
from nomenklatura.matching.util import type_pair, FNUL
from nomenklatura.matching.compare.util import clean_map


def custom_identifier_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """
    Match tax IDs, registration numbers, and other identifiers between entities.
    Applies primarily to Organization entities, but also works for Person entities.
    """
    query_ids_, result_ids_ = type_pair(query, result, registry.identifier)

    if not query_ids_ or not result_ids_:
        return FtResult(score=FNUL, detail=None)

    # Normalize identifiers for comparison
    query_ids = clean_map(query_ids_, StrictFormat.normalize)
    result_ids = clean_map(result_ids_, StrictFormat.normalize)

    common = query_ids.intersection(result_ids)
    if len(common) > 0:
        ids_str = ", ".join(sorted(common)[:3])  # Show first 3
        if len(common) > 3:
            ids_str += f" (+{len(common) - 3} more)"
        detail = f"Matched identifiers: {ids_str}"
        return FtResult(score=1.0, detail=detail)

    return FtResult(score=FNUL, detail=None)
