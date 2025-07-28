from decimal import Decimal
from random import randint
from typing import List
from datetime import datetime, timedelta, timezone
from uuid import UUID
from httpx import AsyncClient
import pytest
from tests.factories import product_data
from fastapi import status


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


async def test_controller_create_should_return_fail(
    client, products_url, product_inserted
):
    product_repeated = product_data()
    product_repeated["name"] = product_inserted.name
    response = await client.post(products_url, json=product_repeated)
    content = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert content["detail"] == (
        f"Produto de nome '{product_repeated['name']}' já existe."
    )


async def test_controller_get_should_return_success(
    client, products_url, product_inserted
):
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


async def test_controller_get_should_return_not_found(
    client: AsyncClient, products_url: str, product_id: UUID
):
    response = await client.get(f"{products_url}{product_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Product not found with filter: {product_id}"}


@pytest.mark.usefixtures("products_inserted")
async def test_controller_query_should_return_success(client, products_url):
    response = await client.get(products_url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), List)
    assert len(response.json()) > 1


async def test_controller_patch_should_return_success(
    client, products_url, product_inserted
):
    response = await client.patch(
        f"{products_url}{product_inserted.id}", json={"price": "7.500"}
    )

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


@pytest.mark.usefixtures("products_inserted")
async def test_controller_patch_should_return_not_found_exception(
    client: AsyncClient, products_url: str, product_id: UUID
):
    response = await client.patch(
        f"{products_url}{product_id}", json={"price": "1.159"}
    )

    content = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert content["detail"] == f"Produto não encontrado com id : {product_id}"


async def test_update_product_updated_at_auto(client, products_url, product_inserted):
    response = await client.patch(
        f"{products_url}{product_inserted.id}", json={"price": "7.500", "quantity": 20}
    )

    assert response.status_code == 200
    updated = response.json()
    updated_at = datetime.fromisoformat(updated["updated_at"])
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)

    assert datetime.now(tz=timezone.utc) - updated_at < timedelta(seconds=5)


async def test_update_product_with_custom_updated_at(
    client, products_url, product_inserted
):
    new_updated_at = datetime(
        randint(2020, 2025),
        randint(1, 12),
        randint(1, 28),
        randint(0, 24),
        randint(0, 59),
        randint(0, 59),
        tzinfo=timezone.utc,
    ).isoformat()

    response = await client.patch(
        f"{products_url}{product_inserted.id}",
        json={
            "price": "8.99",
            "quantity": 30,
            "updated_at": new_updated_at,
        },
    )

    assert response.status_code == 200
    updated = response.json()
    updated_at_resp_dt = datetime.fromisoformat(
        updated["updated_at"].replace("Z", "+00:00")
    )
    new_updated_at_dt = datetime.fromisoformat(new_updated_at)
    assert updated_at_resp_dt == new_updated_at_dt


