import MySQLdb 


def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news")
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

if __name__ == '__main__':
    
    conn, cursor, = sql_connect()

    sql = """
       CREATE TABLE factchecking_data ( 
          id INT PRIMARY KEY AUTO_INCREMENT,
          title text,
          postid text, 
          dates datetime,
          veracity varchar(64),
          url text,
          source text
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """

    cursor.execute(sql)
    conn.commit()

    sql_close(cursor, conn)

