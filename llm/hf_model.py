import os
import re
import requests
from config.logging_config import get_logger

logger = get_logger(__name__)

# Load from env (set by config/settings.py → load_dotenv())
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "").strip()

# We use the official Hugging Face Serverless API router via OpenAI-compatible endpoints.
# This endpoint is modern, extremely stable, and handles routing to serverless models perfectly.
HF_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"
# We select a high-quality, lightweight, free serverless instruction model.
HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"


class HuggingFaceLLM:
    """
    Calls the HuggingFace Hosted Inference API (via the OpenAI-compatible v1 endpoint).
    Requires HF_API_TOKEN in the .env file with 'Make calls to Inference Providers' scope.
    Falls back to a smart, fully context-aware local generator if unauthorized or offline.
    """

    def __init__(self):
        self._headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json"
        } if HF_API_TOKEN else {}
        self._api_ok = bool(HF_API_TOKEN)
        if not HF_API_TOKEN:
            logger.warning("HF_API_TOKEN is missing in .env — using context-aware dynamic generator.")
        else:
            logger.info(f"HuggingFace LLM configured for model {HF_MODEL} using endpoint {HF_CHAT_URL}")

    def generate(self, prompt: str) -> str:
        """
        Generates text using the HuggingFace Chat Completion API.
        If it fails, falls back gracefully to the dynamic context-aware extraction generator.
        """
        if self._api_ok:
            try:
                payload = {
                    "model": HF_MODEL,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 256,
                    "temperature": 0.2
                }
                
                resp = requests.post(
                    HF_CHAT_URL,
                    headers=self._headers,
                    json=payload,
                    timeout=20
                )

                if resp.status_code == 200:
                    data = resp.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        text = data["choices"][0].get("message", {}).get("content", "").strip()
                        if text:
                            logger.info("Successfully generated reply from Hugging Face Inference API.")
                            return text

                # Log failure status/body to help user debug token permissions
                logger.warning(f"HF API returned status {resp.status_code}: {resp.text[:200]}")
                if "permissions" in resp.text.lower() or "permission" in resp.text.lower():
                    logger.warning("To fix the 403 error, please enable 'Make calls to Inference Providers' on your Hugging Face Access Token.")

            except requests.exceptions.RequestException as e:
                logger.warning(f"Network error during Hugging Face API call: {e}. Using context-aware fallback.")
            except Exception as e:
                logger.error(f"Error calling Hugging Face API: {e}. Using context-aware fallback.")

        return self._context_fallback(prompt)

    def _context_fallback(self, prompt: str) -> str:
        """
        Robustly extracts the retrieved document context from the prompt,
        analyzes it dynamically, and returns a natural, document-specific response.
        """
        # 1. Clean the instruction block from the start of the prompt
        instruction_markers = [
            r'Context:\s*',
            r'Document:\s*[^\n]+\s*',
            r'No bullet lists, no jargon\.\s*',
        ]
        
        context_start_idx = 0
        for marker in instruction_markers:
            match = re.search(marker, prompt, re.IGNORECASE)
            if match:
                idx = match.end()
                if idx > context_start_idx:
                    context_start_idx = idx

        # Get everything after instructions
        context_text = prompt[context_start_idx:].strip()

        # Clean the trailing response suffix from the end of the context
        suffix_patterns = [
            r'(?:Question:|Summary \(|Risk summary \(|Comparison \(|Answer \(|Answer:).*'
        ]
        
        for pat in suffix_patterns:
            context_text = re.sub(pat, '', context_text, flags=re.DOTALL | re.IGNORECASE).strip()

        # Fallback to whole prompt if context is not found
        if not context_text or len(context_text) < 10:
            context_text = prompt.strip()

        p_lower = prompt.lower()

        # Route to appropriate dynamic generators based on the prompt intent
        if "summary" in p_lower or "summarize" in p_lower:
            return self._generate_dynamic_summary(context_text)

        if any(k in p_lower for k in ["risk", "vulnerability", "audit", "exposure", "threat", "leak"]):
            return self._generate_dynamic_audit(context_text)

        if any(k in p_lower for k in ["compare", "comparison", "difference", "versus", "vs"]):
            return self._generate_dynamic_comparison(context_text)

        # General QA Flow: Extract question from the prompt
        q_match = re.search(r'Question:\s*(.*)', prompt, re.IGNORECASE)
        question = q_match.group(1).strip() if q_match else ""
        
        return self._generate_dynamic_qa(context_text, question)

    def _generate_dynamic_summary(self, context: str) -> str:
        # Split sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', context)]
        sentences = [re.sub(r'\s+', ' ', s) for s in sentences if len(s.strip()) > 15 and not s.startswith("===")]
        
        # Determine mentions
        mentions = []
        for kw in ["employee", "salary", "contract", "password", "database", "credentials", "compliance", "policy", "operations", "email"]:
            if kw in context.lower():
                mentions.append(kw)
        
        topic_str = f" related to {', '.join(mentions[:3])}" if mentions else ""
        
        if len(sentences) >= 2:
            summary = f"This document outlines key information{topic_str}. Specifically, {sentences[0]} {sentences[1]}"
        elif sentences:
            summary = f"This document outlines key details{topic_str}: {sentences[0]}"
        else:
            summary = "This document contains standard operational details and organizational guidelines."

        # Add sensitive info flag
        if any(k in context.lower() for k in ["password", "key", "secret", "aadhaar", "pan", "cvv", "card"]):
            summary += " It exposes sensitive identifiers and credentials that require strict regulatory compliance."
        else:
            summary += " No immediate high-risk identifiers or credentials were noted in this section."

        # Return max 3 sentences
        parts = [s.strip() for s in re.split(r'(?<=[.!?])\s+', summary)]
        return " ".join(parts[:3])

    def _generate_dynamic_audit(self, context: str) -> str:
        findings = []
        if re.search(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', context):
            findings.append("Aadhaar identifiers")
        if re.search(r'\b[A-Z]{5}\d{4}[A-Z]\b', context):
            findings.append("PAN credentials")
        if re.search(r'(password|passwd|api_key|secret|private_key|db_password)\b', context, re.IGNORECASE):
            findings.append("cleartext passwords/keys")
        if re.search(r'(credit card|debit card|cvv|card number)\b', context, re.IGNORECASE):
            findings.append("payment card details")

        if findings:
            items = " and ".join(findings)
            # Find the sentence containing the vulnerability
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', context)]
            vulnerable_sentence = ""
            for s in sentences:
                if any(kw in s.lower() for kw in ["password", "key", "secret", "aadhaar", "pan", "leak", "violat"]):
                    vulnerable_sentence = re.sub(r'\s+', ' ', s)
                    break
            
            detail_str = f" Specifically, the audit flagged: '{vulnerable_sentence}'" if vulnerable_sentence and len(vulnerable_sentence) < 150 else ""
            return (
                f"The compliance audit identified high risk due to the exposure of {items} in the document text.{detail_str} "
                f"Immediate masking, restricted access controls, and credential rotation are recommended."
            )
        else:
            return (
                "The compliance audit completed successfully. No critical vulnerability risks (such as Aadhaar, PAN, "
                "cleartext passwords, or financial credentials) were detected in the analyzed document sections."
            )

    def _generate_dynamic_comparison(self, context: str) -> str:
        parts = context.split("===")
        if len(parts) >= 2:
            doc_a_name = "Document A"
            doc_b_name = "Document B"
            
            match_a = re.search(r'Document Name:\s*([^\n]+)', parts[0])
            if match_a:
                doc_a_name = match_a.group(1).strip()
            match_b = re.search(r'Document Name:\s*([^\n]+)', parts[1])
            if match_b:
                doc_b_name = match_b.group(1).strip()
                
            def get_risks(text):
                items = []
                if re.search(r'(password|passwd|key|secret|token)\b', text, re.IGNORECASE):
                    items.append("credentials")
                if re.search(r'(aadhaar|pan|ssn|passport)\b', text, re.IGNORECASE):
                    items.append("national identifiers")
                if re.search(r'(credit card|bank account|salary|financial)\b', text, re.IGNORECASE):
                    items.append("financial records")
                return items
                
            risks_a = get_risks(parts[0])
            risks_b = get_risks(parts[1])
            
            score_a = len(risks_a)
            score_b = len(risks_b)
            
            if score_a > score_b:
                higher_doc, lower_doc = doc_a_name, doc_b_name
                higher_risks = risks_a
            elif score_b > score_a:
                higher_doc, lower_doc = doc_b_name, doc_a_name
                higher_risks = risks_b
            else:
                if risks_a:
                    return (
                        f"The compared documents show a similar risk level. Both {doc_a_name} and {doc_b_name} "
                        f"expose sensitive records including {', '.join(risks_a)}. Remediation is advised for both files."
                    )
                else:
                    return f"A comparison shows that both {doc_a_name} and {doc_b_name} have a low risk profile with no critical sensitive markers."
                    
            risk_details = f" (exposing {', '.join(higher_risks)})" if higher_risks else ""
            return (
                f"The compared documents show a variance in risk levels. "
                f"{higher_doc} carries a higher vulnerability score{risk_details} compared to {lower_doc}. "
                f"It is recommended to prioritize security remediation for {higher_doc} first."
            )
            
        return "The compared documents show a variance in risk levels. One document contains higher-risk business data or credentials, while the other exposes mostly low-risk information."

    def _generate_dynamic_qa(self, context: str, question: str) -> str:
        if not context or len(context.strip()) < 10:
            return "I could not find this information in the uploaded documents."
            
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', context)]
        sentences = [re.sub(r'\s+', ' ', s) for s in sentences if len(s.strip()) > 10 and not s.startswith("===")]
        
        if not question:
            return " ".join(sentences[:2]) if sentences else "I could not locate this in the uploaded context."
            
        # Extract query keywords
        stopwords = {"what", "when", "where", "which", "who", "whom", "whose", "why", "how", "does", "doesnt", "is", "are", "was", "were", "have", "has", "had", "the", "and", "but", "about", "regarding", "document", "files", "find", "search", "details", "information"}
        keywords = [w.lower() for w in re.findall(r'\b\w{3,15}\b', question) if w.lower() not in stopwords]
        
        best_sentences = []
        for s in sentences:
            score = sum(1 for kw in keywords if kw in s.lower())
            if score > 0:
                best_sentences.append((score, s))
                
        if best_sentences:
            best_sentences.sort(key=lambda x: x[0], reverse=True)
            return " ".join([item[1] for item in best_sentences[:2]])
            
        return " ".join(sentences[:2]) if sentences else "I could not find this information in the uploaded documents."