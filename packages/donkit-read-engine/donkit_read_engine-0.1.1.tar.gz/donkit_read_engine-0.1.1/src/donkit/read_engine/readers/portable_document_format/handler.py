import base64
import io
import json
import os
import pathlib
import re
import shutil
import threading
import time
import uuid
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed

import fitz
import psutil
from loguru import logger

from ..static_visual_format.models import (
    qwen2_vl_7b_model_agent,
    get_image_analysis_service,
)


def _sanitize_json_like(text: str) -> str:
    """Best-effort fixes for common JSON formatting glitches from LLMs.

    - Fix pattern: "]},\n\n\n\n\n\n\n\n\n\n\n\n \"key\"" -> "], \"key\"" (extra '}' right after closing list)
    - Remove trailing commas before closing braces/brackets: ", }" -> " }", ", ]" -> " ]"
    """
    s = text
    # 1) Extra '}' right after a list ends and before next key
    s = re.sub(r"\]\s*},\s*\"", r"], \"", s)
    # 2) Remove trailing commas before } or ]
    s = re.sub(r",\s*([}\]])", r"\1", s)
    return s


def _fix_json_with_llm(invalid_json: str, error_message: str) -> str | None:
    """Attempt to fix invalid JSON by asking LLM to correct it.

    Args:
        invalid_json: The invalid JSON string
        error_message: The error message from JSON parser

    Returns:
        Fixed JSON string or None if LLM call fails
    """
    try:
        # Limit JSON size to prevent excessive processing time (10KB max)
        if len(invalid_json) > 10240:
            logger.debug(
                f"JSON too large for LLM fix ({len(invalid_json)} bytes), skipping"
            )
            return None

        service = get_image_analysis_service()
        # Check if service has text-only method (GeminiImageAnalysisService)
        if not hasattr(service, "call_text_only"):
            logger.debug(
                "Image analysis service doesn't support text-only calls, skipping LLM fix"
            )
            return None

        prompt = f"""Fix the following invalid JSON. The JSON has a syntax error: {error_message}
            
            Invalid JSON:
            ```json
            {invalid_json}
            ```
            
            Return ONLY the corrected valid JSON without any explanations, markdown formatting, or additional text. Just the raw JSON.""".strip()

        logger.info("Requesting LLM to fix invalid JSON...")
        fixed_json = service.call_text_only(prompt)

        # Strip potential markdown fences from response
        fixed_json = fixed_json.strip()
        if fixed_json.startswith("```json"):
            fixed_json = fixed_json[7:]
        elif fixed_json.startswith("```"):
            fixed_json = fixed_json[3:]
        if fixed_json.endswith("```"):
            fixed_json = fixed_json[:-3]
        fixed_json = fixed_json.strip()

        # Validate that the fix worked
        try:
            json.loads(fixed_json)
            logger.info("LLM successfully fixed the JSON")
            return fixed_json
        except json.JSONDecodeError as e:
            logger.warning(f"LLM-fixed JSON is still invalid: {e}")
            return None

    except Exception as e:
        logger.warning(f"Failed to fix JSON with LLM: {e}")
        return None


def split_pdf_into_pages(pdf_path: pathlib.Path, output_dir: pathlib.Path) -> None:
    """Splits the PDF into individual pages and saves them in the specified directory.

    :param pdf_path: Path to the input PDF file.
    :param output_dir: Directory where the pages will be saved.
    """
    # Open the PDF document
    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    document = fitz.open(pdf_path)
    # Loop through each page and save it as a separate PDF
    for page_num in range(document.page_count):
        output_file = output_dir / f"page_{page_num + 1}.pdf"
        with open(output_file, "wb") as f:
            pdf_writer = fitz.open()
            pdf_writer.insert_pdf(document, from_page=page_num, to_page=page_num)
            pdf_writer.save(f)
    document.close()


def process_pdf_page_as_image(page_path: str) -> str:
    """Converts a PDF page to an image, encodes it in Base64, and sends it to the Qwen2-VL-7B model.

    :param page_path: Path to the saved PDF page.
    :return: The image context returned by the Qwen2-VL-7B model.
    """
    # Open the PDF page
    document = fitz.open(page_path)
    page = document[0]
    pix = page.get_pixmap()  # Render the page as an image
    image_bytes = io.BytesIO(pix.tobytes("png"))  # Convert to PNG bytes
    document.close()

    # Encode the image in Base64 format
    encoded_image = base64.b64encode(image_bytes.getvalue()).decode("utf-8")

    # Log Base64 image size for memory tracking
    image_size_mb = len(encoded_image) / 1024 / 1024
    logger.debug(
        f"Base64 image size: {image_size_mb:.2f}MB for {pathlib.Path(page_path).name}"
    )

    # Send the Base64-encoded image to the model and retrieve the context
    image_context = qwen2_vl_7b_model_agent(encoded_image, image_type="Slides")

    # Clear the encoded image from memory
    del encoded_image

    return image_context


