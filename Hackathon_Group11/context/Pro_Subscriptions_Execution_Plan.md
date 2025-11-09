# Pro Subscriptions Integration - Execution Plan

**Created:** Based on "Leverage Your Pro Subscriptions in the Hackathon P.md"  
**Status:** In Progress  
**Total Estimated Time:** ~2 hours

---

## Integration Priority Matrix

| Tool | Impact | Effort | Priority | Time | Status |
|------|--------|--------|----------|------|--------|
| **Perplexity** | High | Low | 🔴 **CRITICAL** | 10 min | ✅ Completed |
| **Wispr Flow** | High | Medium | 🔴 **CRITICAL** | 20 min | ✅ Completed |
| **Chronicle** | High | Low | 🟡 **HIGH** | 30 min | ⚪ Pending |
| **Numerous.ai** | Medium | Medium | 🟡 **HIGH** | 30 min | ✅ Completed |
| **Emily AI** | Medium | Low | 🟡 **HIGH** | 20 min | ⚪ Pending |
| **Fireflies** | Medium | Low | 🟠 **MEDIUM** | 15 min | ⚪ Pending |

---

## Integration 1: Perplexity Search (10 min) — CRITICAL

### Objective
Add Perplexity as a fallback search engine when Tavily fails or is unavailable.

### Files to Modify
- `agents/retriever.py`

### Steps

#### Step 1.1: Install Perplexity SDK
- [x] Check Perplexity Python SDK package name
- [x] Add to `requirements.txt` (using requests library for API calls)
- [x] Install package: `pip install requests` (already in requirements)

#### Step 1.2: Add Perplexity to Retriever Agent
**Location:** `agents/retriever.py`

**Changes:**
1. [x] Import requests library (after line 11)
2. [x] Initialize Perplexity in `__init__` method (after line 32, after Tavily initialization)
3. [x] Add fallback logic in `retrieve()` method (around line 66-80)
   - Try Tavily first
   - If Tavily fails, fallback to Perplexity
   - If both fail, return empty results
4. [x] Add fallback for news search as well

#### Step 1.3: Add Perplexity Parser Method
**Location:** After `_parse_arxiv_results()` method (after line 182)

**Create:** `_parse_perplexity_results()` method
- [x] Parse Perplexity API response structure
- [x] Convert to same format as Tavily results
- [x] Handle edge cases (empty results, malformed data)
- [x] Added `_search_perplexity()` method for API calls

#### Checkpoint
- [x] Implementation complete
- [ ] Test by temporarily disabling Tavily API key (manual testing required)
- [ ] Verify Perplexity fallback works (manual testing required)
- [x] Verify results format matches expected structure
- [x] Test error handling when both APIs fail

---

## Integration 2: Wispr Flow Voice Input (20 min) — CRITICAL

### Objective
Add voice input capability to research form using Web Speech API (with future Wispr Flow integration support).

### Files to Create/Modify
- **NEW:** `frontend/src/components/VoiceInput.tsx`
- **NEW:** `frontend/src/components/VoiceInput.css`
- **MODIFY:** `frontend/src/components/ResearchForm.tsx`
- **MODIFY:** `backend/main.py` (optional endpoint)

### Steps

#### Step 2.1: Create VoiceInput Component
**File:** `frontend/src/components/VoiceInput.tsx`

**Features:**
- [x] Use Web Speech API as primary (browser-native)
- [x] Support for future Wispr Flow integration
- [x] Similar structure to `TextToSpeechControls.tsx`
- [x] Handle browser compatibility
- [x] Show listening state
- [x] Display transcript in real-time
- [x] Error handling for unsupported browsers
- [x] TypeScript type definitions for Web Speech API

**Props:**
```typescript
interface Props {
  onVoiceCapture: (text: string) => void
  disabled?: boolean
}
```

#### Step 2.2: Create VoiceInput Styles
**File:** `frontend/src/components/VoiceInput.css`

**Styles:**
- [x] Voice button with listening animation
- [x] Transcript display
- [x] Error message styling
- [x] Accessibility considerations
- [x] Responsive design

#### Step 2.3: Integrate into ResearchForm
**File:** `frontend/src/components/ResearchForm.tsx`

**Changes:**
1. [x] Import `VoiceInput` component
2. [x] Add voice input section above text input
3. [x] Auto-populate query field when voice captured
4. [x] Add visual separator ("or" divider) between input methods
5. [x] Add divider styles to `App.css`

#### Step 2.4: Optional Backend Endpoint
**File:** `backend/main.py`

**Add:** `/api/research-voice` endpoint
- [x] Accept audio data (for future Wispr Flow integration)
- [x] Placeholder implementation
- [x] Return success response
- [x] Added to root endpoint documentation

#### Checkpoint
- [x] Implementation complete
- [ ] Voice input works in supported browsers (manual testing required)
- [x] Transcript appears in query field (code implemented)
- [x] Error handling for unsupported browsers
- [x] UI is polished and accessible

---

## Integration 3: Chronicle Presentation (30 min) — HIGH

### Objective
Add Chronicle presentation embed for architecture walkthrough.

### Files to Create/Modify
- **NEW:** `frontend/src/components/PresentationEmbed.tsx`
- **MODIFY:** `frontend/src/App.tsx` (add tabs)

### Steps

#### Step 3.1: Create Presentation Component
**File:** `frontend/src/components/PresentationEmbed.tsx`

**Features:**
- Iframe embed for Chronicle presentation
- Placeholder when no URL provided
- Responsive sizing
- Loading states

