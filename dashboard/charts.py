import pandas as pd
import plotly.express as px
from pathlib import Path

def create_pie_chart(processed_docs: dict):
    categories = []
    for doc in processed_docs.values():
        for ent in doc.entities:
            categories.append(ent.category)
            
    if not categories:
        return None
        
    df = pd.DataFrame({"Category": categories})
    df_counts = df["Category"].value_counts().reset_index()
    df_counts.columns = ["Category", "Count"]
    
    fig = px.pie(
        df_counts, 
        values="Count", 
        names="Category", 
        title="Entities by Category", 
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
    return fig

def create_bar_chart(processed_docs: dict):
    data = []
    for doc in processed_docs.values():
        for ent in doc.entities:
            data.append({"Category": ent.category, "Risk Weight": ent.risk_weight})
            
    if not data:
        return None
        
    df = pd.DataFrame(data)
    df_counts = df.groupby("Category").size().reset_index(name="Count")
    
    fig = px.bar(
        df_counts, 
        x="Category", 
        y="Count", 
        title="Counts of Sensitive Elements", 
        color="Category", 
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
    return fig

def create_timeline_chart(audit_csv_path: Path):
    if not audit_csv_path.exists() or audit_csv_path.stat().st_size == 0:
        return None
        
    try:
        df = pd.read_csv(audit_csv_path)
        # Drop rows where Filename is empty (which are Q&A logs)
        df = df.dropna(subset=["Filename"])
        if df.empty:
            return None
            
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        df["Date"] = df["Timestamp"].dt.date
        df_grouped = df.groupby("Date").size().reset_index(name="Count")
        
        fig = px.line(df_grouped, x="Date", y="Count", title="Documents Processed Over Time", markers=True)
        fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        return fig
    except Exception:
        return None
