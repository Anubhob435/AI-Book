from dotenv import load_dotenv
import os
import json
import time
import datetime
from pathlib import Path

# Update the import for the Google Generative AI client
from google import genai

load_dotenv()
# Configure the client with your API key
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

# Existing single story agents
def headline_agent(topic: str) -> str:
    prompt = f"Come up with an engaging and creative title for a story about: {topic}"
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()

def writer_agent(title: str) -> str:
    prompt = f"Write a fictional short story based on the title: '{title}'. Make it around 700-1000 words."
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()

def editor_agent(story: str) -> str:
    prompt = f"Please edit the following story for grammar, clarity, and flow. Keep the creative style:\n\n{story}"
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()

def publisher_agent(title: str, story: str):
    filename = title.replace(" ", "_").replace(":", "").lower() + ".txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Title: {title}\n\n{story}")
    print(f"✅ Story saved as '{filename}'")


def story_pipeline(topic: str):
    print("🎯 Generating headline...")
    title = headline_agent(topic)
    print(f"📝 Title: {title}")

    print("📖 Writing story...")
    raw_story = writer_agent(title)

    print("✏️ Editing story...")
    edited_story = editor_agent(raw_story)

    print("📤 Publishing story...")
    publisher_agent(title, edited_story)

# Book metadata management
class BookMetadata:
    """Class to manage book metadata tracking"""
    
    def __init__(self, book_dir, book_title):
        self.book_dir = Path(book_dir)
        self.safe_title = book_title.replace(" ", "_").replace(":", "").lower()
        self.chapters_dir = self.book_dir / self.safe_title
        self.metadata_file = self.chapters_dir / "book_metadata.json"
        
        # Create directories if they don't exist
        self.book_dir.mkdir(exist_ok=True)
        self.chapters_dir.mkdir(exist_ok=True)
    
    def initialize(self, book_plan, cover_description, toc, topic):
        """Initialize a new book's metadata"""
        metadata = {
            "book_info": {
                "title": book_plan["book_title"],
                "description": book_plan["book_description"],
                "topic": topic,
                "creation_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "last_updated": datetime.datetime.now().strftime("%Y-%m-%d"),
                "status": "planning",  # planning, in-progress, complete
                "total_chapters": len(book_plan["chapters"]),
                "completed_chapters": 0,
                "estimated_word_count": 0,
                "estimated_page_count": 0
            },
            "generation_info": {
                "book_plan": book_plan,
                "cover_description": cover_description,
                "toc": toc
            },
            "chapters": []
        }
        
        # Create chapter entries with status tracking
        for chapter in book_plan["chapters"]:
            metadata["chapters"].append({
                "chapter_number": chapter["chapter_number"],
                "chapter_title": chapter["chapter_title"],
                "synopsis": chapter["synopsis"],
                "key_points": chapter["key_points"],
                "status": "planned",  # planned, writing, written, edited, published
                "creation_date": None,
                "last_edited": None,
                "publication_date": None,
                "word_count": 0,
                "page_count": 0,
                "filename": None
            })
        
        # Save metadata
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        return metadata
    
    def load(self):
        """Load existing book metadata"""
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def update_chapter(self, chapter_index, filename, content):
        """Update a chapter's metadata after writing/editing"""
        metadata = self.load()
        if not metadata:
            raise FileNotFoundError(f"Book metadata not found for {self.safe_title}")
        
        # Calculate metrics
        word_count = len(content.split())
        # Estimate page count (250 words per page is a common estimate)
        page_count = round(word_count / 250, 1)
        
        # Update chapter info
        chapter = metadata["chapters"][chapter_index]
        chapter["status"] = "published"
        chapter["last_edited"] = datetime.datetime.now().strftime("%Y-%m-%d")
        chapter["publication_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
        chapter["word_count"] = word_count
        chapter["page_count"] = page_count
        chapter["filename"] = str(filename)
        
        # Update book level info
        metadata["book_info"]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d")
        metadata["book_info"]["completed_chapters"] = sum(1 for chapter in metadata["chapters"] if chapter["status"] == "published")
        
        if metadata["book_info"]["completed_chapters"] < metadata["book_info"]["total_chapters"]:
            metadata["book_info"]["status"] = "in-progress"
        else:
            metadata["book_info"]["status"] = "complete"
        
        # Recalculate total word and page count
        total_word_count = sum(chapter["word_count"] for chapter in metadata["chapters"] if chapter["word_count"] > 0)
        metadata["book_info"]["estimated_word_count"] = total_word_count
        metadata["book_info"]["estimated_page_count"] = round(total_word_count / 250, 1)
        
        # Save updated metadata
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        return metadata
    
    def get_next_chapter_index(self):
        """Get the index of the next chapter to write"""
        metadata = self.load()
        if not metadata:
            return None
        
        for i, chapter in enumerate(metadata["chapters"]):
            if chapter["status"] == "planned":
                return i
        
        return None
    
    def get_book_info(self):
        """Get a summary of the book's current state"""
        metadata = self.load()
        if not metadata:
            return None
        
        return {
            "title": metadata["book_info"]["title"],
            "status": metadata["book_info"]["status"],
            "completed": f"{metadata['book_info']['completed_chapters']}/{metadata['book_info']['total_chapters']}",
            "word_count": metadata["book_info"]["estimated_word_count"],
            "page_count": metadata["book_info"]["estimated_page_count"]
        }
    
    def get_all_metadata(self):
        """Get the complete metadata for export"""
        return self.load()

# New book creation agents
def book_planner_agent(topic: str, num_chapters: int) -> dict:
    """Creates a detailed book outline with chapters based on the topic"""
    prompt = f"""
    Create a detailed outline for a book about '{topic}' with {num_chapters} chapters.
    For each chapter, provide:
    1. A compelling chapter title
    2. A brief synopsis of what happens in the chapter (100-150 words)
    3. Key points or scenes to include
    
    Also provide an overall book title and a short description of the book.
    Format your response as a JSON object with this structure:
    {{
        "book_title": "Title of the Book",
        "book_description": "Short description of the book's premise",
        "chapters": [
            {{
                "chapter_number": 1,
                "chapter_title": "Chapter Title",
                "synopsis": "Brief description of the chapter",
                "key_points": ["point 1", "point 2", "point 3"]
            }},
            // additional chapters...
        ]
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        book_plan = json.loads(response.text)
        return book_plan
    except Exception as e:
        print(f"Error in creating book plan: {e}")
        # Fallback to a simpler format if JSON parsing fails
        return {
            "book_title": f"Book about {topic}",
            "book_description": f"A collection of stories about {topic}",
            "chapters": [{"chapter_number": i, "chapter_title": f"Chapter {i}", 
                         "synopsis": f"A story about {topic}", 
                         "key_points": [f"Explore {topic}"]} 
                        for i in range(1, num_chapters + 1)]
        }

def chapter_writer_agent(book_plan: dict, chapter_index: int) -> str:
    """Writes a full chapter based on the book plan"""
    chapter = book_plan["chapters"][chapter_index]
    
    prompt = f"""
    Write Chapter {chapter['chapter_number']}: "{chapter['chapter_title']}" for the book "{book_plan['book_title']}".
    
    Use this synopsis as a guide: {chapter['synopsis']}
    
    Include these key points/scenes:
    {', '.join(chapter['key_points'])}
    
    Write a compelling chapter of approximately 1500-2000 words that advances the overall narrative.
    Use engaging dialogue, vivid descriptions, and well-developed characters.
    
    If this is chapter 1, introduce the main characters and setting.
    If this is the final chapter, provide appropriate closure while leaving room for reader interpretation.
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()

def chapter_editor_agent(chapter_content: str, chapter_title: str) -> str:
    """Edits a chapter for grammar, style, and coherence"""
    prompt = f"""
    Please edit the following chapter titled "{chapter_title}" for grammar, clarity, flow, and narrative coherence.
    Preserve the creative style and voice while improving the overall quality.
    
    Chapter content:
    {chapter_content}
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()

def table_of_contents_generator(book_plan: dict) -> str:
    """Generates a table of contents for the book"""
    toc = f"# {book_plan['book_title']}\n\n"
    toc += "## Table of Contents\n\n"
    
    for chapter in book_plan["chapters"]:
        toc += f"{chapter['chapter_number']}. {chapter['chapter_title']}\n"
    
    return toc

def book_cover_description_agent(book_plan: dict) -> str:
    """Generates a description for a book cover"""
    prompt = f"""
    Create a detailed description for a book cover design for the book titled "{book_plan['book_title']}".
    Book description: {book_plan['book_description']}
    
    Include suggestions for:
    1. Main imagery or illustration
    2. Color scheme
    3. Typography style
    4. Overall mood/feeling the cover should convey
    
    The description should provide clear visual direction for a book cover designer.
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()

def book_pipeline(topic: str, num_chapters: int = 5):
    """Complete pipeline to create and publish a book"""
    print(f"📚 Starting book creation process on topic: {topic}")
    
    # Plan the book
    print("🧠 Planning book structure...")
    book_plan = book_planner_agent(topic, num_chapters)
    print(f"📑 Book Title: {book_plan['book_title']}")
    print(f"📝 Book Plan: {len(book_plan['chapters'])} chapters planned")
    
    # Generate cover description
    print("🎨 Generating cover description...")
    cover_description = book_cover_description_agent(book_plan)
    
    # Generate table of contents
    print("📋 Creating table of contents...")
    toc = table_of_contents_generator(book_plan)
    
    # Initialize metadata manager and create initial metadata
    book_metadata = BookMetadata("books", book_plan["book_title"])
    book_metadata.initialize(book_plan, cover_description, toc, topic)
    
    print(f"✅ Book structure planned and saved. You can now generate chapters one by one.")
    print(f"📘 To generate a chapter, use: write_next_chapter('{book_plan['book_title']}')")
    
    # Return the book title for reference
    return book_plan['book_title']

def write_next_chapter(book_title: str):
    """Write the next chapter in the book sequence"""
    # Initialize the metadata manager
    book_metadata = BookMetadata("books", book_title)
    metadata = book_metadata.load()
    
    if not metadata:
        print(f"❌ Book '{book_title}' not found. Please create a book plan first with book_pipeline().")
        return
    
    # Get the next chapter to write
    chapter_index = book_metadata.get_next_chapter_index()
    
    if chapter_index is None:
        print("✅ All chapters have been completed. You can now compile the book.")
        print(f"📚 To compile the book, use: compile_book('{book_title}')")
        return
    
    chapter = metadata["chapters"][chapter_index]
    book_plan = metadata["generation_info"]["book_plan"]
    
    print(f"📖 Writing chapter {chapter['chapter_number']}: {chapter['chapter_title']}...")
    raw_chapter = chapter_writer_agent(book_plan, chapter_index)
    
    print(f"✏️ Editing chapter {chapter['chapter_number']}...")
    edited_chapter = chapter_editor_agent(raw_chapter, chapter['chapter_title'])
    
    # Save the chapter
    chapter_filename = book_metadata.chapters_dir / f"chapter_{chapter['chapter_number']:02d}_{chapter['chapter_title'].replace(' ', '_').lower()}.md"
    with open(chapter_filename, "w", encoding="utf-8") as f:
        f.write(f"# Chapter {chapter['chapter_number']}: {chapter['chapter_title']}\n\n")
        f.write(edited_chapter)
    
    # Update metadata with chapter details
    book_metadata.update_chapter(chapter_index, chapter_filename, edited_chapter)
    
    # Get updated information
    book_info = book_metadata.get_book_info()
    
    print(f"✅ Chapter {chapter['chapter_number']} completed and saved as '{chapter_filename}'")
    print(f"📊 Book Progress: {book_info['completed']} chapters | {book_info['word_count']} words | ~{book_info['page_count']} pages")
    
    if book_info['status'] != 'complete':
        print(f"📝 To continue with the next chapter, use: write_next_chapter('{book_title}')")
    else:
        print("📚 All chapters completed! You can now compile the book.")
        print(f"📚 To compile the book, use: compile_book('{book_title}')")

def compile_book(book_title: str, force: bool = False):
    """Compile all written chapters into a complete book"""
    # Initialize the metadata manager
    book_metadata = BookMetadata("books", book_title)
    metadata = book_metadata.load()
    
    if not metadata:
        print(f"❌ Book '{book_title}' not found. Please create a book plan first with book_pipeline().")
        return
    
    book_plan = metadata["generation_info"]["book_plan"]
    cover_description = metadata["generation_info"]["cover_description"]
    toc = metadata["generation_info"]["toc"]
    
    completed = sum(1 for chapter in metadata["chapters"] if chapter["status"] == "published")
    total = len(metadata["chapters"])
    
    if completed < total and not force:
        print(f"⚠️ Not all chapters are complete. {completed}/{total} chapters have been written.")
        print(f"📝 To continue writing, use: write_next_chapter('{book_title}')")
        print(f"📚 Or force compilation with incomplete chapters by using: compile_book('{book_title}', force=True)")
        return
    
    # Compile chapters
    chapters = []
    for chapter in metadata["chapters"]:
        if chapter["status"] == "published" and chapter["filename"]:
            with open(chapter["filename"], "r", encoding="utf-8") as f:
                # Skip the title line (first line) since we'll add it in the book compilation
                content = f.read()
                header_end = content.find('\n\n')
                if header_end > -1:
                    chapter_content = content[header_end + 2:]
                else:
                    chapter_content = content
                chapters.append(chapter_content)
        else:
            # For incomplete chapters, add a placeholder if force=True
            if force:
                chapters.append("*[This chapter is not yet written]*")
            
    # Compile book content
    book_filename = book_metadata.book_dir / f"{book_metadata.safe_title}.md"
    book_content = f"# {metadata['book_info']['title']}\n\n"
    book_content += f"*{metadata['book_info']['description']}*\n\n"
    book_content += f"**Topic:** {metadata['book_info']['topic']}\n\n"
    book_content += f"**Created:** {metadata['book_info']['creation_date']}\n"
    book_content += f"**Last Updated:** {metadata['book_info']['last_updated']}\n"
    book_content += f"**Word Count:** {metadata['book_info']['estimated_word_count']}\n"
    book_content += f"**Page Count:** {metadata['book_info']['estimated_page_count']}\n\n"
    book_content += "---\n\n"
    book_content += toc
    book_content += "\n\n---\n\n"
    
    # Add cover description
    book_content += "## Cover Design Description\n\n"
    book_content += f"{cover_description}\n\n"
    book_content += "---\n\n"
    
    # Add each chapter
    for i, chapter_content in enumerate(chapters):
        if i < len(metadata["chapters"]):
            chapter = metadata["chapters"][i]
            book_content += f"## Chapter {chapter['chapter_number']}: {chapter['chapter_title']}\n\n"
            book_content += f"{chapter_content}\n\n"
            book_content += "---\n\n"
    
    # Write to file
    with open(book_filename, "w", encoding="utf-8") as f:
        f.write(book_content)
    
    print(f"✅ Book successfully compiled and published as '{book_filename}'")
    print(f"📚 Individual chapters are available in '{book_metadata.chapters_dir}'")
    
    # Generate a JSON export of all metadata
    export_filename = book_metadata.book_dir / f"{book_metadata.safe_title}_metadata_export.json"
    with open(export_filename, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📊 Complete book metadata exported to '{export_filename}'")

def get_book_status(book_title: str = None):
    """Get the status of a book or list all available books"""
    book_dir = Path("books")
    
    if not book_dir.exists():
        print("📚 No books found yet. Create one with book_pipeline()")
        return
    
    # If no specific book is requested, list all books
    if book_title is None:
        books = []
        for item in book_dir.iterdir():
            if item.is_dir():
                metadata_file = item / "book_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, "r", encoding="utf-8") as f:
                            metadata = json.load(f)
                            books.append({
                                "title": metadata["book_info"]["title"],
                                "status": metadata["book_info"]["status"],
                                "completed": f"{metadata['book_info']['completed_chapters']}/{metadata['book_info']['total_chapters']}",
                                "word_count": metadata["book_info"]["estimated_word_count"],
                                "page_count": metadata["book_info"]["estimated_page_count"]
                            })
                    except Exception as e:
                        print(f"Error reading metadata for {item.name}: {e}")
        
        if not books:
            print("📚 No books found yet. Create one with book_pipeline()")
            return
        
        print("\n📚 AVAILABLE BOOKS:")
        print("=" * 80)
        for book in books:
            print(f"Title: {book['title']}")
            print(f"Status: {book['status']} ({book['completed']} chapters)")
            print(f"Word Count: {book['word_count']} (~{book['page_count']} pages)")
            print("-" * 80)
        
    else:
        # Get status for a specific book
        book_metadata = BookMetadata("books", book_title)
        book_info = book_metadata.get_book_info()
        
        if not book_info:
            print(f"❌ Book '{book_title}' not found.")
            return
        
        metadata = book_metadata.get_all_metadata()
        
        print(f"\n📚 BOOK STATUS: {book_info['title']}")
        print("=" * 80)
        print(f"Status: {book_info['status']}")
        print(f"Chapters: {book_info['completed']}")
        print(f"Word Count: {book_info['word_count']}")
        print(f"Page Count: {book_info['page_count']}")
        print("-" * 80)
        print("CHAPTERS:")
        
        for chapter in metadata["chapters"]:
            status_emoji = "✅" if chapter["status"] == "published" else "⏳"
            print(f"{status_emoji} Chapter {chapter['chapter_number']}: {chapter['chapter_title']}")
            print(f"   Status: {chapter['status']}")
            if chapter["publication_date"]:
                print(f"   Published: {chapter['publication_date']}")
            if chapter["word_count"] > 0:
                print(f"   Words: {chapter["word_count"]} (~{chapter['page_count']} pages)")
            print()

# Example usage
if __name__ == "__main__":
    # For a single story
    # story_pipeline("a magical forest")
    
    # For a complete book, chapter by chapter
    # Step 1: Create book plan
    book_title = book_pipeline("space exploration in the distant future", num_chapters=3)
    
    # Step 2: Write each chapter one at a time
    write_next_chapter(book_title)
    
    # Step 3: After all chapters are written, compile the book
    compile_book(book_title)
    
    # Get status of books
    # get_book_status()  # List all books
    # get_book_status(book_title)  # Get details about a specific book
    
    # For demonstration, uncomment one of these lines:
    #book_pipeline("magical adventure in a hidden kingdom", num_chapters=3)
