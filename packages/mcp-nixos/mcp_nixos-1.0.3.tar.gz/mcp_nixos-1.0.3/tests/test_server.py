"""Comprehensive test suite for MCP-NixOS server with 100% coverage."""

from unittest.mock import Mock, patch

import pytest
import requests
from mcp_nixos import server
from mcp_nixos.server import (
    DARWIN_URL,
    HOME_MANAGER_URL,
    NIXOS_API,
    NIXOS_AUTH,
    error,
    es_query,
    get_channels,
    mcp,
    parse_html_options,
)


def get_tool_function(tool_name: str):
    """Get the underlying function from a FastMCP tool."""
    tool = getattr(server, tool_name)
    if hasattr(tool, "fn"):
        return tool.fn
    return tool


# Get the underlying functions for direct use
darwin_info = get_tool_function("darwin_info")
darwin_list_options = get_tool_function("darwin_list_options")
darwin_options_by_prefix = get_tool_function("darwin_options_by_prefix")
darwin_search = get_tool_function("darwin_search")
darwin_stats = get_tool_function("darwin_stats")
home_manager_info = get_tool_function("home_manager_info")
home_manager_list_options = get_tool_function("home_manager_list_options")
home_manager_options_by_prefix = get_tool_function("home_manager_options_by_prefix")
home_manager_search = get_tool_function("home_manager_search")
home_manager_stats = get_tool_function("home_manager_stats")
nixos_info = get_tool_function("nixos_info")
nixos_search = get_tool_function("nixos_search")
nixos_stats = get_tool_function("nixos_stats")


