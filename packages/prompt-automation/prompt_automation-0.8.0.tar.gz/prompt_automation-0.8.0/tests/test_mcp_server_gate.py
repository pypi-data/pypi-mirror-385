import json
from pathlib import Path

import pytest

from prompt_automation import menus
from prompt_automation.renderer import load_template


def _base_template() -> dict:
    return {
        "id": "test-template",
        "title": "Test",
        "style": "LLM",
        "template": ["{{goals}}"],
        "placeholders": [{"name": "goals"}],
        "metadata": {},
    }


def test_render_template_uses_mcp_server_when_feature_enabled(monkeypatch):
    template = _base_template()
    template["metadata"]["features"] = {"mcp_server": True}

    monkeypatch.setattr(menus, "_is_mcp_server_enabled", lambda: True)

    calls: list[dict] = []

    def _fake_execute_project(args, **kwargs):
        calls.append(args.copy())
        return "PLAN"

    from prompt_automation.mcp import server as mcp_server

    monkeypatch.setattr(mcp_server, "execute_project", _fake_execute_project)

    rendered = menus.render_template(template, values={"goals": "Ship feature"})

    assert rendered == "PLAN"
    assert len(calls) == 1
    payload = calls[0]
    assert payload["goals"] == "Ship feature"
    assert "template" in payload and isinstance(payload["template"], dict)
    assert menus._supports_mcp_server(template) is True


def test_render_template_skips_mcp_server_when_feature_disabled(monkeypatch):
    template = _base_template()
    template["metadata"]["feature_flags"] = {"mcp_server": "false"}

    monkeypatch.setattr(menus, "_is_mcp_server_enabled", lambda: True)

    from prompt_automation.mcp import server as mcp_server

    monkeypatch.setattr(mcp_server, "execute_project", pytest.fail)

    rendered = menus.render_template(template, values={"goals": "Ship feature"})

    assert rendered == "Ship feature"
    assert menus._supports_mcp_server(template) is False


def test_render_template_skips_mcp_server_when_globally_disabled(monkeypatch):
    template = _base_template()

    monkeypatch.setattr(menus, "_is_mcp_server_enabled", lambda: False)

    from prompt_automation.mcp import server as mcp_server

    monkeypatch.setattr(mcp_server, "execute_project", pytest.fail)

    rendered = menus.render_template(template, values={"goals": "Ship feature"})

    assert rendered == "Ship feature"
    assert menus._supports_mcp_server(template) is True


def test_render_template_uses_mcp_server_by_default_when_globally_enabled(monkeypatch):
    template = _base_template()

    monkeypatch.setattr(menus, "_is_mcp_server_enabled", lambda: True)

    calls: list[dict] = []

    def _fake_execute_project(args, **kwargs):
        calls.append(args.copy())
        return "PLAN"

    from prompt_automation.mcp import server as mcp_server

    monkeypatch.setattr(mcp_server, "execute_project", _fake_execute_project)

    rendered = menus.render_template(template, values={"goals": "Ship feature"})

    assert rendered == "PLAN"
    assert len(calls) == 1
    assert menus._supports_mcp_server(template) is True


def test_supports_mcp_server_handles_malformed_metadata(monkeypatch):
    template = _base_template()
    template["metadata"] = {
        "features": "not-a-dict",
        "feature_flags": ["mcp_server"],
        "mcp": ["unexpected"],
        "mcp_server": {"nested": "value"},
    }

    monkeypatch.setattr(menus, "_is_mcp_server_enabled", lambda: True)

    assert menus._supports_mcp_server(template) is True


def test_supports_mcp_server_respects_nested_metadata_disable(monkeypatch):
    template = _base_template()
    template["metadata"] = {
        "mcp": {"server": {"enabled": False}},
    }

    monkeypatch.setattr(menus, "_is_mcp_server_enabled", lambda: True)

    assert menus._supports_mcp_server(template) is False


def test_supports_mcp_server_accepts_nested_metadata_enable(monkeypatch):
    template = _base_template()
    template["metadata"] = {
        "mcp": {"server": {"mode": "on"}},
    }

    monkeypatch.setattr(menus, "_is_mcp_server_enabled", lambda: True)

    assert menus._supports_mcp_server(template) is True


def test_supports_mcp_server_default_true_when_only_default_flag_false(monkeypatch):
    template = _base_template()
    template["metadata"] = {"feature_flags": {"default": False}}

    monkeypatch.setattr(menus, "_is_mcp_server_enabled", lambda: True)

    assert menus._supports_mcp_server(template) is True


def test_load_template_normalizes_feature_flags(tmp_path: Path):
    data = _base_template()
    data["metadata"]["features"] = ["mcp-server"]
    path = tmp_path / "template.json"
    path.write_text(json.dumps(data))

    loaded = load_template(path)

    assert loaded["metadata"]["features"]["mcp_server"] is True
    assert loaded["metadata"]["feature_flags"]["mcp_server"] is True

    # ensure original data untouched beyond normalization copy
    assert "mcp-server" not in loaded["metadata"]["features"]


def test_render_template_falls_back_when_mcp_server_unavailable(monkeypatch):
    """Test that template rendering gracefully falls back when MCP server is unavailable."""
    template = _base_template()
    template["metadata"]["features"] = {"mcp_server": True}

    monkeypatch.setattr(menus, "_is_mcp_server_enabled", lambda: True)

    from prompt_automation.mcp import server as mcp_server

    def _fake_execute_project_failure(args, **kwargs):
        raise RuntimeError("retry budget exhausted after 3 attempts; connection refused")

    monkeypatch.setattr(mcp_server, "execute_project", _fake_execute_project_failure)

    # Should fall back to normal rendering instead of crashing
    rendered = menus.render_template(template, values={"goals": "Ship feature"})

    # Should render with the normal template processing (just the goals value)
    assert rendered == "Ship feature"


def test_default_retry_policy_has_limits():
    """Test that DEFAULT_RETRY_POLICY has reasonable limits to prevent indefinite retries."""
    from prompt_automation.mcp.server import DEFAULT_RETRY_POLICY

    # Verify retry policy has limits to prevent hanging
    assert DEFAULT_RETRY_POLICY.max_attempts is not None, "max_attempts should be set to prevent infinite retries"
    assert DEFAULT_RETRY_POLICY.max_duration is not None, "max_duration should be set to prevent infinite retries"
    
    # Verify limits are reasonable (not too high)
    assert DEFAULT_RETRY_POLICY.max_attempts <= 10, "max_attempts should be reasonable (≤10)"
    assert DEFAULT_RETRY_POLICY.max_duration <= 30.0, "max_duration should be reasonable (≤30s)"
    
    # Verify limits are reasonable (not too low)
    assert DEFAULT_RETRY_POLICY.max_attempts >= 3, "max_attempts should allow some retries (≥3)"
    assert DEFAULT_RETRY_POLICY.max_duration >= 3.0, "max_duration should allow some time for retries (≥3s)"
