import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import build  # noqa: E402


class TreeHashTest(unittest.TestCase):
    def test_ordena_pelo_texto_do_caminho_em_qualquer_so(self):
        # 'references/INDEX.md' fica entre 'ibm' e 'intercom' no sort de Path do Windows,
        # mas antes de todos no Linux; o hash tem de seguir a ordem do texto nos dois.
        files = {
            "SKILL.md": b"skill",
            "references/INDEX.md": b"index",
            "references/ibm/DESIGN.md": b"ibm",
            "references/intercom/DESIGN.md": b"intercom",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel, data in files.items():
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_bytes(data)
            expected = hashlib.sha256()
            for rel in sorted(files):
                expected.update(rel.encode() + b"\0" + files[rel] + b"\0")
            self.assertEqual(build.tree_hash(root), expected.hexdigest())


class NextVersionTest(unittest.TestCase):
    def test_mesmo_dia_sobe_o_patch(self):
        self.assertEqual(build.next_version("1.20261012.2", "20261012"), "1.20261012.3")

    def test_dia_novo_zera_o_patch(self):
        self.assertEqual(build.next_version("1.20261012.2", "20261013"), "1.20261013.0")

    def test_versao_inicial(self):
        self.assertEqual(build.next_version("1.0.0", "20261012"), "1.20261012.0")


class DescribeUnlistedTest(unittest.TestCase):
    def test_corta_descricao_longa_na_palavra(self):
        text = '# Design System Inspired by Slack\ndescription: "' + "palavra " * 40 + 'fim."\n'
        name, desc = build.describe_unlisted(text, "slack")
        self.assertEqual(name, "Slack")
        self.assertTrue(desc.endswith("palavra…"))
        self.assertLessEqual(len(desc), 161)

    def test_sem_titulo_usa_o_slug(self):
        name, desc = build.describe_unlisted("sem cabeçalho", "bmw-m")
        self.assertEqual(name, "Bmw M")
        self.assertIn("Sem descrição", desc)


if __name__ == "__main__":
    unittest.main()
