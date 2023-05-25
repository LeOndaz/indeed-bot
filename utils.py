import logging
from inspect import iscoroutinefunction
from typing import List
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from fastapi import WebSocket
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from consts import ua
from errors import MissingInfoError

logger = logging.getLogger(__file__)
f_handler = logging.FileHandler("logs.log")
f_handler.setLevel(logging.INFO)
f_format = logging.Formatter("[%(levelname)s]: %(asctime)s %(message)s")
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)


def setup_webdriver(proxy=None):
    """
    Init a new webdriver changing user-agent every time..
    :return:
    """
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={ua.random}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # enable proxy-ing
    if proxy:
        host, port = proxy
        options.add_argument(f"--proxy-server={host}:{port}")

    # save profile data
    # options.add_argument(f"user-data-dir={PROFILE_PATH}")

    service = webdriver.chrome.service.Service(executable_path="chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def navigate_to_url(driver: webdriver.Chrome, url: str):
    driver.get(url)


def open_in_new_tab(driver: webdriver.Chrome, url: str):
    driver.execute_script(f"window.open('{url}', '_blank')")


def switch_to_tab(driver: webdriver.Chrome, handle):
    """
    Switches to an active tab.
    :param driver: Driver to act on.
    :param tab_num: Tab number, 0-indexed.
    :return: None
    """
    driver.switch_to.window(handle)


def clear_input(input):
    input.get_attribute("value")
    input.send_keys(Keys.CONTROL + "A" + Keys.DELETE)


def paginated_search_manager(driver: webdriver.Chrome, what, where):
    """
    1-Indexed.
    :param what:
    :param where:
    :param driver:
    :return:
    """

    def switch_to(page_num):
        parsed_url = list(urlparse(driver.current_url))
        qs = parse_qs(parsed_url[4])
        qs["start"] = (page_num - 1) * 10

        if qs.get("query", None) is not None:
            qs["q"] = what

        if qs.get("location", None) is not None:
            qs["l"] = where

        new_qs = {
            key: val[0] if isinstance(val, list) else val for key, val in qs.items()
        }
        new_qs = urlencode(new_qs)
        parsed_url[4] = new_qs
        new_url = urlunparse(parsed_url)

        return driver.get(new_url)

    return switch_to


def handle_step(driver: webdriver.Chrome, step_map, step):
    try:
        handler, *args = step_map[step]
        return handler(driver, *args)

    except KeyError:
        logger.error("Can't handle current step. No sufficient info. Skipping.")
        raise MissingInfoError()


def get_by_many_possible_locators(driver, locators):
    for locator in locators:
        elements = driver.find_elements(*locator)

        if elements:
            return elements


def close_all_but_first(driver):
    first_handle = driver.window_handles[0]

    for handle in driver.window_handles:
        if handle != first_handle:
            switch_to_tab(driver, handle)
            driver.close()


async def resolve_func(func):
    if iscoroutinefunction(func):
        code = await func()
    else:
        code = func()

    return code


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
