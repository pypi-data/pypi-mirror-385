from datetime import datetime
from typing import List, Dict, Any

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
                dt_object = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                formatted_date = dt_object.strftime("%d/%m/%Y")
            except ValueError:
                pass

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
                months = remaining_days // 30

                time_diff_str = ""
                if years > 0:
                    time_diff_str += f"{years} año{'s' if years > 1 else ''}"
                if months > 0:
                    if time_diff_str: time_diff_str += ", "
                    time_diff_str += f"{months} mes{'es' if months > 1 else ''}"
                if remaining_days % 30 > 0 or (years == 0 and months == 0 and days > 0):
                    if time_diff_str: time_diff_str += ", "
                    time_diff_str += f"{remaining_days % 30} día{'s' if remaining_days % 30 > 1 else ''}"
                
                if not time_diff_str and days == 0:
                    time_diff_str = "menos de un día"
                elif not time_diff_str:
                    time_diff_str = f"{days} día{'s' if days > 1 else ''}"

                print(f"Tiempo entre el primer y último lanzamiento: {time_diff_str}")
            except ValueError:
                print("No se pudo calcular el tiempo entre lanzamientos debido a un formato de fecha inválido.")
        elif len(sorted_releases) == 1:
            print("Solo hay un lanzamiento, no se puede calcular el tiempo entre lanzamientos.")
        else:
            print("No hay lanzamientos válidos para calcular el tiempo entre ellos.")

def display_tags(releases_data: List[Dict[str, Any]]) -> None:
    """
    Muestra solo los nombres de los tags de los lanzamientos.
    """
    print("\n--- Tags de Lanzamientos ---\n")
    for release in releases_data:
        print(release.get('tag_name', 'N/A'))

def display_assets(releases_data: List[Dict[str, Any]]) -> None:
    """
    Muestra los assets de cada lanzamiento con su contador de descargas.
    """
    print("\n--- Assets de Lanzamientos ---\n")
    for release in releases_data:
        print(f"Lanzamiento: {release.get('release_name', 'N/A')} (Tag: {release.get('tag_name', 'N/A')})")
        assets = release.get('assets', [])
        if assets:
            for asset in assets:
                print(f"  - {asset.get('name', 'N/A')}: {asset.get('download_count', 0)} descargas")
        else:
            print("  No hay assets.")
        print()
