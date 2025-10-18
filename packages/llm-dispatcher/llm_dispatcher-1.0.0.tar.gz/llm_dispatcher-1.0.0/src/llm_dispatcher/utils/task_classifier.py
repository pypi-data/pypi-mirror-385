"""
Task classification system for automatic task type detection.

This module provides intelligent task classification to automatically
determine the most appropriate task type for LLM requests.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging

from ..core.base import TaskType

logger = logging.getLogger(__name__)


class TaskClassifier:
    """
    Intelligent task classifier for automatic task type detection.

    This class analyzes input text and context to determine the most
    appropriate task type for LLM processing.
    """

    def __init__(self):
        self.keywords = self._initialize_keywords()
        self.patterns = self._initialize_patterns()
        self.context_weights = self._initialize_context_weights()

    def _initialize_keywords(self) -> Dict[TaskType, List[str]]:
        """Initialize keyword mappings for task classification."""
        return {
            TaskType.TEXT_GENERATION: [
                "write",
                "generate",
                "create",
                "compose",
                "draft",
                "produce",
                "story",
                "article",
                "blog",
                "content",
                "text",
                "narrative",
                "creative",
                "fiction",
                "non-fiction",
                "essay",
                "report",
            ],
            TaskType.CODE_GENERATION: [
                "code",
                "program",
                "script",
                "function",
                "class",
                "method",
                "algorithm",
                "implementation",
                "debug",
                "fix",
                "optimize",
                "python",
                "javascript",
                "java",
                "c++",
                "sql",
                "api",
                "framework",
                "library",
                "package",
                "module",
            ],
            TaskType.TRANSLATION: [
                "translate",
                "convert",
                "language",
                "english",
                "spanish",
                "french",
                "german",
                "chinese",
                "japanese",
                "korean",
                "portuguese",
                "italian",
                "russian",
                "arabic",
                "hindi",
            ],
            TaskType.SUMMARIZATION: [
                "summarize",
                "summary",
                "abstract",
                "overview",
                "brief",
                "condense",
                "shorten",
                "key points",
                "main ideas",
                "executive summary",
                "tl;dr",
                "recap",
            ],
            TaskType.QUESTION_ANSWERING: [
                "what",
                "how",
                "why",
                "when",
                "where",
                "who",
                "which",
                "question",
                "answer",
                "explain",
                "describe",
                "define",
                "help",
                "assist",
                "clarify",
                "understand",
            ],
            TaskType.CLASSIFICATION: [
                "classify",
                "categorize",
                "group",
                "sort",
                "label",
                "type",
                "category",
                "class",
                "classification",
                "sentiment",
                "positive",
                "negative",
                "neutral",
            ],
            TaskType.SENTIMENT_ANALYSIS: [
                "sentiment",
                "emotion",
                "feeling",
                "mood",
                "attitude",
                "opinion",
                "positive",
                "negative",
                "neutral",
                "happy",
                "sad",
                "angry",
                "excited",
                "disappointed",
            ],
            TaskType.VISION_ANALYSIS: [
                "image",
                "picture",
                "photo",
                "visual",
                "see",
                "look",
                "analyze",
                "describe",
                "identify",
                "recognize",
                "detect",
                "ocr",
                "text extraction",
                "object detection",
                "face recognition",
            ],
            TaskType.AUDIO_TRANSCRIPTION: [
                "audio",
                "sound",
                "speech",
                "voice",
                "transcribe",
                "transcription",
                "listen",
                "hear",
                "record",
                "podcast",
                "interview",
                "meeting",
                "conversation",
            ],
            TaskType.STRUCTURED_OUTPUT: [
                "json",
                "xml",
                "yaml",
                "csv",
                "structured",
                "format",
                "schema",
                "template",
                "form",
                "data",
                "extract",
                "parse",
                "organize",
                "table",
                "list",
            ],
            TaskType.FUNCTION_CALLING: [
                "function",
                "call",
                "api",
                "tool",
                "action",
                "execute",
                "run",
                "invoke",
                "trigger",
                "webhook",
                "endpoint",
                "service",
                "integration",
            ],
            TaskType.REASONING: [
                "reason",
                "think",
                "analyze",
                "logic",
                "deduce",
                "infer",
                "conclude",
                "argument",
                "premise",
                "hypothesis",
                "theory",
                "cause",
                "effect",
                "relationship",
                "correlation",
            ],
            TaskType.MATH: [
                "math",
                "mathematics",
                "calculate",
                "compute",
                "solve",
                "equation",
                "formula",
                "algebra",
                "geometry",
                "calculus",
                "statistics",
                "probability",
                "number",
                "numeric",
            ],
        }

    def _initialize_patterns(self) -> Dict[TaskType, List[str]]:
        """Initialize regex patterns for task classification."""
        return {
            TaskType.CODE_GENERATION: [
                r"def\s+\w+\s*\(",  # Python function definition
                r"function\s+\w+\s*\(",  # JavaScript function
                r"class\s+\w+",  # Class definition
                r"import\s+\w+",  # Import statement
                r"#include\s*<",  # C++ include
                r"SELECT\s+.*FROM",  # SQL query
                r"CREATE\s+TABLE",  # SQL DDL
            ],
            TaskType.QUESTION_ANSWERING: [
                r"^(what|how|why|when|where|who|which)\s+",  # Question words
                r"\?\s*$",  # Ends with question mark
                r"can you\s+",  # Can you questions
                r"could you\s+",  # Could you questions
                r"would you\s+",  # Would you questions
            ],
            TaskType.MATH: [
                r"\d+\s*[+\-*/]\s*\d+",  # Basic arithmetic
                r"=\s*\d+",  # Equals number
                r"solve\s+for\s+\w+",  # Solve for variable
                r"calculate\s+",  # Calculate instruction
                r"find\s+the\s+value",  # Find value
            ],
            TaskType.TRANSLATION: [
                r"translate\s+to\s+\w+",  # Translate to language
                r"from\s+\w+\s+to\s+\w+",  # From language to language
                r"in\s+\w+\s+language",  # In language
            ],
        }

    def _initialize_context_weights(self) -> Dict[str, float]:
        """Initialize context weights for classification."""
        return {
            "keyword_match": 0.4,
            "pattern_match": 0.3,
            "context_length": 0.1,
            "question_indicators": 0.1,
            "code_indicators": 0.1,
        }

    def classify(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> Tuple[TaskType, float]:
        """
        Classify text to determine the most appropriate task type.

        Args:
            text: Input text to classify
            context: Additional context information

        Returns:
            Tuple of (task_type, confidence_score)
        """
        if not text or not text.strip():
            return TaskType.TEXT_GENERATION, 0.0

        text_lower = text.lower().strip()
        scores = {}

        # Calculate scores for each task type
        for task_type in TaskType:
            score = self._calculate_task_score(task_type, text_lower, context)
            scores[task_type] = score

        # Find the task type with highest score
        best_task = max(scores.items(), key=lambda x: x[1])

        return best_task[0], best_task[1]

    def _calculate_task_score(
        self, task_type: TaskType, text: str, context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate score for a specific task type."""
        score = 0.0

        # Keyword matching
        keyword_score = self._calculate_keyword_score(task_type, text)
        score += keyword_score * self.context_weights["keyword_match"]

        # Pattern matching
        pattern_score = self._calculate_pattern_score(task_type, text)
        score += pattern_score * self.context_weights["pattern_match"]

        # Context length factor
        length_score = self._calculate_length_score(text)
        score += length_score * self.context_weights["context_length"]

        # Question indicators
        question_score = self._calculate_question_score(text)
        score += question_score * self.context_weights["question_indicators"]

        # Code indicators
        code_score = self._calculate_code_score(text)
        score += code_score * self.context_weights["code_indicators"]

        # Context-based adjustments
        if context:
            score = self._apply_context_adjustments(score, task_type, context)

        return min(score, 1.0)  # Cap at 1.0

    def _calculate_keyword_score(self, task_type: TaskType, text: str) -> float:
        """Calculate score based on keyword matching."""
        keywords = self.keywords.get(task_type, [])
        if not keywords:
            return 0.0

        matches = 0
        for keyword in keywords:
            if keyword in text:
                matches += 1

        return min(matches / len(keywords), 1.0)

    def _calculate_pattern_score(self, task_type: TaskType, text: str) -> float:
        """Calculate score based on pattern matching."""
        patterns = self.patterns.get(task_type, [])
        if not patterns:
            return 0.0

        matches = 0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1

        return min(matches / len(patterns), 1.0)

    def _calculate_length_score(self, text: str) -> float:
        """Calculate score based on text length."""
        length = len(text.split())

        # Different task types have different optimal lengths
        if length < 10:
            return 0.3  # Short text, likely question or simple request
        elif length < 50:
            return 0.7  # Medium text, good for most tasks
        elif length < 200:
            return 1.0  # Long text, good for complex tasks
        else:
            return 0.8  # Very long text, might be overwhelming

    def _calculate_question_score(self, text: str) -> float:
        """Calculate score based on question indicators."""
        question_indicators = [
            "?",
            "what",
            "how",
            "why",
            "when",
            "where",
            "who",
            "which",
        ]
        matches = sum(1 for indicator in question_indicators if indicator in text)
        return min(matches / 3, 1.0)  # Normalize to 0-1

    def _calculate_code_score(self, text: str) -> float:
        """Calculate score based on code indicators."""
        code_indicators = [
            "def ",
            "function",
            "class ",
            "import ",
            "#include",
            "SELECT",
            "CREATE",
        ]
        matches = sum(1 for indicator in code_indicators if indicator in text)
        return min(matches / 2, 1.0)  # Normalize to 0-1

    def _apply_context_adjustments(
        self, score: float, task_type: TaskType, context: Dict[str, Any]
    ) -> float:
        """Apply context-based adjustments to the score."""
        adjusted_score = score

        # Adjust based on input type
        if "images" in context and context["images"]:
            if task_type == TaskType.VISION_ANALYSIS:
                adjusted_score += 0.3
            else:
                adjusted_score -= 0.1

        if "audio" in context and context["audio"]:
            if task_type == TaskType.AUDIO_TRANSCRIPTION:
                adjusted_score += 0.3
            else:
                adjusted_score -= 0.1

        # Adjust based on structured output requirements
        if "structured_output" in context and context["structured_output"]:
            if task_type == TaskType.STRUCTURED_OUTPUT:
                adjusted_score += 0.2
            else:
                adjusted_score -= 0.1

        # Adjust based on function calling requirements
        if "functions" in context and context["functions"]:
            if task_type == TaskType.FUNCTION_CALLING:
                adjusted_score += 0.2
            else:
                adjusted_score -= 0.1

        return max(0.0, min(adjusted_score, 1.0))

    def get_top_candidates(self, text: str, n: int = 3) -> List[Tuple[TaskType, float]]:
        """
        Get top N task type candidates with their scores.

        Args:
            text: Input text to classify
            n: Number of top candidates to return

        Returns:
            List of (task_type, score) tuples sorted by score
        """
        if not text or not text.strip():
            return [(TaskType.TEXT_GENERATION, 0.0)]

        text_lower = text.lower().strip()
        scores = []

        for task_type in TaskType:
            score = self._calculate_task_score(task_type, text_lower, None)
            scores.append((task_type, score))

        # Sort by score (descending) and return top N
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:n]

    def classify_with_confidence(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        min_confidence: float = 0.3,
    ) -> Optional[TaskType]:
        """
        Classify text with confidence threshold.

        Args:
            text: Input text to classify
            context: Additional context information
            min_confidence: Minimum confidence threshold

        Returns:
            TaskType if confidence is above threshold, None otherwise
        """
        task_type, confidence = self.classify(text, context)

        if confidence >= min_confidence:
            return task_type
        else:
            return None

    def get_classification_explanation(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get detailed explanation of classification decision.

        Args:
            text: Input text to classify
            context: Additional context information

        Returns:
            Dictionary with classification details
        """
        if not text or not text.strip():
            return {
                "task_type": TaskType.TEXT_GENERATION,
                "confidence": 0.0,
                "reasoning": "Empty text, defaulting to text generation",
                "scores": {},
            }

        text_lower = text.lower().strip()
        task_type, confidence = self.classify(text, context)

        # Get detailed scores
        scores = {}
        for t in TaskType:
            scores[t.value] = self._calculate_task_score(t, text_lower, context)

        # Get reasoning
        reasoning = self._get_reasoning(task_type, text_lower, context)

        return {
            "task_type": task_type,
            "confidence": confidence,
            "reasoning": reasoning,
            "scores": scores,
            "top_candidates": self.get_top_candidates(text, 3),
        }

    def _get_reasoning(
        self, task_type: TaskType, text: str, context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate human-readable reasoning for classification."""
        reasons = []

        # Check keyword matches
        keywords = self.keywords.get(task_type, [])
        matched_keywords = [kw for kw in keywords if kw in text]
        if matched_keywords:
            reasons.append(f"Contains keywords: {', '.join(matched_keywords[:3])}")

        # Check pattern matches
        patterns = self.patterns.get(task_type, [])
        matched_patterns = [p for p in patterns if re.search(p, text, re.IGNORECASE)]
        if matched_patterns:
            reasons.append(f"Matches patterns: {len(matched_patterns)} pattern(s)")

        # Check context indicators
        if context:
            if (
                "images" in context
                and context["images"]
                and task_type == TaskType.VISION_ANALYSIS
            ):
                reasons.append("Contains image input")
            if (
                "audio" in context
                and context["audio"]
                and task_type == TaskType.AUDIO_TRANSCRIPTION
            ):
                reasons.append("Contains audio input")
            if (
                "structured_output" in context
                and context["structured_output"]
                and task_type == TaskType.STRUCTURED_OUTPUT
            ):
                reasons.append("Requires structured output")

        if not reasons:
            reasons.append("Default classification based on text characteristics")

        return "; ".join(reasons)


# Global task classifier instance
task_classifier = TaskClassifier()


def classify_task(
    text: str, context: Optional[Dict[str, Any]] = None
) -> Tuple[TaskType, float]:
    """Convenience function to classify task type."""
    return task_classifier.classify(text, context)


def get_task_candidates(text: str, n: int = 3) -> List[Tuple[TaskType, float]]:
    """Convenience function to get top task candidates."""
    return task_classifier.get_top_candidates(text, n)
