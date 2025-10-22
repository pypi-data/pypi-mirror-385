"""
MOSAICX WebApp Backend - FastAPI Server

================================================================================
MOSAICX: Medical cOmputational Suite for Advanced Intelligent eXtraction
DIGIT-X Lab, LMU Radiology | Lalith Kumar Shiyam Sundar, PhD
================================================================================

A modern web interface for MOSAICX capabilities, providing REST endpoints
for schema generation, document extraction, and clinical report summarization.

Structure:
- /api/v1/generate-schema: Create Pydantic models from natural language
- /api/v1/extract-document: Extract structured data from medical documents  
- /api/v1/summarize-reports: Generate timeline summaries from clinical reports
- /api/v1/schemas: Manage schema registry
"""

import os
import sys
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import tempfile
import shutil
import asyncio
from contextlib import asynccontextmanager

# Add the parent directory to path so we can import mosaicx
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError

# Import MOSAICX API
from mosaicx import generate_schema, console
from mosaicx.constants import APPLICATION_VERSION, MOSAICX_COLORS, USER_SCHEMA_DIR
from mosaicx.display import styled_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class SchemaGenerationRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=1000, 
                           description="Natural language description of the medical schema")
    schema_name: Optional[str] = Field(None, min_length=3, max_length=50,
                                     description="Custom name for the schema (used in filename)")
    class_name: Optional[str] = Field("GeneratedModel", 
                                    description="Name for the Pydantic model class") 
    model: Optional[str] = Field("gpt-oss:120b", 
                               description="LLM model to use for generation")
    temperature: Optional[float] = Field(0.2, ge=0.0, le=2.0,
                                       description="Sampling temperature")
    base_url: Optional[str] = Field(None, description="Custom API endpoint")
    api_key: Optional[str] = Field(None, description="Custom API key")


class SchemaGenerationResponse(BaseModel):
    schema_id: str = Field(..., description="Unique identifier for the generated schema")
    class_name: str = Field(..., description="Generated Pydantic class name")
    python_code: str = Field(..., description="Complete Python/Pydantic model code")
    file_path: Optional[str] = Field(None, description="Path where schema was saved")
    model_used: str = Field(..., description="LLM model used for generation")
    description: str = Field(..., description="Original description provided")


class ExtractionRequest(BaseModel):
    schema_identifier: str = Field(..., description="Schema ID, filename, or path")
    model: Optional[str] = Field("gpt-oss:120b", description="LLM model for extraction")
    base_url: Optional[str] = Field(None, description="Custom API endpoint")
    api_key: Optional[str] = Field(None, description="Custom API key")


class ExtractionResponse(BaseModel):
    success: bool = Field(..., description="Whether extraction was successful")
    extracted_data: Dict[str, Any] = Field(..., description="Structured data extracted from a document")
    schema_used: str = Field(..., description="Schema identifier used for extraction")
    model_used: str = Field(..., description="LLM model used for extraction")
    file_name: str = Field(..., description="Original document filename")


class SummarizationRequest(BaseModel):
    patient_id: str = Field(..., description="Patient identifier for the summary")
    model: Optional[str] = Field("gpt-oss:120b", description="LLM model for summarization")
    temperature: Optional[float] = Field(0.2, ge=0.0, le=2.0, description="Sampling temperature")
    base_url: Optional[str] = Field(None, description="Custom API endpoint")
    api_key: Optional[str] = Field(None, description="Custom API key")


class SummarizationResponse(BaseModel):
    patient_id: str = Field(..., description="Patient identifier")
    timeline: List[Dict[str, Any]] = Field(..., description="Chronological timeline of reports")
    overall_summary: str = Field(..., description="Overall clinical summary")
    reports_processed: int = Field(..., description="Number of reports processed")


class DirectorySummarizationRequest(BaseModel):
    directory_path: str = Field(..., description="Path to directory containing clinical documents")
    patient_id: Optional[str] = Field("patient", description="Patient identifier for the summary")
    model: Optional[str] = Field("gpt-oss:120b", description="LLM model for processing")
    temperature: Optional[float] = Field(0.2, ge=0.0, le=2.0, description="Sampling temperature")
    base_url: Optional[str] = Field(None, description="Custom API endpoint")
    api_key: Optional[str] = Field(None, description="Custom API key")


class DirectorySummarizationResponse(BaseModel):
    patient_id: str = Field(..., description="Patient identifier")
    files_processed: List[str] = Field(..., description="List of documents that were processed")
    timeline: List[Dict[str, Any]] = Field(..., description="Chronological timeline of reports")
    overall_summary: str = Field(..., description="Overall clinical summary")
    total_files: int = Field(..., description="Total number of documents processed")


