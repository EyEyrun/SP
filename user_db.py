import sqlite3

class Database:

    def __init__(self, login):
        self.conn = sqlite3.connect(login)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email text,"
                         "password text, sms text, video_directory text, image_directory)")
        self.conn.commit()

    def verify(self, email):
        self.cur.execute("SELECT * FROM users WHERE email=?", (email,))
        rows = self.cur.fetchone()
        return rows

    def signup(self, email, password, sms, video_directory, image_directory):
        self.cur.execute("INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?)",
                         (email, password, sms, video_directory, image_directory))
        self.conn.commit()

    def login(self, email, password):
        self.cur.execute("SELECT * FROM users WHERE email=? AND password=?",
                         (email, password))
        rows = self.cur.fetchone()
        return rows

    def __del__(self):
        self.conn.close()

db = Database('users_log.db')