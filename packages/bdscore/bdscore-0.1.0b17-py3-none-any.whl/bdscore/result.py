import json
import time
from typing import Dict, Any, Optional, Union
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class BDSData:
    """
    Classe para encapsular e manipular dados de resposta das APIs.
    """
    
    def __init__(self, raw_data: Any):
        """
        Inicializa uma instância de BDSData.
        
        Args:
            raw_data: Dados brutos da resposta da API
        """
        self.raw_data = raw_data
    
    def to_df(self, normalize: bool = True) -> 'pd.DataFrame':
        """
        Converte os dados para um DataFrame pandas.
        
        Args:
            normalize: Se True, normaliza dados JSON aninhados em colunas planas
            
        Returns:
            pandas.DataFrame: DataFrame com os dados da resposta
            
        Raises:
            ImportError: Se pandas não estiver instalado
            ValueError: Se os dados não puderem ser convertidos para DataFrame
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas não está instalado. Instale com: pip install pandas")
        
        if self.raw_data is None:
            return pd.DataFrame()
        
        try:
            # Se o raw_data é uma string JSON, tenta fazer parse
            if isinstance(self.raw_data, str):
                data = json.loads(self.raw_data)
            else:
                data = self.raw_data
            
            # Se é uma lista, cria DataFrame diretamente
            if isinstance(data, list):
                if normalize and len(data) > 0 and isinstance(data[0], dict):
                    return pd.json_normalize(data)
                return pd.DataFrame(data)
            
            # Se é um dict, verifica se tem uma chave de dados comum
            if isinstance(data, dict):
                # Procura por chaves comuns de dados
                data_keys = ['data', 'results', 'items', 'records', 'values']
                for key in data_keys:
                    if key in data and isinstance(data[key], list):
                        if normalize and len(data[key]) > 0 and isinstance(data[key][0], dict):
                            return pd.json_normalize(data[key])
                        return pd.DataFrame(data[key])
                
                # Se não encontrou chave de dados, normaliza o dict inteiro
                if normalize:
                    return pd.json_normalize([data])
                else:
                    return pd.DataFrame([data])
            
            # Para outros tipos, tenta criar DataFrame
            return pd.DataFrame([data])
            
        except Exception as e:
            raise ValueError(f"Não foi possível converter os dados para DataFrame: {str(e)}")
    
    def to_dict(self) -> Any:
        """
        Retorna os dados brutos como dicionário ou tipo original.
        
        Returns:
            Dados em seu formato original
        """
        return self.raw_data
    
    def to_json(self, indent: int = 2) -> str:
        """
        Converte os dados para JSON string.
        
        Args:
            indent: Indentação para formatação
            
        Returns:
            String JSON formatada
        """
        return json.dumps(self.raw_data, indent=indent, default=str, ensure_ascii=False)
    
    def __str__(self) -> str:
        """Representação string dos dados como dicionário."""
        if self.raw_data is None:
            return "None"
        
        # Se já é um dict ou list, retorna como string JSON formatada
        if isinstance(self.raw_data, (dict, list)):
            return json.dumps(self.raw_data, indent=2, ensure_ascii=False, default=str)
        
        # Para outros tipos, converte para string
        return str(self.raw_data)
    
    def __repr__(self) -> str:
        """Representação detalhada dos dados."""
        return f"BDSData(type={type(self.raw_data).__name__}, data={self.raw_data})"


class BDSResult:
    """
    Classe para encapsular resultados de chamadas de API do BDSCore.
    
    Attributes:
        api_url (str): URL completa da API chamada
        call_duration (float): Duração da chamada em segundos
        correlation_id (str): ID de correlação da requisição
        data (BDSData): Objeto contendo os dados da resposta
        headers (Dict[str, str]): Headers da resposta HTTP
        idempotency_code (str): Código de idempotência da requisição
        status_code (int): Código de status HTTP da resposta
        request_timestamp (float): Timestamp da requisição
        response_timestamp (float): Timestamp da resposta
    """
    
    def __init__(
        self,
        api_url: str,
        body: Any,
        headers: Dict[str, str],
        status_code: int,
        call_duration: float,
        correlation_id: Optional[str] = None,
        idempotency_code: Optional[str] = None,
        request_timestamp: Optional[float] = None,
        response_timestamp: Optional[float] = None
    ):
        """
        Inicializa uma instância de BDSResult.
        
        Args:
            api_url: URL completa da API chamada
            body: Corpo da resposta da API
            headers: Headers da resposta HTTP
            status_code: Código de status HTTP da resposta
            call_duration: Duração da chamada em segundos
            correlation_id: ID de correlação da requisição
            idempotency_code: Código de idempotência da requisição
            request_timestamp: Timestamp da requisição
            response_timestamp: Timestamp da resposta
        """
        self.api_url = api_url
        self.data = BDSData(body)
        self.headers = headers
        self.status_code = status_code
        self.call_duration = call_duration
        self.correlation_id = correlation_id or headers.get('X-Correlation-ID')
        self.idempotency_code = idempotency_code or headers.get('X-Idempotency-Key')
        self.request_timestamp = request_timestamp or (time.time() - call_duration)
        self.response_timestamp = response_timestamp or time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o resultado para um dicionário.
        
        Returns:
            Dict contendo todos os atributos do resultado
        """
        return {
            'api_url': self.api_url,
            'call_duration': self.call_duration,
            'correlation_id': self.correlation_id,
            'data': self.data.to_dict(),
            'headers': dict(self.headers),
            'idempotency_code': self.idempotency_code,
            'status_code': self.status_code,
            'request_timestamp': self.request_timestamp,
            'response_timestamp': self.response_timestamp
        }
    
    def to_json(self, indent: int = 2) -> str:
        """
        Converte o resultado para JSON string.
        
        Args:
            indent: Indentação para formatação
            
        Returns:
            String JSON formatada
        """
        return json.dumps(self.to_dict(), indent=indent, default=str, ensure_ascii=False)
    
    def is_success(self) -> bool:
        """
        Verifica se a chamada foi bem-sucedida.
        
        Returns:
            True se o status code indica sucesso (200-299)
        """
        return 200 <= self.status_code < 300
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Retorna apenas os metadados da resposta (sem os dados).
        
        Returns:
            Dict com metadados da resposta
        """
        metadata = self.to_dict()
        metadata.pop('data', None)
        return metadata
    
    def __str__(self) -> str:
        """Representação string do resultado."""
        return f"BDSResult(url='{self.api_url}', status={self.status_code}, duration={self.call_duration:.3f}s)"
    
    def __repr__(self) -> str:
        """Representação detalhada do resultado."""
        return (f"BDSResult(api_url='{self.api_url}', status_code={self.status_code}, "
                f"call_duration={self.call_duration:.3f}s, correlation_id='{self.correlation_id}')")
