import re
from models import Document, Entity
from llm.hf_model import HuggingFaceLLM
from config.logging_config import get_logger
from risk.risk_weights import RISK_WEIGHTS

logger = get_logger(__name__)

KEYWORDS_MAP = {
    "Business Confidential": ["confidential", "proprietary", "restricted", "non-disclosure", "nda"],
    "Internal Documents": ["internal use", "internal only", "private", "not for distribution"],
    "Trade Secrets": ["trade secret", "patent pending", "proprietary information", "source code", "algorithm"],
    "Contracts": ["contract", "agreement", "signatory", "hereby agrees", "parties", "covenant"],
    "Legal Documents": ["court", "litigation", "arbitration", "jurisdiction", "lawsuit", "legal notice", "plaintiff", "defendant"],
    "Sensitive Business Risks": ["financial forecast", "acquisition", "merger", "bankruptcy", "audit report", "insider trading", "liability"]
}

class LLMValidator:
    def __init__(self):
        self.llm = HuggingFaceLLM()

    def detect(self, document: Document) -> Document:
        entities = []
        text = document.cleaned_text
        cleaned_pages = document.metadata.get("cleaned_pages", [text])
        filename = document.original_name

        for page_idx, page_text in enumerate(cleaned_pages, start=1):
            if not page_text.strip():
                continue

            matched_categories = []
            for category, keywords in KEYWORDS_MAP.items():
                for kw in keywords:
                    if re.search(r'\b' + re.escape(kw) + r'\b', page_text.lower()):
                        matched_categories.append(category)
                        break

            if not matched_categories:
                continue

            logger.info(f"Page {page_idx} of {filename} matched pre-filter keywords for: {matched_categories}. Calling LLM...")
            
            categories_str = ", ".join(matched_categories)
            prompt = (
                f"Analyze if this text contains sensitive corporate elements under these categories: {categories_str}.\n"
                f"Text:\n{page_text[:1000]}\n\n"
                f"Response format MUST be Category: <category>, Snippet: <exact phrase>, Confidence: <0.0-1.0>, Reason: <reason>.\n"
                f"If none of these are present, response MUST be 'None'."
            )

            llm_response = self.llm.generate(prompt)
            parsed_entities = self._parse_llm_response(llm_response, page_text, page_idx, filename)
            
            if parsed_entities:
                entities.extend(parsed_entities)
            else:
                for cat in matched_categories:
                    for line in page_text.splitlines():
                        for kw in KEYWORDS_MAP[cat]:
                            if kw in line.lower():
                                start_char = page_text.find(line)
                                end_char = start_char + len(line)
                                entities.append(
                                    Entity(
                                        category=cat,
                                        value=line[:100].strip(),
                                        confidence=0.85,
                                        method="LLM Validation",
                                        risk_weight=RISK_WEIGHTS.get(cat, 5),
                                        start=start_char if start_char >= 0 else 0,
                                        end=end_char if start_char >= 0 else len(line),
                                        page=page_idx,
                                        filename=filename
                                    )
                                )
                                break
                        else:
                            continue
                        break

        unique_llm_entities = []
        seen = set()
        for ent in entities:
            key = (ent.category, ent.value, ent.start, ent.end, ent.page)
            if key not in seen:
                seen.add(key)
                unique_llm_entities.append(ent)

        document.entities.extend(unique_llm_entities)
        logger.info(f"{len(unique_llm_entities)} LLM entities detected in {filename}")
        return document

    def _parse_llm_response(self, response: str, text: str, page: int, filename: str) -> list[Entity]:
        if not response or "none" in response.lower() or len(response.strip()) < 10:
            return []

        entities = []
        try:
            cat_match = re.search(r"Category:\s*([^,\n]+)", response)
            val_match = re.search(r"Snippet:\s*([^,\n]+)", response)
            conf_match = re.search(r"Confidence:\s*([0-9.]+)", response)

            if cat_match and val_match:
                cat = cat_match.group(1).strip()
                val = val_match.group(1).strip()
                conf = float(conf_match.group(1).strip()) if conf_match else 0.90
                
                start_offset = text.find(val)
                if start_offset == -1:
                    start_offset = text.lower().find(val.lower())
                
                if start_offset == -1:
                    start_offset = 0
                end_offset = start_offset + len(val)

                entities.append(
                    Entity(
                        category=cat,
                        value=val,
                        confidence=conf,
                        method="LLM Validation",
                        risk_weight=RISK_WEIGHTS.get(cat, 5),
                        start=start_offset,
                        end=end_offset,
                        page=page,
                        filename=filename
                    )
                )
        except Exception as e:
            logger.error(f"Error parsing LLM response '{response}': {e}")
        
        return entities
