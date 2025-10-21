"""Tests for the Function class."""

import os
from unittest.mock import MagicMock, patch

import pytest

from groundhog_hpc.function import Function


def dummy_function():
    return "results!"


class TestFunctionInitialization:
    """Test Function initialization."""

    def test_initialization_with_defaults(self):
        """Test Function initialization with default parameters."""

        func = Function(dummy_function)

        assert func._local_function == dummy_function
        assert func._shell_function is None
        assert func.walltime is not None

    def test_initialization_with_custom_endpoint(self, mock_endpoint_uuid):
        """Test Function initialization with custom endpoint."""

        func = Function(dummy_function, endpoint=mock_endpoint_uuid)
        assert func.endpoint == mock_endpoint_uuid

    def test_reads_script_path_from_environment(self):
        """Test that script path is read from environment variable."""

        os.environ["GROUNDHOG_SCRIPT_PATH"] = "/path/to/script.py"
        try:
            func = Function(dummy_function)
            assert func._script_path == "/path/to/script.py"
        finally:
            del os.environ["GROUNDHOG_SCRIPT_PATH"]


class TestLocalExecution:
    """Test local function execution."""

    def test_call_executes_local_function(self):
        """Test that __call__ executes the local function."""

        def add(a, b):
            return a + b

        func = Function(add)
        result = func(2, 3)
        assert result == 5


class TestRemoteExecution:
    """Test remote function execution logic."""

    def test_remote_call_outside_harness_raises(self):
        """Test that calling .remote() outside a harness raises error."""

        func = Function(dummy_function)

        with pytest.raises(RuntimeError, match="outside of a @hog.harness function"):
            func.remote()

    def test_running_in_harness_detection(self):
        """Test the _running_in_harness method."""

        func = Function(dummy_function)

        # Not in harness
        assert not func._running_in_harness()

        # In harness
        os.environ["GROUNDHOG_IN_HARNESS"] = "True"
        try:
            assert func._running_in_harness()
        finally:
            del os.environ["GROUNDHOG_IN_HARNESS"]

    def test_remote_call_lazy_initialization(self, tmp_path):
        """Test that _shell_function is lazily initialized on first .remote() call."""

        # Create a temporary script file
        script_path = tmp_path / "test_script.py"
        script_content = """import groundhog_hpc as hog

@hog.function()
def dummy_function():
    return "result"

@hog.harness()
def main():
    return dummy_function.remote()
"""
        script_path.write_text(script_content)

        os.environ["GROUNDHOG_SCRIPT_PATH"] = str(script_path)
        os.environ["GROUNDHOG_IN_HARNESS"] = "True"

        func = Function(dummy_function)

        # Initially, shell function is not initialized
        assert func._shell_function is None

        # Mock the new architecture
        mock_shell_func = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = "remote_result"

        with patch(
            "groundhog_hpc.function.script_to_submittable",
            return_value=mock_shell_func,
        ) as mock_script_to_submittable:
            with patch(
                "groundhog_hpc.function.submit_to_executor",
                return_value=mock_future,
            ) as mock_submit:
                result = func.remote()

        # After calling .remote(), _shell_function should be initialized
        assert func._shell_function is not None
        mock_script_to_submittable.assert_called_once()
        mock_submit.assert_called_once()
        assert result == "remote_result"

        # Clean up
        del os.environ["GROUNDHOG_SCRIPT_PATH"]
        del os.environ["GROUNDHOG_IN_HARNESS"]

    def test_submit_raises_without_script_path(self):
        """Test that submit raises when script_path is None."""

        os.environ["GROUNDHOG_IN_HARNESS"] = "True"
        try:
            func = Function(dummy_function)
            func._script_path = None

            with pytest.raises(ValueError, match="Could not locate source file"):
                func.submit()
        finally:
            del os.environ["GROUNDHOG_IN_HARNESS"]

    def test_submit_creates_shell_function(self, tmp_path):
        """Test that submit creates a shell function using script_to_submittable."""

        script_path = tmp_path / "test_script.py"
        script_content = "# test script content"
        script_path.write_text(script_content)

        os.environ["GROUNDHOG_IN_HARNESS"] = "True"
        try:
            func = Function(dummy_function)
            func._script_path = str(script_path)

            mock_shell_func = MagicMock()
            mock_future = MagicMock()

            with patch(
                "groundhog_hpc.function.script_to_submittable",
                return_value=mock_shell_func,
            ) as mock_script_to_submittable:
                with patch(
                    "groundhog_hpc.function.submit_to_executor",
                    return_value=mock_future,
                ):
                    func.submit()

            # Verify script_to_submittable was called with correct arguments
            mock_script_to_submittable.assert_called_once()
            call_args = mock_script_to_submittable.call_args[0]
            assert call_args[0] == str(script_path)
            assert call_args[1] == "dummy_function"
        finally:
            del os.environ["GROUNDHOG_IN_HARNESS"]


