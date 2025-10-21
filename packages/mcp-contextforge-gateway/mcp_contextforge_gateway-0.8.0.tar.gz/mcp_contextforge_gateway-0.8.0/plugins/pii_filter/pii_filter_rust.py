# -*- coding: utf-8 -*-
"""Location: ./plugins/pii_filter/pii_filter_rust.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Mihai Criveti

Rust PII Filter Wrapper

Thin Python wrapper around the Rust implementation for seamless integration.
"""

from typing import Dict, List, Any, TYPE_CHECKING
import logging

# Use TYPE_CHECKING to avoid circular import at runtime
if TYPE_CHECKING:
    from .pii_filter import PIIFilterConfig

logger = logging.getLogger(__name__)

# Try to import Rust implementation
# Fix sys.path to prioritize site-packages over source directory
try:
    import sys
    import os

    # Temporarily remove current directory from path if it contains plugins_rust source
    original_path = sys.path.copy()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    plugins_rust_src = os.path.join(project_root, 'plugins_rust')

    # Remove source directory from path temporarily
    filtered_path = [p for p in sys.path if not p.startswith(plugins_rust_src)]
    sys.path = filtered_path

    try:
        from plugins_rust import PIIDetectorRust as _RustDetector
        RUST_AVAILABLE = True
        logger.info("🦀 Rust PII filter module imported successfully")
    finally:
        # Restore original path
        sys.path = original_path

except ImportError as e:
    RUST_AVAILABLE = False
    _RustDetector = None
    logger.warning(f"⚠️  Rust PII filter not available: {e}")


class RustPIIDetector:
    """Thin wrapper around Rust PIIDetectorRust implementation.

    This class provides the same interface as the Python PIIDetector,
    but delegates all operations to the high-performance Rust implementation.

    Example:
        >>> config = PIIFilterConfig()
        >>> detector = RustPIIDetector(config)
        >>> detections = detector.detect("My SSN is 123-45-6789")
        >>> print(detections)
        {'ssn': [{'value': '123-45-6789', 'start': 10, 'end': 21, ...}]}
    """

    def __init__(self, config: "PIIFilterConfig"):
        """Initialize Rust-backed PII detector.

        Args:
            config: PII filter configuration (Pydantic model)

        Raises:
            ImportError: If Rust implementation is not available
            ValueError: If configuration is invalid
        """
        # Import here to avoid circular dependency
        from .pii_filter import PIIFilterConfig  # pylint: disable=import-outside-toplevel

        if not RUST_AVAILABLE:
            raise ImportError(
                "Rust implementation not available. "
                "Install with: pip install mcpgateway[rust]"
            )

        # Validate config type
        if not isinstance(config, PIIFilterConfig):
            raise TypeError(f"Expected PIIFilterConfig, got {type(config)}")

        self.config = config

        # Convert Pydantic config to dictionary for Rust
        config_dict = config.model_dump()

        try:
            # Create Rust detector (this calls into Rust via PyO3)
            self._rust_detector = _RustDetector(config_dict)
            logger.debug("Rust PII detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Rust PII detector: {e}")
            raise ValueError(f"Rust detector initialization failed: {e}") from e

    def detect(self, text: str) -> Dict[str, List[Dict]]:
        """Detect PII in text using Rust implementation.

        Args:
            text: Text to scan for PII

        Returns:
            Dictionary mapping PII type to list of detections:
            {
                "ssn": [
                    {"value": "123-45-6789", "start": 10, "end": 21, "mask_strategy": "partial"}
                ],
                "email": [
                    {"value": "john@example.com", "start": 30, "end": 46, "mask_strategy": "partial"}
                ]
            }

        Example:
            >>> detector.detect("SSN: 123-45-6789")
            {'ssn': [{'value': '123-45-6789', 'start': 5, 'end': 16, 'mask_strategy': 'partial'}]}
        """
        try:
            return self._rust_detector.detect(text)
        except Exception as e:
            logger.error(f"Rust detection failed: {e}")
            raise RuntimeError(f"PII detection failed: {e}") from e

    def mask(self, text: str, detections: Dict[str, List[Dict]]) -> str:
        """Mask detected PII in text using Rust implementation.

        Args:
            text: Original text
            detections: Detection results from detect()

        Returns:
            Masked text with PII replaced according to strategies

        Example:
            >>> text = "SSN: 123-45-6789"
            >>> detections = detector.detect(text)
            >>> detector.mask(text, detections)
            'SSN: ***-**-6789'
        """
        try:
            return self._rust_detector.mask(text, detections)
        except Exception as e:
            logger.error(f"Rust masking failed: {e}")
            raise RuntimeError(f"PII masking failed: {e}") from e

    def process_nested(self, data: Any, path: str = "") -> tuple[bool, Any, Dict]:
        """Process nested data structures (dicts, lists, strings) using Rust.

        This method recursively traverses nested structures and detects/masks
        PII in all string values found within.

        Args:
            data: Data structure to process (dict, list, str, or other)
            path: Current path in the structure (for logging)

        Returns:
            Tuple of (modified, new_data, detections) where:
            - modified: True if any PII was found and masked
            - new_data: The data structure with masked PII
            - detections: Dictionary of all detections found

        Example:
            >>> data = {"user": {"ssn": "123-45-6789", "name": "John"}}
            >>> modified, new_data, detections = detector.process_nested(data)
            >>> print(new_data)
            {'user': {'ssn': '***-**-6789', 'name': 'John'}}
        """
        try:
            return self._rust_detector.process_nested(data, path)
        except Exception as e:
            logger.error(f"Rust nested processing failed: {e}")
            raise RuntimeError(f"Nested PII processing failed: {e}") from e


# Export module-level availability flag
__all__ = ['RustPIIDetector', 'RUST_AVAILABLE']
