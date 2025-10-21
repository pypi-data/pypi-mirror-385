"""Test package imports and basic functionality."""

import pytest


def test_package_imports():
    """Test that all main classes can be imported from the package."""
    try:
        from atlassian_page_client import AtlassianPageClient, AtlassianPage, AtlassianPageContent
        
        # Verify classes are available
        assert AtlassianPageClient is not None
        assert AtlassianPage is not None
        assert AtlassianPageContent is not None
        
    except ImportError as e:
        pytest.fail(f"Failed to import package classes: {e}")


def test_package_version():
    """Test that package version is accessible."""
    try:
        from atlassian_page_client import __version__
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0
        
    except ImportError:
        pytest.fail("Package version not accessible")


def test_package_metadata():
    """Test that package metadata is accessible."""
    try:
        import atlassian_page_client
        
        # Test that main attributes exist
        assert hasattr(atlassian_page_client, '__version__')
        assert hasattr(atlassian_page_client, '__author__')
        assert hasattr(atlassian_page_client, '__all__')
        
        # Test __all__ contains expected classes
        expected_exports = ['AtlassianPageClient', 'AtlassianPage', 'AtlassianPageContent']
        for export in expected_exports:
            assert export in atlassian_page_client.__all__
            
    except (ImportError, AttributeError) as e:
        pytest.fail(f"Package metadata not accessible: {e}")


def test_class_instantiation():
    """Test that classes can be instantiated with proper parameters."""
    from atlassian_page_client import AtlassianPageClient, AtlassianPage, AtlassianPageContent
    
    # Test AtlassianPageContent
    content = AtlassianPageContent("<p>Test</p>")
    assert content is not None
    assert content.raw_html == "<p>Test</p>"
    
    # Test AtlassianPage
    page_data = {
        "id": "test",
        "body": {"storage": {"value": "<p>Test</p>"}},
        "version": {"number": 1, "_links": {"self": "http://test.com/1"}}
    }
    page = AtlassianPage("test-id", page_data)
    assert page is not None
    assert page.get_page_id() == "test-id"
    
    # Test AtlassianPageClient
    client = AtlassianPageClient("test@example.com", "token", "https://test.com")
    assert client is not None
    assert client.email == "test@example.com"
