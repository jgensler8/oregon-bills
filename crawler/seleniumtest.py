from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome()
driver.get("https://olis.leg.state.or.us/liz/2017R1/Measures/list/")

elem = driver.find_element_by_css_selector("a[href='#senateBills_search']")
elem.send_keys(Keys.RETURN)

elems = driver.find_elements_by_css_selector("a[data-parent='#senateBills_search']")
for elem in elems:
    time.sleep(3)
    elem.send_keys(Keys.RETURN)
time.sleep(5)
driver.close()

elem = driver.find_element_by_tag_name("html")
print(elem.get_attribute('outerHTML'))