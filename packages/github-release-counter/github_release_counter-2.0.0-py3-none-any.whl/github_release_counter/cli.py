import argparse
from .github_api import GitHubAPI, RepoFormatError, GitHubAPIError
from .display import display_stats, display_tags, display_assets

def main():
    parser = argparse.ArgumentParser(
        description="Obtiene las estadísticas de descargas de los lanzamientos de un repositorio de GitHub."
    )
    parser.add_argument(
        "repo_path",
        help="La ruta del repositorio en formato 'propietario/repositorio' (ej. octocat/Spoon-Knife)."
    )
    parser.add_argument(
        "--token", "-t",
        help="Token personal de acceso a GitHub para aumentar el límite de la API."
    )
    parser.add_argument(
        "--tags-only",
        action="store_true",
        help="Muestra solo los nombres de los tags de los lanzamientos."
    )
    parser.add_argument(
        "--assets-only",
        action="store_true",
        help="Muestra solo los nombres de los assets y sus descargas."
    )
    args = parser.parse_args()
    
    try:
        api = GitHubAPI(args.repo_path, args.token)
        releases_data = api.get_releases()
        
        if not releases_data:
            print(f"El repositorio '{api.owner}/{api.repo}' no tiene lanzamientos (releases).")
            return

        if args.tags_only:
            display_tags(releases_data)
        elif args.assets_only:
            display_assets(releases_data)
        else:
            display_stats(api.owner, api.repo, releases_data)

    except (RepoFormatError, GitHubAPIError) as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
