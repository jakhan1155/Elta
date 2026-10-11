"""
Журнал работы бота (пишется в logs/bot.log через scripts/run_bot.ps1).
"""
import logging


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
