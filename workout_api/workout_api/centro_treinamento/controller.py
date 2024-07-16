from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from sqlalchemy import select
from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from workout_api.centro_treinamento.models import CentroTreinamentoModel

from workout_api.contrib.dependencies import DatabaseDependency
router = APIRouter()

@router.post(
    '/',
      summary='Criar um novo centro de treinamento',
      status_code=status.HTTP_201_CREATED,
      response_model = CategoriaOut
      )
async def post(
    db_session: DatabaseDependency, 
    centro_treinamento_in: CentroTreinamentoIn = Body(...)
) -> CentroTreinamentoOut:
    centro_treinamento_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_in.model_dump())
    CentroTreinamentoModel = CentroTreinamentoOut(**centro_treinamento_out.model_dump())

    db_session.add( centro_treinamento_out)
    await db_session.commit()
    return  centro_treinamento_out


@router.get(
    '/',
      summary='consultar todos os centros de treinamento',
      status_code=status.HTTP_200_OK,
      response_model = list[CentroTreinamentoOut]
      )
async def query(db_session: DatabaseDependency, ) -> list[CentroTreinamentoOut]:
    centro_treinamento_out: list[CentroTreinamentoOut] = (await db_session.execute(select(CentroTreinamentoModel))).scalars().all()

    return centro_treinamento_out

@router.get(
    '/{id}',
      summary='consultar um centro de treinamento pelo Id',
      status_code=status.HTTP_200_OK,
      response_model = CentroTreinamentoOut,
      )
async def query(id: UUID4, db_session: DatabaseDependency, ) -> CentroTreinamentoOut:
    centro_treinamento_out: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
        ).scalars().first()
    
    if not centro_treinamento_out:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail='centro de treinamento não encontrado no id:{id}'
          )

    return centro_treinamento_out