def sort_files_naturally(file_list):
    """Sorts a list of filenames in natural order (e.g., page_1, page_2, ..., page_10).

    :param file_list: List of filenames to sort.
    :return: Sorted list of filenames.
    """

    def extract_page_number(filename):
        # Extract the number from the filename using regex
        match = re.search(r"page_(\d+)\.pdf", filename)
        return int(match.group(1)) if match else 0

    return sorted(file_list, key=extract_page_number)


def pdf_read_handler_memory_optimized(
    path: str, batch_size: int = 10, max_workers: int = 3
) -> Iterator[dict[str, str | int]]:
    """Memory-optimized PDF processor that yields results in batches.

    :param path: Path to the PDF file.
    :param batch_size: Number of pages to process in each batch.
    :param max_workers: Maximum number of concurrent threads.
    :yield: Dictionary containing extracted data from each page.
    """
    # Create a unique temporary directory for page splitting (prevents race conditions with multiple workers)
    unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
    pdf_name = pathlib.Path(path).stem
    tmp_dir = pathlib.Path(__file__).parent.joinpath(
        f"tmp_batch_{pdf_name}_{unique_id}"
    )
    tmp_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(
        f"📁 Created unique tmp directory for batch processing: {tmp_dir.name}"
    )

    try:
        split_pdf_into_pages(pathlib.Path(path), tmp_dir)
        sorted_files = sort_files_naturally(os.listdir(tmp_dir))

        logger.info(f"Processing {len(sorted_files)} pages in batches of {batch_size}")

        # Process pages in batches to control memory usage
        for batch_start in range(0, len(sorted_files), batch_size):
            batch_end = min(batch_start + batch_size, len(sorted_files))
            batch_files = sorted_files[batch_start:batch_end]

            logger.debug(
                f"Processing batch {batch_start // batch_size + 1}: pages {batch_start + 1}-{batch_end}"
            )

            # Process current batch with ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit tasks for current batch
                future_to_page = {
                    executor.submit(
                        process_single_page, tmp_dir, page_file, page_num
                    ): page_num
                    for page_num, page_file in enumerate(
                        batch_files, start=batch_start + 1
                    )
                }

                # Collect results as they complete
                batch_results = []
                for future in as_completed(future_to_page):
                    page_num = future_to_page[future]
                    try:
                        # Add timeout to prevent hanging on stuck tasks
                        result = future.result(timeout=120)  # 2 minutes per page max
                        result["page"] = page_num
                        batch_results.append(result)
                    except TimeoutError:
                        logger.error(
                            f"Timeout processing page {page_num} (>120s) - skipping"
                        )
                        batch_results.append(
                            {
                                "page": page_num,
                                "type": "Slide",
                                "content": {"error": "Processing timeout (>120s)"},
                            }
                        )
                    except Exception as e:
                        logger.error(f"Error processing page {page_num}: {e}")
                        batch_results.append(
                            {
                                "page": page_num,
                                "type": "Slide",
                                "content": {"error": f"Processing failed: {e!s}"},
                            }
                        )

                # Sort batch results and yield them
                batch_results.sort(key=lambda x: x["page"])
                for result in batch_results:
                    yield result

                # Clear batch results to free memory
                del batch_results

            logger.debug(f"Completed batch {batch_start // batch_size + 1}")

    finally:
        # Cleanup the temporary directory
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
            logger.debug("Cleaned up temporary directory")


