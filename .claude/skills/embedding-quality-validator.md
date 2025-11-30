---
name: embedding-quality-validator
description: Validate embedding and chunking quality for RAG systems. Use after generating embeddings and before storing in vector database to ensure semantic coherence, proper chunk boundaries, and retrieval accuracy.
---

# Skill: Embedding Quality Validator

**Version**: 1.0.0
**Created**: 2025-11-28
**Category**: Quality Assurance
**Decision Points**: 4

## Description

This skill provides a systematic framework for validating the quality of document chunking and embeddings in RAG pipelines. It ensures chunks are semantically complete, embeddings capture meaning accurately, and retrieval will perform well.

## When to Use This Skill

**Apply this skill when:**
- After chunking documents but before generating embeddings
- After generating embeddings but before storing in vector database
- When debugging poor retrieval quality ("why didn't it find the right answer?")
- When onboarding new content types (code, tables, diagrams)
- During RAG pipeline development and testing

**Skip this skill when:**
- Using pre-validated chunking strategies (standard patterns already tested)
- Working with tiny corpora (<100 chunks) where manual inspection is feasible
- In production after validation is automated in CI/CD

## Persona

You are a quality auditor for semantic search systems who thinks about chunk quality the way a proofreader thinks about sentence structure:

- **Semantic completeness**: Does this chunk make sense in isolation?
- **Boundary integrity**: Are chunks split at natural boundaries (paragraphs, sections)?
- **Context preservation**: Does overlap maintain coherence without excessive duplication?
- **Retrieval testability**: Can I write queries that should match this chunk?

Your goal: Catch chunking and embedding issues before they cause retrieval failures in production.

## Analytical Questions

Before approving embeddings for production, analyze:

### 1. **Chunk Semantic Completeness**
- Can each chunk be understood without reading adjacent chunks?
- Are chunks split mid-sentence or mid-thought?
- Do code blocks start and end cleanly (no partial functions)?
- Are lists and tables kept intact or split meaningfully?

### 2. **Overlap Strategy Validation**
- Does overlap preserve context between chunks?
- Is overlap excessive (>30% causing storage bloat)?
- Is overlap insufficient (<10% losing continuity)?
- Are overlapping sections semantically meaningful (not random tokens)?

### 3. **Embedding Quality Assessment**
- Do semantically similar chunks have high cosine similarity (>0.75)?
- Do semantically different chunks have low similarity (<0.5)?
- Are embeddings capturing domain-specific terminology correctly?
- Are code embeddings distinguishable from text embeddings when needed?

### 4. **Retrieval Accuracy Testing**
- For 5-10 test queries, are the correct chunks in top-3 results?
- What is the average similarity score for correct matches? (should be >0.7)
- Are there false positives (irrelevant chunks ranking high)?
- Are there false negatives (relevant chunks missing from top-10)?

## Decision Principles

Apply these validation criteria:

### 1. **Chunk Completeness Standard**

```python
# Test: Random sample 20 chunks, manually review

PASS if:
✅ First sentence of chunk makes sense (no mid-thought starts)
✅ Last sentence of chunk concludes properly (no mid-thought cuts)
✅ Code blocks are syntactically complete (can be parsed)
✅ Tables/lists are intact or split at row/item boundaries

FAIL if:
❌ Chunks start with pronouns without antecedents ("It does X" - what is "it"?)
❌ Chunks end mid-sentence or mid-code-block
❌ Technical terms introduced without context (first use, no definition)
```

**How to fix**: Adjust chunk size, change split strategy (semantic vs fixed-size), add more context to chunk boundaries.

### 2. **Overlap Validation Standard**

```python
# Test: Calculate overlap percentage for 20 random chunk pairs

target_overlap_percentage = 15  # 10-20% is optimal

PASS if:
✅ Average overlap is 10-20% of chunk size
✅ Overlapping content is semantically meaningful (complete sentences)
✅ No duplicate chunks (100% overlap except at boundaries)

FAIL if:
❌ Overlap <5% (context loss risk)
❌ Overlap >30% (storage waste, duplicate results)
❌ Overlapping content is mid-sentence fragments
```

**How to fix**: Adjust overlap token count, use sentence-aware splitting, deduplicate exact matches.

### 3. **Semantic Similarity Standard**

```python
# Test: Calculate intra-chapter vs inter-chapter similarity

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

embeddings_chapter_1 = [...]  # Embeddings for all chunks in Chapter 1
embeddings_chapter_2 = [...]  # Embeddings for all chunks in Chapter 2

intra_similarity = np.mean(cosine_similarity(embeddings_chapter_1))
inter_similarity = np.mean(cosine_similarity(embeddings_chapter_1, embeddings_chapter_2))

PASS if:
✅ Intra-chapter similarity (related content) > 0.75
✅ Inter-chapter similarity (different topics) < 0.6
✅ Clear separation: intra > inter + 0.15 margin

FAIL if:
❌ Intra-chapter similarity < 0.7 (embeddings not capturing semantic relationships)
❌ Inter-chapter similarity > 0.7 (embeddings too generic, not distinguishing topics)
❌ No clear boundary (intra ≈ inter)
```

**How to fix**: Use domain-specific embedding model, add metadata context to chunks, verify content is actually semantically distinct.

### 4. **Retrieval Accuracy Standard**

