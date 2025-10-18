from faker.providers import BaseProvider

class ErpProvider(BaseProvider):
    
    def cpf_ou_cnpj(self):
        if self.random_int(0, 1) == 0:
            return self.generator.cpf()
        else:
            return self.generator.cnpj()
    
    def tamanho_roupa(self):
        return self.random_element(('PP', 'P', 'M', 'G', 'GG', 'XG'))

    def tecido_roupa(self):
        tecidos = ('Algodão', 'Seda', 'Linho', 'Poliéster', 'Viscose', 'Couro', 'Elastano')
        return self.random_element(tecidos)

    def nome_colecao(self):
        prefixos = ('Elegância', 'Classic', 'Studio', 'Vintage')
        sufixos = ('Chic', 'Couture', 'Vigor', 'Eterno')
        return f"{self.random_element(prefixos)} {self.random_element(sufixos)}"

    def forma_pagamento_erp(self):
        return self.random_element(('Cartão de Crédito', 'Boleto Bancário', 'PIX', 'Dinheiro'))

    def status_pagamento_erp(self):
        return self.random_element(('Aprovado', 'Pendente', 'Recusado', 'Em análise', 'Estornado'))

    def status_pedido_ecommerce(self):
        return self.random_element(('Processando', 'Pagamento Aprovado', 'Em transporte', 'Entregue', 'Cancelado'))

    def cfop_venda(self):
        return self.random_element(('5101', '5102', '6101', '6102', '5405'))

    def codigo_rastreamento_br(self):
        return self.generator.bothify('??#########??').upper()