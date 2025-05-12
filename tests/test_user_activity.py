def test_create_activity(client, db_session):
    from app.models.product import Product

    # Create dummy product
    product = Product(
        title="Test Product",
        description="Test Desc",
        price=10.0,
        stock=5,
        imageUrl="test.jpg",
        category_id=1
    )
    db_session.add(product)
    db_session.commit()

    payload = {
        "user_id": None,
        "product_id": product.id,
        "action": "view"
    }

    response = client.post(
        "/activities/",
        json=payload,
        cookies={"guest_session_id": "test-session-123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product.id
    assert data["action"] == "view"

def test_get_top_viewed_book_details(client):
    response = client.get("/activities/top-viewed-details")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
