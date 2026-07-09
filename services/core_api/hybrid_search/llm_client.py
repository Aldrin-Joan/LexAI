"""Groq API client wrapper for Legal Case Knowledge Graph System.

This module provides a wrapper around the Groq Cloud API for:
- Case categorization
- Entity extraction
- Relationship detection
- RAG Answer Generation
- Case Briefing
"""

import json
import time
from typing import Dict, List, Optional, Any
import requests
from config import Config
from utils import print_error, print_warning


class LLMClient:
    """Wrapper for Groq API interactions."""

    def __init__(self):
        """Initialize the Groq client."""
        self.api_key = Config.GROQ_API_KEY
        self.model_name = Config.GROQ_MODEL
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.total_tokens = 0
        self.cache: Dict[str, Any] = {}

    def _make_request(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_retries: int = 3,
        is_json: bool = False,
    ) -> Optional[str]:
        """Make a request to Groq API with retry logic."""
        if not self.api_key:
            print_error("GROQ_API_KEY is not set in environment.")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }

        if is_json:
            payload["response_format"] = {"type": "json_object"}

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                res_data = response.json()

                # Track token usage if available
                usage = res_data.get("usage")
                if usage:
                    self.total_tokens += usage.get("total_tokens", 0)

                choices = res_data.get("choices", [])
                if choices:
                    return choices[0]["message"]["content"]

                return None

            except Exception as e:
                print_warning(
                    f"Groq API request failed (attempt {attempt + 1}/"
                    f"{max_retries}): {str(e)}"
                )
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    print_error(
                        f"Groq API failed after {max_retries} attempts"
                    )
                    return None

        return None

    def categorize_case(
        self,
        case_text: str,
        case_title: str
    ) -> Optional[Dict[str, Any]]:
        """Categorize a legal case into main and sub-categories."""
        cache_key = f"categorize_{hash(case_title)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        if len(case_text) > Config.MAX_TEXT_LENGTH:
            case_text = case_text[:Config.MAX_TEXT_LENGTH]

        prompt = f"""Analyze the following Indian Supreme Court case.

Case Title: {case_title}
Text Excerpt: {case_text[:2000]}

Respond with a JSON object:
{{
    "main_category": "domain (e.g., civil_law)",
    "sub_category": "area (e.g., murder_homicide)",
    "case_type": "type",
    "verdict": "Allowed/Dismissed/etc",
    "confidence_main": 0.95,
    "confidence_sub": 0.90,
    "reasoning": "Quick explanation"
}}"""

        response = self._make_request(prompt, is_json=True)

        if response:
            try:
                result = json.loads(response)
                self.cache[cache_key] = result
                return result
            except json.JSONDecodeError:
                return None
        return None

    def extract_entities(
        self,
        case_text: str,
        case_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Extract legal entities from case text."""
        prompt = f"""Extract entities from this legal text in JSON.

Text: {case_text[:3000]}

Format: {{"entities": [{{"type": "JUDGE", "text": "Name", "confidence": 0.9}}]}}
"""
        response = self._make_request(prompt, is_json=True)
        if response:
            try:
                return json.loads(response).get("entities", [])
            except json.JSONDecodeError:
                return []
        return []

    def detect_relationships(
        self,
        case_text: str,
        entities: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Placeholder for relationship detection."""
        return []

    def analyze_search_query(
        self,
        query: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze query to extract filters."""
        prompt = f"""Analyze query: "{query}"
Extract JSON: {{
    "main_category": "domain", "sub_category": "subdomain",
    "keywords": ["term1", "term2"],
    "year_range": {{"start": 2000, "end": 2025}}
}}"""
        response = self._make_request(prompt, is_json=True)
        if response:
            try:
                return json.loads(response)
            except Exception:
                return None
        return None

    def generate_hypothetical_document(self, query: str) -> str:
        """Generate a hypothetical judgment (HyDE)."""
        prompt = f"Write a hypothetical SC judgment excerpt for: {query}"
        response = self._make_request(prompt)
        return response.strip() if response else query

    def generate_synthetic_queries(
        self,
        title: str,
        text_preview: str
    ) -> List[str]:
        """Generate search queries for a case."""
        prompt = f"""Generate 3 distinct search queries for: {title}
Context: {text_preview[:500]}
Output queries separated by newlines.
"""
        response = self._make_request(prompt)
        if response:
            return response.strip().split("\n")[:3]
        return [title]

    def generate_answer(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[str]:
        """Generate RAG summary using Groq with citations and history."""
        # 1. Format Context
        context_text = ""
        for i, doc in enumerate(context_docs[:5], 1):
            title = doc.get('title', 'N/A')
            snippet = doc.get('text', 'No content')[:2500]
            context_text += f"\n[CASE {i}] {title}: {snippet}\n"

        # 2. Format History
        history_text = ""
        if history:
            # Only take the last 6 messages to keep context window clean
            for msg in history[-6:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                content = msg["content"]
                history_text += f"{role}: {content}\n"

        prompt = f"""You are a AI Senior Advocate.
Based on the provided precedents and conversation history, answer the query.

STRICT RULES:
1. CITATIONS: Use the FULL Case Names and Citations for every legal point.
2. GROUNDING: Only answer based on the provided [CASE] texts.
3. STRUCTURE: Use a structured 'Legal Opinion' format.
4. FOLLOW-UPS: If this is a follow-up query, maintain consistency with history.
5. NO MARKDOWN: DO NOT use markdown formatting. No bold (**), no italics (*),
   no markdown tables, no backticks (`). Use PLAIN TEXT ONLY.

CONVERSATION HISTORY:
{history_text or "No previous history."}

CURRENT QUESTION: {query}

PRECEDENTS:
{context_text}

LEGAL ADVICE:"""
        return self._make_request(prompt)

    def generate_case_brief(
        self,
        case_title: Any,
        full_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Generate structured legal brief with IRAC."""
        # Defensive check in case dict is passed instead of string title
        title_str = ""
        if isinstance(case_title, dict):
            title_str = case_title.get('title', 'N/A')
        else:
            title_str = str(case_title)

        excerpt = full_text[:4500]
        prompt = f"""Create a detailed legal brief (IRAC format) for: {title_str}.
Include the full citation if available in the text.

Structure:
- Facts
- Issues
- Held / Decision
- Reasoning

TEXT: {excerpt}

PLAIN TEXT BRIEF (NO MARKDOWN):"""
        return self._make_request(prompt)

    def get_token_usage(self) -> int:
        """Get total tokens consumed."""
        return self.total_tokens

    def clear_cache(self) -> None:
        """Clear cache."""
        self.cache.clear()
