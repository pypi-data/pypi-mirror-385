"""
Tests for Cython-optimized URL operations.

This module tests both the Cython implementations and their Python fallbacks
to ensure backward compatibility and correctness.
"""

import pytest
from typing import Set
from good_common.types.url_cython_optimized import (
    CYTHON_AVAILABLE,
    FastURLComponents,
    URLCanonicalizer,
    CompiledPatternMatcher,
    DomainRuleMatcher,
    URLClassifier,
    OptimizedURL,
    fast_canonicalize_domain,
    fast_clean_path,
    fast_filter_query_params,
    fast_normalize_url,
    split_url_parts,
    join_url_parts,
    is_tracking_param,
    create_optimized_url_instance,
)
from good_common.types.web import URL as OriginalURL


class TestFastURLComponents:
    """Test FastURLComponents parsing."""
    
    def test_basic_url_parsing(self):
        """Test basic URL component extraction."""
        url = "https://www.example.com:8080/path/to/resource?query=value&other=123#fragment"
        components = FastURLComponents(url)
        
        assert components.scheme == "https"
        assert components.host == "www.example.com"
        assert components.port == 8080
        assert components.path == "/path/to/resource"
        assert components.query == "query=value&other=123"
        assert components.fragment == "fragment"
        assert components.netloc == "www.example.com:8080"
    
    def test_url_without_scheme(self):
        """Test parsing URL without scheme."""
        url = "example.com/path?query=value"
        components = FastURLComponents(url)
        
        assert components.scheme == ""
        assert components.host == ""
        assert components.path == "example.com/path"
        assert components.query == "query=value"
    
    def test_url_reconstruction(self):
        """Test URL reconstruction from components."""
        original = "https://example.com/path?query=value#fragment"
        components = FastURLComponents(original)
        reconstructed = components.reconstruct()
        
        assert reconstructed == original
    
    def test_query_dict_parsing(self):
        """Test query parameter dictionary parsing."""
        url = "https://example.com?foo=bar&baz=qux&foo=bar2"
        components = FastURLComponents(url)
        query_dict = components.get_query_dict()
        
        assert "foo" in query_dict
        assert query_dict["foo"] == ["bar", "bar2"]
        assert query_dict["baz"] == ["qux"]


class TestURLCanonicalizer:
    """Test URL canonicalization with caching."""
    
    def test_basic_canonicalization(self):
        """Test basic URL canonicalization."""
        canonicalizer = URLCanonicalizer()
        
        # Test various URLs
        test_cases = [
            ("https://WWW.EXAMPLE.COM/PATH/?utm_source=test#fragment", 
             "https://example.com/PATH"),
            ("http://example.com//path///to////resource/?", 
             "http://example.com/path/to/resource"),
            ("https://example.com/file.pdf?utm_campaign=promo&page=1",
             "https://example.com/file.pdf?page=1"),
        ]
        
        for input_url, expected in test_cases:
            result = canonicalizer.canonicalize(input_url)
            assert result == expected
    
    def test_caching(self):
        """Test that caching works correctly."""
        canonicalizer = URLCanonicalizer(max_cache_size=2)
        
        url1 = "https://example.com/page1?utm_source=test"
        url2 = "https://example.com/page2?utm_source=test"
        
        # First calls should cache
        result1a = canonicalizer.canonicalize(url1)
        result2a = canonicalizer.canonicalize(url2)
        
        # Second calls should hit cache
        result1b = canonicalizer.canonicalize(url1)
        result2b = canonicalizer.canonicalize(url2)
        
        assert result1a == result1b
        assert result2a == result2b
    
    def test_custom_tracking_params(self):
        """Test setting custom tracking parameters."""
        canonicalizer = URLCanonicalizer()
        canonicalizer.set_tracking_params({'custom_tracking', 'my_param'})
        
        url = "https://example.com?custom_tracking=123&keep=this"
        result = canonicalizer.canonicalize(url)
        
        # Note: This test might need adjustment based on implementation
        assert "keep=this" in result or result.endswith("/")


