import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from Config.Config import Config
from Config.Logger import Logger
import pandas as pd

logger = Logger.get_logger()


class DataCrawler:

    def __init__(self):
        self.base_url = Config.BASE_URL
        self.images_directory = Config.IMAGES_DIRECTORY
        self.selectors = Config.SELECTORS
        Config.ensure_directories()

    async def fetch(self, session, url):
        try:
            async with session.get(url) as response:
                logger.info(f"Fetching URL: {url}")
                return await response.text()
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    async def download_image(self, session, image_url, filename):
        try:
            async with session.get(image_url) as response:
                if response.status == 200:
                    async with aiofiles.open(filename, 'wb') as f:
                        await f.write(await response.read())
                    logger.info(f"Downloaded image: {filename}")
                else:
                    logger.warning(f"Failed to download image from {image_url}")
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {e}")

    async def scrape_product_info(self, session, product_url):
        html_content = await self.fetch(session, product_url)
        if not html_content:
            return {}
        product_info = {}
        soup = BeautifulSoup(html_content, 'html.parser')
        name_element = soup.select_one(self.selectors['product_name'])
        if name_element:
            product_info['Name'] = name_element.text.strip()  # Extract the text and remove extra whitespace
            logger.info(f"Product Name: {product_info['Name']}")
        else:
            logger.warning(f"Product name not found on {product_url}")
        basic_info_table = soup.select_one(self.selectors['basic_info_table'])
        if basic_info_table:
            rows = basic_info_table.find_all('tr')
            for row in rows:
                ths = row.find_all('th')
                tds = row.find_all('td')
                for th, td in zip(ths, tds):
                    attribute_name = th.get('title', '').strip()
                    attribute_value = td.get('title', td.text).strip()
                    product_info[attribute_name] = attribute_value
            logger.info(f"Scraped basic information from {product_url}")
        else:
            logger.warning(f"No basic info table found on {product_url}")
        detailed_info_table = soup.select_one(self.selectors['detailed_info_table'])
        if detailed_info_table:
            rows = detailed_info_table.find_all('tr')
            for row in rows:
                ths = row.find_all('th')
                tds = row.find_all('td')
                for th, td in zip(ths, tds):
                    attribute_name = th.get('title', '').strip()
                    attribute_value = td.get('title', td.text).strip()
                    product_info[attribute_name] = attribute_value
            logger.info(f"Scraped detailed information from {product_url}")
        else:
            logger.warning(f"No detailed info table found on {product_url}")
        model_number = product_info.get('Số mô hình', 'unknown_model').replace(" ", "_")
        magiczoom_element = soup.select_one(self.selectors['magiczoom_image'])
        if magiczoom_element and 'href' in magiczoom_element.attrs:
            big_image_url = urljoin(self.base_url, magiczoom_element['href'])
            await self.download_image(session, big_image_url, f"{self.images_directory}/{model_number}_01.jpg")
        small_images = soup.select(self.selectors['additional_images'])
        for idx, img_tag in enumerate(small_images, start=2):
            small_image_url = urljoin(self.base_url, img_tag['src'])
            await self.download_image(session, small_image_url,
                                      f"{self.images_directory}/{model_number}_{str(idx).zfill(2)}.jpg")
        product_info['Product URL'] = product_url
        return product_info

    async def fetch_product_urls(self, session, page_url):
        html_content = await self.fetch(session, page_url)
        if not html_content:
            return []
        product_urls = []
        soup = BeautifulSoup(html_content, 'html.parser')
        product_links = soup.select(self.selectors['product_links'])
        for link in product_links:
            product_url = urljoin(self.base_url, link['href'])
            logger.info(f"Found product URL: {product_url}")
            product_urls.append(product_url)
        return product_urls

    async def scrape_all_products(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for page_num in range(Config.START_PAGE, Config.END_PAGE + 1):
                page_url = self.base_url if page_num == Config.START_PAGE else Config.PAGE_URL_TEMPLATE.format(
                    page_num=page_num)
                logger.info(f"Scraping page: {page_url}")
                tasks.append(self.fetch_product_urls(session, page_url))
            product_urls_per_page = await asyncio.gather(*tasks)
            all_product_urls = [url for product_urls in product_urls_per_page for url in product_urls]
            logger.info(f"Total product URLs collected: {len(all_product_urls)}")
            product_tasks = [self.scrape_product_info(session, product_url) for product_url in all_product_urls]
            all_product_info = await asyncio.gather(*product_tasks)
            return all_product_info

    def save_to_csv(self, df, filename):
        try:
            df.to_csv(filename, index=False)
            logger.info(f"Data saved to {filename} successfully.")
        except Exception as e:
            logger.error(f"Error saving data to Csv: {e}")

    async def run(self):
        product_info_list = await self.scrape_all_products()
        df = pd.DataFrame(product_info_list)
        self.save_to_csv(df, Config.CSV_FILENAME)
