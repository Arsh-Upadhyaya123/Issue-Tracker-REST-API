import os
import tempfile
from pathlib import Path
import unittest
from fastapi.testclient import TestClient
import app


class IssueAPITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        app.DB_PATH = Path(self.temp.name) / 'test.db'
        app.init_db()
        self.client = TestClient(app.app)

    def tearDown(self):
        self.client.close()
        self.temp.cleanup()

    def test_create_filter_update_delete(self):
        created = self.client.post('/issues', json={'title': 'Fix login', 'priority': 'high'})
        self.assertEqual(created.status_code, 201)
        issue_id = created.json()['id']
        self.assertEqual(len(self.client.get('/issues?priority=high').json()), 1)
        edited = self.client.patch(f'/issues/{issue_id}', json={'status': 'done'})
        self.assertEqual(edited.json()['status'], 'done')
        self.assertEqual(self.client.delete(f'/issues/{issue_id}').status_code, 204)
        self.assertEqual(self.client.get(f'/issues/{issue_id}').status_code, 404)

    def test_validation(self):
        self.assertEqual(self.client.post('/issues', json={'title': ''}).status_code, 422)
        self.assertEqual(self.client.get('/issues?limit=1000').status_code, 422)


if __name__ == '__main__':
    unittest.main()
