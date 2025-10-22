from abc import ABC, abstractmethod
from datetime import datetime
from modelos_helpdesk import Ticket, Agente, Usuario, Solicitante, StatusTicket, PrioridadeTicket
from daos import TicketDAO, UsuarioDAO, CategoriaDAO
from seguranca import gerar_hash_senha
import uuid

# --- EXEMPLO 1: GERAÇÃO DE RELATÓRIOS ---
class RelatorioTemplate(ABC):
    """(TEMPLATE) Define o esqueleto para a geração de relatórios."""

    def gerar_relatorio(self):
        """Este é o Template Method. Ele define a ordem fixa das coisas."""
        conteudo = []
        conteudo.append(self._gerar_cabecalho())
        conteudo.append(self._gerar_corpo())
        conteudo.append(self._gerar_rodape())
        return "\n".join(conteudo)

    def _gerar_rodape(self):
        """Hook com implementação padrão."""
        return f"\n--- Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} ---"

    @abstractmethod
    def _gerar_cabecalho(self) -> str:
        pass

    @abstractmethod
    def _gerar_corpo(self) -> str:
        pass

class RelatorioTicketsPorStatus(RelatorioTemplate):
    """(CONCRETO) Gera um relatório de tickets por status buscando do DB."""
    def __init__(self, ticket_dao: TicketDAO):
        self._ticket_dao = ticket_dao

    def _gerar_cabecalho(self) -> str:
        return "========== RELATÓRIO DE TICKETS POR STATUS (DO BANCO DE DADOS) =========="

    def _gerar_corpo(self) -> str:
        tickets = self._ticket_dao.get_all()
        tickets_por_status = {}
        for t in tickets:
            status_valor = t.status.value
            if status_valor not in tickets_por_status:
                tickets_por_status[status_valor] = []
            tickets_por_status[status_valor].append(f"  - #{t.id_ticket[:8]}... ('{t.assunto}')")
        
        linhas = []
        for status, descricoes in sorted(tickets_por_status.items()):
            linhas.append(f"Status: {status}")
            linhas.extend(descricoes)
        return "\n".join(linhas) if linhas else "Nenhum ticket encontrado."

# --- EXEMPLO 2: PROCESSAMENTO DE NOVOS TICKETS (TRIAGEM) ---
class ProcessadorTicketTemplate(ABC):
    """(TEMPLATE) Define o algoritmo para triagem de um novo ticket com persistência."""

    def processar_novo_ticket(self, ticket: Ticket):
        """Template Method que orquestra a triagem e salvamento do ticket."""
        print(f"Iniciando triagem do Ticket #{ticket.id_ticket[:8]}... ('{ticket.assunto}')...")
        if not self._validar_ticket(ticket):
            print("  - Erro: Ticket inválido. Processo abortado.")
            return

        self._definir_prioridade(ticket)
        print(f"  - Prioridade definida para: {ticket.prioridade.name}")
        
        self._atribuir_agente_sugerido(ticket)
        if ticket.agente_id:
            agente = UsuarioDAO().get(ticket.agente_id)
            print(f"  - Sugestão de agente: {agente.nome_completo if agente else 'ID não encontrado'}")
        else:
            print("  - Nenhum agente disponível encontrado.")
        
        self._notificar_setor_responsavel(ticket)
        
        # Passo final: salvar as alterações no banco
        TicketDAO().save(ticket)
        print(f"  - Ticket salvo no banco de dados com as atualizações.")

    def _validar_ticket(self, ticket: Ticket) -> bool:
        return bool(ticket.assunto and ticket.descricao and ticket.solicitante_id)

    def _notificar_setor_responsavel(self, ticket: Ticket):
        categoria = CategoriaDAO().get(ticket.categoria_id)
        if categoria:
            print(f"  - Notificação enviada para o setor: {categoria.setor_responsavel}")

    @abstractmethod
    def _definir_prioridade(self, ticket: Ticket):
        pass

    @abstractmethod
    def _atribuir_agente_sugerido(self, ticket: Ticket):
        pass

class ProcessadorTicketHardware(ProcessadorTicketTemplate):
    """(CONCRETO) Lógica de triagem para tickets de hardware, buscando agentes do DB."""
    def __init__(self):
        self._agentes_disponiveis = [
            agente for agente in UsuarioDAO().get_agentes() 
            if agente.especialidade and agente.especialidade.lower() == 'hardware'
        ]

    def _definir_prioridade(self, ticket: Ticket):
        if any(keyword in ticket.descricao.lower() for keyword in ["não liga", "quebrado", "queimado"]):
            ticket.prioridade = PrioridadeTicket.ALTA
        else:
            ticket.prioridade = PrioridadeTicket.MEDIA

    def _atribuir_agente_sugerido(self, ticket: Ticket):
        if self._agentes_disponiveis:
            # Lógica de sugestão: Apenas sugere, não atribui mais automaticamente.
            # A atribuição manual será feita pela interface.
            agente_sugerido = self._agentes_disponiveis[0]
            print(f"  - SUGESTÃO: O agente {agente_sugerido.nome_completo} é recomendado para este ticket.")
            # ticket.agente_id = self._agentes_disponiveis[0].id_usuario

