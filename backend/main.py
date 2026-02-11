"""
ContextWeave Lite - FastAPI Backend
Main application entry point and API endpoints
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from git_utils import get_commit_history, get_related_files, read_file_content
from llm.provider_factory import get_llm_provider, get_available_providers
from schemas import ContextRequest, ContextResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ContextWeave Lite API",
    description="AI-powered code context and history analysis",
    version="0.1.0"
)

# Add CORS middleware to allow VS Code extension to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ContextWeave Lite API",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check including LLM provider availability"""
    provider_name = os.getenv("LLM_PROVIDER", "groq")
    available_providers = get_available_providers()
    
    return {
        "status": "healthy",
        "version": "0.1.0",
        "llm_provider": provider_name,
        "available_providers": available_providers
    }


@app.post("/context/file", response_model=ContextResponse)
async def analyze_file_context(request: ContextRequest):
    """
    Main endpoint: Analyze a file and return summary, design decisions, and related files
    
    Args:
        request: ContextRequest with repo_path, file_path, and optional selected_code
        
    Returns:
        ContextResponse with summary, decisions, related_files, and optional weird_code_explanation
    """
    logger.info(f"Analyzing file: {request.file_path} in repo: {request.repo_path}")
    
    try:
        # Step 1: Validate inputs
        if not os.path.exists(request.file_path):
            logger.error(f"File does not exist: {request.file_path}")
            raise HTTPException(
                status_code=400,
                detail=f"File does not exist: {request.file_path}"
            )
        
        # Repo path is optional - if not provided or doesn't exist, we'll analyze without Git
        if not request.repo_path or not os.path.exists(request.repo_path):
            logger.info("Repo path not provided or doesn't exist. Analyzing file without Git history.")
            request.repo_path = os.path.dirname(request.file_path)  # Use file's directory as fallback
        
        # Step 2: Try to get commit history (graceful degradation if not a Git repo)
        logger.info("Fetching commit history...")
        commits = []
        try:
            commits = get_commit_history(
                repo_path=request.repo_path,
                file_path=request.file_path,
                limit=request.commit_limit
            )
            
            if not commits:
                logger.warning("No commit history found for this file")
        except ValueError as e:
            # Not a Git repository - continue without Git history
            logger.warning(f"Git not available: {str(e)}. Continuing with file-only analysis.")
            commits = []
        
        # Step 3: Read current file content
        logger.info("Reading file content...")
        try:
            file_content = read_file_content(request.file_path)
        except ValueError as e:
            logger.error(f"File read error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Could not read file: {str(e)}"
            )
        
        # Step 4: Compute related files (imports + co-changed files if Git available)
        logger.info("Computing related files...")
        try:
            related_files_data = get_related_files(
                repo_path=request.repo_path,
                file_path=request.file_path,
                file_content=file_content
            )
        except Exception as e:
            # If Git operations fail, just use imports
            logger.warning(f"Could not analyze co-changed files: {str(e)}. Using imports only.")
            from git_utils import extract_imports
            related_files_data = {
                'imports': extract_imports(file_content, request.file_path),
                'co_changed': []
            }
        
        # Step 5: Get LLM provider and analyze
        logger.info("Initializing LLM provider...")
        provider_config = {}
        if request.llm_model:
            provider_config['model'] = request.llm_model
        
        provider = get_llm_provider(
            provider_name=request.llm_provider,
            config=provider_config
        )
        
        logger.info(f"Using LLM provider: {provider.get_provider_name()}")
        
        # Check if provider is available
        if not provider.is_available():
            logger.warning(f"Provider {provider.get_provider_name()} is not available")
            if provider.get_provider_name() in ["ollama", "localai"]:
                raise HTTPException(
                    status_code=503,
                    detail=f"Local LLM server not running. Please start {provider.get_provider_name().title()}."
                )
        
        # Call provider to analyze
        logger.info("Calling LLM provider for analysis...")
        response = await provider.generate(
            file_path=request.file_path,
            file_content=file_content,
            commits=commits,
            related_files_data=related_files_data,
            selected_code=request.selected_code
        )
        
        logger.info(f"Analysis complete. Analyzed {len(commits)} commits.")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error analyzing file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting ContextWeave Lite API on port {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
