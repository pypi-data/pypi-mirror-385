# ABOUTME: Test suite for HikuExtractor main API class
# ABOUTME: Tests initialization, extraction workflow, caching, and error handling

from unittest.mock import Mock, patch
import pytest
from pydantic import BaseModel


class SampleSchema(BaseModel):
    """Sample Pydantic schema for testing."""

    title: str
    content: str


class TestHikuExtractorInit:
    """Test HikuExtractor initialization."""

    def test_init_with_api_key_and_default_model(self):
        """Test initialization with API key uses default model."""
        from hikugen.extractor import HikuExtractor

        extractor = HikuExtractor(api_key="test-key")

        assert extractor.api_key == "test-key"
        assert extractor.model == "google/gemini-2.5-flash"

    def test_init_with_custom_model(self):
        """Test initialization with custom model."""
        from hikugen.extractor import HikuExtractor

        extractor = HikuExtractor(api_key="test-key", model="custom-model")

        assert extractor.api_key == "test-key"
        assert extractor.model == "custom-model"

    def test_init_with_custom_db_path(self):
        """Test initialization with custom database path."""
        from hikugen.extractor import HikuExtractor

        extractor = HikuExtractor(api_key="test-key", db_path="custom.db")

        assert extractor.db_path == "custom.db"

    def test_init_sets_up_database(self):
        """Test initialization creates database instance."""
        from hikugen.extractor import HikuExtractor

        extractor = HikuExtractor(api_key="test-key")

        assert hasattr(extractor, "database")
        assert extractor.database is not None

    def test_init_sets_up_code_generator(self):
        """Test initialization creates code generator instance."""
        from hikugen.extractor import HikuExtractor

        extractor = HikuExtractor(api_key="test-key", model="test-model")

        assert hasattr(extractor, "code_generator")
        assert extractor.code_generator is not None


class TestHikuExtractorSingleURL:
    """Test single URL extraction workflow."""

    @patch("hikugen.extractor.fetch_page_content")
    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_extract_single_url_cache_miss_full_workflow(
        self, mock_gen_class, mock_db_class, mock_fetch
    ):
        """Test extract() with cache miss runs full workflow."""
        from hikugen.extractor import HikuExtractor

        mock_db = Mock()
        mock_db.get_cached_code.return_value = None
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator.generate_extraction_code.return_value = ("code", True)
        mock_result = SampleSchema(title="Test", content="Content")
        mock_generator.execute_extraction_code.return_value = mock_result
        mock_generator.check_data_quality_with_llm.return_value = (True, [])
        mock_gen_class.return_value = mock_generator

        mock_fetch.return_value = "<html>Test</html>"

        extractor = HikuExtractor(api_key="test-key")
        result = extractor.extract(
            url="https://example.com", schema=SampleSchema
        )

        assert result == mock_result
        mock_db.get_cached_code.assert_called_once()
        mock_fetch.assert_called_once_with(
            "https://example.com", cookies_path=None, timeout=10
        )
        mock_generator.generate_extraction_code.assert_called_once()
        mock_generator.execute_extraction_code.assert_called_once()
        mock_db.save_extraction_code.assert_called_once()

    @patch("hikugen.extractor.fetch_page_content")
    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_extract_single_url_cache_hit_skips_generation(
        self, mock_gen_class, mock_db_class, mock_fetch
    ):
        """Test extract() with cache hit skips code generation."""
        from hikugen.extractor import HikuExtractor

        cached_code = "cached extraction code"
        mock_db = Mock()
        mock_db.get_cached_code.return_value = {"extraction_code": cached_code}
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_result = SampleSchema(title="Cached", content="Data")
        mock_generator.execute_extraction_code.return_value = mock_result
        mock_gen_class.return_value = mock_generator

        mock_fetch.return_value = "<html>Test</html>"

        extractor = HikuExtractor(api_key="test-key")
        result = extractor.extract(
            url="https://example.com", schema=SampleSchema
        )

        assert result == mock_result
        mock_db.get_cached_code.assert_called_once()
        mock_fetch.assert_called_once()
        mock_generator.generate_extraction_code.assert_not_called()
        mock_generator.execute_extraction_code.assert_called_once_with(
            code=cached_code,
            html_content="<html>Test</html>",
            schema=SampleSchema,
        )
        mock_db.save_extraction_code.assert_not_called()

    @patch("hikugen.extractor.fetch_page_content")
    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_extract_returns_pydantic_instance(
        self, mock_gen_class, mock_db_class, mock_fetch
    ):
        """Test extract() returns Pydantic BaseModel instance."""
        from hikugen.extractor import HikuExtractor

        mock_db = Mock()
        mock_db.get_cached_code.return_value = None
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator.generate_extraction_code.return_value = ("code", True)
        mock_result = SampleSchema(title="Test", content="Content")
        mock_generator.execute_extraction_code.return_value = mock_result
        mock_generator.check_data_quality_with_llm.return_value = (True, [])
        mock_gen_class.return_value = mock_generator

        mock_fetch.return_value = "<html>Test</html>"

        extractor = HikuExtractor(api_key="test-key")
        result = extractor.extract(
            url="https://example.com", schema=SampleSchema
        )

        assert isinstance(result, BaseModel)
        assert isinstance(result, SampleSchema)
        assert result.title == "Test"
        assert result.content == "Content"

    @patch("hikugen.extractor.fetch_page_content")
    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_extract_with_cookies_path(self, mock_gen_class, mock_db_class, mock_fetch):
        """Test extract() passes cookies_path to fetch function."""
        from hikugen.extractor import HikuExtractor

        mock_db = Mock()
        mock_db.get_cached_code.return_value = None
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator.generate_extraction_code.return_value = ("code", True)
        mock_result = SampleSchema(title="Test", content="Content")
        mock_generator.execute_extraction_code.return_value = mock_result
        mock_generator.check_data_quality_with_llm.return_value = (True, [])
        mock_gen_class.return_value = mock_generator

        mock_fetch.return_value = "<html>Test</html>"

        extractor = HikuExtractor(api_key="test-key")
        extractor.extract(
            url="https://example.com",
            schema=SampleSchema,
            cookies_path="/path/to/cookies.txt",
        )

        mock_fetch.assert_called_once_with(
            "https://example.com", cookies_path="/path/to/cookies.txt", timeout=10
        )

    @patch("hikugen.extractor.fetch_page_content")
    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_extract_error_handling_for_invalid_url(
        self, mock_gen_class, mock_db_class, mock_fetch
    ):
        """Test extract() handles HTTP errors gracefully."""
        from hikugen.extractor import HikuExtractor
        import requests

        mock_db = Mock()
        mock_db.get_cached_code.return_value = None
        mock_db_class.return_value = mock_db

        mock_gen_class.return_value = Mock()
        mock_fetch.side_effect = requests.exceptions.HTTPError("404 Not Found")

        extractor = HikuExtractor(api_key="test-key")

        with pytest.raises(requests.exceptions.HTTPError):
            extractor.extract(
                url="https://example.com/404", schema=SampleSchema
            )


