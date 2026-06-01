"""
Storage manager for Legal Case Knowledge Graph System.

This module handles:
- Hierarchical file storage (domain → sub-category → year → case)
- SQLite index for fast lookups
- Case metadata persistence
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import Config
from schemas import CaseMetadata, CategoryPath
from utils import print_success, print_error, print_info


class StorageManager:
    """Manage hierarchical storage of legal cases."""

    def __init__(self):
        """Initialize the storage manager."""
        self.db_path = Config.INDEX_DB_PATH
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database for indexing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create cases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                case_number TEXT,
                title TEXT,
                date TEXT,
                year INTEGER,
                court TEXT,
                main_category TEXT,
                sub_category TEXT,
                case_type TEXT,
                verdict TEXT,
                bench_size TEXT,
                file_path TEXT,
                full_text_path TEXT,
                created_at TEXT
            )
        """)

        # Create index for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category 
            ON cases(main_category, sub_category, year)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_year 
            ON cases(year)
        """)

        # Create FTS table for full-text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS cases_fts 
            USING fts5(case_id, title, main_category, sub_category, content)
        """)

        conn.commit()
        conn.close()

        print_success("Database initialized")

    def store_case(
        self,
        case_data: Dict[str, Any],
        categorization: Dict[str, Any]
    ) -> bool:
        """
        Store a case in hierarchical structure.

        Args:
            case_data: Case data dictionary
            categorization: Categorization results

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract data
            case_id = case_data['case_id']
            main_cat = categorization['main_category']
            sub_cat = categorization['sub_category']
            year = case_data['year']

            # Get storage path
            category_path = Config.get_category_path(
                main_cat,
                sub_cat,
                year
            )

            # Create metadata file
            metadata_file = category_path / f"{case_id}.json"

            metadata = {
                'case_id': case_id,
                'case_number': case_data.get('case_number'),
                'title': case_data.get('title'),
                'date': case_data.get('date').isoformat()
                if isinstance(case_data.get('date'), datetime)
                else str(case_data.get('date')),
                'year': year,
                'court': case_data.get('court'),
                'judges': case_data.get('judges', []),
                'petitioner': case_data.get('petitioner'),
                'respondent': case_data.get('respondent'),
                'main_category': main_cat,
                'sub_category': sub_cat,
                'case_type': categorization.get('case_type'),
                'verdict': categorization.get('verdict'),
                'full_text_path': case_data.get('full_text_path'),
                'confidence_scores': {
                    'main': categorization.get('confidence_main', 0.0),
                    'sub': categorization.get('confidence_sub', 0.0),
                },
                'created_at': datetime.now().isoformat(),
            }

            # Write metadata file
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            # Update database index
            self._index_case(metadata, str(metadata_file))

            print_success(
                f"Stored case: {case_id} in "
                f"{main_cat}/{sub_cat}/{year}"
            )

            return True

        except Exception as e:
            print_error(f"Failed to store case: {str(e)}")
            return False

    def _index_case(
        self,
        metadata: Dict[str, Any],
        file_path: str
    ) -> None:
        """
        Add case to SQLite index.

        Args:
            metadata: Case metadata
            file_path: Path to metadata file
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO cases VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            metadata['case_id'],
            metadata['case_number'],
            metadata['title'],
            metadata['date'],
            metadata['year'],
            metadata['court'],
            metadata['main_category'],
            metadata['sub_category'],
            metadata.get('case_type'),
            metadata.get('verdict'),
            metadata.get('bench_size'),
            file_path,
            metadata.get('full_text_path'),
            metadata['created_at'],
        ))

        # Update FTS index
        content = f"{metadata['title']} {metadata.get('court', '')} {metadata.get('judges', [])}"

        cursor.execute("""
            INSERT OR REPLACE INTO cases_fts (case_id, title, main_category, sub_category, content)
            VALUES (?, ?, ?, ?, ?)
        """, (
            metadata['case_id'],
            metadata['title'],
            metadata['main_category'],
            metadata['sub_category'],
            content
        ))

        conn.commit()
        conn.close()

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve case metadata by ID.

        Args:
            case_id: Case identifier

        Returns:
            Case metadata dictionary or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT file_path FROM cases WHERE case_id = ?",
            (case_id,)
        )
        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        # Load metadata from file
        try:
            with open(result[0], 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print_error(f"Failed to load case metadata: {str(e)}")
            return None

    def get_cases_by_category(
        self,
        main_category: str,
        sub_category: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get cases by category.

        Args:
            main_category: Main legal domain
            sub_category: Optional sub-category
            year: Optional year filter

        Returns:
            List of case metadata dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT file_path FROM cases WHERE main_category = ?"
        params = [main_category]

        if sub_category:
            query += " AND sub_category = ?"
            params.append(sub_category)

        if year:
            query += " AND year = ?"
            params.append(year)

        query += " ORDER BY year DESC, date DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        cases = []
        for (file_path,) in results:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    cases.append(json.load(f))
            except Exception as e:
                print_error(
                    f"Failed to load case from {file_path}: {str(e)}"
                )

        return cases

    def get_category_statistics(
        self,
        main_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics for categories.

        Args:
            main_category: Optional main category filter

        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        if main_category:
            # Stats for specific main category
            cursor.execute("""
                SELECT sub_category, COUNT(*) 
                FROM cases 
                WHERE main_category = ? 
                GROUP BY sub_category
            """, (main_category,))

            stats['sub_categories'] = dict(cursor.fetchall())

            cursor.execute("""
                SELECT year, COUNT(*) 
                FROM cases 
                WHERE main_category = ? 
                GROUP BY year 
                ORDER BY year
            """, (main_category,))

            stats['years'] = dict(cursor.fetchall())

        else:
            # Overall stats
            cursor.execute("""
                SELECT main_category, COUNT(*) 
                FROM cases 
                GROUP BY main_category
            """)

            stats['main_categories'] = dict(cursor.fetchall())

            cursor.execute("""
                SELECT year, COUNT(*) 
                FROM cases 
                GROUP BY year 
                ORDER BY year
            """)

            stats['years'] = dict(cursor.fetchall())

        cursor.execute("SELECT COUNT(*) FROM cases")
        stats['total_cases'] = cursor.fetchone()[0]

        conn.close()

        return stats

    def search_cases(
        self,
        query: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search cases by text query.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching cases
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Use FTS MATCH if searching simple terms
        # Otherwise fallback to LIKE if needed, but FTS is preferred

        # Check if table has data
        try:
            cursor.execute("""
                SELECT c.*, f.rank 
                FROM cases_fts f 
                JOIN cases c ON f.case_id = c.case_id 
                WHERE cases_fts MATCH ? 
                ORDER BY rank 
                LIMIT ?
            """, (query, limit))
        except sqlite3.OperationalError:
            # Fallback for simple LIKE if FTS fails or complex query
            cursor.execute("""
                SELECT * FROM cases 
                WHERE title LIKE ? OR case_number LIKE ?
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))

        # Get column names
        columns = [description[0] for description in cursor.description]
        
        results = cursor.fetchall()
        conn.close()

        cases = []
        for row in results:
            # Create a dict from the row
            case = dict(zip(columns, row))
            # Rename fts_rank if present (from FTS join)
            if 'rank' in case:
                case['fts_rank'] = case.pop('rank')
            cases.append(case)

        return cases
