"""Secret detection engine for identifying and templating sensitive values."""

import math
import re
from dataclasses import dataclass, field
from typing import Optional

from aiconfigkit.core.models import SecretConfidence


@dataclass
class SecretDetectionResult:
    """Result of secret detection analysis.

    Attributes:
        confidence: Confidence level that this is a secret
        reason: Human-readable explanation of detection
        original_value: Original value analyzed
        templated_value: Suggested template replacement (e.g., ${API_KEY})
    """

    confidence: SecretConfidence
    reason: str
    original_value: str
    templated_value: Optional[str] = None


@dataclass
class SecretDetector:
    """Heuristic-based secret detector with three confidence levels.

    Detection rules:
    - HIGH: Keywords (*_TOKEN, *_KEY, *_SECRET, *_PASSWORD, API_*, AUTH_*),
            high entropy (>4.5 bits/char), API key patterns (20+ alphanumeric)
    - MEDIUM: Ambiguous keywords (*_URL with credentials, *_ID with entropy)
    - SAFE: URLs without credentials, booleans, version strings, short values (<8 chars)
    """

    high_entropy_threshold: float = 4.5
    min_secret_length: int = 8

    secret_keywords: list[str] = field(
        default_factory=lambda: [
            "TOKEN",
            "KEY",
            "SECRET",
            "PASSWORD",
            "PASSWD",
            "CREDENTIAL",
            "AUTH",
            "PRIVATE",
            "API",
        ]
    )

    safe_keywords: list[str] = field(
        default_factory=lambda: [
            "PATH",
            "DIR",
            "NAME",
            "TYPE",
            "MODE",
            "DEBUG",
            "LEVEL",
            "HOST",
            "PORT",
            "VERSION",
            "ENABLED",
            "DISABLED",
        ]
    )

    ambiguous_keywords: list[str] = field(default_factory=lambda: ["URL", "ID", "ENDPOINT", "URI"])

    def detect(self, value: str, key_name: str = "") -> SecretDetectionResult:
        """Analyze a value to determine if it's likely a secret.

        Args:
            value: The value to analyze
            key_name: Optional environment variable or key name (e.g., "API_KEY")

        Returns:
            SecretDetectionResult with confidence level and explanation
        """
        if not value or not value.strip():
            return SecretDetectionResult(
                confidence=SecretConfidence.SAFE,
                reason="Empty or whitespace-only value",
                original_value=value,
            )

        key_upper = key_name.upper() if key_name else ""

        keyword_result = self._keyword_match(key_upper, value)
        if keyword_result:
            return keyword_result

        pattern_result = self._pattern_match(value, key_upper)
        if pattern_result:
            return pattern_result

        entropy_result = self._entropy_analysis(value, key_upper)
        if entropy_result:
            return entropy_result

        return SecretDetectionResult(
            confidence=SecretConfidence.SAFE,
            reason="No secret indicators detected",
            original_value=value,
        )

    def template_value(self, key: str) -> str:
        """Convert a key name to a template placeholder.

        Args:
            key: The key name (e.g., "API_KEY", "github_token")

        Returns:
            Template placeholder (e.g., "${API_KEY}")
        """
        normalized_key = key.upper().replace("-", "_")
        if not normalized_key.startswith("$"):
            return f"${{{normalized_key}}}"
        return normalized_key

    def _keyword_match(self, key_upper: str, value: str) -> Optional[SecretDetectionResult]:
        """Check for secret-related keywords in the key name.

        Args:
            key_upper: Uppercase key name
            value: The value being analyzed

        Returns:
            SecretDetectionResult if keyword matched, None otherwise
        """
        if not key_upper:
            return None

        for safe_kw in self.safe_keywords:
            if safe_kw in key_upper:
                parts = key_upper.split("_")
                if safe_kw in parts:
                    is_only_safe = True
                    for part in parts:
                        if part and part not in self.safe_keywords and any(
                            sk in part for sk in self.secret_keywords
                        ):
                            is_only_safe = False
                            break
                    if is_only_safe:
                        return SecretDetectionResult(
                            confidence=SecretConfidence.SAFE,
                            reason=f"Key contains safe keyword '{safe_kw}'",
                            original_value=value,
                        )

        for secret_kw in self.secret_keywords:
            if secret_kw in key_upper:
                return SecretDetectionResult(
                    confidence=SecretConfidence.HIGH,
                    reason=f"Key contains secret keyword '{secret_kw}'",
                    original_value=value,
                    templated_value=self.template_value(key_upper),
                )

        for ambig_kw in self.ambiguous_keywords:
            if ambig_kw in key_upper:
                if self._contains_credentials_in_url(value):
                    return SecretDetectionResult(
                        confidence=SecretConfidence.HIGH,
                        reason=f"Key contains '{ambig_kw}' with embedded credentials",
                        original_value=value,
                        templated_value=self.template_value(key_upper),
                    )
                entropy = self._calculate_entropy(value)
                if entropy > self.high_entropy_threshold:
                    return SecretDetectionResult(
                        confidence=SecretConfidence.MEDIUM,
                        reason=f"Key contains '{ambig_kw}' with high entropy value",
                        original_value=value,
                        templated_value=self.template_value(key_upper),
                    )

        return None

    def _pattern_match(self, value: str, key_upper: str) -> Optional[SecretDetectionResult]:
        """Check for known secret patterns in the value.

        Args:
            value: The value to analyze
            key_upper: Uppercase key name for templating

        Returns:
            SecretDetectionResult if pattern matched, None otherwise
        """
        if self._is_boolean_value(value):
            return SecretDetectionResult(
                confidence=SecretConfidence.SAFE,
                reason="Boolean value",
                original_value=value,
            )

        if self._is_numeric_value(value):
            return SecretDetectionResult(
                confidence=SecretConfidence.SAFE,
                reason="Numeric value",
                original_value=value,
            )

        if self._is_version_string(value):
            return SecretDetectionResult(
                confidence=SecretConfidence.SAFE,
                reason="Version string",
                original_value=value,
            )

        if len(value) < self.min_secret_length:
            return SecretDetectionResult(
                confidence=SecretConfidence.SAFE,
                reason=f"Value too short ({len(value)} chars < {self.min_secret_length})",
                original_value=value,
            )

        if self._matches_api_key_pattern(value):
            return SecretDetectionResult(
                confidence=SecretConfidence.HIGH,
                reason="Matches API key pattern (20+ alphanumeric characters)",
                original_value=value,
                templated_value=self.template_value(key_upper) if key_upper else None,
            )

        if self._matches_jwt_pattern(value):
            return SecretDetectionResult(
                confidence=SecretConfidence.HIGH,
                reason="Matches JWT token pattern",
                original_value=value,
                templated_value=self.template_value(key_upper) if key_upper else None,
            )

        if self._matches_base64_secret_pattern(value):
            entropy = self._calculate_entropy(value)
            if entropy > self.high_entropy_threshold:
                return SecretDetectionResult(
                    confidence=SecretConfidence.HIGH,
                    reason="Matches base64 encoded secret pattern with high entropy",
                    original_value=value,
                    templated_value=self.template_value(key_upper) if key_upper else None,
                )

        url_analysis = self._analyze_url(value)
        if url_analysis:
            return url_analysis

        return None

    def _entropy_analysis(self, value: str, key_upper: str) -> Optional[SecretDetectionResult]:
        """Analyze value entropy to detect potential secrets.

        Args:
            value: The value to analyze
            key_upper: Uppercase key name for templating

        Returns:
            SecretDetectionResult if high entropy detected, None otherwise
        """
        if len(value) < self.min_secret_length:
            return None

        entropy = self._calculate_entropy(value)

        if entropy > self.high_entropy_threshold:
            return SecretDetectionResult(
                confidence=SecretConfidence.MEDIUM,
                reason=f"High entropy value ({entropy:.2f} bits/char)",
                original_value=value,
                templated_value=self.template_value(key_upper) if key_upper else None,
            )

        return None

    def _calculate_entropy(self, value: str) -> float:
        """Calculate Shannon entropy of a string.

        Args:
            value: String to analyze

        Returns:
            Entropy in bits per character
        """
        if not value:
            return 0.0

        char_counts: dict[str, int] = {}
        for char in value:
            char_counts[char] = char_counts.get(char, 0) + 1

        entropy = 0.0
        length = len(value)
        for count in char_counts.values():
            if count > 0:
                probability = count / length
                entropy -= probability * math.log2(probability)

        return entropy

    def _is_boolean_value(self, value: str) -> bool:
        """Check if value is a boolean."""
        return value.lower() in ("true", "false", "yes", "no", "1", "0", "on", "off")

    def _is_numeric_value(self, value: str) -> bool:
        """Check if value is purely numeric."""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _is_version_string(self, value: str) -> bool:
        """Check if value looks like a version string."""
        version_pattern = r"^v?\d+(\.\d+){0,3}(-[\w.]+)?(\+[\w.]+)?$"
        return bool(re.match(version_pattern, value))

    def _matches_api_key_pattern(self, value: str) -> bool:
        """Check if value matches common API key patterns."""
        if len(value) < 20:
            return False
        api_key_pattern = r"^[A-Za-z0-9_-]{20,}$"
        return bool(re.match(api_key_pattern, value))

    def _matches_jwt_pattern(self, value: str) -> bool:
        """Check if value matches JWT token pattern."""
        jwt_pattern = r"^eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$"
        return bool(re.match(jwt_pattern, value))

    def _matches_base64_secret_pattern(self, value: str) -> bool:
        """Check if value looks like a base64-encoded secret."""
        if len(value) < 16:
            return False
        base64_pattern = r"^[A-Za-z0-9+/=]{16,}$"
        if re.match(base64_pattern, value):
            if value.endswith("==") or value.endswith("="):
                return True
            alphanumeric_ratio = sum(c.isalnum() for c in value) / len(value)
            return alphanumeric_ratio > 0.9
        return False

    def _analyze_url(self, value: str) -> Optional[SecretDetectionResult]:
        """Analyze URL values for embedded credentials.

        Args:
            value: The value to analyze

        Returns:
            SecretDetectionResult if URL analysis applies
        """
        url_pattern = r"^https?://"
        if not re.match(url_pattern, value, re.IGNORECASE):
            return None

        if self._contains_credentials_in_url(value):
            return SecretDetectionResult(
                confidence=SecretConfidence.HIGH,
                reason="URL contains embedded credentials",
                original_value=value,
            )

        return SecretDetectionResult(
            confidence=SecretConfidence.SAFE,
            reason="URL without embedded credentials",
            original_value=value,
        )

    def _contains_credentials_in_url(self, value: str) -> bool:
        """Check if URL contains embedded credentials (user:pass@)."""
        cred_pattern = r"https?://[^/]+:[^@]+@"
        return bool(re.match(cred_pattern, value, re.IGNORECASE))


