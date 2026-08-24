import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.api import app
from app.api.routers.auth import AUTH_ACCESS_COOKIE, AUTH_REFRESH_COOKIE


class LogoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.client.cookies.set(
            AUTH_ACCESS_COOKIE,
            "access-token",
            domain="testserver.local",
            path="/",
        )
        self.client.cookies.set(
            AUTH_REFRESH_COOKIE,
            "refresh-token",
            domain="testserver.local",
            path="/",
        )

    @patch("app.api.routers.auth.KeycloakAuthProvider.logout", new_callable=AsyncMock)
    def test_clears_cookies_when_keycloak_logout_fails(self, keycloak_logout: AsyncMock) -> None:
        keycloak_logout.side_effect = HTTPException(
            status_code=503,
            detail="Keycloak is unavailable",
        )

        response = self.client.post("/v1/auth/logout")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["authenticated"])
        self.assertIsNone(self.client.cookies.get(AUTH_ACCESS_COOKIE))
        self.assertIsNone(self.client.cookies.get(AUTH_REFRESH_COOKIE))
        set_cookie_headers = response.headers.get_list("set-cookie")
        self.assertTrue(any(AUTH_ACCESS_COOKIE in header for header in set_cookie_headers))
        self.assertTrue(any(AUTH_REFRESH_COOKIE in header for header in set_cookie_headers))


if __name__ == "__main__":
    unittest.main()