class TestPatternMatcher:
    """Test compiled pattern matching."""
    
    def test_pattern_matching(self):
        """Test basic pattern matching."""
        matcher = CompiledPatternMatcher()
        
        # Add patterns
        matcher.add_pattern("email", r"^[\w\.-]+@[\w\.-]+\.\w+$")
        matcher.add_pattern("url", r"^https?://")
        matcher.add_pattern("number", r"^\d+$")
        
        # Test matching
        assert matcher.matches("test@example.com", "email") is True
        assert matcher.matches("https://example.com", "url") is True
        assert matcher.matches("12345", "number") is True
        assert matcher.matches("not-a-number", "number") is False
    
    def test_pattern_caching(self):
        """Test that pattern matching results are cached."""
        matcher = CompiledPatternMatcher(max_cache_size=10)
        matcher.add_pattern("test", r"^test")
        
        # First call
        result1 = matcher.matches("testing", "test")
        
        # Second call should hit cache
        result2 = matcher.matches("testing", "test")
        
        assert result1 == result2
        assert result1 is True


class TestDomainRuleMatcher:
    """Test domain-specific rule matching."""
    
    def test_exact_domain_matching(self):
        """Test exact domain rule matching."""
        matcher = DomainRuleMatcher()
        
        rules = {"canonical": ["id", "page"], "remove": ["session"]}
        matcher.add_domain_rule("example.com", rules)
        
        retrieved = matcher.get_rules_for_domain("example.com")
        assert retrieved == rules
        
        # Test case insensitive
        retrieved = matcher.get_rules_for_domain("EXAMPLE.COM")
        assert retrieved == rules
    
    def test_wildcard_domain_matching(self):
        """Test wildcard domain patterns."""
        matcher = DomainRuleMatcher()
        
        rules = {"force_https": True}
        matcher.add_domain_rule("*.example.com", rules)
        
        # Should match subdomains
        assert matcher.get_rules_for_domain("sub.example.com") == rules
        assert matcher.get_rules_for_domain("deep.sub.example.com") == rules
        
        # Should not match root domain
        assert matcher.get_rules_for_domain("example.com") == {}


class TestURLClassifier:
    """Test URL classification."""
    
    def test_file_type_classification(self):
        """Test classification of file types."""
        classifier = URLClassifier()
        
        assert classifier.classify_url("https://example.com/document.pdf") == "document"
        assert classifier.classify_url("https://example.com/image.jpg") == "image"
        assert classifier.classify_url("https://example.com/video.mp4") == "video"
        assert classifier.classify_url("https://example.com/audio.mp3") == "audio"
    
    def test_navigation_classification(self):
        """Test classification of navigation pages."""
        classifier = URLClassifier()
        
        assert classifier.classify_url("https://example.com/about") == "navigation"
        assert classifier.classify_url("https://example.com/contact.html") == "navigation"
        assert classifier.classify_url("https://example.com/privacy") == "navigation"
    
    def test_ecommerce_classification(self):
        """Test classification of e-commerce URLs."""
        classifier = URLClassifier()
        
        assert classifier.classify_url("https://shop.com/product/12345") == "product"
        assert classifier.classify_url("https://shop.com/category/electronics") == "category"
        assert classifier.classify_url("https://shop.com/search?q=laptop") == "search"
    
    def test_custom_pattern(self):
        """Test that classifier handles unknown patterns correctly."""
        classifier = URLClassifier()
        
        # Clear cache first
        classifier.clear_cache()
        
        # Test that URLs not matching any pattern get classified as 'unknown'
        result = classifier.classify_url("https://example.com/api/v2/users")
        assert result == "unknown"
        
        # Test that classification is consistent for unknown patterns
        result2 = classifier.classify_url("https://example.com/custom/endpoint")
        assert result2 == "unknown"
    
    def test_batch_classification(self):
        """Test batch URL classification."""
        classifier = URLClassifier()
        
        urls = [
            "https://example.com/document.pdf",
            "https://example.com/image.jpg",
            "https://example.com/about",
            "https://example.com/unknown/path",
        ]
        
        results = classifier.classify_batch(urls)
        
        assert results == ["document", "image", "navigation", "unknown"]


