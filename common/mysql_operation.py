import pymysql


class mysql_operation:
    @classmethod
    def create_connect(cls, mysql_info):
        mysql_info['charset'] = 'utf8'
        conn = pymysql.connect(**mysql_info)
        return conn

    @classmethod
    def exec_sql(cls, sql, mysql_info):
        conn = cls.create_connect(mysql_info)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                conn.commit()
                cursor.close()
                conn.close()
                return True
            except Exception as e:
                # sql执行失败 回滚
                conn.rollback()
                raise Exception("sql执行失败 " + str(e.args))
        else:
            return


if __name__ == "__main__":
    mysql_info = {
        "host": "192.168.13.206",
        "port": 3306,
        "user": "root",
        "password": "yss123",
        "database": "sph_autiomatic",
        "connect_timeout": 1,
    }
    mysql_operation.exec_sql("UPDATE mysql_info SET password = 'adas123asd' WHERE id = 5", mysql_info)
    # mysql_operation.exec_sql("SELECT * FROM mysql_info ", mysql_info)
    # a = mysql_operation.create_connect(mysql_info)
