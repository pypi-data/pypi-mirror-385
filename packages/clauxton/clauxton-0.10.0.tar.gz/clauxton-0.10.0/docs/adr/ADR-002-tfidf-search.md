# ADR-002: TF-IDF for Knowledge Base Search

**Status**: Accepted
**Date**: 2025-01-20
**Deciders**: Clauxton Core Team

## Context

Clauxton Knowledge Base needs search functionality to help users find relevant entries. Users search by keywords or phrases and expect relevant results ranked by importance.

Requirements:
1. **Relevance Ranking**: Most relevant entries should appear first
2. **Multi-field Search**: Search across title, content, and tags
3. **Fast**: Results should appear quickly (<100ms for 100 entries)
4. **No Dependencies**: Should work without external services
5. **Graceful Degradation**: Fallback if dependencies unavailable

## Decision

Use **TF-IDF (Term Frequency-Inverse Document Frequency)** with cosine similarity for relevance-ranked search.

Implementation:
- `scikit-learn` for TF-IDF vectorization
- Cosine similarity for ranking
- Fallback to keyword matching if scikit-learn unavailable

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(corpus)
query_vec = vectorizer.transform([query])
scores = cosine_similarity(query_vec, tfidf_matrix)[0]
```

## Consequences

### Positive

1. **Relevance Ranking**:
   - Better results than simple keyword matching
   - Automatically weights rare terms higher
   - Considers term frequency in documents

2. **Multi-field Support**:
   - Concatenate title + content + tags into single corpus
   - Weighted by field importance (title × 3, tags × 2)

3. **No Setup**:
   - Pure Python implementation
   - No external services (Elasticsearch, etc.)
   - Works offline

4. **Fast Enough**:
   - <10ms for 100 entries
   - <100ms for 1,000 entries
   - Acceptable for target use case

5. **Proven Algorithm**:
   - Well-understood and widely used
   - Extensive documentation and resources

### Negative

1. **Dependency**:
   - Requires `scikit-learn` (large library)
   - **Mitigation**: Fallback to keyword search

2. **Scalability**:
   - Recomputes TF-IDF matrix on every search
   - Not suitable for >10,000 entries
   - **Mitigation**: Target use case is <1,000 entries

3. **No Semantic Understanding**:
   - Doesn't understand synonyms ("API" ≠ "endpoint")
   - Doesn't understand context
   - **Mitigation**: Good enough for technical keywords

4. **Language-Specific**:
   - No stemming/lemmatization by default
   - English-centric tokenization
   - **Mitigation**: Users use consistent technical terms

## Alternatives Considered

### 1. Simple Keyword Matching

**Pros**:
- No dependencies
- Very fast
- Easy to understand

**Cons**:
- No relevance ranking
- Poor results for multi-word queries
- Doesn't handle synonyms

**Why Rejected**: Poor result quality. However, kept as fallback.

### 2. Full-Text Search (Elasticsearch, Lucene)

**Pros**:
- Best search quality
- Advanced features (fuzzy matching, highlighting)
- Scales to millions of documents

**Cons**:
- Requires external service setup
- Overkill for <1,000 entries
- Breaks "no setup" requirement

**Why Rejected**: Too much overhead for target use case.

### 3. Semantic Search (Embeddings + Vector DB)

**Pros**:
- Understands context and synonyms
- Best for natural language queries
- State-of-the-art results

**Cons**:
- Requires ML models (large dependencies)
- Slower (model inference)
- Requires GPU for good performance
- Overkill for technical keyword search

**Why Rejected**: Too complex for current needs. Consider for v2.0.

### 4. Regular Expressions

**Pros**:
- No dependencies
- Powerful pattern matching
- Precise control

**Cons**:
- Poor user experience (users must know regex)
- No relevance ranking
- Doesn't work for natural language

**Why Rejected**: Not user-friendly.

### 5. BM25 (Best Match 25)

**Pros**:
- Better than TF-IDF for some use cases
- Tunable parameters
- Used by Elasticsearch

**Cons**:
- Requires additional library (`rank-bm25`)
- More complex implementation
- Marginal improvement over TF-IDF

**Why Rejected**: TF-IDF is simpler and "good enough".

## Implementation Notes

### Weighted Multi-field Search

```python
def create_search_corpus(entries):
    corpus = []
    for entry in entries:
        # Weight fields: title × 3, tags × 2, content × 1
        text = (
            entry.title * 3 + " " +
            " ".join(entry.tags) * 2 + " " +
            entry.content
        )
        corpus.append(text)
    return corpus
```

### Graceful Degradation

```python
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    USE_TFIDF = True
except ImportError:
    USE_TFIDF = False

def search(query):
    if USE_TFIDF:
        return tfidf_search(query)
    else:
        return keyword_search(query)  # Fallback
```

### Performance Optimization

```python
# Cache vectorizer and matrix if entries haven't changed
if self._corpus_hash == compute_hash(entries):
    # Use cached matrix
    query_vec = self._vectorizer.transform([query])
else:
    # Rebuild matrix
    self._build_tfidf_matrix(entries)
```

## Future Considerations

1. **Caching**: Cache TF-IDF matrix between searches (current: rebuild every time)
2. **Stemming**: Add stemming/lemmatization for better results
3. **Synonyms**: Maintain synonym dictionary for technical terms
4. **Embeddings**: Consider semantic search for v2.0 (if users request)
5. **Filters**: Add filter support (category, date range, tags)

## Performance Benchmarks

| Entries | Build Matrix | Search | Total |
|---------|--------------|--------|-------|
| 10      | <1ms         | <1ms   | <2ms  |
| 100     | ~5ms         | <5ms   | ~10ms |
| 1,000   | ~50ms        | <10ms  | ~60ms |
| 10,000  | ~500ms       | ~50ms  | ~550ms|

**Conclusion**: Acceptable for target use case (<1,000 entries).

## References

- [TF-IDF Explanation](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- [scikit-learn TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- [Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
- [Information Retrieval Algorithms](https://nlp.stanford.edu/IR-book/)
