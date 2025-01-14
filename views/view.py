import datetime
import sys, os
sys.path.append(os.path.abspath(os.curdir))
from models.database import motor_db
from models.model import Assinaturas, Pagamentos
from sqlmodel import Session, select
from datetime import date, datetime
from sqlalchemy import extract, text, func
import time

# ini = time.time()

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
    # def _ultimo_ano(self):
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
        elif tipo == 'lineas':
            plt.plot(ultimo_ano, vals_ano, color = 'orange')
        plt.title('Valores das assinaturas nos últimos 12 meses')
        plt.xlabel('Mês')
        plt.ylabel('Valores')

        manager = plt.get_current_fig_manager()
        manager.window.setGeometry(0, 0, 1280, 800)
        # manager.window.geometry("800x600")
        plt.show()


ass_s = AssinaturasService(motor_db)

print(ass_s.gerar_grafico())

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

# Tempo usado para executar
# fim = time.time()
# print(fim - ini)
