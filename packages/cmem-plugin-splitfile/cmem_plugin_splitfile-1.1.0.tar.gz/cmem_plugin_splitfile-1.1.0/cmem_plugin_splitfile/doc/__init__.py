"""doc"""

from pathlib import Path

with (Path(__path__[0]) / "splitfile_doc.md").open("r", encoding="utf-8") as f:
    SPLITFILE_DOC = f.read()
