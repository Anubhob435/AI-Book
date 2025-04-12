import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import datetime

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# Initialize the client with the API key
client = genai.Client(api_key=api_key)

def generate_illustration(description: str, prefix: str = "illustration") -> str:
    """
    Generate an illustration based on the provided description
    
    Args:
        description: A text description of what to generate
        prefix: A prefix for the filename (default: 'illustration')
        
    Returns:
        The file path of the saved illustration
    """
    # Create illustrations directory if it doesn't exist
    illustrations_dir = os.path.join(os.path.dirname(__file__), 'illustrations')
    if not os.path.exists(illustrations_dir):
        os.makedirs(illustrations_dir)
    
    # Clean up prefix to ensure it's filename-safe
    safe_prefix = prefix.replace(" ", "_").replace(":", "").lower()
    
    # Call the AI model to generate the image
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=description,
        config=types.GenerateContentConfig(
          response_modalities=['Text', 'Image']
        )
    )

    # Generate a unique filename using timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_prefix}_{timestamp}.png"
    filepath = os.path.join(illustrations_dir, filename)

    # Process and save the generated image
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(f"Image generation note: {part.text}")
        elif part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            image.save(filepath)
            print(f"Image saved to: {filepath}")
            return filepath
    
    # If no image was generated, return None
    print("Warning: No image was generated")
    return None

# Example usage - only run if this file is executed directly
if __name__ == "__main__":
    contents = ('Hi, can you create a 3d rendered image of a pig '
                'with wings and a top hat flying over a happy '
                'futuristic scifi city with lots of greenery?')
    
    generate_illustration(contents)