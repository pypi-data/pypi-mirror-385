"""Examples of using msgflux parsers.

This file demonstrates how to use the various document parsers
available in msgflux to extract text, images, and metadata from
different file formats.
"""

import asyncio
from msgflux.data.parsers import Parser


def pdf_example():
    """Example: Parse a PDF document."""
    print("=" * 50)
    print("PDF Parser Example")
    print("=" * 50)

    # Create a PDF parser
    parser = Parser.pdf("pypdf", encode_images_base64=True)

    # Parse a document
    response = parser("path/to/document.pdf")

    # Access the parsed content
    print(f"Text content:\n{response.data['text'][:200]}...")
    print(f"\nNumber of images: {len(response.data['images'])}")
    print(f"Number of pages: {response.data['metadata']['num_pages']}")

    # Access images
    for img_name, img_data in response.data['images'].items():
        print(f"Image: {img_name} (base64 encoded)")


def xlsx_example():
    """Example: Parse an Excel spreadsheet."""
    print("\n" + "=" * 50)
    print("XLSX Parser Example")
    print("=" * 50)

    # Create an XLSX parser with markdown tables
    parser = Parser.xlsx("openpyxl", table_format="markdown")

    # Parse a spreadsheet
    response = parser("path/to/spreadsheet.xlsx")

    # Access the parsed content
    print(f"Text content:\n{response.data['text'][:200]}...")
    print(f"\nNumber of sheets: {response.data['metadata']['num_sheets']}")
    print(f"Sheet names: {response.data['metadata']['sheet_names']}")


def pptx_example():
    """Example: Parse a PowerPoint presentation."""
    print("\n" + "=" * 50)
    print("PPTX Parser Example")
    print("=" * 50)

    # Create a PPTX parser with speaker notes
    parser = Parser.pptx("python_pptx", include_notes=True)

    # Parse a presentation
    response = parser("path/to/presentation.pptx")

    # Access the parsed content
    print(f"Text content:\n{response.data['text'][:200]}...")
    print(f"\nNumber of slides: {response.data['metadata']['num_slides']}")
    print(f"Number of images: {len(response.data['images'])}")


def docx_example():
    """Example: Parse a Word document."""
    print("\n" + "=" * 50)
    print("DOCX Parser Example")
    print("=" * 50)

    # Create a DOCX parser
    parser = Parser.docx("python_docx", table_format="markdown")

    # Parse a document
    response = parser("path/to/document.docx")

    # Access the parsed content
    print(f"Text content:\n{response.data['text'][:200]}...")
    print(f"\nNumber of paragraphs: {response.data['metadata']['num_paragraphs']}")
    print(f"Number of tables: {response.data['metadata']['num_tables']}")
    print(f"Number of images: {response.data['metadata']['num_images']}")


def url_example():
    """Example: Parse a document from a URL."""
    print("\n" + "=" * 50)
    print("URL Parser Example")
    print("=" * 50)

    # Create a parser
    parser = Parser.pdf("pypdf")

    # Parse from URL
    response = parser("https://example.com/document.pdf")

    print(f"Successfully parsed document from URL")
    print(f"Number of pages: {response.data['metadata']['num_pages']}")


async def async_example():
    """Example: Parse documents asynchronously."""
    print("\n" + "=" * 50)
    print("Async Parser Example")
    print("=" * 50)

    # Create parsers
    pdf_parser = Parser.pdf("pypdf")
    xlsx_parser = Parser.xlsx("openpyxl")

    # Parse multiple documents concurrently
    pdf_task = pdf_parser.acall("path/to/document.pdf")
    xlsx_task = xlsx_parser.acall("path/to/spreadsheet.xlsx")

    # Wait for both to complete
    pdf_response, xlsx_response = await asyncio.gather(pdf_task, xlsx_task)

    print(f"PDF parsed: {pdf_response.data['metadata']['num_pages']} pages")
    print(f"XLSX parsed: {xlsx_response.data['metadata']['num_sheets']} sheets")


def bytes_example():
    """Example: Parse a document from bytes."""
    print("\n" + "=" * 50)
    print("Bytes Parser Example")
    print("=" * 50)

    # Read file as bytes
    with open("path/to/document.pdf", "rb") as f:
        file_bytes = f.read()

    # Create parser and parse bytes
    parser = Parser.pdf("pypdf")
    response = parser(file_bytes)

    print(f"Successfully parsed document from bytes")
    print(f"Number of pages: {response.data['metadata']['num_pages']}")


