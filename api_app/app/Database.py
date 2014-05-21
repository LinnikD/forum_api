import MySQLdb


class Database:

    user = 'root'
    password = '1508'
    host = 'localhost'
    db_name = 'mydb'
    connection = None

    def __init__(self):
        self.connect()

    def get_cursor(self, query_str, data=None):
        cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)
        if data is None:
            cursor.execute(query_str)
        else:
            if type(data) is tuple:
                cursor.execute(query_str, data)
            else:
                cursor.execute(query_str, (data, ))
        return cursor

    def query(self, query_str, data=None):
        try:
            cursor = self.get_cursor(query_str, data)
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            cursor = self.get_cursor(query_str, data)
        data = cursor.fetchall()
        cursor.close()
        return data

    def connect(self):
        self.connection = MySQLdb.connect(self.host, self.user, self.password, self.db_name, use_unicode=True)
        self.connection.set_character_set('utf8')
        c = self.connection.cursor()
        c.execute('SET NAMES utf8;')
        c.close()

    def insert(self, query_str, data=None):
        try:
            cursor = self.get_cursor(query_str, data)
            self.connection.commit()
            cursor.close()
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            cursor = self.get_cursor(query_str, data)
            cursor.close()

    def clear(self):
        self.query("SET FOREIGN_KEY_CHECKS = 0")
        self.query("TRUNCATE TABLE subscriptions")
        self.query("TRUNCATE TABLE followers")
        self.query("TRUNCATE TABLE threads")
        self.query("TRUNCATE TABLE posts")
        self.query("TRUNCATE TABLE forums")
        self.query("TRUNCATE TABLE users")
        self.query("SET FOREIGN_KEY_CHECKS = 1")






db = Database()
