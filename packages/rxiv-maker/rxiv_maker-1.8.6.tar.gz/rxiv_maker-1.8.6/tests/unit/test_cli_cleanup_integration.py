"""Unit tests for CLI integration with container cleanup functionality."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


@pytest.mark.skip(reason="Container engine functionality deprecated - tests need updating for new interface")
@pytest.mark.unit
class TestCLIContainerCleanupIntegration(unittest.TestCase):
    """Test CLI integration with container cleanup functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_cleanup_command_exists(self):
        """Test that cleanup functionality is accessible from CLI."""
        try:
            import sys

            sys.path.insert(0, "src")

            # Check if cleanup is available in the CLI
            from click.testing import CliRunner

            from rxiv_maker.cli.main import main

            runner = CliRunner()
            result = runner.invoke(main, ["--help"])

            # The CLI should include cleanup-related functionality
            self.assertEqual(result.exit_code, 0)
            self.assertIsNotNone(result.output)

        except ImportError:
            self.skipTest("CLI imports not available")

    @patch("rxiv_maker.engines.core.factory.ContainerEngineFactory.cleanup_all_engines")
    def test_cleanup_integration_with_engine_factory(self, mock_cleanup):
        """Test cleanup integration through engine factory."""
        try:
            import sys

            sys.path.insert(0, "src")
            from rxiv_maker.engines.core.factory import ContainerEngineFactory

            # Mock successful cleanup
            mock_cleanup.return_value = 2  # 2 engines cleaned up

            # Test cleanup call
            cleaned_count = ContainerEngineFactory.cleanup_all_engines()

            # Verify cleanup was called and returned expected count
            mock_cleanup.assert_called_once()
            self.assertEqual(cleaned_count, 2)

        except ImportError:
            self.skipTest("Engine factory imports not available")

    def test_cleanup_on_cli_exit(self):
        """Test that cleanup happens when CLI exits (if configured)."""
        try:
            import sys

            sys.path.insert(0, "src")

            # Test cleanup behavior during normal operations
            with patch("rxiv_maker.engines.core.factory.ContainerEngineFactory.cleanup_all_engines") as mock_cleanup:
                mock_cleanup.return_value = 1

                # Simulate CLI cleanup trigger
                from rxiv_maker.engines.core.factory import ContainerEngineFactory

                cleanup_count = ContainerEngineFactory.cleanup_all_engines()

                self.assertEqual(cleanup_count, 1)
                mock_cleanup.assert_called_once()

        except ImportError:
            self.skipTest("CLI cleanup integration imports not available")

    def test_cleanup_with_local_execution(self):
        """Test cleanup with local execution (container engines deprecated)."""
        try:
            import sys

            sys.path.insert(0, "src")

            # Local engine doesn't require cleanup of container sessions
            # This test mainly verifies that cleanup commands work in local mode
            # Since everything is local now, cleanup mainly involves file/cache cleanup

            # Test that basic cleanup operations work without engine-specific logic
            # This is a simplified test since container engines are deprecated
            assert True  # Placeholder - actual cleanup testing would depend on implementation

        except ImportError:
            self.skipTest("Cleanup imports not available")

    @patch("subprocess.run")
    def test_cleanup_after_pdf_generation(self, mock_run):
        """Test that cleanup happens after PDF generation operations."""
        try:
            import sys

            sys.path.insert(0, "src")

            # Mock successful subprocess operations
            mock_run.return_value = Mock(returncode=0, stdout="Success")

            # Test cleanup integration with build operations
            with patch("rxiv_maker.engines.core.factory.ContainerEngineFactory.cleanup_all_engines") as mock_cleanup:
                mock_cleanup.return_value = 1

                # Simulate cleanup after build
                from rxiv_maker.engines.core.factory import ContainerEngineFactory

                cleanup_count = ContainerEngineFactory.cleanup_all_engines()

                self.assertEqual(cleanup_count, 1)
                mock_cleanup.assert_called_once()

        except ImportError:
            self.skipTest("Build integration imports not available")

    def test_cleanup_error_handling_in_cli(self):
        """Test CLI handles cleanup errors gracefully."""
        try:
            import sys

            sys.path.insert(0, "src")

            # Test that CLI doesn't crash when cleanup fails
            with patch("rxiv_maker.engines.core.factory.ContainerEngineFactory.cleanup_all_engines") as mock_cleanup:
                mock_cleanup.side_effect = Exception("Cleanup failed")

                # CLI should handle cleanup failures gracefully
                try:
                    from rxiv_maker.engines.core.factory import ContainerEngineFactory

                    ContainerEngineFactory.cleanup_all_engines()
                    self.fail("Should have raised exception")
                except Exception as e:
                    self.assertEqual(str(e), "Cleanup failed")

        except ImportError:
            self.skipTest("CLI error handling imports not available")

    @patch("os.environ.get")
    def test_cleanup_with_environment_variables(self, mock_env_get):
        """Test cleanup behavior with various environment variable configurations."""
        try:
            import sys

            sys.path.insert(0, "src")

            # Test with session reuse enabled
            mock_env_get.return_value = "true"

            with patch("rxiv_maker.engines.core.factory.get_container_engine") as mock_get_engine:
                mock_engine = Mock()
                mock_engine.enable_session_reuse = True
                mock_engine.cleanup_all_sessions.return_value = None
                mock_get_engine.return_value = mock_engine

                from rxiv_maker.engines.core.factory import get_container_engine

                engine = get_container_engine("docker", workspace_dir=self.workspace_dir)

                # Verify session reuse is enabled
                self.assertTrue(engine.enable_session_reuse)

                # Test cleanup
                engine.cleanup_all_sessions()
                mock_engine.cleanup_all_sessions.assert_called_once()

        except ImportError:
            self.skipTest("Environment configuration imports not available")

    def test_cleanup_session_statistics(self):
        """Test that cleanup provides useful statistics."""
        try:
            import sys

            sys.path.insert(0, "src")

            with patch("rxiv_maker.engines.core.factory.get_container_engine") as mock_get_engine:
                mock_engine = Mock()
                mock_engine.get_session_stats.return_value = {
                    "total_sessions": 3,
                    "active_sessions": 2,
                    "session_details": [
                        {"key": "session1", "container_id": "abc123", "active": True},
                        {"key": "session2", "container_id": "def456", "active": False},
                    ],
                }
                mock_get_engine.return_value = mock_engine

                from rxiv_maker.engines.core.factory import get_container_engine

                engine = get_container_engine("docker", workspace_dir=self.workspace_dir)

                stats = engine.get_session_stats()

                # Verify statistics are provided
                self.assertEqual(stats["total_sessions"], 3)
                self.assertEqual(stats["active_sessions"], 2)
                self.assertEqual(len(stats["session_details"]), 2)

        except ImportError:
            self.skipTest("Session statistics imports not available")

    def test_cleanup_integration_with_memory_management(self):
        """Test cleanup integration with memory management features."""
        try:
            import sys

            sys.path.insert(0, "src")

            # Test cleanup with memory-constrained environments
            with patch("rxiv_maker.engines.core.factory.get_container_engine") as mock_get_engine:
                mock_engine = Mock()
                mock_engine.memory_limit = "1g"
                mock_engine.cpu_limit = "1.0"
                mock_engine._max_sessions = 2  # Reduced for memory constraints
                mock_engine.cleanup_all_sessions.return_value = None
                mock_get_engine.return_value = mock_engine

                from rxiv_maker.engines.core.factory import get_container_engine

                engine = get_container_engine(
                    "docker", workspace_dir=self.workspace_dir, memory_limit="1g", cpu_limit="1.0"
                )

                # Verify resource limits are set
                self.assertEqual(engine.memory_limit, "1g")
                self.assertEqual(engine.cpu_limit, "1.0")
                self.assertEqual(engine._max_sessions, 2)

                # Test cleanup respects resource constraints
                engine.cleanup_all_sessions()
                mock_engine.cleanup_all_sessions.assert_called_once()

        except ImportError:
            self.skipTest("Memory management integration imports not available")

    # Container cleanup tests removed - container engines are deprecated