def process_single_page(
    tmp_dir: pathlib.Path, page_file: str, page_num: int
) -> dict[str, str | int]:
    """Process a single PDF page and return the result.

    :param tmp_dir: Temporary directory containing page files.
    :param page_file: Name of the page file to process.
    :param page_num: Page number for logging.
    :return: Dictionary containing extracted data from the page.
    """
    page_path = os.path.join(tmp_dir, page_file)

    try:
        # Log memory for first few pages to monitor per-page consumption
        if page_num <= 5:
            log_memory_usage(
                f"page_{page_num}_start", f"- Starting page {page_num} processing"
            )

        raw_data_from_model = process_pdf_page_as_image(page_path)

        if page_num <= 5:
            log_memory_usage(
                f"page_{page_num}_after_image", f"- Page {page_num} image processed"
            )

        final_content = parse_model_output(raw_data_from_model, page_num)

        if page_num <= 5:
            log_memory_usage(
                f"page_{page_num}_end", f"- Page {page_num} processing complete"
            )

        return {"type": "Slide", "content": final_content}

    except Exception as e:
        logger.error(f"Error processing page {page_num}: {e}")
        return {"type": "Slide", "content": {"error": f"Page processing failed: {e!s}"}}


def parse_model_output(raw_data_from_model, page_num: int) -> dict:
    """Parse model output into final content format.

    :param raw_data_from_model: Raw output from the model.
    :param page_num: Page number for logging.
    :return: Parsed content dictionary.
    """
    if isinstance(raw_data_from_model, dict):
        return raw_data_from_model
    elif isinstance(raw_data_from_model, str):
        # logger.debug(f"Raw string from model for page {page_num}: '{raw_data_from_model}'")

        text_to_process = raw_data_from_model.strip()

        # Remove markdown fences if present
        if text_to_process.startswith("```json"):
            text_to_process = text_to_process[len("```json") :]
            if text_to_process.endswith("```"):
                text_to_process = text_to_process[: -len("```")]
        elif text_to_process.startswith("```"):
            text_to_process = text_to_process[len("```") :]
            if text_to_process.endswith("```"):
                text_to_process = text_to_process[: -len("```")]

        text_to_process = text_to_process.strip()
        if not text_to_process:
            logger.warning(
                f"Empty string after stripping fences for page {page_num}. Original raw: '{raw_data_from_model}'"
            )
            return {"error": "Empty content from model after stripping fences"}

        try:
            # Attempt 1: Parse directly
            return json.loads(text_to_process)
        except json.JSONDecodeError as e_direct:
            logger.warning(
                f"Direct json.loads failed for page {page_num}: {e_direct}. Attempting to extract JSON with raw_decode."
            )

            # Attempt 1b: sanitize common glitches and try again quickly
            sanitized = _sanitize_json_like(text_to_process)
            if sanitized != text_to_process:
                try:
                    return json.loads(sanitized)
                except json.JSONDecodeError:
                    pass

            # Attempt 2: Find first '{' or '[' and use raw_decode
            idx_brace = text_to_process.find("{")
            idx_bracket = text_to_process.find("[")
            start_idx = -1

            if idx_brace != -1 and (idx_bracket == -1 or idx_brace < idx_bracket):
                start_idx = idx_brace
            elif idx_bracket != -1:
                start_idx = idx_bracket

            if start_idx != -1:
                json_candidate_str = text_to_process[start_idx:]
                try:
                    decoder = json.JSONDecoder()
                    obj, end_pos = decoder.raw_decode(json_candidate_str)
                    return obj
                except json.JSONDecodeError as e_raw:
                    logger.warning(
                        f"JSONDecodeError with raw_decode for page {page_num}: {e_raw}. Attempting LLM fix..."
                    )

                    # Attempt 3: Ask LLM to fix the JSON
                    fixed_json_str = _fix_json_with_llm(json_candidate_str, str(e_raw))
                    if fixed_json_str:
                        try:
                            return json.loads(fixed_json_str)
                        except json.JSONDecodeError:
                            pass

                    logger.error(
                        f"All JSON parsing attempts failed for page {page_num}. Original error: {e_direct}"
                    )
                    return {
                        "error": "Failed to parse model output as JSON after multiple attempts including LLM fix",
                        "details_direct_parse": str(e_direct),
                        "details_substring_parse": str(e_raw),
                        "original_string_after_markdown_strip": text_to_process,
                    }
            else:
                # No '{' or '[' found to attempt raw_decode
                logger.error(
                    f"No JSON start character ('{{' or '[') found after markdown stripping for page {page_num}. Original direct error: {e_direct}. String: '{text_to_process}'"
                )
                return {
                    "error": "No JSON start character found in model output",
                    "details": str(e_direct),
                    "original_string_after_markdown_strip": text_to_process,
                }
    else:
        logger.warning(
            f"Unexpected data type from model for page {page_num}: "
            f"{type(raw_data_from_model)}. Value: {raw_data_from_model!r}"
        )
        return {
            "error": "Unexpected data type from model",
            "type": str(type(raw_data_from_model)),
        }


