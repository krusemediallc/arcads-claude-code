import importlib.util
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "nano-banana-image-ad"
    / "scripts"
    / "generate_image.py"
)
SPEC = importlib.util.spec_from_file_location("nano_banana_generate_image", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class AtlasProviderTests(unittest.TestCase):
    def test_model_route_depends_on_whether_images_are_present(self):
        self.assertEqual(
            MODULE.atlas_model("nano-banana-2", False),
            "google/nano-banana-2/text-to-image",
        )
        self.assertEqual(
            MODULE.atlas_model("nano-banana-pro", True),
            "google/nano-banana-pro/edit",
        )

    def test_submit_posts_once_with_live_schema_fields(self):
        with mock.patch.object(MODULE, "http_post_json") as post:
            post.return_value = {"code": 200, "data": {"id": "prediction-1"}}
            prediction_id = MODULE.atlas_submit(
                "product photo",
                "nano-banana-2",
                "1:1",
                ["https://files.example/reference.png"],
                "https://api.example/api/v1",
                "Bearer test",
            )

        self.assertEqual(prediction_id, "prediction-1")
        post.assert_called_once()
        url, _headers, body = post.call_args.args[:3]
        self.assertEqual(url, "https://api.example/api/v1/model/generateImage")
        self.assertEqual(body["model"], "google/nano-banana-2/edit")
        self.assertEqual(body["images"], ["https://files.example/reference.png"])
        self.assertEqual(body["aspect_ratio"], "1:1")
        self.assertEqual(body["resolution"], "1k")
        self.assertEqual(body["output_format"], "png")

    def test_prediction_get_retries_only_transient_failures(self):
        transient = urllib.error.URLError("temporary")
        with mock.patch.object(
            MODULE.urllib.request,
            "urlopen",
            side_effect=[transient, FakeResponse({"code": 200, "data": {"status": "completed"}})],
        ) as urlopen, mock.patch.object(MODULE.time, "sleep") as sleep:
            result = MODULE.atlas_get_prediction(
                "prediction/with slash",
                "https://api.example/api/v1",
                "Bearer test",
            )

        self.assertEqual(result, {"status": "completed"})
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(1)
        request = urlopen.call_args_list[0].args[0]
        self.assertTrue(request.full_url.endswith("/prediction/prediction%2Fwith%20slash"))

    def test_generate_one_uses_atlas_path_without_arcads_calls(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            MODULE, "atlas_submit", return_value="prediction-1"
        ) as atlas_submit, mock.patch.object(
            MODULE, "atlas_poll", return_value="https://files.example/output.png"
        ), mock.patch.object(MODULE, "http_download") as download, mock.patch.object(
            MODULE, "probe_dimensions", return_value=(1024, 1024)
        ), mock.patch.object(MODULE, "submit") as arcads_submit:
            result = MODULE.generate_one(
                1,
                "product photo",
                "nano-banana-2",
                "image",
                "1:1",
                None,
                [],
                Path(tmp),
                "product-photo",
                "20260901T000000Z",
                "https://api.example/api/v1",
                "Bearer test",
                None,
                None,
                False,
                False,
                provider="atlas",
            )

        atlas_submit.assert_called_once()
        arcads_submit.assert_not_called()
        download.assert_called_once()
        self.assertEqual(result["provider"], "atlas")
        self.assertEqual(result["asset_id"], "prediction-1")

    def test_default_generate_one_path_remains_arcads(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            MODULE, "submit", return_value="asset-1"
        ) as arcads_submit, mock.patch.object(
            MODULE, "poll", return_value="https://files.example/output.png"
        ), mock.patch.object(MODULE, "http_download"), mock.patch.object(
            MODULE, "probe_dimensions", return_value=(1024, 1024)
        ), mock.patch.object(MODULE, "atlas_submit") as atlas_submit:
            result = MODULE.generate_one(
                1,
                "product photo",
                "nano-banana-2",
                "image",
                "1:1",
                None,
                [],
                Path(tmp),
                "product-photo",
                "20260901T000000Z",
                "https://arcads.example",
                "Basic test",
                "product-1",
                None,
                False,
                False,
            )

        arcads_submit.assert_called_once()
        atlas_submit.assert_not_called()
        self.assertEqual(result["provider"], "arcads")


if __name__ == "__main__":
    unittest.main()
