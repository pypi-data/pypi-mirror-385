from typing import List, Dict
import re
from Levenshtein import ratio

from nomenklatura.matching.types import Feature, HeuristicAlgorithm, FtResult, ScoringConfig
from nomenklatura.matching.util import props_pair, type_pair, FNUL
from followthemoney.proxy import E
from followthemoney.types import registry


class CustomV1Config:
    """Static configuration for CustomV1 matching algorithm"""
    # Name feature weights (best-of selection, total contributes 0.75 to final score)
    FULLNAME_WEIGHT = 0.50
    SURNAME_WEIGHT = 0.15
    FIRSTNAME_WEIGHT = 0.10
    MIDDLENAME_WEIGHT = 0.10
    
    # DOB weights (additive, total: 0.15)
    DOB_YEAR_WEIGHT = 0.10
    DOB_MONTH_WEIGHT = 0.03
    DOB_DAY_WEIGHT = 0.02
    
    # Gender/Nationality bonus (additive, total: 0.10)
    GENDER_BONUS_WEIGHT = 0.05
    NATIONALITY_BONUS_WEIGHT = 0.05
    
    # Penalties
    DOB_YEAR_MISMATCH_PENALTY = -0.20
    GENDER_MISMATCH_PENALTY = -0.10
    COUNTRY_MISMATCH_PENALTY = -0.15


class NameParser:
    """Parse and clean names"""
    
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
    
    @classmethod
    def extract_title(cls, name: str) -> tuple:
        """Extract title from name"""
        parts = name.strip().split()
        if not parts:
            return None, name
        
        first_part = parts[0].lower()
        if first_part in cls.TITLES:
            normalized_title = cls.TITLES[first_part]
            remaining_name = ' '.join(parts[1:])
            return normalized_title, remaining_name
        
        return None, name
    
    @classmethod
    def remove_title(cls, name: str) -> str:
        """Remove title from name"""
        _, name_without_title = cls.extract_title(name)
        return name_without_title
    
    @classmethod
    def normalize_name(cls, name: str) -> str:
        """Normalize name for comparison"""
        name = ' '.join(name.split()).lower()
        name = re.sub(r'[.,\-_]', ' ', name)
        name = ' '.join(name.split())
        return name
    
    @classmethod
    def parse_compound_name(cls, name: str) -> List[str]:
        """Parse compound names"""
        parts = re.split(r'[-\s]+', name.lower())
        return [p for p in parts if p]
    
    @classmethod
    def parse_full_name(cls, full_name: str) -> Dict[str, str]:
        """
        Parse a full name into components
        Returns dict with 'first', 'middle', 'last' keys
        """
        # Remove title first
        title, name_without_title = cls.extract_title(full_name)
        
        # Split into parts
        parts = name_without_title.strip().split()
        
        result = {'first': None, 'middle': None, 'last': None, 'title': title}
        
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


