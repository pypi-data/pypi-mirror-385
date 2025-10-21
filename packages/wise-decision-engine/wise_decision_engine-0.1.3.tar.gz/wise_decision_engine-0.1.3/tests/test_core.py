"""Testes para o módulo core do WiseDecisionEngine."""

import json
import pytest
from pathlib import Path
from wise_decision_engine import WiseDecisionEngine


@pytest.fixture
def simple_decision():
    """Fixture com uma decisão real do zen-engine para testes."""
    decision_path = Path(__file__).parent.parent / "examples" / "real_decision.json"
    with open(decision_path, "r") as f:
        return json.load(f)


@pytest.fixture
def simple_decision_json(simple_decision):
    """Fixture com a decisão como string JSON."""
    return json.dumps(simple_decision)


@pytest.fixture
def test_data():
    """Fixture com dados de teste reais."""
    data_path = Path(__file__).parent.parent / "examples" / "test_data.json"
    with open(data_path, "r") as f:
        return json.load(f)


@pytest.mark.unit
class TestWiseDecisionEngineInit:
    """Testes de inicialização do WiseDecisionEngine."""
    
    def test_init_with_dict(self, simple_decision):
        """Testa inicialização com dict."""
        engine = WiseDecisionEngine(simple_decision)
        assert engine.decision_content == simple_decision
    
    def test_init_with_json_string(self, simple_decision_json):
        """Testa inicialização com string JSON."""
        engine = WiseDecisionEngine(simple_decision_json)
        assert isinstance(engine.decision_content, dict)
    
    def test_init_with_invalid_json(self):
        """Testa inicialização com JSON inválido."""
        with pytest.raises(ValueError, match="não é um JSON válido"):
            WiseDecisionEngine("{invalid json}")
    
    def test_init_with_invalid_type(self):
        """Testa inicialização com tipo inválido."""
        with pytest.raises(ValueError, match="deve ser string JSON ou dict"):
            WiseDecisionEngine(123)


@pytest.mark.unit
class TestWiseDecisionEngineClassMethods:
    """Testes dos métodos de classe."""
    
    def test_from_json_string(self, simple_decision_json):
        """Testa criação a partir de string JSON."""
        engine = WiseDecisionEngine.from_json_string(simple_decision_json)
        assert isinstance(engine.decision_content, dict)
    
    def test_from_dict(self, simple_decision):
        """Testa criação a partir de dict."""
        engine = WiseDecisionEngine.from_dict(simple_decision)
        assert engine.decision_content == simple_decision


@pytest.mark.unit
class TestWiseDecisionEngineEvaluate:
    """Testes de avaliação de decisões."""
    
    def test_lazy_loading_decision(self, simple_decision):
        """Testa se a decisão é carregada sob demanda."""
        engine = WiseDecisionEngine(simple_decision)
        
        # Inicialmente, decisão não está carregada
        assert engine._decision is None
        
        # Ao acessar pela primeira vez, deve carregar
        decision = engine.decision
        assert decision is not None
        assert engine._decision is not None
    
    def test_evaluate_single_premium_client(self, simple_decision, test_data):
        """Testa avaliação de cliente premium."""
        engine = WiseDecisionEngine(simple_decision)
        
        # Cliente Premium: Lima (faturamento alto, score alto, situação regular)
        input_data = test_data[5]  # Lima - Cliente Premium
        result = engine.evaluate(input_data)
        
        assert "result" in result
        assert result["result"]["segmento"] == "Cliente Premium"
        assert result["result"]["score_final"] == 90
        assert result["result"]["cnpj"] == input_data["cnpj"]
    
    def test_evaluate_single_gold_client(self, simple_decision, test_data):
        """Testa avaliação de cliente gold."""
        engine = WiseDecisionEngine(simple_decision)
        
        # Cliente Gold: Freitas - ME (faturamento médio, score bom)
        input_data = test_data[0]  # Freitas - ME - Cliente Gold
        result = engine.evaluate(input_data)
        
        assert "result" in result
        assert result["result"]["segmento"] == "Cliente Gold"
        assert result["result"]["score_final"] == 75
        assert result["result"]["cnpj"] == input_data["cnpj"]
    
    def test_evaluate_single_high_risk(self, simple_decision, test_data):
        """Testa avaliação de cliente alto risco."""
        engine = WiseDecisionEngine(simple_decision)
        
        # Alto Risco: da Mota (mineração irregular, pendências fiscais)
        input_data = test_data[1]  # da Mota - Alto Risco
        result = engine.evaluate(input_data)
        
        assert "result" in result
        assert result["result"]["segmento"] == "Cliente Básico"
        assert result["result"]["score_final"] == 40
        assert result["result"]["cnpj"] == input_data["cnpj"]
    
    def test_evaluate_batch(self, simple_decision, test_data):
        """Testa avaliação em lote."""
        engine = WiseDecisionEngine(simple_decision)
        
        # Usa primeiros 3 registros dos dados de teste
        input_list = test_data[:3]
        
        results = engine.evaluate_batch(input_list)
        
        assert len(results) == 3
        
        # Verifica primeiro resultado (Cliente Gold)
        assert results[0]["result"]["segmento"] == "Cliente Gold"
        assert results[0]["result"]["score_final"] == 75
        
        # Verifica segundo resultado (Cliente Básico)
        assert results[1]["result"]["segmento"] == "Cliente Básico"
        assert results[1]["result"]["score_final"] == 40
        
        # Verifica terceiro resultado (Cliente Premium)
        assert results[2]["result"]["segmento"] == "Cliente Premium"
        assert results[2]["result"]["score_final"] == 90


@pytest.mark.unit
class TestWiseDecisionEngineErrors:
    """Testes de tratamento de erros."""
    
    def test_evaluate_with_invalid_decision(self):
        """Testa inicialização com decisão inválida."""
        # Testa com conteúdo de decisão completamente inválido
        invalid_decision = {"invalid": "content"}
        
        with pytest.raises(Exception):  # zen-engine lançará exceção
            engine = WiseDecisionEngine(invalid_decision)
            # Força a criação da decisão
            _ = engine.decision
