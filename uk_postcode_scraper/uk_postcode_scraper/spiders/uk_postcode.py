import re

import scrapy


class UkPostcodeSpider(scrapy.Spider):
    name = "uk_postcode"
    start_urls = ["https://www.doogal.co.uk/AdministrativeAreas.php/"]
    home_url = "https://www.doogal.co.uk/"

    postcode_page_number = 2

    def extract_district_code(self, url: str) -> str:
        pattern1 = r"(?<==).*$"
        pattern2 = r"(?<==)(.*?)(?=&)"

        if "page" in url:
            return re.search(pattern2, url).group()

        return re.search(pattern1, url).group()

    def parse(self, response):
        rows = response.xpath("//tr")[1:]

        for row in rows:
            data_url = row.xpath("./td/a/@href").extract()
            data_area = row.xpath("./td/a/text()").extract()

            try:
                admin_url, county_url = data_url
                admin_area, county_area = data_area

                admin_url = self.home_url + admin_url
                county_url = self.home_url + county_url

                urls = admin_url + county_url
                areas = admin_area + county_area

                for url, area in zip(urls, areas):

                    try:
                        yield response.follow(
                            url,
                            callback=self.parse_area,
                            cb_kwargs={
                                "area": area,
                                "district_code": self.extract_district_code(url)
                            }
                        )

                    except AttributeError:
                        continue

            except ValueError:
                try:
                    admin_url, admin_area = data_url[0], data_area[0]
                    county_url, county_area = "", ""

                    url = self.home_url + admin_url

                    try:
                        yield response.follow(
                            url,
                            callback=self.parse_area,
                            cb_kwargs={
                                "area": admin_area,
                                "district_code": self.extract_district_code(url)
                            }
                        )

                    except AttributeError:
                        continue

                except IndexError:
                    pass

    def parse_area(self, response, area, district_code):
        rows = response.xpath("//tr")

        for row in rows:
            postcode_url = row.xpath("./td/a/@href").get()
            postcode = row.xpath("./td/a/text()").get()

            try:
                url = self.home_url + postcode_url
                ward = row.xpath("./td/text()").extract()[0]

                self.logger.info(f"Checking postcode availability: {postcode}")
                yield response.follow(
                    url,
                    callback=self.parse_postcode,
                    cb_kwargs={
                        "area": area,
                        "postcode": postcode,
                        "ward": ward
                    }
                )

            except TypeError:
                continue

        try:
            next_page = f"https://www.doogal.co.uk/AdministrativeAreas.php?district={district_code}&page={self.postcode_page_number}"
            self.postcode_page_number += 1
            self.logger.info(f"Following page: {self.postcode_page_number}")

            yield response.follow(
                next_page,
                callback=self.parse_area,
                cb_kwargs={
                    "area": area,
                    "district_code": district_code,
                }
            )

        except Exception:
            pass

    def parse_postcode(self, response, area, postcode, ward):
        try:
            table = response.xpath("//div[@class='col-md-6']")[3]
            headers = table.xpath(".//th/text()").extract()

            if "Date usage ended" not in headers:
                yield {
                    "area": area,
                    "postcode": postcode,
                    "ward": ward
                }

        except Exception:
            pass