# --- EXEMPLO 3: PROVISIONAMENTO DE NOVOS USUÁRIOS ---
class ProvisionamentoUsuarioTemplate(ABC):
    """(TEMPLATE) Define o algoritmo para criar e salvar um novo usuário no DB."""
    def provisionar_usuario(self, nome: str, email: str, matricula: str, senha: str, **kwargs) -> Usuario:
        """Template Method que cria e salva o usuário."""
        print(f"Provisionando novo usuário: {nome}...")
        
        # Gera ID único para evitar sobrescritas
        id_usuario = str(uuid.uuid4())

        # Valida unicidade de e-mail
        if UsuarioDAO().get_by_email(email):
            raise ValueError("Já existe um usuário cadastrado com este e-mail.")
        
        usuario = self._criar_conta_base(id_usuario, nome, email, matricula, senha, **kwargs)
        print(f"  - Objeto de usuário criado ({usuario.__class__.__name__}).")
        
        self._atribuir_permissoes_especificas(usuario)
        self._configurar_ambiente(usuario)

        usuario.senha = gerar_hash_senha(senha)
        
        UsuarioDAO().save(usuario)
        
        self._enviar_email_boas_vindas(usuario)
        
        print(f"Provisionamento de '{nome}' concluído e salvo no banco.")
        return usuario

    def _enviar_email_boas_vindas(self, usuario: Usuario):
        print(f"  - Email de boas-vindas enviado para {usuario.email}.")

    def _configurar_ambiente(self, usuario: Usuario):
        pass

    @abstractmethod
    def _criar_conta_base(self, id_usuario: str, nome: str, email: str, matricula: str, senha: str, **kwargs) -> Usuario:
        pass

    @abstractmethod
    def _atribuir_permissoes_especificas(self, usuario: Usuario):
        pass

class ProvisionamentoAgente(ProvisionamentoUsuarioTemplate):
    """(CONCRETO) Provisiona um novo Agente e salva no DB."""
    def _criar_conta_base(self, id_usuario: str, nome: str, email: str, matricula: str, senha: str, **kwargs) -> Agente:
        especialidade = kwargs.get('especialidade', 'Geral')
        return Agente(id_usuario=id_usuario, nome_completo=nome, email=email, matricula=matricula, senha=senha, especialidade=especialidade)

    def _atribuir_permissoes_especificas(self, usuario: Agente):
        print(f"  - Permissões de AGENTE atribuídas: [ver_todos_tickets, atribuir, fechar].")

    def _configurar_ambiente(self, usuario: Agente):
        print(f"  - Ambiente de suporte configurado para o agente.")

class ProvisionamentoSolicitante(ProvisionamentoUsuarioTemplate):
    """(CONCRETO) Provisiona um novo Solicitante e salva no DB."""
    def _criar_conta_base(self, id_usuario: str, nome: str, email: str, matricula: str, senha: str, **kwargs) -> Solicitante:
        return Solicitante(id_usuario=id_usuario, nome_completo=nome, email=email, matricula=matricula, senha=senha)

    def _atribuir_permissoes_especificas(self, usuario: Solicitante):
        print(f"  - Permissões de SOLICITANTE atribuídas: [abrir_ticket, ver_meus_tickets].")

# --- EXEMPLO 2: PROCESSAMENTO DE NOVOS TICKETS (TRIAGEM) ---
# O fluxo pra analisar um ticket novo é o mesmo, mas a lógica de como definir a prioridade ou achar um agente pode mudar com a categoria.

class ProcessadorTicketSoftware(ProcessadorTicketTemplate):
    """(CONCRETO) Lógica de triagem para tickets de software."""
    def __init__(self):
        self._agentes_disponiveis = [
            agente for agente in UsuarioDAO().get_agentes()
            if agente.especialidade and agente.especialidade.lower() == 'software'
        ]

    def _definir_prioridade(self, ticket: Ticket):
        if "urgente" in ticket.descricao.lower():
            ticket.prioridade = PrioridadeTicket.ALTA
        else:
            ticket.prioridade = PrioridadeTicket.BAIXA

    def _atribuir_agente_sugerido(self, ticket: Ticket):
        if self._agentes_disponiveis:
            # Lógica simples: pega o primeiro agente de software disponível
            ticket.agente_id = self._agentes_disponiveis[0].id_usuario