import sqlite3

class Database:

    def __init__(self, login):
        self.conn = sqlite3.connect(login)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, email text,"
                         "password text, ip text, sms text, img_dir text, vid_dir text)")
        self.conn.commit()

    def fetch(self):
