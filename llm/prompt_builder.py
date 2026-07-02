class PromptBuilder:

    def build(
        self,
        question,
        retrieved_chunks,
    ):

        context = "\n\n".join(retrieved_chunks)

        return f"""
You are MSentinel AI. Answer the question below in plain, simple English.
Keep your answer short — 2 to 3 sentences. Avoid technical jargon.
Only use information from the context. If the answer is not there, say:
"I could not find this information in the uploaded documents."

Context:

{context}

Question: {question}

Answer (2-3 sentences):
"""