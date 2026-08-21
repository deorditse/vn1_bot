import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.api.api import app
from app.api.dependencies.gateway_auth import require_gateway_user
from app.api.dependencies.rate_limiting import limiter
from domain.auth import User


class GenerateDescriptionApiTests(unittest.TestCase):
    def setUp(self) -> None:
        limiter.reset()
        app.dependency_overrides[require_gateway_user] = lambda: User(
            id="test-user",
            username="test",
        )
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    @patch("app.api.routers.generate.DescriptionGenerationUseCase")
    def test_accepts_json_and_returns_xlsx_attachment(self, use_case_class):
        use_case_class.return_value.execute_request = AsyncMock(return_value=b"xlsx-data")

        response = self.client.post(
            "/generate-description",
            json={"id": "72128", "raw_description": "raw markup"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"xlsx-data")
        self.assertEqual(
            response.headers["content-type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn("attachment", response.headers["content-disposition"])
        use_case_class.return_value.execute_request.assert_awaited_once()

    @patch("app.api.routers.generate.DescriptionGenerationUseCase")
    def test_returns_generation_report_headers(self, use_case_class):
        use_case_class.return_value.execute_request_with_report = AsyncMock(
            return_value=SimpleNamespace(
                content=b"xlsx-data",
                total_rows=10,
                error_rows=2,
                success_rows=8,
            )
        )

        response = self.client.post(
            "/generate-description",
            json={"id": "72128", "raw_description": "raw markup"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["x-vn1-total-rows"], "10")
        self.assertEqual(response.headers["x-vn1-error-rows"], "2")
        self.assertEqual(response.headers["x-vn1-success-rows"], "8")
        use_case_class.return_value.execute_request_with_report.assert_awaited_once()

    @patch("app.api.routers.generate.DescriptionGenerationUseCase")
    def test_accepts_spreadsheet_upload(self, use_case_class):
        use_case_class.return_value.execute_request = AsyncMock(return_value=b"xlsx-data")

        response = self.client.post(
            "/generate-description",
            files={
                "file": (
                    "input.xlsx",
                    b"source-data",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )

        self.assertEqual(response.status_code, 200)
        use_case_class.return_value.execute_request.assert_awaited_once()

    def test_rejects_unsupported_content_type(self):
        response = self.client.post(
            "/generate-description",
            content=b"raw",
            headers={"content-type": "text/plain"},
        )

        self.assertEqual(response.status_code, 422)

    def test_rejects_malformed_json(self):
        response = self.client.post(
            "/generate-description",
            content=b"{",
            headers={"content-type": "application/json"},
        )

        self.assertEqual(response.status_code, 422)

    def test_rejects_empty_id_and_invalid_field_types(self):
        empty_id = self.client.post(
            "/generate-description",
            json={"id": "  ", "raw_description": "raw"},
        )
        invalid_type = self.client.post(
            "/generate-description",
            json={"id": [1], "raw_description": "raw"},
        )

        self.assertEqual(empty_id.status_code, 422)
        self.assertEqual(invalid_type.status_code, 422)

    def test_rejects_file_and_text_in_same_multipart_request(self):
        response = self.client.post(
            "/generate-description",
            data={"id": "1", "raw_description": "raw"},
            files={"file": ("input.xlsx", b"source-data")},
        )

        self.assertEqual(response.status_code, 422)

    @patch("app.api.routers.generate.DescriptionGenerationUseCase")
    def test_rate_limit_returns_429_and_uses_independent_user_keys(self, use_case_class):
        use_case_class.return_value.execute_request = AsyncMock(return_value=b"xlsx-data")
        payload = {"id": "1", "raw_description": "raw"}

        responses = [
            self.client.post(
                "/generate-description",
                json=payload,
                headers={"x-vn1-user-id": "user-a"},
            )
            for _ in range(6)
        ]
        other_user_response = self.client.post(
            "/generate-description",
            json=payload,
            headers={"x-vn1-user-id": "user-b"},
        )

        self.assertEqual([response.status_code for response in responses[:5]], [200] * 5)
        self.assertEqual(responses[5].status_code, 429)
        self.assertEqual(other_user_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
