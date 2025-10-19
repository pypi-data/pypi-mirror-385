import spacy
from spacy.language import Language
from spacy.matcher import Matcher
from spacy.tokens import Doc

# --- Configuration ---
# This model name corresponds to the dependency specified in pyproject.toml
DEFAULT_MODEL = "en_core_web_sm"

# --- 1. Custom Component Factory ---

@Language.factory("legal_entity_matcher", default_config={"label": "LEGAL_ENTITY"})
def create_legal_entity_matcher(nlp, name, label):
    """Factory to create and register the custom matcher component."""
    # This is the core engine containing all 12 custom NER rules
    return LegalEntityMatcher(nlp.vocab, label)

# --- 2. Custom Matcher Class (The Rule Engine) ---

class LegalEntityMatcher:
    def __init__(self, vocab, label):
        self.matcher = Matcher(vocab)
        self.label = label
        
        # --- Define Patterns for ALL Legal Entities ---
        
        # CORE LEGAL ENTITIES
        
        # 1. CASE ID (Example: 2024-CV-101)
        self.matcher.add("CASE_ID_PATTERN", [[{"TEXT": {"REGEX": r"\d{4}-CV-\d+"}}]],
                         on_match=self.set_case_id_label)
        
        # 2. COURT NAME (Example: Supreme Court, NCLT)
        self.matcher.add("COURT_NAME_PATTERN",
            [
                [{"LOWER": "supreme"}, {"LOWER": "court"}],
                [{"LOWER": "national"}, {"LOWER": "green"}, {"LOWER": "tribunal"}], 
                [{"LOWER": "nclt"}] 
            ],
            on_match=self.set_court_name_label)
        
        # 3. LEGAL DATE (Example: the 5th day of October, 2025)
        self.matcher.add("LEGAL_DATE_PATTERN",
            [
                [{"LOWER": "the"}, {"IS_DIGIT": True}, {"LOWER": "day"}, 
                 {"LOWER": "of"}, {"POS": "PROPN"}, {"TEXT": ","}, {"IS_DIGIT": True}]
            ],
            on_match=self.set_legal_date_label)
        
        # 4. JURISDICTION (Example: County of Los Angeles, State of Texas)
        self.matcher.add("JURISDICTION_PATTERN",
            [
                [{"LOWER": "county"}, {"LOWER": "of"}, {"POS": "PROPN", "OP": "+"}], 
                [{"LOWER": "state"}, {"LOWER": "of"}, {"POS": "PROPN"}]
            ],
            on_match=self.set_jurisdiction_label)
        
        # DOMAIN-SPECIFIC ENTITIES
        
        # 5. CONTRACT TYPE (Commercial, Employment, Energy)
        self.matcher.add("CONTRACT_TYPE_PATTERN",
            [
                [{"TEXT": {"IN": ["NDA", "MOU", "PPA"]}}], 
                [{"LOWER": "service"}, {"LOWER": "agreement"}],
                [{"LOWER": "bot"}, {"LOWER": "contract"}],
            ],
            on_match=self.set_contract_type_label)

        # 6. IP ID (Patent/Trademark Identifiers)
        self.matcher.add("IP_ID_PATTERN",
            [
                [{"TEXT": {"REGEX": r"[A-Z]{2}-\d{4}-\d{7}-[A-Z]\d{1}"}}],
                [{"LOWER": "trademark"}, {"LOWER": "application"}, {"LOWER": "no"}, {"IS_PUNCT": True}, {"IS_DIGIT": True}]
            ],
            on_match=self.set_ip_id_label)

        # 7. ACT / STATUTE (Criminal, Regulatory, Data Privacy)
        self.matcher.add("ACT_STATUTE_PATTERN",
            [
                [{"LOWER": "section"}, {"IS_DIGIT": True}, {"TEXT": "IPC"}],
                [{"TEXT": "DPDP"}, {"LOWER": "act"}], 
                [{"TEXT": "GDPR"}], 
                [{"LOWER": "it"}, {"LOWER": "act"}],
            ],
            on_match=self.set_act_statute_label)

        # 8. DEED TYPE / AGREEMENT TYPE (Real Estate, Banking)
        self.matcher.add("DEED_TYPE_PATTERN",
            [
                [{"LOWER": "sale"}, {"LOWER": "deed"}],
                [{"LOWER": "mortgage"}, {"LOWER": "deed"}],
                [{"LOWER": "power"}, {"LOWER": "of"}, {"LOWER": "attorney"}]
            ],
            on_match=self.set_deed_type_label)
            
        # 9. REGULATORY FILINGS (Securities, Competition, Tax)
        self.matcher.add("REGULATORY_FILING_PATTERN",
            [
                [{"LOWER": "annual"}, {"LOWER": "return"}],
                [{"TEXT": "IPO"}, {"LOWER": "document"}],
                [{"LOWER": "merger"}, {"LOWER": "control"}, {"LOWER": "filing"}]
            ],
            on_match=self.set_regulatory_filing_label)
            
        # 10. BANKRUPTCY & INSOLVENCY (IBC)
        self.matcher.add("INSOLVENCY_PATTERN",
            [
                [{"LOWER": "resolution"}, {"LOWER": "plan"}],
                [{"LOWER": "insolvency"}, {"LOWER": "petition"}],
                [{"TEXT": "IBC"}]
            ],
            on_match=self.set_insolvency_label)
            
        # 11. HEALTHCARE & MEDICAL (Specific Documents)
        self.matcher.add("HEALTH_DOC_PATTERN",
            [
                [{"LOWER": "medical"}, {"LOWER": "negligence"}],
                [{"LOWER": "hospital"}, {"LOWER": "consent"}, {"LOWER": "forms"}]
            ],
            on_match=self.set_health_doc_label)
            
        # 12. INTERNATIONAL LAW & TREATIES
        self.matcher.add("INTL_TREATY_PATTERN",
            [
                [{"LOWER": "bilateral"}, {"LOWER": "treaty"}],
                [{"LOWER": "wto"}, {"LOWER": "trade"}, {"LOWER": "agreement"}],
            ],
            on_match=self.set_intl_treaty_label)


    # --- Matcher Callback Functions (Labeling Logic) ---

    def _set_span_label(self, doc, matches, i, label):
        """Helper to create a new entity span and add it to the doc."""
        match_id, start, end = matches[i]
        # Doc.char_span is used for robust entity creation across tokens
        span = Doc.char_span(doc, doc[start].idx, doc[end-1].idx + len(doc[end-1]), label=label)
        if span:
            # We append the new span to the existing list of entities
            doc.ents = list(doc.ents) + [span]
            
    # Simple callbacks calling the helper function
    def set_case_id_label(self, matcher, doc, i, matches): self._set_span_label(doc, matches, i, "CASE_ID")
    def set_court_name_label(self, matcher, doc, i, matches): self._set_span_label(doc, matches, i, "COURT_NAME")
    def set_legal_date_label(self, matcher, doc, i, matches): self._set_span_label(doc, matches, i, "LEGAL_DATE")
    def set_jurisdiction_label(self, matcher, doc, i, matches): self._set_span_label(doc, matches, i, "JURISDICTION")
    def set_contract_type_label(self, matcher, doc, i, matches): self._set_span_label(doc, matches, i, "CONTRACT_TYPE")
    def set_ip_id_label(self, matcher, doc, i, matches): self._set_span_label(doc, matches, i, "IP_ID")
    def set_act_statute_label(self, matcher, doc, i, matches): self._set_span_label(doc, matches, i, "ACT_STATUTE")
    def set_deed_type_label(self, matcher, doc, i, matches): self._set_span_label(doc, matches, i, "DEED_TYPE")
    def set_regulatory_filing_label(self, matcher, doc, i, matches): self._set_span_label(doc, matches, i, "REG_FILING")
    def set_insolvency_label(self, matcher, doc, i, matches): self._set_span_label(doc, matches, i, "INSOLVENCY_TERM")
    def set_health_doc_label(self, matcher, doc, i, matches): self._set_span_label(doc, matches, i, "HEALTH_DOC")
    def set_intl_treaty_label(self, matcher, doc, i, matches): self._set_span_label(doc, matches, i, "INTL_TREATY")


    def __call__(self, doc):
        """The main method called when the component runs in the pipeline."""
        self.matcher(doc) 
        return doc

# --- 3. User-Facing Load Function ---

def load_legal_nlp(model_name: str = DEFAULT_MODEL):
    """
    Loads a base spaCy model and adds the custom legal NER components.
    This is the function the user calls: lexar.load()
    """
    try:
        # Load the base model 
        nlp = spacy.load(model_name)
    except OSError:
        print(f"Base model '{model_name}' not found. Please ensure it is installed.")
        print(f"Run: python -m spacy download {model_name}")
        return None
    
    # Add your custom legal NER component to the pipeline
    # Placing it before 'ner' ensures custom rules take priority
    if 'ner' in nlp.pipe_names:
        nlp.add_pipe("legal_entity_matcher", before="ner")
    else:
        nlp.add_pipe("legal_entity_matcher", last=True)
        
    return nlp