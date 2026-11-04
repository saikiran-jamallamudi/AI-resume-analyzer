import unittest

from app.analyzer import analyze_resume, extract_skills


class AnalyzerTests(unittest.TestCase):
    def test_extracts_expected_skills(self):
        text = "Built APIs using Python, Flask, PostgreSQL and Docker."
        self.assertEqual(
            extract_skills(text),
            ["Python", "PostgreSQL", "Flask", "Docker"]
        )

    def test_analyze_returns_gaps_and_match(self):
        resume = (
            "Python developer building Flask REST APIs with MySQL and Git. "
            "Created and tested backend services for an internal application."
        )
        job = (
            "Looking for a Python developer with Flask, PostgreSQL, Docker and "
            "REST APIs. Experience building backend services is preferred."
        )
        result = analyze_resume(resume, job)
        self.assertIn("Python", result["matched_skills"])
        self.assertIn("PostgreSQL", result["missing_skills"])
        self.assertIn("Docker", result["missing_skills"])
        self.assertGreaterEqual(result["match_score"], 0)
        self.assertLessEqual(result["match_score"], 100)
        self.assertTrue(result["recommendations"])

    def test_rejects_short_inputs(self):
        with self.assertRaises(ValueError):
            analyze_resume("too short", "This job description is long enough to pass validation.")


if __name__ == "__main__":
    unittest.main()
