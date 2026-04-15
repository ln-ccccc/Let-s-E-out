def _auth_headers(client, phone: str) -> dict[str, str]:
    r = client.post("/api/v1/auth/verify-otp", json={"phone": phone, "code": "000000"})
    assert r.status_code == 200, r.text
    token = r.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}


def test_mvp_happy_path(app_client):
    h = _auth_headers(app_client, "13300000000")

    r = app_client.get("/api/v1/me", headers=h)
    assert r.status_code == 200

    r = app_client.post(
        "/api/v1/places",
        json={"name": "测试店", "city": "武汉", "area": "洪山区"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    place_id = r.json()["id"]

    r = app_client.post(
        "/api/v1/visits",
        json={
            "placeId": place_id,
            "dayPart": "dinner",
            "publishStatus": "private",
            "highlights": "好吃",
            "pitfalls": "略贵",
            "revisitIntent": "maybe",
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    visit_id = r.json()["id"]

    r = app_client.get("/api/v1/visits/mine", headers=h)
    assert r.status_code == 200
    assert any(x["id"] == visit_id for x in r.json()["items"])

    r = app_client.post("/api/v1/favorites", json={"visitId": visit_id}, headers=h)
    assert r.status_code == 404

    r = app_client.patch(
        f"/api/v1/visits/{visit_id}",
        json={"publishStatus": "public"},
        headers=h,
    )
    assert r.status_code == 200

    r = app_client.get("/api/v1/public/visits", headers=h)
    assert r.status_code == 200
    assert any(x["id"] == visit_id for x in r.json()["items"])

    r = app_client.post("/api/v1/favorites", json={"visitId": visit_id}, headers=h)
    assert r.status_code == 201, r.text

    r = app_client.get("/api/v1/favorites", headers=h)
    assert r.status_code == 200
    assert any(x["id"] == visit_id for x in r.json()["items"])

    r = app_client.post(
        "/api/v1/reports",
        json={"targetType": "visit", "targetId": visit_id, "reason": "other"},
        headers=h,
    )
    assert r.status_code == 201

    r = app_client.post(
        "/api/v1/feedbacks",
        json={"type": "suggestion", "message": "不错"},
        headers=h,
    )
    assert r.status_code == 201


def test_admin_can_list_reports_and_feedbacks(app_client):
    h = _auth_headers(app_client, "13300000001")

    from app.db.session import SessionLocal
    from app.models.user import User
    from sqlalchemy import select

    with SessionLocal() as db:
        u = db.scalar(select(User).where(User.phone == "13300000001"))
        u.role = "admin"
        db.add(u)
        db.commit()

    r = app_client.get("/api/v1/admin/reports", headers=h)
    assert r.status_code == 200

    r = app_client.get("/api/v1/admin/feedbacks", headers=h)
    assert r.status_code == 200
