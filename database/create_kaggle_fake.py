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
       CREATE TABLE kaggle_data ( 
          id INT PRIMARY KEY AUTO_INCREMENT,
          uuid varchar(64),
          ord_in_thread int,
          author text,
          published datetime, 
          title text,
          description text,
          language varchar(16),
          crawled datetime, 
          site_url text, 
          country text, 
          domain_rank int, 
          thread_title text,
          spam_score float, 
          main_img_url text,
          replies_count int, 
          participants_count int, 
          likes int, 
          comments int, 
          shares int, 
          type text
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """

    cursor.execute(sql)
    conn.commit()

    sql_close(cursor, conn)

