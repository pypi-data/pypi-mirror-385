"""Testes de integração do WiseDecisionEngine com adaptadores."""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from wise_decision_engine import WiseDecisionEngine, FileAdapter, DatabricksAdapter


@pytest.fixture
def real_decision():
    """Fixture com decisão real para testes."""
    decision_path = Path(__file__).parent.parent / "examples" / "real_decision.json"
    with open(decision_path, "r") as f:
        return json.load(f)


@pytest.fixture
def temp_directory():
    """Fixture que cria diretório temporário para testes."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.mark.unit
class TestWiseDecisionEngineFromAdapter:
    """Testes para método from_adapter."""
    
    def test_from_adapter_success(self, temp_directory, real_decision):
        """Testa criação de engine via adaptador."""
        # Prepara arquivo de decisão
        decision_file = temp_directory / "credito.json"
        with open(decision_file, 'w') as f:
            json.dump(real_decision, f)
        
        # Cria adaptador e engine
        adapter = FileAdapter(temp_directory)
        engine = WiseDecisionEngine.from_adapter(adapter, "credito")
        
        assert engine.decision_content == real_decision
        # Testa se funciona
        assert engine.decision is not None


@pytest.mark.unit
class TestWiseDecisionEngineFromFile:
    """Testes para método from_file."""
    
    def test_from_file_single_file(self, temp_directory, real_decision):
        """Testa carregamento de arquivo único."""
        decision_file = temp_directory / "credito.json"
        with open(decision_file, 'w') as f:
            json.dump(real_decision, f)
        
        engine = WiseDecisionEngine.from_file(decision_file)
        
        assert engine.decision_content == real_decision
    
    def test_from_file_directory_with_name(self, temp_directory, real_decision):
        """Testa carregamento de diretório com nome da decisão."""
        decision_file = temp_directory / "credito.json"
        with open(decision_file, 'w') as f:
            json.dump(real_decision, f)
        
        engine = WiseDecisionEngine.from_file(temp_directory, "credito")
        
        assert engine.decision_content == real_decision
    
    def test_from_file_directory_without_name(self, temp_directory):
        """Testa erro ao tentar carregar diretório sem nome."""
        with pytest.raises(ValueError, match="decision_name é obrigatório"):
            WiseDecisionEngine.from_file(temp_directory)


@pytest.mark.unit
class TestWiseDecisionEngineFromDatabricks:
    """Testes para método from_databricks."""
    
    @patch('pyspark.sql.SparkSession')
    def test_from_databricks_success(self, mock_spark_session_class, real_decision):
        """Testa criação de engine via Databricks."""
        # Mock do Spark e DataFrame
        mock_spark = Mock()
        mock_df = Mock()
        mock_row = Mock()
        mock_row.__getitem__ = Mock(return_value=json.dumps(real_decision))
        
        mock_df.collect.return_value = [mock_row]
        mock_spark.read.table.return_value.filter.return_value.select.return_value.limit.return_value = mock_df
        
        engine = WiseDecisionEngine.from_databricks(
            catalog="test_cat",
            schema="test_schema", 
            table="decisions",
            decision_name="credito-pj",
            spark_session=mock_spark
        )
        
        assert engine.decision_content == real_decision
        mock_spark.read.table.assert_called_with("test_cat.test_schema.decisions")


@pytest.mark.integration
class TestWiseDecisionEngineIntegration:
    """Testes de integração completos com adaptadores."""
    
    def test_engine_file_adapter_evaluation(self, temp_directory, real_decision):
        """Testa fluxo completo: adaptador -> engine -> avaliação."""
        # Prepara decisão em arquivo
        decision_file = temp_directory / "credito.json"
        with open(decision_file, 'w') as f:
            json.dump(real_decision, f)
        
        # Cria engine via arquivo
        engine = WiseDecisionEngine.from_file(decision_file)
        
        # Dados de teste
        test_data = {
            "cnpj": "12.345.678/0001-90",
            "razao_social": "Empresa Teste",
            "tempo_atividade_meses": 24,
            "setor": "Comércio",
            "situacao_cadastral": "Ativa",
            "pendencias_fiscais": False,
            "faturamento_anual": 2500000,
            "score_interno": 850,
            "limite_solicitado": 300000
        }
        
        # Avalia decisão
        resultado = engine.evaluate(test_data)
        
        # Verifica resultado
        assert "result" in resultado
        assert "performance" in resultado
        result = resultado["result"]
        assert "segmento" in result
        assert "score_final" in result
        assert "cnpj" in result
        assert result["cnpj"] == test_data["cnpj"]
    
    def test_engine_list_and_load_decisions(self, temp_directory, real_decision):
        """Testa listagem e carregamento de múltiplas decisões."""
        # Cria múltiplos arquivos de decisão
        decisions = {
            "credito": real_decision,
            "seguro": real_decision.copy(),  # Simula outra decisão
        }
        
        for name, content in decisions.items():
            decision_file = temp_directory / f"{name}.json"
            with open(decision_file, 'w') as f:
                json.dump(content, f)
        
        # Testa listagem via adaptador
        adapter = FileAdapter(temp_directory)
        available_decisions = adapter.list_decisions()
        
        assert sorted(available_decisions) == ["credito", "seguro"]
        
        # Testa carregamento de cada decisão
        for decision_name in available_decisions:
            engine = WiseDecisionEngine.from_adapter(adapter, decision_name)
            assert engine.decision_content is not None
            # Verifica se engine funciona
            assert engine.decision is not None