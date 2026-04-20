"""Tests for the WebFetch handler."""

import json
from unittest.mock import MagicMock, patch

import nah.context
from nah import config, taxonomy
from nah.config import NahConfig
from nah.hook import _extract_webfetch_host, handle_webfetch


def _set_llm_config(llm_cfg: dict):
    config._cached_config = NahConfig(llm=llm_cfg)


def _ollama_config():
    return {
        "enabled": True,
        "backends": ["ollama"],
        "ollama": {"url": "http://localhost:11434/api/generate", "model": "test"},
    }


def _mock_ollama(decision: str, reasoning: str = "ok"):
    resp = MagicMock()
    resp.read.return_value = json.dumps({
        "response": json.dumps({"decision": decision, "reasoning": reasoning}),
    }).encode()
    return MagicMock(return_value=resp)


class TestExtractWebfetchHost:
    def test_https_url(self):
        assert _extract_webfetch_host("https://example.com/path") == "example.com"

    def test_http_url(self):
        assert _extract_webfetch_host("http://example.com") == "example.com"

    def test_bare_domain_upgrades_to_https(self):
        assert _extract_webfetch_host("example.com/some/path") == "example.com"

    def test_subdomain(self):
        assert _extract_webfetch_host("https://blog.example.com/post") == "blog.example.com"

    def test_port_stripped(self):
        # urlparse.hostname strips port and lowercases
        assert _extract_webfetch_host("https://example.com:8080/x") == "example.com"

    def test_empty_returns_none(self):
        assert _extract_webfetch_host("") is None

    def test_garbage_returns_none(self):
        # A string with no "." and no "://" parses to a hostname-less URL
        assert _extract_webfetch_host("not a url at all!!!") is None


class TestHandleWebfetch:
    def test_missing_url_allows(self):
        assert handle_webfetch({})["decision"] == taxonomy.ALLOW

    def test_empty_url_allows(self):
        assert handle_webfetch({"url": ""})["decision"] == taxonomy.ALLOW

    def test_unparseable_url_asks(self):
        result = handle_webfetch({"url": "   "})
        assert result["decision"] == taxonomy.ASK
        assert "could not parse URL" in result["reason"]

    def test_known_host_allows(self):
        nah.context._known_hosts.add("trusted.example.com")
        try:
            result = handle_webfetch({"url": "https://trusted.example.com/page"})
            assert result["decision"] == taxonomy.ALLOW
            assert "trusted.example.com" in result["reason"]
        finally:
            nah.context._known_hosts.discard("trusted.example.com")

    def test_unknown_host_no_llm_asks(self):
        """Without LLM enabled, unknown host → ask."""
        _set_llm_config({"enabled": False})
        result = handle_webfetch({"url": "https://some-random-site.example/x"})
        assert result["decision"] == taxonomy.ASK
        assert "unknown host" in result["reason"]
        assert "some-random-site.example" in result["reason"]

    @patch("nah.llm.urllib.request.urlopen")
    def test_unknown_host_llm_allows(self, mock_urlopen):
        """LLM allow (e.g. public GET rule) → allow without prompting user."""
        _set_llm_config(_ollama_config())
        mock_urlopen.return_value = _mock_ollama("allow", "public read").return_value

        result = handle_webfetch({"url": "https://some-random-site.example/x"})
        assert result["decision"] == taxonomy.ALLOW

    @patch("nah.llm.urllib.request.urlopen")
    def test_unknown_host_llm_block_capped_to_ask(self, mock_urlopen):
        """Default max_decision=ask caps LLM block to ask with suggestion text."""
        _set_llm_config(_ollama_config())
        mock_urlopen.return_value = _mock_ollama("block", "suspicious").return_value

        result = handle_webfetch({"url": "https://some-random-site.example/x"})
        assert result["decision"] == taxonomy.ASK
        assert "LLM suggested block" in result.get("reason", "")

    def test_bare_domain_known_host_allows(self):
        """Bare domain (no scheme) still matches known_hosts — Claude Code upgrades to https."""
        nah.context._known_hosts.add("cardenal.com.uy")
        try:
            result = handle_webfetch({"url": "cardenal.com.uy/tienda"})
            assert result["decision"] == taxonomy.ALLOW
        finally:
            nah.context._known_hosts.discard("cardenal.com.uy")
