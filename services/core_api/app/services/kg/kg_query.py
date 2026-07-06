from app.services.kg.kg_loader import KnowledgeGraphLoader
import re

class KnowledgeGraphQuery:
    def __init__(self):
        self.loader = KnowledgeGraphLoader()

    def extract_entities(self, text: str) -> list:
        """
        Extract key entities from the user's query using substring matching.
        """
        text = text.lower()
        entities = []
        for key in self.loader.graph.keys():
            if key in text:
                entities.append(key)
        return entities

    def expand_query(self, query: str) -> tuple[str, list]:
        """
        Expand the original user query using related entities from the KG.
        Returns the new query string and the list of explicitly added sources.
        """
        entities = self.extract_entities(query)
        expanded_terms = set()
        
        for entity in entities:
            related = self.loader.get_related_entities(entity)
            expanded_terms.update(related)
            
        if expanded_terms:
            expansion_text = " ".join(expanded_terms)
            return f"{query} {expansion_text}", list(expanded_terms)
            
        return query, []
