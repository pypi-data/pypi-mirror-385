from passlib.context import CryptContext

_pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    default="pbkdf2_sha256",
    deprecated="auto"
)

_BCRYPT_MAX_BYTES = 71  # usado apenas para compatibilidade com hashes antigos em bcrypt


def _normalizar_senha(senha_clara: str) -> str:
    """Normaliza a senha para evitar erros de tamanho do bcrypt (máx. 72 bytes)."""
    if senha_clara is None:
        return ""
    senha_bytes = senha_clara.encode("utf-8")
    if len(senha_bytes) <= _BCRYPT_MAX_BYTES:
        return senha_clara
    senha_truncada = senha_bytes[:_BCRYPT_MAX_BYTES]
    return senha_truncada.decode("utf-8", errors="ignore")


def gerar_hash_senha(senha_clara: str) -> str:
    """Gera um hash seguro para a senha fornecida."""
    if not senha_clara:
        raise ValueError("Senha não pode ser vazia para geração de hash.")
    senha_normalizada = _normalizar_senha(senha_clara)
    return _pwd_context.hash(senha_normalizada)


def verificar_senha(senha_clara: str, senha_armazenada: str) -> tuple[bool, bool]:
    """Verifica uma senha em texto claro contra o valor armazenado.

    Retorna uma tupla (valido, precisa_rehash), onde:
      - valido: True se a senha confere
      - precisa_rehash: True se o hash precisa ser atualizado (ou se estava em texto plano)
    """
    if not senha_armazenada:
        return False, False

    senha_normalizada = _normalizar_senha(senha_clara)

    try:
        valido = _pwd_context.verify(senha_normalizada, senha_armazenada)
        if not valido:
            return False, False
        return True, _pwd_context.needs_update(senha_armazenada)
    except ValueError:
        # Valor armazenado não é um hash válido (provavelmente texto plano legado)
        if senha_normalizada == senha_armazenada:
            return True, True
        return False, False