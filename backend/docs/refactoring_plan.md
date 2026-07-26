# Refactoring Plan — Legal Information Assistance System

**Created**: July 24, 2026
**Based on**: Architecture Audit Report
**Goal**: Production-grade, clean architecture implementation

---

## Overview

This refactoring plan addresses the critical issues identified in the architecture audit, prioritizing safety, correctness, and maintainability. The refactoring will be executed in phases to minimize risk and ensure system stability.

---

## Phase 1: Critical Safety Fixes (Immediate)

### 1.1 Fix Chunk ID Collision

**File**: `legal_ai/services/chunking_v2.py`

**Current Issue**:
```python
def generate_chunk_id(document_name, part, chapter, article, clause, schedule, annex):
    # Returns same ID for multiple chunks under same article
    return f"{doc_slug}-part-{part}-chapter-{chapter}-article-{article}"
```

**Solution**:
```python
def generate_chunk_id(
    document_name: str,
    part: Optional[str],
    chapter: Optional[str],
    article: Optional[str],
    clause: Optional[str],
    schedule: Optional[str],
    annex: Optional[str],
    chunk_sequence: int,
    content_hash: Optional[str] = None,
) -> str:
    """Generate deterministic unique chunk ID."""
    doc_slug = document_name.lower().replace(" ", "-").replace("।", "").replace(",", "")
    
    parts = [doc_slug]
    
    if part:
        parts.append(f"part-{part}")
    if chapter:
        parts.append(f"chapter-{chapter}")
    if schedule:
        parts.append(f"schedule-{schedule}")
    elif annex:
        parts.append(f"annex-{annex}")
    elif article:
        parts.append(f"article-{article}")
        if clause:
            parts.append(f"clause-{clause}")
    
    # Add sequence number for uniqueness within same hierarchy
    parts.append(f"seq-{chunk_sequence}")
    
    # Optional: Add content hash for additional uniqueness
    if content_hash:
        parts.append(f"hash-{content_hash[:8]}")
    
    return "-".join(parts)
```

**Changes Required**:
- Update `generate_chunk_id()` signature
- Update `_create_chunk_metadata()` to pass chunk sequence
- Update `chunk()` method to track sequence numbers
- Add tests for uniqueness

**Impact**: Medium - Requires database migration for existing chunks

---

### 1.2 Implement Safe OCR Correction

**File**: `legal_ai/services/chunking_v2.py`

**Current Issue**:
```python
OCR_CORRECTIONS = {
    "रािः": "राज्यः",  # Global replacement, no tracking
    # ... 100+ corrections
}
```

**Solution**:
```python
@dataclass
class OCRCorrection:
    original: str
    corrected: str
    confidence: float
    rule_id: str

class SafeOCRCorrector:
    def __init__(self):
        self.corrections = self._load_safe_corrections()
    
    def _load_safe_corrections(self) -> Dict[str, OCRCorrection]:
        # Load only high-confidence corrections
        return {
            "राि": OCRCorrection("राि", "राज्य", 0.95, "NEP-001"),
            # Only include validated corrections
        }
    
    def correct(self, text: str) -> Tuple[str, List[OCRCorrection]]:
        """Apply corrections with tracking."""
        corrected = text
        applied_corrections = []
        
        for original, correction in self.corrections.items():
            if original in corrected:
                corrected = corrected.replace(original, correction.corrected)
                applied_corrections.append(correction)
        
        return corrected, applied_corrections
```

**Changes Required**:
- Create `OCRCorrection` dataclass
- Create `SafeOCRCorrector` class
- Update `ChunkMetadata` to include `ocr_corrections` field
- Update `_create_chunk_metadata()` to use safe corrector
- Keep `source_text` immutable
- Store `corrected_text` separately

**Impact**: High - Requires database schema update

---

### 1.3 Implement Page Mapping

**File**: `legal_ai/services/chunking_v2.py`

**Current Issue**:
```python
if page_mapping:
    pass  # TODO: implement
```

**Solution**:
```python
def _map_char_to_page(
    char_position: int,
    page_mapping: Dict[int, Tuple[int, int]]
) -> Optional[int]:
    """Map character position to page number."""
    for page_num, (start, end) in page_mapping.items():
        if start <= char_position <= end:
            return page_num
    return None

def _determine_page_range(
    text: str,
    start_pos: int,
    end_pos: int,
    page_mapping: Dict[int, Tuple[int, int]]
) -> Tuple[Optional[int], Optional[int]]:
    """Determine page range for a text segment."""
    page_start = _map_char_to_page(start_pos, page_mapping)
    page_end = _map_char_to_page(end_pos, page_mapping)
    return page_start, page_end
```

