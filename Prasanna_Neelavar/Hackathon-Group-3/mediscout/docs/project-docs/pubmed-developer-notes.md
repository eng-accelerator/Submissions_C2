## PubMED API - Developer Notes

> Practical developer note on accessing PubMed via NCBI’s E‑utilities API, with ready-to-run examples in curl and Python.

### What is the PubMed API
- PubMed is accessed programmatically through NCBI’s Entrez Programming Utilities (E‑utilities), the public API for all Entrez databases including the PubMed database (db=pubmed). [1][2]
- The base URL for all endpoints is https://eutils.ncbi.nlm.nih.gov/entrez/eutils/, and you select a utility such as esearch.fcgi, esummary.fcgi, efetch.fcgi, elink.fcgi, epost.fcgi, etc. [2][3]

### Core workflow (search → summarize → fetch)
- Typical flow: use ESearch to get PMIDs for a query, ESummary to pull structured summaries/metadata, and EFetch to retrieve full PubMed records (XML or text abstract). [2][3]
- For large result sets or multi-step pipelines, enable the Entrez History server (usehistory=y) to obtain WebEnv and query_key, then reuse those values across ESummary/EFetch/ELink to batch and paginate efficiently. [2][3]

### Key utilities you’ll use
- ESearch: text search returning UIDs (PMIDs) with options for filters, dates, sorting, pagination, JSON output, and posting results to History. [3]
- ESummary: document summaries (DocSums) for PMIDs with XML or JSON output and pagination via retstart/retmax. [3]
- EFetch: full data records for PMIDs, commonly retmode=xml or retmode=text with rettype=abstract for PubMed. [3]
- EPost: upload a list of PMIDs to the History server to get WebEnv and query_key (useful for batching before ESummary/EFetch). [3]
- ELink: related items and external/full-text links; supports modes like neighbor, neighbor_history, prlinks, and linkname filters. [3]

### Authentication, identification, and rate limits
- Include api_key to increase the default request rate from about 3 requests/second to about 10 requests/second per key, and request higher limits from NCBI if needed. [2][4]
- Provide tool and email parameters in all requests to identify your application and a contact email, which helps with support and compliance. [3]
- If you exceed your limit you may see an error like {"error":"API rate limit exceeded"}, so implement backoff/retry and respect throughput guidelines. [2]

### Pagination and batching
- Use retstart and retmax to page through large result sets in ESearch, ESummary, and EFetch, with a per-call maximum of 10,000 records. [3]
- PubMed special case: ESearch returns at most the first 10,000 matching PMIDs via the API; for more, iterate carefully or consider EDirect-based batching workflows. [3]
- For large jobs, use usehistory=y so the entire set is stored server-side and then retrieve it in slices with retstart/retmax to avoid re-running the search. [2][3]

### Query syntax tips (PubMed)
- Boolean operators AND/OR/NOT must be uppercase, fields are tagged in square brackets (e.g., title, author, pdat), and spaces must be encoded in URLs. [2][3]
- PubMed supports proximity searching in Title or Title/Abstract fields, for example "asthma treatment"[Title:~3] to find terms within 3 words of each other. [3]

### Formats and identifiers
- For PubMed, UIDs are PMIDs; ESummary supports retmode=json and XML, while EFetch commonly uses retmode=xml or retmode=text with rettype=abstract for human-readable abstracts. [3]
- Use EInfo to discover supported fields, sorts, and links for a given db (retmode=json is available for EInfo too). [3]

### Compliance and data access options
- PubMed data are accessible via the E‑utilities API and via FTP snapshots (annual baseline plus daily updates) if you need to mirror locally. [5]
- Follow NLM/NCBI terms, include appropriate disclaimers in your software, and consult PubMed DTD/docs when parsing XML at scale. [2][5]

### Minimal curl examples
- Search PubMed for “arrhythmia” and return PMIDs as JSON (first 50) with History enabled:
  - Explanation: This uses ESearch with db=pubmed, retmode=json, retmax=50, and usehistory=y to store the full set on the History server. [3]
  - curl:
    - curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=arrhythmia&retmode=json&retmax=50&usehistory=y&tool=yourapp&email=you@example.com"
