import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("utils", types.SimpleNamespace(process_images=lambda *args: None))
import server
from fastapi.testclient import TestClient


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_dir = server.TASKS_DIR
        server.TASKS_DIR = Path(self.tmp.name)
        self.client = TestClient(server.app)

    def tearDown(self):
        server.TASKS_DIR = self.old_dir
        self.tmp.cleanup()

    def test_processing_status_and_download(self):
        def fake_process(workdir, paths):
            self.assertEqual(Path(paths[0]).name, "0000.jpg")
            output = Path(workdir) / "output"
            output.mkdir()
            (output / "livro_OCR.txt").write_text("exemplo", encoding="utf-8")
        with patch.object(server, "process_images", fake_process):
            response = self.client.post("/process/", files={"files": ("../../foto.jpg", b"image", "image/jpeg")})
        self.assertEqual(response.status_code, 200)
        task_id = response.json()["task_id"]
        self.assertEqual(self.client.get(f"/status/{task_id}").json()["status"], "completed")
        self.assertEqual(self.client.get(f"/download/{task_id}/txt").text, "exemplo")

    def test_failed_processing_is_visible(self):
        with patch.object(server, "process_images", side_effect=ValueError("bad image")):
            response = self.client.post("/process/", files={"files": ("foto.jpg", b"bad", "image/jpeg")})
        self.assertEqual(self.client.get(f"/status/{response.json()['task_id']}").json()["status"], "failed")

    def test_rejects_unsupported_format_and_invalid_identifier(self):
        self.assertEqual(self.client.post("/process/", files={"files": ("x.pdf", b"pdf", "application/pdf")}).status_code, 400)
        self.assertEqual(self.client.get("/status/not-a-uuid").status_code, 400)
        self.assertEqual(list(server.TASKS_DIR.iterdir()), [])

    def test_rejects_oversize_upload_and_cleans_task(self):
        with patch.object(server, "MAX_FILE_BYTES", 3):
            response = self.client.post("/process/", files={"files": ("x.jpg", b"1234", "image/jpeg")})
        self.assertEqual(response.status_code, 413)
        self.assertEqual(list(server.TASKS_DIR.iterdir()), [])


if __name__ == "__main__":
    unittest.main()

