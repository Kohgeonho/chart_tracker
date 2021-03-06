import selenium.webdriver as webdriver
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from time import sleep
import datetime
from collections import defaultdict
from pytz import timezone

import pandas as pd
from tqdm import tqdm

display = None
driver = None

def driver_init():
    global display
    global driver
    
    display = Display(visible=0,size=(1024, 768))
    display.start()

    driver = webdriver.Chrome('/home/ubuntu/chromedriver')
    
def driver_quit():  
    driver.quit()
    display.stop()

def get_table():
        
    def find_id(element):
        return str(element)[25:33]
    
    def chart(n):        
        driver.get(f'https://www.genie.co.kr/chart/top200?pg={n}')
        page = driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        
        table = soup.find(attrs={'class':'newest-list'}) \
                    .find_all('tr', attrs={'class':'list'})
        
        return [find_id(e) for e in table]
        
    return chart(1) + chart(2) + chart(3) + chart(4)


class song_page():
        
    def __init__(self, id, rank):
        self.id = id
        self.rank = rank
    
    def get_page(self):
        url = f"https://www.genie.co.kr/detail/songInfo?xgnm={self.id}"
        self.url = url

        driver.get(url)
        song_page = driver.page_source
        song_soup = BeautifulSoup(song_page, 'lxml')
        self.soup = song_soup
        
    def get_name(self):
        self.name = self.soup.find('h2',attrs={'class':'name'}).text.strip()

    def get_values(self):
        values = self.soup.find('ul',attrs={'class':'info-data'}) \
                          .find_all(attrs={'class':'value'})
        attrs  = self.soup.find('ul',attrs={'class':'info-data'}) \
                          .find_all(attrs={'class':'attr'})
        items  = defaultdict(lambda: "NULL")
        
        def find_id(soup, char, num):
            return str(soup).split(char)[num]
        
        items['artist']   = find_id(values[0], "'", 3)
        items['album']    = find_id(values[1], "'", 3)
        items['??????']      = values[2].text
        items['????????????']   = "0:" + values[3].text
        
        for i, item in enumerate(attrs[4:]):
            attr = find_id(item, '"', 3)
            items[attr] = [find_id(v, "'", 1) for v in values[4+i].find_all('a')]
        
        self.artist    = items['artist']
        self.album     = items['album']
        self.genre     = items['??????']
        self.playtime  = items['????????????']
        self.lyricists = items['?????????']
        self.composers = items['?????????']
        self.arrangers = items['?????????']

        
    def get_likes(self):
        likes_raw = self.soup.find('em',attrs={'id':'emLikeCount'}).text
        likes_str = ''.join(likes_raw.strip().split(","))
        self.likes = int(likes_str)

    def get_totals(self):
        counts = self.soup.find('div', attrs={'class':'total'}) \
                     .find_all('div')
        listners_str = ''.join(counts[0].text.strip().split(","))
        self.listeners = int(listners_str)
        
        numplays_str = ''.join(counts[1].text.strip().split(","))
        self.numplays = int(numplays_str)
        
    def get_comments(self):
        comments_raw = self.soup.find('span', attrs={'class':'article'}).text
        comments_str = str(comments_raw)[3:].split("???")[0]
        self.comments = int(comments_str)

    def get_now(self):
        KST = timezone('Asia/Seoul')
        now_raw = datetime.datetime.now()
        now_kr_raw = now_raw.astimezone(KST)
        
        now_str = str(now_kr_raw).split(" ")
        now_date = now_str[0]
        now_time = now_str[1].split(":")[0] + ":00:00"
        
        self.now = now_date + " " + now_time

    def set_attributes(self):
        self.get_page()
        self.get_name()
        self.get_values()
        self.get_likes()
        self.get_totals()
        self.get_comments()
        self.get_now()

    def get_attributes(self):
        return (self.id, self.name, self.genre, self.playtime)
    
    def time_attributes(self):
        return (self.id, self.now, self.rank, self.numplays, self.likes, self.listeners, self.comments)
    
class musician_page():
    
    def __init__(self, id):
        self.id = id
    
    def get_page(self):
        url = f"https://www.genie.co.kr/detail/artistInfo?xxnm={self.id}"
        self.url = url

        driver.get(url)
        song_page = driver.page_source
        song_soup = BeautifulSoup(song_page, 'lxml')
        self.soup = song_soup
        
    def get_name(self):
        self.name = self.soup.find('h2',attrs={'class':'name'}).text.strip()
        
    def get_values(self):
        values = self.soup.find('ul',attrs={'class':'info-data'}) \
                          .find_all(attrs={'class':'value'})
        attrs  = self.soup.find('ul',attrs={'class':'info-data'}) \
                          .find_all(attrs={'class':'attr'})
        items  = defaultdict(lambda: "NULL")
        
        items['??????'], items['????????????'] = values[0].text.split("/")
        items['????????????']  = values[1].text
        items['??????']     = values[2].text.split("/")[0].strip()
        items['??????']     = values[3].text if len(values) > 3 else "NULL"
        
        self.gender      = items['??????']
        self.type        = items['????????????']
        self.period      = items['????????????']
        self.nationality = items['??????']
        
        debut = items['??????'].split("???")[0]
        self.debut = debut if debut != "" else "NULL"
    
    def set_attributes(self):
        self.get_page()
        self.get_name()
        self.get_values()

    def get_attributes(self):
        return (self.id, self.name, self.debut, self.nationality,
                self.gender, self.type)
    
    
class album_page():
    
    def __init__(self, id):
        self.id = id
    
    def get_page(self):
        url = f"https://www.genie.co.kr/detail/albumInfo?axnm={self.id}"
        self.url = url

        driver.get(url)
        song_page = driver.page_source
        song_soup = BeautifulSoup(song_page, 'lxml')
        self.soup = song_soup
        
    def get_name(self):
        self.name = self.soup.find('h2',attrs={'class':'name'}).text.strip()
        
    def get_values(self):
        values = self.soup.find('ul',attrs={'class':'info-data'}) \
                          .find_all(attrs={'class':'value'})
        attrs  = self.soup.find('ul',attrs={'class':'info-data'}) \
                          .find_all(attrs={'class':'attr'})
        items  = defaultdict(lambda: "NULL")
        
        items['??????'], items['?????????'] = values[1].text.split(" / ")
        items['?????????'] = values[2].text
        items['?????????'] = values[3].text
        items['?????????'] = values[4].text
        
        self.genre        = items['??????']
        self.style        = items['?????????']
        self.release_co   = items['?????????']
        self.agency       = items['?????????']
        self.release_date = items['?????????'].strip().replace(".", "-")
    
    def get_tracks(self):
        track_soup = self.soup.find('div', attrs={'class':'songlist-box'}) \
                              .find_all('tr', attrs={'class':'list'})

        self.tracks = [(str(tsoup).split('"')[3], 
                        'Title' if tsoup.find('td', attrs={'class':'info'}) \
                                        .find('a',  attrs={'href': '#'}) \
                                        .text.startswith('\nTITLE') else "NULL")
                       for tsoup in track_soup]
    
    def set_attributes(self):
        self.get_page()
        self.get_name()
        self.get_values()
        self.get_tracks()

    def get_attributes(self):
        return (self.id, self.name, self.agency, self.release_date,
                self.genre, self.style)
    
