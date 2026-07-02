from dashboard.metrics import compute_dashboard_metrics
from dashboard.tables import format_entities_table
from dashboard.charts import create_pie_chart, create_bar_chart, create_timeline_chart
from pathlib import Path

class DashboardController:
    def get_metrics(self, processed_docs: dict) -> dict:
        return compute_dashboard_metrics(processed_docs)

    def get_table(self, processed_docs: dict):
        return format_entities_table(processed_docs)

    def get_pie_chart(self, processed_docs: dict):
        return create_pie_chart(processed_docs)

    def get_bar_chart(self, processed_docs: dict):
        return create_bar_chart(processed_docs)

    def get_timeline_chart(self, audit_csv_path: Path):
        return create_timeline_chart(audit_csv_path)
