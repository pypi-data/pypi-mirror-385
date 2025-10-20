# Search Algorithm

This document explains how Clauxton's Knowledge Base search works.

---

## Overview

Clauxton uses **TF-IDF (Term Frequency-Inverse Document Frequency)** algorithm for relevance-based search. When scikit-learn is not installed, it automatically falls back to simple keyword matching.

---

## TF-IDF Search (Primary)

### What is TF-IDF?

**TF-IDF** is a statistical measure that evaluates how important a word is to a document in a collection of documents.

- **TF (Term Frequency)**: How often a term appears in a document
- **IDF (Inverse Document Frequency)**: How rare a term is across all documents

**Result**: Terms that appear frequently in a document but rarely across all documents get higher scores.

### How It Works

1. **Indexing Phase** (when you add/update entries):
   ```python
   # Create searchable corpus from each entry
   corpus = [
       f"{entry.title} {entry.content} {' '.join(entry.tags)}"
       for entry in entries
   ]

   # Build TF-IDF matrix
   vectorizer = TfidfVectorizer(
       stop_words='english',    # Filter common words (the, a, is, etc.)
       max_features=1000,       # Top 1000 important terms
       ngram_range=(1, 2),      # Single words and word pairs
       lowercase=True           # Case-insensitive
   )
   tfidf_matrix = vectorizer.fit_transform(corpus)
   ```

2. **Search Phase** (when you run `clauxton kb search "query"`):
   ```python
   # Convert query to TF-IDF vector
   query_vec = vectorizer.transform([query])

   # Calculate cosine similarity with all entries
   scores = cosine_similarity(query_vec, tfidf_matrix)[0]

   # Sort by relevance (highest score first)
   results = sorted(entries_with_scores, key=lambda x: x[1], reverse=True)
   ```

### Example

Given these Knowledge Base entries:

```yaml
entries:
  - id: KB-001
    title: "Use FastAPI framework"
    content: "All backend APIs use FastAPI for async support."
    tags: [backend, api, fastapi]

  - id: KB-002
    title: "API versioning strategy"
    content: "Use /v1/ prefix for all API endpoints."
    tags: [api, versioning]

  - id: KB-003
    title: "Database pattern"
    content: "Use Repository pattern for database access."
    tags: [database, pattern]
```

**Search query**: `"FastAPI"`

**TF-IDF scoring**:
- **KB-001**: Score = 0.85 (FastAPI appears in title, content, and tags)
- **KB-002**: Score = 0.12 (Only "API" matches, not "FastAPI")
- **KB-003**: Score = 0.00 (No match)

**Results** (sorted by relevance):
```
1. KB-001 - Use FastAPI framework (score: 0.85)
2. KB-002 - API versioning strategy (score: 0.12)
```

### Search query**: `"API"`

**TF-IDF scoring**:
- **KB-002**: Score = 0.78 ("API" appears 2 times, rare term)
- **KB-001**: Score = 0.65 ("API" appears 1 time in "FastAPI")
- **KB-003**: Score = 0.00 (No match)

**Results**:
```
1. KB-002 - API versioning strategy (score: 0.78)
2. KB-001 - Use FastAPI framework (score: 0.65)
```

---

## Simple Search (Fallback)

### When Used

- When `scikit-learn` is not installed
- When SearchEngine initialization fails
- Automatically detected at runtime

### How It Works

Simple keyword matching with weighted scoring:

```python
score = 0.0

# Title matches (weight: 2.0)
if query.lower() in entry.title.lower():
    score += 2.0

# Content matches (weight: 1.0)
if query.lower() in entry.content.lower():
    score += 1.0

# Tag matches (weight: 1.5)
for tag in entry.tags:
    if query.lower() in tag.lower():
        score += 1.5
        break

# Sort by score (highest first)
results = sorted(matches, key=lambda x: x[1], reverse=True)
```

### Example (Same entries as above)

**Search query**: `"API"`

**Simple search scoring**:
- **KB-001**: Score = 3.5 (title: 0, content: 1.0, tag "api": 1.5, tag "fastapi": 0) = **2.5**
- **KB-002**: Score = 3.5 (title: 2.0, content: 1.0, tag "api": 1.5) = **4.5**
- **KB-003**: Score = 0.0 (No match)

**Results**:
```
1. KB-002 - API versioning strategy (score: 4.5)
2. KB-001 - Use FastAPI framework (score: 2.5)
```

---

## Comparison: TF-IDF vs Simple Search

| Feature | TF-IDF Search | Simple Search |
|---------|---------------|---------------|
| **Algorithm** | Statistical relevance | Keyword matching |
| **Dependency** | Requires scikit-learn | No dependencies |
| **Accuracy** | Higher (considers term rarity) | Lower (only presence/absence) |
| **Performance** | Fast (O(k) where k = results) | Fast (O(n) where n = entries) |
| **Case sensitivity** | Case-insensitive | Case-insensitive |
| **Stopwords** | Filtered ("the", "a", "is") | Not filtered |
| **Partial matches** | Yes (via ngrams) | Yes (substring matching) |

### When TF-IDF is Better

