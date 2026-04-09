"""Configuration management for LearningAgent project."""

import os
from pathlib import Path
from typing import ClassVar
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for LearningAgent settings."""

    # LLM Configuration
    LLM_MODEL_ID: str = os.getenv("LLM_MODEL_ID", "claude-3-5-sonnet-20241022")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.anthropic.com")
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))

    # GitHub Configuration
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")

    # Application Configuration
    LEARNING_AGENT_HOME: Path = Path(os.getenv(
        "LEARNING_AGENT_HOME",
        Path.home() / ".learningAgent"
    ))
    LOG_LEVEL: str = os.getenv("LEARNING_AGENT_LOG_LEVEL", "INFO")

    # Summary Configuration
    SUMMARY_FULL_REWRITE_THRESHOLD: ClassVar[int] = 5

    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present.

        Raises:
            ValueError: If LLM_API_KEY is not set.
        """
        if not cls.LLM_API_KEY:
            raise ValueError("LLM_API_KEY is required but not set")

    @classmethod
    def ensure_home_directory(cls) -> Path:
        """Ensure the learning agent home directory exists.

        Returns:
            Path to the home directory.
        """
        cls.LEARNING_AGENT_HOME.mkdir(parents=True, exist_ok=True)
        return cls.LEARNING_AGENT_HOME
