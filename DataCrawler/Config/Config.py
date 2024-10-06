import os


class Config:
    BASE_URL = "https://vietnamese.motospare-parts.com/buy-h4.html"
    PAGE_URL_TEMPLATE = "https://vietnamese.motospare-parts.com/buy-h4-page{page_num}.html"
    IMAGES_DIRECTORY = "DataCrawler/images"
    START_PAGE = 1
    END_PAGE = 5
    CSV_FILENAME = "scraped_products.csv"

    SELECTORS = {
        'product_name': "body > div.hu_product_detailmain_115V2.w > h1",
        'basic_info_table': "div.info table.tab1",
        'detailed_info_table': "div.info2 table.tab1",
        'magiczoom_image': "a.MagicZoom",
        'additional_images': "div.left_small_img span.pic_box img",
        'product_links': "div.imgbox a",
    }

    @staticmethod
    def ensure_directories():
        if not os.path.exists(Config.IMAGES_DIRECTORY):
            os.makedirs(Config.IMAGES_DIRECTORY)
