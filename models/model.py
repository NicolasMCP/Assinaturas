from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import date
from decimal import Decimal


class Assinaturas(SQLModel, table = True):
    id: int = Field(default=None, primary_key = True)
    empresa: str
    site: Optional[str] = None
    data_assinatura: date
    valor: Decimal


class Pagamentos(SQLModel, table = True):
    id: int = Field(primary_key = True)
    assinatura_id: int = Field(foreign_key='assinaturas.id')
    data_pagamento: date
    assinaturas: Assinaturas = Relationship()
