# Technical Design Document - Pending Items

This document lists critical design details that are currently missing from the `technical-design-mvp.md` and need to be addressed to ensure a robust, maintainable, and secure system. These items will be integrated into the main TDD once defined.

## Missing Design Details:

*   **Dependency Versioning:** Status: [x]
*   **Logging Standards and Principles:** Status: [x]
*   **Detailed Error Handling & Recovery Strategy:** Status: [x]
*   **Input Validation and Security Hardening:** Status: [x]
*   **Concrete Data Ingestion and Chunking Strategy:** Status: [x]
*   **UI State Management and Streaming:** Status: [x]
*   **Agent-Specific Design & Prompt Engineering:** Status: [x]
*   **Detailed Testing Strategy:** Status: [x]

*   **Implement and Execute RAG Evaluation for Chunking Strategy:** Status: [ ]
    *   Create a "golden dataset" of 3-5 documents and 5-10 questions with manually mapped "ideal" chunks.
    *   Implement an evaluation script to test various chunking strategies (e.g., different chunk sizes, overlaps).
    *   Measure and compare Hit Rate and MRR for each strategy.
    *   Update the TDD (Section 5.2) with the optimal parameters found.

