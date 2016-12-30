#!/usr/bin/env python
# coding: utf-8

from fais_mes_courses import MonopBot
from unittest import TestCase
from datetime import datetime, timedelta
from mock import Mock, patch


class MonopBotTest(TestCase):

    @patch('fais_mes_courses.WebDriverWait')
    def setUp(self, mockWDW):
        self.bot = MonopBot(Mock())

    def test_date_validity(self):
        # date should be after day n+1 at noon
        self.assertFalse(
            self.bot.valid_delivery_date((datetime.now() + timedelta(1)).replace(hour=9)))

        # date should be before "in 6 days"
        self.assertFalse(
            self.bot.valid_delivery_date(datetime.now() + timedelta(days=6)))

        # date should be between 7 and 21
        self.assertFalse(
            self.bot.valid_delivery_date(
                (datetime.now() + timedelta(days=2)).replace(hour=6)))

        # date should be between 7 and 21
        self.assertFalse(
            self.bot.valid_delivery_date(
                (datetime.now() + timedelta(days=2)).replace(hour=22)))

        valid_date = (datetime.now() + timedelta(days=2)).replace(hour=9)
        self.assertTrue(self.bot.valid_delivery_date(valid_date))

    def test_date_availability(self):
        valid_mock = Mock()
        valid_mock.get_attribute.return_value = "libre"
        invalid_mock = Mock()
        invalid_mock.get_attribute.return_value = "nondispo"

        table_cells = {"h3 j2": valid_mock,
                       "h5 j3": invalid_mock,
                       "h6 j3": valid_mock,
                       "h8 j3": invalid_mock}

        def finds_element_css(arg):
            return table_cells[arg.split('"')[1]]

        self.bot.driver.find_element_by_css_selector = Mock(side_effect=finds_element_css)
        # Tests a few dates, mock configured to accept / refuse
        self.assertTrue(self.bot.available_delivery_date(
            (datetime.now() + timedelta(days=2)).replace(hour=9)))
        # Here special attention to the "12h30" slot of monoprix messing things up
        self.assertFalse(self.bot.available_delivery_date(
            (datetime.now() + timedelta(days=3)).replace(hour=11)))
        self.assertTrue(self.bot.available_delivery_date(
            (datetime.now() + timedelta(days=3)).replace(hour=12)))
        self.assertFalse(self.bot.available_delivery_date(
            (datetime.now() + timedelta(days=3)).replace(hour=13)))
