import requests, re, sqlite3, threading
from util import re_search, get_db, close_db
from config import paths, headers


def get_list(path: str, page: int = 1, get_all_page: bool = False):
    page_str = f'index_{page}.html' if page > 1 else ''
    url = f'https://pic.netbian.com/{path}/{page_str}'
    r = requests.get(url, headers=headers)
    r.encoding = 'gbk'
    data = r.text
    all_page = re_search(r'<span class="slh">.*?>(\d+)<', data)
    if not all_page:
        print('请求错误')
        return
    if get_all_page:
        return int(all_page)
    ul = re_search(r'list">.*?<ul class=".*?clearfix.*?">(.*?)</ul>', data)
    li = re.findall(r'<li>(.*?)</li>', ul, re.DOTALL)
    list_data = []
    for i in li:
        img_id = re_search(r'href="/tupian/(.*?).html"', i)
        pre_img_url = re_search(r'<img.*?src="(.*?)"', i)
        title = re_search(r'alt="(.*?)"', i)
        list_data.append(
            {'img_id': img_id, 'pre_img_url': pre_img_url, 'title': title, 'path': path}
        )
    return list_data


def thread_get_list(path: str, page: int = 1):
    global all_list, has_finish, all_page
    list_data = get_list(path, page)
    lock.acquire()
    has_finish += 1
    all_list += list_data
    print(f'\r已抓取 {has_finish}/{all_page} 页（{path}）', end='')
    lock.release()
    sem.release()


def insert_img_info(img_info: dict):
    global has_finish, img_count
    conn, cursor = get_db()
    img_id = img_info['img_id']
    img_url = get_img_url(img_id)
    img_info['img_url'] = img_url
    lock.acquire()
    try:
        cursor.execute(
            'INSERT INTO "img_list" VALUES (?, ?, ?, ?, ?)',
            (
                img_info['img_id'],
                img_info['pre_img_url'],
                img_info['img_url'],
                img_info['title'],
                img_info['path'],
            ),
        )
        conn.commit()
    except Exception as e:
        pass
    close_db(conn, cursor)
    has_finish += 1
    print(f'\r已采集 {has_finish} / {img_count} 张图片', end='')
    lock.release()
    sem.release()


def get_img_url(img_id: str):
    url = f'https://pic.netbian.com/tupian/{img_id}.html'
    r = requests.get(url, headers=headers)
    r.encoding = 'gbk'
    img_url = re_search(r'id="img"><img src="(.*?)"', r.text)
    return img_url


def init_table():
    '''初始化数据表'''
    conn, cursor = get_db()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS "img_list" (
            "img_id" INTEGER NOT NULL,
            "pre_img_url" TEXT NOT NULL,
            "img_url" TEXT NOT NULL,
            "title" TEXT NOT NULL,
            "path" TEXT NOT NULL,
            PRIMARY KEY("img_id")
        )'''
    )
    close_db(conn, cursor)


if __name__ == '__main__':
    init_table()
    lock = threading.Lock()
    sem = threading.Semaphore(20)
    threads = []
    all_list = []
    for path in paths:
        all_page = get_list(path, get_all_page=True)
        has_finish = 0
        for i in range(all_page):
            sem.acquire()
            thread = threading.Thread(target=thread_get_list, args=(path, i + 1))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        print()
    threads = []
    has_finish = 0  # 已完成的任务数量
    img_count = len(all_list)  # 任务总数量
    img_ids = []
    for img_info in all_list:
        sem.acquire()
        img_id = img_info['img_id']
        if img_id not in img_ids:
            img_ids.append(img_id)
            thread = threading.Thread(target=insert_img_info, args=(img_info,))
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()
    get_list(path)