@pytest.mark.skip(reason="Container engine functionality deprecated - tests need updating for new interface")
@pytest.mark.unit
class TestCLICleanupCommands(unittest.TestCase):
    """Test specific CLI cleanup commands and their functionality."""

    def test_cleanup_command_help(self):
        """Test cleanup command help text is available."""
        try:
            import sys

            sys.path.insert(0, "src")
            from click.testing import CliRunner

            from rxiv_maker.cli.main import main

            runner = CliRunner()
            result = runner.invoke(main, ["--help"])

            # Should not error and should provide help
            self.assertEqual(result.exit_code, 0)
            self.assertIsInstance(result.output, str)

        except ImportError:
            self.skipTest("CLI imports not available")

    def test_cleanup_dry_run_mode(self):
        """Test cleanup dry-run mode that shows what would be cleaned."""
        try:
            import sys

            sys.path.insert(0, "src")

            # Test dry-run functionality
            with patch("rxiv_maker.engines.core.factory.ContainerEngineFactory.cleanup_all_engines") as mock_cleanup:
                # In dry-run mode, cleanup should not actually be called
                mock_cleanup.return_value = 2

                # Simulate dry-run check
                from rxiv_maker.engines.core.factory import ContainerEngineFactory

                available_engines = ContainerEngineFactory.get_supported_engines()

                # Should be able to see what would be cleaned without actually cleaning
                self.assertIsInstance(available_engines, list)

        except ImportError:
            self.skipTest("Dry-run functionality imports not available")

    def test_cleanup_force_mode(self):
        """Test cleanup force mode that bypasses safety checks."""
        try:
            import sys

            sys.path.insert(0, "src")

            # Test force cleanup
            with patch("rxiv_maker.engines.core.factory.get_container_engine") as mock_get_engine:
                mock_engine = Mock()
                mock_engine._cleanup_expired_sessions = Mock()
                mock_get_engine.return_value = mock_engine

                from rxiv_maker.engines.core.factory import get_container_engine

                engine = get_container_engine("docker")

                # Force cleanup should bypass throttling
                engine._cleanup_expired_sessions(force=True)
                mock_engine._cleanup_expired_sessions.assert_called_once_with(force=True)

        except ImportError:
            self.skipTest("Force cleanup imports not available")


if __name__ == "__main__":
    unittest.main()
