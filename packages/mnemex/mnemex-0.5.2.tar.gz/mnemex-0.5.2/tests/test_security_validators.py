"""Comprehensive tests for security.validators module."""

import pytest

from mnemex.security.validators import (
    ALLOWED_RELATION_TYPES,
    ALLOWED_TARGETS,
    MAX_CONTENT_LENGTH,
    MAX_LIST_LENGTH,
    MAX_TAG_LENGTH,
    validate_entity,
    validate_list_length,
    validate_positive_int,
    validate_relation_type,
    validate_score,
    validate_string_length,
    validate_tag,
    validate_target,
    validate_uuid,
)


class TestValidateUuid:
    """Tests for validate_uuid function."""

    def test_valid_uuid_lowercase(self):
        """Test valid lowercase UUIDs."""
        uuid1 = "123e4567-e89b-12d3-a456-426614174000"
        assert validate_uuid(uuid1) == uuid1.lower()

        uuid2 = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        assert validate_uuid(uuid2) == uuid2.lower()

    def test_valid_uuid_uppercase(self):
        """Test valid uppercase UUIDs are converted to lowercase."""
        uuid_upper = "123E4567-E89B-12D3-A456-426614174000"
        expected = "123e4567-e89b-12d3-a456-426614174000"
        assert validate_uuid(uuid_upper) == expected

    def test_valid_uuid_mixed_case(self):
        """Test valid mixed-case UUIDs are converted to lowercase."""
        uuid_mixed = "123e4567-E89B-12d3-A456-426614174000"
        expected = "123e4567-e89b-12d3-a456-426614174000"
        assert validate_uuid(uuid_mixed) == expected

    def test_valid_uuid_with_hyphens(self):
        """Test valid UUIDs with proper hyphen placement."""
        uuid_valid = "550e8400-e29b-41d4-a716-446655440000"
        assert validate_uuid(uuid_valid) == uuid_valid

    def test_invalid_uuid_too_short(self):
        """Test rejection of UUIDs that are too short."""
        with pytest.raises(ValueError, match="must be a valid UUID"):
            validate_uuid("123e4567-e89b-12d3-a456")

    def test_invalid_uuid_too_long(self):
        """Test rejection of UUIDs that are too long."""
        with pytest.raises(ValueError, match="must be a valid UUID"):
            validate_uuid("123e4567-e89b-12d3-a456-426614174000-extra")

    def test_invalid_uuid_wrong_characters(self):
        """Test rejection of UUIDs with invalid characters."""
        with pytest.raises(ValueError, match="must be a valid UUID"):
            validate_uuid("123g4567-e89b-12d3-a456-426614174000")

        with pytest.raises(ValueError, match="must be a valid UUID"):
            validate_uuid("123e4567-e89b-12d3-a456-42661417400z")

    def test_invalid_uuid_no_hyphens(self):
        """Test rejection of UUIDs without hyphens."""
        with pytest.raises(ValueError, match="must be a valid UUID"):
            validate_uuid("123e4567e89b12d3a456426614174000")

    def test_invalid_uuid_wrong_hyphen_placement(self):
        """Test rejection of UUIDs with wrong hyphen placement."""
        with pytest.raises(ValueError, match="must be a valid UUID"):
            validate_uuid("123e456-7e89b-12d3-a456-426614174000")

    def test_non_string_input_integer(self):
        """Test rejection of non-string inputs (integer)."""
        with pytest.raises(ValueError, match="must be a string, got int"):
            validate_uuid(12345)

    def test_non_string_input_none(self):
        """Test rejection of None input."""
        with pytest.raises(ValueError, match="must be a string, got NoneType"):
            validate_uuid(None)

    def test_non_string_input_list(self):
        """Test rejection of list input."""
        with pytest.raises(ValueError, match="must be a string, got list"):
            validate_uuid(["123e4567-e89b-12d3-a456-426614174000"])

    def test_empty_string(self):
        """Test rejection of empty string."""
        with pytest.raises(ValueError, match="must be a valid UUID"):
            validate_uuid("")

    def test_custom_field_name_in_errors(self):
        """Test that custom field_name appears in error messages."""
        with pytest.raises(ValueError, match="user_id"):
            validate_uuid("invalid", field_name="user_id")

        with pytest.raises(ValueError, match="memory_uuid"):
            validate_uuid(123, field_name="memory_uuid")

    def test_uuid_truncation_in_error_message(self):
        """Test that very long invalid UUIDs are truncated in error messages."""
        long_invalid = "x" * 100
        with pytest.raises(ValueError, match=r"\.\.\."):
            validate_uuid(long_invalid)


