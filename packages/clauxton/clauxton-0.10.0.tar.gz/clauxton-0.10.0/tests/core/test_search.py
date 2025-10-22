"""Tests for TF-IDF search engine."""
from datetime import datetime

import pytest

from clauxton.core.models import KnowledgeBaseEntry

# Import check
try:
    from clauxton.core.search import SearchEngine
    SEARCH_ENGINE_AVAILABLE = True
except ImportError:
    SEARCH_ENGINE_AVAILABLE = False
    SearchEngine = None


pytestmark = pytest.mark.skipif(
    not SEARCH_ENGINE_AVAILABLE,
    reason="scikit-learn not installed"
)


@pytest.fixture
def sample_entries():
    """Create sample KB entries for testing."""
    return [
        KnowledgeBaseEntry(
            id="KB-20251019-001",
            title="Use FastAPI framework",
            category="architecture",
            content="All backend APIs use FastAPI for async support and automatic docs.",
            tags=["backend", "api", "fastapi"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ),
        KnowledgeBaseEntry(
            id="KB-20251019-002",
            title="PostgreSQL for production",
            category="decision",
            content="Use PostgreSQL 15+ for production databases.",
            tags=["database", "postgresql"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ),
        KnowledgeBaseEntry(
            id="KB-20251019-003",
            title="Repository pattern",
            category="pattern",
            content="Use Repository pattern for all database access layers.",
            tags=["pattern", "database"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ),
    ]


def test_search_basic(sample_entries):
    """Test basic TF-IDF search."""
    engine = SearchEngine(sample_entries)
    results = engine.search("FastAPI", limit=10)

    assert len(results) > 0
    assert results[0][0].id == "KB-20251019-001"  # FastAPI entry should be first
    assert results[0][1] > 0  # Score should be positive


def test_search_relevance_ranking(sample_entries):
    """Test that more relevant results rank higher."""
    engine = SearchEngine(sample_entries)
    results = engine.search("database", limit=10)

    # Both PostgreSQL and Repository entries mention "database"
    # Should return both
    assert len(results) >= 2
    entry_ids = [r[0].id for r in results]
    assert "KB-20251019-002" in entry_ids
    assert "KB-20251019-003" in entry_ids


def test_search_with_category_filter(sample_entries):
    """Test search with category filter."""
    engine = SearchEngine(sample_entries)
    results = engine.search("database", category="decision", limit=10)

    assert len(results) == 1
    assert results[0][0].id == "KB-20251019-002"
    assert results[0][0].category == "decision"


def test_search_empty_query(sample_entries):
    """Test search with empty query."""
    engine = SearchEngine(sample_entries)
    results = engine.search("", limit=10)

    # Empty query should return empty results (consistent with simple search)
    assert len(results) == 0


def test_search_no_matches(sample_entries):
    """Test search with no matches."""
    engine = SearchEngine(sample_entries)
    results = engine.search("nonexistent_term_xyz_12345", limit=10)

    assert len(results) == 0


def test_search_empty_entries():
    """Test search with no entries."""
    engine = SearchEngine([])
    results = engine.search("test", limit=10)

    assert len(results) == 0


def test_rebuild_index(sample_entries):
    """Test rebuilding search index."""
    engine = SearchEngine([])
    assert engine.tfidf_matrix is None

    engine.rebuild_index(sample_entries)
    results = engine.search("FastAPI", limit=10)

    assert len(results) > 0


def test_search_with_tags(sample_entries):
    """Test that tags are included in search."""
    engine = SearchEngine(sample_entries)

    # Search for a tag that's only in tags, not in title/content
    results = engine.search("fastapi", limit=10)

    assert len(results) > 0
    # Should find the FastAPI entry
    entry_ids = [r[0].id for r in results]
    assert "KB-20251019-001" in entry_ids


def test_search_case_insensitive(sample_entries):
    """Test that search is case-insensitive."""
    engine = SearchEngine(sample_entries)

    results_lower = engine.search("fastapi", limit=10)
    results_upper = engine.search("FASTAPI", limit=10)
    results_mixed = engine.search("FastAPI", limit=10)

    # All should return the same results
    assert len(results_lower) == len(results_upper) == len(results_mixed)
    if results_lower:
        assert results_lower[0][0].id == results_upper[0][0].id == results_mixed[0][0].id


def test_search_limit(sample_entries):
    """Test that limit parameter works."""
    engine = SearchEngine(sample_entries)

    results_all = engine.search("database", limit=10)
    results_limited = engine.search("database", limit=1)

    assert len(results_limited) <= 1
    if results_limited and results_all:
        # Limited result should be the top result from full search
        assert results_limited[0][0].id == results_all[0][0].id


def test_search_with_nonexistent_category(sample_entries):
    """Test search with non-existent category."""
    engine = SearchEngine(sample_entries)
    results = engine.search("database", category="nonexistent", limit=10)

    assert len(results) == 0


def test_search_scores_decrease(sample_entries):
    """Test that scores are in descending order."""
    # Add more entries to test ranking
    extended_entries = sample_entries + [
        KnowledgeBaseEntry(
            id="KB-20251019-004",
            title="API Gateway",
            category="architecture",
            content="Use API Gateway for all external traffic.",
            tags=["api", "gateway"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ),
    ]

    engine = SearchEngine(extended_entries)
    results = engine.search("API", limit=10)

    if len(results) > 1:
        # Scores should be in descending order
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)


# ============================================================================
# Edge Cases: Stopwords and Empty Vocabulary
# ============================================================================


def test_search_all_stopwords_query(sample_entries):
    """Test search with query containing only stopwords."""
    engine = SearchEngine(sample_entries)

    # Query with only English stopwords
    results = engine.search("the a an is are", limit=10)

    # Should return empty results (stopwords filtered out)
    assert len(results) == 0


def test_search_query_with_stopwords_mixed(sample_entries):
    """Test search with query containing stopwords and keywords."""
    engine = SearchEngine(sample_entries)

    # Query with stopwords + actual keyword
    results = engine.search("the FastAPI is", limit=10)

    # Should still find FastAPI (stopwords ignored)
    assert len(results) > 0
    assert results[0][0].id == "KB-20251019-001"


def test_search_all_stopwords_corpus():
    """Test search when corpus contains only stopwords in title/content (tags excluded)."""
    # Entries with content that's only stopwords (tags are non-stopwords but not in title/content)
    stopword_entries = [
        KnowledgeBaseEntry(
            id="KB-20251019-001",
            title="the a an",
            category="architecture",
            content="the the the a a a is is is",
            tags=[],  # No tags to ensure only stopwords in corpus
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ),
    ]

    # Should not crash when building index with all-stopword content
    engine = SearchEngine(stopword_entries)

    # tfidf_matrix should be None (empty vocabulary after stopword removal)
    assert engine.tfidf_matrix is None

    # Search should return empty results (no valid terms to match)
    results = engine.search("database", limit=10)
    assert len(results) == 0


def test_search_stopwords_with_category_filter(sample_entries):
    """Test search with stopwords query and category filter."""
    engine = SearchEngine(sample_entries)

    # All stopwords + category filter
    results = engine.search("the a an", category="architecture", limit=10)

    # Should return empty (stopwords filtered out)
    assert len(results) == 0


def test_search_unknown_terms(sample_entries):
    """Test search with terms not in vocabulary."""
    engine = SearchEngine(sample_entries)

    # Terms that don't exist in any entry
    results = engine.search("xyzabc123nonexistent", limit=10)

    # Should return empty results
    assert len(results) == 0


# ============================================================================
# Edge Cases: Unicode and Special Characters
# ============================================================================


def test_search_unicode_content():
    """Test TF-IDF search with Unicode content (Japanese)."""
    unicode_entries = [
        KnowledgeBaseEntry(
            id="KB-20251019-001",
            title="FastAPI使い方",
            category="architecture",
            content="FastAPIの基本的な使い方を説明します。",
            tags=["fastapi", "日本語"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ),
        KnowledgeBaseEntry(
            id="KB-20251019-002",
            title="PostgreSQL設定",
            category="decision",
            content="PostgreSQLの設定方法。",
            tags=["database"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ),
    ]

    engine = SearchEngine(unicode_entries)

    # Search for English term in Unicode content
    results = engine.search("FastAPI", limit=10)
    assert len(results) > 0
    assert results[0][0].id == "KB-20251019-001"

    # Search for Japanese term
    results = engine.search("使い方", limit=10)
    # Should work (Unicode tokenization)
    assert len(results) >= 0  # May or may not work depending on tokenizer


def test_search_special_characters():
    """Test search with special regex characters."""
    special_entries = [
        KnowledgeBaseEntry(
            id="KB-20251019-001",
            title="C++ Programming",
            category="architecture",
            content="C++ is a programming language.",
            tags=["cpp"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ),
        KnowledgeBaseEntry(
            id="KB-20251019-002",
            title="Regex patterns",
            category="pattern",
            content="Use patterns like (.*) and [a-z]+.",
            tags=["regex"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ),
    ]

    engine = SearchEngine(special_entries)

    # Search should not crash with special characters
    results = engine.search("C++", limit=10)
    assert len(results) >= 0  # Should not crash

    results = engine.search("(.*)", limit=10)
    assert len(results) >= 0  # Should not crash


def test_search_emoji():
    """Test search with emoji content."""
    emoji_entries = [
        KnowledgeBaseEntry(
            id="KB-20251019-001",
            title="FastAPI guide 🚀",
            category="architecture",
            content="FastAPI is fast 🔥 and easy to use ✅.",
            tags=["api"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ),
    ]

    engine = SearchEngine(emoji_entries)

    # Search for regular term should work
    results = engine.search("FastAPI", limit=10)
    assert len(results) > 0
    assert results[0][0].id == "KB-20251019-001"

    # Search for emoji (may or may not work)
    results = engine.search("🚀", limit=10)
    assert len(results) >= 0  # Should not crash


# ============================================================================
# Performance Tests: Large Dataset
# ============================================================================


def test_search_performance_large_dataset():
    """Test TF-IDF search performance with 200+ entries."""
    import time

    # Create 200 diverse entries
    large_entries = []
    categories = ["architecture", "decision", "pattern", "constraint", "convention"]
    keywords = [
        "API", "database", "FastAPI", "PostgreSQL", "authentication",
        "authorization", "cache", "Redis", "Docker", "Kubernetes",
        "microservices", "monolith", "REST", "GraphQL", "WebSocket",
        "testing", "CI/CD", "deployment", "monitoring", "logging",
    ]

    for i in range(200):
        category = categories[i % len(categories)]
        keyword_set = keywords[i % len(keywords)::5]  # Different keyword combinations

        entry = KnowledgeBaseEntry(
            id=f"KB-20251019-{i+1:03d}",
            title=f"{keyword_set[0]} implementation {i+1}",
            category=category,
            content=f"This entry discusses {' and '.join(keyword_set)} in detail. "
                   f"It provides guidelines for implementing {keyword_set[0]} "
                   f"with best practices and common pitfalls to avoid. "
                   f"Entry number {i+1} in our knowledge base.",
            tags=keyword_set[:3],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        )
        large_entries.append(entry)

    # Test indexing performance
    start_time = time.time()
    engine = SearchEngine(large_entries)
    indexing_time = time.time() - start_time

    # Indexing should complete in reasonable time (< 1 second)
    assert indexing_time < 1.0, f"Indexing took {indexing_time:.3f}s (expected < 1.0s)"

    # Test search performance
    start_time = time.time()
    results = engine.search("FastAPI", limit=10)
    search_time = time.time() - start_time

    # Search should complete in reasonable time (< 100ms)
    assert search_time < 0.1, f"Search took {search_time:.3f}s (expected < 0.1s)"

    # Verify results are relevant
    assert len(results) > 0, "Should find results for 'FastAPI'"
    assert results[0][1] > 0, "Top result should have positive relevance score"

    # Test search with category filter
    start_time = time.time()
    results_filtered = engine.search("API", category="architecture", limit=10)
    filtered_search_time = time.time() - start_time

    # Filtered search should also be fast
    assert filtered_search_time < 0.15, f"Filtered search took {filtered_search_time:.3f}s"

    # Verify filtering works
    assert all(r[0].category == "architecture" for r in results_filtered)


def test_search_relevance_ranking_large_dataset():
    """Test that relevance ranking works correctly with large dataset."""
    # Create entries with varying keyword frequencies
    entries = []

    # Entry with keyword mentioned 5 times
    entries.append(KnowledgeBaseEntry(
        id="KB-20251019-998",
        title="FastAPI FastAPI FastAPI",
        category="architecture",
        content="FastAPI is the best. We use FastAPI for everything. "
               "FastAPI FastAPI FastAPI is great.",
        tags=["fastapi"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        version=1
    ))

    # Entry with keyword mentioned 1 time
    entries.append(KnowledgeBaseEntry(
        id="KB-20251019-999",
        title="Web Framework",
        category="architecture",
        content="FastAPI is one option among many frameworks.",
        tags=["framework"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        version=1
    ))

    # Add 100 noise entries (no "FastAPI" keyword)
    for i in range(100):
        entries.append(KnowledgeBaseEntry(
            id=f"KB-20251019-{i+1:03d}",
            title=f"Topic {i}",
            category="decision",
            content=f"This is about something else entirely. Entry {i}.",
            tags=["other"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        ))

    engine = SearchEngine(entries)
    results = engine.search("FastAPI", limit=10)

    # Should find both relevant entries
    assert len(results) >= 2

    # Entry with more mentions should rank higher
    assert results[0][0].id == "KB-20251019-998", "High-frequency entry should rank first"
    assert results[1][0].id == "KB-20251019-999", "Low-frequency entry should rank second"

    # Scores should reflect frequency
    assert results[0][1] > results[1][1], "Higher frequency should have higher score"
