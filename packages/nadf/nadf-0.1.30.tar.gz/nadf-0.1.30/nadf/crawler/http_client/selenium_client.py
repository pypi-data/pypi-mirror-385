import os
import pathlib
import ssl
import tempfile
import urllib.request
import asyncio
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.common.exceptions import (
    WebDriverException,
    NoSuchWindowException,
    InvalidSessionIdException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from nadf.crawler.http_client.crawler_client import CrawlerClient
from nadf.exception.ssl_invalid_exception import SSLInvalidException
from dotenv import load_dotenv

load_dotenv()

# ----- SSL 설정 (기존 유지) -----
try:
    import certifi
    _cafile = certifi.where()
    _ctx = ssl.create_default_context(cafile=_cafile)
    _opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=_ctx))
    urllib.request.install_opener(_opener)
except Exception:
    raise SSLInvalidException()


def _detect_chrome_binary() -> str:
    """컨테이너 내 Chrome 바이너리 경로 자동 감지(문자열 반환)."""
    candidates = [
        os.getenv("GOOGLE_CHROME_BIN"),
        os.getenv("CHROME_BIN"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    for c in candidates:
        if c and Path(c).exists():
            return str(c)
    raise RuntimeError(
        "Chrome binary not found. Set $GOOGLE_CHROME_BIN or install google-chrome-stable."
    )


def _detect_version_main(chrome_bin: str) -> Optional[int]:
    """설치된 Chrome 메이저 버전 추출 실패 시 None."""
    # 환경변수로 강제 지정 가능: CHROME_VERSION_MAIN=139
    env_val = os.getenv("CHROME_VERSION_MAIN")
    if env_val and env_val.isdigit():
        return int(env_val)

    try:
        out = subprocess.check_output([chrome_bin, "--version"], text=True).strip()
        # 예) "Google Chrome 139.0.6487.62"
        import re
        m = re.search(r"(\d+)\.", out)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None


def _detect_chromedriver_path() -> Optional[str]:
    """시스템에 설치된 chromedriver 경로 감지 (ARM 환경용)."""
    # 환경변수로 강제 지정 가능: CHROMEDRIVER_PATH=/usr/bin/chromedriver
    env_path = os.getenv("CHROMEDRIVER_PATH")
    if env_path and Path(env_path).exists():
        return str(env_path)

    candidates = [
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
    ]

    for c in candidates:
        if Path(c).exists():
            return str(c)

    return None


def _is_arm_architecture() -> bool:
    """ARM 아키텍처 여부 확인."""
    machine = platform.machine().lower()
    return "arm" in machine or "aarch64" in machine


class SeleniumClient(CrawlerClient):
    def __init__(self):
        self._exec = ThreadPoolExecutor(max_workers=1)
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            # 코루틴 밖에서 생성되면 기존 정책대로 loop를 생성/획득
            self._loop = asyncio.get_event_loop()

        self._lock = asyncio.Lock()

        def _new_driver():
            opts = uc.ChromeOptions()

            opts.binary_location = _detect_chrome_binary()

            opts.add_argument("--headless=new")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_argument("--no-first-run")
            opts.add_argument("--no-default-browser-check")
            opts.add_argument("--remote-debugging-port=0")

            # 깨끗한 프로필(손상된 캐시/권한 이슈 차단)
            user_data_dir = tempfile.mkdtemp(prefix="uc-")
            pathlib.Path(user_data_dir).mkdir(parents=True, exist_ok=True)
            opts.add_argument(f"--user-data-dir={user_data_dir}")

            # ARM 환경에서는 시스템에 설치된 chromedriver 사용
            if _is_arm_architecture():
                driver_path = _detect_chromedriver_path()
                if driver_path:
                    driver = uc.Chrome(
                        driver_executable_path=driver_path,
                        options=opts,
                        use_subprocess=False  # ARM에서 subprocess 호출 시 실패 방지
                    )
                else:
                    # ARM이지만 chromedriver를 찾지 못한 경우 기본 방식 시도
                    driver = uc.Chrome(options=opts)
            else:
                # x86/x64 환경에서는 기존 방식 유지
                driver = uc.Chrome(options=opts)

            driver.set_page_load_timeout(10)
            return driver

        self._new_driver = _new_driver
        # 최초 드라이버 비동기 생성
        self._driver_fut = self._loop.run_in_executor(self._exec, self._new_driver)

    async def _run(self, fn):
        driver = await self._driver_fut
        return await self._loop.run_in_executor(self._exec, lambda: fn(driver))

    async def _recreate_driver(self):
        def _quit_and_create(old):
            try:
                old.quit()
            except Exception:
                pass
            return self._new_driver()

        old = await self._driver_fut
        self._driver_fut = self._loop.run_in_executor(self._exec, lambda: _quit_and_create(old))
        return await self._driver_fut

    async def _ensure_alive(self):
        def _check(drv):
            try:
                _ = drv.current_window_handle
                return True
            except Exception:
                return False

        drv = await self._driver_fut
        alive = await self._loop.run_in_executor(self._exec, lambda: _check(drv))
        if not alive:
            await self._recreate_driver()

    # override
    async def get(self, url: str):
        async with self._lock:
            await self._ensure_alive()

            def _fetch(driver):
                driver.get(url)
                #
                # # 명시적 대기: 나무위키의 주요 콘텐츠 영역이 로드될 때까지 대기
                # try:
                #     wait = WebDriverWait(driver, 10)
                #     # 나무위키의 문서 콘텐츠가 포함된 요소가 로드될 때까지 대기
                #     # 여러 셀렉터를 시도하여 나무위키의 콘텐츠 영역 감지
                #     selectors = [
                #         (By.CLASS_NAME, "wiki-paragraph"),
                #         (By.CLASS_NAME, "wiki-heading"),
                #         (By.TAG_NAME, "article"),
                #         (By.CSS_SELECTOR, "[class*='wiki']"),
                #     ]
                #
                #     for by, selector in selectors:
                #         try:
                #             wait.until(EC.presence_of_element_located((by, selector)))
                #             break
                #         except TimeoutException:
                #             continue
                #
                #     # 추가 대기: JavaScript 렌더링을 위한 짧은 대기
                #     import time
                #     time.sleep(1)
                #
                # except TimeoutException:
                #     # 타임아웃이 발생해도 페이지 소스는 반환 (빈 페이지보다는 낫기 때문)
                #     pass
                #
                return BeautifulSoup(driver.page_source, "html.parser")

            try:
                return await self._run(_fetch)

            except (NoSuchWindowException, InvalidSessionIdException, WebDriverException):
                # 드라이버 재생성 후 한 번 재시도
                await self._recreate_driver()
                return await self._run(_fetch)

    async def close(self):
        try:
            d = await self._driver_fut
            await self._loop.run_in_executor(self._exec, d.quit)
        finally:
            self._exec.shutdown(wait=False)


if __name__ == "__main__":
    async def main():
        client = SeleniumClient()
        try:
            print("나루토 크롤링")
            soup = await client.get("https://namu.wiki/w/나루토")
            print(soup.title.text if soup.title else "(no title)")
            print(soup.text)
        finally:
            await client.close()

    asyncio.run(main())
