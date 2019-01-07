import codecs
import json
import re
from consts import *
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def validate_range(given_range):
    if not given_range:
        return None
    if not isinstance(given_range, list) and not isinstance(given_range, tuple):
        return None
    if len(given_range) != 2:  # Range between 2 numbers only!
        return None
    return [min(given_range), max(given_range)]


class FacebookGroupProductsHandler(object):
    """
    Retrieves all products that their price is between a given range from a public Facebook group.
    Using selenium to search among the elements
    """
    _rendering_wait_time = 10
    _scrolling_pause_time = 0.1

    def __init__(self, facebook_group_url):
        self._group_url = facebook_group_url
        self._articles = []
        self._articles_urls = []
        self._driver = webdriver.Chrome(executable_path=WEB_DRIVER_EXE)
        self._driver.get(facebook_group_url)
        self._driver.implicitly_wait(3)

    def scroll_content(self):
        for i in range(0, 20):
            self._driver.execute_script(SCROLLING_SCRIPT)
            sleep(self._scrolling_pause_time)
        sleep(self._rendering_wait_time)  # more time for rendering the page

    @property
    def articles(self):
        return self._articles

    @property
    def _products_wrappers(self):
        return self._driver.find_elements_by_xpath(ARTICLES_XPATH)

    @staticmethod
    def get_product(wrapper):
        try:
            return wrapper.find_element_by_class_name(PRODUCT_CLASS)
        except NoSuchElementException:
            return None

    @staticmethod
    def search_valid_price_from_text(text, price_range):
        """
        If article does not contain a price, try to retrieve the price from the text.
        """
        valid_numbers = []
        for num in re.findall(r'\d+', text):
            if not num.startswith("0"):  # Probably a phone number
                if price_range[0] <= int(num) <= price_range[1]:
                    valid_numbers.append(int(num))
        if valid_numbers:
            return min(valid_numbers)
        return -1

    def get_product_price(self, product, wrapper, price_range):
        price_element = None
        try:
            price_element = product.find_element_by_class_name(PRODUCT_PRICE_CLASS)
        except (NoSuchElementException, AttributeError):
            if price_range:  # If does not have price range will return -1
                return self.search_valid_price_from_text(wrapper.text, price_range)
        if price_element:
            try:
                return int("".join(price_element.text[1:].split(",")))  # First char is the currency sign
            except ValueError:
                pass # will return -1 anyway
        return -1

    @staticmethod
    def get_article_url(wrapper):
        try:
            url_span = wrapper.find_element_by_tag_name("a")
        except (NoSuchElementException, AttributeError):
            return None
        if url_span:
            return url_span.get_attribute("href")
        return None

    def handle_article(self, is_live, article_url, price, description, output_file=""):
        """
        Whether print it or write it to a file
        """
        article = {
            "url": article_url,
            "price": price,
            "description": description
        }
        self._articles_urls.append(article_url)
        self._articles.append(article)

        if is_live:
            print article
        else:
            output_path = output_file if output_file else "products.txt"
            with codecs.open(output_path, "a+", encoding='utf-8') as f:
                f.write(json.dumps(article))
                f.write("\n")

    def search_products(self, price_range=None, is_live=True, output_file=""):
        price_range = validate_range(price_range)
        for wrap in self._products_wrappers:
            product = self.get_product(wrap)
            price = self.get_product_price(product, wrap, price_range)
            article_url = self.get_article_url(wrap)
            if price > 0:
                should_write_product = False
                if price_range:
                    if price_range[0] <= price <= price_range[1]:
                        should_write_product = True
                else:
                    should_write_product = True

                if should_write_product and article_url not in self._articles_urls:
                    self.handle_article(is_live, article_url, price, wrap.text, output_file=output_file)