class TestHelperFunctions:
    """Test all helper functions with edge cases."""

    def test_error_basic(self):
        """Test basic error formatting."""
        result = error("Test message")
        assert result == "Error (ERROR): Test message"

    def test_error_with_code(self):
        """Test error formatting with custom code."""
        result = error("Not found", "NOT_FOUND")
        assert result == "Error (NOT_FOUND): Not found"

    def test_error_xml_escaping(self):
        """Test character escaping in errors."""
        result = error("Error <tag> & \"quotes\" 'apostrophe'", "CODE")
        assert result == "Error (CODE): Error <tag> & \"quotes\" 'apostrophe'"

    def test_error_empty_message(self):
        """Test error with empty message."""
        result = error("")
        assert result == "Error (ERROR): "

    @patch("mcp_nixos.server.requests.post")
    def test_es_query_success(self, mock_post):
        """Test successful Elasticsearch query."""
        mock_resp = Mock()
        mock_resp.json.return_value = {"hits": {"hits": [{"_source": {"test": "data"}}]}}
        mock_post.return_value = mock_resp

        result = es_query("test-index", {"match_all": {}})
        assert len(result) == 1
        assert result[0]["_source"]["test"] == "data"

        # Verify request parameters
        mock_post.assert_called_once_with(
            f"{NIXOS_API}/test-index/_search",
            json={"query": {"match_all": {}}, "size": 20},
            auth=NIXOS_AUTH,
            timeout=10,
        )

    @patch("mcp_nixos.server.requests.post")
    def test_es_query_custom_size(self, mock_post):
        """Test Elasticsearch query with custom size."""
        mock_resp = Mock()
        mock_resp.json.return_value = {"hits": {"hits": []}}
        mock_post.return_value = mock_resp

        es_query("test-index", {"match_all": {}}, size=50)

        # Verify size parameter
        call_args = mock_post.call_args[1]
        assert call_args["json"]["size"] == 50

    @patch("mcp_nixos.server.requests.post")
    def test_es_query_http_error(self, mock_post):
        """Test Elasticsearch query with HTTP error."""
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_post.return_value = mock_resp

        with pytest.raises(Exception, match="API error: 404 Not Found"):
            es_query("test-index", {"match_all": {}})

    @patch("mcp_nixos.server.requests.post")
    def test_es_query_connection_error(self, mock_post):
        """Test Elasticsearch query with connection error."""
        mock_post.side_effect = requests.ConnectionError("Connection failed")

        with pytest.raises(Exception, match="API error: Connection failed"):
            es_query("test-index", {"match_all": {}})

    @patch("mcp_nixos.server.requests.post")
    def test_es_query_missing_hits(self, mock_post):
        """Test Elasticsearch query with missing hits field."""
        mock_resp = Mock()
        mock_resp.json.return_value = {}  # No hits field
        mock_post.return_value = mock_resp

        result = es_query("test-index", {"match_all": {}})
        assert result == []

    @patch("mcp_nixos.server.requests.get")
    def test_parse_html_options_success(self, mock_get):
        """Test successful HTML parsing."""
        mock_resp = Mock()
        html_content = """
        <html>
            <dt>programs.git.enable</dt>
            <dd>
                <p>Enable git</p>
                <span class="term">Type: boolean</span>
            </dd>
            <dt>programs.vim.enable</dt>
            <dd>
                <p>Enable vim</p>
                <span class="term">Type: boolean</span>
            </dd>
        </html>
        """
        mock_resp.content = html_content.encode("utf-8")
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        result = parse_html_options("http://test.com")
        assert len(result) == 2
        assert result[0]["name"] == "programs.git.enable"
        assert result[0]["description"] == "Enable git"
        assert result[0]["type"] == "boolean"

    @patch("mcp_nixos.server.requests.get")
    def test_parse_html_options_with_query(self, mock_get):
        """Test HTML parsing with query filter."""
        mock_resp = Mock()
        html_content = """
        <html>
            <dt>programs.git.enable</dt>
            <dd><p>Enable git</p></dd>
            <dt>programs.vim.enable</dt>
            <dd><p>Enable vim</p></dd>
        </html>
        """
        mock_resp.content = html_content.encode("utf-8")
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        result = parse_html_options("http://test.com", query="git")
        assert len(result) == 1
        assert result[0]["name"] == "programs.git.enable"

    @patch("mcp_nixos.server.requests.get")
    def test_parse_html_options_with_prefix(self, mock_get):
        """Test HTML parsing with prefix filter."""
        mock_resp = Mock()
        html_content = """
        <html>
            <dt>programs.git.enable</dt>
            <dd><p>Enable git</p></dd>
            <dt>services.nginx.enable</dt>
            <dd><p>Enable nginx</p></dd>
        </html>
        """
        mock_resp.content = html_content.encode("utf-8")
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        result = parse_html_options("http://test.com", prefix="programs")
        assert len(result) == 1
        assert result[0]["name"] == "programs.git.enable"

    @patch("mcp_nixos.server.requests.get")
    def test_parse_html_options_empty_response(self, mock_get):
        """Test HTML parsing with empty response."""
        mock_resp = Mock()
        mock_resp.content = b"<html></html>"
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        result = parse_html_options("http://test.com")
        assert not result

    @patch("mcp_nixos.server.requests.get")
    def test_parse_html_options_connection_error(self, mock_get):
        """Test HTML parsing with connection error."""
        mock_get.side_effect = requests.ConnectionError("Failed to connect")

        with pytest.raises(Exception, match="Failed to fetch docs: Failed to connect"):
            parse_html_options("http://test.com")

    @patch("mcp_nixos.server.requests.get")
    def test_parse_html_options_limit(self, mock_get):
        """Test HTML parsing with limit."""
        mock_resp = Mock()
        # Create many options
        options_html = ""
        for i in range(10):
            options_html += f"<dt>option.{i}</dt><dd><p>desc{i}</p></dd>"
        mock_resp.content = f"<html>{options_html}</html>".encode()
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        result = parse_html_options("http://test.com", limit=5)
        assert len(result) == 5

    @patch("mcp_nixos.server.requests.get")
    def test_parse_html_options_windows_1252_encoding(self, mock_get):
        """Test HTML parsing with windows-1252 encoding."""
        # Create HTML content with special characters
        html_content = """
        <html>
            <head><meta charset="windows-1252"></head>
            <dt>programs.git.userName</dt>
            <dd>
                <p>Git user name with special chars: café</p>
                <span class="term">Type: string</span>
            </dd>
        </html>
        """

        mock_resp = Mock()
        # Simulate windows-1252 encoded content
        mock_resp.content = html_content.encode("windows-1252")
        mock_resp.encoding = "windows-1252"
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        # Should not raise encoding errors
        result = parse_html_options("http://test.com")
        assert len(result) == 1
        assert result[0]["name"] == "programs.git.userName"
        assert "café" in result[0]["description"]

    @patch("mcp_nixos.server.requests.get")
    def test_parse_html_options_utf8_with_bom(self, mock_get):
        """Test HTML parsing with UTF-8 BOM."""
        html_content = """
        <html>
            <dt>programs.neovim.enable</dt>
            <dd>
                <p>Enable Neovim with unicode: 你好</p>
                <span class="term">Type: boolean</span>
            </dd>
        </html>
        """

        mock_resp = Mock()
        # Add UTF-8 BOM at the beginning
        mock_resp.content = b"\xef\xbb\xbf" + html_content.encode("utf-8")
        mock_resp.encoding = "utf-8-sig"
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        result = parse_html_options("http://test.com")
        assert len(result) == 1
        assert result[0]["name"] == "programs.neovim.enable"
        assert "你好" in result[0]["description"]

    @patch("mcp_nixos.server.requests.get")
    def test_parse_html_options_iso_8859_1_encoding(self, mock_get):
        """Test HTML parsing with ISO-8859-1 encoding."""
        html_content = """
        <html>
            <head><meta charset="iso-8859-1"></head>
            <dt>services.nginx.virtualHosts</dt>
            <dd>
                <p>Nginx config with special: naïve résumé</p>
            </dd>
        </html>
        """

        mock_resp = Mock()
        # Simulate ISO-8859-1 encoded content
        mock_resp.content = html_content.encode("iso-8859-1")
        mock_resp.encoding = "iso-8859-1"
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        result = parse_html_options("http://test.com")
        assert len(result) == 1
        assert result[0]["name"] == "services.nginx.virtualHosts"
        assert "naïve" in result[0]["description"]
        assert "résumé" in result[0]["description"]


