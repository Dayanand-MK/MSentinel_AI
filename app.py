import streamlit as st
from pathlib import Path

from config.constants import APP_NAME
from config.logging_config import get_logger
from loaders.document_loader import DocumentLoader
from utils.file_utils import allowed_file, save_uploaded_file
from utils.helpers import get_file_size_mb
from preprocessing import TextCleaner
from detection import RegexDetector, SpacyDetector
from utils import remove_duplicate_entities

logger = get_logger(__name__)
loader = DocumentLoader()
cleaner = TextCleaner()
regex_detector = RegexDetector()
spacy_detector = SpacyDetector()

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ MSentinel AI")
st.subheader("AI-Powered Document Security & Compliance Platform")

uploaded_files = st.file_uploader(
    "Choose Documents",
    type=["pdf", "txt", "csv"],
    accept_multiple_files=True,
)

if uploaded_files:

    st.success(f"{len(uploaded_files)} file(s) selected.")

    file_table = []
    previews = []
    documents = []

    progress = st.progress(0)

    for index, uploaded_file in enumerate(uploaded_files):

        if not allowed_file(uploaded_file.name):
            st.error(f"Unsupported file: {uploaded_file.name}")
            continue

        saved_path = save_uploaded_file(uploaded_file)

        document = loader.load(saved_path)
        documents.append(document)

        document = cleaner.clean(document)

        document = regex_detector.detect(document)
        document = spacy_detector.detect(document)
        document = remove_duplicate_entities(document)

        # preview = document.raw_text[ : 500] if document.raw_text else "No text extracted."

        # previews.append(
        #    {
        #        "name": uploaded_file.name,
        #        "preview": preview,
        #    }
        #)

        logger.info("Uploaded %s", uploaded_file.name)

        file_table.append(
            {
                "Original Name": uploaded_file.name,
                "Saved Name": Path(saved_path).name,
                "Type": saved_path.suffix.replace(".", "").upper(),
                "Size (MB)": get_file_size_mb(saved_path),
                "Characters": document.character_count,
                "Words": document.word_count,
                "Lines": document.line_count,
                "OCR Used": document.ocr_used,
            }
        )

        progress.progress((index + 1) / len(uploaded_files))

    st.divider()

    st.subheader("Uploaded Files")

    st.dataframe(
        file_table,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Document Preview")

    for document in documents:
        with st.expander(document.original_name):
            st.code(document.cleaned_text[:1000])

    st.subheader("Document Statistics")

    stats = []

    for doc in documents:
        stats.append(
            {
                "Document": doc.original_name,
                "Characters": doc.character_count,
                "Words": doc.word_count,
                "Lines": doc.line_count,
                "OCR": "Yes" if doc.ocr_used else "No",
            }
        )

    st.dataframe(
        stats,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Detected Sensitive Information")

    for doc in documents:

        st.markdown(f"### {doc.original_name}")

        if not doc.entities:
            st.success("No sensitive information detected.")
            continue

        rows = []

        for entity in doc.entities:

            rows.append(
                {
                    "Category": entity.category,
                    "Value": entity.value,
                    "Method": entity.method,
                    "Confidence": f"{entity.confidence:.2f}",
                    "Risk": entity.risk_weight,
                    "Position": f"{entity.start}-{entity.end}",
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    st.subheader("Extracted Text Preview")

    for item in previews:
        with st.expander(item["name"], expanded=False):
            st.code(item["preview"])

    st.success("Uploaded files are ready for analysis.")