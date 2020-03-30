from council.crawlers.EdmondCrawler import EdmondCrawler
# from council.crawlers import el_reno, lawton, \
#     midwest_city, moore, norman, okc, tulsa

class CrawlerFactory:

    @staticmethod
    def create_crawler(department, progress_recorder):
        name = department.crawler.crawler_name
        crawler = None

        if name == "Edmond":
            crawler = EdmondCrawler(department, progress_recorder)

        # elif name == "El Reno":
        #     crawler = el_reno.ElRenoCrawler(department)

        # elif name == "Lawton":
        #     crawler = lawton.LawtonCrawler(department)

        # elif name == "Midwest City":
        #     crawler = midwest_city.MidwestCityCrawler(department)

        # elif name == "Moore":
        #     crawler = moore.MooreCrawler(department)

        # elif name == "Norman":
        #     crawler = norman.NormanCrawler(department)

        # elif name == "Oklahoma City":
        #     crawler = okc.OKCCrawler(department)

        # elif name == "Tulsa":
        #     crawler = tulsa.TulsaCrawler(department)

        return crawler
