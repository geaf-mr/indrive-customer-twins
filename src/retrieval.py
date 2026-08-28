"""
Local TF-IDF & Cosine Similarity vector retrieval engine over evidence matrix and corpus chunks.
"""

import json
import os
import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class LocalRetriever:
    def __init__(self, corpus_path: str = "data/processed/corpus.json", evidence_path: str = "evidence/evidence_matrix.json"):
        self.corpus = []
        self.evidence_matrix = []
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words=None)
        self.docs = []
        self.doc_metadata = []

        self._load_and_index(corpus_path, evidence_path)

    def _load_and_index(self, corpus_path: str, evidence_path: str):
        # Load evidence matrix items
        if os.path.exists(evidence_path):
            with open(evidence_path, "r", encoding="utf-8") as f:
                self.evidence_matrix = json.load(f)
                for item in self.evidence_matrix:
                    for ev in item.get("evidencia", []):
                        text = f"{item['tema']} {item['patron']} {item['interpretacion']} {ev['evidencia_textual']}"
                        self.docs.append(text)
                        self.doc_metadata.append({
                            "type": "matrix",
                            "patron_id": item["patron_id"],
                            "tema": item["tema"],
                            "patron": item["patron"],
                            "profile_affinity": item["profile_affinity"],
                            "transcript_id": ev["transcript_id"],
                            "interviewee_label": ev["interviewee_label"],
                            "app_affiliation": ev["app_affiliation"],
                            "text_snippet": ev["evidencia_textual"],
                            "interpretacion": item["interpretacion"]
                        })

        # Load raw corpus chunks
        if os.path.exists(corpus_path):
            with open(corpus_path, "r", encoding="utf-8") as f:
                self.corpus = json.load(f)
                for chunk in self.corpus:
                    text = f"{chunk['transcript_id']} {chunk['app_affiliation']} {chunk['text']}"
                    self.docs.append(text)
                    self.doc_metadata.append({
                        "type": "corpus",
                        "transcript_id": chunk["transcript_id"],
                        "interviewee_label": chunk["interviewee_label"],
                        "app_affiliation": chunk["app_affiliation"],
                        "text_snippet": chunk["text"],
                        "interpretacion": "Extracto directo de la transcripción cualitativa."
                    })

        if self.docs:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.docs)
        else:
            self.tfidf_matrix = None

    def retrieve(self, query: str, profile_affinity: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.tfidf_matrix is None or not self.docs:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Sort indices by score descending
        ranked_indices = np.argsort(similarities)[::-1]

        results = []
        seen_snippets = set()

        for idx in ranked_indices:
            score = float(similarities[idx])
            meta = self.doc_metadata[idx]

            # Filter by profile affinity if specified and present
            if profile_affinity and meta.get("profile_affinity") and meta.get("profile_affinity") not in [profile_affinity, "both"]:
                continue

            snippet = meta["text_snippet"]
            if snippet in seen_snippets:
                continue
            seen_snippets.add(snippet)

            item = dict(meta)
            item["score"] = round(score, 4)
            results.append(item)

            if len(results) >= top_k:
                break

        return results

if __name__ == "__main__":
    retriever = LocalRetriever()
    res = retriever.retrieve("¿Cómo reaccionas ante una tarifa muy baja?", profile_affinity="twin_a", top_k=3)
    print("Test retrieval results:")
    for r in res:
        print(f"[{r['transcript_id']}] Score: {r['score']} | Snippet: {r['text_snippet'][:100]}...")
