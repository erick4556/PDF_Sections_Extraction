import pymupdf4llm
import pathlib

md_text = pymupdf4llm.to_markdown("../documents2/10.1007@s11244-007-9022-7.pdf")

print(md_text)