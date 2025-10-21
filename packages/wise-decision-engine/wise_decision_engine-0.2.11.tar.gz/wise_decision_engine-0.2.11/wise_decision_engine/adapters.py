"""
Adaptadores para diferentes fontes de dados de decisões.

Permite carregar decisões do zen-engine a partir de:
- Databricks (tabelas)
- Arquivos locais (JSON/YAML)
- Bancos de dados relacionais
- APIs REST
"""

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .session_cache import get_default_session_cache, create_cache_key


class DecisionAdapter(ABC):
    """
    Interface abstrata para adaptadores de fontes de dados.
    
    Todos os adaptadores devem implementar esta interface para garantir
    compatibilidade com o WiseDecisionEngine.
    """
    
    def __init__(self, enable_cache: bool = True, session_cache=None):
        """
        Inicializa adaptador base.
        
        Args:
            enable_cache: Habilita cache de sessão
            session_cache: Instância de SessionCache customizada (usa padrão se None)
        """
        self.enable_cache = enable_cache
        self.session_cache = session_cache or get_default_session_cache()
        self._source_name = self.__class__.__name__.replace('Adapter', '').lower()
    
    @abstractmethod
    def get_decision(self, decision_name: str) -> Dict[str, Any]:
        """
        Busca uma decisão pelo nome.
        
        Args:
            decision_name: Nome/identificador da decisão
            
        Returns:
            Dict com o conteúdo da decisão
            
        Raises:
            ValueError: Se a decisão não for encontrada
            Exception: Para outros erros de conexão/acesso
        """
        pass
    
    @abstractmethod
    def list_decisions(self) -> List[str]:
        """
        Lista todas as decisões disponíveis.
        
        Returns:
            Lista com os nomes das decisões disponíveis
        """
        pass
    
    def _get_cached_decision(self, decision_name: str) -> Optional[Dict[str, Any]]:
        """
        Busca decisão no cache se habilitado.
        
        Args:
            decision_name: Nome da decisão
            
        Returns:
            Conteúdo da decisão se encontrada no cache, None caso contrário
        """
        if not self.enable_cache:
            return None
        
        cache_key = create_cache_key(self._source_name, decision_name)
        return self.session_cache.get(cache_key)
    
    def _cache_decision(self, decision_name: str, content: Dict[str, Any]) -> None:
        """
        Armazena decisão no cache se habilitado.
        
        Args:
            decision_name: Nome da decisão
            content: Conteúdo da decisão
        """
        if not self.enable_cache:
            return
        
        cache_key = create_cache_key(self._source_name, decision_name)
        self.session_cache.put(cache_key, content)
    
    def validate_decision_content(self, content: Dict[str, Any]) -> bool:
        """
        Valida se o conteúdo da decisão é válido para o zen-engine.
        
        Args:
            content: Conteúdo da decisão a ser validado
            
        Returns:
            True se válido, False caso contrário
        """
        # Validação básica - deve ter estrutura do zen-engine
        required_fields = ["nodes"]
        return all(field in content for field in required_fields)