def log_memory_usage(stage: str, additional_info: str = "") -> None:
    """Log current memory usage with process details.

    :param stage: Stage description (e.g., "start", "after_splitting", "processing", "end")
    :param additional_info: Additional context information
    """
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()

        # Convert bytes to MB for readability
        rss_mb = memory_info.rss / 1024 / 1024
        vms_mb = memory_info.vms / 1024 / 1024

        logger.info(
            f"[MEMORY {stage.upper()}] RSS: {rss_mb:.1f}MB, VMS: {vms_mb:.1f}MB, "
            f"Percent: {memory_percent:.1f}% {additional_info}"
        )
    except Exception as e:
        logger.warning(f"Failed to log memory usage at {stage}: {e}")


def pdf_read_handler(path: str, max_workers: int = 3) -> list[dict[str, str | int]]:
    """Optimized PDF processor that returns full results but uses controlled concurrency.

    Fixes memory issues by using ThreadPoolExecutor instead of creating hundreds of threads.
    Returns full result list for compatibility with document_service.

    :param path: Path to the PDF file.
    :param max_workers: Maximum number of concurrent threads (default: 3).
    :return: A list of dictionaries containing extracted data from each page.
    """
    start_time = time.time()
    log_memory_usage("start", f"- Starting PDF processing: {pathlib.Path(path).name}")
    logger.info(f"⏱️ PDF processing started at {time.strftime('%H:%M:%S')}")

    # Create a unique temporary directory for page splitting (prevents race conditions with multiple workers)
    unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
    pdf_name = pathlib.Path(path).stem
    tmp_dir = pathlib.Path(__file__).parent.joinpath(f"tmp_{pdf_name}_{unique_id}")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"📁 Created unique tmp directory: {tmp_dir.name}")

    try:
        split_pdf_into_pages(pathlib.Path(path), tmp_dir)
        split_time = time.time()
        logger.info(f"⏱️ PDF split completed in {split_time - start_time:.2f}s")

        sorted_files = sort_files_naturally(os.listdir(tmp_dir))

        log_memory_usage("after_splitting", f"- Split into {len(sorted_files)} pages")
        logger.info(f"Processing {len(sorted_files)} pages with {max_workers} workers")

        # Warn if too many pages might cause RabbitMQ timeout
        if len(sorted_files) > 50:
            estimated_time = len(sorted_files) * 2  # Rough estimate: 2s per page
            logger.warning(
                f"⚠️ Large PDF ({len(sorted_files)} pages) - estimated processing time: {estimated_time}s - may cause RabbitMQ timeout!"
            )

        results = []
        processed_count = 0

        # Use ThreadPoolExecutor instead of creating hundreds of threads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            log_memory_usage(
                "executor_start",
                f"- ThreadPoolExecutor started with {max_workers} workers",
            )

            # Submit all tasks
            future_to_page = {
                executor.submit(
                    process_single_page, tmp_dir, page_file, page_num
                ): page_num
                for page_num, page_file in enumerate(sorted_files, start=1)
            }

            task_submission_time = time.time()
            logger.info(
                f"⏱️ Task submission completed in {task_submission_time - split_time:.2f}s"
            )
            log_memory_usage(
                "tasks_submitted", f"- {len(future_to_page)} tasks submitted"
            )

            # Collect results as they complete
            processing_start_time = time.time()
            for future in as_completed(future_to_page):
                page_num = future_to_page[future]
                try:
                    # Add timeout to prevent hanging on stuck tasks (e.g., API timeouts)
                    result = future.result(timeout=120)  # 2 minutes per page max
                    result["page"] = page_num
                    results.append(result)
                    processed_count += 1

                    # Log timing and memory every 10 pages or at key milestones
                    if processed_count % 10 == 0 or processed_count in [5, 15, 25]:
                        elapsed_time = time.time() - processing_start_time
                        avg_time_per_page = elapsed_time / processed_count
                        remaining_pages = len(sorted_files) - processed_count
                        estimated_remaining_time = remaining_pages * avg_time_per_page

                        logger.info(
                            f"⏱️ Progress: {processed_count}/{len(sorted_files)} pages ({elapsed_time:.1f}s elapsed, ~{estimated_remaining_time:.1f}s remaining)"
                        )

                        # Warn if processing is taking too long (potential RabbitMQ timeout)
                        if elapsed_time > 120:  # 2 minutes
                            logger.warning(
                                f"⚠️ PDF processing taking long ({elapsed_time:.1f}s) - RabbitMQ timeout risk!"
                            )

                        log_memory_usage(
                            "processing",
                            f"- Completed {processed_count}/{len(sorted_files)} pages, results in memory: {len(results)}",
                        )

                except TimeoutError:
                    logger.error(
                        f"Timeout processing page {page_num} (>120s) - skipping"
                    )
                    results.append(
                        {
                            "page": page_num,
                            "type": "Slide",
                            "content": {"error": "Processing timeout (>120s)"},
                        }
                    )
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Error processing page {page_num}: {e}")
                    results.append(
                        {
                            "page": page_num,
                            "type": "Slide",
                            "content": {"error": f"Processing failed: {e!s}"},
                        }
                    )
                    processed_count += 1

        # Sort results by page number before returning
        sorting_start_time = time.time()
        log_memory_usage("before_sorting", f"- About to sort {len(results)} results")
        results.sort(key=lambda x: x["page"])

        end_time = time.time()
        total_time = end_time - start_time
        processing_time = end_time - processing_start_time
        sorting_time = end_time - sorting_start_time

        log_memory_usage(
            "end", f"- Processing complete: {len(results)} pages processed"
        )
        logger.info("⏱️ PDF processing completed:")
        logger.info(f"   📄 Total time: {total_time:.2f}s for {len(results)} pages")
        logger.info(
            f"   🔄 Processing time: {processing_time:.2f}s (avg: {processing_time / len(results):.2f}s/page)"
        )
        logger.info(f"   🔀 Sorting time: {sorting_time:.2f}s")

        # Final warning if total time exceeded reasonable RabbitMQ limits
        if total_time > 300:  # 5 minutes
            logger.error(
                f"🚨 PDF processing took {total_time:.1f}s - VERY HIGH risk of RabbitMQ timeout!"
            )
        elif total_time > 180:  # 3 minutes
            logger.warning(
                f"⚠️ PDF processing took {total_time:.1f}s - HIGH risk of RabbitMQ timeout!"
            )
        elif total_time > 120:  # 2 minutes
            logger.warning(
                f"⚠️ PDF processing took {total_time:.1f}s - moderate RabbitMQ timeout risk"
            )

        return results

    finally:
        # Cleanup the temporary directory
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
            log_memory_usage("cleanup", "- Temporary directory cleaned up")
            logger.debug("Cleaned up temporary directory")


