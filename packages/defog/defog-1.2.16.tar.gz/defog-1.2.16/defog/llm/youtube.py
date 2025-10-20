# converts a youtube video to a detailed, ideally diarized transcript
from defog.llm.utils_logging import (
    ToolProgressTracker,
    SubTaskLogger,
    NoOpToolProgressTracker,
    NoOpSubTaskLogger,
)
from defog import config
from urllib.parse import urlparse


async def get_youtube_summary(
    video_url: str,
    model: str = "gemini-2.5-pro",
    verbose: bool = True,
    system_instructions: list[str] = [
        "Please provide a detailed, accurate transcript of the video. Please include timestamps in the format HH:MM:SS and names (if available) for each speaker. Do not describe what you *see* in the video, just create a great transcript based on what you *hear*.",
        "You should skip umms, ahhs, small talk, and other filler words.",
        "If you find yourself repeating the same words, you should stop.",
    ],
    task_description: str = "Please provide a detailed, accurate transcript of the video.",
) -> str:
    """
    Get a detailed, diarized transcript of a YouTube video using streaming generation.

    Transcripts are generated in real-time and optionally displayed to console as they're created.
    Uses optimized settings for audio-only processing with efficient FPS and deterministic output.

    Args:
        video_url: The URL of the YouTube video. Must be a valid YouTube URL.
        model: The Gemini model to use (default: "gemini-2.5-pro").
        verbose: Whether to display real-time transcript streaming and progress (default: True).
        system_instructions: List of system instructions for the AI model. Controls the style and format of output.
        task_description: Specific task description sent to the AI model. Defines what the model should produce.

    Returns:
        A detailed, ideally diarized transcript of the video. May be empty if
        transcription fails or video has no audio.

    Raises:
        ValueError: If GEMINI_API_KEY environment variable is not set or URL is invalid.

    Example:
        >>> transcript = await get_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        >>> print(f"Transcript length: {len(transcript)} characters")
    """
    tracker_class = ToolProgressTracker if verbose else NoOpToolProgressTracker
    logger_class = SubTaskLogger if verbose else NoOpSubTaskLogger

    async with tracker_class(
        "YouTube Transcript",
        f"Transcribing video from: {video_url[:50]}{'...' if len(video_url) > 50 else ''}",
    ) as tracker:
        subtask_logger = logger_class()
        subtask_logger.log_provider_info("Gemini", model)

        if config.get("GEMINI_API_KEY") is None:
            raise ValueError("GEMINI_API_KEY is not set")

        # Validate YouTube URL
        if not _is_valid_youtube_url(video_url):
            raise ValueError(f"Invalid YouTube URL: {video_url}")

        from google import genai
        from google.genai.types import (
            Content,
            Part,
            FileData,
            VideoMetadata,
            GenerateContentConfig,
        )

        client = genai.Client(api_key=config.get("GEMINI_API_KEY"))

        tracker.update(10, "Processing. Takes ~1s for every ~10s of video")
        subtask_logger.log_subtask(
            "Using low FPS (0.01) for efficient audio processing", "info"
        )

        if verbose:
            print("\n🎥 Streaming summary as it's generated:\n")
            print("=" * 60)

        transcript_chunks = []

        async for chunk in await client.aio.models.generate_content_stream(
            model=model,
            contents=Content(
                parts=[
                    Part(
                        file_data=FileData(file_uri=video_url),
                        video_metadata=VideoMetadata(fps=0.01),
                    ),
                    Part(text=task_description),
                ]
            ),
            config=GenerateContentConfig(
                system_instruction=system_instructions,
                temperature=0.1,
            ),
        ):
            try:
                if chunk and chunk.text:
                    if verbose:
                        print(chunk.text, end="", flush=True)
                    transcript_chunks.append(chunk.text)
            except Exception as e:
                subtask_logger.log_subtask(
                    f"Error processing chunk: {str(e)}", "warning"
                )
                continue

        if verbose:
            print("\n" + "=" * 60)
            print("✅ Transcript complete!\n")

        full_transcript = "".join(transcript_chunks)

        if not full_transcript.strip():
            subtask_logger.log_subtask(
                "Warning: Generated transcript is empty", "warning"
            )

        tracker.update(90, "Finalizing transcript")
        transcript_length = len(full_transcript)

        subtask_logger.log_result_summary(
            "YouTube Transcript",
            {
                "transcript_length": f"{transcript_length} characters",
                "model_used": model,
            },
        )

        return full_transcript


def _is_valid_youtube_url(url: str) -> bool:
    """
    Validate if the provided URL is a valid YouTube URL.

    Args:
        url: The URL to validate.

    Returns:
        True if the URL is a valid YouTube URL, False otherwise.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return False

        # Check for various YouTube URL formats
        youtube_domains = [
            "youtube.com",
            "www.youtube.com",
            "youtu.be",
            "m.youtube.com",
        ]

        if parsed.netloc in youtube_domains:
            if parsed.netloc == "youtu.be":
                # youtu.be/VIDEO_ID format
                return bool(parsed.path and len(parsed.path) > 1)
            else:
                # youtube.com/watch?v=VIDEO_ID format
                return (
                    "watch" in parsed.path
                    or "embed" in parsed.path
                    or "v" in parsed.path
                )

        return False
    except Exception:
        return False
