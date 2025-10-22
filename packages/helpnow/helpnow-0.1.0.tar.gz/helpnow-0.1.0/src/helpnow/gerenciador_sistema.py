from datetime import datetime
from configuracao_sistema import ConfiguracaoSistema

class GerenciadorBackup:
    """
    Singleton para controlar o processo de backup.
    Isso evita que múltiplos backups sejam disparados ao mesmo tempo.
    """
    _instancia = None
    _log_ultima_execucao = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    def executar_backup(self):
        config = ConfiguracaoSistema()
        agendamento = config.obter_config("BACKUP_SCHEDULE")

        print(f"Iniciando backup do sistema (agendamento: {agendamento})...")
        # Lógica de backup aqui
        print("Backup concluído com sucesso.")
        self._log_ultima_execucao = f"Backup finalizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

    def get_log_ultima_execucao(self):
        return self._log_ultima_execucao or "Nenhum backup executado ainda."