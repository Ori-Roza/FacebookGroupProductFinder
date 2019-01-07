import argparse
from facebook_group_products_handler import FacebookGroupProductsHandler


def args():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-fg', '--facebook_group', help='A Facebook group you want to search in', required=True,
                        type=str)
    parser.add_argument('-r', '--range', help='A range of a product price-> e.x "3000,5000"', required=False, default=None, type=str)
    parser.add_argument('-l', '--is_live', help='Show on console or dump to file', required=False, default=1, type=int)
    return parser.parse_args()


def stream_products(facebook_group, price_range=None, is_live=True):
    s = FacebookGroupProductsHandler(facebook_group)
    while True:
        s.scroll_content()
        s.search_products(is_live=is_live, price_range=price_range)


if __name__ == '__main__':
    arguments = args()
    facebook_group = arguments.facebook_group
    is_live = bool(arguments.is_live)
    price_range = [int(edge) for edge in arguments.range.split(",")]
    stream_products(facebook_group, price_range, is_live=is_live)
