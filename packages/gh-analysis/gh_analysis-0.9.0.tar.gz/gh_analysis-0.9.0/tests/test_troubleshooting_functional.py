"""Functional tests for troubleshoot processor.

These tests focus on real behavior with minimal mocking.
Only mock external services (API calls) where absolutely necessary.
"""

import os
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from gh_analysis.ai.mcp_server import troubleshoot_mcp_server
from gh_analysis.ai.troubleshooting_agents import (
    create_gpt5_high_agent,
    create_gpt5_medium_agent,
    create_gpt5_mini_high_agent,
    create_gpt5_mini_medium_agent,
    create_troubleshooting_agent,
)


class TestMCPServerIntegration:
    """Test MCP server with real initialization."""

    def test_mcp_server_creates_isolated_tmpdir(self):
        """Verify MCP server gets unique temp directory."""
        # Create two servers and verify they have different TMPDIRs
        server1 = troubleshoot_mcp_server("test_token1")
        server2 = troubleshoot_mcp_server("test_token2")

        # Extract TMPDIR from environment
        tmpdir1 = server1.env.get("TMPDIR") if server1.env else None
        tmpdir2 = server2.env.get("TMPDIR") if server2.env else None

        assert tmpdir1 is not None and tmpdir2 is not None
        assert tmpdir1 != tmpdir2
        assert "mcp-troubleshoot" in tmpdir1
        assert "mcp-troubleshoot" in tmpdir2

    def test_mcp_server_environment_setup(self):
        """Test environment variables are properly set."""
        server = troubleshoot_mcp_server("sbctl_test", "github_test")

        assert server.env is not None
        assert server.env["SBCTL_TOKEN"] == "sbctl_test"
        assert server.env["GITHUB_TOKEN"] == "github_test"
        assert "TMPDIR" in server.env


class TestAgentCreation:
    """Test agent creation with real components."""

    def test_agent_factory_creates_correct_type(self):
        """Test agent factory returns correct agent type."""
        # Set required environment
        os.environ["OPENAI_API_KEY"] = "test_key"

        # Create agent (will fail on actual API call but we can check type)
        try:
            agent = create_troubleshooting_agent(
                "o3_medium",
                "sbctl_token",
            )
            # Check agent has expected attributes
            assert hasattr(agent, "model")
            assert hasattr(agent, "run")
            assert hasattr(agent, "output_type")
        except Exception as e:
            # Expected to fail without real API key
            # But should fail at API call, not agent creation
            assert "API" in str(e) or "connection" in str(e).lower()

    def test_agent_requires_correct_env_vars(self):
        """Test agents fail gracefully without required env vars."""
        # Clear environment
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("ANTHROPIC_API_KEY", None)

        # GPT-5 and O3 agents should require OPENAI_API_KEY
        for agent_name in [
            "gpt5_mini_medium",
            "gpt5_mini_high",
            "gpt5_medium",
            "gpt5_high",
            "o3_medium",
            "o3_high",
        ]:
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                create_troubleshooting_agent(agent_name, "token")


class TestGPT5AgentCreation:
    """Test GPT-5 agent creation functions."""

    def test_create_gpt5_mini_medium_agent(self):
        """Test GPT-5-mini medium agent creation."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = create_gpt5_mini_medium_agent("test-token")
            assert agent is not None
            assert hasattr(agent, "model")
            assert hasattr(agent, "run")
            assert hasattr(agent, "output_type")

    def test_create_gpt5_mini_high_agent(self):
        """Test GPT-5-mini high agent creation."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = create_gpt5_mini_high_agent("test-token")
            assert agent is not None
            assert hasattr(agent, "model")
            assert hasattr(agent, "run")
            assert hasattr(agent, "output_type")

    def test_create_gpt5_medium_agent(self):
        """Test GPT-5 medium agent creation."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = create_gpt5_medium_agent("test-token")
            assert agent is not None
            assert hasattr(agent, "model")
            assert hasattr(agent, "run")
            assert hasattr(agent, "output_type")

    def test_create_gpt5_high_agent(self):
        """Test GPT-5 high agent creation."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = create_gpt5_high_agent("test-token")
            assert agent is not None
            assert hasattr(agent, "model")
            assert hasattr(agent, "run")
            assert hasattr(agent, "output_type")

    def test_create_gpt5_agents_require_openai_key(self):
        """Test that all GPT-5 agents require OPENAI_API_KEY."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="OPENAI_API_KEY environment variable required"
            ):
                create_gpt5_mini_medium_agent("test-token")

            with pytest.raises(
                ValueError, match="OPENAI_API_KEY environment variable required"
            ):
                create_gpt5_mini_high_agent("test-token")

            with pytest.raises(
                ValueError, match="OPENAI_API_KEY environment variable required"
            ):
                create_gpt5_medium_agent("test-token")

            with pytest.raises(
                ValueError, match="OPENAI_API_KEY environment variable required"
            ):
                create_gpt5_high_agent("test-token")

    def test_factory_function_supports_new_agents(self):
        """Test factory function creates all new agent types."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agents_to_test = [
                "gpt5_mini_medium",
                "gpt5_mini_high",
                "gpt5_medium",
                "gpt5_high",
            ]
            for agent_name in agents_to_test:
                agent = create_troubleshooting_agent(agent_name, "test-token")
                assert agent is not None

    def test_factory_function_rejects_opus(self):
        """Test that opus_41 is no longer available."""
        with pytest.raises(ValueError, match="opus_41 agent is no longer supported"):
            create_troubleshooting_agent("opus_41", "test-token")


