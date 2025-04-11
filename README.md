# AI-Book Generator

An AI-powered system that uses multiple specialized agents to plan, write, edit, and publish complete books with multiple chapters.

## Features

- **Book Planning**: Automatically creates a structured outline with chapter breakdowns
- **Multi-Chapter Generation**: Creates coherent, interconnected chapters that form a complete narrative
- **Editing and Refinement**: Improves writing quality through dedicated editing agents
- **Book Cover Design Ideas**: Generates detailed cover design descriptions
- **Publishing**: Compiles chapters into a complete book with proper formatting
- **Single Story Mode**: Can also generate individual short stories

## Requirements

- Python 3.7+
- Google Gemini API key

## Setup

1. Install required dependencies:
   ```
   pip install python-dotenv google-generativeai
   ```

2. Create a `.env` file in the project root with your API key:
   ```
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```

## Usage

### Generate a Complete Book

```python
from main import book_pipeline

# Create a book with 5 chapters (default)
book_pipeline("space exploration in the distant future")

# Create a book with a custom number of chapters
book_pipeline("medieval fantasy adventure", num_chapters=7)
```

### Generate a Single Story

```python
from main import story_pipeline

# Create a short stand-alone story
story_pipeline("a magical forest")
```

## Output

The system creates:

1. A main book file in Markdown format inside the `books` directory
2. Individual chapter files in a subdirectory named after the book
3. Terminal output showing progress throughout the generation process

## Agent System Architecture

The system consists of specialized AI agents that work together:

1. **Book Planner Agent**: Creates the overall structure and chapter outlines
2. **Chapter Writer Agent**: Writes individual chapters based on the outline
3. **Chapter Editor Agent**: Improves the quality of each chapter
4. **Table of Contents Generator**: Creates a structured contents listing
5. **Cover Description Agent**: Creates visual design concepts for the book cover
6. **Book Publisher Agent**: Assembles and formats the final book

## Customization

You can modify the system by:
- Adjusting chapter length in the `chapter_writer_agent` function
- Changing output formats in the `book_publisher_agent` function
- Adding additional agents for specialized tasks

## Future Enhancements

Potential improvements:
- PDF export capability
- Character consistency tracking
- Illustration generation
- Genre-specific writing agents
- Interactive book planning interface
