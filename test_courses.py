#!/usr/bin/env python
# coding: utf-8

from fais_mes_courses import MonopBot, InvalidDeliveryDate
from unittest import TestCase
from datetime import datetime, timedelta


class MonopBotTest(TestCase):

    def setUp(self):
        self.bot = MonopBot()

    def test_date_validity(self):
        # date should be after day n+1 at noon
        tomorrow_nine = datetime.now() + timedelta(1)
        tomorrow_nine.hour = 9
        with self.assertRaises(InvalidDeliveryDate):
            self.bot.set_delivery_date(tomorrow_nine)

