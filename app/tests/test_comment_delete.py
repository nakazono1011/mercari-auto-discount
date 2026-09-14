import unittest
from unittest.mock import Mock

from crawler.mercari.weekly_comment_delete_crawler import (
    pick_confirm_delete_button,
    pick_visible_confirm_delete_button,
)


class PickConfirmDeleteButtonTest(unittest.TestCase):
    def test_picks_button_whose_label_is_inside_a_span(self):
        cancel = Mock(text="キャンセル")
        confirm = Mock(text="削除する")
        self.assertIs(pick_confirm_delete_button([cancel, confirm]), confirm)

    def test_returns_none_when_confirm_button_is_missing(self):
        self.assertIsNone(pick_confirm_delete_button([Mock(text="キャンセル")]))


class PickVisibleConfirmDeleteButtonTest(unittest.TestCase):
    def test_ignores_hidden_empty_dialog(self):
        hidden = Mock()
        hidden.is_displayed.return_value = False
        hidden.find_elements.return_value = []
        visible = Mock()
        visible.is_displayed.return_value = True
        confirm = Mock(text="削除する")
        visible.find_elements.return_value = [Mock(text="キャンセル"), confirm]
        self.assertIs(
            pick_visible_confirm_delete_button([hidden, visible]),
            confirm,
        )

    def test_returns_none_when_dialog_is_not_open(self):
        hidden = Mock()
        hidden.is_displayed.return_value = False
        hidden.find_elements.return_value = []
        self.assertIsNone(pick_visible_confirm_delete_button([hidden]))
