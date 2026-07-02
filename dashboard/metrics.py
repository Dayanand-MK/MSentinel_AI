def compute_dashboard_metrics(processed_docs: dict) -> dict:
    if not processed_docs:
        return {
            "uploaded_files": 0,
            "sensitive_data_count": 0,
            "avg_compliance_score": 100.0,
            "avg_risk_score": 0.0,
            "avg_processing_time": 0.0
        }
    
    total_docs = len(processed_docs)
    total_entities = sum(len(doc.entities) for doc in processed_docs.values())
    avg_compliance = sum(doc.compliance_score for doc in processed_docs.values()) / total_docs
    avg_risk = sum(doc.risk_score for doc in processed_docs.values()) / total_docs
    avg_proc_time = sum(doc.processing_time for doc in processed_docs.values()) / total_docs
    
    return {
        "uploaded_files": total_docs,
        "sensitive_data_count": total_entities,
        "avg_compliance_score": round(avg_compliance, 1),
        "avg_risk_score": round(avg_risk, 1),
        "avg_processing_time": round(avg_proc_time, 2)
    }
