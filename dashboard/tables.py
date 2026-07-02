import pandas as pd

def format_entities_table(processed_docs: dict) -> pd.DataFrame:
    rows = []
    for doc in processed_docs.values():
        for ent in doc.entities:
            rows.append({
                "Document": doc.original_name,
                "Category": ent.category,
                "Value": ent.value,
                "Method": ent.method,
                "Confidence": f"{ent.confidence:.2f}",
                "Risk Weight": ent.risk_weight,
                "Page": getattr(ent, "page", 1),
            })
    return pd.DataFrame(rows)
