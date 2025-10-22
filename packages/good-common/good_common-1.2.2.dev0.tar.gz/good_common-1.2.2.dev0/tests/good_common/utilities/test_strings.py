"""Tests for good_common.utilities._strings module."""

import pytest

from good_common.utilities._strings import (
    is_uuid,
    camel_to_slug,
    camel_to_snake,
    camel_to_kebab,
    snake_to_camel,
    snake_to_kebab,
    kebab_to_camel,
    kebab_to_snake,
    slug_to_camel,
    slug_to_snake,
    slug_to_kebab,
    detect_string_type,
    encode_base32,
)


class TestUUIDValidation:
    """Test UUID validation function."""

    def test_is_uuid_valid(self):
        """Test valid UUID strings."""
        valid_uuids = [
            "550e8400-e29b-41d4-a716-446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "00000000-0000-0000-0000-000000000000",
        ]
        
        for uuid_str in valid_uuids:
            assert is_uuid(uuid_str) is True

    def test_is_uuid_invalid(self):
        """Test invalid UUID strings."""
        invalid_uuids = [
            "not-a-uuid",
            "550e8400-e29b-41d4-a716",
            "550e8400e29b41d4a716446655440000",  # Missing hyphens
            "",
            "xyz-xyz-xyz-xyz",
        ]
        
        for uuid_str in invalid_uuids:
            assert is_uuid(uuid_str) is False


class TestCasingConversions:
    """Test string casing conversion functions."""

    def test_camel_to_slug(self):
        """Test camelCase to slug conversion."""
        assert camel_to_slug("CamelCase") == "camel-case"
        assert camel_to_slug("myVariableName") == "my-variable-name"
        assert camel_to_slug("HTTPSConnection") == "https-connection"
        assert camel_to_slug("CamelCase", force_lower=False) == "Camel-Case"

    def test_camel_to_snake(self):
        """Test camelCase to snake_case conversion."""
        assert camel_to_snake("CamelCase") == "camel_case"
        assert camel_to_snake("myVariableName") == "my_variable_name"
        assert camel_to_snake("HTTPSConnection") == "https_connection"
        assert camel_to_snake("IOError") == "io_error"

    def test_camel_to_kebab(self):
        """Test camelCase to kebab-case conversion."""
        assert camel_to_kebab("CamelCase") == "camel-case"
        assert camel_to_kebab("myVariableName") == "my-variable-name"
        assert camel_to_kebab("HTTPSConnection") == "https-connection"
        
    def test_camel_to_kebab_with_protected_acronyms(self):
        """Test camelCase to kebab with protected acronyms."""
        assert camel_to_kebab("HTTPSConnection", ["HTTPS"]) == "HTTPS-connection"
        assert camel_to_kebab("XMLHttpRequest", ["XML", "Http"]) == "XML-Http-request"

    def test_snake_to_camel(self):
        """Test snake_case to camelCase conversion."""
        assert snake_to_camel("snake_case") == "snakeCase"
        assert snake_to_camel("my_variable_name") == "myVariableName"
        assert snake_to_camel("https_connection") == "httpsConnection"
        assert snake_to_camel("_private_var") == "PrivateVar"

    def test_snake_to_kebab(self):
        """Test snake_case to kebab-case conversion."""
        assert snake_to_kebab("snake_case") == "snake-case"
        assert snake_to_kebab("my_variable_name") == "my-variable-name"
        assert snake_to_kebab("https_connection") == "https-connection"

    def test_kebab_to_camel(self):
        """Test kebab-case to camelCase conversion."""
        assert kebab_to_camel("kebab-case") == "kebabCase"
        assert kebab_to_camel("my-variable-name") == "myVariableName"
        assert kebab_to_camel("https-connection") == "httpsConnection"

    def test_kebab_to_snake(self):
        """Test kebab-case to snake_case conversion."""
        assert kebab_to_snake("kebab-case") == "kebab_case"
        assert kebab_to_snake("my-variable-name") == "my_variable_name"
        assert kebab_to_snake("https-connection") == "https_connection"

    def test_slug_to_camel(self):
        """Test slug to camelCase conversion."""
        assert slug_to_camel("slug-case") == "slugCase"
        assert slug_to_camel("my-slug-name") == "mySlugName"
        assert slug_to_camel("api-key") == "apiKey"

    def test_slug_to_snake(self):
        """Test slug to snake_case conversion."""
        assert slug_to_snake("slug-case") == "slug_case"
        assert slug_to_snake("my-slug-name") == "my_slug_name"
        assert slug_to_snake("api-key") == "api_key"


class TestSlugConversions:
    """Test slug conversion functions."""

    def test_slug_to_kebab(self):
        """Test slug to kebab-case conversion."""
        assert slug_to_kebab("slug_case") == "slug-case"
        assert slug_to_kebab("my_slug_name") == "my-slug-name"
        assert slug_to_kebab("api_key") == "api-key"


class TestStringType:
    """Test string type detection."""

    def test_detect_string_type(self):
        """Test string type detection."""
        assert detect_string_type("CamelCase") == "camelCase" 
        assert detect_string_type("snake_case") == "snake_case"
        assert detect_string_type("kebab-case") == "kebab-case"
        assert detect_string_type("regular text") == "unknown"


class TestBase32:
    """Test base32 encoding function."""

    def test_encode_base32(self):
        """Test base32 encoding."""
        result = encode_base32("Hello World")
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Test with bytes
        result_bytes = encode_base32(b"Hello World")
        assert isinstance(result_bytes, str)
        assert result == result_bytes