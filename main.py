import argparse
from facebook_group_products_handler import FacebookGroupProductsHandler


def args():
    parser = argparse.ArgumentParser(
        description='retrieves all products between a given range from a public Facebook group')
    parser.add_argument('-fg', '--facebook_group', help='A Facebook group you want to search in', required=True,
                        type=str)
    parser.add_argument('-r', '--range', help='A range of a product price-> e.x "3000,5000"', required=False,
                        default=None, type=str)
    parser.add_argument('-l', '--is_live', help='Show on console or dump to file', required=False, default=1, type=int)
    parser.add_argument('-o', '--output_file', help='If is_live is False then we can set the file path', required=False,
                        default="", type=str)
    return parser.parse_args()


def stream_products(facebook_group, price_range=None, is_live=True, output_file=""):
    """
    Endless loop that retrieves all products between a given range from a public Facebook group
    :param facebook_group: URL of a public Facebook group
    :param price_range: list of a range e.g [3000, 5000]
    :param is_live: Bool, True to print on screen, False to write to file
    :return:
    """
    s = FacebookGroupProductsHandler(facebook_group)
    while True:
        s.scroll_content()
        s.search_products(is_live=is_live, price_range=price_range, output_file=output_file)


if __name__ == '__main__':
    arguments = args()
    facebook_group = arguments.facebook_group
    is_live = bool(arguments.is_live)
    output_path = arguments.output_file
    if arguments.range:
        price_range = [int(edge) for edge in arguments.range.split(",")]
    else:
        price_range = None
    stream_products(facebook_group, price_range, is_live=is_live, output_file=output_path)
