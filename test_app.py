import unittest
import os
import sqlite3
from app import app, init_db, get_db
class FlaskAppTestCase(unittest.TestCase):
   
    def setUp(self):

        # 1. Use test database
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test"
        app.config["DATABASE"] = "test.db"

        # 2. Delete old DB BEFORE anything opens it
        if os.path.exists("test.db"):
            os.remove("test.db")

        # 3. Now build fresh schema
        init_db()

        # 4. Create test client
        self.client = app.test_client()

        
    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        #this tests if the text exists in your page so we know it loaded
        self.assertIn(b"Check out some home energy solutions", response.data)

    def tearDown(self):
        if os.path.exists("test.db"):
            os.remove("test.db")


if __name__ == "__main__":
    unittest.main()