class TestHikuExtractorEdgeCases:
    """Test edge cases and error scenarios."""

    @patch("hikugen.extractor.fetch_page_content")
    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_extract_with_different_urls_uses_different_cache_keys(
        self, mock_gen_class, mock_db_class, mock_fetch
    ):
        """Test extract() uses different cache keys for different URLs."""
        from hikugen.extractor import HikuExtractor

        mock_db = Mock()
        mock_db.get_cached_code.return_value = None
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator.generate_extraction_code.return_value = ("code", True)
        mock_generator.execute_extraction_code.return_value = SampleSchema(
            title="Test", content="Data"
        )
        mock_generator.check_data_quality_with_llm.return_value = (True, [])
        mock_gen_class.return_value = mock_generator

        mock_fetch.return_value = "<html>Test</html>"

        extractor = HikuExtractor(api_key="test-key")

        result1 = extractor.extract(url="https://example.com/1", schema=SampleSchema)
        result2 = extractor.extract(url="https://example.com/2", schema=SampleSchema)

        assert result1 == SampleSchema(title="Test", content="Data")
        assert result2 == SampleSchema(title="Test", content="Data")
        assert mock_fetch.call_count == 2
        assert mock_db.get_cached_code.call_count == 2


class TestHikuExtractorCacheParameter:
    """Test cache parameter functionality."""

    @patch("hikugen.extractor.fetch_page_content")
    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_extract_with_cache_false_bypasses_cache(
        self, mock_gen_class, mock_db_class, mock_fetch
    ):
        """Test extract() with use_cached_code=False bypasses cache lookup."""
        from hikugen.extractor import HikuExtractor

        mock_db = Mock()
        mock_db.get_cached_code.return_value = {"extraction_code": "cached"}
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator.generate_extraction_code.return_value = ("new_code", True)
        mock_generator.execute_extraction_code.return_value = SampleSchema(
            title="Test", content="Data"
        )
        mock_generator.check_data_quality_with_llm.return_value = (True, [])
        mock_gen_class.return_value = mock_generator

        mock_fetch.return_value = "<html>Test</html>"

        extractor = HikuExtractor(api_key="test-key")
        extractor.extract(
            url="https://example.com", schema=SampleSchema, use_cached_code=False
        )

        mock_db.get_cached_code.assert_not_called()
        mock_generator.generate_extraction_code.assert_called_once()
        mock_db.save_extraction_code.assert_called_once()

    @patch("hikugen.extractor.fetch_page_content")
    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_extract_with_cache_true_uses_cache(
        self, mock_gen_class, mock_db_class, mock_fetch
    ):
        """Test extract() with use_cached_code=True uses cache by default."""
        from hikugen.extractor import HikuExtractor

        cached_code = "cached extraction code"
        mock_db = Mock()
        mock_db.get_cached_code.return_value = {"extraction_code": cached_code}
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator.execute_extraction_code.return_value = SampleSchema(
            title="Test", content="Data"
        )
        mock_gen_class.return_value = mock_generator

        mock_fetch.return_value = "<html>Test</html>"

        extractor = HikuExtractor(api_key="test-key")
        extractor.extract(
            url="https://example.com", schema=SampleSchema, use_cached_code=True
        )

        mock_db.get_cached_code.assert_called_once()
        mock_generator.generate_extraction_code.assert_not_called()


