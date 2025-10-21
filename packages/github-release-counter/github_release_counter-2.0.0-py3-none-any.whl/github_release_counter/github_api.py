import requests
from typing import List, Dict, Any, Tuple, Optional

# --- Custom Exceptions ---
class RepoFormatError(Exception):
    """Excepción para formato de repositorio inválido."""
    pass

class GitHubAPIError(Exception):
    """Excepción para errores relacionados con la API de GitHub."""
    pass

class GitHubAPI:
    """
    Una clase para interactuar con la API de GitHub y obtener estadísticas de lanzamientos.
    """
    def __init__(self, repo_path: str, github_token: Optional[str] = None):
        """
        Inicializa la clase GitHubAPI.

        Args:
            repo_path (str): La ruta del repositorio en formato 'propietario/repositorio' o una URL de GitHub.
            github_token (str, optional): Token personal de acceso a GitHub.
        
        Raises:
            RepoFormatError: Si el formato del repositorio es inválido.
        """
        self.repo_path = repo_path
        self.github_token = github_token
        self.owner, self.repo = self._parse_repo_path(repo_path)
        if not self.owner or not self.repo:
            raise RepoFormatError("Formato de repositorio inválido. Debe ser 'propietario/repositorio' o una URL de GitHub válida.")

    @staticmethod
    def _parse_repo_path(repo_input: str) -> Optional[Tuple[str, str]]:
        """
        Analiza la entrada del repositorio para extraer el propietario y el nombre.
        Admite formatos como 'propietario/repo', URLs https y URLs git.
        """
        path = repo_input.strip()

        if path.startswith("https://github.com/"):
            path = path[len("https://github.com/"):]
        elif path.startswith("git@github.com:"):
            path = path[len("git@github.com:"):]

        if path.endswith(".git"):
            path = path[:-len(".git")]
        
        path = path.strip('/')

        if path.lower().endswith('/releases'):
            path = path[:-len('/releases')].strip('/')

        parts = path.split('/')
        if len(parts) == 2 and all(parts):
            return parts[0], parts[1]
        
        return None

    def get_releases(self) -> List[Dict[str, Any]]:
        """
        Obtiene y procesa las estadísticas de descargas de los lanzamientos de un repositorio.

        Returns:
            List[Dict[str, Any]]: Una lista de diccionarios con los detalles de los lanzamientos.
        
        Raises:
            GitHubAPIError: Si ocurre un error al comunicarse con la API de GitHub.
        """
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases"
        headers = {}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Error de conexión o HTTP: {e}") from e

        try:
            releases_data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            raise GitHubAPIError("No se pudo decodificar la respuesta JSON de la API.") from e

        if not isinstance(releases_data, list):
            if isinstance(releases_data, dict) and releases_data.get("message") == "Not Found":
                raise GitHubAPIError(f"Repositorio '{self.owner}/{self.repo}' no encontrado o no tienes acceso.")
            else:
                raise GitHubAPIError("Respuesta inesperada de la API. Se esperaba una lista de lanzamientos.")

        return self._process_releases(releases_data)

    def _process_releases(self, releases_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Procesa la lista de lanzamientos de la API."""
        processed_releases = []
        for release in releases_data:
            release_info = {
                'tag_name': release.get('tag_name', 'N/A'),
                'release_name': release.get('name', release.get('tag_name', 'N/A')),
                'published_at': release.get('published_at', 'N/A'),
                'author': release.get('author', {}).get('login', 'Desconocido'),
                'prerelease': release.get('prerelease', False),
                'draft': release.get('draft', False),
                'html_url': release.get('html_url', 'N/A'),
                'assets': []
            }
            
            release_downloads = 0
            for asset in release.get('assets', []):
                size_bytes = asset.get('size', 0)
                size_mb = round(size_bytes / (1024 * 1024), 2) if size_bytes else 0
                asset_info = {
                    'name': asset.get('name', 'N/A'),
                    'download_count': asset.get('download_count', 0),
                    'size_bytes': size_bytes,
                    'size_mb': size_mb,
                    'content_type': asset.get('content_type', 'N/A'),
                    'browser_download_url': asset.get('browser_download_url', 'N/A')
                }
                release_info['assets'].append(asset_info)
                release_downloads += asset_info['download_count']
            
            release_info['total_release_downloads'] = release_downloads
            processed_releases.append(release_info)
        
        return processed_releases