from typing import Any


def template_secrets_in_config(config: dict[str, Any], detector: Optional[SecretDetector] = None) -> tuple[dict[str, Any], list[str]]:
    """Process a configuration dict and template detected secrets.

    Args:
        config: Configuration dictionary (e.g., MCP server config)
        detector: SecretDetector instance (creates default if None)

    Returns:
        Tuple of (templated config, list of templated key names)
    """
    if detector is None:
        detector = SecretDetector()

    templated_keys: list[str] = []
    result = _template_dict_recursive(config, detector, templated_keys, "")

    # We know the result is a dict since config is a dict
    assert isinstance(result, dict)
    return result, templated_keys


def _template_dict_recursive(
    obj: Any,
    detector: SecretDetector,
    templated_keys: list[str],
    current_path: str,
) -> Any:
    """Recursively process nested structures for secret templating.

    Args:
        obj: Object to process
        detector: SecretDetector instance
        templated_keys: List to append templated key names
        current_path: Current key path for context

    Returns:
        Processed object with secrets templated
    """
    if isinstance(obj, dict):
        result: dict[str, Any] = {}
        for key, value in obj.items():
            path = f"{current_path}.{key}" if current_path else key
            if isinstance(value, str):
                detection = detector.detect(value, key)
                if detection.confidence in (SecretConfidence.HIGH, SecretConfidence.MEDIUM):
                    if detection.templated_value:
                        result[key] = detection.templated_value
                        templated_keys.append(key)
                    else:
                        result[key] = detector.template_value(key)
                        templated_keys.append(key)
                else:
                    result[key] = value
            else:
                result[key] = _template_dict_recursive(value, detector, templated_keys, path)
        return result
    elif isinstance(obj, list):
        return [_template_dict_recursive(item, detector, templated_keys, current_path) for item in obj]
    else:
        return obj
