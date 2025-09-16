# 웹페이지의 모든 이미지를 로컬 폴더에 저장

## download_images.py
### 기능 요약
- 표준 라이브러리만 사용(추가 설치 불필요)
- 상대/절대 경로 자동 처리
- src, srcset, data-src, data-original, data-lazy 등 lazy-loading 속성 지원
- srcset은 보통 가장 큰 해상도(마지막 후보)를 선택
- style="background-image:url(...)"에 들어있는 이미지도 수집
- 중복 이미지는 내용 해시(SHA-256)로 걸러 저장
- 응답 헤더의 Content-Type과 URL 확장자에서 적절한 확장자 추론
- 파일명 충돌 시 자동으로 _2, _3…을 붙여 안전 저장
### 사용법
```bash
# 기본 사용
python download_images.py "https://example.com"

# 저장 폴더 지정
python download_images.py "https://example.com" -o ./images
```
### 참고
- 데이터 URL(data:로 시작) 형식 이미지는 건너뜁니다.
- CSS 파일 내부의 background-image 등은 이 스크립트 범위 밖이라, 페이지 인라인 style에 한해 수집합니다.


## download_images_async.py
### 기능 요약
- aiohttp + asyncio 로 여러 이미지를 동시에 다운로드 (비동기)
- 기본 동시성(concurrency)은 10, -c 옵션으로 조절 가능
- srcset, src, data-src 등 다양한 속성 지원
- 중복 이미지(내용 동일)는 해시로 필터링
- 자동 파일명 중복 방지
### 사용법
```bash
pip install aiohttp aiofiles
# 기본 사용
python download_images_async.py "https://example.com"

# 저장 폴더 지정
python download_images_async.py "https://example.com" -o ./images

# 동시 다운로드 개수 지정
python download_images_async.py "https://example.com" -c 20
```