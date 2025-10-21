import base64
import hashlib
import json
import os
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, Literal, TypeVar

import requests
import vertexai
import google.auth
from dotenv import load_dotenv
from google.oauth2 import service_account
from loguru import logger
from requests.models import Response
from vertexai.generative_models import GenerativeModel, Image, Part


T = TypeVar("T", bound=Callable[..., Any])


load_dotenv()


def retry_on_exception(
    max_retries: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 10.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[T], T]:
    """Decorator that retries a function when specified exceptions occur.

    Args:
        max_retries: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds
        max_wait: Maximum wait time in seconds
        exceptions: Tuple of exceptions to catch and retry on
    """

    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break

                    wait_time = min(
                        initial_wait * (2**attempt)
                        + (0.1 * attempt),  # expo backoff with jitter
                        max_wait,
                    )
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed with error: {e!s}. "
                        f"Retrying in {wait_time:.2f} seconds..."
                    )
                    time.sleep(wait_time)

            # If we get here, all retries failed
            logger.error(
                f"All {max_retries} attempts failed. Last error: {last_exception!s}"
            )
            raise last_exception  # type: ignore

        return wrapper  # type: ignore

    return decorator


# Content type constants
CONTENT_TYPES = (
    "Charts",
    "Diagrams",
    "Flowcharts",
    "Tables",
    "Text Documents",
    "Other",
)

# Prompt constants
AGENT_PROMPT: str = (
    "Identify what is shown in the image and categorize it into one of these categories: {}. "
    "Answer options: [Charts, Diagrams, Flowcharts, Tables, Text Documents, Slides, Other]"
    "In your response, write only the category name"
).format(", ".join(CONTENT_TYPES))

CONTENT_PROMPTS: dict[str, str] = {
    "Charts": (
        "Extract and structure the chart information in JSON format. Include: "
        "1. chartType - identify the type of chart (line, bar, scatter, etc.) "
        "2. axes - detail both x and y axes with names, units, scales, and range "
        "3. dataPoints - list all visible data points with their exact values "
        "4. trends - identify key patterns, correlations, extremes, or anomalies "
        "5. legend - all items from the legend with their descriptions "
        "6. additionalText - any titles, footnotes, or annotations on the chart "
        "Be precise, concise, and avoid subjective interpretations. Format response as a JSON object."
    ),
    "Diagrams": (
        "Extract and structure all diagram information in JSON format. Include: "
        "1. diagramType - identify the specific type of diagram "
        "2. elements - list all components with their labels, values, and relative sizes "
        "3. relationships - describe all connections between elements "
        "4. colorCoding - explain any color significance "
        "5. metrics - extract all numerical data with proper context "
        "6. labelText - capture all text labels exactly as shown "
        "Be precise, concise, and avoid subjective interpretations. Format response as a JSON object."
    ),
    "Flowcharts": (
        "Extract and structure the flowchart information in JSON format. Include: "
        "1. nodes - list all blocks with their exact labels and functions "
        "2. connections - detail all arrows with their directions and any annotations "
        "3. decisionPoints - identify all branch points and their conditions "
        "4. startEnd - clearly mark starting and ending points "
        "5. processFlow - describe the complete sequence of steps "
        "6. annotations - capture any additional text or notes "
        "Be precise, concise, and avoid subjective interpretations. Format response as a JSON object."
    ),
    "Tables": (
        "Extract and structure the table information in JSON format with: "
        "1. headers - list all column and row headers exactly as shown "
        "2. data - capture all cell values preserving their exact format (text, numbers) "
        "3. relationships - identify any data relationships or patterns "
        "4. footnotes - include any table notes or references "
        "5. title - capture any table title or caption "
        "Format the table data as a proper JSON array with named fields for each column. "
        "Be precise, concise, and avoid subjective interpretations."
    ),
    "Text Documents": (
        "Extract all text content from the image and structure it in JSON format with: "
        "1. title - document title or heading if present "
        "2. sections - organize content by logical sections "
        "3. paragraphs - preserve paragraph structure "
        "4. formatting - note any emphasized text, bullet points, or numbered lists "
        "5. metadata - capture dates, page numbers, or other metadata "
        "Transcribe all text exactly as shown without adding interpretations. "
        "Format response as a JSON object."
    ),
    "Slides": (
        "Extract and structure all slide content in JSON format with the following keys: "
        '"title": extract the main slide title, '
        '"content": all body text preserving bullet points and hierarchical structure, '
        '"tables": format any tables as nested JSON arrays with column headers, '
        '"charts": describe any charts with type, data points, and trends, '
        '"images": brief descriptions of any non-chart images, '
        '"notes": any presenter notes or footnotes. '
        "Be extremely precise and concise. Avoid any commentary or subjective interpretation. "
        "Format response as a clean JSON object without line breaks or extra formatting."
    ),
    "Other": (
        "Extract and structure the image content in JSON format with: "
        '"type": identify the primary content type, '
        '"textElements": list all visible text elements exactly as shown, '
        '"visualElements": describe key visual components concisely, '
        '"data": extract any numerical data or measurements, '
        '"relationships": identify any clear relationships between elements. '
        "Be precise, concise, and avoid subjective interpretations. "
        "Format response as a clean JSON object without fluff or commentary."
    ),
}

