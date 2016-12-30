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

        # Tests two dates, mock configured to accept one and refuse the other
        self.assertTrue(self.bot.available_delivery_date(
            (datetime.now() + timedelta(days=2)).replace(hour=9)))
        self.assertFalse(self.bot.available_delivery_date(
            (datetime.now() + timedelta(days=3)).replace(hour=11)))
