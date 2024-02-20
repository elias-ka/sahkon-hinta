from __future__ import annotations

import logging
from dataclasses import dataclass

from playwright.async_api import Page, async_playwright
from rich.console import Console
from rich.table import Table

sahko_tk_url = "https://sahko.tk/"

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


@dataclass
class Price:
    price_now: str
    day_low: str
    day_high: str
    seven_day_avg: str
    twentyeight_day_avg: str
    vat: str

    @classmethod
    async def from_page(cls, page: Page) -> Price:
        async def get_text(selector: str) -> str:
            return (await page.inner_text(selector)).replace(" snt/kWh", "")

        return Price(
            price_now=await get_text("span#price_now"),
            day_low=await get_text("span#min_price"),
            day_high=await get_text("span#max_price"),
            seven_day_avg=await get_text("span#avg"),
            twentyeight_day_avg=await get_text("span#avg_28"),
            vat=await cls._get_vat(page),
        )

    @staticmethod
    async def _get_vat(page: Page) -> str:
        text = await page.inner_text("ul.nav-pills.nav-justified li.nav-item a.active")
        return text.split(" ")[-3]


async def run() -> None:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(sahko_tk_url)
            prices = await Price.from_page(page)
            await browser.close()
    except Exception as e:
        logger.error(f"Tapahtui virhe: {e}", exc_info=True)
        return

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


def main() -> None:
    import asyncio

    asyncio.run(run())


if __name__ == "__main__":
    main()
