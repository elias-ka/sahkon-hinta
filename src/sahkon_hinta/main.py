from __future__ import annotations

import datetime
import json
import logging
from dataclasses import dataclass
from pathlib import Path

from playwright.async_api import Page, async_playwright
from rich.console import Console
from rich.table import Table

SAHKO_TK_URL = "https://sahko.tk/"
CACHE_FILE = "sahkon_hinta_cache.json"

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


@dataclass
class Prices:
    price_now: str
    day_low: str
    day_high: str
    seven_day_avg: str
    twentyeight_day_avg: str
    vat: str
    timestamp: str

    def save_to_cache(self):
        file = Path(CACHE_FILE).resolve()
        file.touch(exist_ok=True)
        file.write_text(json.dumps(self.__dict__, indent=2))

    @staticmethod
    async def from_page(page: Page) -> Prices:
        async def get_text(selector: str) -> str:
            return (await page.inner_text(selector)).replace(" snt/kWh", "")

        vat = (
            await page.inner_text("ul.nav-pills.nav-justified li.nav-item a.active")
        ).split(" ")[-3]

        return Prices(
            price_now=await get_text("span#price_now"),
            day_low=await get_text("span#min_price"),
            day_high=await get_text("span#max_price"),
            seven_day_avg=await get_text("span#avg"),
            twentyeight_day_avg=await get_text("span#avg_28"),
            vat=vat,
            timestamp=datetime.datetime.now().isoformat(),
        )

    @staticmethod
    def from_json(data: str) -> Prices:
        return Prices(**json.loads(data))


async def fetch_prices_and_update_cache() -> Prices:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(SAHKO_TK_URL)
            prices = await Prices.from_page(page)
            prices.save_to_cache()
            await browser.close()
            return prices
    except Exception as e:
        logger.error(f"Tapahtui virhe: {e}", exc_info=True)
        raise e


def load_cached_prices() -> Prices | None:
    try:
        file = Path(CACHE_FILE).resolve(strict=True)
        return Prices.from_json(file.read_text())
    except FileNotFoundError:
        return None


async def get_prices() -> Prices:
    # the headless browser is slow to start and the prices are updated
    # every day around 1:45 PM finnish time, so we can cache the prices
    if (cached := load_cached_prices()) is not None:
        last_cached = datetime.datetime.fromisoformat(cached.timestamp)
        now = datetime.datetime.now()
        if (now.hour, now.minute) >= (13, 45) and now.date() != last_cached.date():
            return await fetch_prices_and_update_cache()
        else:
            return cached
    return await fetch_prices_and_update_cache()


async def main():
    prices = await get_prices()
    table = Table(
        title=f"Sähkön hinta (snt/kWh) {prices.vat}% alv",
        caption="Lähde: sahko.tk",
        show_edge=False,
        box=None,
        safe_box=True,
    )
    table.add_column("Nyt", justify="center")
    table.add_column("Päivän alin", justify="center")
    table.add_column("Päivän ylin", justify="center")
    table.add_column("7pv keskihinta", justify="center")
    table.add_column("28pv keskihinta", justify="center")

    table.add_row(
        prices.price_now,
        prices.day_low,
        prices.day_high,
        prices.seven_day_avg,
        prices.twentyeight_day_avg,
    )
    console = Console()
    console.print(table)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
