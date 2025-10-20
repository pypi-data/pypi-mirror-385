"""CustomV1 matching algorithm - optimized for Person and Organization entity matching"""
from typing import Dict

from nomenklatura.matching.types import Feature, HeuristicAlgorithm
from nomenklatura.matching.util import FNUL

from .names import (
    custom_name_match,
    custom_surname_match,
    custom_firstname_match,
    custom_middlename_match,
    custom_title_mismatch,
)
from .dates import (
    custom_dob_year_match,
    custom_dob_month_match,
    custom_dob_day_match,
    custom_dob_year_mismatch,
)
from .attributes import (
    custom_gender_bonus,
    custom_gender_mismatch,
    custom_nationality_bonus,
    custom_country_mismatch,
)
from .contacts import (
    custom_email_match,
    custom_phone_match,
)
from .identifiers import (
    custom_identifier_match,
)
from .addresses import (
    custom_address_match,
)


class CustomV1(HeuristicAlgorithm):
    """
    Custom matching algorithm optimized for Person and Organization matching with:

    Person entities:
    - Dual-approach name matching (full name Levenshtein + sum of parts)
    - Birth date scoring with year-only support
    - Dynamic weight redistribution for missing middlenames
    - Gender and nationality bonuses
    - Contact matching (email, phone)
    - Address matching
    - Identifier matching (tax IDs, registration numbers)

    Organization entities:
    - Simple name matching with suffix normalization (Ltd, Inc, Corp, etc.)
    - Incorporation date scoring
    - Contact matching (email, phone)
    - Address matching
    - Identifier matching (tax IDs, registration numbers)

    Scoring targets:
    - Perfect name + no DOB + attributes = 0.90
    - Perfect name + full DOB + attributes = 1.00
    """

    NAME = "custom-v1"

    features = [
        # Name matching features (best-of selection)
        Feature(func=custom_name_match, weight=0.60),
        Feature(func=custom_surname_match, weight=0.20),
        Feature(func=custom_firstname_match, weight=0.12),
        Feature(func=custom_middlename_match, weight=0.08),

        # DOB/Incorporation date matching features (additive)
        Feature(func=custom_dob_year_match, weight=0.10),
        Feature(func=custom_dob_month_match, weight=0.06),
        Feature(func=custom_dob_day_match, weight=0.04),

        # Attribute bonuses (additive)
        Feature(func=custom_gender_bonus, weight=0.10),
        Feature(func=custom_nationality_bonus, weight=0.10),

        # Contact and identifier matching (strong signals)
        Feature(func=custom_email_match, weight=0.95),
        Feature(func=custom_phone_match, weight=0.90),
        Feature(func=custom_identifier_match, weight=0.95),

        # Address matching (qualifier bonus)
        Feature(func=custom_address_match, weight=0.15, qualifier=True),

        # Qualifiers (penalties)
        Feature(func=custom_dob_year_mismatch, weight=-0.20, qualifier=True),
        Feature(func=custom_gender_mismatch, weight=-0.10, qualifier=True),
        Feature(func=custom_country_mismatch, weight=-0.05, qualifier=True),
        Feature(func=custom_title_mismatch, weight=-0.05, qualifier=True),
    ]

    @classmethod
    def compute_score(cls, scores: Dict[str, float], weights: Dict[str, float]) -> float:
        """
        Compute final score with hybrid approach:
        - Best-of for name features, contact features, and identifier features
        - Additive for other features
        - Dynamic weight redistribution for missing middlenames
        """
        # Check if middlename is missing
        middlename_score = scores.get('custom_middlename_match', FNUL)
        middlename_missing = (middlename_score == FNUL)

        # Adjust weights if middlename is missing
        adjusted_weights = weights.copy()

        if middlename_missing:
            # Redistribute middlename weight (0.08) proportionally
            # Surname gets 0.05, Firstname gets 0.03
            middlename_weight = 0.08
            surname_weight = 0.20
            firstname_weight = 0.12
            total_base = surname_weight + firstname_weight  # 0.32

            surname_boost = middlename_weight * (surname_weight / total_base)     # 0.05
            firstname_boost = middlename_weight * (firstname_weight / total_base) # 0.03

            adjusted_weights['custom_surname_match'] = surname_weight + surname_boost       # 0.25
            adjusted_weights['custom_firstname_match'] = firstname_weight + firstname_boost # 0.15
            adjusted_weights['custom_middlename_match'] = 0.0

        # Calculate best-of scores for strong signals (names, contacts, identifiers)
        strong_signal_features = [
            # Name features
            'custom_name_match',
            'custom_surname_match',
            'custom_firstname_match',
            'custom_middlename_match',
            # Contact/identifier features
            'custom_email_match',
            'custom_phone_match',
            'custom_identifier_match',
        ]

        best_strong_signal = 0.0
        for feat_name in strong_signal_features:
            score = scores.get(feat_name, FNUL)
            weight = adjusted_weights.get(feat_name, 0.0)

            if score == FNUL or weight == 0.0:
                continue

            weighted = score * weight
            if weighted > best_strong_signal:
                best_strong_signal = weighted

        total_score = best_strong_signal

        # Add other features (DOB, gender, nationality)
        other_features = [
            'custom_dob_year_match',
            'custom_dob_month_match',
            'custom_dob_day_match',
            'custom_gender_bonus',
            'custom_nationality_bonus'
        ]

        for feat_name in other_features:
            score = scores.get(feat_name, FNUL)
            weight = adjusted_weights.get(feat_name, 0.0)

            if score > 0.0:
                total_score += score * weight

        # Apply qualifiers (address bonus and penalties)
        for feat in cls.features:
            if not feat.qualifier:
                continue

            qual_score = scores.get(feat.name, 0.0)
            qual_weight = adjusted_weights.get(feat.name, 0.0)

            if qual_score > 0.0:
                total_score += qual_score * qual_weight

        # Clamp to [0, 1]
        return max(0.0, min(1.0, total_score))
