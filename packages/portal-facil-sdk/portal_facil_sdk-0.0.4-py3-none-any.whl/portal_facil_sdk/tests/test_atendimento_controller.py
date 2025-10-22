from unittest import TestCase
from unittest.mock import MagicMock
from controllers.atendimento_controller import AtendimentoController
from entities.beneficiario import Beneficiario
from entities.ticket import Ticket
from tests.constants import DADOS_BENEFICIARIO, DADOS_TICKET


class TestAtendimentoController(TestCase):
    
    def setUp(self):
        provider = MagicMock()
        provider.obter_beneficiario.return_value = DADOS_BENEFICIARIO
        provider.abrir_ticket.return_value = DADOS_TICKET
        self.controller = AtendimentoController(provider)

    def test_consultar_beneficiario(self):
        doc = '0000027'
        beneficiario = self.controller.consultar_beneficiario(doc)
        self.assertIsInstance(beneficiario, Beneficiario)
        self.controller._provider.obter_beneficiario.return_value = []
        self.assertRaises(ValueError, self.controller.consultar_beneficiario, doc)

    def test_abrir_chamado(self):
        beneficiario = Beneficiario(
            codigo='0000027', nome='BENEFICIARIO GENERICO', cpf='035.710.586-90'
        )
        telefone = '1137092380'
        ticket = self.controller.abrir_chamado(beneficiario, telefone)
        self.assertIsInstance(ticket, Ticket)