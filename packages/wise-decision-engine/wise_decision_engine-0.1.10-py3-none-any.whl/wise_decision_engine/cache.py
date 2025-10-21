"""Sistema de cache inteligente para decisões do WiseDecisionEngine.

Implementa cache de sessão focado em performance sem comprometer atualizações:
- Session Cache: Cache válido apenas durante a sessão atual
- Broadcast Cache: Compartilhamento eficiente entre executors Spark
- Auto-refresh: Limpa automaticamente em novas sessões
- Métricas de performance
"""

import json
import time
import threading
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum


class CacheStrategy(Enum):
    """Estratégias de cache disponíveis."""
    SESSION = "session"  # Cache de sessão (padrão)
    BROADCAST = "broadcast"  # Cache distribuído via broadcast
    NONE = "none"  # Sem cache


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
    
    @property
    def miss_rate(self) -> float:
        """Taxa de miss do cache."""
        return 100.0 - self.hit_rate
    
    def reset(self):
        """Reseta todas as métricas."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.total_size = 0


@dataclass
class SessionEntry:
    """Entrada do cache de sessão - simples e eficiente."""
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


class DecisionCache(ABC):
    """Interface abstrata para cache de decisões."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Busca decisão no cache."""
        pass
    
    @abstractmethod
    def put(self, key: str, content: Dict[str, Any]) -> None:
        """Armazena decisão no cache."""
        pass
    
    @abstractmethod
    def invalidate(self, key: str) -> bool:
        """Remove decisão do cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Limpa todo o cache."""
        pass
    
    @abstractmethod
    def get_metrics(self) -> CacheMetrics:
        """Retorna métricas do cache."""
        pass


class SessionCache(DecisionCache):
    """
    Cache de sessão - válido apenas durante a sessão atual.
    
    Funcionalidades:
    - Auto-refresh em novas sessões (notebook restart, novo job)
    - Thread-safe para uso concorrente
    - Zero risco de usar versões desatualizadas entre sessões
    - Performance máxima dentro da mesma sessão
    """
    
    def __init__(self, max_size: int = 50):
        """
        Inicializa cache de sessão.
        
        Args:
            max_size: Número máximo de decisões em cache
        """
        self.max_size = max_size
        self._cache: Dict[str, SessionEntry] = {}
        self._lock = threading.RLock()
        self._metrics = CacheMetrics()
        self._session_id = self._get_current_session_id()
    
    def _get_current_session_id(self) -> str:
        """
        Gera ID único para a sessão atual.
        
        Combina PID + timestamp de início para detectar reinicializações.
        """
        import os
        import psutil
        
        try:
            # PID + timestamp de criação do processo = sessão única
            process = psutil.Process(os.getpid())
            create_time = process.create_time()
            return f"{os.getpid()}_{create_time:.0f}"
        except:
            # Fallback simples se psutil não estiver disponível
            return f"{os.getpid()}_{time.time():.0f}"
    
    def _check_session_validity(self) -> None:
        """
        Verifica se ainda estamos na mesma sessão.
        Se não, limpa o cache automaticamente.
        """
        current_session = self._get_current_session_id()
        if current_session != self._session_id:
            # Nova sessão detectada - limpa cache
            old_size = len(self._cache)
            self._cache.clear()
            self._session_id = current_session
            
            if old_size > 0:
                self._metrics.evictions += old_size
                # Log da limpeza automática (opcional)
                print(f"⚙️ Session cache auto-cleared: {old_size} entries (new session detected)")
    
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
        """Remove decisão do cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Limpa todo o cache."""
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