class TestAutoRegeneration:
    """Test auto-regeneration with code reuse."""

    @patch("hikugen.extractor.fetch_page_content")
    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_cached_failure_regenerates(
        self, mock_gen_class, mock_db_class, mock_fetch
    ):
        """Test cached code failure triggers regeneration."""
        from hikugen.extractor import HikuExtractor

        mock_db = Mock()
        mock_db.get_cached_code.return_value = {"extraction_code": "old_code"}
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        # First execution fails, second succeeds
        mock_generator.execute_extraction_code.side_effect = [
            RuntimeError("Cached code failed"),
            SampleSchema(title="Success", content="Data"),
        ]
        mock_generator.regenerate_code.return_value = ("new_code", True)
        mock_generator.check_data_quality_with_llm.return_value = (True, [])
        mock_gen_class.return_value = mock_generator

        mock_fetch.return_value = "<html>Test</html>"

        extractor = HikuExtractor(api_key="test-key")
        result = extractor.extract(
            url="https://example.com",
            schema=SampleSchema,
            max_regenerate_attempts=1,
        )

        assert mock_generator.regenerate_code.call_count == 1
        assert mock_generator.execute_extraction_code.call_count == 2
        assert result.title == "Success"

    @patch("hikugen.extractor.fetch_page_content")
    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_quality_failure_regenerates(
        self, mock_gen_class, mock_db_class, mock_fetch
    ):
        """Test quality check failure triggers regeneration."""
        from hikugen.extractor import HikuExtractor

        mock_db = Mock()
        mock_db.get_cached_code.return_value = None
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator.generate_extraction_code.return_value = ("code", True)
        mock_generator.execute_extraction_code.return_value = SampleSchema(
            title="Test", content="Data"
        )
        # Quality check fails first, passes second
        mock_generator.check_data_quality_with_llm.side_effect = [
            (False, ["title is empty"]),
            (True, []),
        ]
        mock_generator.regenerate_code.return_value = ("new_code", True)
        mock_gen_class.return_value = mock_generator

        mock_fetch.return_value = "<html>Test</html>"

        extractor = HikuExtractor(api_key="test-key")
        extractor.extract(
            url="https://example.com",
            schema=SampleSchema,
            validate_quality=True,
        )

        assert mock_generator.check_data_quality_with_llm.call_count == 2
        assert mock_generator.regenerate_code.call_count == 1

    @patch("hikugen.extractor.fetch_page_content")
    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_max_regenerate_zero_raises_immediately(self, mock_gen_class, mock_db_class, mock_fetch):
        """Test max_regenerate_attempts=0 raises immediately on failure."""
        from hikugen.extractor import HikuExtractor

        mock_db = Mock()
        mock_db.get_cached_code.return_value = {"extraction_code": "code"}
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator.execute_extraction_code.side_effect = RuntimeError("Fail")
        mock_gen_class.return_value = mock_generator

        mock_fetch.return_value = "<html>Test</html>"

        extractor = HikuExtractor(api_key="test-key")

        with pytest.raises(RuntimeError):
            extractor.extract(
                url="https://example.com",
                schema=SampleSchema,
                max_regenerate_attempts=0,
            )

        mock_generator.regenerate_code.assert_not_called()


