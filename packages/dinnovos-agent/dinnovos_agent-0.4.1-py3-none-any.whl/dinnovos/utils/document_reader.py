"""Document Reader utility for Dinnovos Agent"""

from typing import List, Dict, Optional, Union
from pathlib import Path
import os


class DocumentReader:
    """
    DocumentReader - Flexible document reading utility
    
    Reads PDF and TXT files and provides methods to integrate easily
    with Agent and LLM classes.
    
    Features:
    - Read PDF files (with PyPDF2 or pdfplumber)
    - Read TXT files with various encodings
    - Extract text with metadata
    - Format content for LLM consumption
    - Chunk large documents for context management
    """
    
    def __init__(self, pdf_backend: str = "pypdf2"):
        """
        Initialize DocumentReader
        
        Args:
            pdf_backend: PDF reading backend to use ('pypdf2' or 'pdfplumber')
                        Default is 'pypdf2' for simplicity
        """
        self.pdf_backend = pdf_backend
        self._validate_backend()
    
    def _validate_backend(self):
        """Validate that the selected PDF backend is available"""
        if self.pdf_backend == "pypdf2":
            try:
                import PyPDF2
            except ImportError:
                raise ImportError(
                    "PyPDF2 is not installed. Install it with: pip install PyPDF2"
                )
        elif self.pdf_backend == "pdfplumber":
            try:
                import pdfplumber
            except ImportError:
                raise ImportError(
                    "pdfplumber is not installed. Install it with: pip install pdfplumber"
                )
        else:
            raise ValueError(
                f"Invalid PDF backend: {self.pdf_backend}. "
                "Choose 'pypdf2' or 'pdfplumber'"
            )
    
    def read_txt(self, file_path: str, encoding: str = "utf-8") -> str:
        """
        Read a TXT file
        
        Args:
            file_path: Path to the TXT file
            encoding: File encoding (default: utf-8)
        
        Returns:
            str: Content of the file
        
        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If encoding is incorrect
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.suffix.lower() == ".txt":
            raise ValueError(f"File must be a .txt file, got: {path.suffix}")
        
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError as e:
            # Try common encodings if utf-8 fails
            if encoding == "utf-8":
                for fallback_encoding in ["latin-1", "cp1252", "iso-8859-1"]:
                    try:
                        with open(path, "r", encoding=fallback_encoding) as f:
                            return f.read()
                    except UnicodeDecodeError:
                        continue
            raise UnicodeDecodeError(
                f"Could not decode file with encoding {encoding}. "
                "Try specifying a different encoding."
            )
    
    def read_pdf(self, file_path: str) -> str:
        """
        Read a PDF file
        
        Args:
            file_path: Path to the PDF file
        
        Returns:
            str: Extracted text from the PDF
        
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.suffix.lower() == ".pdf":
            raise ValueError(f"File must be a .pdf file, got: {path.suffix}")
        
        if self.pdf_backend == "pypdf2":
            return self._read_pdf_pypdf2(path)
        elif self.pdf_backend == "pdfplumber":
            return self._read_pdf_pdfplumber(path)
    
    def _read_pdf_pypdf2(self, path: Path) -> str:
        """Read PDF using PyPDF2"""
        import PyPDF2
        
        text_content = []
        
        try:
            with open(path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(text)
            
            return "\n\n".join(text_content)
        except Exception as e:
            raise RuntimeError(f"Error reading PDF with PyPDF2: {str(e)}")
    
    def _read_pdf_pdfplumber(self, path: Path) -> str:
        """Read PDF using pdfplumber"""
        import pdfplumber
        
        text_content = []
        
        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and text.strip():
                        text_content.append(text)
            
            return "\n\n".join(text_content)
        except Exception as e:
            raise RuntimeError(f"Error reading PDF with pdfplumber: {str(e)}")
    
    def read(self, file_path: str, encoding: str = "utf-8") -> str:
        """
        Read a document (auto-detects PDF or TXT based on extension)
        
        Args:
            file_path: Path to the document
            encoding: Encoding for TXT files (default: utf-8)
        
        Returns:
            str: Content of the document
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == ".pdf":
            return self.read_pdf(file_path)
        elif suffix == ".txt":
            return self.read_txt(file_path, encoding=encoding)
        else:
            raise ValueError(
                f"Unsupported file type: {suffix}. "
                "Supported types: .pdf, .txt"
            )
    
    def read_with_metadata(self, file_path: str, encoding: str = "utf-8") -> Dict[str, any]:
        """
        Read a document and return content with metadata
        
        Args:
            file_path: Path to the document
            encoding: Encoding for TXT files (default: utf-8)
        
        Returns:
            dict: Dictionary with 'content', 'file_name', 'file_type', 'size', 'path'
        """
        path = Path(file_path)
        content = self.read(file_path, encoding=encoding)
        
        return {
            "content": content,
            "file_name": path.name,
            "file_type": path.suffix.lower(),
            "size": path.stat().st_size,
            "path": str(path.absolute()),
            "char_count": len(content),
            "word_count": len(content.split())
        }
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into chunks for better context management
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of characters to overlap between chunks
        
        Returns:
            List[str]: List of text chunks
        """
        if chunk_size <= overlap:
            raise ValueError("chunk_size must be greater than overlap")
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # If this is not the last chunk, try to break at a sentence or word
            if end < text_length:
                # Look for sentence ending
                for delimiter in ['. ', '! ', '? ', '\n\n', '\n']:
                    last_delimiter = text.rfind(delimiter, start, end)
                    if last_delimiter != -1:
                        end = last_delimiter + len(delimiter)
                        break
                else:
                    # If no delimiter found, break at last space
                    last_space = text.rfind(' ', start, end)
                    if last_space != -1:
                        end = last_space
            
            chunks.append(text[start:end].strip())
            start = end - overlap
        
        return chunks
    
    def read_and_chunk(self, file_path: str, chunk_size: int = 1000, 
                       overlap: int = 100, encoding: str = "utf-8") -> List[str]:
        """
        Read a document and split it into chunks
        
        Args:
            file_path: Path to the document
            chunk_size: Maximum characters per chunk
            overlap: Number of characters to overlap between chunks
            encoding: Encoding for TXT files (default: utf-8)
        
        Returns:
            List[str]: List of text chunks
        """
        content = self.read(file_path, encoding=encoding)
        return self.chunk_text(content, chunk_size=chunk_size, overlap=overlap)
    
    def format_for_llm(self, file_path: str, encoding: str = "utf-8", 
                      include_metadata: bool = True) -> str:
        """
        Format document content for LLM consumption
        
        Args:
            file_path: Path to the document
            encoding: Encoding for TXT files (default: utf-8)
            include_metadata: Whether to include file metadata in the output
        
        Returns:
            str: Formatted text ready for LLM
        """
        if include_metadata:
            data = self.read_with_metadata(file_path, encoding=encoding)
            
            formatted = f"""Document: {data['file_name']}
Type: {data['file_type']}
Size: {data['size']} bytes
Words: {data['word_count']}

---

{data['content']}"""
            return formatted
        else:
            return self.read(file_path, encoding=encoding)
    
    def to_messages(self, file_path: str, role: str = "user", 
                   encoding: str = "utf-8", include_metadata: bool = False) -> List[Dict[str, str]]:
        """
        Convert document content to message format for Agent.chat()
        
        Args:
            file_path: Path to the document
            role: Message role ('user' or 'assistant')
            encoding: Encoding for TXT files (default: utf-8)
            include_metadata: Whether to include file metadata
        
        Returns:
            List[Dict]: Message in format [{"role": "user", "content": "..."}]
        """
        content = self.format_for_llm(file_path, encoding=encoding, 
                                     include_metadata=include_metadata)
        
        return [{"role": role, "content": content}]
    
    def to_chunked_messages(self, file_path: str, chunk_size: int = 1000,
                           overlap: int = 100, role: str = "user",
                           encoding: str = "utf-8") -> List[Dict[str, str]]:
        """
        Convert document to multiple chunked messages
        
        Args:
            file_path: Path to the document
            chunk_size: Maximum characters per chunk
            overlap: Number of characters to overlap between chunks
            role: Message role ('user' or 'assistant')
            encoding: Encoding for TXT files (default: utf-8)
        
        Returns:
            List[Dict]: List of messages, one per chunk
        """
        chunks = self.read_and_chunk(file_path, chunk_size=chunk_size, 
                                    overlap=overlap, encoding=encoding)
        
        messages = []
        for i, chunk in enumerate(chunks):
            content = f"[Chunk {i+1}/{len(chunks)}]\n\n{chunk}"
            messages.append({"role": role, "content": content})
        
        return messages
    
    def read_multiple(self, file_paths: List[str], encoding: str = "utf-8") -> Dict[str, str]:
        """
        Read multiple documents
        
        Args:
            file_paths: List oDf file paths
            encoding: Encoding for TXT files (default: utf-8)
        
        Returns:
            Dict[str, str]: Dictionary mapping file paths to their content
        """
        results = {}
        
        for file_path in file_paths:
            try:
                results[file_path] = self.read(file_path, encoding=encoding)
            except Exception as e:
                results[file_path] = f"Error reading file: {str(e)}"
        
        return results
    
    def combine_documents(self, file_paths: List[str], separator: str = "\n\n---\n\n",
                         encoding: str = "utf-8", include_headers: bool = True) -> str:
        """
        Read and combine multiple documents into a single text
        
        Args:
            file_paths: List of file paths
            separator: Text to use between documents
            encoding: Encoding for TXT files (default: utf-8)
            include_headers: Whether to include file names as headers
        
        Returns:
            str: Combined text from all documents
        """
        combined_parts = []
        
        for file_path in file_paths:
            try:
                content = self.read(file_path, encoding=encoding)
                
                if include_headers:
                    file_name = Path(file_path).name
                    combined_parts.append(f"=== {file_name} ===\n\n{content}")
                else:
                    combined_parts.append(content)
            except Exception as e:
                error_msg = f"Error reading {file_path}: {str(e)}"
                combined_parts.append(error_msg)
        
        return separator.join(combined_parts)
