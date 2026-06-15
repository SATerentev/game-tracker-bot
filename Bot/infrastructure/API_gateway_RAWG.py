import aiohttp
import logging

import config
from entity.RAWG_GameDTO import RAWG_GameDTO
from entity.Result import Result

API_KEY = config.API_KEY
logger = logging.getLogger(__name__)

async def search_game(game_name: str) -> Result:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.rawg.io/api/games?"
                                   f"key={API_KEY}&"
                                   f"search={game_name}&"
                                   f"page=1&"
                                   f"page_size=5&"
                                   f"ordering=-added") as resp:
                data = await resp.json()
        results = data['results']
        games = []
        if results is None or len(results) == 0:
            return Result(None, False, "Game not found")
        for result in results:
            games.append(RAWG_GameDTO(name=result['name'], rawg_id=result['id']))
        return Result(games, True, "")
    except Exception as e:
        logger.error("RAWG API error while searching '%s': %s", game_name, e, exc_info=True)
        return Result(None, False, "Error occurred while searching for game\n" + str(e))