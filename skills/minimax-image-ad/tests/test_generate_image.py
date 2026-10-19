from __future__ import annotations

import argparse
import base64
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "scripts" / "generate_image.py"
SPEC = importlib.util.spec_from_file_location("minimax_generate_image", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class GenerateImageTests(unittest.TestCase):
    def test_regional_endpoints_are_complete(self) -> None:
        self.assertEqual(
            MODULE.REGIONAL_ENDPOINTS,
            {
                "global_en": "https://api.minimax.io/v1/image_generation",
                "cn_zh": "https://api.minimaxi.com/v1/image_generation",
            },
        )

    def test_build_payload_includes_requested_fields_only(self) -> None:
        args = argparse.Namespace(
            model="image-01",
            prompt="A studio product photograph",
            response_format="url",
            n=2,
            aspect_ratio="1:1",
            width=None,
            height=None,
            seed=42,
            prompt_optimizer=False,
        )
        self.assertEqual(
            MODULE.build_payload(args),
            {
                "model": "image-01",
                "prompt": "A studio product photograph",
                "response_format": "url",
                "n": 2,
                "aspect_ratio": "1:1",
                "seed": 42,
                "prompt_optimizer": False,
            },
        )

    def test_response_images_reads_counts(self) -> None:
        images, counts = MODULE.response_images(
            {
                "data": {"image_urls": ["https://example.test/image.png"]},
                "metadata": {"success_count": 1, "failed_count": 0},
                "base_resp": {"status_code": 0},
            }
        )
        self.assertEqual(images, ["https://example.test/image.png"])
        self.assertEqual(counts, {"success_count": 1, "failed_count": 0})

    def test_response_images_rejects_api_error(self) -> None:
        with self.assertRaisesRegex(MODULE.MiniMaxAPIError, "API error 1001"):
            MODULE.response_images(
                {"base_resp": {"status_code": 1001, "status_msg": "invalid request"}}
            )

    def test_save_image_decodes_base64(self) -> None:
        encoded = base64.b64encode(b"image bytes").decode("ascii")
        with tempfile.TemporaryDirectory() as directory:
            path = MODULE.save_image(encoded, "base64", Path(directory) / "result")
            self.assertEqual(path.suffix, ".png")
            self.assertEqual(path.read_bytes(), b"image bytes")

    def test_post_generation_uses_bearer_auth(self) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b'{"data":{"image_urls":["x"]}}'
        with mock.patch.object(MODULE.urllib.request, "urlopen", return_value=response) as urlopen:
            MODULE.post_generation(
                MODULE.REGIONAL_ENDPOINTS["global_en"],
                "test-key",
                {"model": "image-01", "prompt": "test"},
            )
        request = urlopen.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")


if __name__ == "__main__":
    unittest.main()
