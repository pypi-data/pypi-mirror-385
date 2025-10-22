"""
Enhanced search engine with TF-IDF.

Provides relevance-based search for Knowledge Base entries.
"""
from typing import List, Optional, Tuple

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from clauxton.core.models import KnowledgeBaseEntry


class SearchEngine:
    """TF-IDF based search engine for Knowledge Base entries."""

    def __init__(self, entries: List[KnowledgeBaseEntry]):
        """
        Initialize search engine with entries.

        Args:
            entries: List of Knowledge Base entries to index

        Raises:
            ImportError: If scikit-learn is not installed
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError(
                "scikit-learn is required for TF-IDF search. "
                "Install with: pip install scikit-learn"
            )

        self.entries = entries
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=1,  # Minimum document frequency
            lowercase=True
        )
        self.tfidf_matrix = None
        self._build_index()

    def _build_index(self) -> None:
        """Build TF-IDF index from entries."""
        if not self.entries:
            self.tfidf_matrix = None
            return

        # Create corpus: combine title, content, tags
        corpus = [
            f"{entry.title} {entry.content} {' '.join(entry.tags or [])}"
            for entry in self.entries
        ]

        try:
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        except ValueError:
            # Empty vocabulary (e.g., all stop words)
            self.tfidf_matrix = None

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[KnowledgeBaseEntry, float]]:
        """
        Search for entries matching query.

        Args:
            query: Search query string
            category: Optional category filter
            limit: Maximum number of results

        Returns:
            List of (entry, relevance_score) tuples, sorted by relevance (highest first)
        """
        if not self.entries or self.tfidf_matrix is None:
            return []

        if not query.strip():
            # Empty query: return empty results (consistent with simple search)
            return []

        # Filter by category first
        if category:
            filtered_entries = [e for e in self.entries if e.category == category]
            if not filtered_entries:
                return []

            # Rebuild index for filtered entries
            temp_engine = SearchEngine.__new__(SearchEngine)
            temp_engine.entries = filtered_entries
            temp_engine.vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=1000,
                ngram_range=(1, 2),
                min_df=1,
                lowercase=True
            )
            temp_engine.tfidf_matrix = None
            temp_engine._build_index()

            if temp_engine.tfidf_matrix is None:
                return []

            # Transform query and calculate similarity
            try:
                query_vec = temp_engine.vectorizer.transform([query])
                scores = cosine_similarity(query_vec, temp_engine.tfidf_matrix)[0]
            except ValueError:
                # Query contains only stop words or unknown terms
                return []

            # Sort by score descending
            indices = scores.argsort()[-limit:][::-1]
            return [
                (filtered_entries[i], float(scores[i]))
                for i in indices
                if scores[i] > 0
            ]
        else:
            # No category filter
            try:
                query_vec = self.vectorizer.transform([query])
                scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]
            except ValueError:
                # Query contains only stop words or unknown terms
                return []

            # Sort by score descending
            indices = scores.argsort()[-limit:][::-1]
            return [
                (self.entries[i], float(scores[i]))
                for i in indices
                if scores[i] > 0
            ]

    def rebuild_index(self, entries: List[KnowledgeBaseEntry]) -> None:
        """
        Rebuild index with new entries.

        Args:
            entries: Updated list of entries
        """
        self.entries = entries
        self._build_index()
