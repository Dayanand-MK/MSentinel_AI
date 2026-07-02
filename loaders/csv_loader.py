from pathlib import Path
import pandas as pd

from config.logging_config import get_logger

logger = get_logger(__name__)


class CSVLoader:
    def extract_text(self, file_path: Path) -> str:
        try:
            df = pd.read_csv(file_path)
            text = df.to_string(index=False)
            logger.info("CSV extracted: %s", file_path.name)
            return text

        except Exception as e:
            logger.exception("CSV extraction failed.")
            raise RuntimeError(str(e))