from saveSQL import *
import schedule

print("program started", end='\n\n')
crawl()
schedule.every().hour.do(crawl)
while True:
    schedule.run_pending()
    sleep(1)