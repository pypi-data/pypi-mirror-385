from typing import Dict

from nomenklatura.matching.util import FNUL


class CustomV1Config:
    """Static configuration for CustomV1 matching algorithm"""
    # Base name weights (total: 0.70 when all present)
    FULLNAME_WEIGHT = 0.50
    SURNAME_WEIGHT = 0.15
    FIRSTNAME_WEIGHT = 0.05
    
    # DOB weights (total: 0.20 when all present)
    DOB_YEAR_WEIGHT = 0.15
    DOB_MONTH_WEIGHT = 0.03
    DOB_DAY_WEIGHT = 0.02
    
    # Gender/Nationality bonus (total: 0.10 when all present)
    GENDER_BONUS_WEIGHT = 0.05
    NATIONALITY_BONUS_WEIGHT = 0.05
    
    # Qualifier weights (penalties for mismatch)
    DOB_YEAR_MISMATCH_PENALTY = -0.20
    GENDER_MISMATCH_PENALTY = -0.10
    COUNTRY_MISMATCH_PENALTY = -0.15


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
    result_obj = FtResult(score=FNUL, detail="Gender mismatch")
    print(f"[custom_gender_bonus] OUTPUT: score={result_obj.score}")
    return result_obj


def custom_nationality_bonus(query: E, result: E, config: ScoringConfig) -> FtResult:
    """Bonus for nationality match (not a penalty)"""
    print(f"\n[custom_nationality_bonus] INPUT:")
    print(f"  Query schema: {query.schema.name}, ID: {query.id}")
    print(f"  Result schema: {result.schema.name}, ID: {result.id}")
    
    if not (query.schema.is_a("Person") and result.schema.is_a("Person")):
        print(f"[custom_nationality_bonus] Not Person entities, returning 1.0")
        result_obj = FtResult(score=1.0, detail="Not Person entities")
        print(f"[custom_nationality_bonus] OUTPUT: score={result_obj.score}")
        return result_obj
    
    query_countries, result_countries = props_pair(query, result, ["nationality"])
    print(f"  Query countries: {query_countries}")
    print(f"  Result countries: {result_countries}")
    
    if not query_countries or not result_countries:
        print(f"[custom_nationality_bonus] Nationality missing, returning 1.0 (neutral - no bonus, no penalty)")
        result_obj = FtResult(score=1.0, detail="Nationality missing")
        print(f"[custom_nationality_bonus] OUTPUT: score={result_obj.score}")
        return result_obj
    
    for q_country, r_country in zip(query_countries, result_countries):
        print(f"  Comparing: '{q_country}' vs '{r_country}'")
        
        if not q_country or not r_country:
            continue
        
        if q_country.lower() == r_country.lower():
            print(f"  Nationality match - giving bonus!")
            result_obj = FtResult(score=1.0, detail=f"Nationality match: {q_country}")
            print(f"[custom_nationality_bonus] OUTPUT: score={result_obj.score}")
            return result_obj
    
    print(f"  Nationality mismatch - neutral (no bonus)")
    result_obj = FtResult(score=FNUL, detail="Nationality mismatch")
    print(f"[custom_nationality_bonus] OUTPUT: score={result_obj.score}")
    return result_obj