# Application startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    console.print(styled_message("🚀 MOSAICX WebApp Backend Starting...", "info"))
    
    # Create temp directory for uploads
    os.makedirs("/tmp/mosaicx_uploads", exist_ok=True)
    os.makedirs("/tmp/mosaicx_schemas", exist_ok=True)
    
    yield
    
    # Shutdown
    console.print(styled_message("🛑 MOSAICX WebApp Backend Shutting Down...", "warning"))


# Initialize FastAPI app
app = FastAPI(
    title="MOSAICX WebApp API",
    description="REST API for Medical cOmputational Suite for Advanced Intelligent eXtraction",
    version=APPLICATION_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving (for frontend assets if needed)
# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "MOSAICX WebApp Backend",
        "version": APPLICATION_VERSION,
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": APPLICATION_VERSION,
        "mosaicx_available": True
    }


@app.post("/api/v1/generate-schema", response_model=SchemaGenerationResponse)
async def generate_schema_endpoint(request: SchemaGenerationRequest):
    """
    Generate a Pydantic schema from natural language description
    """
    try:
        console.print(styled_message(f"🔬 Generating schema: {request.class_name}", "info"))
        logger.info(f"Schema generation request - schema_name: '{request.schema_name}', class_name: '{request.class_name}', description: '{request.description[:50]}...'")
        
        # Determine class name - use custom schema name if provided, otherwise use default
        class_name = request.class_name
        if request.schema_name:
            # Convert schema name to proper PascalCase class name
            import re
            # Remove special characters and convert to PascalCase
            clean_name = re.sub(r'[^a-zA-Z0-9]', '_', request.schema_name)
            class_name = ''.join(word.capitalize() for word in clean_name.split('_'))
        
        # Use CLI for schema generation to ensure exact same behavior
        import subprocess
        
        cmd = [
            "python", "-m", "mosaicx", "generate",
            "--desc", request.description,
            "--model", request.model
        ]
        
        if class_name != "GeneratedModel":
            cmd.extend(["--class-name", class_name])
        if request.base_url:
            cmd.extend(["--base-url", request.base_url])
        if request.api_key:
            cmd.extend(["--api-key", request.api_key])
        if request.temperature:
            cmd.extend(["--temperature", str(request.temperature)])
            
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="/app")
        
        if result.returncode != 0:
            raise Exception(f"CLI schema generation failed: {result.stderr}")
            
        # Find the newest .py file in the managed schema directory
        schema_dir = USER_SCHEMA_DIR
        schema_dir.mkdir(parents=True, exist_ok=True)
        schema_files = list(schema_dir.glob("*.py"))
        if not schema_files:
            raise Exception("No schema files found after generation")

        newest_file = max(schema_files, key=lambda path: path.stat().st_mtime)
        python_code = newest_file.read_text(encoding="utf-8")
        schema_id = newest_file.stem
        saved_path = str(newest_file)
        
        return SchemaGenerationResponse(
            schema_id=schema_id,
            class_name=class_name,
            python_code=python_code,
            file_path=str(saved_path),
            model_used=request.model or "llama3.2:latest",
            description=request.description
        )
        
    except Exception as e:
        logger.error(f"Schema generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schema generation failed: {str(e)}"
        )


from mosaicx.document_loader import DOC_SUFFIXES