class TestExtractFromHtml:
    """Test extract_from_html() API method."""

    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_extract_from_html_basic(self, mock_gen_class, mock_db_class):
        """Test extract_from_html() extracts data from provided HTML."""
        from hikugen.extractor import HikuExtractor

        mock_db = Mock()
        mock_db.get_cached_code.return_value = None
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator.generate_extraction_code.return_value = ("code", True)
        mock_result = SampleSchema(title="Extracted", content="Data from HTML")
        mock_generator.execute_extraction_code.return_value = mock_result
        mock_generator.check_data_quality_with_llm.return_value = (True, [])
        mock_gen_class.return_value = mock_generator

        extractor = HikuExtractor(api_key="test-key")
        html = "<html><body>Test content</body></html>"
        result = extractor.extract_from_html(
            html_content=html,
            name="test_extraction",
            schema=SampleSchema,
        )

        assert result == mock_result
        mock_generator.generate_extraction_code.assert_called_once()
        mock_generator.execute_extraction_code.assert_called_once()
        mock_db.save_extraction_code.assert_called_once()

    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_extract_from_html_uses_name_as_cache_key(self, mock_gen_class, mock_db_class):
        """Test extract_from_html() uses name parameter as cache key."""
        from hikugen.extractor import HikuExtractor

        mock_db = Mock()
        mock_db.get_cached_code.return_value = None
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator.generate_extraction_code.return_value = ("code", True)
        mock_generator.execute_extraction_code.return_value = SampleSchema(
            title="Test", content="Data"
        )
        mock_generator.check_data_quality_with_llm.return_value = (True, [])
        mock_gen_class.return_value = mock_generator

        extractor = HikuExtractor(api_key="test-key")
        extractor.extract_from_html(
            html_content="<html>test</html>",
            name="my_custom_task",
            schema=SampleSchema,
        )

        # Verify cache key uses the name parameter
        call_args = mock_db.get_cached_code.call_args
        assert call_args[0][0] == "my_custom_task"

        save_call_args = mock_db.save_extraction_code.call_args
        assert save_call_args[0][0] == "my_custom_task"

    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_extract_from_html_cache_hit(self, mock_gen_class, mock_db_class):
        """Test extract_from_html() uses cached code when available."""
        from hikugen.extractor import HikuExtractor

        cached_code = "cached extraction code"
        mock_db = Mock()
        mock_db.get_cached_code.return_value = {"extraction_code": cached_code}
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_result = SampleSchema(title="Cached", content="Result")
        mock_generator.execute_extraction_code.return_value = mock_result
        mock_gen_class.return_value = mock_generator

        extractor = HikuExtractor(api_key="test-key")
        result = extractor.extract_from_html(
            html_content="<html>test</html>",
            name="cached_task",
            schema=SampleSchema,
        )

        assert result == mock_result
        mock_generator.generate_extraction_code.assert_not_called()
        mock_generator.execute_extraction_code.assert_called_once_with(
            code=cached_code,
            html_content="<html>test</html>",
            schema=SampleSchema,
        )
        mock_db.save_extraction_code.assert_not_called()

    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_extract_from_html_different_names_different_cache(
        self, mock_gen_class, mock_db_class
    ):
        """Test different names create separate cache entries."""
        from hikugen.extractor import HikuExtractor

        mock_db = Mock()
        mock_db.get_cached_code.return_value = None
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator.generate_extraction_code.return_value = ("code", True)
        mock_generator.execute_extraction_code.return_value = SampleSchema(
            title="Test", content="Data"
        )
        mock_generator.check_data_quality_with_llm.return_value = (True, [])
        mock_gen_class.return_value = mock_generator

        extractor = HikuExtractor(api_key="test-key")
        html = "<html>same content</html>"

        extractor.extract_from_html(html_content=html, name="task1", schema=SampleSchema)
        extractor.extract_from_html(html_content=html, name="task2", schema=SampleSchema)

        # Verify different cache keys were used
        cache_get_calls = mock_db.get_cached_code.call_args_list
        assert cache_get_calls[0][0][0] == "task1"
        assert cache_get_calls[1][0][0] == "task2"

    @patch("hikugen.extractor.HikuDatabase")
    @patch("hikugen.extractor.HikuCodeGenerator")
    def test_extract_from_html_supports_regeneration(self, mock_gen_class, mock_db_class):
        """Test extract_from_html() supports regeneration on failure."""
        from hikugen.extractor import HikuExtractor

        mock_db = Mock()
        mock_db.get_cached_code.return_value = None
        mock_db_class.return_value = mock_db

        mock_generator = Mock()
        mock_generator.generate_extraction_code.return_value = ("code", True)
        # First fails, second succeeds
        mock_generator.execute_extraction_code.side_effect = [
            RuntimeError("Initial fail"),
            SampleSchema(title="Success", content="Data"),
        ]
        mock_generator.regenerate_code.return_value = ("new_code", True)
        mock_generator.check_data_quality_with_llm.return_value = (True, [])
        mock_gen_class.return_value = mock_generator

        extractor = HikuExtractor(api_key="test-key")
        result = extractor.extract_from_html(
            html_content="<html>test</html>",
            name="regen_test",
            schema=SampleSchema,
            max_regenerate_attempts=1,
        )

        assert result.title == "Success"
        assert mock_generator.regenerate_code.call_count == 1
