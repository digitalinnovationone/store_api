from typing import List
import pytest
from tests.factories import product_data
from fastapi import status


# -----------------------------
# Teste: criar produto
# -----------------------------
async def test_controller_create_should_return_success(client, products_url):
    response = await client.post(products_url, json=product_data())
    content = response.json()

    del content["created_at"]
    del content["updated_at"]
    del content["id"]

    assert response.status_code == status.HTTP_201_CREATED
    assert content == {
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": "8.500",
        "status": True,
    }


# -----------------------------
# Teste: criar produto duplicado (IntegrityError)
# -----------------------------
async def test_controller_create_duplicate_should_return_303(client, products_url, product_inserted):
    response = await client.post(products_url, json={
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": "8.500",
        "status": True
    })
    assert response.status_code == 303
    assert "Erro ao inserir produto" in response.json()["detail"]


# -----------------------------
# Teste: GET produto por ID
# -----------------------------
async def test_controller_get_should_return_success(client, products_url, product_inserted):
    response = await client.get(f"{products_url}{product_inserted.id}")
    content = response.json()

    del content["created_at"]
    del content["updated_at"]

    assert response.status_code == status.HTTP_200_OK
    assert content == {
        "id": str(product_inserted.id),
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": "8.500",
        "status": True,
    }


async def test_controller_get_should_return_not_found(client, products_url):
    response = await client.get(f"{products_url}4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Product not found with filter: 4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    }


# -----------------------------
# Teste: GET produtos (query) com e sem filtro
# -----------------------------
@pytest.mark.usefixtures("products_inserted")
async def test_controller_query_should_return_success(client, products_url):
    response = await client.get(products_url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), List)
    assert len(response.json()) > 1


@pytest.mark.usefixtures("products_inserted")
async def test_controller_query_with_price_filter(client, products_url, products_inserted):
    response = await client.get(f"{products_url}?min_price=5000&max_price=8000")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(5000 <= float(product["price"].replace('.', '').replace(',', '.')) <= 8000 for product in data)


# -----------------------------
# Teste: PATCH produto
# -----------------------------
async def test_controller_patch_should_return_success(client, products_url, product_inserted):
    response = await client.patch(f"{products_url}{product_inserted.id}", json={"price": "7.500"})
    content = response.json()

    del content["created_at"]
    del content["updated_at"]

    assert response.status_code == status.HTTP_200_OK
    assert content == {
        "id": str(product_inserted.id),
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": "7.500",
        "status": True,
    }


async def test_controller_patch_should_return_not_found(client, products_url):
    response = await client.patch(
        f"{products_url}4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca",
        json={"price": "7.500"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


# -----------------------------
# Teste: DELETE produto
# -----------------------------
async def test_controller_delete_should_return_no_content(client, products_url, product_inserted):
    response = await client.delete(f"{products_url}{product_inserted.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_controller_delete_should_return_not_found(client, products_url):
    response = await client.delete(f"{products_url}4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Product not found with filter: 4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    }
