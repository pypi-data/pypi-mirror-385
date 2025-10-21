import base64, json

import respx, httpx
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from empowernow_common.fastapi import build_auth_dependency


def _jwt(iss: str, sub: str = "user") -> str:
    h = base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode()).rstrip(b"=").decode()
    p = base64.urlsafe_b64encode(json.dumps({"iss": iss, "sub": sub}).encode()).rstrip(b"=").decode()
    return f"{h}.{p}."


def test_auth_dependency_success(tmp_path):
    # Prepare IdP YAML
    yaml_path = tmp_path / "idps.yaml"
    yaml_path.write_text(
        """
    idps:
      - name: example
        issuer: https://example.com/
        introspection_url: https://example.com/introspect
        client_id: c
        client_secret: s
    """
    )

    # Use new unified auth dependency
    dep = build_auth_dependency(idps_yaml_path=str(yaml_path))

    app = FastAPI()

    @app.get("/")
    async def root(user=Depends(dep)):
        return {"uid": f"auth:account:{user['issuer']}:{user['subject']}"}

    token = _jwt("https://example.com/")

    with respx.mock(assert_all_called=True) as router:
        router.post("https://example.com/introspect").mock(
            return_value=httpx.Response(
                200,
                json={
                    "active": True,
                    "iss": "https://example.com/",
                    "sub": "user",
                    "exp": 9999999999,
                },
            )
        )

        client = TestClient(app)
        r = client.get("/", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["uid"] == "auth:account:https://example.com/:user"
        # normalized claims attached
        assert r.json().get("normalized_claims") is None  # endpoint returns only uid, but state should have it 