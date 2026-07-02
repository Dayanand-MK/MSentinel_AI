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

    def ask(self, question: str):
        results = self.retriever.search(question)
        chunks = results.get("documents", [[]])[0]
        prompt = self.prompt_builder.build(question, chunks)
        answer = self.llm.generate(prompt)
        return answer, results

    def summarize(self, doc_name: str) -> str:
        results = self.retriever.search("summary overview content main points", top_k=5, where={"document": doc_name})
        chunks = results.get("documents", [[]])[0]
        if not chunks:
            return f"No document content found for {doc_name} in database. Make sure it was processed successfully."
        
        context = "\n\n".join(chunks)
        prompt = (
            f"You are MSentinel AI. Summarize the following document content focusing on its core topic, compliance aspects, and security vulnerabilities.\n\n"
            f"Context:\n{context}\n\n"
            f"Summary:"
        )
        return self.llm.generate(prompt)

    def compare(self, doc_names: list[str], aspect: str = "risk and compliance findings") -> str:
        comparison_texts = []
        for name in doc_names:
            results = self.retriever.search(aspect, top_k=3, where={"document": name})
            chunks = results.get("documents", [[]])[0]
            context = "\n\n".join(chunks) if chunks else "No content available."
            comparison_texts.append(f"Document Name: {name}\nContent:\n{context}")
        
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
        results = self.retriever.search("risk score vulnerability exposure leak threat", top_k=4, where={"document": doc_name})
        chunks = results.get("documents", [[]])[0]
        if not chunks:
            return f"No document content found for risk analysis of {doc_name}."
        
        context = "\n\n".join(chunks)
        prompt = (
            f"You are MSentinel AI Security Risk Assessor. Perform a detailed security threat and risk assessment on this text. Identify data exposures and provide reasoning.\n\n"
            f"Context:\n{context}\n\n"
            f"Vulnerability & Risk Analysis Report:"
        )
        return self.llm.generate(prompt)
