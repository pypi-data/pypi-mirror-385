# HelpNow – Plataforma de Helpdesk Inteligente

Aplicação web construída com **Flask** e **Firebase Firestore** para orquestrar o ciclo completo de atendimento interno. O projeto une padrões de projeto clássicos (Singleton, Template Method e Observer) com módulos de governança de SLA, inventário de ativos e retroalimentação dos solicitantes.

## 📌 Sumário

- [Visão geral](#-visão-geral)
- [Principais recursos](#-principais-recursos)
- [Arquitetura e padrões](#-arquitetura-e-padrões)
- [Pré-requisitos](#-pré-requisitos)
- [Configuração do ambiente](#-configuração-do-ambiente)
- [Estrutura do projeto](#-estrutura-do-projeto)
- [Fluxo por perfil de usuário](#-fluxo-por-perfil-de-usuário)
- [Módulos de SLA e inventário](#-módulos-de-sla-e-inventário)
- [Coleções no Firestore](#-coleções-no-firestore)
- [Execução e rotinas úteis](#-execução-e-rotinas-úteis)
- [Próximos passos sugeridos](#-próximos-passos-sugeridos)

## 🌐 Visão geral

| Item | Descrição |
|------|-----------|
| **Stack** | Python 3 · Flask · Jinja2 · Firebase Admin SDK · Firestore |
| **Público-alvo** | Equipes de suporte interno (Service Desk) com necessidade de controle de SLA e ativos |
| **Padrões de projeto** | Singleton (configuração), Template Method (provisionamento/relatórios), Observer (notificações de ticket) |
| **Autenticação** | Sessão Flask com hash de senhas via Passlib (bcrypt) |
| **Deploy sugerido** | App Flask com variáveis de ambiente apontando para credenciais Firebase |

## 🚀 Principais recursos

- **Perfis diferenciados**: Solicitanes abrem e acompanham tickets; Agentes tratam chamados; Administradores gerenciam cadastros, SLAs e ativos.
- **Fluxo de tickets completo**: abertura, atribuição, mensagens, troca de status e fechamento com histórico preservado.
- **Painel do agente**: visão dos tickets em andamento com destaque para chamados atribuídos ao usuário logado.
- **Governança de SLA**: cadastro, edição e (des)ativação de acordos de nível de serviço com tempos de resposta e resolução.
- **Inventário de ativos**: controle de equipamentos/recursos com status operacional e vínculo opcional a categorias de ticket.
- **Gestão administrativa**: telas para categorias, especialidades, usuários e agentes.
- **Feedback pós-atendimento**: solicitantes avaliam tickets encerrados; administradores analisam notas e comentários em um painel dedicado.
- **Relatórios prontos**: geração de relatório de tickets por status utilizando Template Method.

## 🧱 Arquitetura e padrões

- `firebase_config.py`: inicializa o Firestore utilizando **Singleton** para evitar múltiplas inicializações do SDK.
- `template_methods.py`: define ganchos reutilizáveis para provisionamento de perfis e geração de relatórios.
- `modelos_helpdesk.py`: concentra as entidades (Usuario, Ticket, SLA, Ativo, etc.) com conversão automática para Firestore.
- `daos.py`: encapsula o acesso às coleções do Firestore, garantindo isolamento da camada de dados.
- Observers (`LogObserver`, `NotificacaoEmailObserver`, `PainelDashboardObserver`) respondem a mudanças de estado dos tickets.

## 🛠️ Pré-requisitos

- Python 3.9 ou superior.
- Credencial de serviço do Firebase com acesso ao Firestore (`helpnow-89742-firebase-adminsdk-fbsvc-c93ddd8230.json`).
- Conta Firebase habilitada para o Firestore no modo nativo.
- (Opcional) Git para versionamento.

## 🧪 Configuração do ambiente

```bash
# 1. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Exporta variáveis (ajuste o caminho da credencial)
export FLASK_APP=app.py
export FLASK_ENV=development          # habilita recarregamento automático
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/helpnow-89742-firebase-adminsdk-fbsvc-c93ddd8230.json"

# 4. Executa o servidor
flask run --port 5001 --debug
```

> 💡 O módulo `firebase_config.py` também aceita que você altere o caminho do arquivo de credencial, caso prefira carregá-lo via variável de ambiente.

### Semeando um administrador padrão

Ao executar `python app.py`, a função `seed_admin()` cria (caso não exista) o usuário:

| E-mail | Senha |
|--------|-------|
| `admin@helpnow.local` | `admin123` |

Utilize essas credenciais para acessar o painel administrativo na primeira execução.

## 🗂️ Estrutura do projeto

```
├── app.py                    # Rotas Flask e orquestração do fluxo de tickets
├── daos.py                   # Data Access Objects para Firestore
├── firebase_config.py        # Inicialização do Firebase Admin SDK
├── modelos_helpdesk.py       # Entidades e lógica de domínio
├── template_methods.py       # Implementações do padrão Template Method
├── seguranca.py              # Funções de hash/verificação de senhas
├── configuracao_sistema.py   # Singleton para configurações gerais
├── static/
│   └── style.css             # Estilos das páginas
├── templates/                # Telas em Jinja2
│   ├── login.html
│   ├── painel_agente.html
│   ├── gerenciar_slas.html
│   ├── gerenciar_ativos.html
│   ├── ...
└── requirements.txt          # Dependências do projeto
```

## 👥 Fluxo por perfil de usuário

### Solicitanes

1. Cadastram-se em `/usuarios/novo`.
2. Abrem tickets em `/tickets/novo`, selecionando categoria e descrevendo o problema.
3. Acompanham o status em `/tickets/meus`, interagem via mensagens e avaliam o atendimento após o fechamento.

### Agentes

1. Visualizam tickets abertos em `/tickets/ativos`.
2. Recebem atribuição via `/tickets/atribuir` (feita por administradores/agentes autorizados).
3. Adicionam mensagens e encerram os chamados quando resolvidos.

### Administradores

1. Gerenciam usuários, categorias e especialidades.
2. Mantêm cadastros de SLA (`/admin/slas`) e inventário (`/admin/ativos`).
3. Acompanham feedbacks em `/admin/feedbacks` e geram relatórios em `/relatorios/status`.

## 📈 Módulos de SLA e inventário

| Tela | Objetivo | Destaques |
|------|----------|-----------|
| `/admin/slas` | Criar e atualizar acordos de nível de serviço | Definição de tempos de resposta/resolução, ativação em um clique, edição in-line |
| `/admin/ativos` | Controlar recursos de TI | Cadastro rápido, quantidades, status operacional (em uso, estoque, manutenção, descarte) |

Além dessas telas, os cadastros podem ser relacionados às categorias e aos tickets conforme a evolução das regras de negócio.

## 🗃️ Coleções no Firestore

| Coleção | Propósito | Entidade |
|---------|-----------|----------|
| `usuarios` | Perfis de solicitantes, agentes e administradores | `Usuario`, `Agente`, `Solicitante`, `Admin` |
| `categorias` | Assuntos dos tickets e setor responsável | `Categoria` |
| `especialidades` | Habilidades técnicas dos agentes | `Especialidade` |
| `tickets` | Chamados com histórico de mensagens, status e atribuições | `Ticket` |
| `slas` | Acordos de nível de serviço | `SLA` |
| `ativos` | Inventário de hardware/software | `Ativo` |
| `feedbacks` | Avaliações dos solicitantes após o fechamento | `FeedbackTicket` |

## 🏃 Execução e rotinas úteis

- **Executar em modo script**: `python app.py` (executa seed do admin e roda em modo debug na porta 5001).
- **Relatório por status**: acesse `/relatorios/status` para gerar a visão consolidada de chamados.
- **Exportar dependências**: mantenha o arquivo `requirements.txt` atualizado com `pip freeze > requirements.txt` sempre que adicionar novas bibliotecas.

## 🔮 Próximos passos sugeridos

- Integrar SLAs automaticamente na criação de tickets, calculando prazos estimados de resposta/resolução.
- Permitir vincular ativos diretamente a tickets e gerar alertas de baixa disponibilidade.
- Adicionar testes automatizados (PyTest) para fluxos críticos.
- Publicar o frontend com estética responsiva (Bootstrap/Tailwind) e internacionalização.

---

Feito com 💙 para apoiar times de suporte na disciplina de Linha de Produto de Software. Ajuste, estenda e recombine os módulos conforme as variações desejadas da plataforma HelpNow.
