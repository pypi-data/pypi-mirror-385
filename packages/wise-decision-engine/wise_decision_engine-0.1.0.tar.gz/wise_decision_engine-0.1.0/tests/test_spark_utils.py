"""
Testes para utilitários Spark/Databricks.

Testa funcionalidades de UDFs otimizadas, broadcast e integração.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

# Mock do PySpark antes dos imports
mock_pyspark_modules = {
    'pyspark': MagicMock(),
    'pyspark.sql': MagicMock(), 
    'pyspark.sql.functions': MagicMock(),
    'pyspark.sql.types': MagicMock(),
    'pandas': MagicMock()
}

with patch.dict('sys.modules', mock_pyspark_modules):
    from wise_decision_engine.spark_utils import (
        SparkDecisionEvaluator,
        create_decision_udf, 
        apply_decision_to_dataframe,
        DatabricksHelper,
        print_migration_guide,
        create_legacy_udf,
        require_pyspark,
        PYSPARK_AVAILABLE
    )
    from wise_decision_engine.adapters import FileAdapter, DatabricksAdapter


class TestRequirePysparkDecorator:
    """Testa decorator de verificação do PySpark."""
    
    def test_require_pyspark_when_available(self):
        """Testa decorator quando PySpark está disponível."""
        with patch('wise_decision_engine.spark_utils.PYSPARK_AVAILABLE', True):
            @require_pyspark
            def test_func():
                return "success"
            
            result = test_func()
            assert result == "success"
    
    def test_require_pyspark_when_not_available(self):
        """Testa decorator quando PySpark não está disponível."""
        # Mock the module-level PYSPARK_AVAILABLE
        import wise_decision_engine.spark_utils as spark_utils_module
        original_value = spark_utils_module.PYSPARK_AVAILABLE
        
        try:
            spark_utils_module.PYSPARK_AVAILABLE = False
            
            @require_pyspark
            def test_func():
                return "success"
            
            with pytest.raises(ImportError) as exc_info:
                test_func()
            
            assert "PySpark não está disponível" in str(exc_info.value)
        finally:
            spark_utils_module.PYSPARK_AVAILABLE = original_value


class TestSparkDecisionEvaluator:
    """Testa avaliador de decisões Spark."""
    
    def setup_method(self):
        """Setup para testes."""
        # Mock adapter e decision
        self.mock_adapter = Mock(spec=FileAdapter)
        self.decision_name = "test-decision"
        
        # Mock engine
        self.mock_engine = Mock()
        self.mock_engine.decision_content = {"nodes": []}
        
        # Mock adapter methods that WiseDecisionEngine expects
        self.mock_adapter.get_decision.return_value = '{"nodes": []}'
        
        # Patch WiseDecisionEngine.from_adapter
        patcher = patch('wise_decision_engine.spark_utils.WiseDecisionEngine.from_adapter')
        self.mock_from_adapter = patcher.start()
        self.mock_from_adapter.return_value = self.mock_engine
        self.addCleanup(patcher.stop)
    
    def addCleanup(self, func):
        """Helper para cleanup de patches."""
        # Em ambiente real, pytest faria isso automaticamente
        pass
    
    def test_init(self):
        """Testa inicialização do avaliador."""
        evaluator = SparkDecisionEvaluator(
            self.mock_adapter, 
            self.decision_name,
            result_columns=["score", "category"]
        )
        
        assert evaluator.adapter == self.mock_adapter
        assert evaluator.decision_name == self.decision_name
        assert evaluator.result_columns == ["score", "category"]
        assert evaluator.engine == self.mock_engine
        assert evaluator._decision_content == {"nodes": []}
        
        # Verifica chamada do from_adapter
        self.mock_from_adapter.assert_called_once_with(
            self.mock_adapter, self.decision_name
        )
    
    @patch('wise_decision_engine.spark_utils.PYSPARK_AVAILABLE', True)
    def test_create_broadcast_decision(self):
        """Testa criação de broadcast variable."""
        evaluator = SparkDecisionEvaluator(self.mock_adapter, self.decision_name)
        
        # Mock spark context
        mock_sc = Mock()
        mock_broadcast = Mock()
        mock_sc.broadcast.return_value = mock_broadcast
        
        # Primeira chamada - cria broadcast
        result = evaluator._create_broadcast_decision(mock_sc)
        
        assert result == mock_broadcast
        mock_sc.broadcast.assert_called_once_with({"nodes": []})
        
        # Segunda chamada - reutiliza broadcast
        result2 = evaluator._create_broadcast_decision(mock_sc)
        
        assert result2 == mock_broadcast
        # Não deve chamar broadcast novamente
        assert mock_sc.broadcast.call_count == 1


class TestHelperFunctions:
    """Testa funções auxiliares."""
    
    @patch('wise_decision_engine.spark_utils.PYSPARK_AVAILABLE', True)
    @patch('wise_decision_engine.spark_utils.SparkDecisionEvaluator')
    def test_create_decision_udf(self, mock_evaluator_class):
        """Testa criação de UDF."""
        # Setup mocks
        mock_adapter = Mock()
        mock_evaluator = Mock()
        mock_udf = Mock()
        
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.create_udf.return_value = mock_udf
        
        # Executa função
        result = create_decision_udf(
            mock_adapter, 
            "test-decision",
            result_columns=["score"],
            return_full_result=True
        )
        
        # Verificações
        mock_evaluator_class.assert_called_once_with(
            mock_adapter, "test-decision", ["score"]
        )
        mock_evaluator.create_udf.assert_called_once_with(True)
        assert result == mock_udf
    
    @patch('wise_decision_engine.spark_utils.PYSPARK_AVAILABLE', True)
    @patch('wise_decision_engine.spark_utils.SparkDecisionEvaluator')
    def test_apply_decision_to_dataframe(self, mock_evaluator_class):
        """Testa aplicação de decisão em DataFrame."""
        # Setup mocks
        mock_df = Mock()
        mock_adapter = Mock()
        mock_evaluator = Mock()
        mock_result_df = Mock()
        
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.apply_to_dataframe.return_value = mock_result_df
        
        # Executa função
        result = apply_decision_to_dataframe(
            mock_df,
            mock_adapter,
            "test-decision", 
            result_column="result",
            input_columns=["col1", "col2"],
            result_columns=["score"],
            expand_result=False
        )
        
        # Verificações
        mock_evaluator_class.assert_called_once_with(
            mock_adapter, "test-decision", ["score"]
        )
        mock_evaluator.apply_to_dataframe.assert_called_once_with(
            mock_df, "result", ["col1", "col2"], False
        )
        assert result == mock_result_df


class TestDatabricksHelper:
    """Testa helper específico para Databricks."""
    
    @patch('wise_decision_engine.spark_utils.PYSPARK_AVAILABLE', True)
    @patch('wise_decision_engine.spark_utils.DatabricksAdapter')
    @patch('wise_decision_engine.spark_utils.apply_decision_to_dataframe')
    def test_quick_decision_apply(self, mock_apply_function, mock_adapter_class):
        """Testa aplicação rápida de decisão."""
        # Setup mocks
        mock_adapter = Mock()
        mock_df = Mock()
        mock_result_df = Mock()
        
        # Mock adapter methods to avoid Spark session issues
        mock_adapter.get_decision.return_value = '{"nodes": []}'
        
        mock_adapter_class.return_value = mock_adapter
        mock_apply_function.return_value = mock_result_df
        
        # Executa função
        result = DatabricksHelper.quick_decision_apply(
            "catalog", "schema", "table",
            "test-decision",
            mock_df,
            result_columns=["score", "category"]
        )
        
        # Verificações
        mock_adapter_class.assert_called_once_with("catalog", "schema", "table")
        mock_apply_function.assert_called_once_with(
            mock_df, mock_adapter, "test-decision",
            result_columns=["score", "category"],
            expand_result=True
        )
        assert result == mock_result_df
    
    @patch('wise_decision_engine.spark_utils.PYSPARK_AVAILABLE', True)
    @patch('wise_decision_engine.spark_utils.DatabricksAdapter')
    @patch('wise_decision_engine.spark_utils.create_decision_udf')
    @patch('wise_decision_engine.spark_utils.SparkSession')
    def test_create_reusable_udf(self, mock_spark_session, mock_create_udf, mock_adapter_class):
        """Testa criação de UDF reutilizável."""
        # Setup mocks
        mock_adapter = Mock()
        mock_udf = Mock()
        mock_spark = Mock()
        
        # Mock adapter methods to avoid Spark session issues
        mock_adapter.get_decision.return_value = '{"nodes": []}'
        
        mock_adapter_class.return_value = mock_adapter
        mock_create_udf.return_value = mock_udf
        mock_spark_session.getActiveSession.return_value = mock_spark
        
        # Executa função com nome da UDF
        result = DatabricksHelper.create_reusable_udf(
            "catalog", "schema", "table",
            "test-decision",
            udf_name="test_udf"
        )
        
        # Verificações
        mock_adapter_class.assert_called_once_with("catalog", "schema", "table")
        mock_create_udf.assert_called_once_with(mock_adapter, "test-decision")
        mock_spark.udf.register.assert_called_once_with("test_udf", mock_udf)
        assert result == mock_udf
    
    @patch('wise_decision_engine.spark_utils.PYSPARK_AVAILABLE', True)
    @patch('wise_decision_engine.spark_utils.DatabricksAdapter')
    @patch('wise_decision_engine.spark_utils.create_decision_udf')
    def test_create_reusable_udf_without_name(self, mock_create_udf, mock_adapter_class):
        """Testa criação de UDF sem registro."""
        # Setup mocks
        mock_adapter = Mock()
        mock_udf = Mock()
        
        # Mock adapter methods to avoid Spark session issues
        mock_adapter.get_decision.return_value = '{"nodes": []}'
        
        mock_adapter_class.return_value = mock_adapter
        mock_create_udf.return_value = mock_udf
        
        # Executa função sem nome da UDF
        result = DatabricksHelper.create_reusable_udf(
            "catalog", "schema", "table",
            "test-decision",
            udf_name=None
        )
        
        # Verificações
        mock_adapter_class.assert_called_once_with("catalog", "schema", "table")
        mock_create_udf.assert_called_once_with(mock_adapter, "test-decision")
        assert result == mock_udf


class TestUtilityFunctions:
    """Testa funções utilitárias."""
    
    def test_print_migration_guide(self, capsys):
        """Testa impressão do guia de migração."""
        print_migration_guide()
        
        captured = capsys.readouterr()
        
        # Verifica se o guia foi impresso
        assert "🚀 Guia de Migração" in captured.out
        assert "ANTES (seu código atual" in captured.out 
        assert "DEPOIS (com Spark Utils" in captured.out
        assert "50x menos código" in captured.out
        assert "SessionCache" in captured.out
    
    @patch('wise_decision_engine.spark_utils.PYSPARK_AVAILABLE', True)
    @patch('wise_decision_engine.spark_utils.pandas_udf')
    def test_create_legacy_udf(self, mock_pandas_udf):
        """Testa criação de UDF legada."""
        # Setup mock
        mock_udf = Mock()
        mock_pandas_udf.return_value = mock_udf
        
        content_value = json.dumps({"nodes": []})
        
        # Executa função
        result = create_legacy_udf(content_value)
        
        # Verificações básicas
        mock_pandas_udf.assert_called_once()
        assert result == mock_udf
    
    def test_create_legacy_udf_without_pyspark(self):
        """Testa criação de UDF legada sem PySpark."""
        import wise_decision_engine.spark_utils as spark_utils_module
        original_value = spark_utils_module.PYSPARK_AVAILABLE
        
        try:
            spark_utils_module.PYSPARK_AVAILABLE = False
            
            with pytest.raises(ImportError) as exc_info:
                create_legacy_udf('{"nodes": []}')
            
            assert "PySpark não disponível" in str(exc_info.value)
        finally:
            spark_utils_module.PYSPARK_AVAILABLE = original_value


# Testes de integração (simulados)
class TestIntegration:
    """Testa integração entre componentes."""
    
    @patch('wise_decision_engine.spark_utils.PYSPARK_AVAILABLE', True)
    def test_full_pipeline_simulation(self):
        """Simula pipeline completo de uso."""
        # Este teste simula o fluxo completo sem PySpark real
        
        # 1. Setup adapter
        adapter = Mock(spec=DatabricksAdapter)
        
        # 2. Cria evaluator
        with patch('wise_decision_engine.spark_utils.WiseDecisionEngine.from_adapter') as mock_from_adapter:
            mock_engine = Mock()
            mock_engine.decision_content = {"nodes": []}
            mock_from_adapter.return_value = mock_engine
            
            evaluator = SparkDecisionEvaluator(adapter, "test-decision")
            
            # 3. Verifica que engine foi criado
            assert evaluator.engine == mock_engine
            assert evaluator._decision_content == {"nodes": []}
            
            # 4. Verifica que adapter foi usado corretamente
            mock_from_adapter.assert_called_once_with(adapter, "test-decision")


if __name__ == "__main__":
    pytest.main([__file__])