from importlib import import_module

def create_crawler(department, progress_recorder):
    name = department.crawler.crawler_name
    module = import_module(".crawlers.{}".format(name), package="council")
    crawler = getattr(module, name)(department, progress_recorder)
    return crawler
