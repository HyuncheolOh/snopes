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
       CREATE TABLE snopes_set ( 
          id INT PRIMARY KEY AUTO_INCREMENT,
          post_id varchar(32) NOT NULL,
          title text,
          category varchar(64),
          url text,
          description text,
          veracity varchar(16),
          published_date datetime,
          modified_date datetime,
          share_count int(11),
          fact_checker varchar(64),
          claim text,
          sources text,
          tag text,
          detailed_description text
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """

    cursor.execute(sql)
    conn.commit()

    sql_close(cursor, conn)

