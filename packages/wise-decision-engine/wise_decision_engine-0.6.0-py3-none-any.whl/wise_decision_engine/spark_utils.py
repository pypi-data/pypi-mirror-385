"""
Utilitários otimizados para Spark/Databricks.

Transforma o uso complexo do zen-engine em UDFs simples e eficientes:
- UDFs otimizadas com SessionCache automático
- Broadcast automático de decisões
- Helpers para conversão de schemas
- Integração transparente com DataFrames
"""

import json
from typing import List, Optional, Callable, Union
from functools import wraps

try:
    from pyspark.sql import DataFrame, SparkSession
    from pyspark.sql.functions import pandas_udf, col, to_json, struct, from_json
    from pyspark.sql.types import StringType, StructType, StructField
    import pandas as pd
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    # Stubs para quando PySpark não estiver disponível
    DataFrame = None
    pandas_udf = None
    StringType = None


from .core import WiseDecisionEngine
from .adapters import DatabricksAdapter, DecisionAdapter
from .schema_inference import (
    AutoSchemaHelper, 
    auto_expand_decision_results
)


def require_pyspark(func):
    """Decorator que verifica se PySpark está disponível."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not PYSPARK_AVAILABLE:
            raise ImportError(
                "PySpark não está disponível. "
                "Instale com: pip install pyspark"
            )
        return func(*args, **kwargs)
    return wrapper


def is_databricks_serverless():
    """
    Detecta se estamos executando em ambiente Databricks Serverless.
    
    Returns:
        True se estivermos em Serverless, False caso contrário
    """
    try:
        spark = SparkSession.getActiveSession()
        if spark is None:
            return False
        # Tenta acessar sparkContext - falhará no Serverless
        _ = spark.sparkContext
        return False
    except Exception as e:
        # Se der erro ao acessar sparkContext, provavelmente é Serverless
        return "JVM_ATTRIBUTE_NOT_SUPPORTED" in str(e) or "serverless" in str(e).lower()


class SparkDecisionEvaluator:
    """
    Avaliador de decisões otimizado para Spark/Databricks.
    
    Transforma o uso complexo do zen-engine em UDFs simples e eficientes.
    Usa SessionCache automático para máxima performance.
    """
    
    def __init__(self, 
                 adapter: DecisionAdapter, 
                 decision_name: str,
                 result_columns: Optional[List[str]] = None):
        """
        Inicializa avaliador Spark.
        
        Args:
            adapter: Adaptador para buscar a decisão
            decision_name: Nome da decisão a ser carregada
            result_columns: Colunas específicas do resultado a extrair
        """
        self.adapter = adapter
        self.decision_name = decision_name
        self.result_columns = result_columns
        
        # Carrega engine uma vez (usa cache automaticamente)
        self.engine = WiseDecisionEngine.from_adapter(adapter, decision_name)
        
        # Prepara informações para broadcast
        self._decision_content = self.engine.decision_content
        self._broadcast_decision = None
    
    @require_pyspark
    def _create_broadcast_decision(self, spark_session):
        """Cria broadcast variable da decisão se não existir.
        
        Compatível com Databricks Serverless - usa serialização direta
        ao invés de broadcast variables quando sparkContext não está disponível.
        """
        if self._broadcast_decision is None:
            try:
                # Tenta usar broadcast em clusters tradicionais
                sc = spark_session.sparkContext
                self._broadcast_decision = sc.broadcast(self._decision_content)
            except Exception:
                # Fallback para Serverless - usa conteúdo direto
                self._broadcast_decision = type('BroadcastFallback', (), {
                    'value': self._decision_content
                })
        return self._broadcast_decision
    
    @require_pyspark
    def create_udf(self, return_full_result: bool = False) -> Callable:
        """
        Cria UDF otimizada para usar em DataFrames.
        
        Args:
            return_full_result: Se True, retorna resultado completo.
                               Se False, retorna apenas campos de 'result'
        
        Returns:
            UDF pronta para usar em withColumn()
        """
        # Obtém SparkSession para broadcast (compatível com Serverless)
        spark = SparkSession.getActiveSession()
        if spark is None:
            raise Exception("Nenhuma SparkSession ativa encontrada")
        
        broadcast_decision = self._create_broadcast_decision(spark)
        
        @pandas_udf(StringType())
        def evaluate_decision_udf(json_input: pd.Series) -> pd.Series:
            """
            UDF otimizada para avaliar decisões em lote.
            
            Usa broadcast variable para compartilhar decisão entre executors.
            Processa múltiplas linhas em pandas Series para máxima eficiência.
            """
            # Lazy loading do engine no worker
            if not hasattr(evaluate_decision_udf, "_engine"):
                from .core import WiseDecisionEngine
                import zen
                
                # Cria engine a partir do broadcast
                decision_content = broadcast_decision.value
                zen_engine = zen.ZenEngine()
                decision = zen_engine.create_decision(decision_content)
                
                # Armazena para reutilização no worker
                evaluate_decision_udf._engine = decision
            
            engine = evaluate_decision_udf._engine
            results = []
            
            for json_line in json_input:
                try:
                    # Parse input
                    input_data = json.loads(json_line)
                    
                    # Avalia decisão
                    result = engine.evaluate(input_data)
                    
                    if return_full_result:
                        # Retorna resultado completo
                        results.append(json.dumps(result))
                    else:
                        # Retorna apenas campos do 'result'
                        if 'result' in result:
                            results.append(json.dumps(result['result']))
                        else:
                            results.append(json.dumps(result))
                            
                except Exception as e:
                    # Em caso de erro, retorna JSON com erro
                    error_result = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    results.append(json.dumps(error_result))
            
            return pd.Series(results)
        
        return evaluate_decision_udf
    
    @require_pyspark
    def apply_to_dataframe(self, 
                          df: DataFrame, 
                          result_column: str = "decision_result",
                          input_columns: Optional[List[str]] = None,
                          expand_result: bool = True,
                          auto_schema: bool = True,
                          schema_strategy: str = "conservative",
                          original_fields: Union[bool, List[str]] = True,
                          decision_fields: Union[bool, List[str]] = True,
                          return_only_new_fields: Union[bool, List[str]] = None) -> DataFrame:
        """
        Aplica decisão em DataFrame inteiro de forma otimizada.
        
        Args:
            df: DataFrame de entrada
            result_column: Nome da coluna com o resultado
            input_columns: Colunas específicas para incluir (None = todas)
            expand_result: Se True, expande campos do resultado como colunas
            auto_schema: Se True, usa schema inference automática
            schema_strategy: "conservative", "aggressive", ou "flat_only"
            original_fields: Campos originais a incluir no resultado
                - True: Todos os campos originais (padrão)
                - False: Nenhum campo original
                - List[str]: Campos específicos ['customer_id', 'account_id']
            decision_fields: Campos da decisão a incluir no resultado
                - True: Todos os campos gerados pela decisão (padrão)
                - False: Nenhum campo da decisão
                - List[str]: Campos específicos ['decision_score', 'decision_approved']
            return_only_new_fields: DEPRECATED - Use original_fields e decision_fields
            
        Returns:
            DataFrame com campos selecionados conforme especificação
        """
        # Handle deprecated parameter with backward compatibility
        if return_only_new_fields is not None:
            import warnings
            warnings.warn(
                "return_only_new_fields is deprecated. Use original_fields and decision_fields instead.", 
                DeprecationWarning, 
                stacklevel=2
            )
            
            if return_only_new_fields is True:
                original_fields = False
                decision_fields = True
            elif return_only_new_fields is False:
                original_fields = True
                decision_fields = True
            elif isinstance(return_only_new_fields, list):
                original_fields = return_only_new_fields
                decision_fields = True
        
        # Captura colunas originais antes do processamento
        original_columns = set(df.columns)
        
        # Prepara input JSON
        if input_columns:
            struct_cols = [col(c) for c in input_columns if c in df.columns]
        else:
            struct_cols = [col(c) for c in df.columns]
        
        # Cria UDF
        decision_udf = self.create_udf(return_full_result=not expand_result)
        
        # Aplica decisão
        result_df = (
            df.withColumn("_input_json", to_json(struct(*struct_cols)))
            .withColumn(result_column, decision_udf(col("_input_json")))
            .drop("_input_json")
        )
        
        # Expande resultado se solicitado
        if expand_result:
            if auto_schema:
                # Usa schema inference automática
                result_df = auto_expand_decision_results(
                    result_df, 
                    result_column, 
                    schema_strategy,
                    prefix=False,
                    keep_original=False  # Remove coluna original por padrão
                )
            else:
                # Usa método manual (backward compatibility)
                result_df = self._expand_decision_result(result_df, result_column)
        
        # 🔥 NOVA LÓGICA: Seleção inteligente de campos
        final_columns = set(result_df.columns)
        new_decision_columns = final_columns - original_columns
        
        # Determina quais colunas originais incluir
        if original_fields is True:
            selected_original = original_columns
        elif original_fields is False:
            selected_original = set()
        else:  # Lista
            selected_original = {col for col in original_fields if col in original_columns}
        
        # Determina quais colunas de decisão incluir
        if decision_fields is True:
            selected_decision = new_decision_columns
        elif decision_fields is False:
            selected_decision = set()
        else:  # Lista
            selected_decision = {col for col in decision_fields if col in new_decision_columns}
        
        # Combina seleções
        final_selection = selected_original | selected_decision
        
        if final_selection:
            return result_df.select(*sorted(final_selection))
        else:
            # Edge case: seleção vazia
            from pyspark.sql.functions import lit
            return result_df.select(lit(None).alias("_empty_selection")).drop("_empty_selection")
    
    def _expand_decision_result(self, df: DataFrame, result_column: str) -> DataFrame:
        """Expande resultado JSON em colunas separadas."""
        # Se temos colunas específicas, cria schema
        if self.result_columns:
            # Cria schema básico baseado nas colunas solicitadas
            fields = [StructField(col_name, StringType(), True) 
                     for col_name in self.result_columns]
            result_schema = StructType(fields)
            
            # Aplica schema e extrai colunas
            expanded_df = df.withColumn(
                "_parsed_result", 
                from_json(col(result_column), result_schema)
            )
            
            # Adiciona colunas individuais
            for field in result_schema.fields:
                expanded_df = expanded_df.withColumn(
                    field.name,
                    col(f"_parsed_result.{field.name}")
                )
            
            return expanded_df.drop("_parsed_result")
        else:
            # Sem schema específico, mantém resultado como JSON
            return df


@require_pyspark
def create_decision_udf(adapter: DecisionAdapter, 
                       decision_name: str,
                       result_columns: Optional[List[str]] = None,
                       return_full_result: bool = False) -> Callable:
    """
    Factory function para criar UDF de decisão rapidamente.
    
    Args:
        adapter: Adaptador para buscar decisão
        decision_name: Nome da decisão
        result_columns: Colunas específicas a extrair
        return_full_result: Se deve retornar resultado completo
        
    Returns:
        UDF pronta para usar
        
    Example:
        ```python
        adapter = DatabricksAdapter("catalog", "schema", "table")
        udf = create_decision_udf(adapter, "credito-pj")
        
        df.withColumn("score", udf(to_json(struct("*"))))
        ```
    """
    evaluator = SparkDecisionEvaluator(adapter, decision_name, result_columns)
    return evaluator.create_udf(return_full_result)


@require_pyspark  
def apply_decision_to_dataframe(df: DataFrame,
                               adapter: DecisionAdapter,
                               decision_name: str,
                               result_column: str = "decision_result",
                               input_columns: Optional[List[str]] = None,
                               result_columns: Optional[List[str]] = None,
                               expand_result: bool = True,
                               auto_schema: bool = True,
                               schema_strategy: str = "conservative",
                               original_fields: Union[bool, List[str]] = True,
                               decision_fields: Union[bool, List[str]] = True,
                               return_only_new_fields: Union[bool, List[str]] = None) -> DataFrame:
    """
    Aplica decisão em DataFrame - função de conveniência com schema inference automática.
    
    Args:
        df: DataFrame de entrada  
        adapter: Adaptador para buscar decisão
        decision_name: Nome da decisão
        result_column: Nome da coluna resultado
        input_columns: Colunas de entrada (None = todas)
        result_columns: Colunas resultado a extrair
        expand_result: Se deve expandir resultado
        auto_schema: Se True, usa schema inference automática
        schema_strategy: "conservative", "aggressive", ou "flat_only"
        original_fields: Campos originais a incluir no resultado
            - True: Todos os campos originais (padrão)
            - False: Nenhum campo original
            - List[str]: Campos específicos ['customer_id', 'account_id']
        decision_fields: Campos da decisão a incluir no resultado
            - True: Todos os campos gerados pela decisão (padrão)
            - False: Nenhum campo da decisão
            - List[str]: Campos específicos ['decision_score', 'decision_approved']
        return_only_new_fields: DEPRECATED - Use original_fields e decision_fields
        
    Returns:
        DataFrame com decisão aplicada
        
    Example:
        ```python
        adapter = DatabricksAdapter("catalog", "schema", "table")
        
        resultado_df = apply_decision_to_dataframe(
            clientes_df,
            adapter, 
            "credito-pj",
            auto_schema=True,
            schema_strategy="aggressive"
        )
        ```
    """
    evaluator = SparkDecisionEvaluator(adapter, decision_name, result_columns)
    return evaluator.apply_to_dataframe(
        df, result_column, input_columns, expand_result, auto_schema, schema_strategy, 
        original_fields, decision_fields, return_only_new_fields
    )


class DatabricksHelper:
    """Helper específico para ambiente Databricks."""
    
    @staticmethod
    @require_pyspark
    def quick_decision_apply(catalog: str,
                           schema: str, 
                           table: str,
                           decision_name: str,
                           data_df: DataFrame,
                           result_columns: Optional[List[str]] = None,
                           auto_schema: bool = True,
                           schema_strategy: str = "conservative",
                           show_schema_info: bool = False,
                           original_fields: Union[bool, List[str]] = True,
                           decision_fields: Union[bool, List[str]] = True,
                           return_only_new_fields: Union[bool, List[str]] = None) -> DataFrame:
        """
        Aplica decisão em DataFrame de forma ultra-rápida com schema inference automática.
        
        Método mais simples possível para Databricks com expansão automática de colunas.
        
        Args:
            catalog: Catálogo Databricks
            schema: Schema da tabela
            table: Tabela com decisões
            decision_name: Nome da decisão
            data_df: DataFrame com dados
            result_columns: Colunas resultado (None = todas - usado apenas se auto_schema=False)
            auto_schema: Se True, usa schema inference automática
            schema_strategy: "conservative" (default), "aggressive", ou "flat_only"
            show_schema_info: Se True, mostra informações do schema inferido
            original_fields: Campos originais a incluir no resultado
                - True: Todos os campos originais (padrão)
                - False: Nenhum campo original
                - List[str]: Campos específicos ['customer_id', 'account_id']
            decision_fields: Campos da decisão a incluir no resultado
                - True: Todos os campos gerados pela decisão (padrão)
                - False: Nenhum campo da decisão
                - List[str]: Campos específicos ['decision_score', 'decision_approved']
            return_only_new_fields: DEPRECATED - Use original_fields e decision_fields
            
        Returns:
            DataFrame com resultado expandido automaticamente
            
        Examples:
            ```python
            # 1. Comportamento padrão: todos os campos
            resultado_completo = DatabricksHelper.quick_decision_apply(
                "wisedecisions_catalog", "public", "decision",
                "credito-pj", clientes_df
            )
            
            # 2. Apenas campos da decisão
            apenas_decisao = DatabricksHelper.quick_decision_apply(
                "wisedecisions_catalog", "public", "decision",
                "credito-pj", clientes_df,
                original_fields=False,
                decision_fields=True
            )
            
            # 3. Join otimizado: chaves + decisão
            join_otimizado = DatabricksHelper.quick_decision_apply(
                "wisedecisions_catalog", "public", "decision",
                "credito-pj", clientes_df,
                auto_schema=True,
                original_fields=['customer_id', 'account_id'],
                decision_fields=True
            )
            
            # 4. Análise específica: campos selecionados
            analise_especifica = DatabricksHelper.quick_decision_apply(
                "wisedecisions_catalog", "public", "decision",
                "credito-pj", clientes_df,
                original_fields=['customer_id', 'renda'],
                decision_fields=['decision_score', 'decision_approved']
            )
            ```
        """
        # Cria adapter automaticamente
        adapter = DatabricksAdapter(catalog, schema, table)
        
        # Aplica decisão com schema inference automática
        result_df = apply_decision_to_dataframe(
            data_df, adapter, decision_name,
            result_columns=result_columns,
            expand_result=True,
            auto_schema=auto_schema,
            schema_strategy=schema_strategy,
            original_fields=original_fields,
            decision_fields=decision_fields,
            return_only_new_fields=return_only_new_fields
        )
        
        # Mostra informações do schema se solicitado
        if show_schema_info and auto_schema:
            print("\n📊 Schema Inference aplicada:")
            AutoSchemaHelper.print_schema_info(result_df, "decision_result")
        
        return result_df
    
    @staticmethod
    @require_pyspark
    def create_reusable_udf(catalog: str,
                          schema: str,
                          table: str, 
                          decision_name: str,
                          udf_name: str = None) -> Callable:
        """
        Cria UDF reutilizável registrada no Spark.
        
        Args:
            catalog: Catálogo Databricks
            schema: Schema da tabela  
            table: Tabela com decisões
            decision_name: Nome da decisão
            udf_name: Nome da UDF (None = auto-gerado)
            
        Returns:
            UDF registrada
            
        Example:
            ```python
            # Cria UDF uma vez
            avaliar_credito = DatabricksHelper.create_reusable_udf(
                "wisedecisions_catalog", "public", "decision", "credito-pj"
            )
            
            # Usa quantas vezes quiser
            df1.withColumn("score", avaliar_credito(to_json(struct("*"))))
            df2.withColumn("score", avaliar_credito(to_json(struct("*"))))
            ```
        """
        adapter = DatabricksAdapter(catalog, schema, table)
        udf = create_decision_udf(adapter, decision_name)
        
        # Registra UDF no Spark se nome fornecido
        if udf_name:
            spark = SparkSession.getActiveSession()
            spark.udf.register(udf_name, udf)
            print(f"✅ UDF '{udf_name}' registrada com sucesso!")
        
        return udf


def print_migration_guide():
    """Imprime guia de migração do código atual para utilitários."""
    guide = """
