"""
Unit tests for GeminiService.

This module tests the Google Gemini AI integration service, including:
- Service initialization and configuration
- AI overview generation for record labels
- Error handling and safety filter responses
- Fallback behavior for blocked content
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.gemini_service import GeminiService


class TestGeminiServiceInit:
    """Test GeminiService initialization."""
    
    def test_init_with_api_key(self):
        """Test initialization with provided API key."""
        service = GeminiService(api_key='test_key_123')
        
        assert service.api_key == 'test_key_123'
        assert service.model is None  # Lazy initialization
    
    def test_init_without_api_key(self):
        """Test initialization without API key."""
        service = GeminiService()
        
        assert service.api_key is None
        assert service.model is None


class TestInitializeModel:
    """Test the _initialize_model method."""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_initialize_model_success(self, mock_model_class, mock_configure, app_context):
        """Test successful model initialization."""
        app_context.config['GEMINI_API_KEY'] = 'test_api_key'
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        service = GeminiService()
        result = service._initialize_model()
        
        assert result is True
        assert service.model == mock_model
        mock_configure.assert_called_once_with(api_key='test_api_key')
        mock_model_class.assert_called_once_with('gemini-flash-latest')
    
    def test_initialize_model_no_api_key(self, app_context):
        """Test initialization fails when no API key is configured."""
        app_context.config['GEMINI_API_KEY'] = None
        
        service = GeminiService()
        result = service._initialize_model()
        
        assert result is False
        assert service.model is None
    
    def test_initialize_model_import_error(self, app_context):
        """Test initialization fails when google.generativeai is not installed."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        
        with patch.dict('sys.modules', {'google.generativeai': None}):
            service = GeminiService()
            result = service._initialize_model()
            
            assert result is False
    
    @patch('google.generativeai.configure')
    def test_initialize_model_already_initialized(self, mock_configure, app_context):
        """Test that model is not re-initialized if already set."""
        service = GeminiService()
        service.model = Mock()  # Already initialized
        
        result = service._initialize_model()
        
        assert result is True
        mock_configure.assert_not_called()  # Should not configure again
    
    @patch('google.generativeai.configure')
    def test_initialize_model_configure_error(self, mock_configure, app_context):
        """Test initialization handles configuration errors."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        mock_configure.side_effect = Exception("API configuration failed")
        
        service = GeminiService()
        result = service._initialize_model()
        
        assert result is False


class TestGenerateLabelOverview:
    """Test the generate_label_overview method."""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_overview_success(self, mock_model_class, mock_configure, app_context):
        """Test successful label overview generation."""
        # Setup mocks
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Mock response with proper structure
        mock_part = Mock()
        mock_part.text = "Blue Note Records was founded in 1939. It's a legendary jazz label. Artists include Miles Davis and John Coltrane. Known for iconic album covers."
        
        mock_content = Mock()
        mock_content.parts = [mock_part]
        
        mock_candidate = Mock()
        mock_candidate.content = mock_content
        
        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        
        mock_model.generate_content.return_value = mock_response
        
        # Test
        service = GeminiService()
        result = service.generate_label_overview("Blue Note Records")
        
        assert result is not None
        assert "Blue Note Records" in result
        assert "1939" in result
        mock_model.generate_content.assert_called_once()
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_overview_content_blocked(self, mock_model_class, mock_configure, app_context):
        """Test handling when content is blocked by safety filters."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Mock blocked response (finish_reason = 2 means SAFETY)
        mock_candidate = Mock()
        mock_candidate.content = None
        mock_candidate.finish_reason = 2
        
        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        
        mock_model.generate_content.return_value = mock_response
        
        # Test
        service = GeminiService()
        result = service.generate_label_overview("Test Label")
        
        assert result == "Visit the links below for more info."
    
    def test_generate_overview_model_not_initialized(self, app_context):
        """Test overview generation fails when model cannot be initialized."""
        app_context.config['GEMINI_API_KEY'] = None  # No API key
        
        service = GeminiService()
        result = service.generate_label_overview("Test Label")
        
        assert result is None
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_overview_api_exception(self, mock_model_class, mock_configure, app_context):
        """Test handling of API exceptions during generation."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        mock_model.generate_content.side_effect = Exception("API Error")
        
        service = GeminiService()
        result = service.generate_label_overview("Test Label")
        
        assert result is None
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_overview_empty_response(self, mock_model_class, mock_configure, app_context):
        """Test handling when API returns empty response."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        mock_response = Mock()
        mock_response.candidates = []
        
        mock_model.generate_content.return_value = mock_response
        
        service = GeminiService()
        result = service.generate_label_overview("Test Label")
        
        assert result is None
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_overview_with_generation_config(self, mock_model_class, mock_configure, app_context):
        """Test that generation uses correct configuration."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Mock successful response
        mock_part = Mock()
        mock_part.text = "Test overview"
        mock_content = Mock()
        mock_content.parts = [mock_part]
        mock_candidate = Mock()
        mock_candidate.content = mock_content
        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response
        
        service = GeminiService()
        service.generate_label_overview("Test Label")
        
        # Verify generation_config was passed
        call_args = mock_model.generate_content.call_args
        assert 'generation_config' in call_args.kwargs
        config = call_args.kwargs['generation_config']
        assert config['temperature'] == 0.7
        assert config['max_output_tokens'] == 300
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_overview_with_safety_settings(self, mock_model_class, mock_configure, app_context):
        """Test that generation uses relaxed safety settings."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Mock successful response
        mock_part = Mock()
        mock_part.text = "Test overview"
        mock_content = Mock()
        mock_content.parts = [mock_part]
        mock_candidate = Mock()
        mock_candidate.content = mock_content
        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response
        
        service = GeminiService()
        service.generate_label_overview("Test Label")
        
        # Verify safety_settings were passed
        call_args = mock_model.generate_content.call_args
        assert 'safety_settings' in call_args.kwargs
        assert len(call_args.kwargs['safety_settings']) == 4  # 4 harm categories


