"""
Schema Inference automática para WiseDecisionEngine.

Detecta automaticamente a estrutura dos resultados das decisões
e cria schemas Spark apropriados para expansão automática.
"""

import json
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from pyspark.sql.types import (
        StructType, StructField, StringType, IntegerType, 
        DoubleType, BooleanType, ArrayType, MapType, LongType, FloatType
    )
    from pyspark.sql.functions import col, from_json
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    # Classes dummy para quando PySpark não está disponível
    class StringType:
        pass
    class IntegerType:
        pass
    class DoubleType:
        pass
    class BooleanType:
        pass
    class LongType:
        pass
    class FloatType:
        pass
    class ArrayType:
        def __init__(self, element_type):
            pass
    class StructType:
        def __init__(self, fields=None):
            pass
    class StructField:
        def __init__(self, name, data_type, nullable):
            pass


class InferenceStrategy(Enum):
    """Estratégias de inferência de schema."""
    CONSERVATIVE = "conservative"  # Apenas tipos básicos
    AGGRESSIVE = "aggressive"     # Inclui arrays e maps
    FLAT_ONLY = "flat_only"      # Só campos planos (sem nested)


@dataclass
class SchemaStats:
    """Estatísticas sobre schema inference."""
    samples_analyzed: int = 0
    fields_detected: int = 0
    nested_levels: int = 0
    strategy_used: str = ""
    confidence_score: float = 0.0