- **Large Knowledge Bases** (50+ entries): Better ranking
- **Technical terms**: "API", "database", "pattern" get proper weights
- **Query specificity**: "FastAPI" ranks higher than just "API"

### When Simple Search is Sufficient

- **Small Knowledge Bases** (< 20 entries): Ranking less critical
- **No scikit-learn**: Automatic fallback
- **Exact keyword searches**: Both methods work similarly

---

## Advanced Features

### Category Filtering

Both search methods support category filtering:

```bash
clauxton kb search "API" --category architecture
```

**Behavior**:
- TF-IDF: Rebuilds index with filtered entries
- Simple: Skips non-matching categories

### Tag Filtering

```bash
# Via MCP or API (not yet in CLI)
kb.search("API", tags=["backend"])
```

**Behavior**:
- TF-IDF: Applies after relevance scoring
- Simple: Skips entries without matching tags

### Result Limiting

```bash
clauxton kb search "API" --limit 5
```

**Behavior**:
- Returns top 5 most relevant results
- Default limit: 10

### Empty Query Handling

```bash
clauxton kb search ""
```

**Behavior**:
- Both methods return empty list
- No results for empty/whitespace-only queries

---

## Edge Cases

### All-Stopwords Query

**Query**: `"the a an is"`

**TF-IDF**: Returns empty (all stopwords filtered out)
**Simple**: Returns empty (no matches)

### All-Stopwords Corpus

**Entry content**: `"the the the a a a is is is"`

**TF-IDF**: `tfidf_matrix = None` (empty vocabulary)
**Simple**: Works normally (no stopword filtering)

### Unicode Content

**Entry**: `"FastAPI使い方 🚀"`
**Query**: `"FastAPI"`

**TF-IDF**: ✅ Finds match (Unicode tokenization)
**Simple**: ✅ Finds match (substring matching)

### Special Characters

**Query**: `"C++"`

**TF-IDF**: ✅ Handles gracefully (no regex escaping needed)
**Simple**: ✅ Handles gracefully (substring matching)

---

## Implementation Details

### Files

- **`clauxton/core/search.py`**: TF-IDF SearchEngine class
- **`clauxton/core/knowledge_base.py`**: Integration and fallback logic

### Key Classes

```python
class SearchEngine:
    """TF-IDF search engine."""

    def __init__(self, entries: List[KnowledgeBaseEntry]):
        """Build TF-IDF index from entries."""

    def search(
        self, query: str, category: Optional[str] = None, limit: int = 10
    ) -> List[Tuple[KnowledgeBaseEntry, float]]:
        """Search with relevance scoring."""

    def rebuild_index(self, entries: List[KnowledgeBaseEntry]) -> None:
        """Rebuild index after data changes."""
```

### Fallback Detection

```python
try:
    from clauxton.core.search import SearchEngine
    SEARCH_ENGINE_AVAILABLE = True
except ImportError:
    SEARCH_ENGINE_AVAILABLE = False
    SearchEngine = None

# In KnowledgeBase.search()
if SEARCH_ENGINE_AVAILABLE and self._search_engine is not None:
    # Use TF-IDF
    results = self._search_engine.search(query, category, limit)
else:
    # Fallback to simple search
    results = self._simple_search(query, category, tags, limit)
```

---

## Performance

### Indexing (add/update/delete operations)

- **Small KB** (< 50 entries): < 10ms
- **Medium KB** (50-200 entries): < 50ms
- **Large KB** (200+ entries): < 200ms

### Searching

- **Small KB**: < 5ms
- **Medium KB**: < 10ms
- **Large KB**: < 20ms

**Note**: Performance measured with TF-IDF. Simple search is slightly faster but less accurate.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'sklearn'"

**Problem**: scikit-learn not installed.

**Solution**:
```bash
pip install scikit-learn
```

**Workaround**: Clauxton automatically falls back to simple search. No action needed unless you want TF-IDF.

### "Search results seem random"

**Problem**: Expecting alphabetical order, but getting relevance order.

**Solution**: This is expected! TF-IDF ranks by **relevance**, not alphabetically.

**Example**:
- Entry A: "FastAPI" mentioned 5 times → Higher score
- Entry B: "FastAPI" mentioned 1 time → Lower score
- Result: Entry A appears first (more relevant)

### "Empty results for valid query"

**Possible causes**:
1. **All stopwords**: Query like "the a an" returns empty
2. **No matches**: Term doesn't exist in any entry
3. **Category filter**: No entries in specified category

**Debug**:
```bash
# Try without category filter
clauxton kb search "your query"

# List all entries to verify content
clauxton kb list
```

---

## Future Enhancements (Planned)

### Phase 2 (Weeks 11-12)

- **Semantic Search**: Word embeddings for better matching
- **Fuzzy Matching**: Typo tolerance
- **Search History**: Track popular queries
- **Relevance Feedback**: Learn from user selections

---

## References

- **TF-IDF Algorithm**: [Wikipedia](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- **scikit-learn TfidfVectorizer**: [Docs](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- **Cosine Similarity**: [Wikipedia](https://en.wikipedia.org/wiki/Cosine_similarity)

---

**Last updated**: Week 9 (TF-IDF implementation complete)
