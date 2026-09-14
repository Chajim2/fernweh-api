import pytest
import asyncio

async def post_n_async(auth_client, n=20):
    tasks = [
        auth_client.post("/entries/", json={"text": "some text", "title": f"some title {i}"})
        for i in range(n)
    ]

    await asyncio.gather(*tasks)

async def post_n(auth_client, n=20):
    for _ in range(n):
        resp = await auth_client.post("/entries/", json={"text":"some text", "title":"some title"})
        # ADD THIS: It will instantly crash the test if creation fails
        assert resp.status_code in (200, 201), f"Post failed: {resp.text}"

@pytest.mark.asyncio
async def test_feed_pagination_has_more(auth_client):

    await post_n(auth_client, 15)

    resp = await auth_client.get("/entries/feed", params={"fetched_so_far": 0, "fetch_count": 20})
    data = resp.json()

    print(data)
    print(data["items"])
    assert len(data["items"]) == 15 
    assert not data["has_more"]

    await post_n(auth_client, 67)

    resp = await auth_client.get("/entries/feed", params={"fetched_so_far": 0, "fetch_count": 20})
    data = resp.json()
    assert len(data["items"]) == 20
    assert data["has_more"]
