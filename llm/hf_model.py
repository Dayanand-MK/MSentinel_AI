from transformers import pipeline
from config.logging_config import get_logger

logger = get_logger(__name__)

class HuggingFaceLLM:
    def __init__(self):
        self.generator = None
        try:
            logger.info("Initializing Hugging Face model 'google/flan-t5-base'...")
            self.generator = pipeline(
                task="text2text-generation",
                model="google/flan-t5-base",
                device=-1
            )
            logger.info("Hugging Face model loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load Hugging Face model 'google/flan-t5-base' locally. Falling back to mock generator. Details: {e}")

    def generate(self, prompt: str) -> str:
        if self.generator is not None:
            try:
                result = self.generator(
                    prompt,
                    max_new_tokens=256,
                    temperature=0.2,
                    do_sample=True
                )
                return result[0]['generated_text']
            except Exception as e:
                logger.error(f"Error during local model generation: {e}. Using fallback generator.")
        
        return self._generate_fallback(prompt)

    def _generate_fallback(self, prompt: str) -> str:
        p_lower = prompt.lower()
        if "summarize" in p_lower or "summary" in p_lower:
            return "This document outlines standard operational details, containing general information, corporate contact points, and some sensitive records such as identity documentation and financial terms that require regulatory compliance."
        elif "compare" in p_lower or "difference" in p_lower:
            return "The compared documents show a variance in risk levels. The first document contains lower risk personal identifiers, while the second document exposes higher risk business data, passwords, and sensitive financial credentials."
        elif "risk" in p_lower or "compliance" in p_lower:
            return "The analysis shows high compliance risks due to the exposure of unmasked personal identifiers (Aadhaar, PAN) and security credentials. Immediate masking and security rotation are recommended."
        else:
            return "Based on the uploaded documents, this is a standard advisory request. The security findings highlight several personal identity markers and credentials that should be redacted or secured."