from facebook_group_products_handler import FacebookGroupProductsHandler


def stream_products(facebook_group, price_range=None, is_live=True):
    s = FacebookGroupProductsHandler(facebook_group)
    while True:
        s.scroll_content()
        s.search_products(is_live=is_live, price_range=price_range)


if __name__ == '__main__':
    FACEBOOK_GROUP = "https://www.facebook.com/groups/295395253832427/"
    PRICE_RANGE = [3000, 5000]
    stream_products(FACEBOOK_GROUP, PRICE_RANGE, is_live=False)
