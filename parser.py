# from webdriver_manager.chrome import ChromeDriverManager
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException
from config import USER_AGENT, DRIVER_PATH

if sys.platform == "linux":
    from selenium.webdriver.firefox.options import Options
else:
    from selenium.webdriver.chrome.options import Options


def _create_driver():
    """
        создаем вебдрайвер
    """
    options = Options()
    options.add_argument(f'user-agent={USER_AGENT}')
    options.add_argument('--headless')
    # информация об ошибках которые будут выводиться в терминал
    # INFO = 0, WARNING = 1, LOG_ERROR = 2, LOG_FATAL = 3, default is 0.
    options.add_argument('log-level=3')
    try:
        if sys.platform == "linux":
            driver = webdriver.Firefox(executable_path=DRIVER_PATH, options=options)
        else:
            driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
        return driver
    except WebDriverException as error:
        pass

def _collect_posts_data(driver, request_link):
    """
        собираем данные постов
    """
    try:
        driver.get(request_link)
        posts_data = []
        # получаем часть html со всеми объявлениями
        post_sections = driver.find_elements(by=By.CLASS_NAME, value='items-items-kAJAg')[0]
        # получаем список всех объявлений
        all_posts = post_sections.find_elements(by=By.CLASS_NAME, value='iva-item-body-KLUuy')
        # пробегаемся по всем объявлениям и достаём нужную информацию
        for post in all_posts:
            post_name = post.find_element(by=By.TAG_NAME, value='h3').text if post.find_elements(by=By.TAG_NAME, value='h3') else ' '
            post_price = post.find_element(
                by=By.CLASS_NAME, value='iva-item-priceStep-uq2CQ').text if post.find_elements(
                by=By.CLASS_NAME, value='iva-item-priceStep-uq2CQ') else ' '
            post_badge = post.find_element(
                by=By.CLASS_NAME, value='iva-item-badgeBarStep-DJwW2').text if post.find_elements(
                by=By.CLASS_NAME, value='iva-item-badgeBarStep-DJwW2') else ' '
            post_params = post.find_element(
                by=By.CLASS_NAME, value='iva-item-autoParamsStep-WzfS8').text if post.find_elements(
                by=By.CLASS_NAME, value='iva-item-autoParamsStep-WzfS8') else ' '
            post_description = post.find_element(
                by=By.CLASS_NAME, value='iva-item-descriptionStep-C0ty1').text if post.find_elements(
                by=By.CLASS_NAME, value='iva-item-descriptionStep-C0ty1') else ' '
            post_geo = post.find_element(
                by=By.CLASS_NAME, value='geo-root-zPwRk').text if post.find_elements(
                by=By.CLASS_NAME, value='geo-root-zPwRk') else ' '
            post_link = post.find_element(
                by=By.TAG_NAME, value='a').get_attribute('href') if post.find_elements(
                by=By.TAG_NAME, value='a') else ' '

            posts_data.append({'post_name': post_name,
                               'post_price': post_price,
                               'post_budge': post_badge,
                               'post_params': post_params,
                               'post_description': post_description,
                               'post_geo': post_geo,
                               'post_link': post_link,
                               })
        return posts_data
    except WebDriverException as error:
        pass

def _close_driver(driver):
    """
        закрываем драйвер
    """
    try:
        driver.close()
        driver.quit()
    except WebDriverException as error:
        pass

def get_posts_data(request_link):
    driver = _create_driver()
    posts_data = _collect_posts_data(driver, request_link)
    _close_driver(driver)
    return posts_data

if __name__ == '__main__':
    request_link = 'https://www.avito.ru/uhta/avtomobili?cd=1&f=ASgBAQICAkTyCrCKAZ4SoLgCAUCm_xEk6IeLA~aHiwM&radius=200&searchRadius=200&user=1'
    posts_data = get_posts_data(request_link)
    print('всего найдено за один проход:')
    print(len(posts_data))
