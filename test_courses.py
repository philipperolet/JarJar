#!/usr/bin/env python
# coding: utf-8

from fais_mes_courses import MonopBot, InvalidDeliveryDate
from selenium.common.exceptions import NoSuchElementException
from unittest import TestCase
from datetime import datetime, timedelta
from mock import Mock, patch


class MonopBotTest(TestCase):

    @patch('fais_mes_courses.WebDriverWait')
    def setUp(self, mockWDW):
        self.bot = MonopBot(Mock(), 1)

    def _setup_picking_slot_mocks(self):
        valid_mock = Mock()
        valid_mock.get_attribute.return_value = "libre"
        invalid_mock = Mock()
        invalid_mock.get_attribute.return_value = "nondispo"

        self.table_cells = {"h3 j1": invalid_mock,
                            "h3 j2": valid_mock,
                            "h5 j3": invalid_mock,
                            "h6 j3": valid_mock,
                            "h8 j3": invalid_mock}

        def finds_element_css(arg):
            if "headers" in arg:
                return self.table_cells[arg.split('"')[1]]
            return Mock()

        self.bot.driver.find_element_by_css_selector = Mock(side_effect=finds_element_css)

    @patch('fais_mes_courses.WebDriverWait')
    def test_picking_delivery_slots(self, mockWDW):
        self._setup_picking_slot_mocks()

        # date should be after day n+1 at noon
        with self.assertRaises(InvalidDeliveryDate):
            self.bot.set_delivery_time((datetime.now() + timedelta(1)).replace(hour=9))

        # date should be before "in 6 days"
        with self.assertRaises(InvalidDeliveryDate):
            self.bot.set_delivery_time(datetime.now() + timedelta(days=6))

        # date should be between 7 and 21
        with self.assertRaises(InvalidDeliveryDate):
            self.bot.set_delivery_time((datetime.now() + timedelta(days=2)).replace(hour=6))
        with self.assertRaises(InvalidDeliveryDate):
            self.bot.set_delivery_time((datetime.now() + timedelta(days=2)).replace(hour=22))

        # A few available and unavailable dates with special attention to the "12h30"
        # slot of monoprix messing things up
        self.bot.set_delivery_time(
            (datetime.now() + timedelta(days=2)).replace(hour=9))
        with self.assertRaises(InvalidDeliveryDate):
            self.bot.set_delivery_time(
                (datetime.now() + timedelta(days=3)).replace(hour=11))
        self.bot.set_delivery_time(
            (datetime.now() + timedelta(days=3)).replace(hour=12))
        with self.assertRaises(InvalidDeliveryDate):
            self.bot.set_delivery_time(
                (datetime.now() + timedelta(days=3)).replace(hour=13))

    @patch('fais_mes_courses.logging')
    def test_emptying_basket_already_empty(self, log_mock):
        self.bot.driver.find_element_by_css_selector.return_value.text = "0"
        self.bot.empty_basket()
        log_mock.info.assert_called_once_with("Emptying basket: already empty.")

    @patch('fais_mes_courses.logging')
    def test_emptying_basket_5_elements(self, log_mock):
        # Prepare mock for 5 calls of emptying basket before exception
        self.counter = 0

        def find_by_css_returns(selector):
            self.counter += 1
            basket_pastille = Mock()
            basket_pastille.text = "5"
            if self.counter == 1:
                return basket_pastille
            if self.counter <= 6:
                return Mock()
            raise NoSuchElementException()

        self.bot.driver.find_element_by_css_selector.side_effect = find_by_css_returns

        # expects correct calls to find_element_by_css_selector : 4 initials + 6 for basket removal
        self.bot.empty_basket()
        self.assertEqual(10, len(self.bot.driver.find_element_by_css_selector.call_args_list))
        log_mock.info.assert_called_once_with("Emptied basket: 5 elements")
