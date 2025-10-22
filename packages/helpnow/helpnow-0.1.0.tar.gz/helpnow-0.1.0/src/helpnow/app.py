from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from firebase_config import inicializar_firebase
from daos import (
    UsuarioDAO, CategoriaDAO, TicketDAO, EspecialidadeDAO,
    SLADAO, AtivoDAO, FeedbackTicketDAO
)
from modelos_helpdesk import (
    Solicitante, Agente, Categoria, Especialidade, Ticket, Mensagem,
    StatusTicket, PrioridadeTicket, LogObserver,
    NotificacaoEmailObserver, PainelDashboardObserver,
    SLA, Ativo, FeedbackTicket
)
from template_methods import (
    ProvisionamentoAgente, ProvisionamentoSolicitante, 
    ProcessadorTicketHardware, RelatorioTicketsPorStatus
)
from seguranca import gerar_hash_senha, verificar_senha
import os
import uuid
from datetime import datetime

# --- Inicialização do Flask e Firebase ---
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para usar flash messages
inicializar_firebase()

# --- Instâncias dos DAOs ---
usuario_dao = UsuarioDAO()
categoria_dao = CategoriaDAO()
especialidade_dao = EspecialidadeDAO()
ticket_dao = TicketDAO()
sla_dao = SLADAO()
ativo_dao = AtivoDAO()
feedback_dao = FeedbackTicketDAO()


# --- Controle de Autenticação e Sessão ---

