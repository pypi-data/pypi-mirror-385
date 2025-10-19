import os
import platform
from subprocess import DEVNULL
try:
    from subprocess import CREATE_NO_WINDOW
except ImportError:
    CREATE_NO_WINDOW = 0

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import SessionNotCreatedException
from webdriver_manager.chrome import ChromeDriverManager

from .utils import get_localized_message

def setup_webdriver(lang: str, headless: bool = True) -> webdriver.Chrome:
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    os.environ["ABSL_LOGGING_MIN_LOG_LEVEL"] = "3"

    driver = None
    try:
        chrome_options = Options()
        system_platform = platform.system()

        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")  # Windows'ta faydalı
            chrome_options.add_argument("--window-size=1920,1080")

        if system_platform == "Linux":
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
        elif system_platform == "Darwin":
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-popup-blocking")
        elif system_platform == "Windows":
            chrome_options.add_argument("--disable-extensions")

        chrome_options.add_argument("--lang=tr-TR")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36"
        )

        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-logging", "enable-automation"]
        )

        service = Service(ChromeDriverManager().install(), log_output=DEVNULL)
        try:
            service.creationflags = CREATE_NO_WINDOW
        except Exception:
            pass

        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    except SessionNotCreatedException as e:
        raise RuntimeError(get_localized_message("webdriver_version_mismatch", lang, e))
    except Exception as e:
        if driver:
            driver.quit()
        raise RuntimeError(get_localized_message("webdriver_setup_failed", lang, e))