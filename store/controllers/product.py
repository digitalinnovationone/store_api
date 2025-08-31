from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import UUID4
from store.core.exceptions import NotFoundException

from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.usecases.product import ProductUsecase

router = APIRouter(tags=["products"])
from typing import List
from datetime import datetime
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError

from store.core.exceptions import NotFoundException
from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.usecases.product import ProductUsecase

router = APIRouter(tags=["products"])

# -----------------------------
# POST: Criar um novo produto
# -----------------------------
@router.post(path="/", status_code=status.HTTP_201_CREATED)
async def post(
    body: ProductIn = Body(...),
    usecase: ProductUsecase = Depends()
) -> ProductOut:
    """
    Cria um novo produto.
    Captura erros de integridade e retorna mensagem amigável.
    """
    try:
        return await usecase.create(body=body)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=303,
            detail=f"Erro ao inserir produto: {exc.orig}"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao inserir o produto: {str(exc)}"
        )

# -----------------------------
# GET: Consultar produto por id
# -----------------------------
@router.get(path="/{id}", status_code=status.HTTP_200_OK)
async def get(
    id: UUID4 = Path(alias="id"),
    usecase: ProductUsecase = Depends()
) -> ProductOut:
    """
    Retorna um produto pelo ID.
    """
    try:
        return await usecase.get(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)

# -----------------------------
# GET: Listar produtos com filtros
# -----------------------------
@router.get(path="/", status_code=status.HTTP_200_OK)
async def query(
    min_price: float | None = Query(None, description="Preço mínimo"),
    max_price: float | None = Query(None, description="Preço máximo"),
    usecase: ProductUsecase = Depends()
) -> List[ProductOut]:
    """
    Lista produtos com filtros de preço (opcional).
    """
    return await usecase.query(min_price=min_price, max_price=max_price)

# -----------------------------
# PATCH: Atualizar produto
# -----------------------------
@router.patch(path="/{id}", status_code=status.HTTP_200_OK)
async def patch(
    id: UUID4 = Path(alias="id"),
    body: ProductUpdate = Body(...),
    usecase: ProductUsecase = Depends()
) -> ProductUpdateOut:
    """
    Atualiza um produto pelo ID.
    Atualiza 'updated_at' automaticamente se não fornecido.
    Captura NotFoundException e retorna mensagem amigável.
    """
    try:
        if not body.updated_at:
            body.updated_at = datetime.utcnow()
        return await usecase.update(id=id, body=body)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)

# -----------------------------
# DELETE: Excluir produto
# -----------------------------
@router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    id: UUID4 = Path(alias="id"),
    usecase: ProductUsecase = Depends()
) -> None:
    """
    Exclui um produto pelo ID.
    Captura NotFoundException e retorna mensagem amigável.
    """
    try:
        await usecase.delete(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.post(path="/", status_code=status.HTTP_201_CREATED)
async def post(
    body: ProductIn = Body(...), usecase: ProductUsecase = Depends()
) -> ProductOut:
    return await usecase.create(body=body)


@router.get(path="/{id}", status_code=status.HTTP_200_OK)
async def get(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> ProductOut:
    try:
        return await usecase.get(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get(path="/", status_code=status.HTTP_200_OK)
async def query(usecase: ProductUsecase = Depends()) -> List[ProductOut]:
    return await usecase.query()


@router.patch(path="/{id}", status_code=status.HTTP_200_OK)
async def patch(
    id: UUID4 = Path(alias="id"),
    body: ProductUpdate = Body(...),
    usecase: ProductUsecase = Depends(),
) -> ProductUpdateOut:
    return await usecase.update(id=id, body=body)


@router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> None:
    try:
        await usecase.delete(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
