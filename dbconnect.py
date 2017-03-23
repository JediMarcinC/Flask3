import pymysql

def connection():
    conn = pymysql.connect(host='localhost',
                           user='root',
                           passwd='kuba',
                           db='pythonprogramming')
    
    cur = conn.cursor()
    return cur, conn
