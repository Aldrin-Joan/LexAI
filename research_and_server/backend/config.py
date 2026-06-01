"""
Configuration management for Legal Case Knowledge Graph System.

This module manages all configuration settings including:
- Azure OpenAI credentials
- Storage paths
- Category taxonomy
- Entity and relationship definitions
"""

import os
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration for the application."""

    # Google Gemini Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # Storage Configuration
    BASE_DATA_DIR = Path(__file__).parent.parent.absolute() / "data"
    CATEGORIES_DIR = BASE_DATA_DIR / "categories"
    FULL_TEXTS_DIR = BASE_DATA_DIR / "full_texts"
    INDEX_DB_PATH = BASE_DATA_DIR / "index.db"
    KAGGLE_DATASET_PATH = Path("kaggle_data")

    # Processing Configuration
    MAX_WORKERS = 4
    BATCH_SIZE = 10
    MAX_TEXT_LENGTH = 50000

    # Category Taxonomy
    MAIN_CATEGORIES: Dict[str, List[str]] = {
        "civil_law": [
            "marriage_matrimonial",
            "property_real_estate",
            "contracts_agreements",
            "torts_negligence",
            "consumer_protection",
            "succession_inheritance",
        ],
        "criminal_law": [
            "murder_homicide",
            "theft_robbery",
            "fraud_cheating",
            "corruption_bribery",
            "narcotics_ndps",
            "sexual_offenses",
            "cybercrime",
        ],
        "constitutional_law": [
            "fundamental_rights",
            "directive_principles",
            "federalism_state_powers",
            "judicial_review",
            "emergency_provisions",
        ],
        "corporate_law": [
            "company_disputes",
            "securities_sebi",
            "insolvency_bankruptcy",
            "mergers_acquisitions",
            "corporate_governance",
        ],
        "tax_law": [
            "income_tax",
            "gst_indirect_tax",
            "customs_excise",
            "tax_evasion",
        ],
        "labor_law": [
            "industrial_disputes",
            "employment_rights",
            "wages_benefits",
            "trade_unions",
        ],
        "environmental_law": [
            "pollution_control",
            "forest_wildlife",
            "environmental_impact",
        ],
        "intellectual_property": [
            "patents",
            "trademarks",
            "copyright",
            "trade_secrets",
        ],
        "administrative_law": [
            "government_actions",
            "public_service",
            "regulatory_compliance",
        ],
        "other_domains": [
            "banking_finance",
            "insurance",
            "arbitration",
            "election_law",
        ],
    }

    # Entity Types
    ENTITY_TYPES = [
        "PERSON",
        "ORGANIZATION",
        "COURT",
        "JUDGE",
        "LAW_STATUTE",
        "LEGAL_CONCEPT",
        "CITATION",
        "DATE",
        "LOCATION",
    ]

    # Relationship Types
    RELATIONSHIP_TYPES = [
        "CITES",
        "OVERRULES",
        "FOLLOWS",
        "DISTINGUISHES",
        "PRESIDED_BY",
        "REPRESENTED_BY",
        "FILED_BY",
        "GOVERNED_BY",
        "INTERPRETS",
        "APPLIES",
    ]

    # Case Types
    CASE_TYPES = [
        "Appeal",
        "Writ Petition",
        "Special Leave Petition",
        "Review Petition",
        "Transfer Petition",
        "Contempt Petition",
        "Criminal Appeal",
        "Civil Appeal",
    ]

    # Verdict Types
    VERDICT_TYPES = [
        "Allowed",
        "Dismissed",
        "Partly Allowed",
        "Remanded",
        "Transferred",
        "Withdrawn",
    ]

    # Bench Sizes
    BENCH_SIZES = [
        "Single Judge",
        "Division Bench",
        "Full Bench",
        "Constitutional Bench",
    ]

    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        cls.BASE_DATA_DIR.mkdir(exist_ok=True)
        cls.CATEGORIES_DIR.mkdir(exist_ok=True)
        cls.FULL_TEXTS_DIR.mkdir(exist_ok=True)

        # Create category subdirectories
        for main_cat, sub_cats in cls.MAIN_CATEGORIES.items():
            main_cat_dir = cls.CATEGORIES_DIR / main_cat
            main_cat_dir.mkdir(exist_ok=True)
            for sub_cat in sub_cats:
                sub_cat_dir = main_cat_dir / sub_cat
                sub_cat_dir.mkdir(exist_ok=True)

    @classmethod
    def get_category_path(
        cls,
        main_category: str,
        sub_category: str,
        year: int
    ) -> Path:
        """
        Get the full path for a specific category/year combination.

        Args:
            main_category: Main legal domain
            sub_category: Sub-category within domain
            year: Year of the case

        Returns:
            Path object for the category directory
        """
        path = (
            cls.CATEGORIES_DIR
            / main_category
            / sub_category
            / str(year)
        )
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def validate_category(
        cls,
        main_category: str,
        sub_category: str
    ) -> bool:
        """
        Validate that a category combination is valid.

        Args:
            main_category: Main legal domain
            sub_category: Sub-category within domain

        Returns:
            True if valid, False otherwise
        """
        if main_category not in cls.MAIN_CATEGORIES:
            return False
        return sub_category in cls.MAIN_CATEGORIES[main_category]


# Initialize directories on import
Config.ensure_directories()
