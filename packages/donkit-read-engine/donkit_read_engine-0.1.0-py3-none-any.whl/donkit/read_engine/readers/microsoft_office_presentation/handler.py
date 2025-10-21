import glob
import os
import pathlib
import shutil
import subprocess
from typing import Callable

from loguru import logger


def convert_pptx_to_pdf(pptx_path: str, tmp_dir: str) -> str:
    """Конвертирует PPTX в PDF через LibreOffice."""
    command = f'soffice --headless --convert-to pdf --outdir "{tmp_dir}" "{pptx_path}"'
    logger.info(f"Выполняем команду: {command}")

    subprocess.call(command, shell=True)
    pdf_files = glob.glob(f"{tmp_dir}/*.pdf")
    if not pdf_files:
        raise FileNotFoundError(f"Файл PDF не был создан в папке: {tmp_dir}")

    output_pdf_path = pdf_files[0]
    logger.info(f"Файл PDF создан: {output_pdf_path}")

    return output_pdf_path


def presentation_read_handler(
    pptx_path: str, pdf_handler: Callable
) -> list[dict[str, str | int]]:
    """Extracts text and image placeholders from a PPTX file using OCR model after converting it to PDF.

    :param pptx_path: Path to the PPTX file to process.
    :param pdf_handler: Callable to handle PDF processing.
    :return: A string containing the extracted text and image placeholders.
    """
    # Create a temporary directory for PDF conversion and extraction
    tmp_dir = pathlib.Path(__file__).parent.joinpath("tmp")

    # Remove existing temp directory and recreate it
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    # Define path for the temporary PDF file
    # output_pdf_path = f"{tmp_dir}/{pathlib.Path(pptx_path).name}.pdf"

    # Convert PPTX to PDF
    output_pdf_path = convert_pptx_to_pdf(pptx_path, str(tmp_dir))

    # Use the PDF handler to extract text and images from the converted PDF
    return pdf_handler(path=output_pdf_path)
