import mysql.connector
from mysql.connector import errorcode
import env

def Connect():
    try:
        return mysql.connector.connect(
            host=env.DB.Host,
            port=env.DB.HostPort,
            user=env.DB.Username,
            password=env.DB.Password,
            database=env.DB.Database,
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return False