class SchemaInferenceEngine:
    """
    Engine de inferência automática de schema para resultados de decisões.
    
    Analisa automaticamente os resultados e cria schemas Spark otimizados.
    """
    
    def __init__(self, 
                 strategy: InferenceStrategy = InferenceStrategy.CONSERVATIVE,
                 sample_size: int = 10,
                 confidence_threshold: float = 0.8):
        """
        Inicializa engine de schema inference.
        
        Args:
            strategy: Estratégia de inferência
            sample_size: Número de amostras para análise
            confidence_threshold: Threshold mínimo de confiança
        """
        self.strategy = strategy
        self.sample_size = sample_size
        self.confidence_threshold = confidence_threshold
        self._type_counter = {}
        self._field_counter = {}
    
    def _python_type_to_spark_type(self, py_type, value=None):
        """Converte tipo Python para tipo Spark."""
        if not PYSPARK_AVAILABLE:
            return "string"
        
        type_map = {
            str: StringType(),
            int: IntegerType(),
            float: DoubleType(),
            bool: BooleanType(),
            type(None): StringType()
        }
        
        # Para valores grandes, usa LongType
        if py_type == int and value is not None and abs(value) > 2147483647:
            return LongType()
        
        # Para floats pequenos, pode usar FloatType
        if py_type == float and value is not None and abs(value) < 3.4e38:
            return FloatType()
        
        return type_map.get(py_type, StringType())
    
    def _analyze_value(self, value, field_path=""):
        """Analisa um valor recursivamente."""
        if value is None:
            return StringType()
        
        py_type = type(value)
        
        # Tipos básicos
        if py_type in [str, int, float, bool]:
            return self._python_type_to_spark_type(py_type, value)
        
        # Arrays
        elif isinstance(value, list):
            if self.strategy == InferenceStrategy.FLAT_ONLY:
                return StringType()  # Serializa como JSON
            
            if not value:  # Lista vazia
                return ArrayType(StringType())
            
            # Infere tipo do primeiro elemento não-nulo
            element_type = StringType()
            for item in value[:5]:  # Analisa até 5 elementos
                if item is not None:
                    element_type = self._analyze_value(item, f"{field_path}[]")
                    break
            
            return ArrayType(element_type)
        
        # Maps/Objects
        elif isinstance(value, dict):
            if self.strategy == InferenceStrategy.FLAT_ONLY:
                return StringType()  # Serializa como JSON
            
            fields = []
            for key, val in value.items():
                if isinstance(key, str):  # Chaves devem ser strings
                    field_type = self._analyze_value(val, f"{field_path}.{key}")
                    fields.append(StructField(key, field_type, True))
            
            return StructType(fields) if fields else StringType()
        
        # Fallback
        return StringType()
    
    def _analyze_sample(self, result_sample: str) -> Dict[str, Any]:
        """Analisa uma amostra de resultado."""
        try:
            parsed = json.loads(result_sample)
            
            # Extrai campo 'result' se existir
            if isinstance(parsed, dict) and 'result' in parsed:
                return parsed['result']
            
            return parsed
            
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def infer_schema_from_samples(self, samples: List[str]) -> Optional[StructType]:
        """
        Infere schema a partir de múltiplas amostras.
        
        Args:
            samples: Lista de strings JSON com resultados
            
        Returns:
            StructType inferido ou None se falhar
        """
        if not PYSPARK_AVAILABLE:
            return None
        
        if not samples:
            return None
        
        # Analisa amostras limitadas
        analyzed_samples = []
        for sample in samples[:self.sample_size]:
            analyzed = self._analyze_sample(sample)
            if analyzed:
                analyzed_samples.append(analyzed)
        
        if not analyzed_samples:
            return None
        
        # Coleta todos os campos encontrados
        all_fields = {}
        
        for sample in analyzed_samples:
            if isinstance(sample, dict):
                for field_name, field_value in sample.items():
                    if field_name not in all_fields:
                        all_fields[field_name] = []
                    all_fields[field_name].append(field_value)
        
        # Cria campos do schema
        schema_fields = []
        for field_name, values in all_fields.items():
            # Infere tipo baseado na maioria dos valores
            field_type = self._infer_field_type(values)
            schema_fields.append(StructField(field_name, field_type, True))
        
        return StructType(schema_fields) if schema_fields else None
    
    def _infer_field_type(self, values: List[Any]):
        """Infere tipo de um campo baseado em múltiplos valores."""
        if not values:
            return StringType()
        
        # Remove valores None
        non_null_values = [v for v in values if v is not None]
        
        if not non_null_values:
            return StringType()
        
        # Se todos são do mesmo tipo Python, usa esse tipo
        types = [type(v) for v in non_null_values]
        unique_types = set(types)
        
        if len(unique_types) == 1:
            return self._analyze_value(non_null_values[0])
        
        # Tipos mistos - usa estratégia conservativa
        if self.strategy == InferenceStrategy.CONSERVATIVE:
            return StringType()
        
        # Estratégia agressiva - tenta o tipo mais comum
        from collections import Counter
        type_counts = Counter(types)
        most_common_type = type_counts.most_common(1)[0][0]
        
        # Se a maioria (>60%) é do mesmo tipo, usa esse
        if type_counts[most_common_type] / len(non_null_values) > 0.6:
            return self._python_type_to_spark_type(most_common_type)
        
        return StringType()
    
    def create_expanded_dataframe(self, df, result_column: str = "wd_result", 
                                 schema: Optional[StructType] = None):
        """
        Cria DataFrame expandido com colunas automáticas.
        
        Args:
            df: DataFrame com coluna de resultado
            result_column: Nome da coluna com JSON
            schema: Schema específico (opcional)
            
        Returns:
            DataFrame expandido
        """
        if not PYSPARK_AVAILABLE:
            raise ImportError("PySpark não disponível para schema inference")
        
        # Se schema não fornecido, infere automaticamente
        if schema is None:
            # Coleta amostras
            samples = df.select(result_column).limit(self.sample_size).collect()
            sample_values = [row[result_column] for row in samples if row[result_column]]
            
            schema = self.infer_schema_from_samples(sample_values)
            
            if schema is None:
                # Fallback: mantém como string
                return df
        
        # Cria estrutura completa para parsing
        full_schema = StructType([
            StructField("performance", StringType(), True),
            StructField("result", schema, True)
        ])
        
        # Aplica parsing
        expanded_df = df.withColumn(
            "_parsed_result",
            from_json(col(result_column), full_schema)
        )
        
        # Extrai campos individuais
        for field in schema.fields:
            expanded_df = expanded_df.withColumn(
                field.name,
                col(f"_parsed_result.result.{field.name}")
            )
        
        return expanded_df.drop("_parsed_result")
    
    def get_stats(self) -> SchemaStats:
        """Retorna estatísticas da inferência."""
        return SchemaStats(
            samples_analyzed=len(self._field_counter),
            fields_detected=len(set().union(*self._field_counter.values()) if self._field_counter else set()),
            strategy_used=self.strategy.value,
            confidence_score=0.9  # Simplificado
        )


