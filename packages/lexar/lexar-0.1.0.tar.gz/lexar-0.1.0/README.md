# lexar

[![PyPI version](https://img.shields.io/pypi/v/lexar?color=blue)](https://pypi.org/project/lexar/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ⚖️ Lexar: A Specialised NER Pipeline for Legal Texts

Lexar is an essential tool for legal tech and data science, providing a **spaCy-based Named Entity Recognition (NER)** pipeline specifically engineered to extract and classify structured legal information. Traditional NLP models often fail to recognise the nuanced and formal language of legal documents, but Lexar's rule-based engine provides reliable extraction across multiple legal domains.

### Why Lexar?

* High Precision: Leverages sophisticated linguistic and regular expression patterns (rules) to achieve high precision on structured legal entities, avoiding the ambiguity of statistical models in this domain.
* Deep Legal Taxonomy: Recognises and labels over 12 specialised entity types critical to legal analysis.
* Seamless Integration: Designed as a standard spaCy component, making it easy to integrate into existing NLP or legal technology workflows.

---

## 🚀 Installation

Lexar is compatible with Python 3.8+ and uses standard spaCy dependencies.

```bash
# 1. Install the Lexar package from PyPI
pip install lexar

# 2. Install the required base spaCy language model
# Lexar uses this model for tokenisation and standard entities (like PERSON, ORG).
python -m spacy download en_core_web_sm

📖 Usage Example
To begin processing, load the custom NLP pipeline using the primary lexar.load() function and apply it to any legal text.

import lexar

# Load the custom legal NLP pipeline
nlp = lexar.load()

# Example text demonstrating multiple entity types defined in the pipeline
text = "The litigant filed Case No. 2025-CV-340 in the Supreme Court of the State of Texas, citing the GDPR. This matter was settled on the 15th day of October, 2025, and involved a Mortgage Deed."

doc = nlp(text)

print("\n--- Detected Legal Entities ---")
print("-" * 55)

# Iterate through all recognised entities in the document
for ent in doc.ents:
    # Lexar extracts both custom legal entities and standard spaCy entities
    print(f"| Label: {ent.label_.ljust(20)} | Text: {ent.text}")

# Expected Output (Illustrative):
# | Label: CASE_ID             | Text: 2025-CV-340
# | Label: COURT_NAME          | Text: Supreme Court
# | Label: JURISDICTION        | Text: State of Texas
# | Label: ACT_STATUTE         | Text: GDPR
# | Label: LEGAL_DATE          | Text: 15th day of October, 2025
# | Label: DEED_TYPE           | Text: Mortgage Deed