**Changes Required**:
- Implement character-to-page mapping
- Update PDF extraction to provide page boundaries
- Update chunking to track character positions
- Update metadata with page ranges

**Impact**: Medium - Requires PDF extraction changes

---

### 1.4 Fix Mutable Dataclass Defaults

**File**: `legal_ai/services/chunking_v2.py`

**Current Issue**:
```python
@dataclass
class ChunkMetadata:
    hierarchy_path: List[str] = None  # Unsafe default
```

**Solution**:
```python
from dataclasses import dataclass, field

@dataclass
class ChunkMetadata:
    hierarchy_path: List[str] = field(default_factory=list)
    ocr_corrections: List[OCRCorrection] = field(default_factory=list)
```

**Changes Required**:
- Update all dataclass fields with mutable defaults
- Add type hints for all fields

**Impact**: Low - Simple fix

---

### 1.5 Fix Document Type Consistency

**Files**: `legal_ai/services/chunking_v2.py`, `legal_ai/services/ingestion.py`

**Current Issue**:
```python
def __init__(self, document_type: str = "Act"):  # Hardcoded default
```

**Solution**:
```python
def __init__(self, document_id: int, document_name: str, document_type: str):
    self.document_type = document_type  # Use actual database value
```

**Changes Required**:
- Remove hardcoded default
- Ensure ingestion passes correct document type
- Add validation for document types

**Impact**: Low - Simple fix

---

## Phase 2: Code Quality Improvements

### 2.1 Remove Duplicate Chunking Implementation

**Files**: 
- `legal_ai/services/chunking.py` (DELETE)
- `legal_ai/services/__init__.py` (UPDATE)

**Action**:
1. Search for all imports of `LegalChunker` or `SmartLegalChunker`
2. Replace with `AdvancedLegalChunker`
3. Update test files
4. Delete `chunking.py`
5. Remove backward-compatibility alias

**Impact**: Medium - Requires test updates

---

### 2.2 Deprecate Legacy Database Fields

**File**: `legal_ai/models.py`

**Current Issue**: Duplicate hierarchy fields

**Solution**:
```python
class LegalChunk(models.Model):
    # Legacy fields (deprecated)
    part = models.CharField(max_length=255, blank=True, help_text="Deprecated: Use part_number")
    chapter = models.CharField(max_length=255, blank=True, help_text="Deprecated: Use chapter_number")
    section = models.CharField(max_length=255, blank=True, help_text="Deprecated: Use section_number")
    article = models.CharField(max_length=255, blank=True, help_text="Deprecated: Use article_number")
    dhara = models.CharField(max_length=255, blank=True, help_text="Deprecated: Use section_number")
    
    # Canonical fields
    part_number = models.CharField(max_length=50, blank=True, null=True)
    part_title = models.CharField(max_length=500, blank=True, null=True)
    # ... etc
```

**Action**:
1. Add `help_text` deprecation warnings
2. Create migration to copy data to canonical fields
3. Update code to use canonical fields
4. Plan legacy field removal in future version

**Impact**: High - Requires data migration

---

### 2.3 Make Chunker Stateless

**File**: `legal_ai/services/chunking_v2.py`

**Current Issue**: Mutable context in instance

**Solution**:
```python
class AdvancedLegalChunker:
    def __init__(self, document_id: int, document_name: str, document_type: str):
        self.document_id = document_id
        self.document_name = document_name
        self.document_type = document_type
        self.jurisdiction = "Nepal"
        # Remove mutable context from instance
    
    def chunk(self, text: str, page_mapping: Optional[Dict] = None) -> List[ChunkMetadata]:
        # Create fresh context for each document
        context = self._initialize_context()
        # Process with local context
```

**Action**:
1. Move context to local variable in `chunk()` method
2. Ensure no state persists between calls
3. Add tests for repeated calls

**Impact**: Medium - Requires careful state management

---

### 2.4 Improve Exception Handling

**Files**: Multiple service files

**Current Issue**: Broad exception handling