class FileAdapter(DecisionAdapter):
    """
    Adaptador para carregar decisões de arquivos locais.
    
    Suporta arquivos JSON e permite organização em diretórios.
    """
    
    def __init__(self, base_path: Union[str, Path], enable_cache: bool = True, session_cache=None):
        """
        Inicializa adaptador de arquivos.
        
        Args:
            base_path: Caminho base onde estão os arquivos de decisão
            enable_cache: Habilita cache de sessão
            session_cache: Instância de SessionCache customizada
        """
        super().__init__(enable_cache, session_cache)
        self.base_path = Path(base_path)
        if not self.base_path.exists():
            raise ValueError(f"Caminho base não existe: {self.base_path}")
    
    def get_decision(self, decision_name: str) -> Dict[str, Any]:
        """
        Carrega decisão de arquivo JSON com cache.
        
        Args:
            decision_name: Nome do arquivo (com ou sem extensão .json)
            
        Returns:
            Conteúdo da decisão como dict
        """
        # Tenta buscar no cache primeiro
        cached_content = self._get_cached_decision(decision_name)
        if cached_content is not None:
            return cached_content
        
        # Não encontrou no cache, carrega do arquivo
        # Adiciona extensão se não tiver
        file_name = decision_name if decision_name.endswith('.json') else f"{decision_name}.json"
        file_path = self.base_path / file_name
        
        if not file_path.exists():
            raise ValueError(f"Decisão não encontrada: {decision_name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            if not self.validate_decision_content(content):
                raise ValueError(f"Conteúdo da decisão inválido: {decision_name}")
            
            # Armazena no cache antes de retornar
            self._cache_decision(decision_name, content)
            
            return content
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao ler JSON da decisão {decision_name}: {e}")
        except ValueError as e:
            raise  # Re-raise ValueError (incluindo validação)
        except Exception as e:
            raise Exception(f"Erro ao carregar decisão {decision_name}: {e}")
    
    def list_decisions(self) -> List[str]:
        """
        Lista arquivos JSON no diretório base.
        
        Returns:
            Lista com nomes dos arquivos (sem extensão)
        """
        json_files = []
        for file_path in self.base_path.glob("*.json"):
            json_files.append(file_path.stem)  # Nome sem extensão
        
        return sorted(json_files)


class DatabricksAdapter(DecisionAdapter):
    """
    Adaptador para carregar decisões de tabelas do Databricks.
    
    Conecta com tabelas usando PySpark e busca decisões por nome.
    """
    
    def __init__(self, 
                 catalog: str, 
                 schema: str, 
                 table: str, 
                 name_column: str = "name", 
                 content_column: str = "content",
                 spark_session=None,
                 enable_cache: bool = True,
                 session_cache=None):
        """
        Inicializa adaptador do Databricks.
        
        Args:
            catalog: Nome do catálogo no Databricks
            schema: Nome do schema na tabela
            table: Nome da tabela com as decisões
            name_column: Nome da coluna que contém o nome da decisão
            content_column: Nome da coluna que contém o conteúdo JSON
            spark_session: Sessão do Spark (opcional, usa a ativa se None)
            enable_cache: Habilita cache de sessão
            session_cache: Instância de SessionCache customizada
        """
        super().__init__(enable_cache, session_cache)
        self.catalog = catalog
        self.schema = schema
        self.table = table
        self.name_column = name_column
        self.content_column = content_column
        self.spark_session = spark_session
        
        # Constrói nome completo da tabela
        self.full_table_name = f"{catalog}.{schema}.{table}"
    
    def _get_spark(self):
        """
        Obtém sessão do Spark.
        
        Returns:
            Sessão do Spark ativa
        """
        if self.spark_session:
            return self.spark_session
        
        try:
            # Tenta obter sessão ativa do Spark
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark is None:
                raise Exception("Nenhuma sessão do Spark ativa encontrada")
            return spark
        except ImportError:
            raise Exception("PySpark não está disponível")
    
    def _get_spark_functions(self):
        """
        Obtém módulo de funções do PySpark.
        
        Returns:
            Módulo pyspark.sql.functions
        """
        try:
            from pyspark.sql import functions as F
            return F
        except ImportError:
            raise Exception("PySpark não está disponível")
    
    def get_decision(self, decision_name: str) -> Dict[str, Any]:
        """
        Busca decisão na tabela do Databricks.
        
        Args:
            decision_name: Nome da decisão na coluna name_column
            
        Returns:
            Conteúdo da decisão como dict
        """
        spark = self._get_spark()
        F = self._get_spark_functions()
        
        try:
            # Query para buscar decisão específica
            decision_df = (
                spark.read.table(self.full_table_name)
                .filter(F.col(self.name_column) == decision_name)
                .select(self.content_column)
                .limit(1)
            )
            
            # Coleta resultado
            rows = decision_df.collect()
            
            if not rows:
                raise ValueError(f"Decisão não encontrada: {decision_name}")
            
            # Extrai conteúdo JSON
            content_json = rows[0][self.content_column]
            
            # Parse do JSON
            if isinstance(content_json, str):
                content = json.loads(content_json)
            else:
                content = content_json  # Já é dict
            
            if not self.validate_decision_content(content):
                raise ValueError(f"Conteúdo da decisão inválido: {decision_name}")
            
            return content
            
        except Exception as e:
            if "não encontrada" in str(e):
                raise  # Re-raise ValueError
            raise Exception(f"Erro ao buscar decisão {decision_name} no Databricks: {e}")
    
    def list_decisions(self) -> List[str]:
        """
        Lista todas as decisões disponíveis na tabela.
        
        Returns:
            Lista com nomes das decisões
        """
        spark = self._get_spark()
        
        try:
            # Query para listar nomes das decisões
            names_df = (
                spark.read.table(self.full_table_name)
                .select(self.name_column)
                .distinct()
            )
            
            # Coleta nomes
            rows = names_df.collect()
            decision_names = [row[self.name_column] for row in rows if row[self.name_column]]
            
            return sorted(decision_names)
            
        except Exception as e:
            raise Exception(f"Erro ao listar decisões no Databricks: {e}")


class DatabaseAdapter(DecisionAdapter):
    """
    Adaptador para carregar decisões de bancos de dados relacionais.
    
    Suporta diferentes SGBDs através de connection strings SQLAlchemy.
    """
    
    def __init__(self, 
                 connection_string: str, 
                 table_name: str,
                 name_column: str = "name",
                 content_column: str = "content"):
        """
        Inicializa adaptador de banco de dados.
        
        Args:
            connection_string: String de conexão SQLAlchemy
            table_name: Nome da tabela com decisões
            name_column: Nome da coluna com nome da decisão
            content_column: Nome da coluna com conteúdo JSON
        """
        self.connection_string = connection_string
        self.table_name = table_name
        self.name_column = name_column
        self.content_column = content_column
    
    def _get_connection(self):
        """
        Cria conexão com banco de dados.
        
        Returns:
            Conexão SQLAlchemy
        """
        try:
            from sqlalchemy import create_engine
            engine = create_engine(self.connection_string)
            return engine.connect()
        except ImportError:
            raise Exception("SQLAlchemy não está disponível")
        except Exception as e:
            raise Exception(f"Erro ao conectar com banco: {e}")
    
    def get_decision(self, decision_name: str) -> Dict[str, Any]:
        """
        Busca decisão no banco de dados.
        
        Args:
            decision_name: Nome da decisão
            
        Returns:
            Conteúdo da decisão como dict
        """
        with self._get_connection() as conn:
            try:
                # Query SQL
                query = f"""
                SELECT {self.content_column} 
                FROM {self.table_name} 
                WHERE {self.name_column} = %s
                LIMIT 1
                """
                
                result = conn.execute(query, (decision_name,))
                row = result.fetchone()
                
                if not row:
                    raise ValueError(f"Decisão não encontrada: {decision_name}")
                
                # Parse JSON
                content_json = row[0]
                if isinstance(content_json, str):
                    content = json.loads(content_json)
                else:
                    content = content_json
                
                if not self.validate_decision_content(content):
                    raise ValueError(f"Conteúdo da decisão inválido: {decision_name}")
                
                return content
                
            except Exception as e:
                if "não encontrada" in str(e):
                    raise  # Re-raise ValueError
                raise Exception(f"Erro ao buscar decisão {decision_name} no banco: {e}")
    
    def list_decisions(self) -> List[str]:
        """
        Lista decisões disponíveis no banco.
        
        Returns:
            Lista com nomes das decisões
        """
        with self._get_connection() as conn:
            try:
                query = f"SELECT DISTINCT {self.name_column} FROM {self.table_name}"
                result = conn.execute(query)
                
                decision_names = [row[0] for row in result if row[0]]
                return sorted(decision_names)
                
            except Exception as e:
                raise Exception(f"Erro ao listar decisões no banco: {e}")


# Factory function para criar adaptadores facilmente
def create_adapter(source_type: str, **kwargs) -> DecisionAdapter:
    """
    Factory function para criar adaptadores.
    
    Args:
        source_type: Tipo de adaptador ('file', 'databricks', 'database')
        **kwargs: Parâmetros específicos do adaptador
        
    Returns:
        Instância do adaptador apropriado
        
    Raises:
        ValueError: Se source_type não for reconhecido
    """
    adapters = {
        'file': FileAdapter,
        'databricks': DatabricksAdapter,
        'database': DatabaseAdapter,
    }
    
    if source_type not in adapters:
        available = ', '.join(adapters.keys())
        raise ValueError(f"Tipo de adaptador inválido: {source_type}. Disponíveis: {available}")
    
    return adapters[source_type](**kwargs)