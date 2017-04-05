import luigi
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import urllib2
import os
from bs4 import BeautifulSoup


class WebPageSource(luigi.Task):
    def requires(self):
        return []

    def output(self):
        return luigi.LocalTarget("intermediate/measure-list.html")

    def run(self):
        baseURL = "olis.leg.state.or.us"
        season = "2017R1"
        url = "https://{}/liz/{}/Measures/list/".format(baseURL, season)
        driver = webdriver.Chrome()
        with self.output().open('w') as out:
            driver.get(url)

            elem = driver.find_element_by_css_selector("a[href='#senateBills_search']")
            elem.send_keys(Keys.RETURN)

            elems = driver.find_elements_by_css_selector("a[data-parent='#senateBills_search']")
            for elem in elems:
                time.sleep(3)
                elem.send_keys(Keys.RETURN)
            time.sleep(10)

            elem = driver.find_element_by_tag_name("html")
            out.write(elem.get_attribute('outerHTML'))
            driver.close()


class WebPage2PDFLinks(luigi.Task):
    def requires(self):
        return [WebPageSource()]

    def output(self):
        return luigi.LocalTarget("intermediate/measure-list-links.txt")

    def run(self):
        with self.input()[0].open() as page, self.output().open('w') as out:
            soup = BeautifulSoup(page.read(), "html5lib")
            for a in soup.find_all('a', href=True):
                out.write(a['href'])
                out.write('\n')


class FilterPDFLinks(luigi.Task):
    def requires(self):
        return [WebPage2PDFLinks()]

    def output(self):
        return luigi.LocalTarget("intermediate/measure-filtered-links.txt")

    def run(self):
        with self.input()[0].open() as links, self.output().open('w') as out:
            for link in links:
                if link.endswith("Introduced\n"):
                    out.write(link)


class DownloadPDFLinks(luigi.Task):
    def requires(self):
        return [FilterPDFLinks()]

    # def output(self):
    #     return luigi.LocalTarget("intermediate/measure-filtered-links.txt")

    def download_file(self, url, path):
        response = urllib2.urlopen(url)

        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(path, 'w') as f:
            f.write(response.read())
            f.close()

    def run(self):
        num_lines = sum(1 for line in self.input()[0].open())

        with self.input()[0].open() as links:
            baseURL = "olis.leg.state.or.us"
            failed = 0
            i = 0
            for link in links:
                # Fix newlines on the end of the line
                link = link.strip()
                url = "https://{}/{}".format(baseURL, link)
                filepath = os.path.join("../data{}.pdf".format(link))
                try:
                    self.download_file(url, filepath)
                except:
                    failed += 1
                i += 1
                self.set_status_message("Progress: {} / {}; Failed: {}".format(i, num_lines, failed))
                time.sleep(1)

if __name__ == '__main__':
    luigi.run()
