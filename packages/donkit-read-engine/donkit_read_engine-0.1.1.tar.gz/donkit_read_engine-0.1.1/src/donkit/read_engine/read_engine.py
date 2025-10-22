import json
import os
import argparse
import importlib
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv

from .readers.portable_document_format.handler import pdf_read_handler
from .readers.json_document_format.handler import json_document_read_handler
from .readers.microsoft_office_sheet.handler import (
    sheet_read_handler,
)
from .readers.text_document_format.handler import (
    text_document_read_handler,
)
from .readers.static_visual_format.handler import image_read_handler


load_dotenv()


def simple_pdf_read_handler(path: str) -> list[dict[str, str | int]]:
    """PDF parser without LLM image analysis.

    Uses `StructuredPDFProcessor` with analyze_images=False to avoid requiring
    external AI credentials.
    """
    pdf_parser = importlib.import_module(
        "donkit.read_engine.readers.portable_document_format.pdf_parser"
    )
    # Prefer robust hybrid parser that chooses the best available backend
    if hasattr(pdf_parser, "parse_pdf_hybrid"):
        return pdf_parser.parse_pdf_hybrid(path)
    # Fallback chain if hybrid is unavailable for any reason
    result = None
    if getattr(pdf_parser, "HAS_UNSTRUCTURED", False):
        try:
            result = pdf_parser.parse_pdf_unstructured(path)
            # Check if result is an error dict and use fallback
            if result and isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and result[0].get("type") == "Error":
                    result = None
        except Exception:
            result = None

    if result is None:
        processor = pdf_parser.StructuredPDFProcessor(analyze_images=False)
        result = processor.process_pdf(path)

    return result


class DonkitReader:
    def __init__(self):
        # Decide which PDF reader to use based on environment (LLM creds present or not)
        use_llm_pdf = any(
            os.getenv(k)
            for k in (
                "OPENAI_API_KEY",
                "RAGOPS_VERTEX_CREDENTIALS",
                "GOOGLE_APPLICATION_CREDENTIALS",
                "VERTEXAI_PROJECT",
                "VERTEX_PROJECT",
            )
        )
        from loguru import logger

        logger.debug(use_llm_pdf)
        if use_llm_pdf:
            # Lazy import to avoid importing optional deps at import time
            def selected_pdf_reader(p):
                return pdf_read_handler(p)
        else:
            selected_pdf_reader = simple_pdf_read_handler

        self.readers = {
            ".txt": text_document_read_handler,
            ".json": json_document_read_handler,
            ".csv": text_document_read_handler,
            ".pdf": selected_pdf_reader,
            ".docx": (
                lambda p: importlib.import_module(
                    "donkit.read_engine.readers.microsoft_office_document.handler"
                ).document_read_handler(p)
            ),
            ".doc": (
                lambda p: importlib.import_module(
                    "donkit.read_engine.readers.microsoft_office_document.handler"
                ).document_read_handler(p)
            ),
            ".pptx": (
                lambda p: importlib.import_module(
                    "donkit.read_engine.readers.microsoft_office_presentation.handler"
                ).presentation_read_handler(p, pdf_handler=selected_pdf_reader)
            ),
            ".xlsx": sheet_read_handler,
            ".xls": sheet_read_handler,
            ".png": image_read_handler,
            ".jpg": image_read_handler,
            ".jpeg": image_read_handler,
        }

    def read_document(
        self,
        file_path: str,
        output_type: Literal["text", "json", "markdown"],
    ) -> str:
        """Main method to read a document from S3 and extract its content.

        Args:
            file_path: Path to the file in S3 storage (path/to/file)
                       without bucket name
            output_type: Output format ("text", "json", or "markdown")
            transition process. When we completely switch to a system with projects in companies,
            we need to make it required.

        Returns:
            Path to the processed output file in S3
        """
        try:
            # Get file extension to determine which reader to use
            file_extension = Path(file_path).suffix.lower()
            # Extract content using the appropriate reader (run in thread pool to avoid blocking)
            content = self.__extract_content_sync(file_path, file_extension)
            # Process output based on requested format
            output_file_path = self._process_output(content, file_path, output_type)
            return output_file_path
        except Exception as e:
            raise RuntimeError(f"Failed to process document: {e!s}") from e

    def __extract_content_sync(
        self, file_path: str, file_extension: str
    ) -> str | list[dict[str, Any]]:
        """Synchronous content extraction (runs in thread pool).
        Args:
            file_path: Path to the local file
            file_extension: File extension (including the dot)
        Returns:
            Content extracted from the document (either text or structured data)
        """
        try:
            if file_extension in self.readers:
                return self.readers[file_extension](file_path)
            else:
                msg = (
                    f"Unsupported file extension: {file_extension}"
                    f"Supported extensions: {list(self.readers.keys())}"
                )
                raise ValueError(msg)
        except Exception:
            raise

    @staticmethod
    def _process_output(
        content: str | list[dict[str, Any]],
        file_path: str,
        output_type: Literal["text", "json", "markdown"],
    ) -> str:
        """Process extracted content.

        Args:
            content: Extracted content (text or structured data)
            file_path: Original S3 object key
            output_type: Output format type
        """
        # Create output file name based on original file and output type
        path = Path(file_path)
        file_name = path.stem  # Get filename without extension
        output_dir = str(path.parent / Path("processed"))  # Prepend .txt/ to the path
        if output_type == "text" and isinstance(content, str):  # noqa duplicate content
            output_file_name = f"{file_name}.txt"  # Use .txt extension
            processed_content = content
        elif output_type == "text" and not isinstance(content, str):
            # Convert structured content to text
            output_file_name = f"{file_name}.txt"  # Use .txt extension
            if isinstance(content, list):
                # Handle list of pages/sections
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and "content" in item:
                        text_parts.append(str(item.get("content", "")))
                    else:
                        text_parts.append(str(item))
                processed_content = "\n".join(text_parts)
            else:
                processed_content = str(content)
        elif output_type == "markdown":
            output_file_name = f"{file_name}.md"
            if isinstance(content, list):
                # Handle list of pages/sections
                md_parts = []
                for item in content:
                    if isinstance(item, dict):
                        # Add page headers
                        page_num = item.get("page", "")
                        item_type = item.get("type", "")

                        if page_num:
                            if item_type == "Text":
                                md_parts.append(
                                    f"## Page {page_num}\n\n{item.get('content', '')}"
                                )
                            elif item_type == "Image":
                                md_parts.append(
                                    f"### Image on Page {page_num}\n\n{item.get('content', '')}"
                                )
                            else:
                                md_parts.append(
                                    f"### {item_type} on Page {page_num}\n\n{item.get('content', '')}"
                                )
                        else:
                            md_parts.append(str(item.get("content", "")))
                    else:
                        md_parts.append(str(item))
                processed_content = "\n\n".join(md_parts)
            elif isinstance(content, str):
                processed_content = content
            else:
                processed_content = str(content)
        else:  # json
            output_file_name = f"{file_name}.json"
            if isinstance(content, str):
                content = [
                    {
                        "page": 1,
                        "type": "Text",
                        "content": content,
                    }
                ]
            processed_content = json.dumps(
                {"content": content}, ensure_ascii=False, indent=2
            )
        output_path = Path(output_dir) / output_file_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(processed_content, encoding="utf-8")
        return output_path.as_posix()


