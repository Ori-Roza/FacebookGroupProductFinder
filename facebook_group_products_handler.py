import codecs
import json
from consts import *
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def validate_range(r):
    if not r:
        return None
    if not isinstance(r, list) and not isinstance(r, tuple):
        return None
    if len(r) != 2:
        return None
    return [min(r), max(r)]


class FacebookGroupProductsHandler(object):
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
    def get_product_price(product):
        try:
            price_element = product.find_element_by_class_name(PRODUCT_PRICE_CLASS)
        except (NoSuchElementException, AttributeError):
            return -1  # Not every article has price
        if price_element:
            return int("".join(price_element.text[1:].split(",")))
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

    def handle_article(self, is_live, article_url, price, description):
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
            with codecs.open("products.txt", "a+", encoding='utf-8') as f:
                f.write(json.dumps(article))
                f.write("\n")

    def search_products(self, price_range=None, is_live=True):
        for wrap in self._products_wrappers:
            product = self.get_product(wrap)
            price = self.get_product_price(product)
            article_url = self.get_article_url(wrap)
            if price > 0:
                should_write_product = False
                price_range = validate_range(price_range)
                if price_range:
                    if price_range[0] <= price <= price_range[1]:
                        should_write_product = True
                else:
                    should_write_product = True

                if should_write_product and article_url not in self._articles_urls:
                    self.handle_article(is_live, article_url, price, wrap.text)