```python
# Test: Define test queries with expected results

test_cases = [
    {
        "query": "How to create a ROS2 publisher in Python?",
        "expected_chunks": ["chapter-4-section-2-publishers"],
        "min_similarity": 0.8,
        "max_rank": 3  # Must appear in top-3
    },
    {
        "query": "What is the difference between topics and services?",
        "expected_chunks": ["chapter-5-overview"],
        "min_similarity": 0.75,
        "max_rank": 3
    },
    # 5-10 test cases covering diverse queries
]

PASS if:
✅ Precision@3 > 0.8 (80% of test cases have correct chunk in top-3)
✅ Average similarity for correct matches > 0.75
✅ No false positives with similarity > 0.8 (irrelevant chunks shouldn't rank high)

FAIL if:
❌ Precision@3 < 0.7
❌ Correct chunks consistently rank below position 5
❌ Average similarity < 0.7 (weak signal)
```

**How to fix**: Adjust chunking (preserve more context), use hybrid search (keyword + semantic), add metadata filtering, retune retrieval parameters (top-k, threshold).

## Usage Example

**Scenario**: Validate embeddings for Physical AI textbook before deploying RAG chatbot

**Invocation**:
```
I've generated embeddings for 13 chapters of the Physical AI textbook (2,847 chunks).
Before deploying, I want to validate quality using the embedding-quality-validator skill.

Context:
- Chunking: 1024 tokens, 128 token overlap, split on section boundaries
- Embedding model: text-embedding-3-small (1536 dimensions)
- Content types: Educational text (88%), Python code (12%)

Help me run the 4-step validation:
1. Chunk completeness (sample 20 chunks)
2. Overlap validation (check percentage)
3. Semantic similarity (intra vs inter-chapter)
4. Retrieval accuracy (run test queries)
```

**Expected Analysis**:

```markdown
## Embedding Quality Validation Report

### 1. Chunk Completeness ✅ PASS
**Sample**: 20 random chunks reviewed

- ✅ 18/20 chunks start with complete sentences
- ✅ 19/20 chunks end cleanly (no mid-sentence cuts)
- ✅ All 6 code chunks are syntactically complete (parsed successfully)
- ⚠️ 2 chunks start with "This" without clear antecedent (minor issue)

**Verdict**: PASS (90% clean, issues are edge cases)

### 2. Overlap Validation ✅ PASS
**Analysis**: 50 chunk pairs analyzed

- Average overlap: 16.2% ✅ (target: 10-20%)
- Overlapping content: Complete sentences ✅
- No 100% duplicates found ✅

**Verdict**: PASS (optimal overlap range)

### 3. Semantic Similarity ✅ PASS
**Intra-chapter similarity**: 0.82 ✅ (related content clusters well)
**Inter-chapter similarity**: 0.47 ✅ (different topics clearly separated)
**Separation margin**: 0.35 ✅ (clear boundaries)

**Verdict**: PASS (embeddings capture semantic structure correctly)

### 4. Retrieval Accuracy ✅ PASS
**Test queries**: 10 queries across different chapters

- Precision@3: 0.90 ✅ (9/10 queries found correct chunk in top-3)
- Average similarity: 0.81 ✅ (strong matches)
- False positive rate: 0% ✅ (no irrelevant high-ranking chunks)

**Verdict**: PASS (excellent retrieval performance)

## Overall Assessment: ✅ READY FOR PRODUCTION

**Strengths**:
- Semantic boundaries are clear (intra vs inter-chapter)
- Retrieval accuracy exceeds targets
- Chunk quality is high

**Minor Issues**:
- 2 chunks with pronoun antecedent ambiguity (acceptable for 2,847 total chunks)

**Recommendation**: Deploy to production. Monitor retrieval metrics in first week.
```

## Self-Check Validation

After applying this skill, verify:

- [ ] **Chunk completeness tested**: Manually reviewed 20+ random chunks for semantic integrity
- [ ] **Overlap calculated**: Measured overlap percentage and confirmed 10-20% range
- [ ] **Semantic similarity analyzed**: Compared intra vs inter-chapter/topic similarity with >0.15 margin
- [ ] **Retrieval tested**: Ran 5-10 test queries and measured precision@3 > 0.8
- [ ] **Issues documented**: Any failures have root cause analysis and fix recommendations

## Common Issues and Fixes

### Issue: Chunks start mid-thought ("It does this..." - what is "it"?)
**Fix**: Increase chunk size to capture more context, or use sentence-aware splitting that includes preceding sentence.

### Issue: Code blocks are split mid-function
**Fix**: Use language-aware chunking (langchain.text_splitter for code), preserve complete functions.

### Issue: Low intra-chapter similarity (<0.7)
**Fix**: Content may actually be diverse (acceptable), or embedding model is too generic (try domain-specific model).

### Issue: High inter-chapter similarity (>0.7)
**Fix**: Content overlap between chapters (acceptable), or embeddings not capturing nuances (add metadata context, use better model).

### Issue: Test queries don't retrieve correct chunks
**Fix**:
1. Check if chunks actually contain answer (chunking issue)
2. Try hybrid search (semantic + keyword)
3. Adjust similarity threshold
4. Add metadata filtering (chapter, section)
5. Consider query rewriting for normalization

---

**Key Principle**: Quality validation is not pass/fail. It's about understanding where your RAG system will succeed and where it might struggle, so you can set expectations and optimize strategically.
