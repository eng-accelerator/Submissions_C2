# **CameraToCare – Demo App** 

This README explains:

*  what the app does  
*  how each step works  
*  how to run it

### **What is Camera-to-Care in the Context of Elderly Care?**

This new capability, powered by Generative AI, drastically speeds care by enabling the resident/patient or caregivers to take a picture from a mobile phone quickly, perform initial diagnoses/classification, and match the resident with the optimal caregiver or physician.  

N4M-Care brings LangGraph’s agent-orchestrated reasoning into the world of elder and facility-based care—where every decision, from wound photos to billing compliance, carries clinical, operational, and ethical weight. Our three graph modules demonstrate how AI can operate safely and autonomously inside healthcare workflows: Camera-to-Care converts a simple phone capture into a full clinical encounter through classification, triage, payer logic, and re-check loops.

### **🧭 High-Level Flow**

**User uploads image**  
   ↓  
**Agent 1: Injury Classification**  
   1\) Try Vision LLM (OpenRouter/OpenAI via LangChain)  
   2\) If model refuses/errs → silent fallback to 4 demo images (hash/aHash)  
   ↓  
**Agent 2: Insurance Verification**  
   1\) Try MCP PDF Reader → parse insurance PDF to JSON  
   2\) If PDF not available/parse fails → fallback to local policy DB logic  
   ↓  
**Agent 3: Caregiver Matching**  
   1\) Try MCP LLM Caregiver Search → get nearby caregivers (JSON)  
   2\) Rank by distance/skills; if search fails → fallback to in-app algorithm  
   ↓  
**Agent 4: Visit Scheduling**  
   1\) Try LLM for datetime/CPT suggestion  
   2\) If fails → rule-based scheduling  
   ↓  
**Complete workflow \+ UI display**

## **🔩 Key Components & Logic**

### **1\) Injury Classification (image → JSON)**

* Goal: classify 'injury\_type', 'severity', and 'clinical\_description'.  
* Primary: Vision model (e.g.,'gpt-4o' via OpenRouter/OpenAI using LangChain).  
* Silent fallback: If LLM refuses, errors, or sends bad JSON:  
* Compute SHA‑256 (exact bytes) and perceptual aHash (robust) of uploaded image.

**2\) Insurance Verification**

* Parses member\_id, provider, plan, copay, coverage\_percentage, deductible, preauthorization\_required.  
* Client helper:'mcp\_insurance\_client.py' spawns the MCP server and returns structured JSON.  
* Where the PDF path lives:'RESIDENT\_PROFILES\[patient\_id\]\["insurance\_pdf\_path"\]'.  
* Fallback: If MCP fails or PDF missing → use existing policy database/rules to compute coverage and copay.

**3\) Caregiver Matching**

* First attempt (MCP LLM search): 'mcp\_caregiver\_search\_server.py'   
  exposes 'search\_caregivers\_llm(location, injury\_type, severity)'.  
    
* Calls an LLM via OpenRouter to return JSON caregivers'{name, city, state, skills\[\], phone, url}'.  
    
*  We optionally geocode patient & caregiver city/state and compute distance to rank candidates.  
    
* Fallback: If the LLM tool fails/empty → use in-app caregiver scoring (skills, proximity, calendar score, etc.)  
    
* Where to integrate MCP: At the top of 'match\_caregiver\_node' or ('CaregiverMatcherAgent.match\_caregiver') we enrich options from MCP; we never break existing logic.

**4\) Visit Scheduling**

* First attempt: Ask LLM for'{visit\_datetime, procedure\_code}'.  
    
* Fallback: Rule-based slot selection (first available) \+ CPT mapping by injury/severity.

**5\) Location Service (Geocoding & Distance)**

* 'locationservice.py' now supports:  
* Nominatim/OSM fallback via'geopy' with certifi SSL, custom UA, and rate limiting.

Helpers:

* 'geocode\_city\_state(city, state) \-\> (lat, lon) | None'  
* 'geocode\_address(address) \-\> (lat, lon) | None'  
* 'distance\_miles(lat1, lon1, lat2, lon2) \-\> miles'  
* Designed to be resilient: failures never crash the caregiver node.

**6\) Retries** 

* Encapsulates retry/backoff (e.g., LLM calls, PDF parsing, search tools).

## **⚙️ Setup (one time)**

Python packages to be installed:   
pip install streamlit langchain openai  \# core  
pip install pdfplumber anyio mcp        \# MCP \+ PDF  
pip install geopy certifi googlemaps    \# geocoding \+ SSL bundle

project/ \#Layout  
├─ Camera2Care.py                  \# main app (Streamlit/UI \+ agents)  
├─ locationservice.py               \# geocoding \+ distance helpers  
├─ mcp\_caregiver\_search\_server.py   \# MCP LLM tool: search caregivers  
├─ mcp\_caregiver\_search\_client.py   \# client helper for caregiver search

▶️ **Run instructions**  
**\> streamlit run Camera2Care.py**

* Upload an injury image.  
* (Optional) Upload an insurance PDF via the UI or set the path in'RESIDENT\_PROFILES\[pid\]\["insurance\_pdf\_path"\]'.  
* Ensure the patient location is available (address or city/state) for caregiver search/ranking.

  \*\* Make sure 'OPENROUTER\_API\_KEY' is set.  
  \*\* Ensure patient location is available (address or city/state).

### **🧼 Data & Safety**

* No PHI is logged by default; remove/guard any 'print()' that could leak content.  
* MCP tools run in a separate process; failures don’t crash the app.  
* All fallbacks are silent—the UI doesn’t reveal when a hardcoded dataset or fallback path was used.

