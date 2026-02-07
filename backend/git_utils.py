"""
Git operations using GitPython
Handles commit history, diff analysis, and related file detection
"""
import os
import re
import logging
from typing import List, Dict, Optional
from collections import Counter
from git import Repo, InvalidGitRepositoryError, GitCommandError

logger = logging.getLogger(__name__)


def get_commit_history(repo_path: str, file_path: str, limit: int = 50) -> List[Dict]:
    """
    Get commit history for a specific file
    
    Args:
        repo_path: Absolute path to Git repository
        file_path: Absolute path to file
        limit: Maximum number of commits to retrieve
        
    Returns:
        List of commit dictionaries with hash, author, date, message, lines_changed
        
    Raises:
        ValueError: If repo_path is not a valid Git repository
    """
    try:
        repo = Repo(repo_path)
        logger.info(f"Opened Git repository at {repo_path}")
    except InvalidGitRepositoryError:
        logger.error(f"Not a valid Git repository: {repo_path}")
        raise ValueError(f"Not a valid Git repository: {repo_path}")
    
    # Get relative path from repo root
    relative_path = os.path.relpath(file_path, repo_path)
    logger.info(f"Querying commits for {relative_path} (limit: {limit})")
    
    try:
        # Get commits that touched this file
        commits = list(repo.iter_commits(paths=relative_path, max_count=limit))
    except GitCommandError as e:
        logger.warning(f"Error getting commits for {relative_path}: {e}")
        return []
    
    if not commits:
        logger.info(f"No commits found for {relative_path}")
        return []
    
    logger.info(f"Found {len(commits)} commits for {relative_path}")
    
    result = []
    for commit in commits:
        # Calculate lines changed for this file
        lines_changed = 0
        try:
            if commit.parents:
                diffs = commit.parents[0].diff(commit, paths=relative_path)
                for diff in diffs:
                    if diff.diff:
                        # Count lines in diff (rough estimate)
                        diff_text = diff.diff.decode('utf-8', errors='ignore')
                        lines_changed = len([l for l in diff_text.split('\n') if l.startswith('+') or l.startswith('-')])
        except Exception as e:
            logger.debug(f"Could not calculate diff for commit {commit.hexsha[:7]}: {e}")
        
        result.append({
            "hash": commit.hexsha[:7],  # Short hash
            "full_hash": commit.hexsha,
            "author": commit.author.name,
            "date": commit.committed_datetime.isoformat(),
            "message": commit.message.strip(),
            "lines_changed": lines_changed
        })
    
    logger.info(f"Successfully extracted {len(result)} commits with metadata")
    return result


def get_related_files(repo_path: str, file_path: str, file_content: str) -> Dict:
    """
    Find related files using imports and co-change analysis
    
    Args:
        repo_path: Absolute path to Git repository
        file_path: Absolute path to file
        file_content: Content of the file
        
    Returns:
        Dictionary with 'imports' and 'co_changed' lists
    """
    # Get relative path from repo root
    relative_path = os.path.relpath(file_path, repo_path)
    
    # 1. Extract imports from file content
    imports = extract_imports(file_content, file_path)
    
    # 2. Find co-changed files from Git history
    co_changed = find_co_changed_files(repo_path, relative_path)
    
    return {
        "imports": imports[:5],  # Top 5 imports
        "co_changed": co_changed[:5]  # Top 5 co-changed files
    }


def extract_imports(file_content: str, file_path: str) -> List[str]:
    """
    Extract imported files from code (supports Python, JavaScript, TypeScript, Java)
    
    Args:
        file_content: Content of the file
        file_path: Path to file (to determine language)
        
    Returns:
        List of imported file paths (relative)
    """
    imports = []
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext in ['.py']:
            # Python imports: from X import Y, import X
            import_pattern = r'^\s*(?:from|import)\s+([a-zA-Z0-9_.]+)'
            for line in file_content.split('\n'):
                match = re.match(import_pattern, line)
                if match:
                    module = match.group(1)
                    # Convert module path to file path (rough heuristic)
                    file_import = module.replace('.', '/') + '.py'
                    imports.append(file_import)
        
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            # JavaScript/TypeScript imports: import X from 'Y', require('Y')
            import_pattern = r'(?:import.*from\s+[\'"]([^\'"]+)[\'"]|require\([\'"]([^\'"]+)[\'"]\))'
            for match in re.finditer(import_pattern, file_content):
                imported = match.group(1) or match.group(2)
                if imported and not imported.startswith('.'):
                    imports.append(imported)
        
        elif ext in ['.java']:
            # Java imports: import com.example.Class;
            import_pattern = r'^\s*import\s+([a-zA-Z0-9_.]+);'
            for line in file_content.split('\n'):
                match = re.match(import_pattern, line)
                if match:
                    class_path = match.group(1)
                    # Convert to file path
                    file_import = class_path.replace('.', '/') + '.java'
                    imports.append(file_import)
    
    except Exception as e:
        logger.debug(f"Error extracting imports: {e}")
    
    return imports


def find_co_changed_files(repo_path: str, relative_path: str, limit: int = 100) -> List[Dict]:
    """
    Find files that frequently change together with the target file
    
    Args:
        repo_path: Absolute path to Git repository
        relative_path: Relative path to file from repo root
        limit: Number of commits to analyze
        
    Returns:
        List of dicts with 'path' and 'frequency' keys, sorted by frequency
    """
    try:
        repo = Repo(repo_path)
        commits = list(repo.iter_commits(paths=relative_path, max_count=limit))
    except Exception as e:
        logger.warning(f"Error finding co-changed files: {e}")
        return []
    
    co_changed = Counter()
    
    for commit in commits:
        try:
            # Get all files changed in this commit
            changed_files = [item.a_path for item in commit.stats.files.keys()]
            
            for file in changed_files:
                if file != relative_path:
                    co_changed[file] += 1
        except Exception as e:
            logger.debug(f"Error processing commit {commit.hexsha[:7]}: {e}")
    
    # Return top files sorted by frequency
    result = [
        {"path": path, "frequency": count}
        for path, count in co_changed.most_common(10)
    ]
    
    return result


def read_file_content(file_path: str, max_lines: int = 10000) -> str:
    """
    Read file content from disk, with truncation for very large files
    
    Args:
        file_path: Absolute path to file
        max_lines: Maximum number of lines to read
        
    Returns:
        File content as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    lines.append(f"\n... [File truncated after {max_lines} lines] ...")
                    break
                lines.append(line)
            return ''.join(lines)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise ValueError(f"Could not read file: {e}")
