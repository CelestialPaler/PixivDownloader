'''
This script implements a web crawler, resource downloader and resource manager. 
By running the script, you can update and maintain a specific collection of illustrations 
by setting related parameters such as keywords.
What the does script do can be discribed as follows.
First, information of the target illustration is scanned by the crawler (using the pixivpy App-api). 
Then, a CSV file (illust_data.csv) is used to track all the illustrations that have already been downloaded, 
which means the illustrations will not be downloaded twice. After that, a download task is generated,
and the task is performed by the thread pool. Finally, the CSV file will bem updated and a summary 
will be displayed.
It's worth mentioning that this script simply implements some lightweight features, just as an automated 
script designed to maintain a small image collection. There are a lot of problems that are not well solved,
just use some 'patches' to make the function work for now.
The idea is merely craw and download some illustrations from pixiv, 
so it is far from being a reliable and decent tool. 
So, just use it as a simple wheelbarrow.

1. Install related dependencies (pixivpy, etc.).
2. Create a new folder and save the script in it.
3. Modify the keywords (support multiple keywords). Modify the user name and password used for login (no priority account required).
4. Run the script. The illustration will be saved in the illustration subfolder.
5. When you need to update the illustration collection, run the script again.

See more: https://www.tianshicangxie.com
Github: https://github.com/CelestialPaler
Copyright (c) 2019 Celestial Tech
'''
import os
import sys
import string
import pixivpy3
import requests
import shutil
from multiprocessing import Pool
import csv
import time
import errno 
from datetime import datetime

import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

# functions to show the summary of the operation
def show_summary(keywords, page_index, scanned_num, new_num, serial_num, illust_existed, start_time):
    log = '\n'
    log += '*' * 50
    log += '\nAll task finished!\nSummmery:\n'
    log += '   Keywords scanned: '
    log += str(keywords)
    log += '\n   '
    log += 'Pages: %d\n   Scanned: %d\n   ' % (page_index, scanned_num)
    log += 'New: %d\n   Downloaded: %d\n   ' % (new_num, serial_num)
    log += 'Illust In Total: %d\n' % (len(illust_existed))
    sec = time.time() - start_time
    log += 'Time Used: %d min %d sec\n' % (sec/60, sec%60)
    log += '*' * 50
    logging.info(log)