class TestSubmitMethod:
    """Test the submit() method."""

    def test_submit_raises_outside_harness(self):
        """Test that submit() raises when called outside a harness."""

        func = Function(dummy_function)

        with pytest.raises(RuntimeError, match="outside of a @hog.harness function"):
            func.submit()

    def test_submit_returns_future(self, tmp_path):
        """Test that submit() returns a Future object."""

        script_path = tmp_path / "test_script.py"
        script_path.write_text("# test")

        os.environ["GROUNDHOG_SCRIPT_PATH"] = str(script_path)
        os.environ["GROUNDHOG_IN_HARNESS"] = "True"

        try:
            func = Function(dummy_function)

            mock_future = MagicMock()
            with patch("groundhog_hpc.function.script_to_submittable"):
                with patch(
                    "groundhog_hpc.function.submit_to_executor",
                    return_value=mock_future,
                ):
                    result = func.submit()

            assert result is mock_future
        finally:
            del os.environ["GROUNDHOG_SCRIPT_PATH"]
            del os.environ["GROUNDHOG_IN_HARNESS"]

    def test_submit_serializes_arguments(self, tmp_path):
        """Test that submit() properly serializes function arguments."""

        script_path = tmp_path / "test_script.py"
        script_path.write_text("# test")

        os.environ["GROUNDHOG_SCRIPT_PATH"] = str(script_path)
        os.environ["GROUNDHOG_IN_HARNESS"] = "True"

        try:
            func = Function(dummy_function)

            mock_future = MagicMock()
            with patch("groundhog_hpc.function.script_to_submittable"):
                with patch(
                    "groundhog_hpc.function.submit_to_executor",
                    return_value=mock_future,
                ) as mock_submit:
                    with patch("groundhog_hpc.function.serialize") as mock_serialize:
                        mock_serialize.return_value = "serialized_payload"
                        func.submit(1, 2, kwarg1="value1")

            # Verify serialize was called with args and kwargs
            mock_serialize.assert_called_once()
            call_args = mock_serialize.call_args[0][0]
            assert call_args == ((1, 2), {"kwarg1": "value1"})

            # Verify submit_to_executor received the serialized payload
            assert mock_submit.call_args[1]["payload"] == "serialized_payload"
        finally:
            del os.environ["GROUNDHOG_SCRIPT_PATH"]
            del os.environ["GROUNDHOG_IN_HARNESS"]

    def test_submit_passes_endpoint_and_config(self, tmp_path, mock_endpoint_uuid):
        """Test that submit() passes endpoint and user config to submit_to_executor."""

        script_path = tmp_path / "test_script.py"
        script_path.write_text("# test")

        os.environ["GROUNDHOG_SCRIPT_PATH"] = str(script_path)
        os.environ["GROUNDHOG_IN_HARNESS"] = "True"

        try:
            func = Function(dummy_function, endpoint=mock_endpoint_uuid, account="test")

            mock_future = MagicMock()
            with patch("groundhog_hpc.function.script_to_submittable"):
                with patch(
                    "groundhog_hpc.function.submit_to_executor",
                    return_value=mock_future,
                ) as mock_submit:
                    func.submit()

            # Verify endpoint was passed
            from uuid import UUID

            assert mock_submit.call_args[0][0] == UUID(mock_endpoint_uuid)

            # Verify user config was passed
            config = mock_submit.call_args[1]["user_endpoint_config"]
            assert "account" in config
            assert config["account"] == "test"
        finally:
            del os.environ["GROUNDHOG_SCRIPT_PATH"]
            del os.environ["GROUNDHOG_IN_HARNESS"]

    def test_remote_uses_submit_internally(self, tmp_path):
        """Test that remote() calls submit() and returns its result."""

        script_path = tmp_path / "test_script.py"
        script_path.write_text("# test")

        os.environ["GROUNDHOG_SCRIPT_PATH"] = str(script_path)
        os.environ["GROUNDHOG_IN_HARNESS"] = "True"

        try:
            func = Function(dummy_function)

            mock_future = MagicMock()
            mock_future.result.return_value = "final_result"

            with patch("groundhog_hpc.function.script_to_submittable"):
                with patch(
                    "groundhog_hpc.function.submit_to_executor",
                    return_value=mock_future,
                ):
                    result = func.remote()

            # Verify that result() was called on the future
            mock_future.result.assert_called_once()
            assert result == "final_result"
        finally:
            del os.environ["GROUNDHOG_SCRIPT_PATH"]
            del os.environ["GROUNDHOG_IN_HARNESS"]

    def test_callsite_endpoint_overrides_default(self, tmp_path, mock_endpoint_uuid):
        """Test that endpoint provided at callsite overrides default endpoint."""
        script_path = tmp_path / "test_script.py"
        script_path.write_text("# test")

        os.environ["GROUNDHOG_SCRIPT_PATH"] = str(script_path)
        os.environ["GROUNDHOG_IN_HARNESS"] = "True"

        try:
            # Initialize with default endpoint
            default_endpoint = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            func = Function(dummy_function, endpoint=default_endpoint)

            mock_future = MagicMock()
            with patch("groundhog_hpc.function.script_to_submittable"):
                with patch(
                    "groundhog_hpc.function.submit_to_executor",
                    return_value=mock_future,
                ) as mock_submit:
                    # Call with override endpoint
                    func.submit(endpoint=mock_endpoint_uuid)

            # Verify the override endpoint was used
            from uuid import UUID

            assert mock_submit.call_args[0][0] == UUID(mock_endpoint_uuid)
        finally:
            del os.environ["GROUNDHOG_SCRIPT_PATH"]
            del os.environ["GROUNDHOG_IN_HARNESS"]

    def test_callsite_walltime_overrides_default(self, tmp_path):
        """Test that walltime provided at callsite overrides default walltime."""
        script_path = tmp_path / "test_script.py"
        script_path.write_text("# test")

        os.environ["GROUNDHOG_SCRIPT_PATH"] = str(script_path)
        os.environ["GROUNDHOG_IN_HARNESS"] = "True"

        try:
            # Initialize with default walltime
            func = Function(dummy_function, walltime=60)

            with patch("groundhog_hpc.function.script_to_submittable") as mock_s2s:
                with patch("groundhog_hpc.function.submit_to_executor"):
                    # Call with override walltime
                    func.submit(walltime=120)

            # Verify script_to_submittable was called with override walltime
            # Called as: script_to_submittable(script_path, function_name, walltime)
            assert mock_s2s.call_args[0][2] == 120
        finally:
            del os.environ["GROUNDHOG_SCRIPT_PATH"]
            del os.environ["GROUNDHOG_IN_HARNESS"]

    def test_callsite_user_config_overrides_default(self, tmp_path):
        """Test that user_endpoint_config at callsite overrides default config."""
        script_path = tmp_path / "test_script.py"
        script_path.write_text("# test")

        os.environ["GROUNDHOG_SCRIPT_PATH"] = str(script_path)
        os.environ["GROUNDHOG_IN_HARNESS"] = "True"

        try:
            # Initialize with default config
            func = Function(dummy_function, account="default_account", cores_per_node=4)

            mock_future = MagicMock()
            with patch("groundhog_hpc.function.script_to_submittable"):
                with patch(
                    "groundhog_hpc.function.submit_to_executor",
                    return_value=mock_future,
                ) as mock_submit:
                    # Call with override config
                    func.submit(
                        user_endpoint_config={
                            "account": "override_account",
                            "queue": "gpu",
                        }
                    )

            # Verify the override config was used
            config = mock_submit.call_args[1]["user_endpoint_config"]
            assert config["account"] == "override_account"
            assert config["queue"] == "gpu"
        finally:
            del os.environ["GROUNDHOG_SCRIPT_PATH"]
            del os.environ["GROUNDHOG_IN_HARNESS"]

    def test_worker_init_is_appended_not_overwritten(self, tmp_path):
        """Test that worker_init from callsite is appended to default, not overwritten."""
        script_path = tmp_path / "test_script.py"
        script_path.write_text("# test")

        os.environ["GROUNDHOG_SCRIPT_PATH"] = str(script_path)
        os.environ["GROUNDHOG_IN_HARNESS"] = "True"

        try:
            # Initialize with default worker_init
            default_worker_init = "module load default"
            func = Function(dummy_function, worker_init=default_worker_init)

            mock_future = MagicMock()
            with patch("groundhog_hpc.function.script_to_submittable"):
                with patch(
                    "groundhog_hpc.function.submit_to_executor",
                    return_value=mock_future,
                ) as mock_submit:
                    # Call with custom worker_init
                    custom_worker_init = "module load custom"
                    func.submit(
                        user_endpoint_config={"worker_init": custom_worker_init}
                    )

            # Verify both are present (custom + default)
            config = mock_submit.call_args[1]["user_endpoint_config"]
            assert "worker_init" in config
            # Custom should come first, then newline, then default
            assert custom_worker_init in config["worker_init"]
            assert default_worker_init in config["worker_init"]
            # Verify order: custom + "\n" + default
            assert config["worker_init"].startswith(custom_worker_init)
            assert config["worker_init"].endswith(default_worker_init)
        finally:
            del os.environ["GROUNDHOG_SCRIPT_PATH"]
            del os.environ["GROUNDHOG_IN_HARNESS"]

    def test_default_worker_init_preserved_when_no_callsite_override(self, tmp_path):
        """Test that default worker_init is used when no override provided."""
        script_path = tmp_path / "test_script.py"
        script_path.write_text("# test")

        os.environ["GROUNDHOG_SCRIPT_PATH"] = str(script_path)
        os.environ["GROUNDHOG_IN_HARNESS"] = "True"

        try:
            # Initialize with default worker_init
            default_worker_init = "module load default"
            func = Function(dummy_function, worker_init=default_worker_init)

            mock_future = MagicMock()
            with patch("groundhog_hpc.function.script_to_submittable"):
                with patch(
                    "groundhog_hpc.function.submit_to_executor",
                    return_value=mock_future,
                ) as mock_submit:
                    # Call without any override
                    func.submit()

            # Verify default worker_init is in the config
            config = mock_submit.call_args[1]["user_endpoint_config"]
            assert "worker_init" in config
            assert config["worker_init"] == default_worker_init
        finally:
            del os.environ["GROUNDHOG_SCRIPT_PATH"]
            del os.environ["GROUNDHOG_IN_HARNESS"]
