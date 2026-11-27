"""Tests for tools/auto_apply.py: portal triage, Log queue selection, CV matching, Question Bank parsing."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import auto_apply as aa  # noqa: E402

HEADER = ["due date", "date applied", "Cover Letter?", "questions?", "company", "position", "results", "website", "location"]


class TriageTest(unittest.TestCase):
    def test_auto_portals(self):
        for url, ats in [
            ("https://job-boards.greenhouse.io/muonspace/jobs/5253474007", "greenhouse"),
            ("https://boards.greenhouse.io/vast/jobs/4711403006?gh_jid=4711403006", "greenhouse"),
            ("https://jobs.lever.co/CesiumAstro/a3b0f097", "lever"),
            ("https://jobs.ashbyhq.com/bedrock-robotics/1f413f83", "ashby"),
            ("https://lunaroutpost.bamboohr.com/careers/399", "bamboohr"),
            ("https://ursamajor.com/careers/?gh_jid=4746887005", "greenhouse-embed"),
        ]:
            r = aa.triage(url)
            self.assertEqual((r["tier"], r["ats"]), ("auto", ats), url)

    def test_manual_portals(self):
        for url in [
            "https://sierraspace.wd1.myworkdayjobs.com/Sierra_Space_External_Career_Site/job/x",
            "https://careers-gdms.icims.com/jobs/74531/job",
            "https://textron.taleo.net/careersection/textron_ur/jobdetail.ftl?job=1539986",
            "https://app.ripplematch.com/t/a8770580",
            "https://www.linkedin.com/jobs/view/123",
            "https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?jobId=1",
            "https://careers.rtx.com/global/en/job/01872600",
        ]:
            self.assertEqual(aa.triage(url)["tier"], "manual", url)

    def test_lookalike_host_not_matched(self):
        self.assertEqual(aa.triage("https://notgreenhouse.io.evil.com/x")["tier"], "attempt")

    def test_unknown_career_site_is_attempt(self):
        self.assertEqual(aa.triage("https://careers.garmin.com/jobs/19754")["tier"], "attempt")


class QueueTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "cv").mkdir()
        (self.repo / "cover_letters").mkdir()
        for name in [
            "Marcus Yang Resume Muon Space - Thermal Engineering Intern (Summer 2027).pdf",
            "Marcus Yang Resume Vast - Emerging Talent - Manufacturing Engineering Internship.pdf",
            "Marcus Yang Resume Sierra Space - 2027 Summer Internship - Propulsion Engineering.pdf",
        ]:
            (self.repo / "cv" / name).write_bytes(b"%PDF")

    def tearDown(self):
        self.tmp.cleanup()

    def log(self, *rows):
        return [HEADER] + [list(r) for r in rows]

    def test_selection_rules(self):
        values = self.log(
            ["", "11/25", "", "", "Muon Space", "Spacecraft Test", "applied", "https://job-boards.greenhouse.io/muonspace/jobs/1", ""],
            ["", "", "", "", "Muon Space", "Thermal Engineering Intern (Summer 2027)", "", "https://job-boards.greenhouse.io/muonspace/jobs/2", "San Jose, CA"],
            ["", "", "", "", "Sierra Space", "2027 Summer Internship - Propulsion Engineering", "", "https://sierraspace.wd1.myworkdayjobs.com/x", ""],
            ["", "", "", "", "Bedrock Robotics", "Sensor Test", "", "https://jobs.ashbyhq.com/bedrock-robotics/1", ""],
            ["", "", "", "", "Garmin", "Aviation Systems", "rejected", "https://careers.garmin.com/jobs/1", ""],
            [],
        )
        q = aa.build_queue(values, [], 10, self.repo)
        self.assertEqual([f["row"] for f in q["forms"]], [3])
        self.assertTrue(q["forms"][0]["resume"].endswith("Thermal Engineering Intern (Summer 2027).pdf"))
        reasons = {m["company"]: m["reason"] for m in q["manual"]}
        self.assertIn("Workday", reasons["Sierra Space"])
        self.assertIn("No tailored CV", reasons["Bedrock Robotics"])
        self.assertNotIn("Garmin", reasons)

    def test_short_company_name_matches_long_file(self):
        values = self.log(["", "", "", "", "Vast", "Emerging Talent - Manufacturing Engineering Internship", "", "https://boards.greenhouse.io/vast/jobs/4711403006", ""])
        self.assertIsNotNone(aa.build_queue(values, [], 10, self.repo)["forms"][0]["resume"])

    def test_history_skips_and_retry(self):
        link = "https://job-boards.greenhouse.io/muonspace/jobs/2"
        values = self.log(["", "", "", "", "Muon Space", "Thermal Engineering Intern (Summer 2027)", "", link, ""])
        hist = [["Date"], ["2026-11-28", "3", "Muon Space", "Thermal", link, "Needs Manual Review", "CAPTCHA", "live"]]
        self.assertEqual(aa.build_queue(values, hist, 10, self.repo)["forms"], [])
        hist.append(["2026-11-29", "3", "Muon Space", "Thermal", link, "Retry", "", ""])
        self.assertEqual(len(aa.build_queue(values, hist, 10, self.repo)["forms"]), 1)
        dry = [["Date"], ["2026-11-28", "3", "", "", link, "Dry run - ready to submit", "", "dry-run"]]
        self.assertEqual(len(aa.build_queue(values, dry, 10, self.repo)["forms"]), 1)

    def test_cap_and_due_date_order(self):
        rows = [["", "", "", "", "Muon Space", "Thermal Engineering Intern (Summer 2027)", "", f"https://job-boards.greenhouse.io/m/jobs/{i}", ""] for i in range(3)]
        rows[2][0] = "12/1"
        q = aa.build_queue(self.log(*rows), [], 2, self.repo)
        self.assertEqual([f["row"] for f in q["forms"]], [4, 2])
        self.assertEqual([f["row"] for f in q["over_cap"]], [3])


    def test_auto_portals_before_career_sites(self):
        values = self.log(
            ["", "", "", "", "Muon Space", "Thermal Engineering Intern (Summer 2027)", "", "https://careers.example.com/jobs/1", ""],
            ["", "", "", "", "Muon Space", "Thermal Engineering Intern (Summer 2027)", "", "https://job-boards.greenhouse.io/m/jobs/2", ""],
        )
        self.assertEqual([f["row"] for f in aa.build_queue(values, [], 10, self.repo)["forms"]], [3, 2])


    def test_cover_letter_not_matched_across_roles(self):
        (self.repo / "cover_letters" / "Marcus Yang Cover Letter Muon Space - GNC Hardware Engineering Intern.pdf").write_bytes(b"%PDF")
        self.assertIsNone(aa.find_document("Muon Space", "Thermal Engineering Intern (Summer 2027)", self.repo / "cover_letters", "cover"))
        self.assertIsNotNone(aa.find_document("Muon Space", "GNC Hardware Engineering Intern (Summer 2027)", self.repo / "cover_letters", "cover"))

    def test_role_picks_right_sibling(self):
        for name in ["Marcus Yang Resume Vast - Mechanical Aerospace Engineering Internship.pdf",
                     "Marcus Yang Resume Bedrock Robotics - Sensor Hardware Test Engineer Intern.pdf",
                     "Marcus Yang Resume Bedrock Robotics - Hardware Engineer Intern, Machine Integration & Test.pdf"]:
            (self.repo / "cv" / name).write_bytes(b"%PDF")
        cv = self.repo / "cv"
        self.assertIn("Manufacturing", aa.find_document("Vast", "Emerging Talent - Manufacturing Engineering Internship", cv))
        self.assertIn("Mechanical Aerospace", aa.find_document("Vast", "Emerging Talent - Mechanical/Aerospace Engineering Internship", cv))
        self.assertIn("Sensor", aa.find_document("Bedrock Robotics", "2027 Internship Sensor Hardware Test Engineer", cv))
        self.assertIn("Machine Integration", aa.find_document("Bedrock Robotics", "2027 Internship Hardware Engineer, Machine Integration & Test", cv))


    def test_skip_portals_and_dry_ready(self):
        gh = "https://job-boards.greenhouse.io/muonspace/jobs/2"
        values = self.log(
            ["", "", "", "", "Sierra Space", "2027 Summer Internship - Propulsion Engineering", "", "https://sierraspace.wd1.myworkdayjobs.com/x", ""],
            ["", "", "", "", "Intuitive Machines", "AIT", "", "https://workforcenow.adp.com/x?jobId=1", ""],
            ["", "", "", "", "Muon Space", "Thermal Engineering Intern (Summer 2027)", "", gh, ""],
        )
        q = aa.build_queue(values, [], 10, self.repo, skip_portals=("workday", "adp"))
        self.assertEqual(q["manual"], [])
        self.assertEqual(len(q["portal_skipped"]), 2)
        hist = [["Date"], ["d", "4", "", "", gh, "Dry run - ready to submit", "", "dry-run"]]
        self.assertEqual(aa.build_queue(values, hist, 10, self.repo, skip_dry_ready=True)["forms"], [])
        hist.append(["d", "4", "", "", gh, "Retry", "", ""])
        self.assertEqual(len(aa.build_queue(values, hist, 10, self.repo, skip_dry_ready=True)["forms"]), 1)


class LocationTest(unittest.TestCase):
    def test_midwest(self):
        p = {"current_location": "San Mateo, CA", "midwest_location": "Champaign, IL"}
        for loc in ["Cedar Rapids, IA", "Olathe, KS", "Brecksville, OH", "Grand Rapids, MI", "Wichita, Kansas"]:
            self.assertEqual(aa.location_for(loc, p), "Champaign, IL", loc)
        for loc in ["Long Beach, CA", "San Francisco, CA", "Golden, CO", "", "Mojave, CA (in office)", "Little Rock, Arkansas"]:
            self.assertEqual(aa.location_for(loc, p), "San Mateo, CA", loc)


class QuestionBankTest(unittest.TestCase):
    def test_blocks(self):
        values = [["Q1?"], ["A1 line"], [], ["Largest programming project"], [], [], ["Q3"], ["a"], ["b"]]
        self.assertEqual(
            aa.parse_question_bank(values),
            [
                {"question": "Q1?", "answer": "A1 line"},
                {"question": "Largest programming project", "answer": ""},
                {"question": "Q3", "answer": "a\nb"},
            ],
        )


class DelaysTest(unittest.TestCase):
    def test_range(self):
        d = aa.delays(50, 45, 120, seed=1)
        self.assertTrue(all(45 <= x <= 120 for x in d))
        self.assertGreater(len(set(d)), 10)


if __name__ == "__main__":
    unittest.main()
