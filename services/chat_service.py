from rag.qa_engine import QAEngine

class ChatService:
    def __init__(self):
        self.qa = QAEngine()

    def ask(self, question: str):
        return self.qa.ask(question)

    def summarize(self, doc_name: str) -> str:
        return self.qa.summarize(doc_name)

    def compare(self, doc_names: list[str], aspect: str = "risk and compliance findings") -> str:
        return self.qa.compare(doc_names, aspect)

    def answer_compliance(self, question: str) -> str:
        return self.qa.answer_compliance_question(question)

    def analyze_risks(self, doc_name: str) -> str:
        return self.qa.analyze_risks(doc_name)