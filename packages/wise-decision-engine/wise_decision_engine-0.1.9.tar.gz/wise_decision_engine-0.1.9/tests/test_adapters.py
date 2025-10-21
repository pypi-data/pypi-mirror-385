"""Testes para os adaptadores de fontes de dados."""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from wise_decision_engine.adapters import (
    DecisionAdapter,
    FileAdapter, 
    DatabricksAdapter,
    DatabaseAdapter,
    create_adapter
)


@pytest.fixture
def sample_decision():
    """Fixture com decisão de exemplo válida."""
    return {
        "nodes": {
            "test_decision": {
                "type": "decisionTable",
                "hitPolicy": "first",
                "inputs": [{"name": "input1", "type": "string"}],
                "outputs": [{"name": "output1", "type": "string"}],
                "rules": [{"1": "test", "2": "result"}]
            }
        }
    }


@pytest.fixture
def temp_directory():
    """Fixture que cria diretório temporário para testes."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.mark.unit
class TestFileAdapter:
    """Testes para FileAdapter."""
    
    def test_init_with_valid_path(self, temp_directory):
        """Testa inicialização com caminho válido."""
        adapter = FileAdapter(temp_directory)
        assert adapter.base_path == temp_directory
    
    def test_init_with_invalid_path(self):
        """Testa inicialização com caminho inválido."""
        with pytest.raises(ValueError, match="Caminho base não existe"):
            FileAdapter("/path/that/does/not/exist")
    
    def test_get_decision_success(self, temp_directory, sample_decision):
        """Testa carregamento bem-sucedido de decisão."""
        # Cria arquivo de teste
        decision_file = temp_directory / "test_decision.json"
        with open(decision_file, 'w') as f:
            json.dump(sample_decision, f)
        
        adapter = FileAdapter(temp_directory)
        result = adapter.get_decision("test_decision")
        
        assert result == sample_decision
    
    def test_get_decision_with_extension(self, temp_directory, sample_decision):
        """Testa carregamento com extensão .json no nome."""
        decision_file = temp_directory / "test_decision.json" 
        with open(decision_file, 'w') as f:
            json.dump(sample_decision, f)
        
        adapter = FileAdapter(temp_directory)
        result = adapter.get_decision("test_decision.json")
        
        assert result == sample_decision
    
    def test_get_decision_not_found(self, temp_directory):
        """Testa erro quando decisão não encontrada."""
        adapter = FileAdapter(temp_directory)
        
        with pytest.raises(ValueError, match="Decisão não encontrada"):
            adapter.get_decision("nonexistent")
    
    def test_get_decision_invalid_json(self, temp_directory):
        """Testa erro com JSON inválido."""
        decision_file = temp_directory / "invalid.json"
        with open(decision_file, 'w') as f:
            f.write("{invalid json}")
        
        adapter = FileAdapter(temp_directory)
        
        with pytest.raises(ValueError, match="Erro ao ler JSON"):
            adapter.get_decision("invalid")
    
    def test_get_decision_invalid_content(self, temp_directory):
        """Testa erro com conteúdo inválido (sem 'nodes')."""
        invalid_decision = {"invalid": "content"}
        decision_file = temp_directory / "invalid_content.json"
        with open(decision_file, 'w') as f:
            json.dump(invalid_decision, f)
        
        adapter = FileAdapter(temp_directory)
        
        with pytest.raises(ValueError, match="Conteúdo da decisão inválido"):
            adapter.get_decision("invalid_content")
    
    def test_list_decisions(self, temp_directory, sample_decision):
        """Testa listagem de decisões."""
        # Cria alguns arquivos de teste
        files = ["decision1.json", "decision2.json", "not_json.txt"]
        
        for filename in files[:2]:  # Apenas os JSON
            file_path = temp_directory / filename
            with open(file_path, 'w') as f:
                json.dump(sample_decision, f)
        
        # Cria arquivo não-JSON
        (temp_directory / files[2]).write_text("not json")
        
        adapter = FileAdapter(temp_directory)
        decisions = adapter.list_decisions()
        
        assert sorted(decisions) == ["decision1", "decision2"]


@pytest.mark.unit 
class TestDatabricksAdapter:
    """Testes para DatabricksAdapter."""
    
    def test_init(self):
        """Testa inicialização do adaptador."""
        adapter = DatabricksAdapter(
            catalog="test_catalog",
            schema="test_schema", 
            table="test_table"
        )
        
        assert adapter.catalog == "test_catalog"
        assert adapter.schema == "test_schema"
        assert adapter.table == "test_table"
        assert adapter.full_table_name == "test_catalog.test_schema.test_table"
        assert adapter.name_column == "name"  # default
        assert adapter.content_column == "content"  # default
    
    def test_init_custom_columns(self):
        """Testa inicialização com colunas customizadas."""
        adapter = DatabricksAdapter(
            catalog="cat",
            schema="sch",
            table="tab",
            name_column="decision_name",
            content_column="decision_content"
        )
        
        assert adapter.name_column == "decision_name"
        assert adapter.content_column == "decision_content"
    
    @patch('pyspark.sql.SparkSession')
    def test_get_spark_with_session(self, mock_spark_session):
        """Testa obtenção de sessão Spark quando fornecida."""
        mock_session = Mock()
        adapter = DatabricksAdapter("cat", "sch", "tab", spark_session=mock_session)
        
        spark = adapter._get_spark()
        assert spark == mock_session
    
    @patch('pyspark.sql.SparkSession')
    def test_get_spark_active_session(self, mock_spark_session):
        """Testa obtenção de sessão Spark ativa."""
        mock_active_session = Mock()
        mock_spark_session.getActiveSession.return_value = mock_active_session
        
        adapter = DatabricksAdapter("cat", "sch", "tab")
        spark = adapter._get_spark()
        
        assert spark == mock_active_session
        mock_spark_session.getActiveSession.assert_called_once()
    
    @patch('pyspark.sql.SparkSession')
    def test_get_spark_no_active_session(self, mock_spark_session):
        """Testa erro quando não há sessão Spark ativa."""
        mock_spark_session.getActiveSession.return_value = None
        
        adapter = DatabricksAdapter("cat", "sch", "tab")
        
        with pytest.raises(Exception, match="Nenhuma sessão do Spark ativa encontrada"):
            adapter._get_spark()
    
    def test_get_decision_success(self, sample_decision):
        """Testa busca bem-sucedida de decisão."""
        # Mock do Spark e DataFrame
        mock_spark = Mock()
        mock_df = Mock()
        mock_row = Mock()
        mock_row.__getitem__ = Mock(return_value=json.dumps(sample_decision))
        
        mock_df.collect.return_value = [mock_row]
        mock_spark.read.table.return_value.filter.return_value.select.return_value.limit.return_value = mock_df
        
        adapter = DatabricksAdapter("cat", "sch", "tab", spark_session=mock_spark)
        result = adapter.get_decision("test_decision")
        
        assert result == sample_decision
        mock_spark.read.table.assert_called_with("cat.sch.tab")
    
    def test_get_decision_not_found(self):
        """Testa erro quando decisão não encontrada."""
        mock_spark = Mock()
        mock_df = Mock()
        mock_df.collect.return_value = []  # Nenhuma linha encontrada
        
        mock_spark.read.table.return_value.filter.return_value.select.return_value.limit.return_value = mock_df
        
        adapter = DatabricksAdapter("cat", "sch", "tab", spark_session=mock_spark)
        
        with pytest.raises(ValueError, match="Decisão não encontrada"):
            adapter.get_decision("nonexistent")
    
    def test_list_decisions(self):
        """Testa listagem de decisões."""
        mock_spark = Mock()
        mock_df = Mock()
        
        # Mock rows com nomes de decisões
        mock_row1 = Mock()
        mock_row1.__getitem__ = Mock(return_value="decision1")
        mock_row2 = Mock()
        mock_row2.__getitem__ = Mock(return_value="decision2")
        mock_row3 = Mock()
        mock_row3.__getitem__ = Mock(return_value="decision3")
        
        mock_rows = [mock_row1, mock_row2, mock_row3]
        
        mock_df.collect.return_value = mock_rows
        mock_spark.read.table.return_value.select.return_value.distinct.return_value = mock_df
        
        adapter = DatabricksAdapter("cat", "sch", "tab", spark_session=mock_spark)
        decisions = adapter.list_decisions()
        
        assert decisions == ["decision1", "decision2", "decision3"]


@pytest.mark.unit
class TestDatabaseAdapter:
    """Testes para DatabaseAdapter."""
    
    def test_init(self):
        """Testa inicialização do adaptador."""
        adapter = DatabaseAdapter(
            connection_string="sqlite:///:memory:",
            table_name="decisions"
        )
        
        assert adapter.connection_string == "sqlite:///:memory:"
        assert adapter.table_name == "decisions"
        assert adapter.name_column == "name"  # default
        assert adapter.content_column == "content"  # default


@pytest.mark.unit
class TestCreateAdapter:
    """Testes para função create_adapter."""
    
    def test_create_file_adapter(self, temp_directory):
        """Testa criação de FileAdapter."""
        adapter = create_adapter('file', base_path=temp_directory)
        
        assert isinstance(adapter, FileAdapter)
        assert adapter.base_path == temp_directory
    
    def test_create_databricks_adapter(self):
        """Testa criação de DatabricksAdapter."""
        adapter = create_adapter('databricks', catalog='cat', schema='sch', table='tab')
        
        assert isinstance(adapter, DatabricksAdapter)
        assert adapter.catalog == 'cat'
    
    def test_create_database_adapter(self):
        """Testa criação de DatabaseAdapter.""" 
        adapter = create_adapter('database', 
                                connection_string='sqlite:///:memory:',
                                table_name='decisions')
        
        assert isinstance(adapter, DatabaseAdapter)
        assert adapter.connection_string == 'sqlite:///:memory:'
    
    def test_invalid_adapter_type(self):
        """Testa erro com tipo inválido."""
        with pytest.raises(ValueError, match="Tipo de adaptador inválido"):
            create_adapter('invalid_type')


@pytest.mark.unit
class TestDecisionAdapterValidation:
    """Testes para validação de conteúdo de decisão."""
    
    def test_validate_decision_content_valid(self, temp_directory):
        """Testa validação com conteúdo válido."""
        adapter = FileAdapter(temp_directory)
        
        valid_content = {"nodes": {"test": "content"}}
        assert adapter.validate_decision_content(valid_content) is True
    
    def test_validate_decision_content_invalid(self, temp_directory):
        """Testa validação com conteúdo inválido."""
        adapter = FileAdapter(temp_directory)
        
        invalid_content = {"invalid": "content"}
        assert adapter.validate_decision_content(invalid_content) is False
