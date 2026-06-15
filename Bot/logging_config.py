import logging
from pathlib import Path

LOG_FILE = Path(__file__).parent / "bot.log"


def setup_logging() -> None:
    # \/ Закомментировать при запуске через Docker — логи будут писаться в stdout контейнера \/
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
        force=True,
    )
    # /\ Закомментировать при запуске через Docker /\