#### Step 3.2: Add Tabs to Main App
**File:** `frontend/src/App.tsx`

**Changes:**
- Add tab navigation
- Tab 1: Live Demo (current app)
- Tab 2: Architecture (Chronicle embed)
- Tab 3: Metrics (future: Numerous.ai data)

#### Step 3.3: Manual Step
- Create presentation in Chronicle
- Export embed URL
- Add to environment variables or config

#### Checkpoint
- [ ] Presentation loads correctly
- [ ] Tabs work smoothly
- [ ] Responsive on mobile

---

## Integration 4: Numerous.ai Data Enrichment (30 min) — HIGH

### Objective
Enrich search results with metadata, sentiment analysis, and topic extraction.

### Files to Create/Modify
- **NEW:** `agents/enrichment.py`
- **MODIFY:** `orchestration/coordinator.py`
- **NEW:** `frontend/src/components/ResearchMetrics.tsx`

### Steps

#### Step 4.1: Create Enrichment Agent
**File:** `agents/enrichment.py`

**Features:**
- [x] Custom enrichment agent (Numerous.ai doesn't have public API)
- [x] Enrich sources with:
  - [x] Domain authority scores (based on URL patterns)
  - [x] Sentiment analysis (heuristic-based)
  - [x] Topic categorization (keyword-based)
  - [x] Metadata extraction (dates, domains, word counts)

#### Step 4.2: Integrate into Workflow
**File:** `orchestration/coordinator.py`

**Changes:**
- [x] Add enrichment node after retriever
- [x] Update workflow edges: retriever → enricher → analyzer
- [x] Handle errors gracefully (continues with original sources if enrichment fails)
- [x] Updated backend streaming endpoint to include enrichment stage
- [x] Updated frontend progress tracking to include enrichment stage

#### Step 4.3: Create Metrics Component
**File:** `frontend/src/components/ResearchMetrics.tsx`

**Features:**
- [x] Display enriched metadata
- [x] Visualize sentiment scores (bar chart)
- [x] Show topic distribution (category breakdown)
- [x] Source quality breakdown (high/medium/low quality)
- [x] Summary cards with key metrics
- [x] Integrated into ResearchResults component

#### Checkpoint
- [x] Implementation complete
- [ ] Enrichment adds metadata to sources (manual testing required)
- [ ] Metrics display correctly (manual testing required)
- [x] Error handling works (graceful fallback implemented)

---

## Integration 5: Emily AI Documentation (20 min) — HIGH

### Objective
Use Emily AI to generate comprehensive documentation.

### Manual Steps
- [ ] Use Emily AI to generate README sections
- [ ] Add docstrings to agent files
- [ ] Create feature descriptions
- [ ] Update component JSDoc comments

### Files to Update
- `README.md`
- `agents/*.py`
- `frontend/src/components/*.tsx`

#### Checkpoint
- [ ] Documentation is comprehensive
- [ ] All agents have docstrings
- [ ] Components have JSDoc comments

---

## Integration 6: Fireflies Session Recording (15 min) — MEDIUM

### Objective
Add session recording indicator and auto-documentation.

### Files to Create
- **NEW:** `frontend/src/components/SessionRecording.tsx`

### Steps

#### Step 6.1: Create Session Recording Component
**File:** `frontend/src/components/SessionRecording.tsx`

**Features:**
- Visual recording indicator
- Auto-start on mount
- Log research sessions
- Future: Fireflies API integration

#### Step 6.2: Integrate into App
**File:** `frontend/src/App.tsx`

**Changes:**
- Add SessionRecording component
- Track all research sessions

#### Checkpoint
- [ ] Recording indicator appears
- [ ] Sessions are logged
- [ ] UI is unobtrusive

---

## Environment Variables

Add to `.env.example` and `.env`:

```bash
# Pro Subscription Tools
PERPLEXITY_API_KEY=your_perplexity_key_here
WISPR_FLOW_API_KEY=your_wispr_key_here
NUMEROUS_AI_API_KEY=your_numerous_key_here
FIREFLIES_API_KEY=your_fireflies_key_here
CHRONICLE_PRESENTATION_URL=your_chronicle_embed_url
```

---

## Testing Checklist

### Per Integration
- [ ] Feature works in development
- [ ] No console errors
- [ ] Graceful fallback if API unavailable
- [ ] UI/UX is polished
- [ ] Documentation updated

### Final Integration Test
- [ ] All features work together
- [ ] End-to-end test passes
- [ ] Production build succeeds
- [ ] Deployment works (Vercel + Railway)

---

## Progress Tracking

### Completed
- [x] Execution plan created
- [x] Integration 1: Perplexity Search ✅
- [x] Integration 2: Wispr Flow Voice Input ✅
- [ ] Integration 3: Chronicle Presentation
- [x] Integration 4: Numerous.ai Enrichment ✅
- [ ] Integration 5: Emily AI Documentation
- [ ] Integration 6: Fireflies Session Recording

### Current Status
- **Integration 1:** ✅ Completed
- **Integration 2:** ✅ Completed
- **Integration 4:** ✅ Completed
- **Next:** Integration 3 (Chronicle Presentation) or Integration 5 (Emily AI Documentation)

---

## Notes

- All integrations should have graceful fallbacks
- Maintain existing functionality
- Follow existing code patterns
- Ensure accessibility compliance
- Test on multiple browsers

---

**Last Updated:** [Current Date]  
**Next Steps:** Complete Integration 1 & 2, then proceed to Integration 3