def csv_example():
    """Example: Parse a CSV file."""
    print("\n" + "=" * 50)
    print("CSV Parser Example")
    print("=" * 50)

    # Create a CSV parser
    parser = Parser.csv("csv", delimiter=",", has_header=True)

    # Parse a CSV file
    response = parser("path/to/data.csv")

    # Access the parsed content
    print(f"Text content:\n{response.data['text'][:200]}...")
    print(f"\nNumber of rows: {response.data['metadata']['num_rows']}")
    print(f"Number of columns: {response.data['metadata']['num_cols']}")


def html_example():
    """Example: Parse an HTML document."""
    print("\n" + "=" * 50)
    print("HTML Parser Example")
    print("=" * 50)

    # Create an HTML parser
    parser = Parser.html("beautifulsoup", extract_links=True)

    # Parse an HTML file
    response = parser("path/to/page.html")

    # Access the parsed content
    print(f"Text content:\n{response.data['text'][:200]}...")
    print(f"\nNumber of links: {response.data['metadata']['num_links']}")
    if response.data['links']:
        print(f"First link: {response.data['links'][0]}")


def markdown_example():
    """Example: Parse a Markdown document."""
    print("\n" + "=" * 50)
    print("Markdown Parser Example")
    print("=" * 50)

    # Create a Markdown parser
    parser = Parser.markdown("markdown", extract_code_blocks=True)

    # Parse a Markdown file
    response = parser("path/to/README.md")

    # Access the parsed content
    print(f"Text content:\n{response.data['text'][:200]}...")
    print(f"\nNumber of headings: {response.data['metadata']['num_headings']}")
    print(f"Number of code blocks: {response.data['metadata']['num_code_blocks']}")
    if response.data['front_matter']:
        print(f"Front matter: {response.data['front_matter']}")


def email_example():
    """Example: Parse an email file."""
    print("\n" + "=" * 50)
    print("Email Parser Example")
    print("=" * 50)

    # Create an Email parser
    parser = Parser.email("email", extract_attachments=True)

    # Parse an email file
    response = parser("path/to/message.eml")

    # Access the parsed content
    print(f"From: {response.data['headers']['from']}")
    print(f"Subject: {response.data['headers']['subject']}")
    print(f"\nBody:\n{response.data['body'][:200]}...")
    print(f"\nNumber of attachments: {response.data['metadata']['num_attachments']}")


def chunking_example():
    """Example: Chunk a document for processing."""
    print("\n" + "=" * 50)
    print("Chunking Example")
    print("=" * 50)

    # Create a parser
    parser = Parser.pdf("pypdf")

    # Parse a document
    response = parser("path/to/large_document.pdf")

    # Chunk by character count
    chunks = parser.chunk_text(
        response.data["text"],
        chunk_size=1000,
        chunk_overlap=200
    )
    print(f"Character-based chunks: {len(chunks)}")
    print(f"First chunk:\n{chunks[0][:200]}...")

    # Chunk by token count (requires tiktoken)
    token_chunks = parser.chunk_by_tokens(
        response.data["text"],
        max_tokens=512,
        overlap_tokens=50
    )
    print(f"\nToken-based chunks: {len(token_chunks)}")


def list_available_parsers():
    """List all available parsers."""
    print("\n" + "=" * 50)
    print("Available Parsers")
    print("=" * 50)

    # Get all parser types
    parser_types = Parser.parser_types()
    print(f"Parser types: {parser_types}")

    # Get providers for each type
    providers = Parser.providers()
    for parser_type, provider_list in providers.items():
        print(f"\n{parser_type.upper()} parsers:")
        for provider in provider_list:
            print(f"  - {provider}")


if __name__ == "__main__":
    # List available parsers
    list_available_parsers()

    # Note: The following examples require actual files
    # Uncomment and modify paths as needed

    # pdf_example()
    # xlsx_example()
    # pptx_example()
    # docx_example()
    # csv_example()
    # html_example()
    # markdown_example()
    # email_example()
    # chunking_example()
    # url_example()
    # bytes_example()

    # Run async example
    # asyncio.run(async_example())

    print("\n" + "=" * 50)
    print("Examples completed!")
    print("=" * 50)
