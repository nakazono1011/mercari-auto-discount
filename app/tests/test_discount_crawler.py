import unittest
from unittest.mock import Mock, patch

from selenium.webdriver.common.by import By

from crawler.mercari.discount_crawler import (
    DiscountCrawler,
    item_url_to_edit_url,
    parse_price,
)


class ItemUrlToEditUrlTest(unittest.TestCase):
    def test_converts_item_url_to_sell_edit_url(self):
        self.assertEqual(
            item_url_to_edit_url("https://jp.mercari.com/item/m96706433110"),
            "https://jp.mercari.com/sell/edit/m96706433110",
        )

    def test_returns_none_when_item_id_is_missing(self):
        self.assertIsNone(item_url_to_edit_url("https://jp.mercari.com/mypage/listings"))


class QuitDriverTest(unittest.TestCase):
    def test_quit_driver_does_nothing_when_driver_is_none(self):
        crawler = DiscountCrawler()
        crawler.driver = None
        crawler._quit_driver()
        self.assertIsNone(crawler.driver)

    def test_quit_driver_closes_and_clears_driver(self):
        crawler = DiscountCrawler()
        driver = Mock()
        crawler.driver = driver
        crawler._quit_driver()
        driver.quit.assert_called_once()
        self.assertIsNone(crawler.driver)

    def test_quit_driver_clears_driver_even_if_quit_raises(self):
        crawler = DiscountCrawler()
        driver = Mock()
        driver.quit.side_effect = Exception("no such window")
        crawler.driver = driver
        crawler._quit_driver()
        self.assertIsNone(crawler.driver)


class FakePriceInput:
    """全選択→削除→入力を再現する。drop_first_digits 回は先頭の1桁を取りこぼす。"""

    def __init__(self, value, drop_first_digits=0):
        self.value = value
        self.drop = drop_first_digits
        self.clears = 0

    def get_attribute(self, name):
        return self.value

    def click(self):
        pass

    def send_keys(self, *keys):
        from selenium.webdriver.common.keys import Keys

        for k in keys:
            if k == Keys.BACK_SPACE:
                self.value = ""
                self.clears += 1
            elif k == Keys.COMMAND + "a":
                pass
            else:
                text = str(k)
                if self.drop > 0:
                    self.drop -= 1
                    text = text[1:]
                self.value += text


class ParsePriceTest(unittest.TestCase):
    def test_strips_commas_and_yen(self):
        self.assertEqual(parse_price("3,444"), 3444)
        self.assertEqual(parse_price("¥3,444"), 3444)

    def test_returns_none_for_blank(self):
        self.assertIsNone(parse_price(""))
        self.assertIsNone(parse_price(None))


@patch("crawler.mercari.discount_crawler.time.sleep", return_value=None)
class SetPriceTest(unittest.TestCase):
    def test_retries_when_first_digit_is_dropped(self, _sleep):
        crawler = DiscountCrawler()
        el = FakePriceInput("3,444", drop_first_digits=1)
        crawler._set_price(el, 3333)
        self.assertEqual(parse_price(el.value), 3333)

    def test_raises_when_value_never_matches(self, _sleep):
        crawler = DiscountCrawler()
        el = FakePriceInput("3,444", drop_first_digits=99)
        with self.assertRaisesRegex(Exception, "価格を正しく入力できませんでした"):
            crawler._set_price(el, 3333)
        self.assertEqual(el.clears, 3)


class UpdateAllPriceGuardTest(unittest.TestCase):
    @patch("crawler.mercari.discount_crawler.time.sleep", return_value=None)
    def test_does_not_save_when_price_is_wrong(self, _sleep):
        crawler = DiscountCrawler()
        driver = Mock()
        name_el = Mock()
        name_el.get_attribute.return_value = "靴"
        price_el = FakePriceInput("3,444", drop_first_digits=99)
        edit_button = Mock()

        def find_element(by, value):
            if by == By.NAME and value == "name":
                return name_el
            if "price" in value:
                return price_el
            if "edit-button" in value:
                return edit_button
            raise AssertionError((by, value))

        driver.find_element.side_effect = find_element
        crawler.driver = driver
        crawler._confirm_image_creation_if_needed = Mock()
        crawler._safe_click = Mock()

        crawler._update_all(["https://jp.mercari.com/item/m1"])

        crawler._safe_click.assert_not_called()


class UpdateAllDriverReuseTest(unittest.TestCase):
    @patch("crawler.mercari.discount_crawler.time.sleep", return_value=None)
    def test_restarts_driver_when_window_is_closed(self, _sleep):
        crawler = DiscountCrawler()
        driver = Mock()
        driver.find_element.side_effect = Exception(
            "no such window: target window already closed"
        )
        crawler.driver = driver
        crawler._quit_driver = Mock(wraps=crawler._quit_driver)

        crawler._update_all(["https://jp.mercari.com/item/m1"])

        crawler._quit_driver.assert_called_once()
        self.assertIsNone(crawler.driver)

    @patch("crawler.mercari.discount_crawler.time.sleep", return_value=None)
    def test_does_not_quit_driver_after_item_error(self, _sleep):
        crawler = DiscountCrawler()
        driver = Mock()
        driver.find_element.side_effect = Exception("no such element")
        crawler.driver = driver

        crawler._update_all(["https://jp.mercari.com/item/m1"])

        driver.quit.assert_not_called()
        self.assertIs(crawler.driver, driver)

    @patch("crawler.mercari.discount_crawler.time.sleep", return_value=None)
    def test_does_not_quit_driver_after_successful_item(self, _sleep):
        crawler = DiscountCrawler()
        driver = Mock()
        name_el = Mock()
        name_el.get_attribute.return_value = "靴"
        price_el = FakePriceInput("2000")
        edit_button = Mock()

        def find_element(by, value):
            if by == By.NAME and value == "name":
                return name_el
            if by == By.CSS_SELECTOR and "price" in value:
                return price_el
            if by == By.CSS_SELECTOR and "edit-button" in value:
                return edit_button
            raise AssertionError((by, value))

        driver.find_element.side_effect = find_element
        crawler.driver = driver
        crawler._confirm_image_creation_if_needed = Mock()
        crawler._safe_click = Mock()

        crawler._update_all(["https://jp.mercari.com/item/m1"])

        driver.get.assert_called_once_with("https://jp.mercari.com/sell/edit/m1")
        driver.quit.assert_not_called()
        self.assertIs(crawler.driver, driver)
        self.assertEqual(price_el.value, "1889")
        crawler._safe_click.assert_called_with(edit_button)
