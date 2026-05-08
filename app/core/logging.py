"""
Módulo de Logging (Core)

Configuração centralizada do logger da aplicação.
Utiliza o módulo 'logging' nativo do Python com formato padronizado
incluindo timestamp, nome do logger, nível e mensagem.

O logger 'matricula' é a instância principal e pode ser importada
em qualquer outro módulo da aplicação:

    from app.core.logging import logger
    logger.info("Operação concluída com sucesso")
"""
import logging


def setup_logging():
    """
    Configura o logger raiz com nível INFO e formato padronizado.

    :return: Instância do logger 'matricula' configurada.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("matricula")
    return logger


# Instância singleton do logger, pronta para importação.
logger = setup_logging()
