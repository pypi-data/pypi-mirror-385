# 21.05.24

# External libraries
from rich.console import Console


# Internal utilities
from StreamingCommunity.Util.headers import get_headers
from StreamingCommunity.Util.http_client import create_client
from StreamingCommunity.Util.table import TVShowManager
from StreamingCommunity.Api.Template.config_loader import site_constant
from StreamingCommunity.Api.Template.Class.SearchType import MediaManager


# Logic Import
from .util.ScrapeSerie import GetSerieInfo


# Variable
console = Console()
media_search_manager = MediaManager()
table_show_manager = TVShowManager()


def determine_media_type(item):
    """
    Determine if the item is a film or TV series by checking actual seasons count
    using GetSerieInfo.
    """
    try:
        scraper = GetSerieInfo(item.get('path_id'))
        scraper.collect_info_title()
        return scraper.prog_tipology, scraper.prog_description, scraper.prog_year
    
    except Exception as e:
        console.print(f"[red]Error determining media type: {e}[/red]")
        return None, None, None


def title_search(query: str) -> int:
    """
    Search for titles based on a search query.
      
    Parameters:
        - query (str): The query to search for.

    Returns:
        int: The number of titles found.
    """
    media_search_manager.clear()
    table_show_manager.clear()

    search_url = "https://www.raiplay.it/atomatic/raiplay-search-service/api/v1/msearch"
    console.print(f"[cyan]Search url: [yellow]{search_url}")

    json_data = {
        'templateIn': '6470a982e4e0301afe1f81f1',
        'templateOut': '6516ac5d40da6c377b151642',
        'params': {
            'param': query,
            'from': None,
            'sort': 'relevance',
            'onlyVideoQuery': False,
        },
    }

    try:
        response = create_client(headers=get_headers()).post(search_url, json=json_data)
        response.raise_for_status()

    except Exception as e:
        console.print(f"[red]Site: {site_constant.SITE_NAME}, request search error: {e}")
        return 0

    # Limit to only 15 results for performance
    data = response.json().get('agg').get('titoli').get('cards')[:15]
    
    # Process each item and add to media manager
    for item in data:
        media_type, prog_description, prog_year = determine_media_type(item)
        if media_type is None:
            continue

        media_search_manager.add_media({
            'id': item.get('id', ''),
            'name': item.get('titolo', ''),
            'type': media_type,
            'path_id': item.get('path_id', ''),
            'url': f"https://www.raiplay.it{item.get('url', '')}",
            'image': f"https://www.raiplay.it{item.get('immagine', '')}",
            'desc': prog_description,
            'year': prog_year
        })
          
    return media_search_manager.get_length()