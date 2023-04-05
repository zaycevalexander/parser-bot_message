import pickle
import time

from apscheduler.schedulers.background import BlockingScheduler
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from TelegramBot8 import TeleBot
from writer_and_reader import read_file, write_url

# scheduler
scheduler = BlockingScheduler()

# telegram
API_KEY = 'API_KEY'
bot = TeleBot(API_KEY)
chat_id = 'CHAT_ID'

# options
options = webdriver.ChromeOptions()
options.add_argument(
    'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--headless')

s = Service(executable_path='/hh/chrome_driver/chromedriver')
driver = webdriver.Chrome(options=options, service=s)


# cookies
# pickle.dump(driver.get_cookies(), open('cookie', "wb"))


def main():
    try:
        main_url = 'page_for_parsing'
        driver.get(url=f'{main_url}0')
        time.sleep(3)
        for cookie in pickle.load(open('cookie', 'rb')):
            driver.add_cookie(cookie)
        print('cookie')
        time.sleep(3)
        driver.refresh()
        number_page = driver.find_elements('xpath', '//a[@rel="nofollow"]')
        number_list = []
        for i in number_page:
            if i.text.isdigit():
                number_list.append(i.text)
        max_page = number_list[-1]
        time.sleep(3)
        for page in range(1, int(max_page) + 1):
            print(page)
            driver.get(url=f'{main_url}{page}')
            with open(f'pages/page{page}.html', 'w', encoding='UTF-8') as file:
                file.write(driver.page_source)
            time.sleep(25)
            print('*' * 20)
        url = []
        for page in range(1, int(max_page) + 1):
            with open(f'/hh/chrome_driver/pages/page{page}.html') as file:
                src = file.read()
                obj = BeautifulSoup(src, 'lxml')
                a = obj.findAll('a', class_='serp-item__title')
                for i in a:
                    url.append(i.get('href'))
            new_list = set(url).difference(read_file()['list_value'])
            if new_list:
                for i in new_list:
                    bot.send_message(chat_id, text=str(i))
                    time.sleep(3)
            dict = {
                'list_value': new_list,
                'count': read_file()['count']
            }
            write_url(dict)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


scheduler.add_job(main, 'interval', minutes=20)

scheduler.start()
