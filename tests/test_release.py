# -*- coding: utf-8 -*-
"""판·목록·자동 새 판 확인·법령 연결 묻기 시험 (표준 라이브러리만, 네트워크 없음)."""
import hashlib
import os
import re
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINE = re.compile(r"^([0-9a-f]{64})  ([0-9a-f]{64})  (\S+)  (.+)$")
CONFIG = {
    "repo": "lbiz-partners/vat-skills",
    "dir": "vat-skills",
    "rules": {"vat-rules.md": "부가세챙김이 업무 규칙", "vat-start.md": "부가세챙김이 시작하기",
              "vat-table.md": "부가세챙김이 기준표"},
    "skills_with_marker": ["vat-rules.md", "vat-start.md"],
    "start": "vat-start.md",
    "rules_file": "vat-rules.md",
}


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def body_sha(text):
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    return sha(text[m.end():].strip().encode("utf-8"))


class ReleaseTests(unittest.TestCase):
    def version(self):
        return read("VERSION").strip()

    def test_r1_version_format_and_manifest_label(self):
        v = self.version()
        self.assertRegex(v, r"^\d+\.\d+$")
        manifest = read("MANIFEST.txt")
        self.assertIn("# 판: v" + v + "\n", manifest)
        self.assertIn("(v" + v + ")", manifest.splitlines()[0])

    def test_r2_manifest_lines_match_rule_files(self):
        found = {}
        for line in read("MANIFEST.txt").splitlines():
            m = LINE.match(line)
            if m:
                found[m.group(3)] = m.groups()
        self.assertEqual(set(found), set(CONFIG["rules"]))
        for name, skill in CONFIG["rules"].items():
            text = read(name)
            fh, bh, _, listed = found[name]
            self.assertEqual(fh, sha(text.encode("utf-8")), name)
            self.assertEqual(bh, body_sha(text), name)
            self.assertEqual(listed, skill, name)

    def test_r3_sha256sums_checks_all_files(self):
        listed = {}
        for line in read("SHA256SUMS").splitlines():
            h, name = line.split("  ", 1)
            listed[name] = h
            with open(os.path.join(ROOT, name), "rb") as f:
                self.assertEqual(h, sha(f.read()), name)
        for must in ["MANIFEST.txt", "VERSION"] + list(CONFIG["rules"]) + CONFIG.get("extra_files", []):
            self.assertIn(must, listed)
        if os.path.isdir(os.path.join(ROOT, ".git")):
            tracked = subprocess.run(["git", "-C", ROOT, "ls-files", "--cached", "--others", "--exclude-standard"],
                                     capture_output=True, text=True).stdout.split()
            tracked = {t for t in tracked if t != "SHA256SUMS"}
            self.assertEqual(tracked, set(listed))

    def test_r4_skill_version_marker(self):
        marker = "이 스킬 판: v" + self.version()
        for name in CONFIG["skills_with_marker"]:
            self.assertIn(marker, read(name), name)

    def test_r5_daily_update_section(self):
        start = read(CONFIG["start"])
        sec = start[start.index("## 도구·규칙 파일 새 판 확인"):]
        for bit in (
            "REPO=" + CONFIG["repo"],
            'D="$HOME/' + CONFIG["dir"] + '"',
            "releases/latest",
            "sort -V | tail -1",
            "sha256sum -c --quiet SHA256SUMS",
            "python3 -m unittest discover -s tests",
            "carry_user_data",
            "git ls-files --others",
            ".last_check|.current_tag|*__pycache__*",
            '[ -e "$2/$f" ] && continue',
            '"$D.prev"',
            "git -C \"$D\" describe --tags --exact-match",
            '"v$(cat "$D/VERSION")"',
            '[ "$LATEST" != "$CURRENT" ] && [ "$NEWEST" = "$LATEST" ]',
            "하나라도 실패",
            "폴더의 새 판 규칙 파일 쓰기",
            "MANIFEST.txt",
        ):
            self.assertIn(bit, sec, bit)
        # 같은 판이면 바꾸지 않는다, 실패하면 쓰던 판 유지
        self.assertIn("같은 판·낮은 판·태그 못 읽음", sec)
        self.assertIn("실패 → 쓰던 판 유지", sec)
        self.assertNotIn("rm -rf \"$D\"\n", sec)

    def test_r6_law_step_asks_once(self):
        rules = read(CONFIG["rules_file"])
        sec = rules[rules.index("## 공개 법령 서버 연결 (처음 한 번만 묻기)"):]
        sec = sec[:sec.find("\n## ", 3)]
        for bit in (
            "GetMcpServerStatus", "`korean-law`나 `gomdori-law`", "connected면 그대로 쓴다",
            "`AuthenticateMcpServer`를 한 번만", "법령 조회 연결 물어봄:",
            "「예」면 `AddMcpServer`로 이름 `gomdori-law`, 주소 `https://mcp.gomdori.app/law` 하나만 추가한다",
            "「아니요」거나, 추가가 안 되거나", "주인이 아닌 사람의 「예」로는 연결하지 않는다",
            "묻지 않고 연결하지 않는다",
        ):
            self.assertIn(bit, sec, bit)

    def test_r7_version_stamp_rule(self):
        rules = read(CONFIG["rules_file"])
        sec = rules[rules.index("## 판 표시"):]
        sec = sec[:sec.find("\n## ", 3)]
        self.assertIn("「도구 판 vX.Y」", sec)
        self.assertIn(".current_tag", sec)


class VatRuleTests(unittest.TestCase):
    def test_v1_table_unchanged_since_v6_3(self):
        """기준표(숫자·법령)는 이번 판에서 바꾸지 않는다."""
        with open(os.path.join(ROOT, "vat-table.md"), "rb") as f:
            self.assertEqual(sha(f.read()), "1e15fcc2aea129b78f0cb8387971dd8839ff0006fbcd8b48798b4c0879a05076")

    def test_v2_law_notice_skipped_when_connected_or_asked(self):
        start = read("vat-start.md")
        self.assertIn("법령 조회 연결이 이미 connected이거나, 이 대화에서 업무 규칙 「처음 한 번 묻기」의 질문을 보냈으면 이 안내는 넣지 않는다.", start)