DEFAULT_PROMPT: str = (
    "Extract and structure all content from the image in JSON format with the following structure: "
    '{"type": identify the main content type (chart, table, text, etc.), '
    '"title": extract any prominent title or heading, '
    '"textContent": transcribe all visible text maintaining structure, '
    '"dataElements": identify and extract any data points, measurements, or values, '
    '"visualElements": list key visual components objectively, '
    '"relationships": note any patterns, trends, or logical connections, '
    '"metadata": capture any dates, references, or attributions}. '
    "Be extremely precise and concise. Omit subjective interpretations, commentary, or explanations. "
    "If the image contains tables or structured data, format as nested JSON arrays. "
    "For charts, include exact values where legible. Response must be valid JSON."
)

# Cache configuration
CACHE_FILE = Path("image_cache.json")

# Type aliases
T = TypeVar("T")


# Interface definitions
class ImageCacheService(ABC):
    """Interface for image caching operations."""

    @abstractmethod
    def get(self, image_hash: str) -> str | None:
        """Get cached result for an image hash."""
        ...

    @abstractmethod
    def set(self, image_hash: str, content: str) -> None:
        """Cache result for an image hash."""
        ...

    @abstractmethod
    def get_hash(self, image_bytes: bytes) -> str:
        """Generate hash for image bytes."""
        ...


class ImageAnalysisService(ABC):
    """Interface for image analysis operations."""

    @abstractmethod
    def analyze_image(
        self, encoded_image: str, prompt: str = DEFAULT_PROMPT, **kwargs
    ) -> str:
        """Analyze image content based on the provided prompt."""
        pass

    @abstractmethod
    def analyze_image_type(self, encoded_image: str) -> str:
        """Determine the type of content in the image."""
        pass

    @abstractmethod
    def analyze_with_agent(
        self,
        encoded_image: str,
        image_type: Literal["Slides", "Other"] | None = None,
    ) -> str:
        """Use an agent approach to first identify image type then analyze accordingly."""
        pass

    @staticmethod
    def generate_specific_prompt(image_type: str) -> str:
        return CONTENT_PROMPTS.get(image_type, DEFAULT_PROMPT)

    @abstractmethod
    def call_text_only(self, prompt: str) -> str:
        """Call the service with a text-only prompt."""
        pass


