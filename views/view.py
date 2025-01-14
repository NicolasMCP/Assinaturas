import datetime
import sys, os
sys.path.append(os.path.abspath(os.curdir))
from models.database import motor_db
from models.model import Assinaturas, Pagamentos
from sqlmodel import Session, select
from datetime import date, datetime
from sqlalchemy import extract, text, func
import time

ini = time.time()

class AssinaturasService:
    def __init__(self, motor_db):
        self.motor_db = motor_db

    def create(self, ass: Assinaturas):
        with Session(self.motor_db) as sessao:
            sessao.add(ass)
            sessao.commit()
            return ass

    def list_all(self):
        with Session(self.motor_db) as sessao:
            consulta = select(Assinaturas)
            resultados = sessao.exec(consulta).all()
            return resultados

    def _foi_pago(self, resultados):
        for resultado in resultados:
            if resultado.data_pagamento.month == date.today().month:
                return True
        return False

    def pagar(self, ass: Assinaturas):
        with (Session(self.motor_db) as sessao):
            consulta = (select(Pagamentos)
                        .join(Assinaturas)
                        .where(
                             (Assinaturas.empresa == ass.empresa) &
                             (extract('year', Pagamentos.data_pagamento) == date.today().year) &
                             (extract('month', Pagamentos.data_pagamento) == date.today().month)
                        )
            )
            resultados = sessao.exec(consulta).all()

            if self._foi_pago(resultados):
                pagar_novamente = input('Esta conta já foi paga esse mês, desseja pagar novamente ? S ou N: ')
                if not pagar_novamente.upper() == 'S':
                    return

            pagar = Pagamentos(assinatura_id = ass.id, data_pagamento = date.today())
            sessao.add(pagar)
            sessao.commit()

    def valor_total(self):
        with Session(self.motor_db) as sessao:
            # ________________________ version 2 ______________________________
            # fast 11.38  e  11.35
            consulta = text("SELECT SUM(valor) AS valor_total FROM Assinaturas")
            resultado = sessao.exec(consulta).one()
            return resultado.valor_total
            # _________________________ version 1_____________________________
            # low much 120.57  e  79.66
            # consulta = select(func.sum(Assinaturas.valor))
            # resultado = sessao.exec(consulta).one()
            # return resultado
            # __________________________ version 3 ____________________________
            # low 109.87  e  77.99
        #     consulta = select(Assinaturas)
        #     resultados = sessao.exec(consulta).all()
        # total = 0
        # for resultado in resultados:
        #     total += resultado.valor
        # return float(total)

    def delete(self, id):
        with Session(self.motor_db) as sessao:
            consulta = select(Assinaturas).where(Assinaturas.id == id)
            resultado = sessao.exec(consulta).one()

            print(f"ID: {resultado.id}")
            print(f"Data da Assinatura: {resultado.data_assinatura}")
            print(f"Valor: R$ {resultado.valor:.2f}")
            print(f"Empresa: {resultado.empresa}")
            print(f"Site: {resultado.site}")

            retorno = input('\nDeseja realmente Deletar essa assinatura ? S ou N: ')
            if not retorno.upper() == 'S':
                return

            sessao.delete(resultado)
            sessao.commit()
            print(f"CONFIRMADO!! Empresa: {resultado.empresa} DELETADA.")
            return
    # ---------------------- version 1 ---------------------------
    # def _os_12_meses_anteriores(self):
    #     hoje = datetime.now()
    #     ano = hoje.year
    #     mes = hoje.month
    #     ano_anterior = []
    #     mm = 0
    #     aa = 0
    #     for i in range(12):
    #         if mes - i <= 0:
    #             mm = 12
    #             aa = 1
    #         ano_anterior.append((mes - i + mm, ano - aa))
    #     print(ano_anterior)

    # ---------------------- version 2 ---------------------------
    def _ultimos_12_meses(self):
        hoje = datetime.now()
        ano, mes = hoje.year, hoje.month
        u12_meses = [(mes - i if mes - i > 0 else 12 + (mes - i), ano if mes - i > 0 else ano - 1) for i in range(12)]
        return u12_meses[::-1]

    def _valores_por_mes(self, u12_meses):
        with Session(self.motor_db) as sessao:
            consulta = select(Pagamentos)
            resultado = sessao.exec(consulta).all()
            v12_meses = []
            for i in u12_meses:
                valor = 0

    def gerar_grafico(self):
        u12_meses = self._ultimos_12_meses()
        v12_meses = self._valores_por_mes(u12_meses)


ass_s = AssinaturasService(motor_db)

print(ass_s._ultimos_12_meses())

# ass_s.delete(5)

# print(f"Valor total das assinaturas: R$ {ass_s.valor_total():.2f}")

# ass = Assinaturas(empresa = 'Netflix', site = 'netflix.com.br', data_assinatura = date.today(), valor = 52.00)
# ass_s.create(ass)
# ass = Assinaturas(empresa = 'Pythonando', site = 'pytonando.com.br', data_assinatura = date.today(), valor = 50.00)
# ass_s.create(ass)

# ass_s_list = ass_s.list_all()
# print('-' * 40)
# for item in ass_s_list:
#     print(f"ID: {item.id}")
#     print(f"Data da Assinatura: {item.data_assinatura}")
#     print(f"Valor: R$ {item.valor:.2f}")
#     print(f"Empresa: {item.empresa}")
#     print(f"Site: {item.site}")
#     print('-' * 40)

# x = int(input('id da ass. a pagar: '))
# ass_s.pagar(ass_s_list[x - 1])

fim = time.time()
print(fim - ini)