def env_init():
    dirname = os.path.dirname(__file__)
    illust_folder_path = os.path.join(dirname, 'Illustrations')
    illust_log_path = os.path.join(dirname, 'illust_data.csv')
    try:
        os.makedirs(illust_folder_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise        
    if not os.path.exists(illust_log_path):
        illust_init_log = open(illust_log_path, 'w', newline='', encoding='utf-8')
        log_init_writer = csv.writer(illust_init_log, delimiter=',')
        log_init_writer.writerow(['id', 'title'])
        illust_init_log.close()

# job function that will be assigned to a worker thread in the pool
def download_image(serial_num, target_folder, illust_id, illust_title, illust_url):
    # remove invalid charactor in illust_title
    invalid_charactor = '<>:"/\|?*' # for win10
    illust_title = illust_title.translate(illust_title.maketrans(invalid_charactor, ' ' * len(invalid_charactor)))
    illust_save_path = target_folder + 'Illustrations\\' + str(illust_id) + ' ' + illust_title + '.jpg'

    # pixiv is blocking requests from agents, there`s lots of solutions.
    # check :https://pixiv.cat/reverseproxy.html
    illust_url = illust_url.replace('i.pximg.net', 'i.pixiv.cat')
    illust_url_backup = illust_url
    # in order to get the oringinal image
    illust_url = illust_url.replace('c/600x1200_90_webp/img-master', 'img-original')
    illust_url = illust_url.replace('_master1200', '')

    rqst = requests.get(illust_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})

    # if request failed, it might be caused by the reason that the oringinal illustration is in
    # the png format, so before abort the task, try to download .png instead.
    if rqst.status_code != 200:
        illust_save_path = target_folder + 'Illustrations\\' + str(illust_id) + ' ' + illust_title + '.png'
        illust_url = illust_url.replace('.jpg', '.png')
        rqst = requests.get(illust_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
        # if the requset failed again, use oringnal url to download compressed version of the illustration 
        if rqst.status_code != 200:
            rqst = requests.get(illust_url_backup, stream=True, headers={'User-agent': 'Mozilla/5.0'})
            if rqst.status_code != 200:
                log = '  Request Error! Serial: %4d | ' % (serial_num)
                log += 'Serial: %4d | ID: %5d | Title: %s | URL: %s | ' % (serial_num, illust_id, illust_title, illust_url) 
                log += 'Error Code: %s' % (rqst.status_code)
                logging.error(log)
            
    try:
        # download the illustration
        with open(illust_save_path, 'wb') as f:
            rqst.raw.decode_content = True
            shutil.copyfileobj(rqst.raw, f)
            log = '  Download Successfully. '
            log += 'Serial: %4d | ID: %5d | Title: %s | URL: %s ' % (serial_num, illust_id, illust_title, illust_url)
            logging.info(log)
    except:
        log = '  Download Failed. '
        log += 'Serial: %4d | ID: %5d | Title: %s | URL: %s ' % (serial_num, illust_id, illust_title, illust_url)
        logging.error(log)
    return None

if __name__ == '__main__':
    # set the keywords
    keywords = ['keyword1', 'keyword2', 'keyword3']
    account = "your_account@somemail.com"
    password = "your_password"
    
    # in the root floder a log file will be created to store some info
    # and the illustration will be stored in the 'Illusts' folder
    target_folder = os.path.dirname(__file__) + '\\'
    env_init()

    # some initialization
    start_time = time.time()
    thread_pool = Pool(processes=10)       
    serial_num, page_index = 0, 0
    scanned_num, new_num = 0, 0
    # set a limit to decide when to stop scanning
    serial_num_limit, page_index_limit = 50000, 1000

    # read info about which illust has already been download
    illust_existed = set()
    with open(target_folder + 'illust_data.csv', 'r', encoding='utf-8') as illust_log:
        csv_reader = csv.DictReader(illust_log, delimiter=',')
        for row in csv_reader:
            illust_existed.add(int(row['id']))
    # open the log in write mode to append new informations
    illust_log = open(target_folder + 'illust_data.csv', 'a+', newline='', encoding='utf-8')
    
    # get pixiv api, source code: https://github.com/upbit/pixivpy
    aapi = pixivpy3.AppPixivAPI()
    # login your account, no premium needed
    aapi.login(account, password)

    # open the log in write mode to append new informations
    illust_log = open(target_folder + 'illust_data.csv', 'a+', newline='', encoding='utf-8')
    # search by the keyword
    for keyword in keywords:
        logging.info('Start scanning for %s' % (keyword))
        page_index = 0
        # get the first page of the search result
        search_result = aapi.search_illust(
            word = keyword,
            search_target='partial_match_for_tags', 
            sort='date_desc', 
            duration=None, 
            req_auth=True)  
        # scan all the pages one by one
        while (serial_num < serial_num_limit) and (page_index < page_index_limit):
            tasks = list()
            try:
                for illust_index in range(len(search_result.illusts)):
                    illust = search_result.illusts[illust_index]
                    log = '  Scanning... '
                    log += 'Current Page/Index: %3d/%2d | ' % (page_index, illust_index)
                    log += 'ID: %5d | Title: %s' % (illust.id, illust.title)  
                    logging.info(log)
                    scanned_num += 1

                    illust_url = illust.image_urls['large']

                    # check if the illustration has already been downloaded
                    #if illust.id in illust_existed:
                    if illust.id in illust_existed:
                        log = '  Illustration Already Existed.  Skip. '
                        log += 'ID: %5d | Title: %s' % (illust.id, illust.title)
                        logging.info(log)
                    else:
                        # add new download task     
                        tasks.append((serial_num, target_folder, illust.id, illust.title, illust_url))
                        serial_num+=1
                        # add the new illustration to the set
                        illust_existed.add(illust.id)
                        # update the log file
                        log_writer = csv.writer(illust_log, delimiter=',')
                        log_writer.writerow([illust.id, illust.title]) 
                        new_num += 1
                illust_log.flush()                
   
                # start downloading
                # your can use a task queue to add and assign tasks simultaneously
                # and let the web-crawler and the downloader run independently in parallel
                # which can achieve a better performance, but in here, performance 
                # is not that critical, so yep, one page by one page is good enough
                thread_pool.starmap(download_image, tasks)

                # get the next page
                if search_result.next_url is not None:
                    next_qs = aapi.parse_qs(search_result.next_url)
                    search_result = aapi.search_illust(**next_qs)
                    page_index += 1
                else:
                    break

            except:
                log = '  Unexpected error. Abort. '
                logging.critical(log) 
                break
    
    illust_log.close() 
    show_summary(keywords, page_index, scanned_num, new_num, serial_num, illust_existed, start_time)
