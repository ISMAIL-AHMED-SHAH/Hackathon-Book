"""
Unit tests for Pydantic schemas and error handler.

Tests ensure 100% type safety per Constitution Rule I and validate all
business logic validators per Constitution Rule III.

Test Coverage Target: 90%+ per Constitution Rule II
"""

from datetime import datetime
from typing import Any, Dict

import pytest
from pydantic import ValidationError

from src.models.schemas import (
    Citation,
    GroundingStatus,
    QueryRequest,
    QueryResponse,
)
from src.utils.error_handler import (
    ErrorCode,
    StandardErrorResponse,
    get_standard_error_response,
)


class TestQueryRequest:
    """Test suite for QueryRequest validation."""

    def test_valid_query_request_minimal(self) -> None:
        """Test valid QueryRequest with minimal required fields."""
        request = QueryRequest(
            query_text="What is ROS 2?",
            chapter_id="ch-ros2-fundamentals",
            user_id="550e8400-e29b-41d4-a716-446655440000",
        )

        assert request.query_text == "What is ROS 2?"
        assert request.chapter_id == "ch-ros2-fundamentals"
        assert request.user_id == "550e8400-e29b-41d4-a716-446655440000"
        assert request.top_k == 5  # Default value
        assert request.temperature == 0.7  # Default value
        assert request.session_id is None

    def test_valid_query_request_full(self) -> None:
        """Test valid QueryRequest with all optional fields."""
        request = QueryRequest(
            query_text="How do I create a ROS 2 node?",
            chapter_id="ch-ros2-fundamentals",
            user_id="550e8400-e29b-41d4-a716-446655440000",
            top_k=10,
            temperature=0.3,
            session_id="sess-a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
        )

        assert request.query_text == "How do I create a ROS 2 node?"
        assert request.top_k == 10
        assert request.temperature == 0.3
        assert request.session_id == "sess-a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"

    def test_query_text_whitespace_stripped(self) -> None:
        """Test that query_text whitespace is automatically stripped."""
        request = QueryRequest(
            query_text="  What is ROS 2?  ",
            chapter_id="ch-ros2-fundamentals",
            user_id="550e8400-e29b-41d4-a716-446655440000",
        )

        # Pydantic's str_strip_whitespace=True should strip it
        assert request.query_text == "What is ROS 2?"

    def test_query_text_empty_rejected(self) -> None:
        """Test that empty query_text is rejected (FR-002)."""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(
                query_text="",
                chapter_id="ch-ros2-fundamentals",
                user_id="550e8400-e29b-41d4-a716-446655440000",
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("query_text",)
        # Pydantic returns "should have at least 1 character"
        assert "at least 1" in errors[0]["msg"].lower() or "empty" in errors[0]["msg"].lower()

    def test_query_text_whitespace_only_rejected(self) -> None:
        """Test that whitespace-only query_text is rejected (FR-002)."""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(
                query_text="   ",
                chapter_id="ch-ros2-fundamentals",
                user_id="550e8400-e29b-41d4-a716-446655440000",
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("query_text",)

    def test_query_text_too_long_rejected(self) -> None:
        """Test that query_text exceeding max_length is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(
                query_text="x" * 1001,  # Exceeds max_length=1000
                chapter_id="ch-ros2-fundamentals",
                user_id="550e8400-e29b-41d4-a716-446655440000",
            )

        errors = exc_info.value.errors()
        assert any("max_length" in str(e).lower() for e in errors)

    def test_chapter_id_valid_formats(self) -> None:
        """Test valid chapter_id formats."""
        valid_chapter_ids = [
            "ch-ros2-fundamentals",
            "ch-isaac-sim-intro",
            "ch-abc",  # Minimum length
            "ch-" + "a" * 50,  # Maximum length
            "ch-ros2-nodes-123",  # With numbers
        ]

        for chapter_id in valid_chapter_ids:
            request = QueryRequest(
                query_text="Test",
                chapter_id=chapter_id,
                user_id="550e8400-e29b-41d4-a716-446655440000",
            )
            assert request.chapter_id == chapter_id.lower()

    def test_chapter_id_invalid_formats_rejected(self) -> None:
        """Test invalid chapter_id formats are rejected (FR-013)."""
        invalid_chapter_ids = [
            "ros2-fundamentals",  # Missing 'ch-' prefix
            "ch-ab",  # Too short (< 3 chars after prefix)
            "ch-" + "a" * 51,  # Too long (> 50 chars after prefix)
            "ch-ROS2-Fundamentals",  # Uppercase not allowed
            "ch-ros2_fundamentals",  # Underscore not allowed
            "ch-ros2/fundamentals",  # Slash not allowed
            "ch-ros2; DROP TABLE--",  # SQL injection attempt
        ]

        for chapter_id in invalid_chapter_ids:
            with pytest.raises(ValidationError):
                QueryRequest(
                    query_text="Test",
                    chapter_id=chapter_id,
                    user_id="550e8400-e29b-41d4-a716-446655440000",
                )

    def test_user_id_valid_uuidv4(self) -> None:
        """Test valid UUIDv4 formats are accepted (FR-002)."""
        valid_user_ids = [
            "550e8400-e29b-41d4-a716-446655440000",
            "123e4567-e89b-42d3-a456-426614174000",
            "AAAAAAAA-BBBB-4CCC-8DDD-EEEEEEEEEEEE",  # Uppercase
        ]

        for user_id in valid_user_ids:
            request = QueryRequest(
                query_text="Test",
                chapter_id="ch-ros2-fundamentals",
                user_id=user_id,
            )
            # Should be normalized to lowercase
            assert request.user_id == user_id.lower()

    def test_user_id_invalid_formats_rejected(self) -> None:
        """Test invalid user_id formats are rejected (FR-002)."""
        invalid_user_ids = [
            "not-a-uuid",
            "",
            "550e8400-e29b-41d4-a716",  # Incomplete
        ]

        for user_id in invalid_user_ids:
            with pytest.raises(ValidationError):
                QueryRequest(
                    query_text="Test",
                    chapter_id="ch-ros2-fundamentals",
                    user_id=user_id,
                )

    def test_top_k_boundary_values(self) -> None:
        """Test top_k boundary validation (1-10 range)."""
        # Valid boundaries
        for top_k in [1, 5, 10]:
            request = QueryRequest(
                query_text="Test",
                chapter_id="ch-ros2-fundamentals",
                user_id="550e8400-e29b-41d4-a716-446655440000",
                top_k=top_k,
            )
            assert request.top_k == top_k

        # Invalid boundaries
        for top_k in [0, 11, -1, 100]:
            with pytest.raises(ValidationError):
                QueryRequest(
                    query_text="Test",
                    chapter_id="ch-ros2-fundamentals",
                    user_id="550e8400-e29b-41d4-a716-446655440000",
                    top_k=top_k,
                )

    def test_temperature_boundary_values(self) -> None:
        """Test temperature boundary validation (0.0-1.0 range)."""
        # Valid boundaries
        for temp in [0.0, 0.5, 1.0]:
            request = QueryRequest(
                query_text="Test",
                chapter_id="ch-ros2-fundamentals",
                user_id="550e8400-e29b-41d4-a716-446655440000",
                temperature=temp,
            )
            assert request.temperature == temp

        # Invalid boundaries
        for temp in [-0.1, 1.1, 2.0]:
            with pytest.raises(ValidationError):
                QueryRequest(
                    query_text="Test",
                    chapter_id="ch-ros2-fundamentals",
                    user_id="550e8400-e29b-41d4-a716-446655440000",
                    temperature=temp,
                )

    def test_session_id_valid_format(self) -> None:
        """Test valid session_id format."""
        request = QueryRequest(
            query_text="Test",
            chapter_id="ch-ros2-fundamentals",
            user_id="550e8400-e29b-41d4-a716-446655440000",
            session_id="sess-a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
        )
        assert request.session_id == "sess-a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"

    def test_session_id_invalid_formats_rejected(self) -> None:
        """Test invalid session_id formats are rejected."""
        invalid_session_ids = [
            "sess-123",  # Too short
            "session-a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",  # Wrong prefix
            "sess-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",  # Not hex
            "sess-a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d",  # Wrong length (31 chars)
        ]

        for session_id in invalid_session_ids:
            with pytest.raises(ValidationError):
                QueryRequest(
                    query_text="Test",
                    chapter_id="ch-ros2-fundamentals",
                    user_id="550e8400-e29b-41d4-a716-446655440000",
                    session_id=session_id,
                )


class TestCitation:
    """Test suite for Citation (SourceChunk) model."""

    def test_valid_citation_full(self) -> None:
        """Test valid Citation with all fields."""
        citation = Citation(
            chunk_id="ch-ros2-fundamentals_chunk_0042",
            content="ROS 2 nodes are the fundamental building blocks...",
            similarity_score=0.87,
            page_number=42,
            section_title="Understanding ROS 2 Nodes",
        )

        assert citation.chunk_id == "ch-ros2-fundamentals_chunk_0042"
        assert citation.similarity_score == 0.87
        assert citation.page_number == 42
        assert citation.section_title == "Understanding ROS 2 Nodes"

    def test_valid_citation_minimal(self) -> None:
        """Test valid Citation with only required fields."""
        citation = Citation(
            chunk_id="ch-ros2-fundamentals_chunk_0042",
            content="ROS 2 nodes are the fundamental building blocks...",
            similarity_score=0.87,
        )

        assert citation.page_number is None
        assert citation.section_title is None

    def test_content_max_length_enforced(self) -> None:
        """Test content max_length=500 is enforced."""
        with pytest.raises(ValidationError):
            Citation(
                chunk_id="ch-ros2-fundamentals_chunk_0042",
                content="x" * 501,  # Exceeds max_length
                similarity_score=0.87,
            )

    def test_similarity_score_boundaries(self) -> None:
        """Test similarity_score must be between 0.0 and 1.0."""
        # Valid boundaries
        for score in [0.0, 0.5, 1.0]:
            citation = Citation(
                chunk_id="test_chunk",
                content="Test content",
                similarity_score=score,
            )
            assert citation.similarity_score == score

        # Invalid boundaries
        for score in [-0.1, 1.1, 2.0]:
            with pytest.raises(ValidationError):
                Citation(
                    chunk_id="test_chunk",
                    content="Test content",
                    similarity_score=score,
                )

    def test_page_number_minimum_value(self) -> None:
        """Test page_number must be >= 1."""
        # Valid
        citation = Citation(
            chunk_id="test_chunk",
            content="Test",
            similarity_score=0.5,
            page_number=1,
        )
        assert citation.page_number == 1

        # Invalid
        with pytest.raises(ValidationError):
            Citation(
                chunk_id="test_chunk",
                content="Test",
                similarity_score=0.5,
                page_number=0,
            )


class TestQueryResponse:
    """Test suite for QueryResponse model."""

    def test_valid_query_response_full(self) -> None:
        """Test valid QueryResponse with all fields."""
        response = QueryResponse(
            answer="ROS 2 nodes are the fundamental building blocks...",
            sources=[
                Citation(
                    chunk_id="ch-ros2-fundamentals_chunk_0042",
                    content="ROS 2 nodes are independent...",
                    similarity_score=0.87,
                    page_number=42,
                    section_title="Understanding ROS 2 Nodes",
                )
            ],
            confidence_score=0.87,
            grounding_status=GroundingStatus.FULLY_GROUNDED,
            query_id="qry-1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d",
            session_id="sess-a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
            processing_time_ms=1847,
            metadata={"model_version": "gpt-4-turbo-preview"},
        )

        assert response.answer == "ROS 2 nodes are the fundamental building blocks..."
        assert len(response.sources) == 1
        assert response.confidence_score == 0.87
        assert response.grounding_status == GroundingStatus.FULLY_GROUNDED
        assert response.processing_time_ms == 1847
        assert isinstance(response.created_at, datetime)

    def test_sources_list_constraints(self) -> None:
        """Test sources list must have 1-10 items."""
        # Valid: 1 source
        response = QueryResponse(
            answer="Test answer",
            sources=[
                Citation(
                    chunk_id="test_chunk",
                    content="Test",
                    similarity_score=0.5,
                )
            ],
            confidence_score=0.5,
            grounding_status=GroundingStatus.SPECULATIVE,
            query_id="qry-1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d",
            processing_time_ms=1000,
        )
        assert len(response.sources) == 1

        # Invalid: 0 sources
        with pytest.raises(ValidationError):
            QueryResponse(
                answer="Test answer",
                sources=[],
                confidence_score=0.5,
                grounding_status=GroundingStatus.SPECULATIVE,
                query_id="qry-1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d",
                processing_time_ms=1000,
            )

        # Invalid: 11 sources
        with pytest.raises(ValidationError):
            QueryResponse(
                answer="Test answer",
                sources=[
                    Citation(
                        chunk_id=f"chunk_{i}",
                        content="Test",
                        similarity_score=0.5,
                    )
                    for i in range(11)
                ],
                confidence_score=0.5,
                grounding_status=GroundingStatus.SPECULATIVE,
                query_id="qry-1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d",
                processing_time_ms=1000,
            )

    def test_query_id_pattern_validation(self) -> None:
        """Test query_id must match pattern ^qry-[a-f0-9]{32}$."""
        # Valid
        response = QueryResponse(
            answer="Test",
            sources=[Citation(chunk_id="test", content="Test", similarity_score=0.5)],
            confidence_score=0.5,
            grounding_status=GroundingStatus.SPECULATIVE,
            query_id="qry-1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d",
            processing_time_ms=1000,
        )
        assert response.query_id == "qry-1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d"

        # Invalid patterns
        invalid_query_ids = [
            "query-1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d",  # Wrong prefix
            "qry-1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4",  # Too short
            "qry-1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4dX",  # Too long
            "qry-1A2B3C4D5E6F1A2B3C4D5E6F1A2B3C4D",  # Uppercase
            "qry-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # Invalid hex
        ]

        for query_id in invalid_query_ids:
            with pytest.raises(ValidationError):
                QueryResponse(
                    answer="Test",
                    sources=[Citation(chunk_id="test", content="Test", similarity_score=0.5)],
                    confidence_score=0.5,
                    grounding_status=GroundingStatus.SPECULATIVE,
                    query_id=query_id,
                    processing_time_ms=1000,
                )


class TestGroundingStatus:
    """Test suite for GroundingStatus enum."""

    def test_grounding_status_values(self) -> None:
        """Test all GroundingStatus enum values."""
        assert GroundingStatus.FULLY_GROUNDED.value == "fully_grounded"
        assert GroundingStatus.PARTIALLY_GROUNDED.value == "partially_grounded"
        assert GroundingStatus.SPECULATIVE.value == "speculative"

    def test_grounding_status_in_response(self) -> None:
        """Test GroundingStatus enum works in QueryResponse."""
        for status in [
            GroundingStatus.FULLY_GROUNDED,
            GroundingStatus.PARTIALLY_GROUNDED,
            GroundingStatus.SPECULATIVE,
        ]:
            response = QueryResponse(
                answer="Test",
                sources=[Citation(chunk_id="test", content="Test", similarity_score=0.5)],
                confidence_score=0.5,
                grounding_status=status,
                query_id="qry-1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d",
                processing_time_ms=1000,
            )
            assert response.grounding_status == status


class TestStandardErrorResponse:
    """Test suite for StandardErrorResponse model."""

    def test_valid_error_response_minimal(self) -> None:
        """Test valid StandardErrorResponse with minimal fields."""
        error = StandardErrorResponse(
            error_code=ErrorCode.QUERY_TEXT_EMPTY,
            message="Query text cannot be empty",
        )

        assert error.error_code == ErrorCode.QUERY_TEXT_EMPTY
        assert error.message == "Query text cannot be empty"
        assert error.field is None
        assert error.details is None
        assert error.request_id is None

    def test_valid_error_response_full(self) -> None:
        """Test valid StandardErrorResponse with all fields."""
        error = StandardErrorResponse(
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message="Rate limit exceeded",
            field="user_id",
            details={"retry_after": 60},
            request_id="req-a1b2c3d4",
        )

        assert error.error_code == ErrorCode.RATE_LIMIT_EXCEEDED
        assert error.field == "user_id"
        assert error.details == {"retry_after": 60}
        assert error.request_id == "req-a1b2c3d4"


class TestErrorCode:
    """Test suite for ErrorCode enum."""

    def test_all_error_codes_exist(self) -> None:
        """Test all required error codes exist (per data-model.md)."""
        required_codes = [
            "INVALID_INPUT",
            "QUERY_TEXT_EMPTY",
            "INVALID_CHAPTER_ID",
            "INVALID_USER_ID",
            "MISSING_TOKEN",
            "INVALID_TOKEN",
            "TOKEN_EXPIRED",
            "CHAPTER_ACCESS_DENIED",
            "CONTEXT_NOT_FOUND",
            "INSUFFICIENT_GROUNDING",
            "RATE_LIMIT_EXCEEDED",
            "INTERNAL_ERROR",
            "LLM_SERVICE_ERROR",
            "VECTOR_DB_ERROR",
            "SERVICE_UNAVAILABLE",
        ]

        for code in required_codes:
            assert hasattr(ErrorCode, code), f"Missing ErrorCode.{code}"
            assert ErrorCode[code].value == code


class TestGetStandardErrorResponse:
    """Test suite for get_standard_error_response function."""

    def test_valid_error_response_creation(self) -> None:
        """Test creating a valid error response."""
        result = get_standard_error_response(
            error_code="QUERY_TEXT_EMPTY",
            message="Query text cannot be empty",
            status_code=400,
            field="query_text",
        )

        assert result["status_code"] == 400
        assert result["body"]["error_code"] == "QUERY_TEXT_EMPTY"
        assert result["body"]["message"] == "Query text cannot be empty"
        assert result["body"]["field"] == "query_text"

    def test_error_response_with_details(self) -> None:
        """Test error response with details dictionary."""
        result = get_standard_error_response(
            error_code="RATE_LIMIT_EXCEEDED",
            message="Rate limit exceeded",
            status_code=429,
            details={"retry_after": 60, "limit": 10},
        )

        assert result["status_code"] == 429
        assert result["body"]["details"]["retry_after"] == 60
        assert result["body"]["details"]["limit"] == 10

    def test_error_response_with_request_id(self) -> None:
        """Test error response with request_id."""
        result = get_standard_error_response(
            error_code="INTERNAL_ERROR",
            message="Internal server error",
            status_code=500,
            request_id="req-xyz123",
        )

        assert result["body"]["request_id"] == "req-xyz123"

    def test_invalid_error_code_raises_valueerror(self) -> None:
        """Test invalid error_code raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_standard_error_response(
                error_code="INVALID_CODE_THAT_DOES_NOT_EXIST",
                message="Test message",
            )

        assert "Invalid error_code" in str(exc_info.value)

    def test_default_status_code(self) -> None:
        """Test default status_code is 400."""
        result = get_standard_error_response(
            error_code="INVALID_INPUT",
            message="Invalid input",
        )

        assert result["status_code"] == 400

    def test_exclude_none_in_output(self) -> None:
        """Test that None fields are excluded from output."""
        result = get_standard_error_response(
            error_code="QUERY_TEXT_EMPTY",
            message="Query text cannot be empty",
        )

        # None fields should not be present in the output
        assert "field" not in result["body"]
        assert "details" not in result["body"]
        assert "request_id" not in result["body"]

    def test_all_error_codes_work(self) -> None:
        """Test that all ErrorCode enum values work with the function."""
        for error_code in ErrorCode:
            result = get_standard_error_response(
                error_code=error_code.value,
                message=f"Test message for {error_code.value}",
                status_code=400,
            )

            assert result["status_code"] == 400
            assert result["body"]["error_code"] == error_code.value

    def test_type_hints_enforced(self) -> None:
        """Test that type hints are properly enforced."""
        # This test validates that the function signature has type hints
        import inspect

        sig = inspect.signature(get_standard_error_response)

        # Check return type
        assert sig.return_annotation == Dict[str, Any]

        # Check parameter types
        assert sig.parameters["error_code"].annotation == str
        assert sig.parameters["message"].annotation == str
        assert sig.parameters["status_code"].annotation == int
