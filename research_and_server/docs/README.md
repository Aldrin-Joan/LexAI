# 📖 Documentation & Research Audits

This folder contains the auxiliary documentation, walkthroughs, and critical research audits performed during the development of the Hybrid Legal RAG system.

---

## 🧐 Critical Research Audits

### 1. `hardcore_critique_v2.md`
A no-holds-barred expert critique of the initial system architecture. This document identifies key methodological gaps (e.g., jurisdictional bias, Supreme Court noise floors) that were addressed in the final version.

### 2. `result_report.md`
A high-level summary of the findings, including the "Supreme Court bias" discovery and how the system corrects for it via PageRank weighting.

---

## 🚶 Technical Walkthroughs

### 3. `walkthrough.md`
The master system walkthrough, covering:
- How to initialize the SQLite database
- How to generate FAISS indices
- How to execute multi-case RAG summaries
- How to generate unstructured Case Briefs

---

## 🛠️ Usage
These documents are best read in conjunction with the [Research Paper Modules](../research_paper) to understand the "Why" behind specific architecture decisions (e.g., why RRF-Fusion was used over direct interpolation).
