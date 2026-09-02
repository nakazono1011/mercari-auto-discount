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
        出品ページの「もっと見る」ボタンが非表示になるまで再帰的に押し続ける処理
        """
        LOAD_BUTTON_XPATH = "//button[descendant::*[contains(text(), 'もっと見る')]]"

        if not self.driver.find_elements(By.XPATH, LOAD_BUTTON_XPATH):
            logger.error("[エラー] もっと見るボタンが見つかりませんでした")
            return

        load_more_button = self.driver.find_element(By.XPATH, LOAD_BUTTON_XPATH)
        time.sleep(1)
        self._safe_click(load_more_button)

        ## 1~4秒間でランダムに待機
        time.sleep(random.randint(1, 4))

        ## ロードボタンが無くなるまで再帰的に処理する
        logger.info("[イベント] もっと見る押下")
        self._load_more()

        pass

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
        locators = [
            (By.CSS_SELECTOR, '[data-testid="listing-alert-consent"]'),
            (
                By.XPATH,
                "//input[@type='checkbox'][following-sibling::*[contains(., '画像は自分で撮影・作成しました')]]",
            ),
            (
                By.XPATH,
                "//label[contains(., '画像は自分で撮影・作成しました')]/input[@type='checkbox']",
            ),
        ]

        for by, value in locators:
            checkboxes = self._find_optional_elements(by, value)
            if not checkboxes:
                continue

            checkbox = checkboxes[0]
            if checkbox.is_selected():
                logger.info("[イベント] 画像著作権確認チェックボックスは既にチェック済み")
                return

            self._safe_click(checkbox)
            time.sleep(0.3)
            logger.info("[イベント] 画像著作権確認チェックボックスをチェック")
            return

    @abstractclassmethod
    def crawl(self):
        raise NotImplementedError("実装されていません")
