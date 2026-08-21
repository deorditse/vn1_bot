import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi.responses import Response
from fastapi.testclient import TestClient

from app.api.api import app
from app.api.dependencies.auth import require_auth


class GenerateDescriptionGatewayTests(unittest.TestCase):
    def setUp(self) -> None:
        app.dependency_overrides[require_auth] = lambda: SimpleNamespace(
            id="test-user",
            username="test",
            role="vn1-user",
            roles=["vn1-user"],
            email=None,
            access_token=None,
        )
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    @patch("app.api.routers.generator.ProxyGeneratorUseCase")
    def test_proxies_generate_description_to_generator(self, use_case_class):
        use_case_class.return_value.execute = AsyncMock(
            return_value=Response(
                content=b"xlsx-data",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        )

        response = self.client.post(
            "/generate-description",
            json={"id": "72128", "raw_description": "raw"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"xlsx-data")
        call = use_case_class.return_value.execute.await_args
        self.assertEqual(call.kwargs["path"], "generate-description")
        self.assertEqual(call.kwargs["current_user"].id, "test-user")


if __name__ == "__main__":
    unittest.main()
