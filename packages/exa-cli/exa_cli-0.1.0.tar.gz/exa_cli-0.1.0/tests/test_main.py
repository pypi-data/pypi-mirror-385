import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner
from main import app, get_exa_client
from click.exceptions import Exit as ClickExit

runner = CliRunner()


class TestAPIKeyValidation:
    def test_get_exa_client_missing_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises((SystemExit, ClickExit)):
                get_exa_client()
    
    def test_get_exa_client_with_key(self):
        with patch.dict(os.environ, {"EXA_API_KEY": "test-key"}):
            with patch("main.Exa") as mock_exa:
                client = get_exa_client()
                mock_exa.assert_called_once_with(api_key="test-key")


class TestSearchCommand:
    @patch("main.get_exa_client")
    def test_search_basic(self, mock_get_client):
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.results = [
            Mock(title="Test Title", url="https://example.com", text="Test snippet")
        ]
        mock_exa.search.return_value = mock_result
        mock_get_client.return_value = mock_exa
        
        result = runner.invoke(app, ["search", "test query"])
        
        assert result.exit_code == 0
        mock_exa.search.assert_called_once()
        assert mock_exa.search.call_args.kwargs["query"] == "test query"
        assert mock_exa.search.call_args.kwargs["num_results"] == 10
        assert mock_exa.search.call_args.kwargs["use_autoprompt"] is True
    
    @patch("main.get_exa_client")
    def test_search_with_options(self, mock_get_client):
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.results = []
        mock_exa.search.return_value = mock_result
        mock_get_client.return_value = mock_exa
        
        result = runner.invoke(app, [
            "search", "rust async",
            "--num", "5",
            "--include", "github.com,rust-lang.org",
            "--exclude", "reddit.com",
            "--no-autoprompt"
        ])
        
        assert result.exit_code == 0
        call_kwargs = mock_exa.search.call_args.kwargs
        assert call_kwargs["query"] == "rust async"
        assert call_kwargs["num_results"] == 5
        assert call_kwargs["include_domains"] == ["github.com", "rust-lang.org"]
        assert call_kwargs["exclude_domains"] == ["reddit.com"]
        assert call_kwargs["use_autoprompt"] is False


class TestSimilarCommand:
    @patch("main.get_exa_client")
    def test_similar_basic(self, mock_get_client):
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.results = [
            Mock(title="Similar Page", url="https://similar.com")
        ]
        mock_exa.find_similar.return_value = mock_result
        mock_get_client.return_value = mock_exa
        
        result = runner.invoke(app, ["similar", "https://example.com"])
        
        assert result.exit_code == 0
        mock_exa.find_similar.assert_called_once()
        assert mock_exa.find_similar.call_args.kwargs["url"] == "https://example.com"
        assert mock_exa.find_similar.call_args.kwargs["num_results"] == 10
    
    @patch("main.get_exa_client")
    def test_similar_with_num_results(self, mock_get_client):
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.results = []
        mock_exa.find_similar.return_value = mock_result
        mock_get_client.return_value = mock_exa
        
        result = runner.invoke(app, ["similar", "https://example.com", "--num", "3"])
        
        assert result.exit_code == 0
        assert mock_exa.find_similar.call_args.kwargs["num_results"] == 3


class TestContentsCommand:
    @patch("main.get_exa_client")
    def test_contents_single_url(self, mock_get_client):
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.results = [
            Mock(title="Page Title", url="https://example.com", text="Page content")
        ]
        mock_exa.get_contents.return_value = mock_result
        mock_get_client.return_value = mock_exa
        
        result = runner.invoke(app, ["contents", "https://example.com"])
        
        assert result.exit_code == 0
        mock_exa.get_contents.assert_called_once()
        assert mock_exa.get_contents.call_args.kwargs["urls"] == ["https://example.com"]
        assert mock_exa.get_contents.call_args.kwargs["text"] == {"max_characters": 5000}
    
    @patch("main.get_exa_client")
    def test_contents_multiple_urls(self, mock_get_client):
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.results = []
        mock_exa.get_contents.return_value = mock_result
        mock_get_client.return_value = mock_exa
        
        result = runner.invoke(app, [
            "contents",
            "https://example.com",
            "https://another.com"
        ])
        
        assert result.exit_code == 0
        assert mock_exa.get_contents.call_args.kwargs["urls"] == [
            "https://example.com",
            "https://another.com"
        ]
    
    @patch("main.get_exa_client")
    def test_contents_no_text(self, mock_get_client):
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.results = []
        mock_exa.get_contents.return_value = mock_result
        mock_get_client.return_value = mock_exa
        
        result = runner.invoke(app, ["contents", "https://example.com", "--no-text"])
        
        assert result.exit_code == 0
        assert mock_exa.get_contents.call_args.kwargs["text"] is None


class TestAnswerCommand:
    @patch("main.get_exa_client")
    def test_answer_basic(self, mock_get_client):
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.answer = "Test answer"
        mock_result.citations = [
            Mock(title="Citation 1", url="https://citation1.com")
        ]
        mock_exa.answer.return_value = mock_result
        mock_get_client.return_value = mock_exa
        
        result = runner.invoke(app, ["answer", "what is rust"])
        
        assert result.exit_code == 0
        mock_exa.answer.assert_called_once()
        assert mock_exa.answer.call_args.kwargs["query"] == "what is rust"
        assert mock_exa.answer.call_args.kwargs["text"] is False
    
    @patch("main.get_exa_client")
    def test_answer_with_text(self, mock_get_client):
        mock_exa = Mock()
        mock_result = Mock()
        mock_result.answer = "Test answer"
        mock_result.citations = []
        mock_exa.answer.return_value = mock_result
        mock_get_client.return_value = mock_exa
        
        result = runner.invoke(app, ["answer", "what is rust", "--text"])
        
        assert result.exit_code == 0
        assert mock_exa.answer.call_args.kwargs["text"] is True
