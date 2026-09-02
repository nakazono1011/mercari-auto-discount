import time
import random

from selenium.webdriver.common.by import By

from crawler.mercari import BaseCrawler
from logger import get_module_logger

logger = get_module_logger(__name__)


class WeeklyCommentDeleteCrawler(BaseCrawler):
    START_URL = "https://jp.mercari.com/mypage/listings"
    # 最低いいね数
    MIN_LIKE_COUNT = 2
    # 最低コメント数
    MIN_COMMENT_COUNT = 1
    # 削除対象の判定文字列
    DELETE_TARGET_CHARCTER = "★"

    def _delete_comment_all(self, target_urls):
        for target_url in target_urls:
            item_name = ""
            try:
                self.driver.get(target_url)

                time.sleep(random.randint(1, 4))

                item_name = self.driver.find_element(
                    By.CSS_SELECTOR, 'div[data-testid="name"]'
                ).text

                load_more_comments = []
                deadline = time.time() + 2
                while True:
                    load_more_comments = self._find_optional_elements(
                        By.XPATH, "//button[contains(text(), 'コメントをもっと見る')]"
                    )
                    if load_more_comments:
                        self._safe_click(load_more_comments[0])
                        break
                    if time.time() >= deadline:
                        break
                    time.sleep(0.2)

                comment_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, "[data-testid='comment-list']>div"
                )

                for comment_element in comment_elements:
                    if (
                        self.DELETE_TARGET_CHARCTER
                        in comment_element.find_element(
                            By.CSS_SELECTOR, "[data-testid='message-body']"
                        ).text
                    ):
                        delete_icon = comment_element.find_element(
                            By.XPATH,
                            ".//span[normalize-space()='削除する']/following-sibling::button[@type='button']",
                        )
                        self._safe_click(delete_icon)

                        delete_button_element = self.driver.find_element(
                            By.XPATH, "//button[contains(text(), '削除する')]"
                        )
                        self._safe_click(delete_button_element)

                        time.sleep(3)

                logger.info(
                    f"[商品名] {item_name} [イベント] 週末セールコメント削除完了"
                )

            except Exception as e:
                logger.error(f"[商品名] {item_name} [例外エラー] {e}")
                continue

    def _scrape_target_urls(self):
        """
        コメント対象のURLを生成する
        """

        # 商品リストの要素を取得
        listed_item_element = self.driver.find_element(
            By.CSS_SELECTOR, "[data-testid='listed-item-list']"
        )
        item_list = listed_item_element.find_elements(
            By.CSS_SELECTOR, "[data-testid='listed-item']"
        )

        # 要素内のコメント対象のURLを取得
        item_urls = []
        for el in item_list:
            like_count = int(
                (
                    el.find_elements(By.TAG_NAME, "svg")[0]
                    .find_element(By.XPATH, "./parent::*")
                    .text
                )
            )
            comment_count = int(
                (
                    el.find_elements(By.TAG_NAME, "svg")[1]
                    .find_element(By.XPATH, "./parent::*")
                    .text
                )
            )

            if (
                like_count >= self.MIN_LIKE_COUNT
                and comment_count >= self.MIN_COMMENT_COUNT
            ):
                item_url = self._get_listed_item_url(el)
                if not item_url:
                    logger.warning("[スキップ] 商品URLを取得できませんでした")
                    continue
                item_urls.append(item_url)

        return item_urls

    def crawl(self):
        """
        メイン処理
        """
        logger.info(f"[イベント] 処理開始")
        self.driver = self._load_driver()
        self.driver.get(self.START_URL)

        time.sleep(5)

        # 出品リストをロード
        self._load_more()

        # 週末コメント削除対象のURLを取得
        target_urls = self._scrape_target_urls()

        # コメント削除処理
        self._delete_comment_all(target_urls)
        logger.info(f"[削除件数] {len(target_urls)}件")

        self.driver.quit()
        logger.info(f"[イベント] 処理完了")
