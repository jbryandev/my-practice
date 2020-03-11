from council.crawlers import edmond, el_reno, lawton, \
    midwest_city, moore, norman, okc, tulsa

class CrawlerFactory:

    @staticmethod
    def create_crawler(department):
        name = department.crawler.crawler_name
        crawler = None

        if name == "Edmond":
            crawler = edmond.EdmondCrawler(department)

        elif name == "El Reno":
            crawler = el_reno.ElRenoCrawler(department)

        elif name == "Lawton":
            crawler = lawton.LawtonCrawler(department)

        elif name == "Midwest City":
            crawler = midwest_city.MidwestCityCrawler(department)

        elif name == "Moore":
            crawler = moore.MooreCrawler(department)

        elif name == "Norman":
            crawler = norman.NormanCrawler(department)

        # elif name == "Oklahoma City":
        #     crawler = okc.OKCCrawler(department)

        # elif name == "Tulsa":
        #     crawler = tulsa.TulsaCrawler(department)

        return crawler