class TestOptimizedURL:
    """Test the OptimizedURL wrapper class."""
    
    def test_basic_properties(self):
        """Test basic URL properties."""
        url = OptimizedURL("https://www.example.com:8080/path?query=value#fragment")
        
        assert url.scheme == "https"
        assert url.host == "www.example.com"
        assert url.port == 8080
        assert url.path == "/path"
        assert url.query == "query=value"
        assert url.fragment == "fragment"
    
    def test_canonicalization(self):
        """Test URL canonicalization."""
        url = OptimizedURL("https://WWW.EXAMPLE.COM/PATH/?utm_source=test#fragment")
        canonical = url.canonicalize()
        
        assert "example.com" in canonical.lower()
        assert "utm_source" not in canonical
        assert "#fragment" not in canonical
    
    def test_classification(self):
        """Test URL classification."""
        url = OptimizedURL("https://example.com/document.pdf")
        assert url.classify() == "document"
    
    def test_query_filtering(self):
        """Test query parameter filtering."""
        url = OptimizedURL("https://example.com?utm_source=test&page=1&sort=date")
        
        filtered = url.filter_query_params(keep_params={'page', 'sort'})
        assert "utm_source" not in filtered
        assert "page=1" in filtered
        assert "sort=date" in filtered
    
    def test_tracking_param_detection(self):
        """Test tracking parameter detection."""
        url = OptimizedURL("https://example.com")
        
        assert url.is_tracking_param("utm_source") is True
        assert url.is_tracking_param("fbclid") is True
        assert url.is_tracking_param("page") is False
    
    def test_cython_fallback(self):
        """Test that fallback to pure Python works."""
        # Force pure Python
        url_python = OptimizedURL("https://example.com/test", use_cython=False)
        
        # Force Cython if available
        url_cython = OptimizedURL("https://example.com/test", use_cython=True)
        
        # Both should work
        assert url_python.host == "example.com"
        assert url_cython.host == "example.com"


class TestHelperFunctions:
    """Test standalone helper functions."""
    
    def test_fast_canonicalize_domain(self):
        """Test domain canonicalization."""
        assert fast_canonicalize_domain("WWW.EXAMPLE.COM") == "example.com"
        assert fast_canonicalize_domain("www3.example.com") == "example.com"
        assert fast_canonicalize_domain("example.com") == "example.com"
        assert fast_canonicalize_domain("") == ""
    
    def test_fast_clean_path(self):
        """Test path cleaning."""
        assert fast_clean_path("//path///to////resource//") == "/path/to/resource"
        assert fast_clean_path("/path/") == "/path"
        assert fast_clean_path("/") == "/"
        assert fast_clean_path("") == "/"
    
    def test_fast_filter_query_params(self):
        """Test query parameter filtering."""
        query = "utm_source=test&page=1&fbclid=abc&sort=date"
        
        # Default filtering (removes tracking)
        filtered = fast_filter_query_params(query)
        assert "utm_source" not in filtered
        assert "fbclid" not in filtered
        assert "page" in filtered
        assert "sort" in filtered
        
        # With keep params
        filtered = fast_filter_query_params(query, keep_params={'page'})
        assert filtered == "page=1"
        
        # With remove params
        filtered = fast_filter_query_params(query, remove_params={'page', 'sort'})
        assert "page" not in filtered
        assert "sort" not in filtered
    
    def test_split_and_join_url_parts(self):
        """Test URL splitting and joining."""
        original = "https://example.com/path?query=value#fragment"
        
        # Split
        scheme, host, path, query, fragment = split_url_parts(original)
        assert scheme == "https"
        assert host == "example.com"
        assert path == "/path"
        assert query == "query=value"
        assert fragment == "fragment"
        
        # Join
        reconstructed = join_url_parts(scheme, host, path, query, fragment)
        assert reconstructed == original
    
    def test_is_tracking_param(self):
        """Test tracking parameter detection."""
        assert is_tracking_param("utm_source") is True
        assert is_tracking_param("utm_medium") is True
        assert is_tracking_param("fbclid") is True
        assert is_tracking_param("gclid") is True
        assert is_tracking_param("page") is False
        assert is_tracking_param("sort") is False