class TestNixOSTools:
    """Test all NixOS tools."""

    @patch("mcp_nixos.server.es_query")
    @pytest.mark.asyncio
    async def test_nixos_search_packages_success(self, mock_query):
        """Test successful package search."""
        mock_query.return_value = [
            {
                "_source": {
                    "package_pname": "firefox",
                    "package_pversion": "123.0",
                    "package_description": "A web browser",
                }
            }
        ]

        result = await nixos_search("firefox", search_type="packages", limit=5)
        assert "Found 1 packages matching 'firefox':" in result
        assert "• firefox (123.0)" in result
        assert "  A web browser" in result

    @patch("mcp_nixos.server.es_query")
    @pytest.mark.asyncio
    async def test_nixos_search_options_success(self, mock_query):
        """Test successful option search."""
        mock_query.return_value = [
            {
                "_source": {
                    "option_name": "services.nginx.enable",
                    "option_type": "boolean",
                    "option_description": "Enable nginx",
                }
            }
        ]

        result = await nixos_search("nginx", search_type="options")
        assert "Found 1 options matching 'nginx':" in result
        assert "• services.nginx.enable" in result
        assert "  Type: boolean" in result
        assert "  Enable nginx" in result

    @patch("mcp_nixos.server.es_query")
    @pytest.mark.asyncio
    async def test_nixos_search_programs_success(self, mock_query):
        """Test successful program search."""
        mock_query.return_value = [{"_source": {"package_pname": "vim", "package_programs": ["vim", "vi"]}}]

        result = await nixos_search("vim", search_type="programs")
        assert "Found 1 programs matching 'vim':" in result
        assert "• vim (provided by vim)" in result

    @patch("mcp_nixos.server.es_query")
    @pytest.mark.asyncio
    async def test_nixos_search_empty_results(self, mock_query):
        """Test search with no results."""
        mock_query.return_value = []

        result = await nixos_search("nonexistent")
        assert result == "No packages found matching 'nonexistent'"

    @pytest.mark.asyncio
    async def test_nixos_search_invalid_type(self):
        """Test search with invalid type."""
        result = await nixos_search("test", search_type="invalid")
        assert result == "Error (ERROR): Invalid type 'invalid'"

    @pytest.mark.asyncio
    async def test_nixos_search_invalid_channel(self):
        """Test search with invalid channel."""
        result = await nixos_search("test", channel="invalid")
        assert "Error (ERROR): Invalid channel 'invalid'" in result
        assert "Available channels:" in result

    @pytest.mark.asyncio
    async def test_nixos_search_invalid_limit_low(self):
        """Test search with limit too low."""
        result = await nixos_search("test", limit=0)
        assert result == "Error (ERROR): Limit must be 1-100"

    @pytest.mark.asyncio
    async def test_nixos_search_invalid_limit_high(self):
        """Test search with limit too high."""
        result = await nixos_search("test", limit=101)
        assert result == "Error (ERROR): Limit must be 1-100"

    @patch("mcp_nixos.server.es_query")
    @pytest.mark.asyncio
    async def test_nixos_search_all_channels(self, mock_query):
        """Test search works with all defined channels."""
        mock_query.return_value = []

        channels = get_channels()
        for channel in channels:
            result = await nixos_search("test", channel=channel)
            assert result == "No packages found matching 'test'"

            # Verify correct index is used
            mock_query.assert_called_with(
                channels[channel],
                {
                    "bool": {
                        "must": [{"term": {"type": "package"}}],
                        "should": [
                            {"match": {"package_pname": {"query": "test", "boost": 3}}},
                            {"match": {"package_description": "test"}},
                        ],
                        "minimum_should_match": 1,
                    }
                },
                20,
            )

    @patch("mcp_nixos.server.es_query")
    @pytest.mark.asyncio
    async def test_nixos_search_exception_handling(self, mock_query):
        """Test search with API exception."""
        mock_query.side_effect = Exception("API failed")

        result = await nixos_search("test")
        assert result == "Error (ERROR): API failed"

    @patch("mcp_nixos.server.es_query")
    @pytest.mark.asyncio
    async def test_nixos_info_package_found(self, mock_query):
        """Test info when package found."""
        mock_query.return_value = [
            {
                "_source": {
                    "package_pname": "firefox",
                    "package_pversion": "123.0",
                    "package_description": "A web browser",
                    "package_homepage": ["https://firefox.com"],
                    "package_license_set": ["MPL-2.0"],
                }
            }
        ]

        result = await nixos_info("firefox", type="package")
        assert "Package: firefox" in result
        assert "Version: 123.0" in result
        assert "Description: A web browser" in result
        assert "Homepage: https://firefox.com" in result
        assert "License: MPL-2.0" in result

    @patch("mcp_nixos.server.es_query")
    @pytest.mark.asyncio
    async def test_nixos_info_option_found(self, mock_query):
        """Test info when option found."""
        mock_query.return_value = [
            {
                "_source": {
                    "option_name": "services.nginx.enable",
                    "option_type": "boolean",
                    "option_description": "Enable nginx",
                    "option_default": "false",
                    "option_example": "true",
                }
            }
        ]

        result = await nixos_info("services.nginx.enable", type="option")
        assert "Option: services.nginx.enable" in result
        assert "Type: boolean" in result
        assert "Description: Enable nginx" in result
        assert "Default: false" in result
        assert "Example: true" in result

    @patch("mcp_nixos.server.es_query")
    @pytest.mark.asyncio
    async def test_nixos_info_not_found(self, mock_query):
        """Test info when package/option not found."""
        mock_query.return_value = []

        result = await nixos_info("nonexistent", type="package")
        assert result == "Error (NOT_FOUND): Package 'nonexistent' not found"

    @pytest.mark.asyncio
    async def test_nixos_info_invalid_type(self):
        """Test info with invalid type."""
        result = await nixos_info("test", type="invalid")
        assert result == "Error (ERROR): Type must be 'package' or 'option'"

    @patch("mcp_nixos.server.requests.post")
    @pytest.mark.asyncio
    async def test_nixos_stats_success(self, mock_post):
        """Test stats retrieval."""
        # Mock package count
        pkg_resp = Mock()
        pkg_resp.json.return_value = {"count": 95000}

        # Mock option count
        opt_resp = Mock()
        opt_resp.json.return_value = {"count": 18000}

        mock_post.side_effect = [pkg_resp, opt_resp]

        result = await nixos_stats()
        assert "NixOS Statistics for unstable channel:" in result
        assert "• Packages: 95,000" in result
        assert "• Options: 18,000" in result

    @pytest.mark.asyncio
    async def test_nixos_stats_invalid_channel(self):
        """Test stats with invalid channel."""
        result = await nixos_stats(channel="invalid")
        assert "Error (ERROR): Invalid channel 'invalid'" in result
        assert "Available channels:" in result

    @patch("mcp_nixos.server.requests.post")
    @pytest.mark.asyncio
    async def test_nixos_stats_api_error(self, mock_post):
        """Test stats with API error."""
        mock_post.side_effect = requests.ConnectionError("Failed")

        result = await nixos_stats()
        assert result == "Error (ERROR): Failed to retrieve statistics"


