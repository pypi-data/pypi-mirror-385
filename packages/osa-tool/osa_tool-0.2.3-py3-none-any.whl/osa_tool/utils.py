import logging
import os
import re
import shutil
import stat
from pathlib import Path
from urllib.parse import urlparse

from rich.console import Console
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)

logger = logging.getLogger("rich")

console = Console()


def rich_section(title: str):
    """
    Print a styled section header in the console to visually separate log sections.

    Args:
        title: Title text for the section header.
    """
    console.print("")
    console.rule(f"[bold cyan]{title}[/bold cyan]", style="cyan")


def parse_folder_name(repo_url: str) -> str:
    """
    Parses the repository URL to extract the folder name.

    Args:
        repo_url: The URL of the Git repository.

    Returns:
        The name of the folder where the repository will be cloned.
    """
    patterns = [r"github\.com/[^/]+/([^/]+)", r"gitlab[^/]+/[^/]+/([^/]+)", r"gitverse\.ru/[^/]+/([^/]+)"]
    for pattern in patterns:
        match = re.search(pattern, repo_url)
        if match:
            folder_name = match.group(1)
            logger.debug(f"Parsed folder name '{folder_name}' from repo URL '{repo_url}'")
            return folder_name
    folder_name = re.sub(r"[:/]", "_", repo_url.rstrip("/"))
    logger.debug(f"Parsed folder name '{folder_name}' from repo URL '{repo_url}'")
    return folder_name


def osa_project_root() -> Path:
    """Returns osa_tool project root folder."""
    return Path(__file__).parent


def build_arguments_path() -> str:
    """Returns arguments.yaml path for CLI parser."""
    return os.path.join(osa_project_root(), "config", "settings", "arguments.yaml")


def build_config_path() -> str:
    """Returns config.toml path for CLI parser and settings.py."""
    return os.path.join(osa_project_root(), "config", "settings", "config.toml")


def get_base_repo_url(repo_url: str) -> str:
    """
    Extracts the base repository URL path from a given Git URL.

    Args:
        repo_url (str, optional): The Git repository URL. If not provided,
            the instance's `repo_url` attribute is used. Defaults to None.

    Returns:
        str: The base repository path (e.g., 'username/repo-name').

    Raises:
        ValueError: If the provided URL has unsupported format.
    """
    patterns = [
        r"https?://github\.com/([^/]+/[^/]+)",
        r"https?://[^/]*gitlab[^/]*/(.+)",
        r"https?://gitverse\.ru/([^/]+/[^/]+)",
    ]
    for pattern in patterns:
        match = re.match(pattern, repo_url)
        if match:
            return match.group(1).rstrip("/")
    raise ValueError(f"Unsupported repository URL format: {repo_url}")


def delete_repository(repo_url: str) -> None:
    """
    Deletes the local directory of the downloaded repository based on its URL.
    Works reliably on Windows and Unix-like systems.

    Args:
        repo_url (str): The URL of the repository to be deleted.

    Raises:
        Exception: Logs an error message if deletion fails.
    """
    repo_path = os.path.join(os.getcwd(), parse_folder_name(repo_url))

    def on_rm_error(func, path, exc_info):
        """Force-remove read-only files and log the issue."""
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            logger.error(f"Failed to forcibly remove {path}: {e}")

    try:
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path, onerror=on_rm_error)
            logger.info(f"Directory {repo_path} has been deleted.")
        else:
            logger.info(f"Directory {repo_path} does not exist.")
    except Exception as e:
        logger.error(f"Failed to delete directory {repo_path}: {e}")


def parse_git_url(repo_url: str) -> tuple[str, str, str, str]:
    """
    Parse repository URL and return host, full name, and project name.

    Args:
        repo_url: The URL of the GitHub repository.

    Returns:
        tuple: host_domain, host, project name and full name.
    """
    parsed_url = urlparse(repo_url)

    if parsed_url.scheme not in ["http", "https"]:
        raise ValueError(f"Provided URL is not correct: {parsed_url.scheme}")

    if not parsed_url.netloc:
        raise ValueError(f"Invalid Git repository URL: {parsed_url}")

    host_domain = parsed_url.netloc
    host = host_domain.split(".")[0].lower()

    path_parts = parsed_url.path.strip("/").split("/")
    full_name = "/".join(path_parts[:2])
    name = path_parts[-1]

    return host_domain, host, name, full_name


def get_repo_tree(repo_path: str) -> str:
    """
    Builds a text representation of the project file tree, excluding the .git directory.

    Args:
        repo_path: Path to the repository being explored.

    Returns:
        str: A text representation of the repository's file tree with relative paths to files and directories,
             excluding the `.git` directory. Each file or directory path is on a new line.

    """
    repo_path = Path(repo_path)
    excluded_extensions = {
        # Images
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".tiff",
        ".webp",
        ".drawio",
        ".svg",
        ".ico",
        # Videos
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".flv",
        ".wmv",
        ".webm",
        # Data files
        ".csv",
        ".tsv",
        ".parquet",
        ".json",
        ".xml",
        ".xls",
        ".xlsx",
        ".db",
        ".sqlite",
        ".npy",
        # Archives
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".7z",
        ".rar",
        # Binary / compiled artifacts
        ".exe",
        ".dll",
        ".so",
        ".bin",
        ".obj",
        ".class",
        ".pkl",
        ".dylib",
        ".o",
        ".a",
        ".lib",
        ".lo",
        ".mod",
        ".pyc",
        ".pyo",
        ".pyd",
        ".egg",
        ".whl",
        ".mat",
        # Documents
        ".pdf",
        ".doc",
        ".docx",
        ".odt",
        ".rtf",
        # Test or unused code artifacts
        ".gold",
        ".h",
        ".hpp",
        ".inl",
        ".S",
        # Temporary, system, and service files
        ".DS_Store",
        ".log",
        ".tmp",
        ".bak",
        ".swp",
        ".swo",
        # Project files (optional, depends on your context)
        ".csproj",
        ".sln",
        ".vcxproj",
        ".vcproj",
        ".dSYM",
        ".nb",
    }

    lines = []
    for path in sorted(repo_path.rglob("*")):
        if any(part.lower() in {".git", "log", "logs"} for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in excluded_extensions:
            continue
        rel_path = path.relative_to(repo_path).as_posix()
        lines.append(str(rel_path))
    return "\n".join(lines)


def extract_readme_content(repo_path: str) -> str:
    """
    Extracts the content of the README file from the repository.

    If a README file exists in the repository, it will return its content.
    It checks for both "README.md" and "README.rst" files. If no README is found,
    it returns a default message.

    Args:
        repo_path: Path to the repository being explored.

    Returns:
        str: The content of the README file or a message indicating absence.
    """
    for file in ["README.md", "README_en.rst", "README.rst"]:
        readme_path = os.path.join(repo_path, file)

        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                return f.read()
    else:
        return "No README.md file"
