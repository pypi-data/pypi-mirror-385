"""Attribute matching functions for CustomV1 algorithm (gender, nationality, country)"""
from typing import Set

from followthemoney.proxy import E
from followthemoney.types import registry

from nomenklatura.matching.types import FtResult, ScoringConfig
from nomenklatura.matching.util import props_pair, type_pair


def custom_gender_bonus(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Bonus for gender match"""
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        return FtResult(score=1.0, detail="Not Person entities")

    query_genders, result_genders = props_pair(query, result, ["gender"])
    if not query_genders or not result_genders:
        return FtResult(score=1.0, detail="Gender missing - full points")

    for q_gender in query_genders:
        for r_gender in result_genders:
            if not q_gender or not r_gender:
                continue

            if q_gender.lower() == r_gender.lower():
                return FtResult(score=1.0, detail=f"Gender match: {q_gender}")

    return FtResult(score=0.0, detail="Gender mismatch")


def custom_gender_mismatch(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Penalty for gender mismatch"""
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        return FtResult(score=0.0, detail="Not Person entities")

    query_genders, result_genders = props_pair(query, result, ["gender"])
    if not query_genders or not result_genders:
        return FtResult(score=0.0, detail=None)

    for q_gender in query_genders:
        for r_gender in result_genders:
            if not q_gender or not r_gender:
                continue

            if q_gender.lower() != r_gender.lower():
                return FtResult(score=1.0, detail=f"Gender mismatch: {q_gender} vs {r_gender}")

    return FtResult(score=0.0, detail=None)


def custom_nationality_bonus(query: E, result: E, config: ScoringConfig) -> FtResult:
    """
    Bonus for nationality/country match

    Logic:
    1. Check nationality first:
       - Same nationality: 1.0
       - Different nationality: 0.0
    2. If no nationality, check country:
       - No country: 1.0
       - Same country: 1.0
       - Different countries: 0.5
    """
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        return FtResult(score=1.0, detail="Not Person entities")

    # Get nationality and country
    qv_nat_list, rv_nat_list = type_pair(query, result, registry.country)
    qv_country_list, rv_country_list = props_pair(query, result, ["country"])

    qv_nat = set(qv_nat_list) if qv_nat_list else set()
    rv_nat = set(rv_nat_list) if rv_nat_list else set()
    qv_country = set(qv_country_list) if qv_country_list else set()
    rv_country = set(rv_country_list) if rv_country_list else set()

    # Step 1: Check nationality
    if qv_nat and rv_nat:
        intersection = qv_nat.intersection(rv_nat)
        if intersection:
            return FtResult(score=1.0, detail=f"Nationality match: {intersection}")
        else:
            return FtResult(score=0.0, detail=f"Nationality mismatch: {qv_nat} vs {rv_nat}")

    # Step 2: Check country
    if not qv_country and not rv_country:
        return FtResult(score=1.0, detail="No country - full points")

    if qv_country and rv_country:
        intersection = qv_country.intersection(rv_country)
        if intersection:
            return FtResult(score=1.0, detail=f"Country match: {intersection}")
        else:
            return FtResult(score=0.5, detail=f"Different countries: {qv_country} vs {rv_country}")

    return FtResult(score=1.0, detail="Partial country info - full points")


def custom_country_mismatch(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Penalty for country/nationality mismatch"""
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        return FtResult(score=0.0, detail="Not Person entities")

    # Get nationality and country
    qv_nat_list, rv_nat_list = type_pair(query, result, registry.country)
    qv_country_list, rv_country_list = props_pair(query, result, ["country"])

    qv_nat = set(qv_nat_list) if qv_nat_list else set()
    rv_nat = set(rv_nat_list) if rv_nat_list else set()
    qv_country = set(qv_country_list) if qv_country_list else set()
    rv_country = set(rv_country_list) if rv_country_list else set()

    # Combine both sets
    qv = qv_nat.union(qv_country)
    rv = rv_nat.union(rv_country)

    # Only apply penalty if both have countries AND they don't match
    if qv and rv:
        intersection = qv.intersection(rv)
        if not intersection:
            return FtResult(score=1.0, detail=f"Different countries: {qv} / {rv}")

    return FtResult(score=0.0, detail=None)
