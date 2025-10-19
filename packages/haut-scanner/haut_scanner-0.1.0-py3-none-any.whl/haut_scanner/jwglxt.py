"""用于发现可访问的 HAUT 教务系统入口的扫描工具。"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Iterable, List, Dict, Optional

import aiohttp
from bs4 import BeautifulSoup


DEFAULT_OUTPUT = "jwglxt_urls.json"


class JwglxtScanner:
    """扫描 IP 段以发现可访问的教务系统入口。"""

    def __init__(
        self,
        *,
        ip_range: Iterable[int] | None = None,
        base_url: str = "http://172.18.254.{}/jwglxt/",
        timeout: float = 10.0,
    ) -> None:
        self.ip_range = list(ip_range) if ip_range is not None else list(range(1, 255))
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.results: List[Dict[str, str]] = []

    async def check_site(self, ip: int) -> None:
        url = self.base_url.format(ip)
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, "html.parser")
                        xtmc_element = soup.find(id="xtmc")
                        if xtmc_element:
                            title = xtmc_element.get_text(strip=True)
                            self.results.append(
                                {
                                    "URL": (
                                        "http://172.18.254."
                                        f"{ip}/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?"
                                        "gnmkdm=N253512&layout=default"
                                    ),
                                    "title": title,
                                }
                            )
        except Exception:  # noqa: BLE001 - match original behaviour
            pass  # 忽略异常，继续扫描

    async def scan(self) -> None:
        tasks = [self.check_site(ip) for ip in self.ip_range]
        await asyncio.gather(*tasks)

    def save_results(self, output_path: str | Path = DEFAULT_OUTPUT) -> Optional[Path]:
        if not self.results:
            return None

        path = Path(output_path)
        path.write_text(
            json.dumps(self.results, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path


async def _run_async() -> JwglxtScanner:
    scanner = JwglxtScanner()
    print("正在扫描可访问的教务系统入口...")
    await scanner.scan()
    output_file = scanner.save_results()
    print(f"扫描完成，共发现 {len(scanner.results)} 个可访问入口")
    if output_file:
        print(f"结果已保存至 {output_file}")
    return scanner


def run() -> None:
    """控制台脚本的入口函数。"""

    asyncio.run(_run_async())


if __name__ == "__main__":
    run()