class TestValidateStringLength:
    """Tests for validate_string_length function."""

    def test_valid_string_within_limit(self):
        """Test valid strings within length limits."""
        assert validate_string_length("hello", 10) == "hello"
        assert validate_string_length("test string", 50) == "test string"
        assert validate_string_length("a" * 100, 100) == "a" * 100

    def test_valid_string_at_exact_limit(self):
        """Test strings at exact length limit."""
        assert validate_string_length("a" * 50, 50) == "a" * 50

    def test_empty_string_allow_empty_true(self):
        """Test empty strings with allow_empty=True."""
        assert validate_string_length("", 10, allow_empty=True) == ""

    def test_empty_string_allow_empty_false(self):
        """Test empty strings with allow_empty=False."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_string_length("", 10, allow_empty=False)

    def test_string_too_long(self):
        """Test rejection of strings exceeding max_length."""
        with pytest.raises(
            ValueError, match=r"exceeds maximum length of 10 characters \(got 15 characters\)"
        ):
            validate_string_length("a" * 15, 10)

    def test_string_exceeds_max_content_length(self):
        """Test rejection of very long strings."""
        long_string = "x" * (MAX_CONTENT_LENGTH + 1)
        with pytest.raises(ValueError, match="exceeds maximum length"):
            validate_string_length(long_string, MAX_CONTENT_LENGTH)

    def test_non_string_input_integer(self):
        """Test rejection of non-string inputs (integer)."""
        with pytest.raises(ValueError, match="must be a string, got int"):
            validate_string_length(123, 10)

    def test_non_string_input_list(self):
        """Test rejection of list input."""
        with pytest.raises(ValueError, match="must be a string, got list"):
            validate_string_length(["test"], 10)

    def test_none_with_allow_none_true(self):
        """Test None input with allow_none=True."""
        assert validate_string_length(None, 10, allow_none=True) is None

    def test_none_with_allow_none_false(self):
        """Test None input with allow_none=False."""
        with pytest.raises(ValueError, match="cannot be None"):
            validate_string_length(None, 10, allow_none=False)

    def test_custom_field_name_in_errors(self):
        """Test that custom field_name appears in error messages."""
        with pytest.raises(ValueError, match="content"):
            validate_string_length("a" * 100, 10, field_name="content")

        with pytest.raises(ValueError, match="title"):
            validate_string_length("", 10, field_name="title", allow_empty=False)

    def test_length_formatting_with_commas(self):
        """Test that large numbers are formatted with commas in error messages."""
        with pytest.raises(ValueError, match=r"1,000"):
            validate_string_length("a" * 2000, 1000)


class TestValidatePositiveInt:
    """Tests for validate_positive_int function."""

    def test_valid_positive_integers(self):
        """Test valid positive integers."""
        assert validate_positive_int(1) == 1
        assert validate_positive_int(42) == 42
        assert validate_positive_int(1000) == 1000

    def test_zero_with_default_min(self):
        """Test rejection of zero with default min_value=1."""
        with pytest.raises(ValueError, match="must be >= 1, got 0"):
            validate_positive_int(0)

    def test_zero_with_custom_min_zero(self):
        """Test acceptance of zero with min_value=0."""
        assert validate_positive_int(0, min_value=0) == 0

    def test_negative_numbers(self):
        """Test rejection of negative numbers."""
        with pytest.raises(ValueError, match="must be >= 1, got -1"):
            validate_positive_int(-1)

        with pytest.raises(ValueError, match="must be >= 1, got -100"):
            validate_positive_int(-100)

    def test_non_integer_input_float(self):
        """Test rejection of float inputs."""
        with pytest.raises(ValueError, match="must be an integer, got float"):
            validate_positive_int(3.14)

        with pytest.raises(ValueError, match="must be an integer, got float"):
            validate_positive_int(1.0)

    def test_non_integer_input_string(self):
        """Test rejection of string inputs."""
        with pytest.raises(ValueError, match="must be an integer, got str"):
            validate_positive_int("42")

    def test_non_integer_input_boolean(self):
        """Test rejection of boolean inputs (bool is subclass of int in Python)."""
        with pytest.raises(ValueError, match="must be an integer, got bool"):
            validate_positive_int(True)

        with pytest.raises(ValueError, match="must be an integer, got bool"):
            validate_positive_int(False)

    def test_custom_min_value(self):
        """Test custom min_value parameter."""
        assert validate_positive_int(10, min_value=10) == 10
        assert validate_positive_int(100, min_value=50) == 100

        with pytest.raises(ValueError, match="must be >= 10, got 5"):
            validate_positive_int(5, min_value=10)

    def test_custom_max_value(self):
        """Test custom max_value parameter."""
        assert validate_positive_int(50, max_value=100) == 50
        assert validate_positive_int(100, max_value=100) == 100

        with pytest.raises(ValueError, match="must be <= 100, got 150"):
            validate_positive_int(150, max_value=100)

    def test_custom_min_and_max_value(self):
        """Test custom min and max values together."""
        assert validate_positive_int(50, min_value=10, max_value=100) == 50

        with pytest.raises(ValueError, match="must be >= 10"):
            validate_positive_int(5, min_value=10, max_value=100)

        with pytest.raises(ValueError, match="must be <= 100"):
            validate_positive_int(150, min_value=10, max_value=100)

    def test_custom_field_name_in_errors(self):
        """Test that custom field_name appears in error messages."""
        with pytest.raises(ValueError, match="limit"):
            validate_positive_int(0, field_name="limit")

        with pytest.raises(ValueError, match="count"):
            validate_positive_int("invalid", field_name="count")

    def test_large_positive_integer(self):
        """Test very large positive integers."""
        large_int = 10**10
        assert validate_positive_int(large_int) == large_int


class TestValidateScore:
    """Tests for validate_score function."""

    def test_valid_scores_in_range(self):
        """Test valid scores within [0.0, 1.0] range."""
        assert validate_score(0.5) == 0.5
        assert validate_score(0.75) == 0.75
        assert validate_score(0.123456) == 0.123456

    def test_edge_case_zero(self):
        """Test edge case of exactly 0.0."""
        assert validate_score(0.0) == 0.0

    def test_edge_case_one(self):
        """Test edge case of exactly 1.0."""
        assert validate_score(1.0) == 1.0

    def test_integer_zero_accepted(self):
        """Test integer 0 is accepted and converted to float."""
        result = validate_score(0)
        assert result == 0.0
        assert isinstance(result, float)

    def test_integer_one_accepted(self):
        """Test integer 1 is accepted and converted to float."""
        result = validate_score(1)
        assert result == 1.0
        assert isinstance(result, float)

    def test_negative_score(self):
        """Test rejection of negative scores."""
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0, got -0.1"):
            validate_score(-0.1)

        with pytest.raises(ValueError, match="must be between 0.0 and 1.0, got -1.0"):
            validate_score(-1.0)

    def test_score_greater_than_one(self):
        """Test rejection of scores > 1.0."""
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0, got 1.1"):
            validate_score(1.1)

        with pytest.raises(ValueError, match="must be between 0.0 and 1.0, got 2.5"):
            validate_score(2.5)

    def test_non_numeric_input_string(self):
        """Test rejection of non-numeric inputs (string)."""
        with pytest.raises(ValueError, match="must be a number, got str"):
            validate_score("0.5")

    def test_non_numeric_input_none(self):
        """Test rejection of None input."""
        with pytest.raises(ValueError, match="must be a number, got NoneType"):
            validate_score(None)

    def test_non_numeric_input_list(self):
        """Test rejection of list input."""
        with pytest.raises(ValueError, match="must be a number, got list"):
            validate_score([0.5])

    def test_custom_field_name_in_errors(self):
        """Test that custom field_name appears in error messages."""
        with pytest.raises(ValueError, match="confidence"):
            validate_score(1.5, field_name="confidence")

        with pytest.raises(ValueError, match="importance"):
            validate_score("invalid", field_name="importance")


class TestValidateTag:
    """Tests for validate_tag function."""

    def test_valid_tags_alphanumeric(self):
        """Test valid alphanumeric tags."""
        assert validate_tag("tag") == "tag"
        assert validate_tag("tag123") == "tag123"
        assert validate_tag("TAG") == "TAG"

    def test_valid_tags_with_hyphens(self):
        """Test valid tags with hyphens."""
        assert validate_tag("my-tag") == "my-tag"
        assert validate_tag("machine-learning") == "machine-learning"

    def test_valid_tags_with_underscores(self):
        """Test valid tags with underscores."""
        assert validate_tag("my_tag") == "my_tag"
        assert validate_tag("python_code") == "python_code"

    def test_valid_tags_mixed_allowed_characters(self):
        """Test valid tags with mix of alphanumeric, hyphens, underscores."""
        assert validate_tag("my-tag_123") == "my-tag_123"
        assert validate_tag("ML-model_v2") == "ML-model_v2"

    def test_whitespace_stripped(self):
        """Test that leading/trailing whitespace is stripped."""
        assert validate_tag("  tag  ") == "tag"
        assert validate_tag("\ttag\t") == "tag"

    def test_invalid_characters_spaces(self):
        """Test rejection of tags with spaces."""
        with pytest.raises(ValueError, match="contains invalid characters"):
            validate_tag("my tag")

    def test_invalid_characters_special_chars(self):
        """Test rejection of tags with special characters."""
        with pytest.raises(ValueError, match="contains invalid characters"):
            validate_tag("tag!")

        with pytest.raises(ValueError, match="contains invalid characters"):
            validate_tag("tag@email")

        with pytest.raises(ValueError, match="contains invalid characters"):
            validate_tag("tag#hash")

    def test_empty_tag_after_strip(self):
        """Test rejection of empty tags after stripping."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_tag("")

        with pytest.raises(ValueError, match="cannot be empty"):
            validate_tag("   ")

    def test_tag_too_long(self):
        """Test rejection of tags exceeding MAX_TAG_LENGTH."""
        long_tag = "a" * (MAX_TAG_LENGTH + 1)
        with pytest.raises(ValueError, match=f"exceeds maximum length of {MAX_TAG_LENGTH}"):
            validate_tag(long_tag)

    def test_tag_at_max_length(self):
        """Test tags at exactly MAX_TAG_LENGTH are accepted."""
        max_tag = "a" * MAX_TAG_LENGTH
        assert validate_tag(max_tag) == max_tag

    def test_non_string_input(self):
        """Test rejection of non-string inputs."""
        with pytest.raises(ValueError, match="must be a string, got int"):
            validate_tag(123)

        with pytest.raises(ValueError, match="must be a string, got list"):
            validate_tag(["tag"])

    def test_custom_field_name_in_errors(self):
        """Test that custom field_name appears in error messages."""
        with pytest.raises(ValueError, match="category"):
            validate_tag("invalid tag", field_name="category")

        with pytest.raises(ValueError, match="label"):
            validate_tag("", field_name="label")

    def test_tag_truncation_in_error_message(self):
        """Test that long invalid tags are truncated in error messages."""
        long_invalid = "x" * 60 + " invalid"
        with pytest.raises(ValueError, match="Got:"):
            validate_tag(long_invalid)


