class ConfiguracaoSistema:
    """
    Singleton para gerenciar as configurações globais do sistema.
    Isso garante que valores como dados do BD e timeouts sejam lidos uma só vez.
    """
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._configuracoes = {
                "DATABASE_URL": "firebase://helpdesk-prod",
                "SESSION_TIMEOUT_SECONDS": 7200,
                "BACKUP_SCHEDULE": "daily@02:00"
            }
        return cls._instancia

    def obter_config(self, chave: str):
        return self._configuracoes.get(chave)