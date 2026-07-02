class PromptBuilder:

    def build(
        self,
        question,
        retrieved_chunks,
    ):

        context = "\n\n".join(retrieved_chunks)

        return f"""
You are MSentinel AI.

Answer ONLY from the provided context.

If the answer is unavailable,
reply:

"I could not find this information in the uploaded documents."

Context:

{context}

Question:

{question}

Answer:
"""