# Feature functions
def custom_name_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Match full names with compound surname support"""
    print(f"\n[custom_name_match] INPUT:")
    print(f"  Query schema: {query.schema.name}, ID: {query.id}")
    print(f"  Result schema: {result.schema.name}, ID: {result.id}")
    
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        print(f"[custom_name_match] Not Person entities, returning FNUL")
        result_obj = FtResult(score=FNUL, detail="Not Person entities")
        print(f"[custom_name_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    query_names, result_names = type_pair(query, result, registry.name)
    print(f"  Query names: {query_names}")
    print(f"  Result names: {result_names}")
    
    if not query_names or not result_names:
        print(f"[custom_name_match] No names to compare, returning FNUL")
        result_obj = FtResult(score=FNUL, detail=None)
        print(f"[custom_name_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    best_score = FNUL
    best_match = None
    
    for q_name in query_names:
        for r_name in result_names:
            print(f"  Comparing: '{q_name}' vs '{r_name}'")
            
            q_norm = NameParser.normalize_name(q_name)
            r_norm = NameParser.normalize_name(r_name)
            
            # Exact match
            if q_norm == r_norm:
                print(f"    Exact match!")
                result_obj = FtResult(score=1.0, detail=f"Exact name match: {q_name}")
                print(f"[custom_name_match] OUTPUT: score={result_obj.score}")
                return result_obj
            
            # Levenshtein on full names
            score = ratio(q_norm, r_norm)
            print(f"    Full name Levenshtein: {score:.4f}")
            
            if score > best_score:
                best_score = score
                best_match = f"Name match: {q_name} ~ {r_name}"
    
    result_obj = FtResult(score=best_score, detail=best_match)
    print(f"[custom_name_match] OUTPUT: score={result_obj.score}, detail={result_obj.detail}")
    return result_obj


def custom_surname_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Match surnames (last names) with compound support"""
    print(f"\n[custom_surname_match] INPUT:")
    print(f"  Query schema: {query.schema.name}, ID: {query.id}")
    print(f"  Result schema: {result.schema.name}, ID: {result.id}")
    
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        print(f"[custom_surname_match] Not Person entities, returning FNUL")
        result_obj = FtResult(score=FNUL, detail="Not Person entities")
        print(f"[custom_surname_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    query_names, result_names = type_pair(query, result, registry.name)
    print(f"  Query names: {query_names}")
    print(f"  Result names: {result_names}")
    
    if not query_names or not result_names:
        print(f"[custom_surname_match] No names to compare, returning FNUL")
        result_obj = FtResult(score=FNUL, detail=None)
        print(f"[custom_surname_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    best_score = FNUL
    best_match = None
    
    for q_name in query_names:
        for r_name in result_names:
            q_parsed = NameParser.parse_full_name(q_name)
            r_parsed = NameParser.parse_full_name(r_name)
            
            q_surname = q_parsed['last']
            r_surname = r_parsed['last']
            
            print(f"  Comparing surnames: '{q_surname}' vs '{r_surname}'")
            
            if not q_surname or not r_surname:
                continue
            
            q_parts = NameParser.parse_compound_name(q_surname)
            r_parts = NameParser.parse_compound_name(r_surname)
            print(f"    Query parts: {q_parts}, Result parts: {r_parts}")
            
            if NameParser.normalize_name(q_surname) == NameParser.normalize_name(r_surname):
                print(f"    Exact surname match!")
                result_obj = FtResult(score=1.0, detail=f"Exact surname match: {q_surname}")
                print(f"[custom_surname_match] OUTPUT: score={result_obj.score}")
                return result_obj
            
            if len(q_parts) > 1 or len(r_parts) > 1:
                if q_parts and r_parts:
                    last_q = q_parts[-1]
                    max_score = max(ratio(last_q, rp) for rp in r_parts)
                    print(f"    Compound score: {max_score:.4f}")
                    if max_score > best_score:
                        best_score = max_score
                        best_match = f"Compound surname: {q_surname} ~ {r_surname}"
            else:
                score = ratio(
                    NameParser.normalize_name(q_surname),
                    NameParser.normalize_name(r_surname)
                )
                print(f"    Simple surname score: {score:.4f}")
                if score > best_score:
                    best_score = score
                    best_match = f"Surname: {q_surname} ~ {r_surname}"
    
    result_obj = FtResult(score=best_score, detail=best_match)
    print(f"[custom_surname_match] OUTPUT: score={result_obj.score}, detail={result_obj.detail}")
    return result_obj


def custom_firstname_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Match first names with title removal"""
    print(f"\n[custom_firstname_match] INPUT:")
    print(f"  Query schema: {query.schema.name}, ID: {query.id}")
    print(f"  Result schema: {result.schema.name}, ID: {result.id}")
    
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        print(f"[custom_firstname_match] Not Person entities, returning FNUL")
        result_obj = FtResult(score=FNUL, detail="Not Person entities")
        print(f"[custom_firstname_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    query_names, result_names = type_pair(query, result, registry.name)
    print(f"  Query names: {query_names}")
    print(f"  Result names: {result_names}")
    
    if not query_names or not result_names:
        print(f"[custom_firstname_match] No names to compare, returning FNUL")
        result_obj = FtResult(score=FNUL, detail=None)
        print(f"[custom_firstname_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    best_score = FNUL
    best_match = None
    
    for q_name in query_names:
        for r_name in result_names:
            q_parsed = NameParser.parse_full_name(q_name)
            r_parsed = NameParser.parse_full_name(r_name)
            
            q_first = q_parsed['first']
            r_first = r_parsed['first']
            
            print(f"  Comparing first names: '{q_first}' vs '{r_first}'")
            
            if not q_first or not r_first:
                continue
            
            if NameParser.normalize_name(q_first) == NameParser.normalize_name(r_first):
                print(f"    Exact firstname match!")
                result_obj = FtResult(score=1.0, detail=f"Exact firstname match: {q_first}")
                print(f"[custom_firstname_match] OUTPUT: score={result_obj.score}")
                return result_obj
            
            score = ratio(
                NameParser.normalize_name(q_first),
                NameParser.normalize_name(r_first)
            )
            print(f"    Firstname score: {score:.4f}")
            if score > best_score:
                best_score = score
                best_match = f"Firstname: {q_first} ~ {r_first}"
    
    result_obj = FtResult(score=best_score, detail=best_match)
    print(f"[custom_firstname_match] OUTPUT: score={result_obj.score}, detail={result_obj.detail}")
    return result_obj


def custom_middlename_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Match middle names"""
    print(f"\n[custom_middlename_match] INPUT:")
    print(f"  Query schema: {query.schema.name}, ID: {query.id}")
    print(f"  Result schema: {result.schema.name}, ID: {result.id}")
    
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        print(f"[custom_middlename_match] Not Person entities, returning FNUL")
        result_obj = FtResult(score=FNUL, detail="Not Person entities")
        print(f"[custom_middlename_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    query_names, result_names = type_pair(query, result, registry.name)
    print(f"  Query names: {query_names}")
    print(f"  Result names: {result_names}")
    
    if not query_names or not result_names:
        print(f"[custom_middlename_match] No names to compare, returning FNUL")
        result_obj = FtResult(score=FNUL, detail=None)
        print(f"[custom_middlename_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    best_score = FNUL
    best_match = None
    
    for q_name in query_names:
        for r_name in result_names:
            q_parsed = NameParser.parse_full_name(q_name)
            r_parsed = NameParser.parse_full_name(r_name)
            
            q_middle = q_parsed['middle']
            r_middle = r_parsed['middle']
            
            print(f"  Comparing middle names: '{q_middle}' vs '{r_middle}'")
            
            if not q_middle or not r_middle:
                print(f"    Middle name missing in one or both entities")
                continue
            
            if NameParser.normalize_name(q_middle) == NameParser.normalize_name(r_middle):
                print(f"    Exact middlename match!")
                result_obj = FtResult(score=1.0, detail=f"Exact middlename match: {q_middle}")
                print(f"[custom_middlename_match] OUTPUT: score={result_obj.score}")
                return result_obj
            
            score = ratio(
                NameParser.normalize_name(q_middle),
                NameParser.normalize_name(r_middle)
            )
            print(f"    Middlename score: {score:.4f}")
            if score > best_score:
                best_score = score
                best_match = f"Middlename: {q_middle} ~ {r_middle}"
    
    result_obj = FtResult(score=best_score, detail=best_match)
    print(f"[custom_middlename_match] OUTPUT: score={result_obj.score}, detail={result_obj.detail}")
    return result_obj


def custom_dob_year_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Match DOB years"""
    print(f"\n[custom_dob_year_match] INPUT:")
    print(f"  Query schema: {query.schema.name}, ID: {query.id}")
    print(f"  Result schema: {result.schema.name}, ID: {result.id}")
    
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        print(f"[custom_dob_year_match] Not Person entities, returning 1.0")
        result_obj = FtResult(score=1.0, detail="Not Person entities")
        print(f"[custom_dob_year_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    query_dobs, result_dobs = props_pair(query, result, ["birthDate"])
    print(f"  Query DOBs: {query_dobs}")
    print(f"  Result DOBs: {result_dobs}")
    
    if not query_dobs or not result_dobs:
        print(f"[custom_dob_year_match] No DOBs to compare, returning 1.0 (neutral)")
        result_obj = FtResult(score=1.0, detail="No DOB to compare")
        print(f"[custom_dob_year_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    for q_dob, r_dob in zip(query_dobs, result_dobs):
        print(f"  Comparing DOBs: '{q_dob}' vs '{r_dob}'")
        
        if not q_dob or not r_dob:
            continue
        
        q_year = q_dob.split('-')[0] if '-' in q_dob else q_dob[:4]
        r_year = r_dob.split('-')[0] if '-' in r_dob else r_dob[:4]
        print(f"    Years: '{q_year}' vs '{r_year}'")
        
        if q_year == r_year:
            print(f"    Year match!")
            result_obj = FtResult(score=1.0, detail=f"DOB year match: {q_year}")
            print(f"[custom_dob_year_match] OUTPUT: score={result_obj.score}")
            return result_obj
    
    print(f"  Year mismatch")
    result_obj = FtResult(score=FNUL, detail="DOB year mismatch")
    print(f"[custom_dob_year_match] OUTPUT: score={result_obj.score}")
    return result_obj


def custom_dob_month_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Match DOB months"""
    print(f"\n[custom_dob_month_match] INPUT:")
    print(f"  Query schema: {query.schema.name}, ID: {query.id}")
    print(f"  Result schema: {result.schema.name}, ID: {result.id}")
    
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        print(f"[custom_dob_month_match] Not Person entities, returning 1.0")
        result_obj = FtResult(score=1.0, detail="Not Person entities")
        print(f"[custom_dob_month_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    query_dobs, result_dobs = props_pair(query, result, ["birthDate"])
    print(f"  Query DOBs: {query_dobs}")
    print(f"  Result DOBs: {result_dobs}")
    
    if not query_dobs or not result_dobs:
        print(f"[custom_dob_month_match] No DOBs to compare, returning 1.0 (neutral)")
        result_obj = FtResult(score=1.0, detail="No DOB to compare")
        print(f"[custom_dob_month_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    for q_dob, r_dob in zip(query_dobs, result_dobs):
        print(f"  Comparing DOBs: '{q_dob}' vs '{r_dob}'")
        
        if not q_dob or not r_dob:
            continue
        
        q_parts = q_dob.split('-')
        r_parts = r_dob.split('-')
        print(f"    Parts: {q_parts} vs {r_parts}")
        
        if len(q_parts) >= 1 and len(r_parts) >= 1:
            if q_parts[0] != r_parts[0]:
                print(f"    Year mismatch")
                result_obj = FtResult(score=FNUL, detail="Year mismatch")
                print(f"[custom_dob_month_match] OUTPUT: score={result_obj.score}")
                return result_obj
        
        if len(q_parts) >= 2 and len(r_parts) >= 2:
            if q_parts[1] == r_parts[1]:
                print(f"    Month match!")
                result_obj = FtResult(score=1.0, detail=f"DOB month match: {q_parts[0]}-{q_parts[1]}")
                print(f"[custom_dob_month_match] OUTPUT: score={result_obj.score}")
                return result_obj
    
    print(f"  Month mismatch")
    result_obj = FtResult(score=FNUL, detail="DOB month mismatch")
    print(f"[custom_dob_month_match] OUTPUT: score={result_obj.score}")
    return result_obj


def custom_dob_day_match(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Match DOB days"""
    print(f"\n[custom_dob_day_match] INPUT:")
    print(f"  Query schema: {query.schema.name}, ID: {query.id}")
    print(f"  Result schema: {result.schema.name}, ID: {result.id}")
    
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        print(f"[custom_dob_day_match] Not Person entities, returning 1.0")
        result_obj = FtResult(score=1.0, detail="Not Person entities")
        print(f"[custom_dob_day_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    query_dobs, result_dobs = props_pair(query, result, ["birthDate"])
    print(f"  Query DOBs: {query_dobs}")
    print(f"  Result DOBs: {result_dobs}")
    
    if not query_dobs or not result_dobs:
        print(f"[custom_dob_day_match] No DOBs to compare, returning 1.0 (neutral)")
        result_obj = FtResult(score=1.0, detail="No DOB to compare")
        print(f"[custom_dob_day_match] OUTPUT: score={result_obj.score}")
        return result_obj
    
    for q_dob, r_dob in zip(query_dobs, result_dobs):
        print(f"  Comparing DOBs: '{q_dob}' vs '{r_dob}'")
        
        if not q_dob or not r_dob:
            continue
        
        q_parts = q_dob.split('-')
        r_parts = r_dob.split('-')
        print(f"    Parts: {q_parts} vs {r_parts}")
        
        if len(q_parts) >= 2 and len(r_parts) >= 2:
            if q_parts[0] != r_parts[0] or q_parts[1] != r_parts[1]:
                print(f"    Year/month mismatch")
                result_obj = FtResult(score=FNUL, detail="Year/month mismatch")
                print(f"[custom_dob_day_match] OUTPUT: score={result_obj.score}")
                return result_obj
        
        if len(q_parts) >= 3 and len(r_parts) >= 3:
            if q_parts[2] == r_parts[2]:
                print(f"    Full DOB match!")
                result_obj = FtResult(score=1.0, detail=f"Full DOB match: {q_dob}")
                print(f"[custom_dob_day_match] OUTPUT: score={result_obj.score}")
                return result_obj
    
    print(f"  Day mismatch")
    result_obj = FtResult(score=FNUL, detail="DOB day mismatch")
    print(f"[custom_dob_day_match] OUTPUT: score={result_obj.score}")
    return result_obj


def custom_gender_bonus(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Bonus for gender match (not a penalty)"""
    print(f"\n[custom_gender_bonus] INPUT:")
    print(f"  Query schema: {query.schema.name}, ID: {query.id}")
    print(f"  Result schema: {result.schema.name}, ID: {result.id}")
    
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        print(f"[custom_gender_bonus] Not Person entities, returning 1.0")
        result_obj = FtResult(score=1.0, detail="Not Person entities")
        print(f"[custom_gender_bonus] OUTPUT: score={result_obj.score}")
        return result_obj
    
    query_genders, result_genders = props_pair(query, result, ["gender"])
    print(f"  Query genders: {query_genders}")
    print(f"  Result genders: {result_genders}")
    
    if not query_genders or not result_genders:
        print(f"[custom_gender_bonus] Gender missing, returning 1.0 (neutral - no bonus, no penalty)")
        result_obj = FtResult(score=1.0, detail="Gender missing")
        print(f"[custom_gender_bonus] OUTPUT: score={result_obj.score}")
        return result_obj
    
    for q_gender, r_gender in zip(query_genders, result_genders):
        print(f"  Comparing: '{q_gender}' vs '{r_gender}'")
        
        if not q_gender or not r_gender:
            continue
        
        if q_gender.lower() == r_gender.lower():
            print(f"  Gender match - giving bonus!")
            result_obj = FtResult(score=1.0, detail=f"Gender match: {q_gender}")
            print(f"[custom_gender_bonus] OUTPUT: score={result_obj.score}")
            return result_obj
    
    print(f"  Gender mismatch - neutral (no bonus)")
    result_obj = FtResult(score=0.0, detail="Gender mismatch")
    print(f"[custom_gender_bonus] OUTPUT: score={result_obj.score}")
    return result_obj


def custom_nationality_bonus(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Bonus for nationality/country match - any match counts"""
    print(f"\n[custom_nationality_bonus] INPUT:")
    print(f"  Query schema: {query.schema.name}, ID: {query.id}")
    print(f"  Result schema: {result.schema.name}, ID: {result.id}")
    
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        print(f"[custom_nationality_bonus] Not Person entities, returning 1.0")
        result_obj = FtResult(score=1.0, detail="Not Person entities")
        print(f"[custom_nationality_bonus] OUTPUT: score={result_obj.score}")
        return result_obj
    
    # Get nationality values
    qv_nat, rv_nat = type_pair(query, result, registry.country)
    # Get country values
    qv_country, rv_country = props_pair(query, result, ["country"])
    
    # Combine both sets
    qv = qv_nat.union(qv_country)
    rv = rv_nat.union(rv_country)
    
    print(f"  Query countries (nationality + country): {qv}")
    print(f"  Result countries (nationality + country): {rv}")
    
    # If either side is missing, neutral (no bonus)
    if len(qv) == 0 or len(rv) == 0:
        print(f"[custom_nationality_bonus] Nationality/country missing, returning 1.0 (neutral)")
        result_obj = FtResult(score=1.0, detail="Nationality/country missing")
        print(f"[custom_nationality_bonus] OUTPUT: score={result_obj.score}")
        return result_obj
    
    # Check if any country matches
    intersection = set(qv).intersection(rv)
    
    if len(intersection) > 0:
        print(f"  Country/nationality match found: {intersection}")
        result_obj = FtResult(score=1.0, detail=f"Nationality match: {intersection}")
        print(f"[custom_nationality_bonus] OUTPUT: score={result_obj.score}")
        return result_obj
    else:
        print(f"  No country/nationality match")
        result_obj = FtResult(score=0.0, detail=None)
        print(f"[custom_nationality_bonus] OUTPUT: score={result_obj.score}")
        return result_obj


def custom_gender_mismatch(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Penalty for gender mismatch"""
    print(f"\n[custom_gender_mismatch] INPUT:")
    print(f"  Query schema: {query.schema.name}, ID: {query.id}")
    print(f"  Result schema: {result.schema.name}, ID: {result.id}")
    
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        print(f"[custom_gender_mismatch] Not Person entities, returning 0.0")
        result_obj = FtResult(score=0.0, detail="Not Person entities")
        print(f"[custom_gender_mismatch] OUTPUT: score={result_obj.score}")
        return result_obj
    
    query_genders, result_genders = props_pair(query, result, ["gender"])
    print(f"  Query genders: {query_genders}")
    print(f"  Result genders: {result_genders}")
    
    if not query_genders or not result_genders:
        print(f"[custom_gender_mismatch] No genders to compare, returning 0.0 (no penalty)")
        result_obj = FtResult(score=0.0, detail=None)
        print(f"[custom_gender_mismatch] OUTPUT: score={result_obj.score}")
        return result_obj
    
    for q_gender, r_gender in zip(query_genders, result_genders):
        print(f"  Comparing: '{q_gender}' vs '{r_gender}'")
        
        if not q_gender or not r_gender:
            continue
        
        if q_gender.lower() != r_gender.lower():
            print(f"  Gender mismatch!")
            result_obj = FtResult(score=1.0, detail=f"Gender mismatch: {q_gender} vs {r_gender}")
            print(f"[custom_gender_mismatch] OUTPUT: score={result_obj.score}")
            return result_obj
    
    print(f"  Gender match")
    result_obj = FtResult(score=0.0, detail=None)
    print(f"[custom_gender_mismatch] OUTPUT: score={result_obj.score}")
    return result_obj


def custom_country_mismatch(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Penalty for country/nationality mismatch - both entities linked to different countries"""
    print(f"\n[custom_country_mismatch] INPUT:")
    print(f"  Query schema: {query.schema.name}, ID: {query.id}")
    print(f"  Result schema: {result.schema.name}, ID: {result.id}")
    
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        print(f"[custom_country_mismatch] Not Person entities, returning 0.0")
        result_obj = FtResult(score=0.0, detail="Not Person entities")
        print(f"[custom_country_mismatch] OUTPUT: score={result_obj.score}")
        return result_obj
    
    # Get nationality values
    qv_nat, rv_nat = type_pair(query, result, registry.country)
    # Get country values
    qv_country, rv_country = props_pair(query, result, ["country"])
    
    # Combine both sets
    qv = qv_nat.union(qv_country)
    rv = rv_nat.union(rv_country)
    
    print(f"  Query countries (nationality + country): {qv}")
    print(f"  Result countries (nationality + country): {rv}")
    
    # Only apply penalty if both have countries AND they don't match
    if len(qv) > 0 and len(rv) > 0:
        intersection = set(qv).intersection(rv)
        if len(intersection) == 0:
            detail = f"Different countries: {qv} / {rv}"
            print(f"  Country/nationality mismatch - applying penalty!")
            print(f"  {detail}")
            result_obj = FtResult(score=1.0, detail=detail)
            print(f"[custom_country_mismatch] OUTPUT: score={result_obj.score}")
            return result_obj
        else:
            print(f"  Countries match: {intersection} - no penalty")
    else:
        print(f"  One or both sides missing country - no penalty")
    
    result_obj = FtResult(score=0.0, detail=None)
    print(f"[custom_country_mismatch] OUTPUT: score={result_obj.score}")
    return result_obj


def custom_dob_year_mismatch(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Penalty for DOB year mismatch"""
    print(f"\n[custom_dob_year_mismatch] INPUT:")
    print(f"  Query schema: {query.schema.name}, ID: {query.id}")
    print(f"  Result schema: {result.schema.name}, ID: {result.id}")
    
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        print(f"[custom_dob_year_mismatch] Not Person entities, returning 0.0")
        result_obj = FtResult(score=0.0, detail="Not Person entities")
        print(f"[custom_dob_year_mismatch] OUTPUT: score={result_obj.score}")
        return result_obj
    
    query_dobs, result_dobs = props_pair(query, result, ["birthDate"])
    print(f"  Query DOBs: {query_dobs}")
    print(f"  Result DOBs: {result_dobs}")
    
    if not query_dobs or not result_dobs:
        print(f"[custom_dob_year_mismatch] No DOBs to compare, returning 0.0 (no penalty)")
        result_obj = FtResult(score=0.0, detail=None)
        print(f"[custom_dob_year_mismatch] OUTPUT: score={result_obj.score}")
        return result_obj
    
    for q_dob, r_dob in zip(query_dobs, result_dobs):
        print(f"  Comparing DOBs: '{q_dob}' vs '{r_dob}'")
        
        if not q_dob or not r_dob:
            continue
        
        q_year = q_dob.split('-')[0] if '-' in q_dob else q_dob[:4]
        r_year = r_dob.split('-')[0] if '-' in r_dob else r_dob[:4]
        print(f"    Years: '{q_year}' vs '{r_year}'")
        
        if q_year != r_year:
            print(f"  Year mismatch!")
            result_obj = FtResult(score=1.0, detail=f"DOB year mismatch: {q_year} vs {r_year}")
            print(f"[custom_dob_year_mismatch] OUTPUT: score={result_obj.score}")
            return result_obj
    
    print(f"  Year match")
    result_obj = FtResult(score=0.0, detail=None)
    print(f"[custom_dob_year_mismatch] OUTPUT: score={result_obj.score}")
    return result_obj


class CustomV1(HeuristicAlgorithm):
    """
    Custom matching algorithm optimized for person matching with dynamic weight adjustment
    """
    
    NAME = "custom-v1"
    
    features = [
        # Name matching features (best-of these will be used)
        Feature(func=custom_name_match, weight=CustomV1Config.FULLNAME_WEIGHT),
        Feature(func=custom_surname_match, weight=CustomV1Config.SURNAME_WEIGHT),
        Feature(func=custom_firstname_match, weight=CustomV1Config.FIRSTNAME_WEIGHT),
        Feature(func=custom_middlename_match, weight=CustomV1Config.MIDDLENAME_WEIGHT),
        
        # DOB matching features (additive)
        Feature(func=custom_dob_year_match, weight=CustomV1Config.DOB_YEAR_WEIGHT),
        Feature(func=custom_dob_month_match, weight=CustomV1Config.DOB_MONTH_WEIGHT),
        Feature(func=custom_dob_day_match, weight=CustomV1Config.DOB_DAY_WEIGHT),
        
        # Gender/Nationality bonus (additive)
        Feature(func=custom_gender_bonus, weight=CustomV1Config.GENDER_BONUS_WEIGHT),
        Feature(func=custom_nationality_bonus, weight=CustomV1Config.NATIONALITY_BONUS_WEIGHT),
        
        # Qualifiers (penalties)
        Feature(func=custom_dob_year_mismatch, weight=CustomV1Config.DOB_YEAR_MISMATCH_PENALTY, qualifier=True),
        Feature(func=custom_gender_mismatch, weight=CustomV1Config.GENDER_MISMATCH_PENALTY, qualifier=True),
        Feature(func=custom_country_mismatch, weight=CustomV1Config.COUNTRY_MISMATCH_PENALTY, qualifier=True),
    ]
    
    @classmethod
    def compute_score(
        cls, scores: Dict[str, float], weights: Dict[str, float]
    ) -> float:
        """
        Compute final score with hybrid approach:
        - Best-of for name features (fullname, surname, firstname, middlename)
        - Additive for other features (DOB, gender, nationality)
        - Dynamic weight redistribution when middle name is missing
        """
        print(f"\n[compute_score] INPUT:")
        print(f"  Scores: {scores}")
        print(f"  Weights: {weights}")
        
        # Check if middle name is missing (FNUL) in either query or result
        middlename_score = scores.get('custom_middlename_match', FNUL)
        middlename_missing = (middlename_score == FNUL)
        
        print(f"  Middle name score: {middlename_score:.4f}, missing: {middlename_missing}")
        
        # Adjust name feature weights if middle name is missing
        adjusted_weights = weights.copy()
        
        if middlename_missing:
            print(f"  Middle name missing - redistributing weight")
            
            # Get base weights
            middlename_weight = CustomV1Config.MIDDLENAME_WEIGHT  # 0.10
            surname_weight = CustomV1Config.SURNAME_WEIGHT        # 0.15
            firstname_weight = CustomV1Config.FIRSTNAME_WEIGHT    # 0.10
            
            # Calculate total to redistribute to
            total_base = surname_weight + firstname_weight  # 0.25
            
            # Distribute proportionally
            surname_boost = middlename_weight * (surname_weight / total_base)  # 0.10 * (0.15/0.25) = 0.06
            firstname_boost = middlename_weight * (firstname_weight / total_base)  # 0.10 * (0.10/0.25) = 0.04
            
            adjusted_weights['custom_surname_match'] = surname_weight + surname_boost  # 0.15 + 0.06 = 0.21
            adjusted_weights['custom_firstname_match'] = firstname_weight + firstname_boost  # 0.10 + 0.04 = 0.14
            adjusted_weights['custom_middlename_match'] = 0.0  # Zero out middle name weight
            
            print(f"    Surname weight: {surname_weight:.4f} → {adjusted_weights['custom_surname_match']:.4f}")
            print(f"    Firstname weight: {firstname_weight:.4f} → {adjusted_weights['custom_firstname_match']:.4f}")
            print(f"    Middlename weight: {middlename_weight:.4f} → {adjusted_weights['custom_middlename_match']:.4f}")
        
        # Calculate name score (best-of name features)
        name_features = ['custom_name_match', 'custom_surname_match', 'custom_firstname_match', 'custom_middlename_match']
        best_name_score = 0.0
        best_name_weighted = 0.0
        best_name_feature = None
        
        for feat_name in name_features:
            score = scores.get(feat_name, FNUL)
            weight = adjusted_weights.get(feat_name, 0.0)
            
            # Skip if FNUL or zero weight
            if score == FNUL or weight == 0.0:
                print(f"  Name feature {feat_name}: score={score:.4f}, weight={weight:.4f} (skipped)")
                continue
            
            weighted = score * weight
            print(f"  Name feature {feat_name}: score={score:.4f}, weight={weight:.4f}, weighted={weighted:.4f}")
            
            if weighted > best_name_weighted:
                best_name_weighted = weighted
                best_name_score = score
                best_name_feature = feat_name
        
        total_score = best_name_weighted
        print(f"  Best name feature: {best_name_feature}, weighted score: {best_name_weighted:.4f}")
        
        # Add other main features (DOB, gender, nationality)
        other_features = [
            'custom_dob_year_match', 'custom_dob_month_match', 'custom_dob_day_match',
            'custom_gender_bonus', 'custom_nationality_bonus'
        ]
        
        for feat_name in other_features:
            score = scores.get(feat_name, FNUL)
            weight = adjusted_weights.get(feat_name, 0.0)
            
            # Add to total if score > 0
            if score > 0.0:
                weighted = score * weight
                total_score += weighted
                print(f"  Other feature {feat_name}: score={score:.4f}, weight={weight:.4f}, weighted={weighted:.4f}, running_total={total_score:.4f}")
            else:
                print(f"  Other feature {feat_name}: score={score:.4f} (FNUL - skipped)")
        
        print(f"  Total main features score: {total_score:.4f}")
        
        # Apply qualifiers (penalties)
        for feat in cls.features:
            if not feat.qualifier:
                continue
            qual_score = scores.get(feat.name, 0.0)
            qual_weight = adjusted_weights.get(feat.name, 0.0)
            
            # Only apply penalty if there's an actual mismatch (score > 0)
            if qual_score > 0.0:
                weighted = qual_score * qual_weight
                total_score += weighted
                print(f"  Qualifier {feat.name}: score={qual_score:.4f}, weight={qual_weight:.4f}, weighted={weighted:.4f}, running_total={total_score:.4f}")
            else:
                print(f"  Qualifier {feat.name}: score={qual_score:.4f} (no penalty)")
        
        final_score = max(0.0, min(1.0, total_score))
        print(f"[compute_score] OUTPUT: {final_score:.4f}")
        return final_score