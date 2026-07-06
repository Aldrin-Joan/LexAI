import json
import os

class KnowledgeGraphLoader:
    def __init__(self, data_path="backend/data/kg_mock.json"):
        self.data_path = os.path.join(os.getcwd(), data_path)
        self.graph = {}
        self.load_graph()

    def load_graph(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Handle Ayush's Relation Tuples Format (List of dicts)
            if isinstance(data, list):
                for item in data:
                    source = item.get("source", "").lower()
                    target = item.get("target", "")
                    if source and target:
                        if source not in self.graph:
                            self.graph[source] = []
                        self.graph[source].append(target)
            else:
                self.graph = data
        else:
            # Mock graph simulating external KG relations
            self.graph = {
                "parliament": ["Article 368", "Legislative Powers"],
                "constitution": ["Basic structure doctrine", "Kesavananda Bharati case", "Article 368"],
                "amendment": ["Article 368", "Kesavananda Bharati case", "First Amendment Act"],
                "murder": ["Section 302 IPC", "K.M. Nanavati v. State of Maharashtra", "Culpable Homicide"],
                "theft": ["Section 378 IPC", "Section 379 IPC"],
                "divorce": ["Hindu Marriage Act 1955", "Section 13", "Mutual Consent"],
                "fundamental rights": ["Part III of Constitution", "Article 12-35", "Maneka Gandhi v. Union of India"],
                "bail": ["CrPC Section 437", "CrPC Section 439"],
                "rape": ["Section 376 IPC", "Nirbhaya Case"],
                "property": ["Transfer of Property Act", "Sale Deed"]
            }
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(self.graph, f, indent=4)
                
    def get_related_entities(self, entity: str):
        return self.graph.get(entity.lower(), [])