def main() -> None:
    """CLI entry point for Donkit read engine.

    Usage:
        donkit-read-engine <file_path> [--output-type text|json|markdown]
    """
    parser = argparse.ArgumentParser(
        prog="donkit-read-engine",
        description="Read a document and export extracted content to text/json/markdown",
    )
    parser.add_argument(
        "file_path",
        nargs="?",
        default="/Users/romanlosev/donkit/platform/ragops-agent/shared/read-engine/src/files",
        help="Path to a local file or directory to read (directory will be processed recursively)",
    )
    parser.add_argument(
        "--output-type",
        choices=["text", "json", "markdown"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--pdf-strategy",
        choices=["fast", "hi_res", "ocr_only", "auto"],
        default=None,
        help="unstructured parsing strategy (overrides UNSTRUCTURED_STRATEGY)",
    )
    parser.add_argument(
        "--ocr-lang",
        default=None,
        help="OCR languages for unstructured (e.g., 'rus+eng') (overrides UNSTRUCTURED_OCR_LANG)",
    )

    args = parser.parse_args()

    # Apply optional strategy settings for unstructured before constructing reader
    if args.pdf_strategy:
        os.environ["UNSTRUCTURED_STRATEGY"] = args.pdf_strategy
    if args.ocr_lang:
        os.environ["UNSTRUCTURED_OCR_LANG"] = args.ocr_lang

    reader = DonkitReader()
    input_path = Path(args.file_path)
    if input_path.is_dir():
        exts = set(reader.readers.keys())
        files: list[Path] = [
            f for f in input_path.rglob("*") if f.is_file() and f.suffix.lower() in exts
        ]
        for f in sorted(files):
            try:
                output_path = reader.read_document(f.as_posix(), args.output_type)  # type: ignore[arg-type]
                print(output_path)
            except Exception as e:
                print(f"ERROR processing {f}: {e}")
    else:
        output_path = reader.read_document(input_path.as_posix(), args.output_type)  # type: ignore[arg-type]
        print(output_path)


if __name__ == "__main__":
    main()
