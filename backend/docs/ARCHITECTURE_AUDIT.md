# Architecture Audit Report — Legal Information Assistance System

**Generated**: July 24, 2026
**Purpose**: Production-grade refactoring audit covering entire codebase
**Scope**: Full system audit for clean architecture, SOLID principles, security, performance

---

## Executive Summary

This audit identifies critical issues requiring immediate attention:

1. **Duplicate chunking implementations** - Two competing chunkers (`chunking.py` vs `chunking_v2.py`)
2. **Chunk ID collision risk** - Non-unique IDs for chunks within same article
3. **Unsafe OCR corrections** - Global replacements can corrupt legal meaning
4. **Incomplete page mapping** - `pass` statement in production code
5. **Mutable dataclass defaults** - Type safety violations
6. **Inconsistent document types** - Database vs chunker mismatch
7. **Database model redundancy** - Duplicate hierarchy fields
8. **Stateful chunker** - Context leakage between documents
9. **Broad exception handling** - Error swallowing
10. **Missing test coverage** - No unit tests for critical legal parsing

---

## Current Architecture

### Project Structure

```
backend/
├── config/                    # Django settings, URLs, WSGI/ASGI
│   ├── settings/             # Environment-specific settings
│   ├── urls.py               # Root URL configuration
│   └── celery_app.py         # Celery configuration
├── legal_information_assistance_system/
│   ├── legal_ai/            # Main legal AI app
│   │   ├── services/        # Business logic layer
│   │   ├── api/             # REST API views/serializers
│   │   ├── management/      # Django management commands
│   │   ├── models.py        # Database models
│   │   ├── admin.py         # Admin interface
│   │   ├── clarification/   # Clarification handling
│   │   ├── conversations/   # Conversation management
│   │   ├── knowledge_gaps/ # Knowledge gap detection
│   │   └── understanding/  # Query understanding
│   └── users/              # User management app
├── scraper/                # Scrapy web scraper
├── media/                  # User uploads
├── faiss_store/           # FAISS vector index storage
└── tests/                 # Test files
```

### Django Apps

1. **legal_ai** - Core legal document processing and RAG
2. **users** - User authentication and profiles (django-allauth based)

### Data Flow

```
PDF Upload → Extract Text → Clean Text → Chunk → Embed → FAISS Index → Retrieve → RAG → Answer
```

### Services Layer

| Service | Responsibility | Status |
|---------|---------------|--------|
| `pdf_loader.py` | PDF text extraction with OCR fallback | ✅ Working |
| `text_cleaning.py` | Text normalization and artifact removal | ✅ Working |
| `nepali_font_converter.py` | Legacy font to Unicode conversion | ✅ Working |
| `chunking.py` | OLD chunking implementation | ⚠️ Duplicate |
| `chunking_v2.py` | NEW advanced chunking | ✅ Active |
| `embedding.py` | SentenceTransformer embeddings | ✅ Working |
| `retrieval.py` | FAISS vector search | ✅ Working |
| `hybrid_retrieval.py` | Dense + lexical hybrid search | ✅ Working |
| `reranker.py` | Result reranking | ✅ Working |
| `rag.py` | RAG orchestration pipeline | ✅ Working |
| `llm.py` | LLM integration | ✅ Working |
| `ingestion.py` | Document processing pipeline | ✅ Working |

---

## Critical Issues

### 1. Duplicate Chunking Implementations

**Problem**: Two chunking implementations exist:
- `chunking.py` - Contains `LegalChunker` and `SmartLegalChunker` (alias)
- `chunking_v2.py` - Contains `AdvancedLegalChunker` with OCR correction

**Usage Analysis**:
- `ingestion.py` imports and uses `AdvancedLegalChunker` from `chunking_v2.py`
- `chunking.py` appears unused in production code
- Tests reference both implementations

**Impact**: Code duplication, maintenance burden, potential confusion

**Recommendation**: Remove `chunking.py`, consolidate to single canonical chunker

---

### 2. Chunk ID Collision Risk

**Problem**: `generate_chunk_id()` in `chunking_v2.py` can generate identical IDs:

```python
def generate_chunk_id(document_name, part, chapter, article, clause, schedule, annex):
    # Returns same ID for multiple chunks under same article
    return f"{doc_slug}-part-{part}-chapter-{chapter}-article-{article}"
```

**Impact**: Multiple chunks within same article receive identical IDs, breaking uniqueness constraints

**Recommendation**: Add chunk sequence number or content hash to ensure uniqueness

---

### 3. Unsafe OCR Corrections

**Problem**: `OCR_CORRECTIONS` dictionary contains aggressive global replacements:

```python
OCR_CORRECTIONS = {
    "रािः": "राज्यः",  # Could corrupt valid text
    "राि": "राज्य",
    # ... 100+ corrections
}
```

**Issues**:
- No confidence tracking
- No audit trail
- Substring replacements can corrupt unrelated words
- No validation of correction accuracy
- Applied silently without user awareness

**Impact**: Legal meaning can be silently corrupted

**Recommendation**: Implement safe OCR correction with:
- Separate source/corrected text storage
- Correction confidence scoring
- Audit trail
- Configurable correction rules
- Never modify original source text

