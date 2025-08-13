from typing import List, Optional
from uuid import UUID
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo
from pymongo.errors import DuplicateKeyError
from store.db.mongo import db_client
from store.models.product import ProductModel
from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.core.exceptions import NotFoundException, InsertErrorException


class ProductUsecase:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient = db_client.get()
        self.database: AsyncIOMotorDatabase = self.client.get_database()
        self.collection = self.database.get_collection("products")

    async def create(self, body: ProductIn) -> ProductOut:
        try:
            product_model = ProductModel(**body.model_dump())
            await self.collection.insert_one(product_model.model_dump())
            return ProductOut(**product_model.model_dump())
        except DuplicateKeyError:
            raise InsertErrorException(message="Já existe um produto com este ID ou nome")
        except Exception as e:
            raise InsertErrorException(message=f"Erro ao inserir produto: {str(e)}")

    async def get(self, id: UUID) -> ProductOut:
        result = await self.collection.find_one({"id": id})

        if not result:
            raise NotFoundException(message=f"Produto não encontrado com ID: {id}")

        return ProductOut(**result)

    async def query(self, min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[ProductOut]:
        query_filter = {}
        if min_price is not None and max_price is not None:
            query_filter["price"] = {"$gt": min_price, "$lt": max_price}

        return [ProductOut(**item) async for item in self.collection.find(query_filter)]

    async def update(self, id: UUID, body: ProductUpdate) -> ProductUpdateOut:
        update_data = body.model_dump(exclude_none=True)

        # Atualiza automaticamente updated_at, caso não tenha sido enviado
        if "updated_at" not in update_data:
            update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            filter={"id": id},
            update={"$set": update_data},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        if not result:
            raise NotFoundException(message=f"Produto não encontrado com ID: {id}")

        return ProductUpdateOut(**result)

    async def delete(self, id: UUID) -> bool:
        product = await self.collection.find_one({"id": id})
        if not product:
            raise NotFoundException(message=f"Produto não encontrado com ID: {id}")

        result = await self.collection.delete_one({"id": id})

        return True if result.deleted_count > 0 else False


product_usecase = ProductUsecase()
