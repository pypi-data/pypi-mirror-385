# 🧠 Wise Decision Engine

**Motor de decisão que separa a definição das regras de negócio do seu local de processamento**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Databricks Ready](https://img.shields.io/badge/Databricks-Ready-orange.svg)](https://databricks.com/)
[![CI/CD](https://github.com/five-acts/wise-decision-engine/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/five-acts/wise-decision-engine/actions)
[![codecov](https://codecov.io/gh/five-acts/wise-decision-engine/branch/main/graph/badge.svg)](https://codecov.io/gh/five-acts/wise-decision-engine)
[![PyPI version](https://badge.fury.io/py/wise-decision-engine.svg)](https://badge.fury.io/py/wise-decision-engine)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 💼 **Problema de Negócio**

Em ambientes corporativos, **as regras de negócio mudam constantemente** mas estão frequentemente **acopladas ao código de processamento**. Isso gera:

- ⏳ **Demora para mudanças**: Alterações simples requerem deploy completo
- 🔄 **Dependência técnica**: Regras de negócio presas no pipeline de dados 
- 🚫 **Falta de governança**: Regras espalhadas e sem controle centralizado
- 💸 **Alto custo de manutenção**: Equipe técnica para mudanças de negócio

## 🎯 **Solução: Separação de Responsabilidades**

O **Wise Decision Engine** permite:

| **🏛️ DEFINIÇÃO DA REGRA** | **⚙️ PROCESSAMENTO DOS DADOS** |
|---------------------------|--------------------------------|
| Armazenada em **tabelas/arquivos** | Executado em **Spark/Databricks** |
| Modificável por **analistas** | Gerenciado por **engenheiros** |
| **Governança centralizada** | **Performance otimizada** |
| **Versionamento de regras** | **Processamento distribuído** |

## 🔧 **Como Funciona**

### 1. **Defina a Regra** (Uma vez)
```json
// Salva em tabela Databricks ou arquivo JSON
{
  "name": "aprovacao-credito",
  "rules": {
    "if": [{"var": "renda"}, ">", 5000],
    "then": {"aprovado": true, "limite": 10000},
    "else": {"aprovado": false, "limite": 0}
  }
}
```

### 2. **Processe os Dados** (Sempre que necessário)
```python
from wise_decision_engine import DatabricksHelper

# Uma linha aplica a regra para milhões de registros
resultado = DatabricksHelper.quick_decision_apply(
    catalog="regras_catalog",
    schema="public", 
    table="decisoes",
    decision_name="aprovacao-credito",
    input_df=clientes_df  # DataFrame com milhões de clientes
)

# ✅ Resultado: DataFrame com decisões aplicadas automaticamente
resultado.show()
```

### 3. **Mude a Regra** (Sem redeploy)
```sql
-- Analista de negócio altera diretamente na tabela
UPDATE regras_catalog.public.decisoes 
SET content = '{"rules": {"if": [{"var": "renda"}, ">", 8000], ...}}'
WHERE name = 'aprovacao-credito';

-- ✅ Próxima execução já usa a nova regra (cache automático)
```

## 📦 **Instalação**

```bash
pip install wise-decision-engine
```

## 🚀 **Casos de Uso Reais**

### **Aprovação de Crédito**
```python
# Regra armazenada em tabela Databricks
# Processamento em Spark para milhões de clientes
resultado = DatabricksHelper.quick_decision_apply(
    "financeiro_catalog", "regras", "decisoes",
    "aprovacao-pf", clientes_df
)
```

### **Detecção de Fraude**
```python
# Mesma interface, regra diferente
# Analista atualiza regra sem código
resultado = DatabricksHelper.quick_decision_apply(
    "risco_catalog", "regras", "decisoes", 
    "deteccao-fraude", transacoes_df
)
```

### **Precificação Dinâmica**
```python
# Regras de pricing atualizadas em tempo real
resultado = DatabricksHelper.quick_decision_apply(
    "comercial_catalog", "regras", "decisoes",
    "precificacao-produto", vendas_df
)
```

## 🎯 **Benefícios de Negócio**

### **Para Analistas de Negócio**
- ✅ **Autonomia total**: Alteram regras sem depender de TI
- ✅ **Versionamento**: Histórico completo de mudanças
- ✅ **Teste A/B**: Diferentes versões de regras facilmente
- ✅ **Governança**: Controle centralizado de todas as regras

### **Para Engenheiros de Dados** 
- ✅ **Menos deploy**: Mudanças de regra não requerem código
- ✅ **Performance**: Processamento otimizado para Spark
- ✅ **Manutenibilidade**: Código limpo e desacoplado
- ✅ **Escalabilidade**: Engine preparada para big data

### **Para Organização**
- 💰 **Redução de custos**: 80% menos tempo para mudanças
- ⚡ **Time-to-market**: Novas regras em minutos, não semanas
- 🔒 **Compliance**: Auditoria completa de regras aplicadas
- 📈 **Agilidade**: Resposta rápida a mudanças de mercado

## 🏗️ **Arquitetura da Solução**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   📋 REGRAS     │    │  🔄 PROCESSING   │    │  📊 RESULTADO   │
│                 │    │                  │    │                 │
│ • Tabela Delta  │───▶│ • Spark Engine   │───▶│ • DataFrame     │
│ • Arquivos JSON │    │ • Cache Auto     │    │ • Schema Auto   │
│ • Versionadas   │    │ • UDFs Otimizas  │    │ • Performance   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **Separação Clara de Responsabilidades**
- **📋 Camada de Regras**: Definição e governança (Analistas)
- **🔄 Camada de Processamento**: Performance e escala (Engenheiros)  
- **📊 Camada de Resultado**: Consumo e análise (Usuários finais)

## ⚙️ **Configuração Avançada**

### **Adapters Disponíveis**

```python
from wise_decision_engine import WiseDecisionEngine, DatabricksAdapter, FileAdapter

# Para tabelas Databricks
adapter = DatabricksAdapter(
    catalog="meu_catalog",
    schema="regras", 
    table="decisoes"
)

# Para arquivos JSON locais
adapter = FileAdapter(file_path="/path/to/rules.json")

# Engine configurável
engine = WiseDecisionEngine(adapter=adapter)
```

## 💡 **Exemplo Completo**

### **Notebook Databricks**

```python
# 1. Instalar
%pip install wise-decision-engine

# 2. Aplicar decisão
from wise_decision_engine import DatabricksHelper

resultado = DatabricksHelper.quick_decision_apply(
    catalog="regras_catalog",
    schema="public", 
    table="decisoes",
    decision_name="minha-regra",
    input_df=meus_dados_df
)

# 3. Visualizar resultado
resultado.display()
```

## 🤝 **Contribuição e Suporte**

### **Repositório**
- **Código**: [GitHub](https://github.com/five-acts/wise-decision-engine)
- **Issues**: [Reportar problemas](https://github.com/five-acts/wise-decision-engine/issues)
- **Documentação**: [Wiki](https://github.com/five-acts/wise-decision-engine/wiki)

### **Como Contribuir**
1. Fork o repositório
2. Crie sua feature branch
3. Commit suas mudanças
4. Abra um Pull Request


---

## 📄 **Licença**

MIT License - veja [LICENSE](LICENSE) para detalhes.

**Construído pela [Five Acts](https://github.com/five-acts)** 🎆
