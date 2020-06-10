import scrapy
import re
import logging
from datetime import datetime
from scrapy.utils.log import configure_logging

class Post(scrapy.Item):
    id = scrapy.Field()
    khuVuc = scrapy.Field()
    gia = scrapy.Field()
    dienTich = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    content = scrapy.Field()
    Hdetails = scrapy.Field()
    Sdetails = scrapy.Field()
    ngayDangTai = scrapy.Field()
    ngayHetHan = scrapy.Field()

class BDSSpider(scrapy.Spider):
    name = "BDS"
    
    logging.basicConfig(
        filename='log{}.txt'.format(datetime.now().strftime("%d%m%Y%H%M%S")),
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    # start_urls = ["https://batdongsan.com.vn/ban-dat/"]
    custom_settings = {
        'FEED_FORMAT':'json',                                 
        'FEED_URI':'dbs{}.json'.format(datetime.now().strftime("%d%m%Y%H%M%S"))                      
    }
    def start_requests(self):
      print("Start run !")
      cookies = {'psortfilter': '1%24all%24POh365XbYkg1Len7%2BJPrAA%3D%3D'}
      yield scrapy.Request("https://batdongsan.com.vn/ban-dat/", self.parse, headers={'Cookie':cookies})

    def parse(self, response):
        s = set()
        cookies = {'psortfilter': '1%24all%24POh365XbYkg1Len7%2BJPrAA%3D%3D'}

        txtMax = "".join([s.strip() for s in response.css('div.Header li[rel="all"] span ::text').getall()])
        numMax = int(re.search("[\d]+", txtMax).group())

        if response.request.url=="https://batdongsan.com.vn/ban-dat":
          numpage = 1
        else:
          numpage = int(response.request.url.split("/")[-1][1:])
        print("Trang {0} !".format(numpage))

        for link in response.css('div.search-productItem > div.p-title > h3 > a'):
          url = "https://batdongsan.com.vn"+link.attrib['href']
          id = link.attrib['href'].split("pr")[-1]
          #print(url)
          if (id not in s):
            s.add(id)
            check = 0
            yield scrapy.Request(url, self.parsePost)

        if (numMax//20>=numpage):
          yield scrapy.Request("https://batdongsan.com.vn/ban-dat/p{0}".format(numpage+1), self.parse, headers={'Cookie':cookies})

    def parsePost(self, response):
        id = response.css('div.prd-more-info > div > div::text').get().strip()
        khuVuc = " ".join([s.strip() for s in response.css('span.diadiem-title ::text').getall()])[23:]
        gia_dienTich = [" ".join([s.strip() for s in s.css('::text').getall()]) for s in response.css('span.gia-title')]
        gia = gia_dienTich[0][7:]
        dienTich = gia_dienTich[1][13:]
        tmp = []
        for s in response.css('div.pm-content ::text').getall():
          if "Tìm kiếm theo từ khóa" not in s.strip():
            tmp.append(s.strip())
          else:
            break
        content = "\n".join(tmp)
        Hdetails = dict()
        for detail in response.css('div.table-detail>div.row'):
          key = detail.css('div.left::text').get().strip().replace("\n","").replace("\r","")
          val = detail.css('div.right::text').get().strip().replace("\n","").replace("\r","")
          Hdetails[key]=val
        Sdetails = dict()
        for detail in response.css('div.table-detail div.right-content'):
          key = detail.css('div.left::text').get().strip().replace("\n","").replace("\r","")
          val = detail.css('div.right::text').get().strip().replace("\n","").replace("\r","")
          Sdetails[key]=val
        if ("Email" in Sdetails):
          mail = "".join([chr(int(num[:-1])) for num in response.css('div.contact-email script').extract()[0].split("mailto:")[-1].split("'>")[0].split("&#")[1:]])
          Sdetails["Email"] = mail
        ngayDangTai = response.css('div.prd-more-info>div')[2].css('div::text')[1].get().strip().replace("-","/")
        ngayHetHan = response.css('div.prd-more-info>div')[3].css('div::text')[1].get().strip().replace("-","/")
        try:
          latitude = float(response.css('input#hdLat').attrib['value'])
        except:
          latitude = 200
        try:
          longitude = float(response.css('input#hdLong').attrib['value'])
        except:
          longitude = 200
        return Post(id = id,
                    khuVuc = khuVuc,
                    gia = gia,
                    dienTich = dienTich,
                    latitude = latitude,
                    longitude = longitude,
                    content = content,
                    Hdetails = Hdetails,
                    Sdetails = Sdetails,
                    ngayDangTai = ngayDangTai,
                    ngayHetHan = ngayHetHan)
