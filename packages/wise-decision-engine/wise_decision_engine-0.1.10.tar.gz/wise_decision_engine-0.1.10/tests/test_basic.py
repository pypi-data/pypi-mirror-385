"""Testes básicos para verificar se a estrutura do projeto está funcionando."""

import pytest
from wise_decision_engine import __version__


def test_version():
    """Testa se a versão está definida corretamente."""
    # Testa se a versão segue formato semântico
    import re
    assert re.match(r'^\d+\.\d+\.\d+$', __version__), f"Versão {__version__} não segue formato semântico"
    assert __version__ is not None
    assert len(__version__.split('.')) == 3


def test_package_import():
    """Testa se o pacote pode ser importado sem erros."""
    import wise_decision_engine
    
    assert wise_decision_engine is not None
    assert hasattr(wise_decision_engine, '__version__')