class TestHomeManagerTools:
    """Test all Home Manager tools."""

    @patch("mcp_nixos.server.parse_html_options")
    @pytest.mark.asyncio
    async def test_home_manager_search_success(self, mock_parse):
        """Test successful Home Manager search."""
        mock_parse.return_value = [{"name": "programs.git.enable", "type": "boolean", "description": "Enable git"}]

        result = await home_manager_search("git")
        assert "Found 1 Home Manager options matching 'git':" in result
        assert "• programs.git.enable" in result
        assert "  Type: boolean" in result
        assert "  Enable git" in result

        # Verify parse was called correctly
        mock_parse.assert_called_once_with(HOME_MANAGER_URL, "git", "", 20)

    @pytest.mark.asyncio
    async def test_home_manager_search_invalid_limit(self):
        """Test Home Manager search with invalid limit."""
        result = await home_manager_search("test", limit=0)
        assert result == "Error (ERROR): Limit must be 1-100"

    @patch("mcp_nixos.server.parse_html_options")
    @pytest.mark.asyncio
    async def test_home_manager_search_exception(self, mock_parse):
        """Test Home Manager search with exception."""
        mock_parse.side_effect = Exception("Parse failed")

        result = await home_manager_search("test")
        assert result == "Error (ERROR): Parse failed"

    @patch("mcp_nixos.server.parse_html_options")
    @pytest.mark.asyncio
    async def test_home_manager_info_found(self, mock_parse):
        """Test Home Manager info when option found."""
        mock_parse.return_value = [{"name": "programs.git.enable", "type": "boolean", "description": "Enable git"}]

        result = await home_manager_info("programs.git.enable")
        assert "Option: programs.git.enable" in result
        assert "Type: boolean" in result
        assert "Description: Enable git" in result

    @patch("mcp_nixos.server.parse_html_options")
    @pytest.mark.asyncio
    async def test_home_manager_info_not_found(self, mock_parse):
        """Test Home Manager info when option not found."""
        mock_parse.return_value = [{"name": "programs.vim.enable", "type": "boolean", "description": "Enable vim"}]

        result = await home_manager_info("programs.git.enable")
        assert result == (
            "Error (NOT_FOUND): Option 'programs.git.enable' not found.\n"
            "Tip: Use home_manager_options_by_prefix('programs.git.enable') to browse available options."
        )

    @patch("requests.get")
    @pytest.mark.asyncio
    async def test_home_manager_stats(self, mock_get):
        """Test Home Manager stats message."""
        mock_html = """
        <html>
        <body>
            <dl class="variablelist">
                <dt id="opt-programs.git.enable">programs.git.enable</dt>
                <dd>Enable git</dd>
                <dt id="opt-services.gpg-agent.enable">services.gpg-agent.enable</dt>
                <dd>Enable gpg-agent</dd>
            </dl>
        </body>
        </html>
        """
        mock_resp = Mock()
        mock_resp.content = mock_html.encode("utf-8")
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        result = await home_manager_stats()
        assert "Home Manager Statistics:" in result
        assert "Total options:" in result
        assert "Categories:" in result

    @patch("mcp_nixos.server.parse_html_options")
    @pytest.mark.asyncio
    async def test_home_manager_list_options_success(self, mock_parse):
        """Test Home Manager list options."""
        mock_parse.return_value = [
            {"name": "programs.git.enable", "type": "", "description": ""},
            {"name": "programs.vim.enable", "type": "", "description": ""},
            {"name": "services.ssh.enable", "type": "", "description": ""},
        ]

        result = await home_manager_list_options()
        assert "Home Manager option categories (2 total):" in result
        assert "• programs (2 options)" in result
        assert "• services (1 options)" in result

    @patch("mcp_nixos.server.parse_html_options")
    @pytest.mark.asyncio
    async def test_home_manager_options_by_prefix_success(self, mock_parse):
        """Test Home Manager options by prefix."""
        mock_parse.return_value = [
            {"name": "programs.git.enable", "type": "boolean", "description": "Enable git"},
            {"name": "programs.git.userName", "type": "string", "description": "Git user name"},
        ]

        result = await home_manager_options_by_prefix("programs.git")
        assert "Home Manager options with prefix 'programs.git' (2 found):" in result
        assert "• programs.git.enable" in result
        assert "• programs.git.userName" in result


