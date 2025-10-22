from __future__ import annotations
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

# Dependência para conversão de dicionário para objeto e vice-versa
from dacite import from_dict as dacite_from_dict, Config

class StatusTicket(Enum):
    ABERTO = "Aberto"
    EM_ANDAMENTO = "Em Andamento"
    FECHADO = "Fechado"

class PrioridadeTicket(Enum):
    BAIXA = "Baixa"
    MEDIA = "Média"
    ALTA = "Alta"

class StatusUsuario(Enum):
    ATIVO = "Ativo"
    INATIVO = "Inativo"

@dataclass
class Usuario(ABC):
    id_usuario: str
    nome_completo: str
    email: str
    matricula: str
    especialidade: Optional[str] = None # Movido para cá
    senha: Optional[str] = None
    status_usuario: StatusUsuario = StatusUsuario.ATIVO
    ultimo_login: Optional[datetime] = None
    tipo_usuario: str = field(init=False)

    def __post_init__(self):
        # Define o tipo com base no nome da classe filha
        self.tipo_usuario = self.__class__.__name__

    def to_dict(self):
        # dataclasses.asdict não funciona bem com herança complexa, então fazemos manualmente
        data = {
            "id_usuario": self.id_usuario,
            "nome_completo": self.nome_completo,
            "email": self.email,
            "matricula": self.matricula,
            "senha": self.senha,
            "tipo_usuario": self.tipo_usuario,
            "especialidade": self.especialidade,
            "status_usuario": self.status_usuario.value if isinstance(self.status_usuario, Enum) else self.status_usuario,
            "ultimo_login": self.ultimo_login,
            # Adiciona campos específicos da subclasse
            **{k: v for k, v in self.__dict__.items() if k not in Usuario.__annotations__}
        }
        return {k: v for k, v in data.items() if v is not None} # Remove valores None

    @classmethod
    def from_dict(cls, data: dict):
        """
        Cria a instância correta (Agente ou Solicitante) com base no campo 'tipo_usuario'.
        """
        # Normaliza campos novos
        if isinstance(data.get("status_usuario"), str):
            try:
                data["status_usuario"] = StatusUsuario(data["status_usuario"])  # converte string para enum
            except Exception:
                pass

        tipo = data.get("tipo_usuario") or data.get("tipo") # Compatibilidade com dados antigos
        if tipo == "Agente":
            return dacite_from_dict(data_class=Agente, data=data, config=Config(cast=[Enum]))
        elif tipo == "Solicitante":
            return dacite_from_dict(data_class=Solicitante, data=data, config=Config(cast=[Enum]))
        elif tipo == "Admin":
            return dacite_from_dict(data_class=Admin, data=data, config=Config(cast=[Enum]))
        
        # Fallback para dados antigos que podem não ter o campo 'tipo'
        if "especialidade" in data:
            return dacite_from_dict(data_class=Agente, data=data, config=Config(cast=[Enum]))
        else:
            return dacite_from_dict(data_class=Solicitante, data=data, config=Config(cast=[Enum]))

    def __str__(self):
        return f"{self.nome_completo} ({self.matricula})"

@dataclass
class Agente(Usuario):
    # Usa default_factory para garantir que uma nova lista seja criada para cada instância
    tickets_atribuidos: list[str] = field(default_factory=list)

@dataclass
class Solicitante(Usuario):
    pass

@dataclass
class Admin(Usuario):
    pass

@dataclass
class Mensagem:
    autor_id: str
    autor_nome: str
    texto: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {
            "autor_id": self.autor_id,
            "autor_nome": self.autor_nome,
            "texto": self.texto,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict):
        return dacite_from_dict(data_class=cls, data=data)

    def __str__(self):
        return f"[{self.timestamp.strftime('%d/%m/%Y %H:%M')}] {self.autor_nome}: {self.texto}"

class Categoria:
    def __init__(self, id_categoria: str, nome: str, setor_responsavel: str):
        self.id_categoria = id_categoria
        self.nome = nome
        self.setor_responsavel = setor_responsavel

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def __str__(self):
        return f"{self.nome} (Setor: {self.setor_responsavel})"

@dataclass
class Especialidade:
    id_especialidade: str
    nome: str
    descricao: Optional[str] = None
    ativa: bool = True

    def to_dict(self):
        return {
            "id_especialidade": self.id_especialidade,
            "nome": self.nome,
            "descricao": self.descricao,
            "ativa": self.ativa
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_especialidade=data.get("id_especialidade") or data.get("id"),
            nome=data.get("nome", ""),
            descricao=data.get("descricao"),
            ativa=data.get("ativa", True)
        )

    def __str__(self):
        status = "ativa" if self.ativa else "inativa"
        return f"{self.nome} ({status})"