class BroadcastCache(DecisionCache):
    """
    Cache distribuído usando broadcast variables do Spark.
    
    Ideal para ambientes Spark/Databricks onde a mesma decisão
    é compartilhada entre múltiplos executors durante um job.
    
    Funcionalidades:
    - Compartilhamento eficiente via broadcast variables
    - Válido apenas durante o job/sessão atual
    - Cleanup automático de broadcast variables
    """
    
    def __init__(self, spark_context=None):
        """
        Inicializa cache distribuído.
        
        Args:
            spark_context: SparkContext para broadcast (obtém automaticamente se None)
        """
        self.spark_context = spark_context
        self._broadcast_vars: Dict[str, Any] = {}
        self._metrics = CacheMetrics()
        self._lock = threading.RLock()
    
    def _get_spark_context(self):
        """Obtém SparkContext ativo."""
        if self.spark_context:
            return self.spark_context
        
        try:
            from pyspark import SparkContext
            sc = SparkContext._active_spark_context
            if sc is None:
                raise Exception("Nenhum SparkContext ativo encontrado")
            return sc
        except ImportError:
            raise Exception("PySpark não está disponível")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Busca decisão no cache distribuído."""
        with self._lock:
            if key not in self._broadcast_vars:
                self._metrics.misses += 1
                return None
            
            try:
                broadcast_var = self._broadcast_vars[key]
                content = broadcast_var.value
                self._metrics.hits += 1
                return content.copy()
            except Exception:
                # Broadcast variable pode ter sido invalidada
                del self._broadcast_vars[key]
                self._metrics.misses += 1
                return None
    
    def put(self, key: str, content: Dict[str, Any]) -> None:
        """Armazena decisão no cache distribuído."""
        with self._lock:
            # Remove broadcast existente se houver
            if key in self._broadcast_vars:
                try:
                    self._broadcast_vars[key].destroy()
                except:
                    pass  # Ignora erros de cleanup
            
            # Cria novo broadcast variable
            sc = self._get_spark_context()
            broadcast_var = sc.broadcast(content.copy())
            self._broadcast_vars[key] = broadcast_var
    
    def invalidate(self, key: str) -> bool:
        """Remove decisão do cache distribuído."""
        with self._lock:
            if key in self._broadcast_vars:
                try:
                    self._broadcast_vars[key].destroy()
                except:
                    pass  # Ignora erros de cleanup
                del self._broadcast_vars[key]
                return True
            return False
    
    def clear(self) -> None:
        """Limpa todo o cache distribuído."""
        with self._lock:
            for broadcast_var in self._broadcast_vars.values():
                try:
                    broadcast_var.destroy()
                except:
                    pass  # Ignora erros de cleanup
            
            evicted_count = len(self._broadcast_vars)
            self._broadcast_vars.clear()
            self._metrics.evictions += evicted_count
    
    def get_metrics(self) -> CacheMetrics:
        """Retorna métricas do cache distribuído."""
        with self._lock:
            return CacheMetrics(
                hits=self._metrics.hits,
                misses=self._metrics.misses,
                evictions=self._metrics.evictions,
                total_size=len(self._broadcast_vars)
            )
    """
    Cache distribuído usando broadcast variables do Spark.
    
    Ideal para ambientes Spark/Databricks onde a mesma decisão
    é usada por múltiplos workers/executors.
    """
    
    def __init__(self, spark_context=None):
        """
        Inicializa cache distribuído.
        
        Args:
            spark_context: SparkContext para broadcast (obtido automaticamente se None)
        """
        self.spark_context = spark_context
        self._broadcast_vars: Dict[str, Any] = {}
        self._metrics = CacheMetrics()
        self._lock = threading.RLock()
    
    def _get_spark_context(self):
        """Obtém SparkContext ativo."""
        if self.spark_context:
            return self.spark_context
        
        try:
            from pyspark import SparkContext
            sc = SparkContext._active_spark_context
            if sc is None:
                raise Exception("Nenhum SparkContext ativo encontrado")
            return sc
        except ImportError:
            raise Exception("PySpark não está disponível")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Busca decisão no cache distribuído."""
        with self._lock:
            if key not in self._broadcast_vars:
                self._metrics.misses += 1
                return None
            
            try:
                broadcast_var = self._broadcast_vars[key]
                content = broadcast_var.value
                self._metrics.hits += 1
                return content.copy()
            except Exception:
                # Broadcast variable pode ter sido invalidada
                del self._broadcast_vars[key]
                self._metrics.misses += 1
                return None
    
    def put(self, key: str, content: Dict[str, Any]) -> None:
        """Armazena decisão no cache distribuído."""
        with self._lock:
            # Remove broadcast existente
            if key in self._broadcast_vars:
                try:
                    self._broadcast_vars[key].destroy()
                except:
                    pass  # Ignora erros de cleanup
            
            # Cria novo broadcast variable
            sc = self._get_spark_context()
            broadcast_var = sc.broadcast(content.copy())
            self._broadcast_vars[key] = broadcast_var
            self._update_size_metrics()
    
    def invalidate(self, key: str) -> bool:
        """Remove decisão do cache distribuído."""
        with self._lock:
            if key in self._broadcast_vars:
                try:
                    self._broadcast_vars[key].destroy()
                except:
                    pass  # Ignora erros de cleanup
                del self._broadcast_vars[key]
                self._update_size_metrics()
                return True
            return False
    
    def clear(self) -> None:
        """Limpa todo o cache distribuído."""
        with self._lock:
            for broadcast_var in self._broadcast_vars.values():
                try:
                    broadcast_var.destroy()
                except:
                    pass  # Ignora erros de cleanup
            
            evicted_count = len(self._broadcast_vars)
            self._broadcast_vars.clear()
            self._metrics.evictions += evicted_count
            self._update_size_metrics()
    
    def get_metrics(self) -> CacheMetrics:
        """Retorna métricas do cache distribuído."""
        with self._lock:
            self._update_size_metrics()
            return CacheMetrics(
                hits=self._metrics.hits,
                misses=self._metrics.misses,
                evictions=self._metrics.evictions,
                total_size=self._metrics.total_size
            )
    
    def _update_size_metrics(self) -> None:
        """Atualiza métricas de tamanho."""
        self._metrics.total_size = len(self._broadcast_vars)