- Summarize using WebEnv/query_key from ESearch:
  - Explanation: Replace <WebEnv> and <key> with values returned by ESearch; retmode=json returns structured DocSums. [2][3]
  - curl:
    - curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&WebEnv=<WebEnv>&query_key=<key>&retmode=json&retstart=0&retmax=50&tool=yourapp&email=you@example.com"
- Fetch full records (XML) for specific PMIDs:
  - Explanation: EFetch with retmode=xml returns the PubMed XML for parsing; use retmode=text&rettype=abstract for plain abstracts. [3]
  - curl:
    - curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=17284678,9997&retmode=xml&tool=yourapp&email=you@example.com"

### Minimal Python examples (requests)
- ESearch with paging and History:
  - Explanation: This retrieves the first page, then iterates using retstart/retmax while respecting the 10,000 per-call cap and using History to avoid rerunning the search. [2][3]
  - Code:
    - import os, time, requests
      BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
      params = {
          "db": "pubmed",
          "term": "arrhythmia",
          "retmode": "json",
          "retmax": 100,
          "retstart": 0,
          "usehistory": "y",
          "tool": "yourapp",
          "email": "you@example.com",
          "api_key": os.getenv("NCBI_API_KEY", "")
      }
      r = requests.get(BASE + "esearch.fcgi", params=params, timeout=30)
      r.raise_for_status()
      es = r.json()
      count = int(es["esearchresult"]["count"])
      webenv = es["esearchresult"]["webenv"]
      qkey = es["esearchresult"]["querykey"]
      pmids = es["esearchresult"]["idlist"]
      # page through
      while params["retstart"] + params["retmax"] < min(count, 10000):
          params["retstart"] += params["retmax"]
          time.sleep(0.12)  # ~8 rps with api_key
          r = requests.get(BASE + "esearch.fcgi", params=params, timeout=30)
          r.raise_for_status()
          pmids += r.json()["esearchresult"]["idlist"]
      print(len(pmids), "PMIDs")
- ESummary using History:
  - Explanation: Use WebEnv/query_key instead of id lists, request JSON, and page with retstart/retmax. [2][3]
  - Code:
    - sparams = {
          "db": "pubmed",
          "WebEnv": webenv,
          "query_key": qkey,
          "retmode": "json",
          "retstart": 0,
          "retmax": 200,
          "tool": "yourapp",
          "email": "you@example.com",
      }
      r = requests.get(BASE + "esummary.fcgi", params=sparams, timeout=30)
      r.raise_for_status()
      summaries = r.json()["result"]
- EFetch abstracts:
  - Explanation: Fetch abstracts as plain text for a small batch of PMIDs for human-readable content or quick QA. [3]
  - Code:
    - fparams = {
          "db": "pubmed",
          "id": ",".join(pmids[:20]),
          "retmode": "text",
          "rettype": "abstract",
          "tool": "yourapp",
          "email": "you@example.com",
      }
      r = requests.get(BASE + "efetch.fcgi", params=fparams, timeout=30)
      r.raise_for_status()
      print(r.text[:1000])

### Filtering, sorting, and dates
- Apply database-specific filters and fields via term (e.g., review[Publication Type], 2023[pdat], title/abstract fields), or use explicit field= and sort= parameters where supported. [3]
- Date limits can be set using datetype with reldate in days or mindate/maxdate ranges (e.g., pdat with mindate=2024/01/01&maxdate=2024/12/31). [3]

### Linking and full-text
- Use ELink with cmd=neighbor to get “related articles” in PubMed, or cmd=prlinks to retrieve primary full-text provider links for PMIDs. [3]
- Limit link outputs via linkname (e.g., pubmed_pubmed for within-PubMed neighbors) or by applying term filters after the link operation when db=dbfrom=pubmed. [3]

