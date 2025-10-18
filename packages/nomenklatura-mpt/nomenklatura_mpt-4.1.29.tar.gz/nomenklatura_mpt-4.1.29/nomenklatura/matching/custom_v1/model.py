from typing import List, Dict
import re
from Levenshtein import ratio

from nomenklatura.matching.custom_v1.match import custom_country_mismatch, custom_dob_day_match, custom_dob_month_match, custom_dob_year_match, custom_dob_year_mismatch, custom_firstname_match, custom_gender_bonus, custom_gender_mismatch, custom_middlename_match, custom_name_match, custom_nationality_bonus, custom_surname_match, custom_title_mismatch
from nomenklatura.matching.types import Feature, HeuristicAlgorithm, FtResult, ScoringConfig
from nomenklatura.matching.util import props_pair, type_pair, FNUL
from followthemoney.proxy import E
from followthemoney.types import registry



class CustomV1Config:
    """Static configuration for CustomV1 matching algorithm"""
    # Name feature weights (best-of selection)
    # Perfect name match contributes 0.60, leaving room for DOB to add 0.10 to reach 1.0
    FULLNAME_WEIGHT = 0.60
    SURNAME_WEIGHT = 0.20
    FIRSTNAME_WEIGHT = 0.12
    MIDDLENAME_WEIGHT = 0.08

    # DOB weights (additive, total: 0.20)
    # When DOB matches, returns 1.0 → adds 0.20 (brings to 1.00 with perfect name)
    # When no DOB, returns 0.5 → adds 0.10 (brings to 0.90 with perfect name)
    # When DOB mismatches, returns 0.0 → adds 0.00 + penalty
    DOB_YEAR_WEIGHT = 0.14
    DOB_MONTH_WEIGHT = 0.04
    DOB_DAY_WEIGHT = 0.02

    # Gender bonus (additive: 0.10)
    # Full points if match or missing, 0 if mismatch
    GENDER_BONUS_WEIGHT = 0.10

    # Nationality/Country bonus (additive: 0.10)
    # Full points if nationality match or missing, half if country match, 0 if mismatch
    NATIONALITY_BONUS_WEIGHT = 0.10

    # Penalties
    DOB_YEAR_MISMATCH_PENALTY = -0.20
    GENDER_MISMATCH_PENALTY = -0.10
    COUNTRY_MISMATCH_PENALTY = -0.05
    TITLE_MISMATCH_PENALTY = -0.05

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
        Feature(func=custom_title_mismatch, weight=CustomV1Config.TITLE_MISMATCH_PENALTY, qualifier=True),
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