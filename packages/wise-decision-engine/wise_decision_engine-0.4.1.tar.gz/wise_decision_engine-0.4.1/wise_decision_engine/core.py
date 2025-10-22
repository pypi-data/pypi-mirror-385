"""
Módulo core do WiseDecisionEngine.

Contém a classe principal que encapsula o zen-engine com funcionalidades básicas.
"""

import json
import zen
from typing import Dict, Any, Union
from pathlib import Path


class WiseDecisionEngine:
    """
    Engine principal para avaliar decisões usando zen-engine.
    
    Versão básica com carregamento e avaliação simples, sem cache otimizado.
    """
    
    def __init__(self, decision_content: Union[str, Dict[str, Any]]):
        """
        Inicializa o engine com o conteúdo da decisão.
        
        Args:
            decision_content: Conteúdo da decisão como string JSON ou dict
        """
        self.decision_content = self._parse_decision_content(decision_content)
        self._zen_engine = None
        self._decision = None
    
    def _parse_decision_content(self, content: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Converte o conteúdo da decisão para dict se necessário.
        
        Args:
            content: Conteúdo como string JSON ou dict
            
        Returns:
            Dict com o conteúdo da decisão
            
        Raises:
            ValueError: Se o conteúdo não puder ser parseado
        """
        if isinstance(content, str):
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Conteúdo da decisão não é um JSON válido: {e}")
        elif isinstance(content, dict):
            return content
        else:
            raise ValueError("Conteúdo da decisão deve ser string JSON ou dict")
    
    @property
    def decision(self):
        """
        Lazy loading da decisão do zen-engine.
        
        Returns:
            Instância da decisão do zen-engine
        """
        if self._decision is None:
            if self._zen_engine is None:
                self._zen_engine = zen.ZenEngine()
            # zen-engine aceita dict diretamente
            self._decision = self._zen_engine.create_decision(self.decision_content)
        return self._decision
    
    def evaluate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia os dados de entrada usando a decisão.
        
        Args:
            input_data: Dados de entrada para a decisão
            
        Returns:
            Resultado da avaliação
            
        Raises:
            ValueError: Se houver erro na avaliação
        """
        try:
            result = self.decision.evaluate(input_data)
            return result
        except Exception as e:
            raise ValueError(f"Erro ao avaliar decisão: {e}")
    
    def evaluate_batch(self, input_list: list) -> list:
        """
        Avalia uma lista de dados de entrada.
        
        Args:
            input_list: Lista de dicts com dados de entrada
            
        Returns:
            Lista com os resultados das avaliações
        """
        results = []
        for input_data in input_list:
            result = self.evaluate(input_data)
            results.append(result)
        return results
    
    @classmethod
    def from_json_string(cls, json_string: str) -> 'WiseDecisionEngine':
        """
        Cria uma instância a partir de string JSON.
        
        Args:
            json_string: String JSON com o conteúdo da decisão
            
        Returns:
            Nova instância do WiseDecisionEngine
        """
        return cls(json_string)
    
    @classmethod
    def from_dict(cls, decision_dict: Dict[str, Any]) -> 'WiseDecisionEngine':
        """
        Cria uma instância a partir de dict.
        
        Args:
            decision_dict: Dict com o conteúdo da decisão
            
        Returns:
            Nova instância do WiseDecisionEngine
        """
        return cls(decision_dict)
    
    @classmethod
    def from_adapter(cls, adapter, decision_name: str) -> 'WiseDecisionEngine':
        """
        Cria uma instância carregando decisão via adaptador.
        
        Args:
            adapter: Instância de DecisionAdapter
            decision_name: Nome da decisão para carregar
            
        Returns:
            Nova instância do WiseDecisionEngine
        """
        decision_content = adapter.get_decision(decision_name)
        return cls(decision_content)
    
    @classmethod
    def from_file(cls, file_path: Union[str, 'Path'], decision_name: str = None) -> 'WiseDecisionEngine':
        """
        Cria uma instância carregando de arquivo.
        
        Args:
            file_path: Caminho do arquivo ou diretório
            decision_name: Nome da decisão (se file_path for diretório)
            
        Returns:
            Nova instância do WiseDecisionEngine
        """
        from .adapters import FileAdapter
        from pathlib import Path
        
        file_path = Path(file_path)
        
        if file_path.is_file():
            # Carrega arquivo diretamente
            with open(file_path, 'r') as f:
                content = json.loads(f.read())
            return cls(content)
        else:
            # Usa FileAdapter para diretório
            if not decision_name:
                raise ValueError("decision_name é obrigatório quando file_path é diretório")
            adapter = FileAdapter(file_path)
            return cls.from_adapter(adapter, decision_name)
    
    @classmethod
    def from_databricks(cls, 
                       catalog: str, 
                       schema: str, 
                       table: str, 
                       decision_name: str,
                       name_column: str = "name",
                       content_column: str = "content",
                       spark_session=None) -> 'WiseDecisionEngine':
        """
        Cria uma instância carregando de tabela do Databricks.
        
        Args:
            catalog: Catálogo do Databricks
            schema: Schema da tabela
            table: Nome da tabela
            decision_name: Nome da decisão
            name_column: Nome da coluna com nome da decisão
            content_column: Nome da coluna com conteúdo JSON
            spark_session: Sessão do Spark (opcional)
            
        Returns:
            Nova instância do WiseDecisionEngine
        """
        from .adapters import DatabricksAdapter
        
        adapter = DatabricksAdapter(
            catalog=catalog,
            schema=schema, 
            table=table,
            name_column=name_column,
            content_column=content_column,
            spark_session=spark_session
        )
        return cls.from_adapter(adapter, decision_name)