class AutoSchemaHelper:
    """Helper para integração automática de schema inference."""
    
    @staticmethod
    def enhance_dataframe_with_schema(df, 
                                    result_column: str = "wd_result",
                                    strategy: InferenceStrategy = InferenceStrategy.CONSERVATIVE,
                                    auto_prefix: bool = True):
        """
        Aplica schema inference automática ao DataFrame.
        
        Args:
            df: DataFrame com resultados de decisão
            result_column: Nome da coluna com JSON
            strategy: Estratégia de inferência
            auto_prefix: Se deve prefixar campos com "decision_"
            
        Returns:
            DataFrame expandido com colunas automáticas
        """
        engine = SchemaInferenceEngine(strategy=strategy)
        
        expanded_df = engine.create_expanded_dataframe(df, result_column)
        
        # Adiciona prefixo se solicitado
        if auto_prefix and expanded_df.columns != df.columns:
            # Identifica novas colunas
            original_cols = set(df.columns)
            new_cols = [c for c in expanded_df.columns if c not in original_cols]
            
            # Renomeia novas colunas com prefixo
            for col_name in new_cols:
                expanded_df = expanded_df.withColumnRenamed(
                    col_name, f"decision_{col_name}"
                )
        
        return expanded_df
    
    @staticmethod
    def print_schema_info(df, result_column: str = "wd_result"):
        """Imprime informações sobre schema inferido."""
        engine = SchemaInferenceEngine()
        
        # Coleta amostras
        samples = df.select(result_column).limit(5).collect()
        sample_values = [row[result_column] for row in samples if row[result_column]]
        
        if not sample_values:
            print("⚠️ Nenhuma amostra encontrada")
            return
        
        schema = engine.infer_schema_from_samples(sample_values)
        
        if schema:
            print("📊 Schema Inferido:")
            for field in schema.fields:
                print(f"   {field.name}: {field.dataType}")
        else:
            print("⚠️ Não foi possível inferir schema")
        
        # Mostra amostra do JSON
        print("\n📋 Amostra do resultado:")
        try:
            sample_json = json.loads(sample_values[0])
            if 'result' in sample_json:
                print(json.dumps(sample_json['result'], indent=2)[:200])
        except:
            pass


# Função de conveniência para uso direto
def auto_expand_decision_results(df, 
                               result_column: str = "wd_result",
                               strategy: str = "conservative",
                               prefix: bool = True):
    """
    Função de conveniência para expansão automática de resultados.
    
    Args:
        df: DataFrame com resultados
        result_column: Coluna com JSON
        strategy: "conservative", "aggressive", ou "flat_only"  
        prefix: Se deve prefixar colunas
        
    Returns:
        DataFrame expandido
    """
    strategy_map = {
        "conservative": InferenceStrategy.CONSERVATIVE,
        "aggressive": InferenceStrategy.AGGRESSIVE,
        "flat_only": InferenceStrategy.FLAT_ONLY
    }
    
    selected_strategy = strategy_map.get(strategy, InferenceStrategy.CONSERVATIVE)
    
    return AutoSchemaHelper.enhance_dataframe_with_schema(
        df, result_column, selected_strategy, prefix
    )