class TestBuildLabelPrompt:
    """Test the _build_label_prompt method."""
    
    def test_build_prompt_includes_label_name(self):
        """Test that prompt includes the label name."""
        service = GeminiService()
        prompt = service._build_label_prompt("Blue Note Records")
        
        assert "Blue Note Records" in prompt
    
    def test_build_prompt_requests_paragraph(self):
        """Test that prompt requests one paragraph format."""
        service = GeminiService()
        prompt = service._build_label_prompt("Test Label")
        
        assert "one paragraph" in prompt.lower()
        assert "4 sentences" in prompt.lower()
    
    def test_build_prompt_requests_plain_text(self):
        """Test that prompt requests no markdown formatting."""
        service = GeminiService()
        prompt = service._build_label_prompt("Test Label")
        
        assert "plain text" in prompt.lower()
        assert "no markdown" in prompt.lower()
    
    def test_build_prompt_requests_key_info(self):
        """Test that prompt requests founding year, genres, and artists."""
        service = GeminiService()
        prompt = service._build_label_prompt("Test Label")
        
        assert "founding year" in prompt.lower()
        assert "genres" in prompt.lower()
        assert "notable artists" in prompt.lower()


class TestIsAvailable:
    """Test the is_available method."""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_is_available_when_configured(self, mock_model_class, mock_configure, app_context):
        """Test is_available returns True when properly configured."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        mock_model_class.return_value = Mock()
        
        service = GeminiService()
        assert service.is_available() is True
    
    def test_is_available_when_no_api_key(self, app_context):
        """Test is_available returns False when no API key."""
        app_context.config['GEMINI_API_KEY'] = None
        
        service = GeminiService()
        assert service.is_available() is False
    
    def test_is_available_when_import_fails(self, app_context):
        """Test is_available returns False when package not installed."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        
        with patch.dict('sys.modules', {'google.generativeai': None}):
            service = GeminiService()
            assert service.is_available() is False


