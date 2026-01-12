import google.generativeai as genai
from app.settings import settings
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
        self.default_model = settings.gemini_model
        self.fallback_models = settings.gemini_fallback_models

    def generate_content_with_fallback(self, prompt: str) -> str:
        """
        Generate content using the default model, falling back to others if needed.
        """
        models_to_try = [self.default_model] + self.fallback_models
        errors = []
        
        for model_name in models_to_try:
            try:
                logger.info(f"Attempting generation with model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_msg = f"[{model_name}] {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
                continue
                
        raise Exception(f"All Gemini models failed. Errors: {'; '.join(errors)}")

    def list_available_models(self) -> list[dict]:
        """List available models and their methods."""
        try:
            models = []
            for m in genai.list_models():
                models.append({
                    "name": m.name,
                    "supported_generation_methods": m.supported_generation_methods
                })
            return models
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def check_health(self) -> dict:
        """Check API key validity and model availability."""
        status = {
            "api_key_configured": bool(settings.gemini_api_key),
            "current_model": self.default_model,
            "generation_test": "skipped"
        }
        
        if settings.gemini_api_key:
            try:
                # Minimal test generation
                model = genai.GenerativeModel(self.default_model)
                response = model.generate_content("Hello", generation_config={"max_output_tokens": 5})
                status["generation_test"] = "success"
                status["test_response"] = response.text
            except Exception as e:
                status["generation_test"] = "failed"
                status["error"] = str(e)
                
        return status

gemini_client = GeminiClient()