async def test_update_product_updated_at_behavior_fixed_date(
    client, products_url, product_inserted
):
    update_payload = {"price": "7500", "quantity": 15}
    response = await client.patch(
        f"{products_url}{product_inserted.id}", json=update_payload
    )
    assert response.status_code == 200
    updated = response.json()
    updated_at = datetime.fromisoformat(updated["updated_at"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    assert abs((now - updated_at).total_seconds()) < 5  # Tolerância de 5 segundos

    # Atualização enviando updated_at fixo (deve aceitar)
    fixed_updated_at = "2023-07-15T10:30:00+00:00"
    update_payload_with_fixed = {
        "price": "7999",
        "quantity": 20,
        "updated_at": fixed_updated_at,
    }
    response = await client.patch(
        f"{products_url}{product_inserted.id}", json=update_payload_with_fixed
    )
    assert response.status_code == 200
    updated = response.json()

    updated_at_resp = updated["updated_at"]

    updated_at_resp_dt = datetime.fromisoformat(updated_at_resp.replace("Z", "+00:00"))
    fixed_updated_at_dt = datetime.fromisoformat(fixed_updated_at)
    assert (
        updated_at_resp_dt == fixed_updated_at_dt
    ), f"Esperado {fixed_updated_at}, mas recebido {updated_at_resp}"


async def test_controller_delete_should_return_no_content(
    client, products_url, product_inserted
):
    response = await client.delete(f"{products_url}{product_inserted.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_controller_delete_should_return_not_found(client, products_url):
    response = await client.delete(
        f"{products_url}4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Product not found with filter: 4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    }


@pytest.mark.usefixtures("products_inserted")
async def test_controller_query_with_price_filter_should_return_success(
    client: AsyncClient, products_url: str
):
    response = await client.get(
        products_url, params={"min_price": "5.000", "max_price": "8.000"}
    )

    assert response.status_code == 200
    products = response.json()

    for product in products:
        assert "." in product["price"]
        price_value = float(product["price"].replace(".", ""))
        assert 5000 <= price_value <= 8000


@pytest.mark.usefixtures("products_inserted")
async def test_price_filter_with_valid_range(client: AsyncClient, products_url: str):
    """Testa filtro com range válido"""
    response = await client.get(
        products_url, params={"min_price": "5.000", "max_price": "8.000"}
    )

    assert response.status_code == status.HTTP_200_OK
    products = response.json()
    assert len(products) == 5  # Iphone 8 Pro, 9 Pro Max, 10 Pro Max

    for product in products:
        price = Decimal(product["price"].replace(".", ""))
        assert 5000 <= price <= 8000
        assert product["name"] in [
            "Iphone 8 Pro",
            "Iphone 9 Pro Max",
            "Iphone 10 Pro Max",
            "Iphone 12 Pro Max",
            "Iphone 13 Pro Max",
        ]


@pytest.mark.usefixtures("products_inserted")
async def test_price_filter_with_only_min(client: AsyncClient, products_url: str):
    response = await client.get(products_url, params={"min_price": "7.000"})

    assert response.status_code == status.HTTP_200_OK
    products = response.json()
    assert len(products) == 5


@pytest.mark.usefixtures("products_inserted")
async def test_price_filter_with_only_max(client: AsyncClient, products_url: str):
    response = await client.get(products_url, params={"max_price": "6.570"})

    assert response.status_code == status.HTTP_200_OK
    products = response.json()
    assert len(products) == 3


@pytest.mark.usefixtures("products_inserted")
async def test_price_filter_with_exact_value(client: AsyncClient, products_url: str):
    response = await client.get(
        products_url, params={"min_price": "7.545", "max_price": "7.545"}
    )

    assert response.status_code == status.HTTP_200_OK
    products = response.json()
    assert len(products) == 1
    assert products[0]["name"] == "Iphone 10 Pro Max"
    assert products[0]["price"] == "7.545"


@pytest.mark.usefixtures("products_inserted")
async def test_price_filter_with_invalid_format(client: AsyncClient, products_url: str):
    response = await client.get(
        products_url, params={"min_price": "5000", "max_price": "8000"}
    )
    products = response.json()
    assert len(products) == 0
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures("products_inserted")
async def test_price_filter_with_non_existent_range(
    client: AsyncClient, products_url: str
):
    response = await client.get(
        products_url, params={"min_price": "20.000", "max_price": "30.000"}
    )

    assert response.status_code == status.HTTP_200_OK
    products = response.json()
    assert len(products) == 0


@pytest.mark.usefixtures("products_inserted")
async def test_price_filter_with_swapped_values(client: AsyncClient, products_url: str):
    response = await client.get(
        products_url, params={"min_price": "8.000", "max_price": "5.000"}
    )

    assert response.status_code == status.HTTP_200_OK
    products = response.json()
    assert len(products) == 0


@pytest.mark.usefixtures("products_inserted")
async def test_price_filter_with_status_true(client: AsyncClient, products_url: str):
    response = await client.get(
        products_url,
        params={"min_price": "6.201", "max_price": "8.040"},
    )

    assert response.status_code == status.HTTP_200_OK
    products = response.json()
    assert len(products) == 4
    assert all(product["status"] for product in products)