class TestDarwinTools:
    """Test all Darwin tools."""

    @patch("mcp_nixos.server.parse_html_options")
    @pytest.mark.asyncio
    async def test_darwin_search_success(self, mock_parse):
        """Test successful Darwin search."""
        mock_parse.return_value = [
            {"name": "system.defaults.dock.autohide", "type": "boolean", "description": "Auto-hide the dock"}
        ]

        result = await darwin_search("dock")
        assert "Found 1 nix-darwin options matching 'dock':" in result
        assert "• system.defaults.dock.autohide" in result

    @pytest.mark.asyncio
    async def test_darwin_search_invalid_limit(self):
        """Test Darwin search with invalid limit."""
        result = await darwin_search("test", limit=101)
        assert result == "Error (ERROR): Limit must be 1-100"

    @patch("mcp_nixos.server.parse_html_options")
    @pytest.mark.asyncio
    async def test_darwin_info_found(self, mock_parse):
        """Test Darwin info when option found."""
        mock_parse.return_value = [
            {"name": "system.defaults.dock.autohide", "type": "boolean", "description": "Auto-hide the dock"}
        ]

        result = await darwin_info("system.defaults.dock.autohide")
        assert "Option: system.defaults.dock.autohide" in result
        assert "Type: boolean" in result
        assert "Description: Auto-hide the dock" in result

    @patch("requests.get")
    @pytest.mark.asyncio
    async def test_darwin_stats(self, mock_get):
        """Test Darwin stats message."""
        mock_html = """
        <html>
        <body>
            <dl>
                <dt>system.defaults.dock.autohide</dt>
                <dd>Auto-hide the dock</dd>
                <dt>services.nix-daemon.enable</dt>
                <dd>Enable nix-daemon</dd>
            </dl>
        </body>
        </html>
        """
        mock_resp = Mock()
        mock_resp.content = mock_html.encode("utf-8")
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        result = await darwin_stats()
        assert "nix-darwin Statistics:" in result
        assert "Total options:" in result
        assert "Categories:" in result

    @patch("mcp_nixos.server.parse_html_options")
    @pytest.mark.asyncio
    async def test_darwin_list_options_success(self, mock_parse):
        """Test Darwin list options."""
        mock_parse.return_value = [
            {"name": "system.defaults.dock.autohide", "type": "", "description": ""},
            {"name": "homebrew.enable", "type": "", "description": ""},
        ]

        result = await darwin_list_options()
        assert "nix-darwin option categories (2 total):" in result
        assert "• system (1 options)" in result
        assert "• homebrew (1 options)" in result

    @patch("mcp_nixos.server.parse_html_options")
    @pytest.mark.asyncio
    async def test_darwin_options_by_prefix_success(self, mock_parse):
        """Test Darwin options by prefix."""
        mock_parse.return_value = [
            {"name": "system.defaults.dock.autohide", "type": "boolean", "description": "Auto-hide the dock"}
        ]

        result = await darwin_options_by_prefix("system.defaults")
        assert "nix-darwin options with prefix 'system.defaults' (1 found):" in result
        assert "• system.defaults.dock.autohide" in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @patch("mcp_nixos.server.es_query")
    @pytest.mark.asyncio
    async def test_empty_search_query(self, mock_query):
        """Test search with empty query."""
        mock_query.return_value = []

        result = await nixos_search("")
        assert "No packages found matching ''" in result

    @patch("mcp_nixos.server.es_query")
    @pytest.mark.asyncio
    async def test_special_characters_in_query(self, mock_query):
        """Test search with special characters."""
        mock_query.return_value = []

        result = await nixos_search("test@#$%")
        assert "No packages found matching 'test@#$%'" in result

    @patch("mcp_nixos.server.requests.get")
    def test_malformed_html_response(self, mock_get):
        """Test parsing malformed HTML."""
        mock_resp = Mock()
        mock_resp.content = b"<html><dt>broken"  # Malformed HTML
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        # Should not crash, just return empty or partial results
        result = parse_html_options("http://test.com")
        assert isinstance(result, list)

    @patch("mcp_nixos.server.es_query")
    @pytest.mark.asyncio
    async def test_missing_fields_in_response(self, mock_query):
        """Test handling missing fields in API response."""
        mock_query.return_value = [{"_source": {"package_pname": "test"}}]  # Missing version and description

        result = await nixos_search("test")
        assert "• test ()" in result  # Should handle missing version gracefully

    @patch("mcp_nixos.server.requests.post")
    @pytest.mark.asyncio
    async def test_timeout_handling(self, mock_post):
        """Test handling of request timeouts."""
        mock_post.side_effect = requests.Timeout("Request timed out")

        result = await nixos_stats()
        assert "Error (ERROR):" in result