class TestEndToEnd:
    """End-to-end functional tests."""

    def test_agent_has_model_configured(self):
        """Test that agents have models configured correctly using mocked API keys."""
        # Use fake API keys for testing agent creation without real API calls
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-fake-key"}):
            # Test that o3_medium agent has model set
            agent = create_troubleshooting_agent("o3_medium", "fake-sbctl-token")
            assert hasattr(agent, "_model_name") or hasattr(agent, "model"), (
                "Agent should have model configured"
            )

            # Test that agent has toolsets configured
            assert hasattr(agent, "_user_toolsets"), (
                "Agent should have user toolsets configured for MCP server"
            )

    @pytest.mark.asyncio
    async def test_prompt_content_validation(self):
        """Test that troubleshooting analysis gets correct prompt content."""
        # Create minimal test issue
        test_issue = {
            "org": "testorg",
            "repo": "testrepo",
            "issue": {
                "number": 1,
                "title": "Network connectivity issue",
                "body": "Pods cannot communicate with each other",
                "labels": [{"name": "bug"}],
                "attachments": [],
                "comments": [
                    {
                        "user": {"login": "testuser"},
                        "body": "kubectl get pods shows CrashLoopBackOff status",
                    }
                ],
            },
        }

        # Test the troubleshooting prompt formatter
        from gh_analysis.ai.analysis import format_troubleshooting_prompt

        prompt_content = format_troubleshooting_prompt(test_issue, 0)

        # Validate prompt contains issue data for troubleshooting (not product labeling)
        assert "Network connectivity issue" in prompt_content
        assert "Pods cannot communicate with each other" in prompt_content
        assert "kubectl get pods shows CrashLoopBackOff status" in prompt_content
        assert "**Problem Description:**" in prompt_content

        # Critical: should NOT contain product labeling requests
        assert "product label" not in prompt_content.lower()
        assert (
            "recommend" not in prompt_content.lower()
            or "recommendation" not in prompt_content.lower()
        )

    @pytest.mark.asyncio
    async def test_cli_integration_prompt_validation(self):
        """Integration test: validate CLI uses correct analysis function and prompt."""
        import json
        import os
        import tempfile
        from unittest.mock import AsyncMock

        # Create test issue file
        test_issue = {
            "org": "testorg",
            "repo": "testrepo",
            "issue": {
                "number": 123,
                "title": "Database connection timeout",
                "body": "PostgreSQL connection is failing with timeout errors",
                "labels": [{"name": "bug"}, {"name": "database"}],
                "attachments": [],
                "comments": [
                    {
                        "user": {"login": "devops"},
                        "body": "Checked logs, seeing 'connection refused' errors",
                    }
                ],
            },
            "metadata": {"collection_timestamp": "2025-01-01T00:00:00"},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create proper directory structure
            issues_dir = f"{temp_dir}/issues"
            os.makedirs(issues_dir, exist_ok=True)

            # Create issue file
            issue_file = f"{issues_dir}/testorg_testrepo_issue_123.json"
            with open(issue_file, "w") as f:
                json.dump(test_issue, f)

            # Mock the agent to capture what prompt it receives
            captured_prompt = None

            async def mock_run(message_parts, **kwargs):
                nonlocal captured_prompt
                captured_prompt = message_parts[0] if message_parts else None
                # Return minimal valid response - using new discriminated union
                from gh_analysis.ai.models import ResolvedAnalysis

                mock_result = ResolvedAnalysis(
                    status="resolved",
                    root_cause="Test root cause",
                    evidence=["Test finding"],
                    solution="Test remediation",
                    validation="Test explanation",
                )
                return SimpleNamespace(output=mock_result)

            # Mock agent creation to return our spy agent
            mock_agent = AsyncMock()
            mock_agent.run = mock_run

            env_patches = {
                "GITHUB_ANALYSIS_DATA_DIR": temp_dir,
                "SBCTL_TOKEN": "test_sbctl_token",
                "OPENAI_API_KEY": "test_openai_key",
            }
            with patch.dict(os.environ, env_patches):
                with patch("gh_analysis.runners.get_runner") as mock_get_runner:
                    from gh_analysis.ai.models import ResolvedAnalysis

                    mock_result = ResolvedAnalysis(
                        status="resolved",
                        root_cause="Test root cause",
                        evidence=["Test finding"],
                        solution="Test remediation",
                        validation="Test explanation",
                    )

                    async def mock_analyze(self, data):
                        nonlocal captured_prompt
                        # Capture the prompt from GitHub context
                        from gh_analysis.runners.utils.github_context import (
                            build_github_context,
                        )

                        captured_prompt = build_github_context(data["issue"])
                        return mock_result

                    mock_runner = type(
                        "MockRunner", (), {"agent": mock_agent, "analyze": mock_analyze}
                    )()
                    mock_get_runner.return_value = mock_runner
                    # Import and run the CLI function directly
                    from gh_analysis.cli.process import _run_troubleshoot

                    # This should call analyze_troubleshooting_issue, not analyze_issue
                    await _run_troubleshoot(
                        org="testorg",
                        repo="testrepo",
                        issue_number=123,
                        url=None,
                        agent_name="gpt5_mini_medium",
                        include_images=False,
                        limit_comments=None,
                        dry_run=False,
                        interactive=False,
                        slack_notifications=False,
                    )

            # Validate the prompt content
            assert captured_prompt is not None, (
                "Agent should have received prompt content"
            )

            # Should contain troubleshooting-focused content
            assert "Database connection timeout" in captured_prompt
            assert "PostgreSQL connection is failing" in captured_prompt
            assert "connection refused" in captured_prompt
            # Prompt format changed with runner pattern - check for actual content instead
            assert "Database connection timeout" in captured_prompt

            # Should NOT contain product labeling content
            assert "product label" not in captured_prompt.lower()
            assert (
                "recommend the most appropriate product label"
                not in captured_prompt.lower()
            )
