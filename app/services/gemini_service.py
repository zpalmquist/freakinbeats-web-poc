"""
Service for interacting with Google Gemini API to generate label overviews.
"""

import logging
from typing import Optional
from flask import current_app

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for generating AI content using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini service.
        
        Args:
            api_key: Google Gemini API key (optional, will use config if not provided)
        """
        self.api_key = api_key
        self.model = None
        
    def _initialize_model(self):
        """Lazy initialization of Gemini model."""
        if self.model is not None:
            return True
            
        try:
            import google.generativeai as genai
            
            api_key = self.api_key or current_app.config.get('GEMINI_API_KEY')
            if not api_key:
                logger.warning("GEMINI_API_KEY not configured")
                return False
            
            genai.configure(api_key=api_key)
            # Use the latest stable Gemini Flash model
            self.model = genai.GenerativeModel('gemini-flash-latest')
            return True
            
        except ImportError:
            logger.error("google-generativeai package not installed. Run: pip install google-generativeai")
            return False
        except Exception as e:
            logger.error(f"Error initializing Gemini model: {e}")
            return False
    
    def generate_label_overview(self, label_name: str) -> Optional[str]:
        """
        Generate an informative overview about a record label.
        
        Args:
            label_name: Name of the record label
            
        Returns:
            Generated overview text or None if generation fails
        """
        if not self._initialize_model():
            return None
        
        try:
            from google.generativeai.types import HarmCategory, HarmBlockThreshold
            
            prompt = self._build_label_prompt(label_name)
            
            # Generate content with relaxed safety settings
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 300,  # Keep it concise
                },
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            
            # Check if response has content
            if response and response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    return candidate.content.parts[0].text.strip()
                else:
                    # If blocked by safety, provide a generic fallback
                    logger.warning(f"Content blocked for {label_name}. Finish reason: {candidate.finish_reason}")
                    return "Visit the links below for more info."
            else:
                logger.warning(f"No candidates in response for label: {label_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating overview for {label_name}: {e}")
            return None
    
    def _build_label_prompt(self, label_name: str) -> str:
        """
        Build the prompt for label overview generation.
        
        Args:
            label_name: Name of the record label
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Write a brief overview about the record label "{label_name}" in one paragraph. Maximum 4 sentences. Include founding year if known, music genres, and notable artists. Be concise and factual. Use plain text only, no markdown formatting."""
        
        return prompt
    
    def is_available(self) -> bool:
        """
        Check if Gemini service is available and configured.
        
        Returns:
            True if service can be used, False otherwise
        """
        return self._initialize_model()