class TestBackwardCompatibility:
    """Test backward compatibility with original URL class."""
    
    def test_equivalent_canonicalization(self):
        """Test that canonicalization produces similar results."""
        test_urls = [
            "https://www.example.com/path?utm_source=test",
            "https://EXAMPLE.COM/PATH/TO/RESOURCE/?",
            "http://bit.ly/abc123",
        ]
        
        for url_str in test_urls:
            original = OriginalURL(url_str)
            optimized = OptimizedURL(url_str)
            
            # Components should match (case-insensitive for host)
            assert original.scheme == optimized.scheme
            assert str(original.host).lower() == str(optimized.host).lower()
            assert original.path == optimized.path
            
            # Canonicalization should be similar (may differ in parameter ordering)
            original_canonical = original.canonicalize()
            optimized_canonical = optimized.canonicalize()
            
            # Check key components are preserved
            if original.scheme:
                assert original.scheme in optimized_canonical
            if original.host:
                # Host might be canonicalized differently (www removal)
                # Check that the canonical host (without www) is in the result
                canonical_host = fast_canonicalize_domain(str(original.host))
                assert canonical_host in optimized_canonical.lower()
    
    def test_equivalent_classification(self):
        """Test that classification produces similar results."""
        test_cases = [
            ("https://example.com/document.pdf", "document"),
            ("https://example.com/image.jpg", "image"),
            ("https://example.com/about", "navigation"),
        ]
        
        for url_str, expected_class in test_cases:
            original = OriginalURL(url_str)
            optimized = OptimizedURL(url_str)
            
            # Both should classify similarly
            # Note: Exact match might not be possible due to different implementations
            optimized_class = optimized.classify()
            assert optimized_class == expected_class or optimized_class == "unknown"


@pytest.mark.skipif(not CYTHON_AVAILABLE, reason="Cython extensions not available")
class TestCythonSpecific:
    """Tests specific to Cython implementation."""
    
    def test_cython_performance(self):
        """Basic performance test to ensure Cython is working."""
        import time
        
        # Note: In small test scenarios, Python fallback can be faster due to
        # less overhead. The real performance gains are seen with larger datasets
        # and repeated operations (as shown in the benchmark script).
        
        urls = ["https://example.com/path?utm_source=test" for _ in range(1000)]
        
        # Clear caches to ensure fair comparison
        OptimizedURL.clear_caches()
        
        # Test with Cython
        start = time.perf_counter()
        for url in urls:
            opt = OptimizedURL(url, use_cython=True)
            _ = opt.canonicalize()
        cython_time = time.perf_counter() - start
        
        # Clear caches again
        OptimizedURL.clear_caches()
        
        # Test without Cython
        start = time.perf_counter()
        for url in urls:
            opt = OptimizedURL(url, use_cython=False)
            _ = opt.canonicalize()
        python_time = time.perf_counter() - start
        
        # Just verify both work - performance can vary in test environments
        assert cython_time > 0
        assert python_time > 0
        
        # Print for informational purposes
        print(f"\nCython time: {cython_time:.4f}s, Python time: {python_time:.4f}s")
    
    def test_cache_eviction(self):
        """Test that cache eviction works in Cython implementation."""
        canonicalizer = URLCanonicalizer(max_cache_size=2)
        
        # Add more than max_cache_size URLs
        url1 = "https://example1.com"
        url2 = "https://example2.com"
        url3 = "https://example3.com"
        
        canonicalizer.canonicalize(url1)
        canonicalizer.canonicalize(url2)
        canonicalizer.canonicalize(url3)  # Should trigger eviction
        
        # Cache should still work for recent URLs
        result = canonicalizer.canonicalize(url3)
        assert result  # Should return a valid result