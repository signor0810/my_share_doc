import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from scan_secrets import scan_text  # noqa: E402


def cats(text):
    return {c for _, c, _ in scan_text(text)}


class ScanTests(unittest.TestCase):
    def test_clean_html(self):
        self.assertEqual(scan_text("<html><title>Hi</title><p>version 1.2.3.4 ok</p></html>"), [])

    def test_github_token(self):
        self.assertIn("github-token", cats("t = ghp_" + "a" * 36))

    def test_sk_key(self):
        self.assertIn("sk-api-key", cats("sk-" + "a1B2" * 6))

    def test_private_key(self):
        self.assertIn("private-key", cats("-----BEGIN RSA PRIVATE KEY-----"))

    def test_credential_assignment(self):
        self.assertIn("credential-assignment", cats('password = "hunter2hunter2"'))
        self.assertIn("credential-assignment", cats('"api_key": "abcd1234efgh"'))

    def test_email(self):
        self.assertIn("email", cats("contact me@gmail.com"))
        self.assertEqual(scan_text("a@example.com"), [])

    def test_internal_ips(self):
        for ip in ("10.0.0.5", "192.168.1.20", "172.16.3.4", "100.64.1.1"):
            self.assertIn("internal-ip", cats("host " + ip), ip)
        for ip in ("8.8.8.8", "172.32.0.1", "100.128.0.1", "110.0.0.5", "1.10.0.0.5"):
            self.assertNotIn("internal-ip", cats("host " + ip), ip)

    def test_masking(self):
        (_, _, hit), = [f for f in scan_text("ghp_" + "z" * 36)]
        self.assertNotIn("zzzzzzzz", hit)


if __name__ == "__main__":
    unittest.main()