def login_required(f):
    """Decorator para exigir que o usuário esteja logado."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Você precisa estar logado para acessar esta página.", 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def agente_required(f):
    """Decorator para exigir que o usuário seja um agente."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') not in ['Agente', 'Admin']:
            flash("Acesso restrito a agentes.", 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator para exigir que o usuário seja um admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') != 'Admin':
            flash("Acesso restrito a administradores.", 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login."""
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        usuario = usuario_dao.get_by_email(email)
        
        valido = False
        precisa_rehash = False
        if usuario:
            valido, precisa_rehash = verificar_senha(senha, usuario.senha)

        if valido:
            session['usuario_id'] = usuario.id_usuario
            session['nome_usuario'] = usuario.nome_completo
            session['tipo_usuario'] = usuario.tipo_usuario
            # Atualiza último login
            if precisa_rehash:
                usuario.senha = gerar_hash_senha(senha)
            usuario.ultimo_login = datetime.now()
            usuario_dao.save(usuario)
            flash(f"Bem-vindo, {usuario.nome_completo}!", 'success')
            
            if usuario.tipo_usuario == 'Agente':
                return redirect(url_for('painel_agente'))
            elif usuario.tipo_usuario == 'Admin':
                return redirect(url_for('painel_agente'))
            else:
                return redirect(url_for('ver_meus_tickets'))
        else:
            flash("E-mail ou senha inválidos.", 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Limpa a sessão do usuário."""
    session.clear()
    flash("Você foi desconectado.", 'info')
    return redirect(url_for('login'))


# --- Rotas da Aplicação Web ---

@app.route('/')
@login_required
def index():
    """Página inicial com o menu de opções."""
    if session['tipo_usuario'] in ['Agente', 'Admin']:
        return redirect(url_for('painel_agente'))
    return redirect(url_for('ver_meus_tickets'))

def seed_admin():
    """Garante a existência de uma conta Admin padrão."""
    admin_email = 'admin@helpnow.local'
    admin = usuario_dao.get_by_email(admin_email)
    if not admin:
        from modelos_helpdesk import Admin
        novo_admin = Admin(
            id_usuario=str(uuid.uuid4()),
            nome_completo='Administrador',
            email=admin_email,
            matricula='000000',
            senha=gerar_hash_senha('admin123')
        )
        usuario_dao.save(novo_admin)
        print('[SEED] Conta Admin criada: admin@helpnow.local / admin123')


@app.route('/usuarios/novo', methods=['GET', 'POST'])
def cadastrar_usuario():
    """Cadastro público apenas para Solicitante."""
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        matricula = request.form['matricula']
        senha = request.form['senha']

        try:
            provisionador = ProvisionamentoSolicitante()
            provisionador.provisionar_usuario(nome, email, matricula, senha)
            flash(f"Solicitante '{nome}' cadastrado com sucesso!", 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), 'danger')
    
    return render_template('cadastrar_usuario.html')

@app.route('/tickets/novo', methods=['GET', 'POST'])
@login_required
def criar_ticket():
    """Página para um solicitante abrir um novo ticket."""
    if session['tipo_usuario'] == 'Agente':
        flash("Agentes não podem criar tickets.", 'warning')
        return redirect(url_for('index'))

    if request.method == 'POST':
        solicitante_id = session['usuario_id']
        categoria_id = request.form['categoria_id']
        assunto = request.form['assunto']
        descricao = request.form['descricao']

        novo_ticket = Ticket(
            id_ticket=str(uuid.uuid4()),
            assunto=assunto,
            descricao=descricao,
            solicitante_id=solicitante_id,
            categoria_id=categoria_id
        )
        
        categoria_selecionada = categoria_dao.get(categoria_id)
        if categoria_selecionada and categoria_selecionada.nome.lower() == 'hardware':
            processador = ProcessadorTicketHardware()
            processador.processar_novo_ticket(novo_ticket)
        else:
            ticket_dao.save(novo_ticket)

        flash(f"Ticket '{assunto}' criado com sucesso!", 'success')
        return redirect(url_for('ver_meus_tickets'))

    categorias = categoria_dao.get_all()
    return render_template('criar_ticket.html', categorias=categorias)

@app.route('/tickets/meus')
@login_required
def ver_meus_tickets():
    """Página para um solicitante ver seus tickets."""
    if session['tipo_usuario'] == 'Agente':
        flash("Agentes não podem ver 'meus tickets'.", 'warning')
        return redirect(url_for('painel_agente'))

    solicitante_id = session['usuario_id']
    solicitante = usuario_dao.get(solicitante_id)
    todos_os_tickets = ticket_dao.get_all()
    tickets = [t for t in todos_os_tickets if t.solicitante_id == solicitante_id]
    feedbacks_existentes = {
        feedback.ticket_id: feedback
        for feedback in feedback_dao.get_all()
        if feedback.solicitante_id == solicitante_id
    }

    return render_template(
        'ver_meus_tickets.html',
        tickets=tickets,
        solicitante=solicitante,
        feedbacks=feedbacks_existentes
    )

@app.route('/tickets/atribuir', methods=['GET', 'POST'])
@login_required
@agente_required
def atribuir_ticket():
    """Página para atribuir um ticket a um agente."""
    agentes = usuario_dao.get_agentes()
    
    # Busca todos os tickets abertos que ainda não têm um agente atribuído.
    todos_os_tickets = ticket_dao.get_all()
    tickets_para_atribuir = [
        t for t in todos_os_tickets 
        if not t.agente_id and t.status == StatusTicket.ABERTO
    ]

    if request.method == 'POST':
        agente_id = request.form['agente_id']
        ticket_id = request.form['ticket_id']

        agente = usuario_dao.get(agente_id)
        ticket = ticket_dao.get(ticket_id)

        if agente and ticket:
            ticket.atribuir_agente(agente)
            ticket_dao.save(ticket)
            flash(f"Ticket atribuído a {agente.nome_completo} com sucesso!", 'success')
        else:
            flash("Agente ou Ticket não encontrado.", 'danger')
        
        return redirect(url_for('index'))

    return render_template('atribuir_ticket.html', agentes=agentes, tickets=tickets_para_atribuir)

@app.route('/tickets/<ticket_id>/mensagem', methods=['GET', 'POST'])
@login_required
def adicionar_mensagem(ticket_id):
    """Página para adicionar uma mensagem a um ticket."""
    detalhes = ticket_dao.get_ticket_com_detalhes(ticket_id)
    if not detalhes:
        flash("Ticket não encontrado.", 'danger')
        return redirect(url_for('index'))

    ticket = detalhes['ticket']
    
    # Validação de permissão
    usuario_id = session['usuario_id']
    if not (usuario_id == ticket.solicitante_id or (session['tipo_usuario'] == 'Agente' and usuario_id == ticket.agente_id)):
        flash("Você não tem permissão para ver este ticket.", 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        autor_id = session['usuario_id']
        texto = request.form['texto']
        
        autor = usuario_dao.get(autor_id)
        if autor:
            nova_mensagem = Mensagem(autor_id=autor.id_usuario, autor_nome=autor.nome_completo, texto=texto)
            ticket.adicionar_mensagem(nova_mensagem)
            ticket_dao.save(ticket)
            flash("Mensagem adicionada com sucesso!", 'success')
        else:
            flash("Autor não encontrado.", 'danger')
        
        return redirect(url_for('adicionar_mensagem', ticket_id=ticket_id))

    return render_template('adicionar_mensagem.html', ticket=ticket, detalhes=detalhes)


@app.route('/tickets/ativos')
@login_required
@agente_required
def painel_agente():
    """Painel do agente com tickets que não estão fechados."""
    todos_os_tickets = ticket_dao.get_all()
    tickets_ativos = [
        t for t in todos_os_tickets 
        if t.status in [StatusTicket.ABERTO, StatusTicket.EM_ANDAMENTO]
    ]
    
    # A função get_ticket_com_detalhes já retorna um dicionário com tudo que precisamos.
    detalhes_tickets = [ticket_dao.get_ticket_com_detalhes(t.id_ticket) for t in tickets_ativos]
    # Filtramos os tickets que não foram encontrados para evitar erros no template.
    detalhes_tickets = [d for d in detalhes_tickets if d]

    return render_template('painel_agente.html', tickets_detalhes=detalhes_tickets)


@app.route('/tickets/<ticket_id>/fechar', methods=['POST'])
@login_required
@agente_required
def fechar_ticket(ticket_id):
    """Rota para fechar um ticket."""
    ticket = ticket_dao.get(ticket_id)
    if ticket and ticket.agente_id == session['usuario_id'] and ticket.status == StatusTicket.EM_ANDAMENTO:
        ticket.attach(LogObserver())
        ticket.attach(NotificacaoEmailObserver())
        
        ticket.fechar_ticket()
        ticket_dao.save(ticket)
        flash(f"Ticket #{ticket.id_ticket[:8]}... fechado com sucesso.", 'success')
    else:
        flash("Você não pode fechar este ticket.", 'danger')
        
    return redirect(url_for('painel_agente'))


@app.route('/tickets/<ticket_id>/avaliar', methods=['GET', 'POST'])
@login_required
def avaliar_ticket(ticket_id):
    """Permite que um solicitante avalie um ticket já encerrado."""
    detalhes = ticket_dao.get_ticket_com_detalhes(ticket_id)
    if not detalhes:
        flash('Ticket não encontrado.', 'danger')
        return redirect(url_for('index'))

    ticket = detalhes['ticket']
    if session.get('tipo_usuario') != 'Solicitante' or session.get('usuario_id') != ticket.solicitante_id:
        flash('Você não tem permissão para avaliar este ticket.', 'danger')
        return redirect(url_for('index'))

    if ticket.status != StatusTicket.FECHADO:
        flash('A avaliação só pode ser feita após o fechamento do ticket.', 'warning')
        return redirect(url_for('ver_meus_tickets'))

    feedback_existente = feedback_dao.get_by_ticket(ticket_id)

    if request.method == 'POST':
        try:
            nota = int(request.form.get('nota', 0))
            if nota < 1 or nota > 5:
                raise ValueError('Selecione uma nota entre 1 e 5.')
            comentario = (request.form.get('comentario') or '').strip() or None

            if feedback_existente:
                feedback_existente.nota = nota
                feedback_existente.comentario = comentario
                feedback_existente.data_criacao = datetime.now()
                feedback_dao.save(feedback_existente)
                flash('Avaliação atualizada com sucesso!', 'success')
            else:
                novo_feedback = FeedbackTicket(
                    id_feedback=str(uuid.uuid4()),
                    ticket_id=ticket.id_ticket,
                    solicitante_id=ticket.solicitante_id,
                    agente_id=ticket.agente_id,
                    nota=nota,
                    comentario=comentario
                )
                feedback_dao.save(novo_feedback)
                flash('Avaliação enviada! Obrigado pelo retorno.', 'success')
        except ValueError as erro:
            flash(str(erro), 'danger')
            return redirect(url_for('avaliar_ticket', ticket_id=ticket_id))

        return redirect(url_for('ver_meus_tickets'))

    return render_template('avaliar_ticket.html', ticket=ticket, detalhes=detalhes, feedback=feedback_existente)


@app.route('/admin/feedbacks')
@login_required
@admin_required
def listar_feedbacks():
    """Apresenta o painel de feedbacks recebidos pelos solicitantes."""
    feedbacks = sorted(feedback_dao.get_all(), key=lambda f: f.data_criacao, reverse=True)
    tickets = {ticket.id_ticket: ticket for ticket in ticket_dao.get_all()}
    usuarios = {usuario.id_usuario: usuario for usuario in usuario_dao.get_all()}
    return render_template(
        'listar_feedbacks.html',
        feedbacks=feedbacks,
        tickets=tickets,
        usuarios=usuarios
    )


@app.route('/relatorios/status')
@login_required
@agente_required
def relatorio_status():
    """Página que exibe o relatório de tickets por status."""
    gerador = RelatorioTicketsPorStatus(ticket_dao) # Passamos a instância do DAO
    relatorio_str = gerador.gerar_relatorio() 
    return render_template('relatorio.html', titulo="Relatório de Tickets por Status", relatorio=relatorio_str)


@app.route('/admin/slas', methods=['GET', 'POST'])
@login_required
@admin_required
def gerenciar_slas():
    """Lista e mantém SLAs utilizados pelo helpdesk."""
    if request.method == 'POST':
        acao = request.form.get('acao', 'criar')
        try:
            if acao == 'criar':
                nome = (request.form.get('nome') or '').strip()
                descricao = (request.form.get('descricao') or '').strip() or None
                tempo_resposta = int(request.form.get('tempo_resposta_horas') or 24)
                tempo_resolucao = int(request.form.get('tempo_resolucao_horas') or 72)
                if not nome:
                    raise ValueError('Informe um nome para o SLA.')
                novo = SLA(
                    id_sla=str(uuid.uuid4()),
                    nome=nome,
                    descricao=descricao,
                    tempo_resposta_horas=tempo_resposta,
                    tempo_resolucao_horas=tempo_resolucao
                )
                sla_dao.save(novo)
                flash(f"SLA '{nome}' criado com sucesso.", 'success')

            elif acao == 'atualizar':
                sla_id = request.form.get('id_sla')
                sla = sla_dao.get(sla_id) if sla_id else None
                if not sla:
                    raise ValueError('SLA não encontrado.')
                sla.nome = (request.form.get('nome') or sla.nome).strip()
                sla.descricao = (request.form.get('descricao') or '').strip() or None
                sla.tempo_resposta_horas = int(request.form.get('tempo_resposta_horas') or sla.tempo_resposta_horas)
                sla.tempo_resolucao_horas = int(request.form.get('tempo_resolucao_horas') or sla.tempo_resolucao_horas)
                status_param = request.form.get('ativo')
                if status_param is None:
                    status_param = 'Ativo' if sla.ativo else 'Inativo'
                sla.ativo = str(status_param).lower() in {'ativo', 'on', 'true', '1', 'sim'}
                sla_dao.save(sla)
                flash('SLA atualizado com sucesso.', 'success')

            elif acao == 'alternar':
                sla_id = request.form.get('id_sla')
                sla = sla_dao.get(sla_id) if sla_id else None
                if not sla:
                    raise ValueError('SLA não encontrado.')
                sla.ativo = not sla.ativo
                sla_dao.save(sla)
                status_txt = 'ativado' if sla.ativo else 'desativado'
                flash(f"SLA '{sla.nome}' {status_txt}.", 'info')

            else:
                raise ValueError('Ação inválida.')
        except ValueError as erro:
            flash(str(erro), 'danger')
        except Exception as erro:
            flash(f'Erro ao processar SLA: {erro}', 'danger')
        return redirect(url_for('gerenciar_slas'))

    slas = sorted(sla_dao.get_all(), key=lambda sla: sla.nome.lower())
    return render_template('gerenciar_slas.html', slas=slas)


@app.route('/admin/slas/<sla_id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_sla(sla_id):
    sla = sla_dao.get(sla_id)
    if not sla:
        flash('SLA não encontrado.', 'danger')
    else:
        sla_dao.delete(sla_id)
        flash(f"SLA '{sla.nome}' removido.", 'info')
    return redirect(url_for('gerenciar_slas'))


@app.route('/admin/ativos', methods=['GET', 'POST'])
@login_required
@admin_required
def gerenciar_ativos():
    """Gerencia ativos de TI associados aos tickets."""
    if request.method == 'POST':
        acao = request.form.get('acao', 'criar')
        try:
            if acao == 'criar':
                nome = (request.form.get('nome') or '').strip()
                if not nome:
                    raise ValueError('Informe um nome para o ativo.')
                quantidade = int(request.form.get('quantidade') or 1)
                novo = Ativo(
                    id_ativo=str(uuid.uuid4()),
                    nome=nome,
                    categoria_id=request.form.get('categoria_id') or None,
                    numero_serie=(request.form.get('numero_serie') or '').strip() or None,
                    status_operacional=request.form.get('status_operacional') or 'Em uso',
                    observacoes=(request.form.get('observacoes') or '').strip() or None,
                    quantidade=quantidade
                )
                ativo_dao.save(novo)
                flash(f"Ativo '{nome}' cadastrado.", 'success')

            elif acao == 'atualizar':
                ativo_id = request.form.get('id_ativo')
                ativo = ativo_dao.get(ativo_id) if ativo_id else None
                if not ativo:
                    raise ValueError('Ativo não encontrado.')
                ativo.nome = (request.form.get('nome') or ativo.nome).strip()
                ativo.categoria_id = request.form.get('categoria_id') or None
                ativo.numero_serie = (request.form.get('numero_serie') or '').strip() or None
                ativo.status_operacional = request.form.get('status_operacional') or ativo.status_operacional
                ativo.observacoes = (request.form.get('observacoes') or '').strip() or None
                ativo.quantidade = int(request.form.get('quantidade') or ativo.quantidade or 1)
                ativo_dao.save(ativo)
                flash('Ativo atualizado.', 'success')
            else:
                raise ValueError('Ação inválida para ativos.')
        except ValueError as erro:
            flash(str(erro), 'danger')
        except Exception as erro:
            flash(f'Erro ao processar ativo: {erro}', 'danger')
        return redirect(url_for('gerenciar_ativos'))

    ativos = sorted(ativo_dao.get_all(), key=lambda ativo: ativo.nome.lower())
    categorias = sorted(categoria_dao.get_all(), key=lambda cat: cat.nome.lower())
    categorias_por_id = {cat.id_categoria: cat.nome for cat in categorias}
    return render_template('gerenciar_ativos.html', ativos=ativos, categorias=categorias, categorias_por_id=categorias_por_id)


@app.route('/admin/ativos/<ativo_id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_ativo(ativo_id):
    ativo = ativo_dao.get(ativo_id)
    if not ativo:
        flash('Ativo não encontrado.', 'danger')
    else:
        ativo_dao.delete(ativo_id)
        flash(f"Ativo '{ativo.nome}' removido.", 'info')
    return redirect(url_for('gerenciar_ativos'))

@app.route('/admin/categorias', methods=['GET', 'POST'])
@login_required
@admin_required
def gerenciar_categorias():
    """Lista e cria categorias."""
    if request.method == 'POST':
        acao = request.form.get('acao', 'criar')
        if acao == 'atualizar':
            categoria_id = request.form.get('id_categoria')
            categoria = categoria_dao.get(categoria_id) if categoria_id else None
            if not categoria:
                flash('Categoria não encontrada.', 'danger')
            else:
                categoria.nome = (request.form.get('nome') or categoria.nome).strip()
                categoria.setor_responsavel = (request.form.get('setor_responsavel') or categoria.setor_responsavel).strip()
                categoria_dao.save(categoria)
                flash('Categoria atualizada com sucesso.', 'success')
        else:
            nome = (request.form.get('nome') or '').strip()
            setor = (request.form.get('setor_responsavel') or '').strip()
            if not nome or not setor:
                flash('Informe nome e setor responsável.', 'danger')
            else:
                from modelos_helpdesk import Categoria
                nova = Categoria(id_categoria=str(uuid.uuid4()), nome=nome, setor_responsavel=setor)
                categoria_dao.save(nova)
                flash(f"Categoria '{nome}' criada.", 'success')
        return redirect(url_for('gerenciar_categorias'))
    categorias = categoria_dao.get_all()
    return render_template('gerenciar_categorias.html', categorias=categorias)

@app.route('/admin/categorias/<cat_id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_categoria(cat_id):
    categoria_dao.delete(cat_id)
    flash('Categoria removida.', 'info')
    return redirect(url_for('gerenciar_categorias'))

@app.route('/admin/usuarios')
@login_required
@admin_required
def gerenciar_usuarios():
    usuarios = usuario_dao.get_all()
    especialidades = sorted(especialidade_dao.get_all(), key=lambda esp: esp.nome.lower())
    return render_template('gerenciar_usuarios.html', usuarios=usuarios, especialidades=especialidades)

@app.route('/admin/usuarios/<user_id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_usuario(user_id):
    from modelos_helpdesk import StatusUsuario
    usuario = usuario_dao.get(user_id)
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('gerenciar_usuarios'))

    usuario.nome_completo = request.form.get('nome_completo', usuario.nome_completo)
    usuario.email = request.form.get('email', usuario.email)
    usuario.matricula = request.form.get('matricula', usuario.matricula)
    usuario.tipo_usuario = request.form.get('tipo_usuario', usuario.tipo_usuario)
    status_str = request.form.get('status_usuario')
    if status_str:
        try:
            usuario.status_usuario = StatusUsuario(status_str)
        except Exception:
            pass
    # Especialidade só faz sentido para Agente
    if usuario.tipo_usuario == 'Agente':
        especialidade_form = request.form.get('especialidade')
        usuario.especialidade = especialidade_form.strip() if especialidade_form else None
    else:
        usuario.especialidade = None
    usuario_dao.save(usuario)
    flash('Usuário atualizado.', 'success')
    return redirect(url_for('gerenciar_usuarios'))


@app.route('/admin/especialidades', methods=['GET', 'POST'])
@login_required
@admin_required
def gerenciar_especialidades():
    """Lista, cria e atualiza especialidades disponíveis para agentes."""
    if request.method == 'POST':
        acao = request.form.get('acao')
        nome = (request.form.get('nome') or '').strip()
        descricao = (request.form.get('descricao') or '').strip()

        if acao == 'criar':
            if not nome:
                flash('Informe um nome para a especialidade.', 'danger')
            else:
                nova = Especialidade(
                    id_especialidade=str(uuid.uuid4()),
                    nome=nome,
                    descricao=descricao or None
                )
                especialidade_dao.save(nova)
                flash(f"Especialidade '{nome}' criada com sucesso.", 'success')

        elif acao == 'atualizar':
            esp_id = request.form.get('id_especialidade')
            especialidade = especialidade_dao.get(esp_id) if esp_id else None
            if not especialidade:
                flash('Especialidade não encontrada.', 'danger')
            elif not nome:
                flash('Informe um nome válido para atualizar a especialidade.', 'danger')
            else:
                especialidade.nome = nome
                especialidade.descricao = descricao or None
                especialidade.ativa = request.form.get('ativa') == 'on'
                especialidade_dao.save(especialidade)
                flash(f"Especialidade '{especialidade.nome}' atualizada.", 'success')
        else:
            flash('Ação inválida.', 'danger')

        return redirect(url_for('gerenciar_especialidades'))

    especialidades = sorted(especialidade_dao.get_all(), key=lambda esp: esp.nome.lower())
    return render_template('gerenciar_especialidades.html', especialidades=especialidades)


@app.route('/admin/especialidades/<esp_id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_especialidade(esp_id):
    especialidade = especialidade_dao.get(esp_id)
    if not especialidade:
        flash('Especialidade não encontrada.', 'danger')
        return redirect(url_for('gerenciar_especialidades'))

    agentes_com_especialidade = [
        agente for agente in usuario_dao.get_agentes()
        if agente.especialidade == especialidade.nome
    ]
    if agentes_com_especialidade:
        flash('Não é possível excluir especialidades atribuídas a agentes. Remova ou atualize os agentes antes.', 'warning')
        return redirect(url_for('gerenciar_especialidades'))

    especialidade_dao.delete(esp_id)
    flash('Especialidade removida com sucesso.', 'info')
    return redirect(url_for('gerenciar_especialidades'))

@app.route('/admin/agentes/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def cadastrar_agente_admin():
    """Cadastro de agente apenas por administradores."""
    especialidades = sorted(especialidade_dao.get_all(), key=lambda esp: esp.nome.lower())
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        matricula = request.form['matricula']
        senha = request.form['senha']
        especialidade_escolhida = (request.form.get('especialidade') or '').strip()
        if especialidade_escolhida == '__personalizada__':
            especialidade_escolhida = (request.form.get('especialidade_personalizada') or '').strip()
        especialidade = especialidade_escolhida or 'Geral'

        nomes_existentes = {esp.nome.lower(): esp for esp in especialidades}
        if especialidade.lower() not in nomes_existentes:
            nova_especialidade = Especialidade(
                id_especialidade=str(uuid.uuid4()),
                nome=especialidade
            )
            especialidade_dao.save(nova_especialidade)
            especialidades.append(nova_especialidade)
        try:
            provisionador = ProvisionamentoAgente()
            provisionador.provisionar_usuario(nome, email, matricula, senha, especialidade=especialidade)
            flash(f"Agente '{nome}' cadastrado com sucesso!", 'success')
            return redirect(url_for('painel_agente'))
        except ValueError as e:
            flash(str(e), 'danger')
    especialidades = sorted(especialidades, key=lambda esp: esp.nome.lower())
    return render_template('cadastrar_agente.html', especialidades=especialidades)


if __name__ == '__main__':
    seed_admin()
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port)