class CustomV1(HeuristicAlgorithm):
    """
    Custom matching algorithm optimized for person matching with dynamic weight adjustment
    """
    
    NAME = "custom-v1"
    
    features = [
        # Main name matching features (base score)
        Feature(func=custom_name_match, weight=CustomV1Config.FULLNAME_WEIGHT),
        Feature(func=custom_surname_match, weight=CustomV1Config.SURNAME_WEIGHT),
        Feature(func=custom_firstname_match, weight=CustomV1Config.FIRSTNAME_WEIGHT),
        
        # DOB matching features (bonus when present and matching)
        Feature(func=custom_dob_year_match, weight=CustomV1Config.DOB_YEAR_WEIGHT),
        Feature(func=custom_dob_month_match, weight=CustomV1Config.DOB_MONTH_WEIGHT),
        Feature(func=custom_dob_day_match, weight=CustomV1Config.DOB_DAY_WEIGHT),
        
        # Gender/Nationality bonus (bonus when present and matching)
        Feature(func=custom_gender_bonus, weight=CustomV1Config.GENDER_BONUS_WEIGHT),
        Feature(func=custom_nationality_bonus, weight=CustomV1Config.NATIONALITY_BONUS_WEIGHT),
        
        # Qualifiers (penalties for mismatch when both present)
        Feature(func=custom_dob_year_mismatch, weight=CustomV1Config.DOB_YEAR_MISMATCH_PENALTY, qualifier=True),
        Feature(func=custom_gender_mismatch, weight=CustomV1Config.GENDER_MISMATCH_PENALTY, qualifier=True),
        Feature(func=custom_country_mismatch, weight=CustomV1Config.COUNTRY_MISMATCH_PENALTY, qualifier=True),
    ]
    
    # @classmethod
    # def compute_score(
    #     cls, scores: Dict[str, float], weights: Dict[str, float]
    # ) -> float:
    #     """
    #     Compute final score with special handling for missing properties
    #     Missing properties return 1.0 (neutral) and contribute their full weight as baseline
    #     Matching properties contribute their full weight as bonus
    #     Mismatching properties get penalties
    #     """
    #     print(f"\n[compute_score] INPUT:")
    #     print(f"  Scores: {scores}")
    #     print(f"  Weights: {weights}")
        
    #     # Calculate weighted scores for all main features
    #     weighted_scores = []
        
    #     for feat in cls.features:
    #         if feat.qualifier:
    #             continue
            
    #         score = scores.get(feat.name, FNUL)
    #         weight = weights.get(feat.name, FNUL)
            
    #         # If score is 1.0 (neutral/match), give full weight
    #         # If score is 0.0 (FNUL/no data), give full weight too (neutral)
    #         # If score is between 0-1, proportional weight
    #         if score == 1.0 or score == FNUL:
    #             weighted = weight
    #         else:
    #             weighted = score * weight
            
    #         weighted_scores.append(weighted)
    #         print(f"  Main feature {feat.name}: score={score:.4f}, weight={weight:.4f}, weighted={weighted:.4f}")
        
    #     # Sum all weighted scores (not max) - this is the key change!
    #     base_score = sum(weighted_scores) if weighted_scores else FNUL
    #     print(f"  Sum of main features: {base_score:.4f}")
        
    #     # Apply qualifiers (penalties)
    #     for feat in cls.features:
    #         if not feat.qualifier:
    #             continue
    #         qual_score = scores.get(feat.name, FNUL)
    #         qual_weight = weights.get(feat.name, FNUL)
    #         weighted = qual_score * qual_weight
    #         print(f"  Qualifier {feat.name}: score={qual_score:.4f}, weight={qual_weight:.4f}, weighted={weighted:.4f}")
    #         base_score += weighted
        
    #     final_score = max(0.0, min(1.0, base_score))
    #     print(f"[compute_score] OUTPUT: {final_score:.4f}")
    #     return final_score
    @classmethod
    def compute_score(
        cls, scores: Dict[str, float], weights: Dict[str, float]
    ) -> float:
        """
        Compute final score where all matching features contribute additively
        """
        print(f"\n[compute_score] INPUT:")
        print(f"  Scores: {scores}")
        print(f"  Weights: {weights}")
        
        total_score = 0.0
        
        # Process main features
        for feat in cls.features:
            if feat.qualifier:
                continue
            
            score = scores.get(feat.name, FNUL)
            weight = weights.get(feat.name, FNUL)
            
            # Only add weighted score if feature actually scored something
            if score > 0.0:  # Changed from checking FNUL
                weighted = score * weight
                total_score += weighted
                print(f"  Main feature {feat.name}: score={score:.4f}, weight={weight:.4f}, weighted={weighted:.4f}, running_total={total_score:.4f}")
            else:
                print(f"  Main feature {feat.name}: score={score:.4f} (FNUL - skipped)")
        
        print(f"  Total main features score: {total_score:.4f}")
        
        # Apply qualifiers (penalties)
        for feat in cls.features:
            if not feat.qualifier:
                continue
            qual_score = scores.get(feat.name, FNUL)
            qual_weight = weights.get(feat.name, FNUL)
            
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