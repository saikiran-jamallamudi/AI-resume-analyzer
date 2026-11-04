import unittest

from app import create_app


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_analyze_json(self):
        response = self.client.post("/api/analyze", json={
            "resume_text": (
                "Python developer with Flask REST APIs, MySQL and Git experience "
                "building backend services and testing application features."
            ),
            "job_description": (
                "Hiring a Python developer with Flask, PostgreSQL, Docker and "
                "REST APIs to build and maintain backend services."
            ),
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("match_score", response.get_json())

    def test_validation_error(self):
        response = self.client.post("/api/analyze", json={
            "resume_text": "short",
            "job_description": "short",
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_report_download(self):
        response = self.client.post("/api/report", json={"match_score": 67})
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response.headers.get("Content-Disposition", ""))


if __name__ == "__main__":
    unittest.main()
