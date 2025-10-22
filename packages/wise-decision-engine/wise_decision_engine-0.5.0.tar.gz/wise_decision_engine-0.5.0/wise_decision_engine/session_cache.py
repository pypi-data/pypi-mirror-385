"""
Sistema de cache de sessão para WiseDecisionEngine.

Implementa cache inteligente focado em performance sem comprometer atualizações:
- Session Cache: Válido apenas durante a sessão atual (notebook/job)
- Auto-refresh: Limpa automaticamente quando reinicia sessão  
- Thread-safe: Seguro para uso concorrente
- Zero risco: Sempre usa versão atual entre diferentes execuções
"""

import json
import time
import threading
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


@dataclass
class CacheMetrics:
    """Métricas de performance do cache."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Taxa de acerto do cache."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    def reset(self):
        """Reseta todas as métricas."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.total_size = 0


@dataclass
class SessionEntry:
    """Entrada do cache de sessão."""
    content: Dict[str, Any]
    session_id: str
    created_at: float
    access_count: int = 0
    
    def touch(self):
        """Atualiza contador de acesso."""
        self.access_count += 1
    
    def is_valid_for_session(self, current_session_id: str) -> bool:
        """Verifica se entrada é válida para a sessão atual."""
        return self.session_id == current_session_id


class SessionCache:
    """
    Cache de sessão - válido apenas durante a sessão atual.
    
    Funcionalidades:
    - Auto-refresh em novas sessões (notebook restart, novo job)
    - Thread-safe para uso concorrente
    - Zero risco de usar versões desatualizadas entre sessões
    - Performance máxima dentro da mesma sessão
    
    Perfeito para Databricks/Spark onde:
    - Dentro de um job: máxima performance (cache hit)
    - Entre jobs: sempre versão atual (cache miss = reload)
    """
    
    def __init__(self, max_size: int = 50, enable_logging: bool = True):
        """
        Inicializa cache de sessão.
        
        Args:
            max_size: Número máximo de decisões em cache
            enable_logging: Habilita logs de limpeza automática
        """
        self.max_size = max_size
        self.enable_logging = enable_logging
        self._cache: Dict[str, SessionEntry] = {}
        self._lock = threading.RLock()
        self._metrics = CacheMetrics()
        self._session_id = self._get_current_session_id()
    
    def _get_current_session_id(self) -> str:
        """
        Gera ID único para a sessão atual.
        
        Combina PID + timestamp de início para detectar reinicializações.
        Funciona para:
        - Notebook Databricks (reinicialização = nova sessão)
        - Jobs Spark (novo job = nova sessão)
        - Desenvolvimento local (restart = nova sessão)
        """
        try:
            import psutil
            # PID + timestamp de criação do processo = sessão única
            process = psutil.Process(os.getpid())
            create_time = process.create_time()
            return f"{os.getpid()}_{create_time:.0f}"
        except ImportError:
            # Fallback se psutil não estiver disponível
            return f"{os.getpid()}_{time.time():.0f}"
    
    def _check_session_validity(self) -> None:
        """
        Verifica se ainda estamos na mesma sessão.
        Se não, limpa o cache automaticamente.
        
        Isso garante que:
        - Reiniciar notebook = cache limpo = versão atual
        - Novo job Spark = cache limpo = versão atual  
        - Mesmo job/sessão = cache hit = máxima performance
        """
        current_session = self._get_current_session_id()
        if current_session != self._session_id:
            # Nova sessão detectada - limpa cache
            old_size = len(self._cache)
            self._cache.clear()
            self._session_id = current_session
            
            if old_size > 0:
                self._metrics.evictions += old_size
                if self.enable_logging:
                    print(f"🔄 Session cache refreshed: {old_size} decisions cleared (new session detected)")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Busca decisão no cache de sessão."""
        with self._lock:
            # Verifica validade da sessão primeiro
            self._check_session_validity()
            
            if key not in self._cache:
                self._metrics.misses += 1
                return None
            
            entry = self._cache[key]
            
            # Dupla verificação de sessão (paranoia, mas seguro)
            if not entry.is_valid_for_session(self._session_id):
                del self._cache[key]
                self._metrics.misses += 1
                return None
            
            # Cache hit - atualiza métricas
            entry.touch()
            self._metrics.hits += 1
            return entry.content.copy()  # Retorna cópia segura
    
    def put(self, key: str, content: Dict[str, Any]) -> None:
        """Armazena decisão no cache de sessão."""
        with self._lock:
            # Verifica validade da sessão
            self._check_session_validity()
            
            # Remove entrada existente se houver
            if key in self._cache:
                del self._cache[key]
            
            # Faz eviction se necessário (simples FIFO)
            while len(self._cache) >= self.max_size:
                # Remove entrada mais antiga
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._metrics.evictions += 1
            
            # Adiciona nova entrada
            entry = SessionEntry(
                content=content.copy(),
                session_id=self._session_id,
                created_at=time.time()
            )
            self._cache[key] = entry
    
    def invalidate(self, key: str) -> bool:
        """Remove decisão específica do cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Limpa todo o cache manualmente."""
        with self._lock:
            evicted_count = len(self._cache)
            self._cache.clear()
            self._metrics.evictions += evicted_count
    
    def get_metrics(self) -> CacheMetrics:
        """Retorna métricas do cache."""
        with self._lock:
            return CacheMetrics(
                hits=self._metrics.hits,
                misses=self._metrics.misses,
                evictions=self._metrics.evictions,
                total_size=len(self._cache)
            )
    
    def print_metrics(self) -> None:
        """Imprime métricas formatadas."""
        metrics = self.get_metrics()
        print(f"📊 Session Cache Metrics:")
        print(f"   Hit Rate: {metrics.hit_rate:.1f}%")
        print(f"   Hits: {metrics.hits}")
        print(f"   Misses: {metrics.misses}")
        print(f"   Cache Size: {metrics.total_size}")
        print(f"   Auto-evictions: {metrics.evictions}")


# Instância global padrão
_default_session_cache = SessionCache()


def get_default_session_cache() -> SessionCache:
    """Retorna instância padrão do session cache."""
    return _default_session_cache


def set_default_session_cache(max_size: int = 50, enable_logging: bool = True) -> None:
    """Configura session cache padrão global."""
    global _default_session_cache
    _default_session_cache = SessionCache(max_size, enable_logging)


def create_cache_key(source: str, identifier: str) -> str:
    """
    Cria chave de cache padronizada.
    
    Args:
        source: Tipo de fonte (file, databricks, etc.)
        identifier: Identificador único da decisão
        
    Returns:
        Chave de cache formatada
    """
    return f"{source}:{identifier}"