class TestGeminiServiceIntegration:
    """Integration tests for GeminiService."""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_multiple_overview_generations(self, mock_model_class, mock_configure, app_context):
        """Test generating multiple overviews in sequence."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Mock different responses for different labels
        def generate_response(prompt, **kwargs):
            mock_part = Mock()
            if "Blue Note" in str(prompt):
                mock_part.text = "Blue Note overview"
            elif "Motown" in str(prompt):
                mock_part.text = "Motown overview"
            else:
                mock_part.text = "Generic overview"
            
            mock_content = Mock()
            mock_content.parts = [mock_part]
            mock_candidate = Mock()
            mock_candidate.content = mock_content
            mock_response = Mock()
            mock_response.candidates = [mock_candidate]
            return mock_response
        
        mock_model.generate_content.side_effect = generate_response
        
        service = GeminiService()
        
        result1 = service.generate_label_overview("Blue Note Records")
        result2 = service.generate_label_overview("Motown")
        result3 = service.generate_label_overview("Unknown Label")
        
        assert result1 == "Blue Note overview"
        assert result2 == "Motown overview"
        assert result3 == "Generic overview"
        assert mock_model.generate_content.call_count == 3
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_service_reuses_initialized_model(self, mock_model_class, mock_configure, app_context):
        """Test that model is only initialized once."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Mock successful response
        mock_part = Mock()
        mock_part.text = "Test overview"
        mock_content = Mock()
        mock_content.parts = [mock_part]
        mock_candidate = Mock()
        mock_candidate.content = mock_content
        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response
        
        service = GeminiService()
        
        # Generate multiple times
        service.generate_label_overview("Label 1")
        service.generate_label_overview("Label 2")
        
        # Model should only be initialized once
        assert mock_model_class.call_count == 1
        assert mock_configure.call_count == 1


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_overview_empty_label_name(self, mock_model_class, mock_configure, app_context):
        """Test overview generation with empty label name."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Mock successful response even for empty name
        mock_part = Mock()
        mock_part.text = "Generic overview"
        mock_content = Mock()
        mock_content.parts = [mock_part]
        mock_candidate = Mock()
        mock_candidate.content = mock_content
        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response
        
        service = GeminiService()
        result = service.generate_label_overview("")
        
        # Should still attempt to generate
        assert result is not None
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_overview_special_characters(self, mock_model_class, mock_configure, app_context):
        """Test overview generation with special characters in label name."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        mock_part = Mock()
        mock_part.text = "Label overview with special chars"
        mock_content = Mock()
        mock_content.parts = [mock_part]
        mock_candidate = Mock()
        mock_candidate.content = mock_content
        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response
        
        service = GeminiService()
        
        # Test with various special characters
        result1 = service.generate_label_overview("Label & Records")
        result2 = service.generate_label_overview("Label's Music")
        result3 = service.generate_label_overview("Label (Europe)")
        
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_overview_whitespace_handling(self, mock_model_class, mock_configure, app_context):
        """Test that generated text is properly trimmed."""
        app_context.config['GEMINI_API_KEY'] = 'test_key'
        
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Mock response with extra whitespace
        mock_part = Mock()
        mock_part.text = "  \n  Test overview with whitespace  \n  "
        mock_content = Mock()
        mock_content.parts = [mock_part]
        mock_candidate = Mock()
        mock_candidate.content = mock_content
        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response
        
        service = GeminiService()
        result = service.generate_label_overview("Test Label")
        
        assert result == "Test overview with whitespace"
        assert not result.startswith(" ")
        assert not result.endswith(" ")


class TestPromptBuilding:
    """Test prompt building variations."""
    
    def test_prompt_consistent_format(self):
        """Test that prompts have consistent format."""
        service = GeminiService()
        
        prompt1 = service._build_label_prompt("Label A")
        prompt2 = service._build_label_prompt("Label B")
        
        # Both should have similar structure
        assert "one paragraph" in prompt1.lower()
        assert "one paragraph" in prompt2.lower()
        assert "4 sentences" in prompt1.lower()
        assert "4 sentences" in prompt2.lower()
    
    def test_prompt_length_reasonable(self):
        """Test that prompts are not excessively long."""
        service = GeminiService()
        prompt = service._build_label_prompt("Test Label")
        
        # Prompt should be reasonable length (not too long)
        assert len(prompt) < 500  # Reasonable upper limit
        assert len(prompt) > 50   # Should have meaningful content


# Fixtures for this test module
@pytest.fixture
def mock_gemini_response():
    """Create a mock successful Gemini response."""
    mock_part = Mock()
    mock_part.text = "This is a test label overview with information about genres and artists."
    
    mock_content = Mock()
    mock_content.parts = [mock_part]
    
    mock_candidate = Mock()
    mock_candidate.content = mock_content
    
    mock_response = Mock()
    mock_response.candidates = [mock_candidate]
    
    return mock_response


@pytest.fixture
def mock_blocked_response():
    """Create a mock blocked/filtered Gemini response."""
    mock_candidate = Mock()
    mock_candidate.content = None
    mock_candidate.finish_reason = 2  # SAFETY block
    
    mock_response = Mock()
    mock_response.candidates = [mock_candidate]
    
    return mock_response

