import logging
import azure.functions as func
import pymysql
import xml.etree.ElementTree as ET


import pathlib
import urllib.parse as urlparse
import requests
from bs4 import BeautifulSoup


def get_ssl_cert():
    current_path = pathlib.Path(__file__).parent.parent
    return str(current_path / 'BaltimoreCyberTrustRoot.crt.pem')


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
            # Connect to MySQL
        cnx = pymysql.connect(user="zirong", password="Aa123456",
                          host="crawler-db.mysql.database.azure.com", port=3306, database="sitemap", ssl_ca=get_ssl_cert())
        logging.info(cnx)
        # Store data in databases
        url = urlparse.urljoin(name, 'sitemap.xml')
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, "xml")
        urls_sitemap = soup.findAll('url')
        urls = []
        for  i,u in enumerate(urls_sitemap):
            loc = u.find('loc')
            if not loc:
                loc = "None"
            else:
                loc = loc.string
            urls.append(loc)
            data = """INSERT INTO sitemap(name,loc) VALUES(%s,%s)"""
            c = cnx.cursor()
      
            # executing cursor object
            c.execute(data, (name, loc[:49]))
            cnx.commit()
            if i > 10:
                break
        str = "Successfully stored " + "Sitemap of " + name + "in sql database"

        # Send http requests to trigger function 2
        resp_from_http2 = requests.get("http://localhost:7071/api/HttpTrigger2")
        logging.info(resp_from_http2.content)
        return func.HttpResponse(str)
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200)

    