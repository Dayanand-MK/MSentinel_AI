import re
from pathlib import Path
from rag import Retriever
from llm.hf_model import HuggingFaceLLM
from llm.prompt_builder import PromptBuilder
from config.logging_config import get_logger

logger = get_logger(__name__)

class QAEngine:
    def __init__(self):
        self.retriever = Retriever()
        self.llm = HuggingFaceLLM()
        self.prompt_builder = PromptBuilder()

    def _resolve_doc_name(self, doc_name: str) -> tuple[str, str]:
        """
        Resolves a human document name to (chroma_db_name, display_name).
        Correctly supports UUID filename mappings if the file was processed in the current session.
        """
        # Fetch from active session if possible to obtain actual stored file name
        try:
            import streamlit as st
            if "processed_docs" in st.session_state and doc_name in st.session_state.processed_docs:
                doc = st.session_state.processed_docs[doc_name]
                return doc.original_name, doc_name
        except Exception:
            pass
            
        # Fallback: check case-insensitive match against all indexed documents
        doc_names = self.retriever.get_all_document_names()
        for name in doc_names:
            if name.lower() == doc_name.lower() or Path(name).stem.lower() == doc_name.lower():
                return name, name
                
        # If not found in session/DB, return input as both
        return doc_name, doc_name

    def ask(self, question: str):
        q_lower = question.lower().strip()
        
        # Check Streamlit session state for human name mapping
        session_docs = []
        try:
            import streamlit as st
            if "processed_docs" in st.session_state:
                session_docs = list(st.session_state.processed_docs.keys())
        except Exception:
            pass
            
        # Get all indexed document names in ChromaDB
        db_doc_names = self.retriever.get_all_document_names()
        
        # Combine all candidates for document name matching
        candidate_names = list(set(db_doc_names + session_docs))
        
        # Identify which document names are mentioned in the query
        matched_docs = []
        for name in candidate_names:
            stem = Path(name).stem
            if name.lower() in q_lower or stem.lower() in q_lower:
                matched_docs.append(name)
        
        if matched_docs:
            is_compare = any(kw in q_lower for kw in ["compare", "comparison", "versus", "vs", "difference"])
            is_risk = any(kw in q_lower for kw in ["audit", "vulnerability", "risk", "exposure", "threat", "leak"])
            is_summary = any(kw in q_lower for kw in ["summary", "summarize", "overview", "main points", "brief"])
            
            if is_compare:
                if len(matched_docs) == 1 and len(candidate_names) > 1:
                    other = [d for d in candidate_names if d != matched_docs[0]]
                    matched_docs.append(other[0])
                
                aspect = "risk and compliance findings"
                aspect_match = re.search(r"regarding\s+['\"]?([^'\"]+)['\"]?", question, re.IGNORECASE)
                if aspect_match:
                    aspect = aspect_match.group(1).strip()
                
                # Fetch sources using the resolved chroma names
                chroma_names = [self._resolve_doc_name(d)[0] for d in matched_docs]
                results = self.retriever.search(aspect, top_k=3 * len(matched_docs))
                answer = self.compare(matched_docs, aspect)
                return answer, results
            
            elif is_risk:
                target_doc = matched_docs[0]
                chroma_name, display_name = self._resolve_doc_name(target_doc)
                results = self.retriever.search("risk score vulnerability exposure leak threat", top_k=4, where={"document": chroma_name})
                answer = self.analyze_risks(target_doc)
                return answer, results
                
            elif is_summary:
                target_doc = matched_docs[0]
                chroma_name, display_name = self._resolve_doc_name(target_doc)
                results = self.retriever.search("summary overview content main points", top_k=5, where={"document": chroma_name})
                answer = self.summarize(target_doc)
                return answer, results

        # Default standard Q&A flow
        results = self.retriever.search(question)
        chunks = results.get("documents", [[]])[0]
        prompt = self.prompt_builder.build(question, chunks)
        answer = self.llm.generate(prompt)
        return answer, results

    def summarize(self, doc_name: str) -> str:
        chroma_name, display_name = self._resolve_doc_name(doc_name)
        results = self.retriever.search("summary overview content main points", top_k=5, where={"document": chroma_name})
        chunks = results.get("documents", [[]])[0]
        if not chunks:
            return f"No document content found for {display_name} in database. Make sure it was processed successfully."
        
        context = "\n\n".join(chunks)
        prompt = (
            f"You are MSentinel AI. Summarize the following document content focusing on its core topic, compliance aspects, and security vulnerabilities.\n"
            f"Document Name: {display_name}\n\n"
            f"Context:\n{context}\n\n"
            f"Summary:"
        )
        return self.llm.generate(prompt)

    def compare(self, doc_names: list[str], aspect: str = "risk and compliance findings") -> str:
        comparison_texts = []
        for name in doc_names:
            chroma_name, display_name = self._resolve_doc_name(name)
            results = self.retriever.search(aspect, top_k=3, where={"document": chroma_name})
            chunks = results.get("documents", [[]])[0]
            context = "\n\n".join(chunks) if chunks else "No content available."
            comparison_texts.append(f"Document Name: {display_name}\nContent:\n{context}")
        
        all_context = "\n\n===\n\n".join(comparison_texts)
        prompt = (
            f"You are MSentinel AI. Compare the following documents based on their '{aspect}'. Highlight the differences in sensitive data exposure, security compliance, and risk level.\n\n"
            f"{all_context}\n\n"
            f"Detailed Comparison:"
        )
        return self.llm.generate(prompt)

    def answer_compliance_question(self, question: str) -> str:
        results = self.retriever.search(question, top_k=5)
        chunks = results.get("documents", [[]])[0]
        context = "\n\n".join(chunks)
        prompt = (
            f"You are MSentinel AI, a specialized document security compliance expert.\n"
            f"Answer this compliance question based on the document facts. Relate it to security frameworks (GDPR, SOC2, HIPAA) if applicable.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}\n\n"
            f"Compliance Advisory Answer:"
        )
        return self.llm.generate(prompt)

    def analyze_risks(self, doc_name: str) -> str:
        chroma_name, display_name = self._resolve_doc_name(doc_name)
        results = self.retriever.search("risk score vulnerability exposure leak threat", top_k=4, where={"document": chroma_name})
        chunks = results.get("documents", [[]])[0]
        if not chunks:
            return f"No document content found for risk analysis of {display_name}."
        
        context = "\n\n".join(chunks)
        prompt = (
            f"You are MSentinel AI Security Risk Assessor. Perform a detailed security threat and risk assessment on this text. Identify data exposures and provide reasoning.\n"
            f"Document Name: {display_name}\n\n"
            f"Context:\n{context}\n\n"
            f"Vulnerability & Risk Analysis Report:"
        )
        return self.llm.generate(prompt)