🚀 Guia de Migração - Wise Decision Engine Spark Utils

ANTES (seu código atual - 50+ linhas):
```python
@pandas_udf(StringType())
def wd_evaluate_decision(json_input: pd.Series) -> pd.Series:
    if not hasattr(wd_evaluate_decision, "_decision"):
        content = json.loads(content_value)
        wd_evaluate_decision._decision = zen.ZenEngine().create_decision(content)
    
    decision = wd_evaluate_decision._decision
    
    def avaliar(linha_json):
        entrada = json.loads(linha_json)
        resultado = decision.evaluate(entrada)
        return json.dumps(resultado)
    
    return json_input.apply(avaliar)

resultado_df = (
    clientes_df
    .withColumn("linha_json", to_json(struct("*")))
    .withColumn("wd_result", wd_evaluate_decision("linha_json"))
    .drop("linha_json")
)
```

DEPOIS (com Spark Utils - 1 linha!):
```python
resultado_df = DatabricksHelper.quick_decision_apply(
    "wisedecisions_catalog", "public", "decision", 
    "credito-pj", clientes_df, ["segmento", "score_final"]
)
```

✅ Benefícios:
• 50x menos código
• Cache automático (SessionCache) 
• Broadcast automático da decisão
• Tratamento de erros integrado
• Schema inference automática
• Performance otimizada
"""
    print(guide)


# Compatibilidade com código existente
def create_legacy_udf(content_value: str) -> Callable:
    """
    Cria UDF compatível com código legado.
    
    Para migração gradual do código existente.
    """
    if not PYSPARK_AVAILABLE:
        raise ImportError("PySpark não disponível")
    
    @pandas_udf(StringType())
    def legacy_udf(json_input: pd.Series) -> pd.Series:
        """UDF compatível com código antigo."""
        if not hasattr(legacy_udf, "_engine"):
            import zen
            content = json.loads(content_value)
            zen_engine = zen.ZenEngine()
            legacy_udf._engine = zen_engine.create_decision(content)
        
        engine = legacy_udf._engine
        
        def avaliar(linha_json):
            entrada = json.loads(linha_json)
            resultado = engine.evaluate(entrada)
            return json.dumps(resultado)
        
        return json_input.apply(avaliar)
    
    return legacy_udf