@app.post("/api/v1/extract-document", response_model=ExtractionResponse)
async def extract_document_endpoint(
    file: UploadFile = File(..., description="Clinical document to extract data from"),
    schema_identifier: str = Form(..., description="Schema ID, filename, or path"),
    model: str = Form("gpt-oss:120b", description="LLM model for extraction"),
    base_url: Optional[str] = Form(None, description="Custom API endpoint"),
    api_key: Optional[str] = Form(None, description="Custom API key")
):
    """
    Extract structured data from a clinical document using a specified schema.
    """
    suffix = Path(file.filename).suffix.lower()
    if suffix not in DOC_SUFFIXES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported file format. "
                f"Supported extensions: {', '.join(sorted(DOC_SUFFIXES))}"
            ),
        )
    
    # Save uploaded file temporarily
    temp_doc_path = Path(f"/tmp/mosaicx_uploads/{file.filename}")
    
    try:
        with open(temp_doc_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        console.print(styled_message(f"📄 Extracting from: {file.filename}", "info"))
        
        # Use CLI directly to ensure exact same behavior
        import subprocess
        import json
        
        cmd = [
            "python", "-m", "mosaicx", "extract",
            "--document", str(temp_doc_path),
            "--schema", schema_identifier,
            "--model", model,
            "--output", f"/tmp/mosaicx_extraction_result.json"
        ]
        
        if base_url:
            cmd.extend(["--base-url", base_url])
        if api_key:
            cmd.extend(["--api-key", api_key])
            
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="/app")
        
        if result.returncode != 0:
            raise Exception(f"CLI extraction failed: {result.stderr}")
            
        # Read the JSON output
        with open("/tmp/mosaicx_extraction_result.json", "r") as f:
            extracted_data = json.load(f)
        
        return ExtractionResponse(
            success=True,
            extracted_data=extracted_data,
            schema_used=schema_identifier,
            model_used=model,
            file_name=file.filename
        )
        
    except Exception as e:
        logger.error(f"Document extraction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document extraction failed: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_doc_path.exists():
            temp_doc_path.unlink()


@app.post("/api/v1/summarize-reports", response_model=SummarizationResponse)
async def summarize_reports_endpoint(
    request: SummarizationRequest,
    files: List[UploadFile] = File(..., description="Clinical documents to summarize")
):
    """
    Generate timeline-based summaries from clinical reports using CLI
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one document is required"
        )

    allowed_suffixes = set(DOC_SUFFIXES.keys())

    import tempfile
    import shutil

    temp_dir = Path(tempfile.mkdtemp(prefix='mosaicx_summarize_'))
    json_output = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json_path = json_output.name
    json_output.close()

    try:
        # Save all uploaded files to temporary directory
        for file in files:
            suffix = Path(file.filename).suffix.lower()
            if suffix not in allowed_suffixes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Unsupported file format for summarization: {file.filename}. "
                        f"Supported extensions: {', '.join(sorted(allowed_suffixes))}"
                    ),
                )
            # Save file to temp directory
            temp_path = temp_dir / file.filename
            
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        
        console.print(styled_message(f"📊 Summarizing {len(files)} reports for patient using CLI: {request.patient_id}", "info"))

        # Build CLI command for summarization using --dir
        cmd = [
            "python", "-m", "mosaicx", "summarize",
            "--dir", temp_dir,
            "--patient", request.patient_id,
            "--model", request.model,
            "--temperature", str(request.temperature),
            "--base-url", request.base_url or "http://host.docker.internal:11434/v1",
            "--api-key", "ollama",
            "--output", json_path
        ]
        
        console.print(styled_message(f"🔧 Executing CLI command: {' '.join(cmd)}", "info"))
        
        # Execute CLI command using subprocess
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            error_msg = result.stderr or "Unknown CLI error"
            console.print(styled_message(f"❌ CLI command failed: {error_msg}", "error"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"CLI summarization failed: {error_msg}"
            )
        
        # Read and parse the JSON output file
        import json
        try:
            with open(json_path, 'r') as f:
                summary_data = json.load(f)
            console.print(styled_message(f"✅ CLI summarization successful", "success"))
            
            # Extract data from JSON structure
            timeline = summary_data.get('timeline', [])
            overall_summary = summary_data.get('overall', '')
            patient_info = summary_data.get('patient', {})
            
            return SummarizationResponse(
                patient_id=patient_info.get('patient_id', request.patient_id),
                timeline=timeline,
                overall_summary=overall_summary,
                reports_processed=len(files)
            )
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            # If JSON parsing fails, return the raw output
            console.print(styled_message(f"⚠️ JSON parsing failed: {e}", "warning"))
            return SummarizationResponse(
                patient_id=request.patient_id,
                timeline=[],
                overall_summary=result.stdout.strip() if result.stdout else "Summarization completed but no output captured",
                reports_processed=len(files)
            )
        
    except Exception as e:
        logger.error(f"Report summarization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report summarization failed: {str(e)}"
        )
    
    finally:
        try:
            os.unlink(json_path)
        except Exception:
            pass

        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass



@app.post("/api/v1/summarize-directory", response_model=DirectorySummarizationResponse)
async def summarize_directory_endpoint(request: DirectorySummarizationRequest):
    """
    Process all supported clinical documents in a directory and generate a summary using the CLI.
    """
    try:
        directory_path = Path(request.directory_path)
        
        # Validate directory exists
        if not directory_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Directory not found: {request.directory_path}"
            )
        
        if not directory_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Path is not a directory: {request.directory_path}"
            )
        
        allowed_suffixes = set(DOC_SUFFIXES.keys())
        doc_files = [
            candidate
            for candidate in directory_path.rglob("*")
            if candidate.is_file() and candidate.suffix.lower() in allowed_suffixes
        ]

        if not doc_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"No supported documents found in directory: {request.directory_path}. "
                    f"Supported extensions: {', '.join(sorted(allowed_suffixes))}"
                )
            )
        
        console.print(
            styled_message(
                f"📊 Processing {len(doc_files)} document(s) from directory using CLI: {request.directory_path}",
                "info",
            )
        )
        
        # Create temporary JSON output file
        import tempfile
        json_output = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json_path = json_output.name
        json_output.close()
        
        # Build CLI command for directory summarization
        cmd = [
            "python", "-m", "mosaicx", "summarize",
            "--dir", str(directory_path),
            "--patient", request.patient_id,
            "--model", request.model,
            "--temperature", str(request.temperature),
            "--base-url", request.base_url or "http://host.docker.internal:11434/v1",
            "--api-key", "ollama",
            "--output", json_path
        ]
        
        console.print(styled_message(f"🔧 Executing CLI command: {' '.join(cmd)}", "info"))
        
        # Execute CLI command using subprocess
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            error_msg = result.stderr or "Unknown CLI error"
            console.print(styled_message(f"❌ CLI command failed: {error_msg}", "error"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"CLI summarization failed: {error_msg}"
            )
        
        # Read and parse the JSON output file
        import json
        try:
            with open(json_path, 'r') as f:
                summary_data = json.load(f)
            console.print(styled_message(f"✅ CLI directory summarization successful", "success"))
            
            # Extract data from JSON structure
            timeline = summary_data.get('timeline', [])
            overall_summary = summary_data.get('overall', '')
            patient_info = summary_data.get('patient', {})
            
            return DirectorySummarizationResponse(
                patient_id=patient_info.get('patient_id', request.patient_id),
                files_processed=[f.name for f in doc_files],
                timeline=timeline,
                overall_summary=overall_summary,
                total_files=len(doc_files)
            )
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            # If JSON parsing fails, return the raw output
            console.print(styled_message(f"⚠️ JSON parsing failed: {e}", "warning"))
            return DirectorySummarizationResponse(
                patient_id=request.patient_id,
                files_processed=[f.name for f in doc_files],
                timeline=[],
                overall_summary=result.stdout.strip() if result.stdout else "Summarization completed but no output captured",
                total_files=len(doc_files)
            )
        
        finally:
            # Clean up the temporary JSON file
            try:
                os.unlink(json_path)
            except:
                pass
        
    except Exception as e:
        logger.error(f"Directory summarization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Directory summarization failed: {str(e)}"
        )


@app.post("/api/v1/summarize-files", response_model=DirectorySummarizationResponse)
async def summarize_files_endpoint(
    patient_id: str = Form("patient"),
    model: str = Form("gpt-oss:120b"),
    temperature: float = Form(0.2),
    documents: List[UploadFile] = File(..., description="Clinical documents to summarize"),
):
    """
    Process multiple uploaded clinical documents and generate a summary using the CLI.
    """
    try:
        # Validate we have documents
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No documents provided"
            )
        
        allowed_suffixes = set(DOC_SUFFIXES.keys())

        # Filter for supported files
        valid_documents = []
        for file in documents:
            suffix = Path(file.filename).suffix.lower()
            if suffix not in allowed_suffixes:
                logger.warning(f"Skipping unsupported document: {file.filename}")
                continue
            valid_documents.append(file)
        
        if not valid_documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No valid documents found. "
                    f"Supported extensions: {', '.join(sorted(allowed_suffixes))}"
                )
            )
        
        console.print(
            styled_message(f"📊 Processing {len(valid_documents)} uploaded document(s) using CLI", "info")
        )
        
        # Create temporary directory for files
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix='mosaicx_summarize_files_')
        
        # Save uploaded files to temporary directory
        temp_files = []
        try:
            for file in valid_documents:
                # Extract just the filename without directory path
                clean_filename = Path(file.filename).name
                temp_path = Path(temp_dir) / clean_filename
                
                console.print(styled_message(f"📄 Saving file: {file.filename} -> {clean_filename}", "info"))
                
                with open(temp_path, "wb") as temp_file:
                    content = await file.read()
                    temp_file.write(content)
                temp_files.append(temp_path)
            
            # Create temporary JSON output file
            json_output = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            json_path = json_output.name
            json_output.close()
            
            # Build CLI command for summarization using --dir
            cmd = [
                "python", "-m", "mosaicx", "summarize",
                "--dir", temp_dir,
                "--patient", patient_id,
                "--model", model,
                "--temperature", str(temperature),
                "--base-url", "http://host.docker.internal:11434/v1",
                "--api-key", "ollama",
                "--output", json_path
            ]
            
            console.print(styled_message(f"🔧 Executing CLI command: {' '.join(cmd)}", "info"))
            
            # Execute CLI command using subprocess
            import subprocess
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                error_msg = result.stderr or "Unknown CLI error"
                console.print(styled_message(f"❌ CLI command failed: {error_msg}", "error"))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"CLI summarization failed: {error_msg}"
                )
            
            # Read and parse the JSON output file
            import json
            try:
                with open(json_path, 'r') as f:
                    summary_data = json.load(f)
                console.print(styled_message(f"✅ CLI summarization successful", "success"))
                
                # Extract data from JSON structure
                timeline = summary_data.get('timeline', [])
                overall_summary = summary_data.get('overall', '')
                patient_info = summary_data.get('patient', {})
                
                return DirectorySummarizationResponse(
                    patient_id=patient_info.get('patient_id', patient_id),
                    files_processed=[Path(f.filename).name for f in valid_documents],
                    timeline=timeline,
                    overall_summary=overall_summary,
                    total_files=len(temp_files)
                )
                
            except (json.JSONDecodeError, FileNotFoundError) as e:
                # If JSON parsing fails, return the raw output
                console.print(styled_message(f"⚠️ JSON parsing failed: {e}", "warning"))
                return DirectorySummarizationResponse(
                    patient_id=patient_id,
                    files_processed=[Path(f.filename).name for f in valid_documents],
                    timeline=[],
                    overall_summary=result.stdout.strip() if result.stdout else "Summarization completed but no output captured",
                    total_files=len(temp_files)
                )
            
        finally:
            try:
                os.unlink(json_path)
            except Exception:
                pass

            try:
                shutil.rmtree(temp_dir)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp directory {temp_dir}: {cleanup_error}")
        
    except Exception as e:
        logger.error(f"File summarization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File summarization failed: {str(e)}"
        )


@app.get("/api/v1/schemas")
async def list_schemas():
    """
    List available schemas in the registry
    """
    try:
        schemas_dir = Path("/tmp/mosaicx_schemas")
        schemas = []
        
        if schemas_dir.exists():
            for schema_file in schemas_dir.glob("*.py"):
                schema_id = schema_file.stem
                
                # Try to extract class name and description from the file
                try:
                    content = schema_file.read_text()
                    
                    # Extract class name
                    class_match = re.search(r'class\s+(\w+)\s*\(', content)
                    class_name = class_match.group(1) if class_match else "Unknown"
                    
                    # Extract description from docstring
                    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                    description = "Generated schema"
                    if docstring_match and docstring_match.group(1).strip():
                        description = docstring_match.group(1).strip()[:100] + ("..." if len(docstring_match.group(1).strip()) > 100 else "")
                    
                    # Get file creation time
                    created = schema_file.stat().st_mtime
                    created_iso = datetime.fromtimestamp(created).isoformat() + "Z"
                    
                    schemas.append({
                        "schema_id": schema_id,
                        "class_name": class_name,
                        "description": description,
                        "created": created_iso,
                        "filename": schema_file.name,
                        "file_path": str(schema_file.absolute())
                    })
                    
                except Exception as parse_error:
                    # If parsing fails, still include the schema with basic info
                    created = schema_file.stat().st_mtime
                    created_iso = datetime.fromtimestamp(created).isoformat() + "Z"
                    
                    schemas.append({
                        "schema_id": schema_id,
                        "class_name": "ParseError",
                        "description": "Schema file found but could not parse details",
                        "created": created_iso,
                        "filename": schema_file.name,
                        "file_path": str(schema_file.absolute())
                    })
        
        # Sort by creation time (newest first)
        schemas.sort(key=lambda x: x["created"], reverse=True)
        
        return {"schemas": schemas}
        
    except Exception as e:
        logger.error(f"Failed to list schemas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list schemas: {str(e)}"
        )


@app.get("/api/v1/download-schema/{schema_id}")
async def download_schema(schema_id: str):
    """
    Download a generated schema file
    """
    schema_path = Path(f"/tmp/mosaicx_schemas/{schema_id}.py")
    
    if not schema_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema {schema_id} not found"
        )
    
    return FileResponse(
        path=schema_path,
        filename=f"{schema_id}.py",
        media_type="text/plain"
    )


if __name__ == "__main__":
    import uvicorn
    
    console.print(styled_message("🌐 Starting MOSAICX WebApp Backend...", "success"))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["./"],
        log_level="info"
    )
