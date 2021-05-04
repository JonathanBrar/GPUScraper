from urllib.request import urlopen
from bs4 import BeautifulSoup
import plotly.express as px
import pandas as pd
import time
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email():

    sender_email = 'jon.brar10@gmail.com'
    receiver_email = 'jon.brar10@gmail.com'
    password = 'Your Password'

    message = MIMEMultipart("alternative")
    message['Subject'] = 'A New GPU is in stock!'
    message["From"] = sender_email
    message["To"] = receiver_email

    html = """\
        <html>
            <body>
                <p> Here is the link: </p>
                <a href = "{link}"> link </a> 
            </body>
        </html>

    """.format(link=link)

    part1 = MIMEText(html, 'html')

    message.attach(part1)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


url = "https://www.newegg.ca/p/pl?N=100007708%204814%20601357282&cm_sp=Cat_video-Cards_1-_-Visnav-_-Gaming-Video-Cards_1"


link = urlopen(url)

newegg_html = link.read()
link.close()

page = BeautifulSoup(newegg_html, "html.parser")
item_container = page.find_all("div", {"class": "item-container"})

file = "gpuinfo.csv"

f = open(file, "w")

headers = 'stock,product,gpu_price\n'

f.write(headers)

for item in item_container:

    gpu_title = item.find_all('a', {"class": "item-title"})
    name_of_card = gpu_title[0].text
    shrunk_text = name_of_card[0:70]

    gpu_cost = item.find_all('li', {"class": "price-current"})
    price = gpu_cost[0].strong.text

    previous_cost = item.find_all('li', {"class": "price-was"})
    if (previous_cost[0].span == None):
        old_price = "Not on sale"
    else:
        old_price = previous_cost[0].span.text

    item_available = item.find_all('p', {"class": "item-promo"})
    if not item_available:
        stock = "In Stock!"
        send_email()
        # time.sleep(60)
    else:
        stock = item_available[0].text

    item_link = item.find_all('a', {'class': 'item-title'}, href=True)
    for el in item_link:
        link = el['href']

    print("Title: " + name_of_card)
    print("GPU Price: " + price)
    print("Old Price: " + old_price)
    print("Availability: " + stock + "\n")

    f.write(stock + "," + shrunk_text.replace(',', '|') +
            "," + price.replace(',', '') + "\n")


f.close()


data = pd.read_csv("gpuinfo.csv", sep=',')

fig = px.bar(data, x='product', y='gpu_price',
             title='3080 GPU Prices (NewEgg)', hover_name='stock')


fig.show()
