import os
import psycopg2
import psycopg2.extras
import json


class QueryManager:
    dbCon = None;

    def __init__(self):
        self.dbCon = psycopg2.connect(database=os.environ.get("DATABASE_NAME"),
                                      user=os.environ.get("DATABASE_USERNAME"),
                                      password=os.environ.get("DATABASE_PASSWORD"),
                                      host=os.environ.get("DATABASE_HOST"),
                                      port=os.environ.get("DATABASE_PORT"),
                                      connection_factory=psycopg2.extras.DictConnection,
                                      cursor_factory=psycopg2.extras.RealDictCursor)
        if self.dbCon is None:
            print("Failed to connect to DB.")
        else:
            print("Connected to DB.")

    def get_users(self):
        if self.dbCon is not None:
            cur = self.dbCon.cursor()
            cur.execute("Select * from Users;")
            result = cur.fetchall()
            cur.close()
            return result
        else:
            return json.dumps({"error": "Unable to connect to DB."})

    def get_users_by_id(self, id: int):
        if self.dbCon is not None:
            cur = self.dbCon.cursor()
            cur.execute("Select * from Users where id = %d;" % id)
            result = cur.fetchall()
            cur.close()
            return result
        else:
            return json.dumps({"error": "Unable to connect to DB."})

    def __delete__(self, instance):
        if self.dbCon is not None:
            self.dbCon.close()


queryManager = QueryManager()