# Legacy implementation (kept for reference - DO NOT USE for large files)
def pdf_read_handler_legacy(path: str) -> list[dict[str, str | int]]:
    """LEGACY: Original implementation with SEVERE memory issues for large files.

    ⚠️  WARNING: This creates one thread per page (300+ threads for large PDFs)!
    ⚠️  Use pdf_read_handler() instead which uses ThreadPoolExecutor.

    This function is kept for reference but should NEVER be used.
    """
    logger.error(
        "DEPRECATED: pdf_read_handler_legacy() creates thread explosion! Use pdf_read_handler() instead."
    )

    # Create a unique temporary directory for page splitting (prevents race conditions with multiple workers)
    unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
    pdf_name = pathlib.Path(path).stem
    tmp_dir = pathlib.Path(__file__).parent.joinpath(
        f"tmp_legacy_{pdf_name}_{unique_id}"
    )
    tmp_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(
        f"📁 Created unique tmp directory for legacy processing: {tmp_dir.name}"
    )

    split_pdf_into_pages(pathlib.Path(path), tmp_dir)

    result = []
    threads = []
    lock = threading.Lock()
    semaphore = threading.Semaphore(5)  # Only 5 concurrent, but 300+ threads created!

    def process_page(page: int, page_file: str):
        with semaphore:
            page_path = os.path.join(tmp_dir, page_file)
            raw_data_from_model = process_pdf_page_as_image(page_path)
            final_content = parse_model_output(raw_data_from_model, page)

            with lock:
                result.append({"page": page, "type": "Slide", "content": final_content})

    # ⚠️ PROBLEM: Creates ALL threads at once (300+ for large PDFs)
    sorted_files = sort_files_naturally(os.listdir(tmp_dir))
    for page, page_file in enumerate(sorted_files, start=1):
        thread = threading.Thread(target=process_page, args=(page, page_file))
        threads.append(thread)  # ⚠️ ALL threads in memory!
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Cleanup the temporary directory after processing
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)

    # Sort results by page number before returning
    result.sort(key=lambda x: x["page"])
    return result
