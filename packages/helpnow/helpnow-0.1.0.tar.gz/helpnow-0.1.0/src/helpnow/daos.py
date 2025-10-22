from firebase_config import db
from modelos_helpdesk import (
    Usuario, Agente, Solicitante, Categoria, Ticket, Mensagem, StatusTicket,
    Especialidade, SLA, Ativo, FeedbackTicket
)
from typing import Type, Union

class BaseDAO:
    def __init__(self, collection_name: str, model_class: Type):
        self.collection = db.collection(collection_name)
        self.model_class = model_class

    def save(self, instance):
        """Salva (cria ou atualiza) uma instância no Firestore."""
        doc_id = self._extract_doc_id(instance)
        if not doc_id:
            raise AttributeError(f"Instância {instance} não possui um identificador suportado.")
        doc_ref = self.collection.document(doc_id)
        doc_ref.set(instance.to_dict())
        print(f"[{self.__class__.__name__}] Objeto '{doc_ref.id}' salvo na coleção '{self.collection.id}'.")
        return instance

    def get(self, doc_id: str):
        """Busca um documento pelo seu ID."""
        doc = self.collection.document(doc_id).get()
        if doc.exists:
            return self.model_class.from_dict(doc.to_dict())
        return None

    def get_all(self):
        """Retorna todos os documentos de uma coleção."""
        docs = self.collection.stream()
        return [self.model_class.from_dict(doc.to_dict()) for doc in docs]

    def delete(self, doc_id: str):
        """Remove um documento pelo ID."""
        self.collection.document(doc_id).delete()
        print(f"[{self.__class__.__name__}] Objeto '{doc_id}' removido da coleção '{self.collection.id}'.")

    def _extract_doc_id(self, instance):
        for attr in ('id_usuario', 'id_categoria', 'id_ticket', 'id_especialidade', 'id_sla', 'id_ativo', 'id_feedback'):
            if hasattr(instance, attr):
                return getattr(instance, attr)
        return None

class UsuarioDAO(BaseDAO):
    def __init__(self):
        super().__init__("usuarios", Usuario)

    def get_agentes(self):
        """Retorna todos os usuários que são agentes."""
        agentes_query = self.collection.where("tipo_usuario", "==", "Agente").stream()
        return [Agente.from_dict(agente.to_dict()) for agente in agentes_query]

    def get_by_email(self, email: str) -> Union[Usuario, None]:
        """Busca um usuário pelo seu endereço de e-mail."""
        user_query = self.collection.where("email", "==", email).limit(1).stream()
        users = [self.model_class.from_dict(user.to_dict()) for user in user_query]
        return users[0] if users else None

    def get_by_id(self, user_id: str) -> Union[Usuario, None]:
        return self.get(user_id)

class CategoriaDAO(BaseDAO):
    def __init__(self):
        super().__init__("categorias", Categoria)

class EspecialidadeDAO(BaseDAO):
    def __init__(self):
        super().__init__("especialidades", Especialidade)


class SLADAO(BaseDAO):
    def __init__(self):
        super().__init__("slas", SLA)


class AtivoDAO(BaseDAO):
    def __init__(self):
        super().__init__("ativos", Ativo)


class FeedbackTicketDAO(BaseDAO):
    def __init__(self):
        super().__init__("feedbacks", FeedbackTicket)

    def get_by_ticket(self, ticket_id: str):
        feedback_query = self.collection.where("ticket_id", "==", ticket_id).limit(1).stream()
        itens = [self.model_class.from_dict(doc.to_dict()) for doc in feedback_query]
        return itens[0] if itens else None

    def get_por_agente(self, agente_id: str):
        feedback_query = self.collection.where("agente_id", "==", agente_id).stream()
        return [self.model_class.from_dict(doc.to_dict()) for doc in feedback_query]

class TicketDAO(BaseDAO):
    def __init__(self):
        super().__init__("tickets", Ticket)
        self.usuario_dao = UsuarioDAO()
        self.categoria_dao = CategoriaDAO()

    def save(self, ticket: Ticket):
        """Salva um ticket, garantindo que o ID seja uma string."""
        if not ticket.id_ticket:
            # Gera um ID automático do Firestore
            doc_ref = self.collection.document()
            ticket.id_ticket = doc_ref.id
        else:
            # Garante que o ID seja string para consistência
            ticket.id_ticket = str(ticket.id_ticket)
            
        super().save(ticket)
        return ticket

    def get_ticket_com_detalhes(self, ticket_id: str) -> Union[dict, None]:
        """
        Retorna um dicionário com o ticket e seus objetos relacionados
        (solicitante, categoria, agente).
        """
        ticket = self.get(ticket_id)
        if not ticket:
            return None

        solicitante = self.usuario_dao.get(ticket.solicitante_id)
        categoria = self.categoria_dao.get(ticket.categoria_id)
        agente = self.usuario_dao.get(ticket.agente_id) if ticket.agente_id else None

        return {
            "ticket": ticket,
            "solicitante": solicitante,
            "categoria": categoria,
            "agente": agente
        }

    def get_tickets_por_status(self, status: StatusTicket):
        """Busca tickets filtrando por status."""
        tickets_query = self.collection.where("status", "==", status.value).stream()
        return [self.model_class.from_dict(ticket.to_dict()) for ticket in tickets_query]
