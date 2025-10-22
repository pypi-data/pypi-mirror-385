from unittest import TestCase
from entities.ticket import Ticket
from factories.ticket_factory import criar_ticket
from tests.constants import DADOS_TICKET


class Testticket(TestCase):
    
    def test_ticket_entity(self):
        ticket = Ticket(
            id='196661',
            protocolo='31023920250801095603'
        )
        self.assertEqual(ticket.id, '196661')
        self.assertEqual(ticket.protocolo, '31023920250801095603')
    
    def test_ticket_factory(self):
        received_data = DADOS_TICKET
        ticket = criar_ticket(received_data)
        self.assertIsInstance(ticket, Ticket)