from datetime import datetime
import sys, os
sys.path.append(os.path.abspath(os.curdir))
from models.database import motor_db
from models.model import Assinaturas, Pagamentos
from sqlmodel import Session, select
from datetime import date, datetime
from sqlalchemy import extract, text, func
import time

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

    def _is_pago(self, resultados):
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

            if self._is_pago(resultados):
                pagar_novamente = input('\nEsta conta já foi paga esse mês, desseja pagar novamente ? S ou N: ')
                if not pagar_novamente.upper() == 'S':
                    return

            pagar = Pagamentos(assinatura_id = ass.id, data_pagamento = date.today())
            sessao.add(pagar)
            sessao.commit()
            return

    def valor_total(self):
        with Session(self.motor_db) as sessao:
            consulta = text("SELECT SUM(valor) AS valor_total FROM Assinaturas")
            resultado = sessao.exec(consulta).one()
            return resultado.valor_total

    def exclui_ass(self, id):
        with Session(self.motor_db) as sessao:
            consulta = select(Assinaturas).where(Assinaturas.id == id)
            resultado = sessao.exec(consulta).one()
            retorno = input('\nDeseja realmente Deletar essa assinatura ? S ou N: ')
            if not retorno.upper() == 'S':
                return

            sessao.delete(resultado)
            sessao.commit()
            print(f"CONFIRMADO!! Empresa: {resultado.empresa} DELETADA.")
            return

    def _ultimo_ano(self):
        hoje = datetime.now()
        ano, mes = hoje.year, hoje.month
        ultimo_ano = [(mes - i if mes - i > 0 else 12 + (mes - i), ano if mes - i > 0 else ano - 1) for i in range(12)]
        return ultimo_ano[::-1]

    def _get_vals_ano(self, ultimo_ano):
        with Session(self.motor_db) as sessao:
            consulta = select(Pagamentos)
            resultados = sessao.exec(consulta).all()
            vals_ano = []
            for myyyy in ultimo_ano:
                valor = 0
                for resultado in resultados:
                    if resultado.data_pagamento.month == myyyy[0] and resultado.data_pagamento.year == myyyy[1]:
                        valor += float(resultado.assinaturas.valor)
                vals_ano.append(valor)
            return vals_ano


    def gerar_grafico(self, tipo = 'barras'):
        ultimo_ano = self._ultimo_ano()
        vals_ano = self._get_vals_ano(ultimo_ano)

        ultimo_ano = [str(mes) + '/' + str(ano) for mes, ano in ultimo_ano]
        import matplotlib.pyplot as plt
        if tipo == 'barras':
            plt.bar(ultimo_ano, vals_ano, color = '#6476D9')
        elif tipo == 'linhas':
            plt.plot(ultimo_ano, vals_ano, color = 'orange')
        plt.title('Valores das assinaturas nos últimos 12 meses')
        plt.xlabel('Mês')
        plt.ylabel('Valores')

        manager = plt.get_current_fig_manager()
        manager.window.setGeometry(0, 0, 1280, 800)
        plt.show()
        return

