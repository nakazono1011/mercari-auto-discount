import os
import time
import random
from abc import ABCMeta, abstractclassmethod

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By

import config
from logger import get_module_logger

logger = get_module_logger(__name__)

_IMPLICIT_WAIT_SECONDS = 15


class BaseCrawler(metaclass=ABCMeta):
    def __init__(self):
        pass

    def _load_driver(self, profile_path=config.PROFILE_PATH):
        """
        driver の起動
        """
        options = webdriver.chrome.options.Options()
        options.add_argument("--user-data-dir=" + profile_path)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")

        # Homebrew 等の PATH 上 chromedriver が Chrome とズレていても、
        # Selenium Manager が合うバージョンを取るようにする
        os.environ["SE_SKIP_DRIVER_IN_PATH"] = "true"
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(_IMPLICIT_WAIT_SECONDS)

        return driver

    def _find_optional_elements(self, by, value):
        """存在しないことが多い要素は implicit wait せずに探す。"""
        self.driver.implicitly_wait(0)
        try:
            return self.driver.find_elements(by, value)
        finally:
            self.driver.implicitly_wait(_IMPLICIT_WAIT_SECONDS)

    def _quit_driver(self):
        """driver が無い・既に閉じている場合でも落とさずに終了する。"""
        driver = getattr(self, "driver", None)
        if driver is None:
            return
        try:
            driver.quit()
        except Exception:
            pass
        self.driver = None

    def _safe_click(self, element):
        """固定ヘッダーに隠れないよう中央へスクロールしてからクリックする。"""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            element,
        )
        time.sleep(0.3)
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)

    def _load_more(self):
        """
        出品ページの「もっと見る」ボタンが非表示になるまで押し続ける処理
        """
        LOAD_BUTTON_XPATH = "//button[descendant::*[contains(text(), 'もっと見る')]]"
        first = True

        while True:
            if first:
                buttons = self.driver.find_elements(By.XPATH, LOAD_BUTTON_XPATH)
                first = False
            else:
                buttons = self._find_optional_elements(By.XPATH, LOAD_BUTTON_XPATH)

            if not buttons:
                logger.info("[イベント] 出品リストの読み込み完了")
                return

            time.sleep(1)
            self._safe_click(buttons[0])
            time.sleep(random.randint(1, 4))
            logger.info("[イベント] もっと見る押下")

    def _get_listed_item_url(self, el):
        """出品一覧の要素から商品URLを取得する。"""
        href = el.get_attribute("href")
        if href:
            return href

        links = el.find_elements(By.TAG_NAME, "a")
        if links:
            return links[0].get_attribute("href")

        return None

    def _confirm_image_creation_if_needed(self):
        """
        画像著作権確認チェックボックスが表示されている場合にチェックする。
        全商品に表示されるわけではないため、存在しない場合は何もしない。
        """
        checkboxes = self._find_optional_elements(
            By.CSS_SELECTOR, '[data-testid="listing-alert-consent"]'
        )
        if not checkboxes:
            return

        checkbox = checkboxes[0]
        if checkbox.is_selected():
            logger.info("[イベント] 画像著作権確認チェックボックスは既にチェック済み")
            return

        self._safe_click(checkbox)
        time.sleep(0.3)
        logger.info("[イベント] 画像著作権確認チェックボックスをチェック")

    @abstractclassmethod
    def crawl(self):
        raise NotImplementedError("実装されていません")