**Solution**:
```python
# Create custom exceptions
class DocumentProcessingError(Exception):
    pass

class TextExtractionError(DocumentProcessingError):
    pass

class ChunkingError(DocumentProcessingError):
    pass

# Use specific exceptions
try:
    result = process_document(doc_id)
except FileNotFoundError as e:
    logger.error(f"PDF not found: {e}")
    raise TextExtractionError(f"PDF file not found: {e}")
except ValueError as e:
    logger.error(f"Invalid document: {e}")
    raise DocumentProcessingError(f"Invalid document: {e}")
except Exception as e:
    logger.error(f"Unexpected error processing document {doc_id}: {e}")
    raise DocumentProcessingError(f"Processing failed: {e}")
```

**Action**:
1. Create domain-specific exceptions
2. Replace broad exception handling
3. Add proper logging
4. Add error tracking

**Impact**: Medium - Requires systematic updates

---

### 2.5 Add Type Hints

**Files**: All service files

**Action**:
1. Add type hints to all public functions
2. Add type hints to class methods
3. Use `Optional`, `List`, `Dict`, `Tuple` from `typing`
4. Configure mypy for static checking

**Impact**: Low - Gradual improvement

---

## Phase 3: Performance Improvements

### 3.1 Add Database Indexes

**File**: `legal_ai/models.py`

**Action**:
```python
class Meta:
    ordering = ["doc_id", "chunk_index"]
    indexes = [
        models.Index(fields=["doc", "chunk_index"]),
        models.Index(fields=["doc", "article_number"]),
        models.Index(fields=["doc", "section_number"]),
        models.Index(fields=["chunk_id"]),
        models.Index(fields=["content_hash"]),
        models.Index(fields=["document_type"]),
        models.Index(fields=["language"]),
        models.Index(fields=["chunk_type"]),
        # Composite indexes for common queries
        models.Index(fields=["doc", "article_number", "chunk_index"]),
    ]
    constraints = [
        models.UniqueConstraint(
            fields=["doc", "chunk_id"],
            name="unique_document_chunk_id",
        )
    ]
```

**Impact**: Medium - Requires migration

---

### 3.2 Fix N+1 Queries

**File**: `legal_ai/services/retrieval.py`

**Current Issue**:
```python
chunks = list(LegalChunk.objects.order_by("id"))  # No select_related
```

**Solution**:
```python
chunks = list(LegalChunk.objects.select_related("doc").order_by("id"))
```

**Action**:
1. Add `select_related` for foreign keys
2. Add `prefetch_related` for reverse relations
3. Profile query performance

**Impact**: Low - Simple fix

---

### 3.3 Optimize FAISS Rebuild

**File**: `legal_ai/services/ingestion.py`

**Current Issue**: Rebuild per document

**Solution**: Already implemented - batch rebuild at end

**Action**: Verify implementation is working correctly

**Impact**: None - Already fixed

---

## Phase 4: Testing Implementation

### 4.1 Unit Tests Structure

**Create**: `legal_ai/tests/`

```
legal_ai/tests/
├── __init__.py
├── test_chunking.py
├── test_ocr_correction.py
├── test_header_detection.py
├── test_hierarchy_parsing.py
├── test_metadata_generation.py
├── test_citation_generation.py
├── test_page_mapping.py
├── test_text_cleaning.py
└── test_pdf_extraction.py
```

---

### 4.2 Critical Test Cases

**test_chunking.py**:
```python
def test_chunk_id_uniqueness():
    """Ensure chunk IDs are unique within same article."""
    chunker = AdvancedLegalChunker(1, "Test Doc", "act")
    text = "Article 1\n(1) First clause\n(2) Second clause"
    chunks = chunker.chunk(text)
    chunk_ids = [c.chunk_id for c in chunks]
    assert len(chunk_ids) == len(set(chunk_ids))

def test_hierarchy_tracking():
    """Test hierarchy context is maintained correctly."""
    chunker = AdvancedLegalChunker(1, "Test Doc", "act")
    text = "Part 1\nChapter 1\nArticle 1\n(1) Clause"
    chunks = chunker.chunk(text)
    assert chunks[-1].part_number == "1"
    assert chunks[-1].chapter_number == "1"
    assert chunks[-1].article_number == "1"
```

**test_ocr_correction.py**:
```python
def test_ocr_correction_safety():
    """Ensure source text is not modified."""
    corrector = SafeOCRCorrector()
    source = "राि राज्य"
    corrected, corrections = corrector.correct(source)
    assert source == "राि राज्य"  # Source unchanged
    assert corrected != source  # Corrected version different
    assert len(corrections) > 0  # Corrections tracked
```