# Implementation classes
class FileBasedImageCache:
    """File-based implementation of image caching service."""

    def __init__(self, cache_file: Path = CACHE_FILE):
        self.cache_file = cache_file
        self._cache = self._load_cache()

    def _load_cache(self) -> dict[str, str]:
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text())
            except Exception as e:
                logger.error(f"Failed to load cache: {e}")
        return {}

    def _save_cache(self) -> None:
        try:
            self.cache_file.write_text(
                json.dumps(self._cache, indent=4), encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def get_hash(self, image_bytes: bytes) -> str:
        return hashlib.md5(image_bytes).hexdigest()

    def get(self, image_hash: str) -> str | None:
        return self._cache.get(image_hash)

    def set(self, image_hash: str, content: str) -> None:
        self._cache[image_hash] = content
        self._save_cache()


class GeminiImageAnalysisService(ImageAnalysisService):
    """Implementation using Google's Gemini model for image analysis.

    This class follows the Singleton pattern to ensure only one instance exists.
    """

    _instance = None
    _initialized = False

    def __new__(cls, cache_service: ImageCacheService = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, cache_service: ImageCacheService = None):
        if not self._initialized:
            self.cache_service = cache_service or FileBasedImageCache()

            # Initialize Vertex AI with various auth options
            project_env = (
                os.environ.get("VERTEXAI_PROJECT")
                or os.environ.get("VERTEX_PROJECT")
                or os.environ.get("GOOGLE_CLOUD_PROJECT")
            )
            location_env = (
                os.environ.get("VERTEXAI_LOCATION")
                or os.environ.get("GOOGLE_CLOUD_REGION")
                or "us-central1"
            )

            credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
            credentials_path = os.environ.get("RAGOPS_VERTEX_CREDENTIALS")

            try:
                if credentials_json:
                    # Service account via JSON string
                    credentials_info = json.loads(credentials_json)
                    credentials = service_account.Credentials.from_service_account_info(
                        credentials_info
                    )
                    vertexai.init(
                        project=project_env or "",
                        location=location_env,
                        credentials=credentials,
                    )
                    logger.info(
                        "Initialized Vertex AI with service account from GOOGLE_CREDENTIALS_JSON"
                    )
                elif credentials_path and Path(credentials_path).exists():
                    # Service account via file path
                    credentials = service_account.Credentials.from_service_account_file(
                        credentials_path
                    )
                    vertexai.init(
                        project=project_env or "",
                        location=location_env,
                        credentials=credentials,
                    )
                    logger.info(
                        "Initialized Vertex AI with service account from GOOGLE_APPLICATION_CREDENTIALS"
                    )
                else:
                    # Try Application Default Credentials (ADC)
                    creds, project_adc = google.auth.default()
                    project_final = project_env or project_adc or ""
                    if not project_final:
                        logger.warning(
                            "Vertex project not set; set VERTEXAI_PROJECT or GOOGLE_CLOUD_PROJECT for best results"
                        )
                    vertexai.init(
                        project=project_final, location=location_env, credentials=creds
                    )
                    logger.info(
                        "Initialized Vertex AI with Application Default Credentials"
                    )
            except Exception as e:
                logger.warning(f"Vertex AI init failed: {e!s}")

            self._initialized = True

    @retry_on_exception(
        max_retries=3,
        initial_wait=1.0,
        max_wait=10.0,
        exceptions=(
            Exception,  # Catch all exceptions by default
        ),
    )
    def _call_gemini_api(self, encoded_image: str, prompt: str) -> str:
        """Make the actual API call to Gemini with retry logic."""
        model = GenerativeModel("gemini-2.5-flash")
        image = Image.from_bytes(base64.b64decode(encoded_image))
        parts = [Part.from_image(image), Part.from_text(prompt)]
        response = model.generate_content(parts)
        return response.text

    def call_text_only(self, prompt: str) -> str:
        """Make a text-only API call to Gemini (no image).

        Args:
            prompt: Text prompt to send to the model

        Returns:
            str: Model's text response
        """
        model = GenerativeModel("gemini-2.5-flash")
        parts = [Part.from_text(prompt)]
        response = model.generate_content(parts)
        logger.info(
            f"Successfully received text response from Gemini API: {response.text}"
        )
        return response.text

    def analyze_image(
        self, encoded_image: str, prompt: str = DEFAULT_PROMPT, **kwargs
    ) -> str:
        """Analyze image using Gemini model with retry logic.

        Args:
            encoded_image: Base64 encoded image string
            prompt: Prompt to use for analysis
            **kwargs: Additional arguments (not used, kept for compatibility)

        Returns:
            str: Analysis result from Gemini

        Raises:
            Exception: If all retry attempts fail or if there's an error with the API call
        """
        # Check cache first
        if self.cache_service:
            image_hash = self.cache_service.get_hash(encoded_image.encode())
            cached_result = self.cache_service.get(image_hash)
            if cached_result and cached_result not in CONTENT_TYPES:
                logger.info("Using cached image analysis result")
                return cached_result

        try:
            response_text = self._call_gemini_api(encoded_image, prompt)
            logger.info("Successfully received response from Gemini API")

            # Cache the result
            if self.cache_service:
                image_hash = self.cache_service.get_hash(encoded_image.encode())
                self.cache_service.set(image_hash, response_text)

            return response_text

        except Exception as e:
            logger.error(f"Failed to analyze image after retries: {e!s}")
            return "Error: Failed to analyze image"

    def analyze_image_type(self, encoded_image: str) -> str:
        """Determine the type of content in the image using Gemini."""
        return self.analyze_image(encoded_image, AGENT_PROMPT)

    def analyze_with_agent(
        self,
        encoded_image: str,
        image_type: Literal["Slides", "Other"] = "Other",
    ) -> str:
        """Use a two-step approach: first identify image type then analyze accordingly."""
        # uncomment image type detection if needed (need more llm calls)
        # if not image_type:
        #     image_type = self.analyze_image_type(encoded_image)
        #     logger.info(f"Detected image type: {image_type}")

        specific_prompt = self.generate_specific_prompt(image_type)
        return self.analyze_image(encoded_image, specific_prompt)


class OpenAIImageAnalysisService(ImageAnalysisService):
    """Implementation using OpenAI Vision models (gpt-4o family) via REST."""

    def __init__(
        self,
        cache_service: ImageCacheService | None = None,
        *,
        model: str | None = None,
    ):
        self.cache_service = cache_service or FileBasedImageCache()
        # Allow overriding the model via env; default to a fast, cheap model
        self.model = model or os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")
        self.api_key = os.getenv("OPENAI_API_KEY")
        # Allow custom base URL for OpenAI-compatible APIs (e.g., proxies)
        self.base_url = os.getenv(
            "OPENAI_BASE_URL", "https://api.openai.com/v1"
        ).rstrip("/")
        # Optional organization header
        self.org = os.getenv("OPENAI_ORG")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set; OpenAI service may not work")

    def _post_chat_completion(self, prompt: str, encoded_image: str) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.org:
            headers["OpenAI-Organization"] = self.org
        data = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}"
                            },
                        },
                    ],
                }
            ],
        }
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        j = resp.json()
        return j["choices"][0]["message"]["content"].strip()

    def analyze_image(
        self, encoded_image: str, prompt: str = DEFAULT_PROMPT, **kwargs
    ) -> str:
        # Cache first
        if self.cache_service:
            image_hash = self.cache_service.get_hash(encoded_image.encode())
            cached_result = self.cache_service.get(image_hash)
            if cached_result and cached_result not in CONTENT_TYPES:
                logger.info("Using cached image analysis result (OpenAI)")
                return cached_result

        try:
            content = self._post_chat_completion(prompt, encoded_image)
            if self.cache_service:
                image_hash = self.cache_service.get_hash(encoded_image.encode())
                self.cache_service.set(image_hash, content)
            return content
        except Exception as e:
            logger.error(f"OpenAI analyze_image failed: {e!s}")
            return "Error: Failed to analyze image"

    def call_text_only(self, prompt: str) -> str:
        """Make a text-only API call to OpenAI (no image).

        Args:
            prompt: Text prompt to send to the model

        Returns:
            str: Model's text response
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.org:
            headers["OpenAI-Organization"] = self.org
        data = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [{"role": "user", "content": prompt}],
        }
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        j = resp.json()
        return j["choices"][0]["message"]["content"].strip()

    def analyze_image_type(self, encoded_image: str) -> str:
        return self.analyze_image(encoded_image, AGENT_PROMPT)

    def analyze_with_agent(
        self,
        encoded_image: str,
        image_type: Literal["Slides", "Other"] = "Other",
    ) -> str:
        specific_prompt = self.generate_specific_prompt(image_type)
        return self.analyze_image(encoded_image, specific_prompt)


class QwenImageAnalysisService(ImageAnalysisService):
    """Implementation using Qwen2-VL-7B model for image analysis."""

    def __init__(
        self,
        model_url: str = os.getenv("QWEN2_VL_7B_MODEL_URL"),
        cache_service: ImageCacheService = None,
    ):
        self.model_url = model_url
        self.cache_service = cache_service or FileBasedImageCache()

    def analyze_image(
        self, encoded_image: str, prompt: str = DEFAULT_PROMPT, **kwargs
    ) -> str:
        """Analyze image using Qwen model."""
        temperature = kwargs.get("temperature", 0.3)

        # Check cache first
        if self.cache_service:
            image_hash = self.cache_service.get_hash(encoded_image.encode())
            cached_result = self.cache_service.get(image_hash)
            if cached_result and cached_result not in CONTENT_TYPES:
                logger.info("Using cached image analysis result")
                return cached_result

        request_payload: dict[str, Any] = {
            "image": encoded_image,
            "message": prompt,
            "temperature": temperature,
            "top_p": 0.9,
        }

        response: Response = requests.post(self.model_url, json=request_payload)

        try:
            content = response.json()["content"][0]

            # Cache the result
            if self.cache_service:
                image_hash = self.cache_service.get_hash(encoded_image.encode())
                self.cache_service.set(image_hash, content)

            return content
        except Exception as ex:
            logger.error(f"ERROR {ex} on image {response.json()}")
            return "<BROKEN IMAGE>"

    def call_text_only(self, prompt: str) -> str:
        """Make a text-only API call to Qwen (no image).

        Note: This may not be supported by all Qwen deployments.

        Args:
            prompt: Text prompt to send to the model

        Returns:
            str: Model's text response

        Raises:
            NotImplementedError: If the Qwen endpoint doesn't support text-only requests
        """
        # Try to send text-only request - some Qwen deployments might not support this
        request_payload: dict[str, Any] = {
            "message": prompt,
            "temperature": 0.2,
            "top_p": 0.9,
        }

        try:
            response: Response = requests.post(
                self.model_url, json=request_payload, timeout=30
            )
            response.raise_for_status()
            return response.json()["content"][0]
        except Exception as e:
            logger.warning(f"Qwen text-only call failed: {e}")
            raise NotImplementedError("Qwen service may not support text-only requests")

    def analyze_image_type(self, encoded_image: str) -> str:
        """Determine the type of content in the image using Qwen."""
        return self.analyze_image(encoded_image, AGENT_PROMPT)

    def analyze_with_agent(
        self,
        encoded_image: str,
        image_type: Literal["Slides", "Other"] = "Other",
    ) -> str:
        """Use a two-step approach: first identify image type then analyze accordingly."""
        # if not image_type:
        #     image_type = self.analyze_image_type(encoded_image)
        #     logger.info(f"Detected image type: {image_type}")

        specific_prompt = self.generate_specific_prompt(image_type)
        return self.analyze_image(encoded_image, specific_prompt)


class ImageAnalysisFactory:
    """Factory for creating appropriate image analysis service instances."""

    @staticmethod
    def create_service(
        cache_service: ImageCacheService | None = None,
    ) -> ImageAnalysisService:
        """Create an appropriate image analysis service based on available credentials."""
        if cache_service is None:
            cache_service = FileBasedImageCache()

        # Detect Vertex availability via multiple signals
        if any(
            [
                os.environ.get("GOOGLE_CREDENTIALS_JSON"),
                os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
                os.environ.get("VERTEXAI_PROJECT"),
                os.environ.get("VERTEX_PROJECT"),
                os.environ.get("GOOGLE_CLOUD_PROJECT"),
                os.environ.get("RAGOPS_VERTEX_CREDENTIALS"),
            ]
        ):
            logger.info("Using Vertex AI Gemini service")
            return GeminiImageAnalysisService(cache_service=cache_service)

        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            logger.info("Using OpenAI Vision service")
            return OpenAIImageAnalysisService(cache_service=cache_service)

        logger.info("Using Qwen2-VL-7B model service")
        return QwenImageAnalysisService(cache_service=cache_service)


# Factory function to get the appropriate implementation
def get_image_analysis_service(
    cache_service: ImageCacheService | None = None,
) -> ImageAnalysisService:
    """Get the appropriate image analysis service implementation."""
    return ImageAnalysisFactory.create_service(cache_service)


# Backward compatibility functions
def analyze_image_type(encoded_image: str) -> str:
    """Analyzes the image to determine its type (e.g., chart, flowchart, table, diagram, or scanned document).

    :param encoded_image: The base64-encoded image string.
    :return: The type of data found in the image.
    """
    service = get_image_analysis_service()
    return service.analyze_image_type(encoded_image)


def generate_specific_prompt(image_type: str) -> str:
    """Generates a specific prompt based on the type of image.

    :param image_type: The type of data found in the image.
    :return: The generated specific prompt for the image type.
    """
    service = get_image_analysis_service()
    return service.generate_specific_prompt(image_type)


def qwen2_vl_7b_model_agent(
    encoded_image: str, image_type: Literal["Slides", "Other"] | None = None
) -> str:
    """The agent first identifies the type of data in the image and then sends a specific prompt for further analysis.

    :param encoded_image: The base64-encoded image string.
    :param image_type: Input image type.
    :return: The final detailed analysis based on the image type.
    """
    service = get_image_analysis_service()
    return service.analyze_with_agent(encoded_image, image_type)
