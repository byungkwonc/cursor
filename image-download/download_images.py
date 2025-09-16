#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_images.py
------------------
웹페이지 URL을 입력하면 해당 페이지의 모든 이미지를 로컬 폴더에 저장합니다.
- 외부 라이브러리 불필요(표준 라이브러리만 사용)
- 상대/절대 경로 처리
- lazy-loading(data-src 등) 처리
- srcset에서 가장 큰 후보 선택
- 중복(내용 동일) 방지
- 파일명 충돌 방지 및 확장자 추론
사용법:
    python download_images.py "https://example.com" -o ./images
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import time
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

# --------- Utilities ---------
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

IMAGE_EXTS = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/pjpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
    "image/x-icon": ".ico",
    "image/vnd.microsoft.icon": ".ico",
    "image/svg+xml": ".svg",
    "image/tiff": ".tiff",
    "image/avif": ".avif",
}

DATA_URL_RE = re.compile(r"^data:", re.IGNORECASE)
CSS_URL_RE = re.compile(r'url\((["\']?)(.+?)\1\)')

def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\-. ]+", "_", name)
    name = name.strip()
    return name or "image"

def guess_ext_from_url(url: str) -> str:
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    if ext and len(ext) <= 6:
        return ext
    return ""

def choose_src_from_srcset(srcset: str, base_url: str) -> str | None:
    # Pick the last candidate (보통 가장 큰 해상도)
    # Format: "img1.jpg 320w, img2.jpg 640w, img3.jpg 1024w"
    try:
        candidates = [c.strip() for c in srcset.split(",") if c.strip()]
        if not candidates:
            return None
        last = candidates[-1]
        url_part = last.split()[0]
        return urljoin(base_url, url_part)
    except Exception:
        return None

# --------- HTML Parser ---------
class ImageCollector(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.image_urls: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag.lower() == "img":
            self._collect_from_attrs(dict(attrs))
        else:
            # style="background-image:url(...)" 형태도 수집
            attr_dict = dict(attrs)
            style = attr_dict.get("style")
            if style:
                for m in CSS_URL_RE.finditer(style):
                    url = m.group(2)
                    if not DATA_URL_RE.match(url):
                        self.image_urls.append(urljoin(self.base_url, url))

    def _collect_from_attrs(self, attr: dict):
        # 우선순위: srcset(가장 큰 것) -> src -> data-* 후보들
        for key in ("srcset",):
            if attr.get(key):
                chosen = choose_src_from_srcset(attr[key], self.base_url)
                if chosen:
                    self.image_urls.append(chosen)
                    return
        for key in ("src", "data-src", "data-original", "data-lazy", "data-echo",
                    "data-image", "data-hires", "data-srcset"):
            val = attr.get(key)
            if val:
                # data-srcset 같은 경우에도 srcset 규칙 적용 시도
                if "srcset" in key:
                    chosen = choose_src_from_srcset(val, self.base_url)
                    if chosen:
                        self.image_urls.append(chosen)
                        return
                if not DATA_URL_RE.match(val):
                    self.image_urls.append(urljoin(self.base_url, val))
                    return

# --------- Networking ---------
def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as resp:
        return resp.read()

def fetch_head(url: str):
    # urllib에는 HEAD 편의가 없어 GET 후 헤더만 참고
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as resp:
        return resp.info()

# --------- Download Logic ---------
def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def unique_path(base_dir: str, base_name: str, ext: str) -> str:
    base = sanitize_filename(base_name)
    candidate = os.path.join(base_dir, base + ext)
    if not os.path.exists(candidate):
        return candidate
    i = 2
    while True:
        candidate = os.path.join(base_dir, f"{base}_{i}{ext}")
        if not os.path.exists(candidate):
            return candidate
        i += 1

def download_image(url: str, out_dir: str, seen_hashes: set[str]) -> str | None:
    try:
        if DATA_URL_RE.match(url):
            return None

        headers = fetch_head(url)
        content_type = headers.get_content_type() if headers else None
        ext = IMAGE_EXTS.get(content_type or "", "")

        # 확장자 추론 실패 시 URL에서 추정
        if not ext:
            ext = guess_ext_from_url(url) or ".bin"

        # 실제 다운로드
        data = fetch(url)

        # 중복 검사(내용 해시)
        h = hashlib.sha256(data).hexdigest()
        if h in seen_hashes:
            return None
        seen_hashes.add(h)

        # 파일명 결정
        path_part = urlparse(url).path
        base_name = os.path.basename(path_part) or "image"
        base_name = os.path.splitext(base_name)[0] or "image"
        save_path = unique_path(out_dir, base_name, ext)

        with open(save_path, "wb") as f:
            f.write(data)
        return save_path
    except Exception as e:
        sys.stderr.write(f"[WARN] Failed: {url} -> {e}\n")
        return None

def collect_images_from_html(html: str, base_url: str) -> list[str]:
    parser = ImageCollector(base_url)
    parser.feed(html)
    # 중복 URL 제거(순서 유지)
    seen = set()
    uniq = []
    for u in parser.image_urls:
        if u not in seen:
            uniq.append(u)
            seen.add(u)
    return uniq

def crawl(url: str, out_dir: str) -> tuple[int, int]:
    ensure_dir(out_dir)
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as resp:
        html_bytes = resp.read()
        charset = resp.headers.get_content_charset() or "utf-8"
        try:
            html = html_bytes.decode(charset, errors="replace")
        except Exception:
            html = html_bytes.decode("utf-8", errors="replace")
        base_url = resp.geturl()  # redirects 고려

    img_urls = collect_images_from_html(html, base_url)
    print(f"발견한 이미지 URL 수: {len(img_urls)}")
    saved = 0
    skipped = 0
    seen_hashes: set[str] = set()
    for i, img_url in enumerate(img_urls, 1):
        print(f"[{i}/{len(img_urls)}] 다운로드 중: {img_url}")
        path = download_image(img_url, out_dir, seen_hashes)
        if path:
            saved += 1
            print(f" -> 저장 완료: {path}")
        else:
            skipped += 1
    return saved, skipped

def main():
    parser = argparse.ArgumentParser(description="웹페이지의 모든 이미지를 로컬로 저장합니다.")
    parser.add_argument("url", help="대상 웹페이지 URL")
    parser.add_argument("-o", "--out", default=None, help="저장 폴더(기본: ./images_YYYYmmdd_HHMMSS)")
    args = parser.parse_args()

    out_dir = args.out or f"./images_{time.strftime('%Y%m%d_%H%M%S')}"
    saved, skipped = crawl(args.url, out_dir)
    print("\n===== 결과 =====")
    print(f"저장 폴더: {os.path.abspath(out_dir)}")
    print(f"저장: {saved}개, 건너뜀: {skipped}개")

if __name__ == "__main__":
    main()
