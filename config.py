import sys

if sys.platform == "linux":
    from webdriver_manager.firefox import GeckoDriverManager
    DRIVER_PATH = GeckoDriverManager().install()
else:
    from webdriver_manager.chrome import ChromeDriverManager
    DRIVER_PATH = ChromeDriverManager().install()


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
CHECK_FREQUENCY = 60