---

### 4. Incomplete Page Mapping

**Problem**: `chunking_v2.py` contains:

```python
if page_mapping:
    pass  # TODO: implement
```

**Impact**: Source page tracking not functional, citations cannot reference page numbers

**Recommendation**: Implement proper character offset to page mapping

---

### 5. Mutable Dataclass Defaults

**Problem**: `ChunkMetadata` dataclass has unsafe defaults:

```python
@dataclass
class ChunkMetadata:
    hierarchy_path: List[str] = None  # Should use default_factory
```

**Impact**: Type safety violation, potential shared state bugs

**Recommendation**: Use `field(default_factory=list)` for mutable defaults

---

### 6. Document Type Inconsistency

**Problem**: Database model uses:

```python
DOCUMENT_TYPES = [
    ("constitution", "Constitution"),
    ("civil_code", "National Civil Code"),
    ("criminal_code", "Criminal Code"),
    ("act", "Act"),
    ...
]
```

But chunker defaults to:

```python
def __init__(self, document_type: str = "Act"):
```

**Impact**: Inconsistent document type handling

**Recommendation**: Use canonical internal values, pass actual database document type

---

### 7. Database Model Redundancy

**Problem**: `LegalChunk` model has duplicate hierarchy fields:

```python
# Legacy fields
part = models.CharField(max_length=255, blank=True)
chapter = models.CharField(max_length=255, blank=True)
section = models.CharField(max_length=255, blank=True)
article = models.CharField(max_length=255, blank=True)
dhara = models.CharField(max_length=255, blank=True)

# New advanced fields
part_number = models.CharField(max_length=50, blank=True, null=True)
part_title = models.CharField(max_length=500, blank=True, null=True)
chapter_number = models.CharField(max_length=50, blank=True, null=True)
chapter_title = models.CharField(max_length=500, blank=True, null=True)
# ... more duplicates
```

**Impact**: Storage redundancy, confusion about which fields to use

**Recommendation**: Deprecate legacy fields, migrate to canonical representation

---

### 8. Stateful Chunker

**Problem**: `AdvancedLegalChunker` stores mutable context:

```python
class AdvancedLegalChunker:
    def __init__(self, ...):
        self.context: Dict[str, Optional[str]] = {...}
    
    def _parse_header(self, header: str):
        # Mutates self.context
```

**Impact**: State leakage if chunker instance reused across documents

**Recommendation**: Make chunker stateless, reset context per document

---

### 9. Broad Exception Handling

**Problem**: Multiple instances of:

```python
except Exception:
    pass
```

**Impact**: Errors swallowed, debugging difficult

**Recommendation**: Use specific exceptions, proper logging, error tracking

---

### 10. Missing Test Coverage

**Problem**: No unit tests for:
- Nepali digit normalization
- OCR correction accuracy
- Header detection accuracy
- Article parsing
- Section parsing
- Schedule/Annex parsing
- Chunk ID uniqueness
- Content hashing
- Citation generation

**Impact**: Critical legal parsing logic untested

**Recommendation**: Add comprehensive test suite

---

## Security Issues

| Risk | Severity | Location | Mitigation |
|------|----------|----------|------------|
| `CORS_ALLOW_ALL_ORIGINS = True` | High | `settings/base.py` | Restrict to specific domains |
| `DEBUG = env.bool("DJANGO_DEBUG", False)` | Medium | `settings/base.py` | Ensure False in production |
| No rate limiting on API | Medium | API views | Add throttling |
| No input validation on PDF uploads | High | Upload API | Validate file types, sizes |
| Prompt injection from documents | High | RAG pipeline | Sanitize document text |
| SQL injection risk | Low | ORM usage | Use parameterized queries (already done) |
| Path traversal in file uploads | Medium | FileField | Validate filenames |

---

## Performance Issues

| Issue | Location | Impact | Recommendation |
|-------|----------|--------|----------------|
| FAISS rebuild per document | `ingestion.py` | Slow processing | Batch rebuild |
| N+1 queries in retrieval | `retrieval.py` | Slow search | Use `select_related` |
| No database indexes on metadata | `models.py` | Slow filtering | Add composite indexes |
| Embedding model loaded repeatedly | `embedding.py` | Memory | Already cached with `lru_cache` |
| SQLite for production | `settings/base.py` | Scalability | Use PostgreSQL |

---

## Code Quality Issues

### Dead Code

- `chunking.py` - Unused chunking implementation
- Multiple test files in root: `test_*.py` - Should be in `tests/` directory
- Commented-out code in settings

### Unused Imports

Found in multiple files (TODO: specific cleanup needed)

### Inconsistent Naming

- `section` vs `dhara` for same concept
- `article` vs `अनुच्छेद` inconsistency
- Mixed English/Nepali in variable names

### Type Safety

- Missing type hints in many functions
- `Optional` used inconsistently
- No static type checking configured

---

## Dependency Issues

### Requirements Analysis

