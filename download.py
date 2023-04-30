import sqlite3, requests, os, threading
from util import get_db
from config import headers


def download(url: str, path: str):
    global has_finish
    try:
        r = requests.get(url, headers=headers)
    except:
        return download(url, path)
    if r.content.startswith(b'<!DOCTYPE html>'):
        return download(url, path)
    f = open(path, 'wb')
    f.write(r.content)
    lock.acquire()
    has_finish += 1
    print(f'\r已下载 {has_finish} / {all_count} 张', end='')
    lock.release()
    sem.release()


def get_img_list() -> list:
    conn, cursor = get_db()
    data = cursor.execute('SELECT * FROM "img_list"').fetchall()
    return data


if __name__ == '__main__':
    if not os.path.exists('images'):
        os.mkdir('images')

    img_list = get_img_list()
    threads = []
    lock = threading.Lock()
    sem = threading.Semaphore(20)
    has_finish = 0
    all_count = len(img_list)
    for img_info in img_list:
        img_id, pre_img_url, img_url, title, path = img_info
        file_path = f'images/{img_id}.jpg'
        img_url = 'https://pic.netbian.com' + img_url
        sem.acquire()
        thread = threading.Thread(target=download, args=(img_url, file_path))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