class TestValidateEntity:
    """Tests for validate_entity function."""

    def test_valid_entities_alphanumeric(self):
        """Test valid alphanumeric entities."""
        assert validate_entity("entity") == "entity"
        assert validate_entity("Entity123") == "Entity123"

    def test_valid_entities_with_hyphens(self):
        """Test valid entities with hyphens."""
        assert validate_entity("my-entity") == "my-entity"
        assert validate_entity("project-alpha") == "project-alpha"

    def test_valid_entities_with_underscores(self):
        """Test valid entities with underscores."""
        assert validate_entity("user_123") == "user_123"

    def test_valid_entities_with_spaces(self):
        """Test valid entities with spaces."""
        assert validate_entity("Claude AI") == "Claude AI"
        assert validate_entity("Project Alpha") == "Project Alpha"

    def test_valid_entities_mixed_allowed_characters(self):
        """Test valid entities with mix of allowed characters."""
        assert validate_entity("My-Project_v2 Beta") == "My-Project_v2 Beta"

    def test_whitespace_stripped(self):
        """Test that leading/trailing whitespace is stripped."""
        assert validate_entity("  entity  ") == "entity"
        assert validate_entity("\tentity\t") == "entity"

    def test_multiple_spaces_normalized(self):
        """Test that multiple spaces are normalized to single space."""
        assert validate_entity("Claude  AI") == "Claude AI"
        assert validate_entity("Project   Alpha") == "Project Alpha"
        assert validate_entity("A    B    C") == "A B C"

    def test_invalid_characters_special_chars(self):
        """Test rejection of entities with invalid special characters."""
        with pytest.raises(ValueError, match="contains invalid characters"):
            validate_entity("entity!")

        with pytest.raises(ValueError, match="contains invalid characters"):
            validate_entity("entity@domain")

        with pytest.raises(ValueError, match="contains invalid characters"):
            validate_entity("entity#tag")

    def test_empty_entity_after_strip(self):
        """Test rejection of empty entities after stripping."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_entity("")

        with pytest.raises(ValueError, match="cannot be empty"):
            validate_entity("   ")

    def test_entity_too_long(self):
        """Test rejection of entities exceeding MAX_TAG_LENGTH."""
        long_entity = "a" * (MAX_TAG_LENGTH + 1)
        with pytest.raises(ValueError, match=f"exceeds maximum length of {MAX_TAG_LENGTH}"):
            validate_entity(long_entity)

    def test_entity_at_max_length(self):
        """Test entities at exactly MAX_TAG_LENGTH are accepted."""
        max_entity = "a" * MAX_TAG_LENGTH
        assert validate_entity(max_entity) == max_entity

    def test_non_string_input(self):
        """Test rejection of non-string inputs."""
        with pytest.raises(ValueError, match="must be a string, got int"):
            validate_entity(123)

        with pytest.raises(ValueError, match="must be a string, got dict"):
            validate_entity({"name": "entity"})

    def test_custom_field_name_in_errors(self):
        """Test that custom field_name appears in error messages."""
        with pytest.raises(ValueError, match="person"):
            validate_entity("invalid!", field_name="person")

        with pytest.raises(ValueError, match="project_name"):
            validate_entity("", field_name="project_name")

    def test_entity_truncation_in_error_message(self):
        """Test that long invalid entities are truncated in error messages."""
        long_invalid = "x" * 60 + "!"
        with pytest.raises(ValueError, match="Got:"):
            validate_entity(long_invalid)


class TestValidateListLength:
    """Tests for validate_list_length function."""

    def test_valid_empty_list(self):
        """Test valid empty list."""
        assert validate_list_length([], 10) == []

    def test_valid_list_within_limit(self):
        """Test valid lists within length limits."""
        assert validate_list_length([1, 2, 3], 10) == [1, 2, 3]
        assert validate_list_length(["a", "b"], 5) == ["a", "b"]

    def test_valid_list_at_exact_limit(self):
        """Test lists at exact length limit."""
        items = list(range(10))
        assert validate_list_length(items, 10) == items

    def test_list_too_long(self):
        """Test rejection of lists exceeding max_length."""
        long_list = list(range(20))
        with pytest.raises(
            ValueError, match=r"exceeds maximum length of 10 items \(got 20 items\)"
        ):
            validate_list_length(long_list, 10)

    def test_list_exceeds_max_list_length(self):
        """Test rejection of very long lists."""
        long_list = list(range(MAX_LIST_LENGTH + 1))
        with pytest.raises(ValueError, match="exceeds maximum length"):
            validate_list_length(long_list, MAX_LIST_LENGTH)

    def test_non_list_input_tuple(self):
        """Test rejection of non-list inputs (tuple)."""
        with pytest.raises(ValueError, match="must be a list, got tuple"):
            validate_list_length((1, 2, 3), 10)

    def test_non_list_input_string(self):
        """Test rejection of string input."""
        with pytest.raises(ValueError, match="must be a list, got str"):
            validate_list_length("not a list", 10)

    def test_non_list_input_dict(self):
        """Test rejection of dict input."""
        with pytest.raises(ValueError, match="must be a list, got dict"):
            validate_list_length({"key": "value"}, 10)

    def test_custom_field_name_in_errors(self):
        """Test that custom field_name appears in error messages."""
        with pytest.raises(ValueError, match="tags"):
            validate_list_length(list(range(20)), 10, field_name="tags")

        with pytest.raises(ValueError, match="memory_ids"):
            validate_list_length("not a list", 10, field_name="memory_ids")

    def test_list_with_various_types(self):
        """Test lists containing various types of items."""
        mixed_list = [1, "two", 3.0, None, {"key": "value"}]
        assert validate_list_length(mixed_list, 10) == mixed_list


class TestValidateRelationType:
    """Tests for validate_relation_type function."""

    def test_valid_relation_types(self):
        """Test all valid relation types from ALLOWED_RELATION_TYPES."""
        for rel_type in ALLOWED_RELATION_TYPES:
            assert validate_relation_type(rel_type) == rel_type

    def test_specific_valid_types(self):
        """Test specific known valid relation types."""
        assert validate_relation_type("related") == "related"
        assert validate_relation_type("causes") == "causes"
        assert validate_relation_type("supports") == "supports"
        assert validate_relation_type("contradicts") == "contradicts"
        assert validate_relation_type("has_decision") == "has_decision"
        assert validate_relation_type("consolidated_from") == "consolidated_from"

    def test_invalid_relation_type(self):
        """Test rejection of invalid relation types."""
        with pytest.raises(ValueError, match="must be one of"):
            validate_relation_type("unknown")

        with pytest.raises(ValueError, match="must be one of"):
            validate_relation_type("invalid_type")

    def test_empty_string(self):
        """Test rejection of empty string."""
        with pytest.raises(ValueError, match="must be one of"):
            validate_relation_type("")

    def test_case_sensitive(self):
        """Test that relation type validation is case-sensitive."""
        with pytest.raises(ValueError, match="must be one of"):
            validate_relation_type("RELATED")

        with pytest.raises(ValueError, match="must be one of"):
            validate_relation_type("Related")

    def test_non_string_input(self):
        """Test rejection of non-string inputs."""
        with pytest.raises(ValueError, match="must be a string, got int"):
            validate_relation_type(123)

        with pytest.raises(ValueError, match="must be a string, got list"):
            validate_relation_type(["related"])

    def test_custom_field_name_in_errors(self):
        """Test that custom field_name appears in error messages."""
        with pytest.raises(ValueError, match="rel_type"):
            validate_relation_type("invalid", field_name="rel_type")

        with pytest.raises(ValueError, match="relationship"):
            validate_relation_type(123, field_name="relationship")

    def test_error_message_shows_allowed_values(self):
        """Test that error message shows sorted allowed values."""
        with pytest.raises(ValueError, match="must be one of") as exc_info:
            validate_relation_type("invalid")

        error_message = str(exc_info.value)
        for rel_type in ALLOWED_RELATION_TYPES:
            assert rel_type in error_message


class TestValidateTarget:
    """Tests for validate_target function."""

    def test_valid_targets(self):
        """Test all valid targets from ALLOWED_TARGETS."""
        for target in ALLOWED_TARGETS:
            assert validate_target(target) == target

    def test_valid_obsidian_target(self):
        """Test the specific 'obsidian' target."""
        assert validate_target("obsidian") == "obsidian"

    def test_invalid_target(self):
        """Test rejection of invalid targets."""
        with pytest.raises(ValueError, match="must be one of"):
            validate_target("unknown")

        with pytest.raises(ValueError, match="must be one of"):
            validate_target("markdown")

    def test_empty_string(self):
        """Test rejection of empty string."""
        with pytest.raises(ValueError, match="must be one of"):
            validate_target("")

    def test_case_sensitive(self):
        """Test that target validation is case-sensitive."""
        with pytest.raises(ValueError, match="must be one of"):
            validate_target("OBSIDIAN")

        with pytest.raises(ValueError, match="must be one of"):
            validate_target("Obsidian")

    def test_non_string_input(self):
        """Test rejection of non-string inputs."""
        with pytest.raises(ValueError, match="must be a string, got int"):
            validate_target(123)

        with pytest.raises(ValueError, match="must be a string, got list"):
            validate_target(["obsidian"])

    def test_path_like_input_rejected(self):
        """Test rejection of path-like strings (target is not a path)."""
        with pytest.raises(ValueError, match="must be one of"):
            validate_target("/path/to/vault")

        with pytest.raises(ValueError, match="must be one of"):
            validate_target("./vault")

    def test_error_message_explains_target_vs_path(self):
        """Test that error message explains target is a backend, not a path."""
        with pytest.raises(ValueError, match="storage backend") as exc_info:
            validate_target("invalid")

        error_message = str(exc_info.value)
        assert "not a file path" in error_message
        assert "LTM_VAULT_PATH" in error_message

    def test_custom_field_name_in_errors(self):
        """Test that custom field_name appears in error messages."""
        with pytest.raises(ValueError, match="backend"):
            validate_target("invalid", field_name="backend")

        with pytest.raises(ValueError, match="storage_type"):
            validate_target(123, field_name="storage_type")

    def test_error_message_shows_allowed_values(self):
        """Test that error message shows sorted allowed values."""
        with pytest.raises(ValueError, match="must be one of") as exc_info:
            validate_target("invalid")

        error_message = str(exc_info.value)
        for target in ALLOWED_TARGETS:
            assert target in error_message
