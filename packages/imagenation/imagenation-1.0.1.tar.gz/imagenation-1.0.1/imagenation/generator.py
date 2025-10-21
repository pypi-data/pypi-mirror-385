"""
Core image generation functionality using Google's Imagen
"""

import os
import time
from io import BytesIO

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import PIL.Image

# Load environment variables
load_dotenv()


class ImagenationGenerator:
    """AI Image Generator using Google's Imagen model"""
    
    def __init__(self, api_key: str = None, rate_limit_delay: float = 12.0):
        """
        Initialize the generator with Google API key
        
        Args:
            api_key: Google API key. If None, loads from GOOGLE_API_KEY environment variable
            rate_limit_delay: Delay between requests in seconds (default: 12s for free tier 5 RPM)
        """
        if api_key is None:
            api_key = os.getenv('GOOGLE_API_KEY')
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found. Provide api_key parameter or set GOOGLE_API_KEY environment variable.")
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-preview-image-generation"
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
    
    def _rate_limit_wait(self):
        """Wait if needed to respect rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last
            print(f"Rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def generate_text_to_image(self, text_input: str, output_path: str) -> bool:
        """
        Generate image from text prompt only
        
        Args:
            text_input: Text prompt for image generation
            output_path: Path to save the generated image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._rate_limit_wait()
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[text_input],
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            return self._save_generated_image(response, output_path)
        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                print(f"Rate limit exceeded. Consider increasing delay or upgrading to paid tier.")
            print(f"Error generating text-to-image: {e}")
            return False
    
    def generate_text_image_to_image(self, text_input: str, input_image_path: str, output_path: str) -> bool:
        """
        Generate image from text prompt and input image
        
        Args:
            text_input: Text prompt for image generation
            input_image_path: Path to input image
            output_path: Path to save the generated image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(input_image_path):
                print(f"Input image not found: {input_image_path}")
                return False
            
            self._rate_limit_wait()
            
            image = PIL.Image.open(input_image_path)
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[text_input, image],
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            return self._save_generated_image(response, output_path)
        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                print(f"Rate limit exceeded. Consider increasing delay or upgrading to paid tier.")
            print(f"Error generating text+image-to-image: {e}")
            return False
    
    def _save_generated_image(self, response, output_path: str) -> bool:
        """
        Save generated image from response
        
        Args:
            response: API response containing image data
            output_path: Path to save the image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    print(f"Generated text: {part.text}")
                elif part.inline_data is not None:
                    image = Image.open(BytesIO(part.inline_data.data))
                    
                    # Ensure output directory exists
                    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
                    
                    image.save(output_path)
                    print(f"Image saved to: {output_path}")
                    return True
            
            print("No image data found in response")
            return False
        except Exception as e:
            print(f"Error saving image: {e}")
            return False