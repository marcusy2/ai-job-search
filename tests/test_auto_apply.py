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

    def test_unconfirmed_after_retry_stays_done(self):
        link = "https://job-boards.greenhouse.io/muonspace/jobs/2"
        values = self.log(["", "", "", "", "Muon Space", "Thermal Engineering Intern (Summer 2027)", "", link, ""])
        hist = [["Date"],
                ["d", "2", "", "", link, "Needs Manual Review", "addr", "dry-run"],
                ["d", "2", "", "", link, "Retry", "", ""],
                ["d", "2", "", "", link, "Dry run - ready to submit", "", "dry-run"],
                ["d", "2", "", "", link, "Unconfirmed submit - check email", "", "live"]]
        self.assertEqual(aa.build_queue(values, hist, 10, self.repo)["forms"], [])

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


    def test_bare_link_row_skipped_not_manual(self):
        values = self.log(["", "", "", "", "", "", "", "https://researchpark.illinois.edu/job/x/", ""])
        q = aa.build_queue(values, [], 10, self.repo)
        self.assertEqual((q["forms"], q["manual"]), ([], []))
        self.assertEqual(q["portal_skipped"][0]["ats"], "incomplete-log-row")


    def test_company_cap_counts_applied_and_this_run(self):
        thermal = "Thermal Engineering Intern (Summer 2027)"
        values = self.log(
            ["", "11/25", "", "", "Muon Space", "A", "applied", "https://job-boards.greenhouse.io/m/jobs/9", ""],
            ["", "", "", "", "Muon Space", "B", "rejected", "https://job-boards.greenhouse.io/m/jobs/8", ""],
            ["", "", "", "", "Muon Space", thermal, "", "https://job-boards.greenhouse.io/m/jobs/1", ""],
            ["", "", "", "", "Muon Space", thermal, "", "https://job-boards.greenhouse.io/m/jobs/2", ""],
        )
        q = aa.build_queue(values, [], 10, self.repo, company_cap=3)
        self.assertEqual([f["row"] for f in q["forms"]], [4])
        self.assertEqual([f["row"] for f in q["over_company_cap"]], [5])
        self.assertEqual(len(aa.build_queue(values, [], 10, self.repo)["forms"]), 2)  # no cap

    def test_grace_gong_gate(self):
        companies = [["Company", "Source", "What", "Loc", "Sector", "Fit", "Outside aerospace?", "Conn"],
                     ["Muon Space", "Grace Gong list", "", "", "Aerospace", "A: hands-on hardware", "No", ""],
                     ["Vast", "LRI list + Grace Gong", "", "", "Aerospace", "A: hands-on hardware", "No", ""]]
        values = self.log(
            ["", "", "", "", "Muon Space", "Thermal Engineering Intern (Summer 2027)", "", "https://job-boards.greenhouse.io/m/jobs/1", ""],
            ["", "", "", "", "Vast", "Emerging Talent - Manufacturing Engineering Internship", "", "https://boards.greenhouse.io/vast/jobs/1", ""],
        )
        q = aa.build_queue(values, [], 10, self.repo, companies_values=companies)
        self.assertEqual([p["company"] for p in q["personal"]], ["Muon Space"])
        self.assertEqual([f["company"] for f in q["forms"]], ["Vast"])
        companies[1][6] = "Yes"
        q = aa.build_queue(values, [], 10, self.repo, companies_values=companies)
        self.assertEqual(q["personal"], [])


class CompanyTest(unittest.TestCase):
    def test_keys(self):
        k = aa.company_key
        self.assertEqual(k("General Dynamics Mission Systems"), k("General Dynamics OTS"))
        self.assertEqual(k("RTX (Collins)"), k("Collins Aerospace (RTX)"))
        self.assertNotEqual(k("RTX (Collins)"), k("RTX (Raytheon)"))
        self.assertEqual(k("K2 Space Corporation"), k("K2 Space"))
        self.assertTrue(aa.same_company(k("varda"), k("Varda Space Industries")))
        self.assertTrue(aa.same_company(k("Northrop"), k("Northrop Grumman")))
        self.assertFalse(aa.same_company(k("GE"), k("General Atomics")))

    def test_cap_postings(self):
        log = [HEADER,
               ["", "11/1", "", "", "Relativity Space", "x", "applied", "", ""],
               ["", "11/1", "", "", "Relativity Space", "y", "applied", "", ""],
               ["", "11/1", "", "", "CesiumAstro", "z", "applied", "", ""]]
        post = [["Tier"]] + [["A", "70", c, r, "", "", "", "", "", "", ""] for c, r in [
            ("Relativity Space", "1"), ("CesiumAstro", "2"), ("CesiumAstro", "3"), ("CesiumAstro", "4"),
            ("Freeform", "5"), ("Freeform", "6"), ("Freeform", "7"), ("Freeform", "8")]]
        post[5][10] = "Yes"  # Freeform role 5 already in Log
        out = aa.cap_postings(post, log)
        self.assertEqual([r["role"] for r in out["keep"]], ["2", "3", "6", "7", "8"])
        self.assertIn("already applied to 2", out["drop"][0]["reason"])


class LocationTest(unittest.TestCase):
    def test_midwest(self):
        p = {"current_location": "San Mateo, CA", "midwest_location": "Champaign, IL"}
        for loc in ["Cedar Rapids, IA", "Olathe, KS", "Brecksville, OH", "Grand Rapids, MI", "Wichita, Kansas"]:
            self.assertEqual(aa.location_for(loc, p), "Champaign, IL", loc)
        for loc in ["Long Beach, CA", "San Francisco, CA", "Golden, CO", "", "Mojave, CA (in office)", "Little Rock, Arkansas"]:
            self.assertEqual(aa.location_for(loc, p), "San Mateo, CA", loc)


class HistorySlotTest(unittest.TestCase):
    def test_slot(self):
        hist = [["Date"], ["d", "1", "", "", "https://a"], ["d", "2", "", "", "https://b"]]
        self.assertEqual(aa.history_slot(hist, "https://b"), 3)
        self.assertIsNone(aa.history_slot(hist, "https://c"))


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
