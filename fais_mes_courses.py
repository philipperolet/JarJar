#!/usr/bin/env python
# coding: utf-8
import logging

from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from datetime import datetime, timedelta

LOAD_WT = 10  # Waiting time for elements to load / show (secs)


class InvalidDeliveryDate(Exception):
    pass


class MonopBot(object):
    """
    Bot class that can perform various actions as a
    logged visitor of monoprix.fr
    - driver : selenium webdriver to use for browser emulation
    (chrome, headless predefined above)
    """
    login = 'philipperolet@gmail.com'
    password = 'stuff6472!'
    
    def __init__(self, driver):
        logging.info("Starting MonopBot")
        self.driver = driver
        # to avoid elements not found because not yet loaded, wait for some time before timing out
        self.driver.implicitly_wait(LOAD_WT)

        # Go to monoprix
        self.driver.get("http://www.monoprix.fr")
        logging.info("Reached monoprix.fr")
        self.login(self.login, self.password)

    def login(self, login, password):
        # Gets to login form
        monCompte = self.driver.find_element_by_css_selector(".dropdown.compte")
        monCompte.click()

        # enters login / pass and logs in
        login_field = self.driver.find_element_by_id("emailPopin")
        try:
            WebDriverWait(self.driver, LOAD_WT).until(EC.visibility_of(login_field))
        except TimeoutException:
            self.driver.quit()
            raise RuntimeError("Could not log in")
        login_field.click()
        login_field.send_keys(login)
        pass_field = self.driver.find_element_by_id("mdpPopin")
        pass_field.send_keys(password)
        self.driver.find_element_by_css_selector('#loginForm .modal-action button').click()

        # Checks element below is found to confirm logging in
        self.driver.find_element_by_css_selector(
            'li.dropdown.connect ul.dropdown-menu.compte'
        )
        logging.info("Logged in.")

    def get_last_order_amount(self):
        self.driver.get('https://www.monoprix.fr/jsp/account/accountOrders.jsp')
        return self.driver.find_element_by_css_selector(
            "table.commandes-related tbody tr:first-child td:first-child+td+td+td"
        ).text

    def empty_basket(self):
        raise NotImplementedError

    def add_full_order_to_basket(self, order_nb):
        '''
        adds all items of order #order_nb to basket
        except those unavailable
        order_nb is such that 1 is the most recent order
        '''
        raise NotImplementedError

    def set_delivery_date(self, date):
        if not(self.available_delivery_date(date)):
            raise InvalidDeliveryDate("Date not available for delivery")
        self.select_date(date)

    @staticmethod
    def valid_delivery_date(date):
        """
        Date should be:
        - between day n+1 at noon and day n+5 included
        - between 7 and 21
        """
        today = datetime.now().replace(hour=7, minute=0, second=0)
        if (date.hour < 7) or (date.hour > 21):
            return False
        if (date - today) > timedelta(days=5):
            return False
        if (date - today) < timedelta(days=1, hours=5):
            return False
        return True

    def available_delivery_date(self, date):
        """
        Checks if monoprix is able to deliver at the given date
        """
        # Only certain dates can be considered
        if not(self.valid_delivery_date(date)):
            return False

        # Get the "date coordinates" according to monoprix table
        # two "weird slots" of monoprix, 7h15 and 12h30, are skipped
        # thus the hour adjustment
        delta = date - datetime.now().replace(hour=0)
        hour = date.hour-7
        if hour > 0:
            hour += 1
        if hour > 6:
            hour += 1
        coords = "h{} j{}".format(hour, delta.days)

        # availability is given by the css class of the table cell
        table_cell = self.driver.find_element_by_css_selector(
            'table td[headers="{}"]'.format(coords)
        )
        return "libre" in table_cell.get_attribute("class")

if __name__ == '__main__':
    headless_driver = webdriver.Remote("http://127.0.0.1:9515",
                                       webdriver.DesiredCapabilities.CHROME)
    logging.getLogger().setLevel(logging.INFO)
    # bot = MonopBot(headless_driver)
    bot = MonopBot(webdriver.Chrome())
    print u'Montant dernière commande : {}'.format(unicode(bot.get_last_order_amount()))
    """
    bot.empty_basket()
    [bot.add_full_order_to_basket(i+1) for i in range(4)]
    driver.quit()
    """
