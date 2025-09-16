#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_images_async.py
------------------------
웹페이지 URL을 입력하면 해당 페이지의 모든 이미지를 **비동기 방식**으로 동시에 다운로드합니다.

필요 라이브러리:
    pip install aiohttp aiofiles

사용법:
    python download_images_async.py "https://example.com" -o ./images
"""
import argparse
import asyncio
import hashlib
import os
import re
import time
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import aiohttp
import aiofiles

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

IMAGE_EXTS = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
    "image/x-icon": ".ico",
    "image/svg+xml": ".svg",
    "image/tiff": ".tiff",
    "image/avif": ".avif",
}

DATA_URL_RE = re.compile(r"^data:", re.IGNORECASE)
CSS_URL_RE = re.compile(r'url\((["\']?)(.+?)\1\)')

def sanitize_filename(name: str) -> str:
    return re.sub(r"[^\w\-.]+", "_", name) or "image"

def guess_ext_from_url(url: str) -> str:
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    if ext and len(ext) <= 6:
        return ext
    return ""

def choose_src_from_srcset(srcset: str, base_url: str) -> str | None:
    try:
        candidates = [c.strip() for c in srcset.split(",") if c.strip()]
        if not candidates:
            return None
        last = candidates[-1]
        url_part = last.split()[0]
        return urljoin(base_url, url_part)
    except Exception:
        return None

class ImageCollector(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.image_urls: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag.lower() == "img":
            self._collect_from_attrs(dict(attrs))
        else:
            style = dict(attrs).get("style")
            if style:
                for m in CSS_URL_RE.finditer(style):
                    self.image_urls.append(urljoin(self.base_url, m.group(2)))

    def _collect_from_attrs(self, attr: dict):
        if attr.get("srcset"):
            chosen = choose_src_from_srcset(attr["srcset"], self.base_url)
            if chosen:
                self.image_urls.append(chosen)
                return
        for key in ("src", "data-src", "data-original", "data-lazy", "data-image"):
            val = attr.get(key)
            if val and not DATA_URL_RE.match(val):
                self.image_urls.append(urljoin(self.base_url, val))
                return

async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url, timeout=30) as resp:
        html = await resp.text(errors="replace")
        return html

def collect_images_from_html(html: str, base_url: str) -> list[str]:
    parser = ImageCollector(base_url)
    parser.feed(html)
    seen, uniq = set(), []
    for u in parser.image_urls:
        if u not in seen:
            uniq.append(u)
            seen.add(u)
    return uniq

async def download_image(session, url: str, out_dir: str, seen_hashes: set[str], sem: asyncio.Semaphore):
    async with sem:
        try:
            async with session.get(url, timeout=30) as resp:
                if resp.status != 200:
                    print(f"[WARN] {url} -> HTTP {resp.status}")
                    return None

                content_type = resp.headers.get("Content-Type", "").split(";")[0]
                ext = IMAGE_EXTS.get(content_type, "") or guess_ext_from_url(url) or ".bin"
                data = await resp.read()

            h = hashlib.sha256(data).hexdigest()
            if h in seen_hashes:
                return None
            seen_hashes.add(h)

            base_name = os.path.basename(urlparse(url).path) or "image"
            base_name = os.path.splitext(base_name)[0] or "image"
            base_name = sanitize_filename(base_name)
            save_path = os.path.join(out_dir, base_name + ext)

            i = 2
            while os.path.exists(save_path):
                save_path = os.path.join(out_dir, f"{base_name}_{i}{ext}")
                i += 1

            async with aiofiles.open(save_path, "wb") as f:
                await f.write(data)

            print(f"[OK] {url} -> {save_path}")
            return save_path
        except Exception as e:
            print(f"[ERROR] {url} -> {e}")
            return None

async def crawl(url: str, out_dir: str, concurrency: int = 10):
    os.makedirs(out_dir, exist_ok=True)
    connector = aiohttp.TCPConnector(limit=concurrency)
    sem = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession(connector=connector, headers={"User-Agent": USER_AGENT}) as session:
        html = await fetch_html(session, url)
        img_urls = collect_images_from_html(html, url)
        print(f"발견된 이미지: {len(img_urls)}개")

        seen_hashes: set[str] = set()
        tasks = [download_image(session, u, out_dir, seen_hashes, sem) for u in img_urls]
        results = await asyncio.gather(*tasks)
        saved = [r for r in results if r]
        print(f"다운로드 완료: {len(saved)}개")

def main():
    parser = argparse.ArgumentParser(description="웹페이지의 모든 이미지를 비동기 방식으로 로컬 저장")
    parser.add_argument("url", help="대상 웹페이지 URL")
    parser.add_argument("-o", "--out", default=None, help="저장 폴더 (기본: ./images_날짜)")
    parser.add_argument("-c", "--concurrency", type=int, default=10, help="동시 다운로드 개수")
    args = parser.parse_args()

    out_dir = args.out or f"./images_{time.strftime('%Y%m%d_%H%M%S')}"
    asyncio.run(crawl(args.url, out_dir, args.concurrency))

if __name__ == "__main__":
    main()