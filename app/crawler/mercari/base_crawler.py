import time
import random
from abc import ABCMeta, abstractclassmethod

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import service as fs

import config
from logger import get_module_logger

logger = get_module_logger(__name__)


class BaseCrawler(metaclass=ABCMeta):
    def __init__(self):
        pass

    def _load_driver(
        self, driver_path=config.DRIVER_PATH, profile_path=config.PROFILE_PATH
    ):
        """
        driver の起動
        """
        options = webdriver.chrome.options.Options()
        options.add_argument("--user-data-dir=" + profile_path)

        chrome_service = fs.Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=chrome_service, options=options)
        driver.implicitly_wait(15)

        return driver

    def _load_more(self):
        """
        出品ページの「もっと見る」ボタンが非表示になるまで再帰的に押し続ける処理
        """
        LOAD_BUTTON_XPATH = "//*[@id='currentListing']//*[contains(text(), 'もっと見る')]"

        if not self.driver.find_elements(By.XPATH, LOAD_BUTTON_XPATH):
            logger.error("[エラー] もっと見るボタンが見つかりませんでした")
            return

        load_more_button = self.driver.find_element(
            By.XPATH, LOAD_BUTTON_XPATH
        )
        load_more_button.click()

        ## 1~4秒間でランダムに待機
        time.sleep(random.randint(1, 4))

        ## ロードボタンが無くなるまで再帰的に処理する
        logger.info("[イベント] もっと見る押下")
        self._load_more()

        pass

    @abstractclassmethod
    def crawl(self):
        raise NotImplementedError("実装されていません")