---

### 4.3 Integration Tests

**Create**: `legal_ai/tests/test_pipeline.py`

```python
def test_full_pdf_pipeline():
    """Test complete PDF processing pipeline."""
    # Upload PDF
    # Extract text
    # Clean text
    # Chunk
    # Generate embeddings
    # Index in FAISS
    # Retrieve
    # Verify results
```

---

## Phase 5: Cleanup and Documentation

### 5.1 Remove Unused Files

**Files to Delete**:
- `test_citizenship.py` (move to tests/)
- `test_arrest.py` (move to tests/)
- `test_retrieval.py` (move to tests/)
- `test_retrieval_simple.py` (move to tests/)
- `test_suite.py` (move to tests/)
- `test_runner.py` (move to tests/)
- `verify_fixes.py` (move to tests/ or delete)

**Action**:
1. Move test files to proper location
2. Delete truly unused files
3. Update imports

---

### 5.2 Consolidate Management Commands

**Current Commands**:
- `check_civil_code_chunks.py`
- `check_cleaned_text.py`
- `check_code_extraction.py`
- `check_embeddings.py`
- `check_english_codes.py`
- `check_fundamental_rights.py`
- `chunk_quality_report.py`
- `clean_corpus.py`
- `test_citizenship_retrieval.py`
- `test_code_retrieval.py`
- `test_font_detection.py`
- `test_mixed_extraction.py`

**Action**:
1. Consolidate similar check commands into `check_document.py`
2. Consolidate test commands into `test_retrieval.py`
3. Keep only essential commands

---

### 5.3 Update Documentation

**Create**: `docs/architecture.md`

```markdown
# System Architecture

## Components
- PDF Extraction
- Text Cleaning
- Chunking
- Embedding
- Retrieval
- RAG

## Data Flow
[Detailed flow diagram]

## Deployment
[Deployment instructions]
```

**Create**: `docs/chunking.md`

```markdown
# Chunking System

## Hierarchy Model
[Canonical hierarchy]

## ID Generation
[Chunk ID algorithm]

## OCR Safety
[OCR correction strategy]
```

---

## Execution Timeline

### Week 1: Critical Safety
- Day 1-2: Fix chunk ID collision
- Day 3-4: Implement safe OCR correction
- Day 5: Fix page mapping and dataclass defaults

### Week 2: Code Quality
- Day 1-2: Remove duplicate chunking
- Day 3-4: Deprecate legacy fields
- Day 5: Make chunker stateless

### Week 3: Performance & Testing
- Day 1-2: Add database indexes
- Day 3-4: Implement unit tests
- Day 5: Implement integration tests

### Week 4: Cleanup & Documentation
- Day 1-2: Remove unused files
- Day 3-4: Consolidate commands
- Day 5: Update documentation

---

## Risk Mitigation

### Database Migration Risks
- Test migrations on staging database first
- Create backup before running migrations
- Have rollback plan ready

### Breaking Changes
- Maintain backward compatibility where possible
- Use deprecation warnings
- Provide migration guide

### Performance Regressions
- Profile before and after changes
- Monitor query performance
- Have rollback plan for performance issues

---

## Success Criteria

### Phase 1 Complete When:
- ✅ Chunk IDs are unique
- ✅ OCR corrections are safe and tracked
- ✅ Page mapping is functional
- ✅ Dataclass defaults are safe
- ✅ Document types are consistent

### Phase 2 Complete When:
- ✅ Only one chunking implementation exists
- ✅ Legacy fields are deprecated
- ✅ Chunker is stateless
- ✅ Exception handling is specific
- ✅ Type hints are added

### Phase 3 Complete When:
- ✅ Database indexes are added
- ✅ N+1 queries are fixed
- ✅ FAISS rebuild is optimized

### Phase 4 Complete When:
- ✅ Unit tests cover critical logic
- ✅ Integration tests cover pipeline
- ✅ Regression tests exist for bugs

### Phase 5 Complete When:
- ✅ Unused files are removed
- ✅ Commands are consolidated
- ✅ Documentation is updated

---

## Rollback Plan

If any phase causes critical issues:

1. Stop deployment
2. Revert database migrations
3. Restore code to previous commit
4. Investigate issue
5. Fix and retry

---

## Next Steps

1. Review and approve this plan
2. Set up staging environment
3. Begin Phase 1 implementation
4. Monitor and adjust as needed
