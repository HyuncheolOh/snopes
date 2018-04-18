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
       CREATE TABLE trends_manual ( 
          id INT PRIMARY KEY AUTO_INCREMENT,
          post_id varchar(32) NOT NULL,
          title text,
          key_word varchar(32),
          published_date datetime,
          dates_month text,
          values_month text,
          dates_year text,
          values_year text
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """

    cursor.execute(sql)
    conn.commit()

    sql_close(cursor, conn)

