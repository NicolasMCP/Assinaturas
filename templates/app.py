from datetime import datetime
import sys, os
from decimal import Decimal
sys.path.append(os.path.abspath(os.curdir))
from views.view import AssinaturasService
from models.database import motor_db
from models.model import Assinaturas


def limpa_tela() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')
    return


class UI:
    def __init__(self):
        self.ass_service = AssinaturasService(motor_db)
        return

    def adicionar_ass(self):
        empresa = input('Empresa: ')
        site = input('Site: ')
        data_assinatura = datetime.strptime(input('Data de assinatura: '), '%d/%m/%Y')
        valor = Decimal(input('Valor: '))

        assinaturas = Assinaturas(empresa=empresa, site=site, data_assinatura=data_assinatura, valor=valor)
        self.ass_service.create(assinaturas)
        print('Assinatura adicionada com sucesso.')
        return

    def excluir_ass(self):
        assinaturas = self.ass_service.list_all()
        print('\nEscolha qual assinatura deseja excluir')

        for i in assinaturas:
            print(f'[{i.id}] -> {i.empresa}')

        escolha = int(input('Escolha a assinatura: '))

        print(f"\nID: {assinaturas[escolha-1].id}")
        print(f"Data da Assinatura: {assinaturas[escolha-1].data_assinatura}")
        print(f"Valor: R$ {assinaturas[escolha-1].valor:.2f}")
        print(f"Empresa: {assinaturas[escolha-1].empresa}")
        print(f"Site: {assinaturas[escolha-1].site}")

        self.ass_service.exclui_ass(escolha)
        #TODO: quando excluir uma assinatura deixar o histórico de pagamento dela inativo
        print('Assinatura excluída com sucesso.')
        return

    def valor_mensal_total(self):
        print(f'\nSeu valor total mensal em assinaturas: {self.ass_service.valor_total()}')
        return

    def listar_ass(self):
        assinaturas = self.ass_service.list_all()
        print('\nEscolha a assinatura deseja detalhar')

        for i in assinaturas:
            print(f'[{i.id}] -> {i.empresa}')

        escolha = int(input('Id da assinatura ou 0 para voltar ao menu: '))
        if escolha != 0:
            print(f"\nID: {assinaturas[escolha-1].id}")
            print(f"Data da Assinatura: {assinaturas[escolha-1].data_assinatura}")
            print(f"Valor: R$ {assinaturas[escolha-1].valor:.2f}")
            print(f"Empresa: {assinaturas[escolha-1].empresa}")
            print(f"Site: {assinaturas[escolha-1].site}")
            input('\n<ENTER> para retornar ao menu...')
            return
        else:
            return

    def pagar_ass(self):
        assinaturas = self.ass_service.list_all()
        print('\nEscolha a assinatura deseja Pagar')

        for i in assinaturas:
            print(f'[{i.id}] -> {i.empresa}')

        escolha = int(input('Id da assinatura a Pagar: '))
        print(f"\nID: {assinaturas[escolha-1].id}")
        print(f"Data da Assinatura: {assinaturas[escolha-1].data_assinatura}")
        print(f"Valor: R$ {assinaturas[escolha-1].valor:.2f}")
        print(f"Empresa: {assinaturas[escolha-1].empresa}")
        print(f"Site: {assinaturas[escolha-1].site}")

        self.ass_service.pagar(assinaturas[escolha-1])
        input('\n<ENTER> para retornar ao menu...')
        return

    def inicio(self):
        while True:
            limpa_tela()
            print('''
                [1] -> Adicionar assinatura
                [2] -> Remover assinatura
                [3] -> Valor total
                [4] -> Gastos últimos 12 meses Barras
                [5] -> Gastos últimos 12 meses Linhas
                [6] -> Listar as Assinaturas
                [7] -> Pagar uma Assinatura
                [8] -> Sair
                ''')

            escolha = input('Escolha uma opção: ')

            match escolha:
                case '1':
                    self.adicionar_ass()
                case '2':
                    self.excluir_ass()
                case '3':
                    self.valor_mensal_total()
                case '4':
                    self.ass_service.gerar_grafico('barras')
                case '5':
                    self.ass_service.gerar_grafico('linhas')
                case '6':
                    self.listar_ass()
                case '7':
                    self.pagar_ass()
                    pass
                case _:
                    break


if __name__ == '__main__':
    UI().inicio()