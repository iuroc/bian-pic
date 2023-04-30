import re, sqlite3

def re_search(pattern, text, flag=re.DOTALL):
    result = re.search(pattern, text, flag)
    return result.group(1) if result else None


def get_db():
    '''获取数据库连接和游标'''
    conn = sqlite3.connect('bian_pic_all.db')
    cursor = conn.cursor()
    return conn, cursor

def close_db(conn, cursor):
    '''关闭数据库连接和游标'''
    cursor.close()
    conn.commit()
    conn.close()