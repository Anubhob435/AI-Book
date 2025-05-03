# AI-Book Generator

An AI-powered system that uses multiple specialized agents to plan, write, edit, format, and publish complete books with multiple chapters.

## Features

- **Book Planning**: Automatically creates a structured outline with chapter breakdowns
- **Multi-Chapter Generation**: Creates coherent, interconnected chapters that form a complete narrative
- **Editing and Refinement**: Improves writing quality through dedicated editing agents
- **Advanced Formatting**: Enhances readability with proper markdown formatting for dialogue and emphasis
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
from main import book_pipeline, write_next_chapter, compile_book

# Create a book plan with 5 chapters (default)
book_title = book_pipeline("space exploration in the distant future")

# Write chapters one at a time
write_next_chapter(book_title)  # Write chapter 1
write_next_chapter(book_title)  # Write chapter 2
# ... continue until all chapters are written

# Compile the completed book
compile_book(book_title)

# Or create a book with a custom number of chapters
book_title = book_pipeline("medieval fantasy adventure", num_chapters=7)
```

### Generate a Single Story

```python
from main import story_pipeline

# Create a short stand-alone story
story_pipeline("a magical forest")
```

### Enhance Formatting for Existing Books

```python
from editor import enhance_chapter_formatting, enhance_book_formatting

# Format a single chapter
enhance_chapter_formatting("books/your_book_name/chapter_01_intro.md")

# Format all chapters in a book
enhance_book_formatting("Your Book Title")
```

## Output

The system creates:

1. A main book file in Markdown format inside the `books` directory
2. Individual chapter files in a subdirectory named after the book
3. Chapter illustrations in an `illustrations` folder within each book directory
4. Terminal output showing progress throughout the generation process

## Agent System Architecture

The system consists of specialized AI agents that work together:

1. **Book Planner Agent**: Creates the overall structure and chapter outlines
2. **Chapter Writer Agent**: Writes individual chapters based on the outline
3. **Chapter Editor Agent**: Improves the quality of each chapter
4. **Format Agent**: Enhances content with proper markdown styling and dialogue formatting
5. **Illustrator Agent**: Creates illustrations for key scenes in each chapter
6. **Table of Contents Generator**: Creates a structured contents listing
7. **Cover Description Agent**: Creates visual design concepts for the book cover
8. **Book Publisher Agent**: Assembles and formats the final book

## Customization

You can modify the system by:
- Adjusting chapter length in the `chapter_writer_agent` function
- Changing output formats in the `book_publisher_agent` function
- Adding additional agents for specialized tasks
- Modifying formatting rules in the `FormatAgent` class

## Future Enhancements

Potential improvements:
- PDF export capability
- Character consistency tracking
- Genre-specific writing agents
- Interactive book planning interface
- Enhanced illustration generation
