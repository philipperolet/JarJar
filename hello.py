#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

LOAD_WT = 10  # Waiting time for elements to load / show (secs)
driver = webdriver.Chrome()


class MonopBot(object):
    """
    Bot class that can perform various actions as a
    visitor of monoprix.fr
    """
    def __init__(self):
        # to avoid elements not found because not yet loaded, wait for some time before timing out
        driver.implicitly_wait(LOAD_WT)
        driver.get("http://www.monoprix.fr")

    def login(self):
        monCompte = driver.find_element_by_css_selector(".dropdown.compte")
        monCompte.click()
        # enters login / pass and logs in
        login_field = driver.find_element_by_id("emailPopin")
        try:
            WebDriverWait(driver, LOAD_WT).until(EC.visibility_of(login_field))
        except TimeoutException:
            driver.quit()
            raise RuntimeError("Could not log in")
        login_field.click()
        login_field.send_keys('philipperolet@gmail.com')
        pass_field = driver.find_element_by_id("mdpPopin")
        pass_field.send_keys('stuff6472!')
        driver.find_element_by_css_selector('#loginForm .modal-action button').click()
        driver.find_element_by_css_selector(
            'li.dropdown.connect ul.dropdown-menu.compte'
        )  # Once found, it means we're logged in

    def get_last_order_amount(self):
        driver.get('https://www.monoprix.fr/jsp/account/accountOrders.jsp')
        return driver.find_element_by_css_selector(
            "table.commandes-related tbody tr:first-child td:first-child+td+td+td"
        ).text

bot = MonopBot()
bot.login()
print u'Montant dernière commande : {}'.format(bot.get_last_order_amount())
driver.quit()
