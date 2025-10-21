from bdscore.services.common import Common
from .services.datapack import DataPack
from .services.datamanagement import DataManagement
from .services.utils import Utils
from .result import BDSResult, BDSData
from .enums import ResponseFormat, DynamicDate, CorporateActionType, BooleanString, Format, Date, Corporate, Boolean

import requests
import urllib3
import time
import uuid

class BDSCore:

    """
    Classe base para comunicação com as APIs da BDS DataSolution.
    Ao instanciar, é necessário fornecer a chave de autenticação.
    """
    def __init__(
        self,
        api_key: str,
        datapack_url: str = "https://temp-api.bdsdatapack.com.br",
        common_url: str = "https://temp-api.bdsdatapack.com.br/common",
        guard_url: str = "https://auth.bdsdatapack.com.br/api/v1",
        datamanagement_url: str = "https://api.bdsdatapack.com.br/smart-temp/data-management/v1",
        verify: str | bool = False
    ):
        
        if not api_key or not isinstance(api_key, str):
            raise ValueError("É necessário fornecer uma chave de autenticação válida.")
        self.api_key = api_key
        self.datapack_url = datapack_url
        self.common_url = common_url
        self.guard_url = guard_url
        self.datamanagement_url = datamanagement_url
        self.verify = verify

        self._session = requests.Session()
        self._session.headers.update({"BDSKey": self.api_key})

        # Remove warnings de SSL se verify=False
        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.datapack = DataPack(self)
        self.datamanagement = DataManagement(self)
        self.common = Common(self)
        self.utils = Utils(self)

        # Realiza sincronização inicial (ignora o resultado)
        sync_result = self.__request(
            method="get",
            url=f"{self.guard_url}/user/sync"
        )
        
        # Verifica se a sincronização foi bem-sucedida
        if not sync_result.is_success():
            raise ValueError(f"Falha na sincronização inicial: {sync_result.status_code}")

  
    def __request(self, method, url, **kwargs):
        """
        Handler global para requisições HTTP, com tratamento de erro e correlation id.
        Retorna uma instância de BDSResult com metadados da requisição.
        """
        request_timestamp = time.time()
        idempotency_code = str(uuid.uuid4())
        
        # Adiciona headers de correlação e idempotência se não estiverem presentes
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        
        if 'X-Idempotency-Key' not in kwargs['headers']:
            kwargs['headers']['X-Idempotency-Key'] = idempotency_code
        
        try:
            response = self._session.request(method, url, verify=self.verify, **kwargs)
            response_timestamp = time.time()
            call_duration = response_timestamp - request_timestamp
            
            if response.status_code == 401:
                correlation_id = response.headers.get("bdsh-correlation-id", "N/A")
                raise ValueError(f"Chave de autenticação incorreta ou não autorizada (HTTP 401). Verifique sua BDSKey. CorrelationId: {correlation_id}")
            
            response.raise_for_status()
            
            # Tenta retornar JSON, senão retorna o texto
            try:
                body = response.json()
            except Exception:
                body = response.text
            
            return BDSResult(
                api_url=url,
                body=body,
                headers=dict(response.headers),
                status_code=response.status_code,
                call_duration=call_duration,
                correlation_id=response.headers.get("bdsh-correlation-id"),
                idempotency_code=idempotency_code,
                request_timestamp=request_timestamp,
                response_timestamp=response_timestamp
            )
            
        except requests.RequestException as e:
            response_timestamp = time.time()
            call_duration = response_timestamp - request_timestamp
            correlation_id = None
            body = None
            status_code = 0
            headers = {}
            
            if hasattr(e, 'response') and e.response is not None:
                correlation_id = e.response.headers.get("bdsh-correlation-id", "N/A")
                status_code = e.response.status_code
                headers = dict(e.response.headers)
                try:
                    body = e.response.text
                except Exception:
                    body = None
                    
                # Para erros HTTP, retorna BDSResult com erro
                return BDSResult(
                    api_url=url,
                    body=body,
                    headers=headers,
                    status_code=status_code,
                    call_duration=call_duration,
                    correlation_id=correlation_id,
                    idempotency_code=idempotency_code,
                    request_timestamp=request_timestamp,
                    response_timestamp=response_timestamp
                )
            else:
                # Para erros de rede, lança exceção
                msg = f"Erro na requisição: {e}"
                raise RuntimeError(msg) from e

    def __make_request(self, base_url, endpoint, **kwargs):
        """
        Método genérico unificado para fazer requisições GET com parâmetros dinâmicos.
        
        Args:
            base_url (str): URL base da API (datapack_url, common_url, etc.)
            endpoint (str): O endpoint específico da API
            **kwargs: Parâmetros dinâmicos que variam por endpoint
            
        Returns:
            BDSResult: Instância de BDSResult com a resposta da requisição
        """
        # Constrói a URL completa, garantindo que não haja barras duplicadas
        base_url = base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        url = f"{base_url}/{endpoint}"
        
        # Remove parâmetros None para enviar apenas os que foram fornecidos
        params = {key: value for key, value in kwargs.items() if value is not None}
        
        return self.__request(
            method="get",
            url=url,
            params=params
        )
