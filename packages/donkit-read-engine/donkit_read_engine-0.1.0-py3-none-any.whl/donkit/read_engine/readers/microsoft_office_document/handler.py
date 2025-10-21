import base64
import json
from collections import defaultdict

from docx import Document as DocxDocument
from loguru import logger

from ..microsoft_office_document.parser import (
    DocumentParser,
)
from ..static_visual_format.models import (
    qwen2_vl_7b_model_agent,
)


def document_read_handler(path: str) -> list[dict[str, str | int]]:
    """Processes and extracts structured content from Word document files [DOC/DOCX].
    Returns content with page information similar to PDF handler.

    Args:
        path: Path to the document file

    Returns:
        List of dictionaries containing extracted content with page numbers
    """
    try:
        # Load the Word document from the specified path
        document = DocxDocument(path)

        # Parse the Word document
        parser = DocumentParser(document)
        parsed_document = parser.parse()

        # Группируем контент по страницам
        page_text: dict[int, list[str]] = defaultdict(list)
        result = []

        # Сначала собираем весь текст по страницам
        for item in parsed_document:
            page_num = item.get("page", 1)
            item_type = item.get("type", "")

            if item_type == "Text":
                page_text[page_num].append(item.get("content", ""))
            elif item_type == "Table":
                # Форматируем таблицу в текстовый формат
                table_content = []
                rows = item.get("content", [])

                for row in rows:
                    formatted_row = " | ".join(cell for cell in row if cell)
                    if formatted_row.strip():
                        table_content.append(formatted_row)

                if table_content:
                    table_text = "Table:\n" + "\n".join(table_content)
                    page_text[page_num].append(table_text)
            elif item_type == "Image":
                try:
                    # Анализируем изображение с помощью AI модели
                    image_bytes = item.get("content").getvalue()
                    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
                    image_context = qwen2_vl_7b_model_agent(encoded_image)
                    if image_context.startswith("```json"):
                        image_context = json.loads(
                            image_context.replace("```json", "").replace("```", "")
                        )
                    result.append(
                        {
                            "page": page_num,
                            "type": "Image",
                            "content": image_context,
                            "image_index": len(
                                [
                                    r
                                    for r in result
                                    if r.get("type") == "Image"
                                    and r.get("page") == page_num
                                ]
                            ),
                        }
                    )
                except Exception as e:
                    logger.error(f"Error analyzing image on page {page_num}: {e}")
                    result.append(
                        {
                            "page": page_num,
                            "type": "Image",
                            "content": "Image analysis error",
                            "image_index": len(
                                [
                                    r
                                    for r in result
                                    if r.get("type") == "Image"
                                    and r.get("page") == page_num
                                ]
                            ),
                        }
                    )

        # Добавляем объединенный текст для каждой страницы
        for page_num, texts in sorted(page_text.items()):
            result.append(
                {"page": page_num, "type": "Text", "content": "\n\n".join(texts)}
            )

        # Сортируем результат по страницам и типу (сначала текст, потом изображения)
        result.sort(
            key=lambda x: (
                x.get("page", 0),
                0 if x.get("type", "") == "Text" else 1,
                x.get("image_index", 0),
            )
        )

        return result
    except Exception as e:
        logger.exception(f"Error processing DOCX: {e}")
        return [
            {"page": 1, "type": "Error", "content": "Error processing DOCX document"}
        ]