class NoCache(DecisionCache):
    """Cache nulo - não armazena nada (para testes/debug)."""
    
    def __init__(self):
        self._metrics = CacheMetrics()
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Sempre retorna None (cache miss)."""
        self._metrics.misses += 1
        return None
    
    def put(self, key: str, content: Dict[str, Any]) -> None:
        """Não armazena nada."""
        pass
    
    def invalidate(self, key: str) -> bool:
        """Sempre retorna False."""
        return False
    
    def clear(self) -> None:
        """Não faz nada."""
        pass
    
    def get_metrics(self) -> CacheMetrics:
        """Retorna métricas zeradas."""
        return CacheMetrics(
            hits=self._metrics.hits,
            misses=self._metrics.misses
        )


class CacheManager:
    """
    Gerenciador central de cache com suporte a múltiplas estratégias.
    
    Facilita o uso e configuração de diferentes tipos de cache.
    """
    
    def __init__(self, 
                 strategy: Union[CacheStrategy, str] = CacheStrategy.SESSION,
                 **kwargs):
        """
        Inicializa gerenciador de cache.
        
        Args:
            strategy: Estratégia de cache a usar
            **kwargs: Parâmetros específicos da estratégia
        """
        if isinstance(strategy, str):
            strategy = CacheStrategy(strategy)
        
        self.strategy = strategy
        self._cache = self._create_cache(strategy, **kwargs)
    
    def _create_cache(self, strategy: CacheStrategy, **kwargs) -> DecisionCache:
        """Cria instância de cache baseada na estratégia."""
        if strategy == CacheStrategy.SESSION:
            return SessionCache(**kwargs)
        elif strategy == CacheStrategy.BROADCAST:
            return BroadcastCache(**kwargs)
        elif strategy == CacheStrategy.NONE:
            return NoCache()
        else:
            raise ValueError(f"Estratégia de cache inválida: {strategy}")
    
    def get_decision(self, key: str) -> Optional[Dict[str, Any]]:
        """Busca decisão no cache."""
        return self._cache.get(key)
    
    def cache_decision(self, key: str, content: Dict[str, Any]) -> None:
        """Armazena decisão no cache."""
        self._cache.put(key, content)
    
    def invalidate_decision(self, key: str) -> bool:
        """Remove decisão do cache."""
        return self._cache.invalidate(key)
    
    def clear_cache(self) -> None:
        """Limpa todo o cache."""
        self._cache.clear()
    
    def get_cache_metrics(self) -> CacheMetrics:
        """Retorna métricas do cache."""
        return self._cache.get_metrics()
    
    def print_metrics(self) -> None:
        """Imprime métricas formatadas."""
        metrics = self.get_cache_metrics()
        print(f"📊 Cache Metrics ({self.strategy.value}):")
        print(f"   Hit Rate: {metrics.hit_rate:.1f}%")
        print(f"   Hits: {metrics.hits}")
        print(f"   Misses: {metrics.misses}")
        print(f"   Evictions: {metrics.evictions}")
        print(f"   Total Size: {metrics.total_size}")


# Instância global padrão (pode ser reconfigurada)
_default_cache_manager = CacheManager(CacheStrategy.SESSION)


def get_default_cache() -> CacheManager:
    """Retorna instância padrão do cache manager."""
    return _default_cache_manager


def set_default_cache(strategy: Union[CacheStrategy, str], **kwargs) -> None:
    """Configura cache padrão global."""
    global _default_cache_manager
    _default_cache_manager = CacheManager(strategy, **kwargs)


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