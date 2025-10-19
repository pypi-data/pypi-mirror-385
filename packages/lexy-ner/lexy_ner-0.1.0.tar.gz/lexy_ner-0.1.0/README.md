# lexy-ner

[![PyPI version](https://img.shields.io/pypi/v/lexy-ner?color=blue)](https://pypi.org/project/lexy-ner/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ⚖️ A Specialised NER Pipeline for Legal Texts

Lexy-ner is a **spaCy-based Named Entity Recognition (NER)** pipeline designed specifically to extract and classify structured information from complex legal documents. While general NLP tools (like standard spaCy models) excel at common entities (Person, Org, Date), they often fail on domain-specific identifiers.

This package solves that problem by implementing a sophisticated, rule-based matching engine that recognises entities critical to legal research, compliance, and litigation analysis across multiple domains.

### Why Lexy-ner?

* Deep Legal Taxonomy: Extracts over 12 specialised entity types, including Case IDs, Court Names, Insolvency Terms, Contract Types, and specific Statute References.
* Ease of Use: Integrates seamlessly into any existing spaCy workflow. Install and run with two simple lines of code.
* Open-Source & Extensible: Built on the robust spaCy framework, allowing for easy expansion with custom rules or fine-tuning with deep learning models.

---

## 🚀 Installation

Ensure you are using Python 3.8 or higher.

```bash
# 1. Install the package
pip install lexy-ner

# 2. Install the default language model (required by lexy-ner's pipeline)
python -m spacy download en_core_web_sm