**Current dependencies** (from `requirements.txt`):
- Django 4.x
- sentence-transformers
- faiss-cpu
- pypdf
- PyMuPDF (optional)
- pytesseract (optional)
- celery
- redis
- django-allauth
- djangorestframework
- drf-spectacular

**Issues**:
- Some dependencies optional but not clearly documented
- Version pinning inconsistent
- Some dependencies may be unused

**Recommendation**: Audit and clean up requirements

---

## Files Requiring Migration

### High Priority

1. **chunking.py** - Remove duplicate implementation
2. **chunking_v2.py** - Fix chunk ID generation, OCR safety, page mapping
3. **models.py** - Deprecate legacy fields, add constraints
4. **ingestion.py** - Ensure document type consistency
5. **retrieval.py** - Fix N+1 queries, improve error handling

### Medium Priority

6. **text_cleaning.py** - Add OCR-safe pipeline
7. **pdf_loader.py** - Improve error handling
8. **embedding.py** - Add type hints
9. **rag.py** - Improve error handling
10. **llm.py** - Add prompt injection protection

### Low Priority

11. Root test files - Move to `tests/` directory
12. Management commands - Consolidate similar commands
13. API views - Add rate limiting

---

## Recommended Target Architecture

### Clean Architecture Layers

```
Presentation Layer (API, Admin)
    ↓
Application Layer (Services, Use Cases)
    ↓
Domain Layer (Models, Domain Logic)
    ↓
Infrastructure Layer (Database, External Services)
```

### Canonical Chunking Pipeline

```
Raw PDF Text
    ↓
Unicode Normalization
    ↓
Whitespace Normalization
    ↓
Page Artifact Removal
    ↓
OCR Correction (Safe, Audited)
    ↓
Legal Structure Detection
    ↓
Hierarchy Parsing
    ↓
Structure-Aware Chunking
    ↓
Metadata Generation
    ↓
Validation & Deduplication
    ↓
Embedding
    ↓
Vector Indexing
```

### Canonical Hierarchy Model

```
LegalHierarchy
├── part
├── chapter
├── section
├── article
├── clause
├── subclause
├── paragraph
├── schedule
└── annex
```

### Metadata Schema

```python
CanonicalMetadata:
    chunk_id: str (unique, deterministic)
    document_id: int
    document_name: str
    document_type: str
    hierarchy: LegalHierarchy
    source_page_start: int
    source_page_end: int
    source_text: str (immutable)
    corrected_text: str (separate)
    ocr_status: str
    ocr_corrections: List[Correction]
    content_hash: str
    citation_label: str
```

---

## Refactoring Priority

### Phase 1: Critical Safety (Immediate)

1. Fix chunk ID collision
2. Implement safe OCR correction
3. Add page mapping implementation
4. Fix mutable dataclass defaults
5. Add document type consistency

### Phase 2: Code Quality (High)

6. Remove duplicate chunking implementation
7. Deprecate legacy database fields
8. Make chunker stateless
9. Improve exception handling
10. Add type hints

### Phase 3: Performance (Medium)

11. Add database indexes
12. Fix N+1 queries
13. Optimize FAISS rebuild
14. Add caching where appropriate

### Phase 4: Testing (High)

15. Add unit tests for all parsing logic
16. Add integration tests for pipeline
17. Add regression tests for bugs

### Phase 5: Cleanup (Low)

18. Remove unused files
19. Clean up requirements
20. Consolidate management commands
21. Improve documentation

---

## Migration Safety

### Database Changes Required

1. Add unique constraint on `(doc, chunk_id)`
2. Deprecate legacy hierarchy fields
3. Add new indexes for metadata filtering
4. Data migration for existing chunks

### Backward Compatibility

- Keep legacy fields temporarily with deprecation warnings
- Provide migration path for existing data
- Test migrations on copy of production database

---

## Testing Strategy

### Unit Tests Required

- Nepali digit normalization
- OCR correction accuracy
- Header detection (English/Nepali)
- Article/Section/Rule parsing
- Schedule/Annex parsing
- Clause parsing
- Hierarchy tracking
- Chunk ID uniqueness
- Content hashing
- Citation generation
- Page mapping

### Integration Tests Required

- Full PDF processing pipeline
- Embedding generation
- FAISS indexing
- Retrieval accuracy
- RAG end-to-end

### Regression Tests Required

- Every bug fix gets a test
- Every OCR correction gets validation test

---

## Remaining Risks

### High Risk

- OCR corrections may still contain inaccuracies
- Chunk ID uniqueness not guaranteed without sequence numbers
- Page mapping not implemented

### Medium Risk

- Database migration complexity
- Legacy field deprecation impact
- Performance of new indexing strategy

### Low Risk

- Unused file cleanup
- Documentation updates
- Minor code style improvements

---

## Conclusion

The system has a solid foundation but requires significant refactoring for production readiness. The most critical issues are:

1. **Chunk ID collision** - Can break uniqueness constraints
2. **Unsafe OCR corrections** - Can corrupt legal meaning
3. **Duplicate code** - Maintenance burden
4. **Missing tests** - Critical logic untested

The refactoring should proceed in phases, starting with critical safety issues, then code quality, then performance, then comprehensive testing.