@dataclass
class Ticket:
    id_ticket: str
    assunto: str
    descricao: str
    solicitante_id: str
    categoria_id: str
    agente_id: Optional[str] = None
    status: StatusTicket = StatusTicket.ABERTO
    prioridade: PrioridadeTicket = PrioridadeTicket.MEDIA
    data_criacao: datetime = field(default_factory=datetime.now)
    historico_mensagens: list[Mensagem] = field(default_factory=list)
    _observers: list = field(default_factory=list, init=False, repr=False)

    def to_dict(self):
        return {
            "id_ticket": self.id_ticket,
            "assunto": self.assunto,
            "descricao": self.descricao,
            "solicitante_id": self.solicitante_id,
            "categoria_id": self.categoria_id,
            "agente_id": self.agente_id,
            "status": self.status.value,
            "prioridade": self.prioridade.value,
            "data_criacao": self.data_criacao,
            "historico_mensagens": [msg.to_dict() for msg in self.historico_mensagens]
        }

    @classmethod
    def from_dict(cls, data: dict):
        data['historico_mensagens'] = [Mensagem.from_dict(msg) for msg in data.get('historico_mensagens', [])]
        return dacite_from_dict(data_class=cls, data=data, config=Config(cast=[Enum]))

    def get_solicitante(self) -> Optional[Solicitante]:
        """Busca o objeto Solicitante completo."""
        from daos import UsuarioDAO  # Importação movida para dentro do método
        return UsuarioDAO().get(self.solicitante_id)

    # Métodos do padrão Observer
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def _notify(self):
        # Para notificar, precisamos carregar os objetos completos
        from daos import TicketDAO # Importação tardia para evitar ciclo
        ticket_completo = TicketDAO().get_ticket_com_detalhes(self.id_ticket)
        for observer in self._observers:
            observer.update(ticket_completo)

    def adicionar_mensagem(self, mensagem: Mensagem):
        self.historico_mensagens.append(mensagem)
        # A persistência será feita pelo DAO

    def atribuir_agente(self, agente: Agente):
        self.agente_id = agente.id_usuario
        self.status = StatusTicket.EM_ANDAMENTO
        self._notify()

    def fechar_ticket(self):
        self.status = StatusTicket.FECHADO
        self._notify()

class Observer(ABC):
    @abstractmethod
    def update(self, ticket_com_detalhes: dict):
        pass

class LogObserver(Observer):
    def update(self, ticket_com_detalhes: dict):
        ticket = ticket_com_detalhes['ticket']
        print(f"[LOG] Ticket #{ticket.id_ticket} foi atualizado. Novo status: {ticket.status.value}")

class NotificacaoEmailObserver(Observer):
    def update(self, ticket_com_detalhes: dict):
        ticket = ticket_com_detalhes['ticket']
        solicitante = ticket_com_detalhes['solicitante']
        agente = ticket_com_detalhes.get('agente')

        if ticket.status == StatusTicket.EM_ANDAMENTO and agente:
            assunto = f"Seu ticket #{ticket.id_ticket} está em andamento!"
            corpo = f"Olá, {solicitante.nome_completo},\nO agente {agente.nome_completo} começou a cuidar do seu ticket."
            self._enviar_email(solicitante.email, assunto, corpo)
        
        elif ticket.status == StatusTicket.FECHADO:
            assunto = f"Seu ticket #{ticket.id_ticket} foi resolvido!"
            corpo = f"Olá, {solicitante.nome_completo},\nSeu ticket sobre '{ticket.assunto}' foi resolvido."
            self._enviar_email(solicitante.email, assunto, corpo)

    def _enviar_email(self, para: str, assunto: str, corpo: str):
        print(f"--- [E-MAIL SIMULADO para: {para}] ---")
        print(f"Assunto: {assunto}")
        print(corpo)
        print("------------------------------------------")

class PainelDashboardObserver(Observer):
    def update(self, ticket_com_detalhes: dict):
        ticket = ticket_com_detalhes['ticket']
        print(f"[DASHBOARD] Status do Ticket #{ticket.id_ticket} alterado para '{ticket.status.value}'. Atualizando métricas do sistema.")


@dataclass
class SLA:
    id_sla: str
    nome: str
    descricao: Optional[str] = None
    tempo_resposta_horas: int = 24
    tempo_resolucao_horas: int = 72
    ativo: bool = True

    def to_dict(self):
        return {
            "id_sla": self.id_sla,
            "nome": self.nome,
            "descricao": self.descricao,
            "tempo_resposta_horas": self.tempo_resposta_horas,
            "tempo_resolucao_horas": self.tempo_resolucao_horas,
            "ativo": self.ativo
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_sla=data.get("id_sla") or data.get("id"),
            nome=data.get("nome", ""),
            descricao=data.get("descricao"),
            tempo_resposta_horas=int(data.get("tempo_resposta_horas", 24)),
            tempo_resolucao_horas=int(data.get("tempo_resolucao_horas", 72)),
            ativo=bool(data.get("ativo", True))
        )


@dataclass
class Ativo:
    id_ativo: str
    nome: str
    categoria_id: Optional[str] = None
    numero_serie: Optional[str] = None
    status_operacional: str = "Em uso"
    observacoes: Optional[str] = None
    quantidade: int = 1

    def to_dict(self):
        return {
            "id_ativo": self.id_ativo,
            "nome": self.nome,
            "categoria_id": self.categoria_id,
            "numero_serie": self.numero_serie,
            "status_operacional": self.status_operacional,
            "observacoes": self.observacoes,
            "quantidade": self.quantidade
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_ativo=data.get("id_ativo") or data.get("id"),
            nome=data.get("nome", ""),
            categoria_id=data.get("categoria_id"),
            numero_serie=data.get("numero_serie"),
            status_operacional=data.get("status_operacional", "Em uso"),
            observacoes=data.get("observacoes"),
            quantidade=int(data.get("quantidade", 1))
        )


@dataclass
class FeedbackTicket:
    id_feedback: str
    ticket_id: str
    solicitante_id: str
    agente_id: Optional[str]
    nota: int
    comentario: Optional[str] = None
    data_criacao: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {
            "id_feedback": self.id_feedback,
            "ticket_id": self.ticket_id,
            "solicitante_id": self.solicitante_id,
            "agente_id": self.agente_id,
            "nota": self.nota,
            "comentario": self.comentario,
            "data_criacao": self.data_criacao,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_feedback=data.get("id_feedback") or data.get("id"),
            ticket_id=data.get("ticket_id"),
            solicitante_id=data.get("solicitante_id"),
            agente_id=data.get("agente_id"),
            nota=int(data.get("nota", 0)),
            comentario=data.get("comentario"),
            data_criacao=data.get("data_criacao", datetime.now())
        )
