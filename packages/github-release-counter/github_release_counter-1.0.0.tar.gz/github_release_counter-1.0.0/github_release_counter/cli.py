import requests
import argparse
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

# --- Custom Exceptions ---
class RepoFormatError(Exception):
    """Excepción para formato de repositorio inválido."""
    pass

class GitHubAPIError(Exception):
    """Excepción para errores relacionados con la API de GitHub."""
    pass

def parse_repo_path(repo_input: str) -> Optional[Tuple[str, str]]:
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

def obtener_stats_descargas(repo_path: str, github_token: str = None) -> List[Dict[str, Any]]:
    """
    Obtiene las estadísticas de descargas de los lanzamientos de un repositorio de GitHub.

    Args:
        repo_path (str): La ruta del repositorio en formato 'propietario/repositorio' o una URL de GitHub.
        github_token (str, optional): Token personal de acceso a GitHub para aumentar el límite de la API.

    Returns:
        List[Dict[str, Any]]: Una lista de diccionarios, donde cada diccionario representa un lanzamiento
        con sus detalles y una lista de sus assets.
    
    Raises:
        RepoFormatError: Si el formato del repositorio es inválido.
        GitHubAPIError: Si ocurre un error al comunicarse con la API de GitHub.
    """
    parsed_repo = parse_repo_path(repo_path)
    if not parsed_repo:
        raise RepoFormatError("Formato de repositorio inválido. Debe ser 'propietario/repositorio' o una URL de GitHub válida.")

    owner, repo = parsed_repo
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"

    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

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
            raise GitHubAPIError(f"Repositorio '{owner}/{repo}' no encontrado o no tienes acceso.")
        else:
            raise GitHubAPIError("Respuesta inesperada de la API. Se esperaba una lista de lanzamientos.")

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

def display_stats(owner: str, repo: str, releases_data: List[Dict[str, Any]]) -> None:
    """
    Muestra las estadísticas de descargas de los lanzamientos en la consola.

    Args:
        owner (str): El propietario del repositorio.
        repo (str): El nombre del repositorio.
        releases_data (List[Dict[str, Any]]): Datos estructurados de los lanzamientos.
    """
    total_downloads = 0
    print(f"\n--- Estadísticas de Lanzamientos para {owner}/{repo} ---\n")

    for release in releases_data:
        published_at_str = release['published_at']
        formatted_date = "N/A"
        if published_at_str != 'N/A':
            try:
                # Parse the ISO 8601 format (e.g., 2024-04-01T06:32:13Z)
                dt_object = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                formatted_date = dt_object.strftime("%d/%m/%Y")
            except ValueError:
                pass # Keep N/A if parsing fails

        print(f"Lanzamiento: {release['release_name']} (Tag: {release['tag_name']})")
        print(f"  Publicado el: {formatted_date}")
        print(f"  Autor: {release['author']}")
        print(f"  Pre-lanzamiento: {'Sí' if release['prerelease'] else 'No'}, Borrador: {'Sí' if release['draft'] else 'No'}")
        print(f"  URL: {release['html_url']}")

        assets = release['assets']
        if assets:
            print("  Assets:")
            for asset in assets:
                print(f"    - {asset['name']}")
                print(f"      Descargas: {asset['download_count']}")
                print(f"      Tamaño: {asset['size_mb']} MB")
                print(f"      Tipo: {asset['content_type']}")
                print(f"      URL de descarga: {asset['browser_download_url']}")
        else:
            print("  No hay assets para este lanzamiento.")

        print(f"  Total de descargas para este lanzamiento: {release['total_release_downloads']}\n")
        total_downloads += release['total_release_downloads']

    print(f"--- Resumen ---\n")
    print(f"Descargas totales de todos los lanzamientos: {total_downloads}")

    if releases_data:
        # Sort releases by published_at to ensure correct first/last
        # The API usually returns them in reverse chronological order, but it's safer to sort.
        sorted_releases = sorted(
            [r for r in releases_data if r['published_at'] != 'N/A'],
            key=lambda x: x['published_at']
        )

        if len(sorted_releases) > 1:
            first_release_date_str = sorted_releases[0]['published_at']
            last_release_date_str = sorted_releases[-1]['published_at']

            try:
                first_dt = datetime.fromisoformat(first_release_date_str.replace('Z', '+00:00'))
                last_dt = datetime.fromisoformat(last_release_date_str.replace('Z', '+00:00'))
                time_diff = last_dt - first_dt

                days = time_diff.days
                years = days // 365
                remaining_days = days % 365
                months = remaining_days // 30 # Approximation for months

                time_diff_str = ""
                if years > 0:
                    time_diff_str += f"{years} año{'s' if years > 1 else ''}"
                if months > 0:
                    if time_diff_str: time_diff_str += ", "
                    time_diff_str += f"{months} mes{'es' if months > 1 else ''}"
                if remaining_days % 30 > 0 or (years == 0 and months == 0 and days > 0): # If less than a month or just days
                    if time_diff_str: time_diff_str += ", "
                    time_diff_str += f"{remaining_days % 30} día{'s' if remaining_days % 30 > 1 else ''}"
                
                if not time_diff_str and days == 0:
                    time_diff_str = "menos de un día"
                elif not time_diff_str: # Fallback for very short periods
                    time_diff_str = f"{days} día{'s' if days > 1 else ''}"


                print(f"Tiempo entre el primer y último lanzamiento: {time_diff_str}")
            except ValueError:
                print("No se pudo calcular el tiempo entre lanzamientos debido a un formato de fecha inválido.")
        elif len(sorted_releases) == 1:
            print("Solo hay un lanzamiento, no se puede calcular el tiempo entre lanzamientos.")
        else:
            print("No hay lanzamientos válidos para calcular el tiempo entre ellos.")


def main():
    parser = argparse.ArgumentParser(description="Obtiene las estadísticas de descargas de los lanzamientos de un repositorio de GitHub.")
    parser.add_argument(
        "repo_path",
        help="La ruta del repositorio en formato 'propietario/repositorio' (ej. octocat/Spoon-Knife)."
    )
    parser.add_argument(
        "--token", "-t",
        help="Token personal de acceso a GitHub para aumentar el límite de la API."
    )
    args = parser.parse_args()
    
    try:
        releases_data = obtener_stats_descargas(args.repo_path, args.token)
        
        if releases_data:
            parsed_repo = parse_repo_path(args.repo_path)
            if parsed_repo: # Debería pasar siempre si releases_data no está vacío
                owner, repo = parsed_repo
                display_stats(owner, repo, releases_data)
        else:
            # Si la lista está vacía, significa que no hay lanzamientos.
            parsed_repo = parse_repo_path(args.repo_path)
            if parsed_repo:
                owner, repo = parsed_repo
                print(f"El repositorio '{owner}/{repo}' no tiene lanzamientos (releases).")

    except (RepoFormatError, GitHubAPIError) as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
