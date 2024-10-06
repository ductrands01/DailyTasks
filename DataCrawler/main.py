from Source.DataCrawler import DataCrawler
import asyncio


def main():
    crawler = DataCrawler()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(crawler.run())
    else:
        task = loop.create_task(crawler.run())


if __name__ == "__main__":
    main()
