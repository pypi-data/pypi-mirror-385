"""
Tests for the web interface functionality and serve command.
"""

import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from ugit.commands.add import add
from ugit.commands.commit import commit
from ugit.commands.init import init
from ugit.commands.serve import serve

pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="Web interface tests are skipped on Windows due to file locking issues.",
)


class TestServeCommand:
    """Test the serve command functionality."""

    def test_serve_without_web_dependencies(self):
        """Test serve command when web dependencies are not available."""
        # Create temp repo for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            init()  # Initialize repo so ensure_repository() doesn't exit

            with patch(
                "ugit.web.server.create_app",
                side_effect=ImportError("No module named 'fastapi'"),
            ):
                result = serve()
                assert result == 1  # Should return error code

    def test_serve_command_parameters(self):
        """Test serve command with different parameters."""
        # Create a temporary repository
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)

            # Initialize repository
            init()

            # Mock the web server components
            with patch("ugit.web.server.create_app") as mock_create_app, patch(
                "uvicorn.run"
            ) as mock_uvicorn:

                mock_app = MagicMock()
                mock_create_app.return_value = mock_app

                # Test default parameters
                result = serve(open_browser=False)
                assert result is None or result == 0
                mock_create_app.assert_called_once()
                mock_uvicorn.assert_called_once()

    def test_serve_in_non_repository(self):
        """Test serve command outside of repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)  # Don't initialize - should fail

            result = serve(open_browser=False)
            assert result == 1


class TestWebServer:
    """Test the web server endpoints and functionality."""

    @pytest.fixture
    def test_repo(self):
        """Create a test repository with some content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = os.path.join(temp_dir, "test_repo")
            os.makedirs(repo_path)
            os.chdir(repo_path)

            # Initialize repository
            init()

            # Create some test files
            with open("README.md", "w") as f:
                f.write("# Test Repository\n\nThis is a test.\n")

            with open("main.py", "w") as f:
                f.write('print("Hello, World!")\n')

            # Create subdirectory with files
            os.makedirs("src", exist_ok=True)
            with open("src/utils.py", "w") as f:
                f.write("def helper():\n    return 'helper'\n")

            with open("src/config.py", "w") as f:
                f.write("DEBUG = True\nVERSION = '1.0.0'\n")

            # Create nested directory structure
            os.makedirs("tests/unit", exist_ok=True)
            with open("tests/test_main.py", "w") as f:
                f.write("def test_main():\n    assert True\n")

            with open("tests/unit/test_utils.py", "w") as f:
                f.write(
                    "from src.utils import helper\n\ndef test_helper():\n    assert helper() == 'helper'\n"
                )

            # Add all files to staging
            add(["."])

            # Commit the files
            commit("Initial commit with test files and nested structure")

            yield repo_path

    @pytest.fixture
    def client(self, test_repo):
        """Create a test client for the web application."""
        try:
            from ugit.web.server import create_app

            app = create_app(test_repo)
            with TestClient(app) as client:
                yield client
        except ImportError:
            pytest.skip("Web dependencies not available")

    def test_index_page(self, client):
        """Test the main index page."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_api_files_endpoint(self, client):
        """Test the files API endpoint."""
        response = client.get("/api/files")
        assert response.status_code == 200

        data = response.json()
        assert "files" in data
        assert len(data["files"]) > 0

        # Check that committed files are present
        file_names = [f["name"] for f in data["files"]]
        assert "README.md" in file_names
        assert "main.py" in file_names
        assert "src" in file_names  # Directory should be listed
        assert "tests" in file_names

    def test_api_file_content(self, client):
        """Test retrieving file content."""
        response = client.get("/api/file?path=README.md")
        assert response.status_code == 200

        data = response.json()
        assert "content" in data
        assert "Test Repository" in data["content"]

    def test_api_file_content_nonexistent(self, client):
        """Test retrieving content for non-existent file."""
        response = client.get("/api/file?path=nonexistent.txt")
        assert response.status_code == 404

    def test_api_directory_navigation(self, client):
        """Test navigating into directories."""
        response = client.get("/api/files?path=src")
        assert response.status_code == 200

        data = response.json()
        file_names = [f["name"] for f in data["files"]]
        assert "utils.py" in file_names
        assert "config.py" in file_names

    def test_api_commits_endpoint(self, client):
        """Test the commits API endpoint."""
        response = client.get("/api/commits")
        assert response.status_code == 200

        data = response.json()
        assert "commits" in data
        assert len(data["commits"]) > 0

        # Check commit structure
        commit_data = data["commits"][0]
        assert "sha" in commit_data  # ugit uses 'sha' not 'hash'
        assert "message" in commit_data
        assert "Initial commit" in commit_data["message"]

    def test_static_files(self, client):
        """Test serving static files."""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]

    def test_error_handling(self, client):
        """Test error handling for invalid requests."""
        # Test invalid file path
        response = client.get("/static/invalid.css")
        assert response.status_code == 404


class TestWebIntegration:
    """Integration tests for the web interface."""

    def test_full_web_workflow(self):
        """Test a complete workflow through the web interface."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = os.path.join(temp_dir, "integration_test")
            os.makedirs(repo_path)
            os.chdir(repo_path)

            # Initialize repository
            init()

            # Create and commit first set of files
            with open("file1.txt", "w") as f:
                f.write("First file content\n")
            add(["file1.txt"])
            commit("First commit")

            # Create and commit second set with nested structure
            with open("file2.txt", "w") as f:
                f.write("Second file content\n")

            os.makedirs("docs", exist_ok=True)
            with open("docs/guide.md", "w") as f:
                f.write("# User Guide\n\nThis is documentation.\n")

            os.makedirs("src/components", exist_ok=True)
            with open("src/main.js", "w") as f:
                f.write("console.log('Hello from main.js');\n")

            with open("src/components/button.js", "w") as f:
                f.write("export function Button() { return 'button'; }\n")

            add(["."])
            commit("Add more files with nested structure")

            try:
                from ugit.web.server import create_app

                app = create_app(repo_path)
                client = TestClient(app)

                # Test main page loads
                response = client.get("/")
                assert response.status_code == 200

                # Test file listing shows committed files
                response = client.get("/api/files")
                assert response.status_code == 200
                data = response.json()
                file_names = [f["name"] for f in data["files"]]
                assert "file1.txt" in file_names
                assert "file2.txt" in file_names
                assert "docs" in file_names  # Should show directories
                assert "src" in file_names

                # Test file content retrieval
                response = client.get("/api/file?path=file1.txt")
                assert response.status_code == 200
                data = response.json()
                assert "First file content" in data["content"]

                # Test nested file content
                response = client.get("/api/file?path=docs/guide.md")
                assert response.status_code == 200
                data = response.json()
                assert "User Guide" in data["content"]

                # Test deeply nested file
                response = client.get("/api/file?path=src/components/button.js")
                assert response.status_code == 200
                data = response.json()
                assert "Button" in data["content"]

                # Test directory navigation
                response = client.get("/api/files?path=src")
                assert response.status_code == 200
                data = response.json()
                file_names = [f["name"] for f in data["files"]]
                assert "main.js" in file_names
                assert "components" in file_names

                # Test commits endpoint shows both commits
                response = client.get("/api/commits")
                assert response.status_code == 200
                data = response.json()
                assert len(data["commits"]) >= 2

                commit_messages = [c["message"] for c in data["commits"]]
                assert any("First commit" in msg for msg in commit_messages)
                assert any("nested structure" in msg for msg in commit_messages)

            except ImportError:
                pytest.skip("Web dependencies not available")

            except Exception as e:
                pytest.fail(f"Integration test failed: {e}")
