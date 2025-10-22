from portal_facil_sdk.entities.beneficiario import Beneficiario
from portal_facil_sdk.entities.ticket import Ticket
from portal_facil_sdk.factories.beneficiario_factory import criar_beneficiario
from portal_facil_sdk.factories.ticket_factory import criar_ticket
from portal_facil_sdk.providers.crm_provider import CrmProvider

class AtendimentoController:
    
    def __init__(self, provider: CrmProvider):
        self._provider = provider
    
    def consultar_beneficiario(self, doc: str) -> Beneficiario:
        dados_beneficiario = self._provider.obter_beneficiario(doc)
        return criar_beneficiario(dados_beneficiario)
            
    def abrir_chamado(self, beneficiario: Beneficiario, telefone: str, origem_id=None) -> Ticket: 
        dados_ticket = self._provider.abrir_ticket(beneficiario.codigo, telefone, origem_id)
        return criar_ticket(dados_ticket)
    
    def adicionar_anotacao_chamado(self, ticket: Ticket, anotacao: str) -> None:
        self._provider.adicionar_anotacao(ticket.id, ticket.protocolo, anotacao)

    def encerrar_chamado(self, ticket: Ticket) -> None:
        self._provider.encerrar_chamado(ticket.id, ticket.protocolo)
