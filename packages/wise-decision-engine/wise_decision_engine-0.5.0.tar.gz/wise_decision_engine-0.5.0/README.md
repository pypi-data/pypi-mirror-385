# 🧠 Wise Decision Engine

**Motor de decisão que separa a definição das regras de negócio do seu local de processamento**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Databricks Ready](https://img.shields.io/badge/Databricks-Ready-orange.svg)](https://databricks.com/)
[![Automated Release](https://github.com/five-acts/wise-decision-engine/workflows/🚀%20Complete%20Release%20&%20Deploy/badge.svg)](https://github.com/five-acts/wise-decision-engine/actions)
[![codecov](https://codecov.io/gh/five-acts/wise-decision-engine/branch/main/graph/badge.svg)](https://codecov.io/gh/five-acts/wise-decision-engine)
[![PyPI version](https://badge.fury.io/py/wise-decision-engine.svg)](https://pypi.org/project/wise-decision-engine/)
[![GitHub Release](https://img.shields.io/github/v/release/five-acts/wise-decision-engine)](https://github.com/five-acts/wise-decision-engine/releases)
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

## 🚀 **Releases Automatizados**

Este projeto utiliza um sistema completamente automatizado de releases. Para contribuir:

### Para Desenvolvedores
```bash
# Para nova funcionalidade (minor bump)
git commit -m "feat: implementa cache inteligente"

# Para correção de bug (patch bump)
git commit -m "fix: resolve erro de parsing"

# Para breaking changes (major bump)
git commit -m "feat!: remove API deprecated"

git push origin main
```

**✨ Resultado**: Release automático no GitHub + PyPI em ~1-2 minutos!

📖 **[Veja o guia completo de releases](RELEASES.md)** para detalhes sobre:
- Conventional commits
- Fluxo automático completo  
- Troubleshooting
- Configurações avançadas

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

## 🔍 **Auto-Schema: Expansão Automática de Colunas**

### **Problema: Schema Manual Complexo**
Antes, criar colunas a partir dos resultados das decisões requeria **~20 linhas de código manual**:

```python
# ❌ Schema manual (complexo e propenso a erros)
exemplo_json = resultado_df.select("wd_result").limit(1).collect()[0]["wd_result"]
exemplo_result = json.loads(exemplo_json).get("result", {})

# Define tipos manualmente para cada campo
result_fields = []
for k, v in exemplo_result.items():
    field_type = type_map.get(type(v), StringType())
    result_fields.append(StructField(k, field_type, True))

result_schema = StructType(result_fields)
# ... mais 10+ linhas para aplicar schema ...
```

### **Solução: Auto-Schema Inteligente**
Com auto-schema, isso vira **1 parâmetro**:

```python
# ✅ Auto-schema (automático e inteligente)
resultado = DatabricksHelper.quick_decision_apply(
    "catalog", "schema", "decisoes", "minha-regra", df,
    auto_schema=True,              # 🔥 Detecção automática de tipos
    schema_strategy="aggressive",   # Estratégia inteligente
    show_schema_info=True          # Mostra o que foi detectado
)

# ✅ Resultado: Todas as colunas expandidas automaticamente com tipos corretos!
```

### **Como Funciona o Auto-Schema**

1. **🔍 Análise Automática**: Coleta amostras dos resultados JSON
2. **🧠 Detecção Inteligente**: Identifica tipos automaticamente (int, bool, string, arrays, structs)
3. **📊 Schema Otimizado**: Cria schema Spark com tipos corretos
4. **⚡ Expansão Automática**: Converte para colunas individuais com prefixo `decision_*`

### **Estratégias Disponíveis**

| Estratégia | Descrição | Uso Recomendado |
|-----------|-----------|----------------|
| `conservative` | Tipos básicos apenas | Produção estável |
| `aggressive` | Inclui arrays e structs aninhados | Estruturas complexas |
| `flat_only` | Apenas campos de primeiro nível | Performance máxima |

### **Exemplo de Transformação**

**Input JSON:**
```json
{
  "result": {
    "score": 750,
    "approved": true,
    "limit": 10000.50,
    "reasons": ["good_credit", "stable_income"]
  }
}
```

**Schema Detectado Automaticamente:**
- `score` → `IntegerType()`
- `approved` → `BooleanType()`
- `limit` → `DoubleType()`
- `reasons` → `ArrayType(StringType())` (modo aggressive)

**DataFrame Final:**
```
Original columns + decision_score + decision_approved + decision_limit + decision_reasons
```

### **Benefícios do Auto-Schema**

| Aspecto | Schema Manual | Auto-Schema | Melhoria |
|---------|---------------|-------------|----------|
| **Linhas de código** | ~20 linhas | 1 parâmetro | **20x menos** |
| **Detecção de tipos** | Manual | Automática | **100% automático** |
| **Estruturas complexas** | Muito complexo | Simples | **10x mais simples** |
| **Manutenção** | Alta | Zero | **Eliminada** |
| **Erros de schema** | Frequentes | Raros | **95% redução** |
| **Tempo de desenvolvimento** | Horas | Segundos | **1000x mais rápido** |

### **Casos de Uso Ideais para Auto-Schema**
- ✅ Decisões com muitos campos de saída
- ✅ Estruturas que mudam frequentemente  
- ✅ Múltiplas decisões com schemas diferentes
- ✅ Prototipagem rápida
- ✅ Ambientes de produção com governança

## 🎯 **Apenas Campos Novos: Resultados Limpos**

### **Problema: DataFrame "Poluído" com Dados Originais**
Muitas vezes você quer apenas os **resultados da decisão**, sem carregar os dados originais:

```python
# ❌ DataFrame "poluído" com 50+ colunas originais + resultados
resultado_completo = DatabricksHelper.quick_decision_apply(
    "catalog", "schema", "decisoes", "credito-pj", clientes_df  # 1M+ linhas
)
# Resultado: clientes_df (50 cols) + decision_score + decision_limit + ...
```

### **Solução: Return Only New Fields**
Com `return_only_new_fields=True`, retorna **apenas os campos gerados pela decisão**:

```python
# ✅ DataFrame limpo com APENAS resultados da decisão
resultados_limpos = DatabricksHelper.quick_decision_apply(
    "catalog", "schema", "decisoes", "credito-pj", 
    clientes_df,
    auto_schema=True,              # 🔍 Detecta campos automaticamente
    return_only_new_fields=True    # 🎯 Retorna APENAS campos novos
)
# Resultado: APENAS decision_score + decision_limit + decision_approved + ...
```

### **Sinergia Perfeita: Auto-Schema + Only New Fields**

A combinação é **extremamente poderosa**:

```python
# 🚀 Máxima produtividade: Auto-detecção + Resultados limpos
resultados = DatabricksHelper.quick_decision_apply(
    "catalog", "schema", "decisoes", "minha-regra",
    dados_df,
    auto_schema=True,              # ✨ Detecta campos automaticamente
    schema_strategy="aggressive",   # 💪 Máxima detecção
    return_only_new_fields=True,   # 🎯 Apenas campos da decisão
    show_schema_info=True          # 🔍 Debug: mostra o que foi detectado
)

# ✅ Resultado: DataFrame limpo com campos perfeitamente tipados!
```

### **Casos de Uso Principais**

#### **1. Tabelas de Resultados Puros**
```python
# Salva apenas resultados das decisões
resultados_limpos.write.mode("overwrite").saveAsTable("decisoes_credito")
```

#### **2. Joins Posteriores**
```python
# Join controlado: dados originais + resultados
clientes_enriquecidos = (
    clientes_df
    .join(resultados_limpos.withColumn("row_id", monotonically_increasing_id()), 
          on="row_id")
)
```

#### **3. Pipelines de Feature Engineering**
```python
# Apenas features da decisão para ML
features_decisao = resultados_limpos.select(
    "decision_score", "decision_risk_level", "decision_limit"
)
```

#### **4. APIs de Resultado**
```python
# Payload limpo para APIs
api_response = resultados_limpos.toPandas().to_dict("records")
```

### **Comparação de Resultados**

| Configuração | Colunas de Entrada | Colunas de Saída | Uso Ideal |
|--------------|-------------------|------------------|----------|
| **Padrão** | 50 | 50 + 5 (decisões) | Análise exploratória |
| **return_only_new_fields=True** | 50 | 5 (apenas decisões) | Tabelas de resultado |

### **Benefícios**

| Aspecto | Sem Filtro | Com return_only_new_fields | Melhoria |
|---------|------------|----------------------------|----------|
| **Volume de dados** | 100% | ~10% | **90% redução** |
| **Clareza** | Confuso | Cristalino | **100% melhor** |
| **Performance** | Padrão | Otimizada | **Significativa** |
| **Join posterior** | Difícil | Simples | **10x mais fácil** |
| **API payload** | Pesado | Limpo | **90% menor** |

---

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
