from __future__ import annotations
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import re
from pathlib import Path
from bs4 import BeautifulSoup
from models import IngestedFile


def parse_text_file(path: str | Path) -> IngestedFile:
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in (".html", ".htm"):
        raw = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(raw, "html.parser")
        body = soup.body if soup.body else soup
        text = body.get_text(separator=" ")
        content = re.sub(r"\s+", " ", text).strip()
        file_type = "html"
    else:
        content = path.read_text(encoding="utf-8").strip()
        file_type = "text"

    return IngestedFile(
        filename=path.name,
        file_type=file_type,
        content=content,
        metadata={"word_count": len(content.split())},
    )
