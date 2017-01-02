#!/usr/bin/env python
# coding: utf-8
import logging
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException,
                                        NoSuchElementException,
                                        ElementNotVisibleException,
                                        StaleElementReferenceException)

from datetime import datetime, timedelta


class InvalidDeliveryDate(Exception):
    pass


class MonopBot(object):
    """
    Bot class that can perform various actions as a
    logged visitor of monoprix.fr
    - driver : selenium webdriver to use for browser emulation
    (chrome, headless predefined above)
    """
    username = 'philipperolet@gmail.com'
    password = 'stuff6472!'

    def __init__(self, driver, page_load_wait_time=6):
        logging.info("Starting MonopBot")
        self.driver = driver
        # to avoid elements not found because not yet loaded, wait for some time before timing out
        self.driver.implicitly_wait(page_load_wait_time)
        self.page_load_wait_time = page_load_wait_time

        # Sign in on monoprix.fr
        self.driver.get("http://www.monoprix.fr")
        logging.info("Reached monoprix.fr")
        self.signin(self.username, self.password)

    def signin(self, username, password):
        # Gets to signin form
        monCompte = self.driver.find_element_by_css_selector(".dropdown.compte")
        monCompte.click()

        # enters signin / pass and logs in
        login_field = self.driver.find_element_by_id("emailPopin")
        try:
            WebDriverWait(self.driver, self.page_load_wait_time).until(
                EC.visibility_of(login_field))
        except TimeoutException:
            raise RuntimeError("Could not log in")
        login_field.click()
        login_field.send_keys(username)
        pass_field = self.driver.find_element_by_id("mdpPopin")
        pass_field.send_keys(password)
        self.driver.find_element_by_css_selector('#loginForm .modal-action button').click()

        # Checks element below is found to confirm logging in
        self.driver.find_element_by_css_selector(
            'li.dropdown.connect ul.dropdown-menu.compte'
        )

        # Optional popup about missing items for next delivery : discarded
        try:
            self.driver.find_element_by_id("valider_items_out_of_stock").click()
        except ElementNotVisibleException:
            pass

        logging.info("Logged in.")

    def get_last_order_amount(self):
        self.driver.get('https://www.monoprix.fr/jsp/account/accountOrders.jsp')
        return self.driver.find_element_by_css_selector(
            "table.commandes-related tbody tr:first-child td:first-child+td+td+td"
        ).text

    def _get_slot_cell(self, delivery_time):
        '''Finds the "delivery_time coordinates" according to monoprix table and
        returns the table cell
        '''
        # Date should be between day n+1 at noon and day n+5 included, and between 7h and 21h
        delta = delivery_time - datetime.now().replace(hour=0, minute=0, second=0)
        if (delta.days < 0 or delta.days > 5 or
                delta.seconds < 7 * 3600 or delta.seconds >= 22 * 3600):
            raise InvalidDeliveryDate("Date not available for delivery")

        # two "weird slots" of monoprix, 7h15 and 12h30, are skipped thus the hour adjustment
        hour = delivery_time.hour-7
        if hour > 0:
            hour += 1
        if hour > 6:
            hour += 1
        coords = "h{} j{}".format(hour, delta.days)

        # finds the cell and returns it if the slot is available
        table_cell = self.driver.find_element_by_css_selector(
            'table td[headers="{}"]'.format(coords)
        )  # availability given by the css class of the cell with the delivery_time coordinates
        if not("libre" in table_cell.get_attribute("class")):
            raise InvalidDeliveryDate("Date not available for delivery")
        return table_cell

    def set_delivery_time(self, delivery_time):
        '''Sets the delivery_time and time for groceries delivery.
        Raises InvalidDeliveryDate if the chosen datetime does not work
        '''
        # Goes to delivery slot selection form
        self.driver.get("https://www.monoprix.fr/courses-en-ligne")
        self.driver.find_element_by_css_selector('.mea-Livraison #collapseOne a').click()

        slot_cell = self._get_slot_cell(delivery_time)

        # validates the slot. In some cases a confirmation is asked because some items
        # may not be available. When it happens, the bot confirms
        slot_cell.click()
        ok_button = self.driver.find_element_by_css_selector('.popin-livraison .validate button')
        self.driver.execute_script("arguments[0].scrollIntoView();", ok_button)
        ok_button.click()
        try:
            confirmation_button = self.driver.find_element_by_css_selector(
                '#information-change-slot-different-store div > a+a.button'
            )  # This only appears when a confirmation is needed
            WebDriverWait(self.driver, self.page_load_wait_time).until(
                EC.visibility_of(confirmation_button))
        except TimeoutException:
            pass  # we just go on if no confirmation is needed
        self.delivery_time = delivery_time
        logging.info("Delivery set for {:%b %d} at {:%H}h.".format(delivery_time, delivery_time))

    def add_previous_order_to_basket(self, order_nb):
        '''
        adds all items of order #order_nb to basket
        except those unavailable
        returns a list of unavaible items (string)
        order_nb is such that 1 is the most recent order
        '''
        self.driver.get("https://www.monoprix.fr/jsp/account/accountOrders.jsp")
        self.driver.find_element_by_css_selector(
            "table.commandes-related tbody tr:nth-child({}) td:last-child".format(order_nb)
        ).click()
        self.driver.find_element_by_css_selector(
            "div.panier button.ajout-list-panier"
        ).click()
        logging.info("Added last order num. {} to basket".format(order_nb))
        return self._get_missing_elements()

    def _get_missing_elements(self):
        return ""

    def empty_basket(self):
        # Checks if basket is not already empty
        basket_size = self.driver.find_element_by_css_selector(".monpanier .pastille-nb-art").text
        if basket_size == "0":
            logging.info("Emptying basket: already empty.")
            return

        # Goes to basket view and remove items one by one
        self.driver.get("https://www.monoprix.fr/apercu-panier")
        try:
            while True:
                time.sleep(0.3)  # waits to avoid stalereferences due to JS refresh
                del_first_item_button = self.driver.find_element_by_css_selector(
                    ".cadre-detail-panier div.dyn-supp button")
                self.driver.execute_script(del_first_item_button.get_attribute("onclick"))
        except NoSuchElementException:
            logging.info("Emptied basket: {} elements".format(basket_size))
        except StaleElementReferenceException:
            # In case there is still a staleness (not waited enough), retries
            self.empty_basket()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    bot = MonopBot(webdriver.Chrome())
    bot.set_delivery_time(datetime.now().replace(hour=9) + timedelta(days=2))
    bot.empty_basket()
    missing_elements = [bot.add_previous_order_to_basket(i) for i in range(1, 3)]
    """
    bot.empty_basket()
    [bot.add_full_order_to_basket(i+1) for i in range(4)]
    driver.quit()
    """
#    bot = MonopBot(webdriver.Remote("http://127.0.0.1:9515",
#                                    webdriver.DesiredCapabilities.CHROME)
#    print u'Montant dernière commande : {}'.format(unicode(bot.get_last_order_amount()))