### Large-scale and offline use
- For mirroring or analytics at scale, NLM provides annual PubMed baseline XML and daily update files over FTP in addition to the API route. [5]
- Follow the recommended load order: import the baseline, then apply daily updates in numerical order, replacing revised/deleted citations accordingly. [5]

### Best practices checklist
- Always include tool and email in requests, use api_key for higher throughput, and keep under ~3 rps without a key or ~10 rps with a key. [2][3]
- Use usehistory=y and batch with EPost/ESearch to minimize redundant requests and to handle large sets safely with retstart/retmax. [2][3]
- Prefer retmode=json for ESearch/ESummary when integrating into apps, and retmode=xml for canonical machine parsing of full PubMed records with EFetch. [3]
- Add polite retry/backoff on HTTP 429 and schedule bulk jobs during off-peak windows when possible per NCBI guidance. [2]

### Useful references for implementation
- A General Introduction to the E‑utilities (concepts, endpoints, History server, usage guidelines). [2]
- The E‑utilities In‑Depth (all parameters, examples, JSON support, PubMed-specific limits and proximity search). [3]
- PubMed “Download data” page (API vs FTP, baseline/dailies, DTDs, and update practices). [5]
- API key rate-limit background and defaults (3 rps vs 10 rps). [4]

Sources
[1] APIs - Develop - NCBI - NIH https://www.ncbi.nlm.nih.gov/home/develop/api/
[2] A General Introduction to the E-utilities - Entrez Programming ... - NCBI https://www.ncbi.nlm.nih.gov/books/NBK25497/
[3] The E-utilities In-Depth: Parameters, Syntax and More - NCBI https://www.ncbi.nlm.nih.gov/books/NBK25499/
[4] Release Plan for E-utility API Keys - NCBI Insights - NIH https://ncbiinsights.ncbi.nlm.nih.gov/2018/08/14/release-plan-for-e-utility-api-keys/
[5] Download PubMed Data - NIH https://pubmed.ncbi.nlm.nih.gov/download/
[6] Getting started with the PubMed API https://library.cumc.columbia.edu/kb/getting-started-pubmed-api
[7] Entrez Programming Utilities Help - NCBI Bookshelf - NIH https://www.ncbi.nlm.nih.gov/books/NBK25501/
[8] Web Technologies in R - 12 PubMed API Example - Gaston Sanchez https://www.gastonsanchez.com/R-web-technologies/4-03-api-pubmed.html
[9] E-utilities and the History server - National Library of Medicine https://www.nlm.nih.gov/dataguide/eutilities/history.html
[10] How do I get an enhanced API key (exceeding 10 rps) for NCBI APIs? https://support.nlm.nih.gov/kbArticle/?pn=KA-05318
[11] APIs for Libraries: Exercise: NCBI E-utilities https://joshuadull.github.io/APIs-for-Libraries/08-NCBI-E-Utilities/index.html
[12] easyPubMed: working with retstart and retmax - Data Pulse https://www.data-pulse.com/projects/Rlibs/vignettes/easyPubMed_03_retmax_example.html
[13] New API Keys for the E-utilities - NCBI Insights - NIH https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
[14] Software Tools - Download - NCBI - NIH https://www.ncbi.nlm.nih.gov/home/tools/
[15] Rentrez Tutorial https://cran.r-project.org/web/packages/rentrez/vignettes/rentrez_tutorial.html
[16] Testing Periods for New API Keys - NCBI Insights - NIH https://ncbiinsights.ncbi.nlm.nih.gov/2018/04/19/testing-periods-for-new-api-keys/
[17] For Developers - PMC - NIH https://pmc.ncbi.nlm.nih.gov/tools/developers/
[18] How to retrieve NCBI Entrez summary using gene name ... https://stackoverflow.com/questions/76727448/how-to-retrieve-ncbi-entrez-summary-using-gene-name-with-biopython
[19] NCBI rate-limiting e-utilities queries, causing HTTP 429 #33 - GitHub https://github.com/jimhester/primerTree/issues/33
[20] PubMed https://pubmed.ncbi.nlm.nih.gov