class TestServerIntegration:
    """Test server module integration."""

    def test_mcp_instance_exists(self):
        """Test that mcp instance is properly initialized."""
        assert mcp is not None
        assert hasattr(mcp, "tool")

    def test_constants_defined(self):
        """Test that all required constants are defined."""
        assert NIXOS_API == "https://search.nixos.org/backend"
        assert NIXOS_AUTH == ("aWVSALXpZv", "X8gPHnzL52wFEekuxsfQ9cSh")
        assert HOME_MANAGER_URL == "https://nix-community.github.io/home-manager/options.xhtml"
        assert DARWIN_URL == "https://nix-darwin.github.io/nix-darwin/manual/index.html"
        channels = get_channels()
        assert "unstable" in channels
        assert "stable" in channels

    def test_all_tools_decorated(self):
        """Test that all tool functions are properly decorated."""
        # Tool functions should be registered with mcp and have underlying functions
        tool_names = [
            "nixos_search",
            "nixos_info",
            "nixos_stats",
            "home_manager_search",
            "home_manager_info",
            "home_manager_stats",
            "home_manager_list_options",
            "home_manager_options_by_prefix",
            "darwin_search",
            "darwin_info",
            "darwin_stats",
            "darwin_list_options",
            "darwin_options_by_prefix",
        ]

        for tool_name in tool_names:
            # FastMCP decorates functions, so they should have the original function available
            tool = getattr(server, tool_name)
            assert hasattr(tool, "fn"), f"Tool {tool_name} should have 'fn' attribute"
            assert callable(tool.fn), f"Tool {tool_name}.fn should be callable"
