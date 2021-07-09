import requests
from bs4 import BeautifulSoup 
import re
import csv

class Shoes_data():
    def __init__(self):
        self.Brand_names = "NaN"
        self.Models = "NaN"
        self.Stylecodes = "NaN"
        self.Colors = "NaN"
        self.Ages = "NaN"
        self.Images_links = "NaN"
        self.Prices = "NaN"
        self.Sizes = "NaN"
        self.Product_list = []
    
    def Requesting_urls(self, url):
        data = requests.get(url).text
        Soap_object = BeautifulSoup(data)
        return Soap_object

    def Scrape_data(self, object, urls =''):
        pages = int( object.find('ul',class_='paginate').find_all('li')[-2].text )
        print(pages)

        for p in range(pages):
            if p != 0 :
                object = self.Requesting_urls(urls+f'?page={p}')

            shoelist = object.find('div',class_='layout bucket-list loading-overlay-wrapper bucket-list--mobi-override bucket-list-6')

            for i in range(len(shoelist)):
                try:
                    shoe_url = shoelist.find_all('div',class_='bucket bucket-product-with-details bucket-product-with-attributes')[i].find('a')['href']

                    data = self.Requesting_urls('https://superbalist.com'+shoe_url)

                    div = data.find_all('div',class_='product-accordion__content')

                    if (len(div)>1):
                        layout = div[1].find_all('div',class_="layout")
                    else:
                        layout = div[0].find_all('div',class_="layout")
                    
                    for j in range(len(layout)):
                        # Brands
                        if layout[j].find('div',class_='product-key').text == 'Brand':
                            self.Brand_names = layout[j].find('div',class_='product-value').text.strip('\n ')
                        # Style Code
                        if layout[j].find('div',class_='product-key').text == 'Style Code':
                            self.Stylecodes = layout[j].find('div',class_='product-value').text.strip('\n \t')
                        # Color
                        if layout[j].find('div',class_='product-key').text == 'Colour':
                            self.Colors = layout[j].find('div',class_='product-value').text.strip('\n ').split('/')
                    # Ages
                    Age_div = (div[0].find('div',class_='size').h3.contents[0].strip("/n ").split(" /")[0]).split(" ")
                    if len(Age_div) == 2:
                        self.Ages = Age_div[0]
                    else:
                        self.Ages = (Age_div[0], Age_div[2])

                    #Images Hyperlinks
                    imgs = data.find_all('img', class_='bucket-img')
                    self.Images_links = [im['src'] for im in imgs]

                    #Prices
                    self.Prices = data.find('span', class_='price').text.strip('\n ')

                    #Sizes
                    ex = 'sku--item *'
                    sizes = data.find_all('div', class_=re.compile(ex))
                    self.Sizes = [i.text.strip('\n UK') for i in sizes]

                    # Model
                    self.Models = data.find('h1',class_='headline-tight').text.strip('\n ').split(' - ')[0]
                    
                except IndexError:
                    break
                except AttributeError:
                    self.Ages = ' '
                self.Product_list.append([self.Brand_names, self.Models, self.Stylecodes, self.Colors, self.Ages, self.Images_links, self.Prices, self.Sizes])

    def Write_to_csv(self):
        Fields = ['Brand','Model','Style Code','Colour','Age','Pictures','Price','Sizes of Shoes Available']
        with open('Shoe_list.csv','w') as f :
            csv_file = csv.writer(f)
            csv_file.writerow(Fields)
            csv_file.writerows(self.Product_list)


def main():
    Urls = ['https://superbalist.com/browse/men/shoes/sneakers',
            'https://superbalist.com/browse/women/shoes/sneakers']
    crawler = Shoes_data()
    for k in range(len(Urls)):
        obj = crawler.Requesting_urls(Urls[k])
        crawler.Scrape_data(object=obj, urls=Urls[k])
    crawler.Write_to_csv()

if __name__ == '__main__':
    main()