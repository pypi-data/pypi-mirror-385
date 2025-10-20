import pymupdf
from io import BytesIO


def extract_text_from_pdf(
    source: str | BytesIO,
    *,
    start_page: int = 0,
    end_page: int | None = None,
    step: int | None = None,
    strategy: str = "text",
    sort: bool = True,
) -> str:
    if isinstance(source, str):
        doc = pymupdf.open(source, filetype="pdf")

    if isinstance(source, BytesIO):
        doc = pymupdf.open(stream=source, filetype="pdf")

    total_pages = doc.page_count

    if end_page is None or end_page > total_pages:
        end_page = total_pages

    if start_page < 0 or start_page > total_pages:
        raise ValueError(
            "Invalid Page Range: start_page must be between 0 and total number of pages in document"
        )

    pages = doc.pages(start=start_page, stop=end_page, step=step)

    if strategy == "text":
        return chr(12).join([page.get_text(strategy, sort=sort) for page in pages])

    return [page.get_text(strategy, sort=sort) for page in pages]
