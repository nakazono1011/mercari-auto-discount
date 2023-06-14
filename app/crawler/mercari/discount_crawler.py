import re
import time
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from crawler.mercari import BaseCrawler
from logger import get_module_logger

logger = get_module_logger(__name__)


class DiscountCrawler(BaseCrawler):
    START_URL = "https://jp.mercari.com/mypage/listings"

    def _scrape_target_urls(self):
        """
        値引き対象のURLを生成する
        """

        # 商品リストの要素を取得
        listed_item_element = self.driver.find_element(
            By.CSS_SELECTOR, "[data-testid='listed-item-list']"
        )
        item_list = listed_item_element.find_elements(By.CSS_SELECTOR, "[data-testid='merListItem-container']")

        # 要素内の値引き対象のURLを取得
        item_urls = []
        for el in item_list:
            item_root = el.find_element(By.TAG_NAME, "mer-item-object").shadow_root
            if self._is_skip(item_root):
                continue

            item_url = el.find_element(By.TAG_NAME, "a").get_attribute("href")
            item_urls.append(item_url)

        return item_urls

    def _is_skip(self, el):
        """
        スキップ対象の判定
        """
        pre_update_time_text = el.find_elements(By.CLASS_NAME, "icon-text")[-1].text
        title = el.find_element(By.CLASS_NAME, "item-label").text

        is_before_day = bool(re.search("(分前)|(時間前)", pre_update_time_text))
        is_contain_star = bool(re.search("★", title))

        is_target = is_before_day | is_contain_star

        logger.info(
            f"[タイトル]{title} [前回更新時刻]：{pre_update_time_text} [値引き対象Flg]：{not is_target}"
        )

        return is_target

    def _update_all(self, target_urls):
        """
        対象の商品について値下げを実行する処理
        """
        for target_url in target_urls:
            try:
                self.driver.get(target_url)
                time.sleep(random.randint(1, 2))

                edit_url = self.driver.find_element(
                    By.CSS_SELECTOR, "[data-testid='checkout-button']>a"
                ).get_attribute("href")

                self.driver.get(edit_url)
                time.sleep(random.randint(1, 2))

                item_name = self.driver.find_element(By.NAME, "name").get_attribute(
                    "value"
                )

                price_input_element = self.driver.find_element(
                     By.CSS_SELECTOR,
                    'input[name="price"]',
                )
                current_price = int(price_input_element.get_attribute("value"))
                updated_price = self._discount(current_price)

                price_input_element.click()
                price_input_element.send_keys(Keys.COMMAND + 'a')
                price_input_element.send_keys(Keys.BACK_SPACE)
                price_input_element.send_keys(updated_price)

                time.sleep(0.5)

                edit_button = self.driver.find_element(
                    By.CSS_SELECTOR, '[data-testid="edit-button"]'
                )
                edit_button.click()

                logger.info(
                    f"[イベント] 価格更新 [商品名] {item_name} [更新前価格] {current_price} [更新後] {updated_price} [URL] {self.driver.current_url}"
                )
            except Exception as e:
                logger.info(f"[商品名] {item_name} [例外エラー] {e}")
                continue

    def _discount(self, price):
        """
        値下げ処理
        """
        if price <= 1000:
            raise Exception(f"1000円以下になるので値下げできません")

        # 下3桁が111円の場合は、値引き後に千の位が1桁下がるように、111円引き
        if str(price)[-3::] == "111":
            updated_price = price - 112
        else:
            updated_price = price - 111

        return updated_price

    def crawl(self):
        """
        メイン処理
        """

        logger.info(f"[イベント] 処理開始")
        self.driver = self._load_driver()
        self.driver.get(self.START_URL)

        # 出品リストをロード
        self._load_more()

        # 値下げ対象の出品リストを取得
        target_urls = self._scrape_target_urls()

        # 値下げ処理
        self._update_all(target_urls)
        logger.info(f"[更新件数] {len(target_urls)}件")

        self.driver.quit()
        logger.info(f"[イベント] 処理完了")
