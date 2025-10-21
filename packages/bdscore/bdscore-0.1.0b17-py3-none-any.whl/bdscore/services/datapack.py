from ..enums import ResponseFormat, DynamicDate, CorporateActionType, BooleanString
from typing import Union, Optional, Any, Dict

class DataPack:

    def __init__(self, core):
        self._core = core

    # ---------------------------------------------------------------------
    # Helpers internos
    # ---------------------------------------------------------------------
    def _normalize_value(self, value: Any):
        """Converte enums (ResponseFormat, DynamicDate, BooleanString, CorporateActionType)
        para seus valores primitivos. Mantém outros tipos inalterados."""
        if isinstance(value, (ResponseFormat, DynamicDate, BooleanString, CorporateActionType)):
            return value.value
        return value

    def _prepare_params(self, **kwargs) -> Dict[str, Any]:
        """Remove chaves cujo valor é None e normaliza enums/datas dinâmicas."""
        clean: Dict[str, Any] = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            clean[k] = self._normalize_value(v)
        return clean

    def _request_endpoint(self, endpoint: str, **kwargs):
        """Encapsula chamada ao método genérico do core para endpoints DataPack.

        Args:
            endpoint (str): Nome do endpoint (ex: 'getFX').
            **kwargs: Parâmetros específicos do endpoint.
        """
        params = self._prepare_params(**kwargs)
        return self._core._BDSCore__make_request(
            self._core.datapack_url,
            endpoint,
            **params
        )

    # ====================================
    # MÉTODOS DE MERCADO FINANCEIRO
    # ====================================

    def getFX(self, Symbols, InitialDate, FinalDate: Optional[Union[str, DynamicDate]] = None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format: Optional[ResponseFormat] = None, IgnNull: Optional[BooleanString] = None, isActive=None):
        """
        Obtém dados de câmbio e moedas estrangeiras.
        
        Args:
            Symbols (str): Símbolos das moedas para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str | DynamicDate): Data final da consulta (opcional)
                                         Aceita datas dinâmicas: DynamicDate.YESTERDAY, DynamicDate.LAST_BUSINESS_DAY, etc.
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (ResponseFormat): Formato de retorno (default: ResponseFormat.JSON)
                                   Opções: ResponseFormat.JSON, ResponseFormat.XML, ResponseFormat.CSV, ResponseFormat.EXCEL
            IgnNull (BooleanString): Se deve retornar valores nulos (default: BooleanString.FALSE)
                                   Opções: BooleanString.TRUE, BooleanString.FALSE
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de câmbio para os símbolos especificados
        """
        return self._request_endpoint(
            "getFX",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getEquitiesB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de ações negociadas na B3 (Bolsa de Valores do Brasil).
        
        Args:
            Symbols (str): Símbolos das ações para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de ações da B3 para os símbolos especificados
        """
        return self._request_endpoint(
            "getEquitiesB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getBrazilianTreasury(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados cadastrais e de valores de títulos públicos brasileiros (LFT, LTN, NTN-B, NTN-C, NTN-F).
        
        Args:
            Symbols (str): Símbolos dos títulos públicos para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de títulos do Tesouro Nacional
        """
        return self._request_endpoint(
            "getBrazilianTreasury",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getCommodities(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de commodities negociadas no mercado internacional.
        
        Args:
            Symbols (str): Símbolos das commodities para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de commodities para os símbolos especificados
        """
        return self._request_endpoint(
            "getCommodities",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getIndex(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de índices financeiros internacionais.
        
        Args:
            Symbols (str): Símbolos dos índices para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de índices financeiros
        """
        return self._request_endpoint(
            "getIndex",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getIndexB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de índices negociados na B3 (ex: Ibovespa, IBrX-100, etc.).
        
        Args:
            Symbols (str): Símbolos dos índices B3 para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de índices da B3
        """
        return self._request_endpoint(
            "getIndexB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getIndexPortfolioB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de portfólio dos índices negociados na B3.
        
        Args:
            Symbols (str): Símbolos dos índices para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de portfólio dos índices B3
        """
        return self._request_endpoint(
            "getIndexPortfolioB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    # ====================================
    # MÉTODOS DE DERIVATIVOS E FUTUROS
    # ====================================

    def getFuturesB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de contratos futuros negociados na B3.
        
        Args:
            Symbols (str): Símbolos dos futuros para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de contratos futuros da B3
        """
        return self._request_endpoint(
            "getFuturesB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getFuturesCME(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de contratos futuros negociados na CME (Chicago Mercantile Exchange).
        
        Args:
            Symbols (str): Símbolos dos futuros CME para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de contratos futuros da CME
        """
        return self._request_endpoint(
            "getFuturesCME",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getCMEAgricFutures(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de futuros agrícolas negociados na CME.
        
        Args:
            Symbols (str): Símbolos dos futuros agrícolas para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de futuros agrícolas da CME
        """
        return self._request_endpoint(
            "getCMEAgricFutures",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getCMEFuturesCommodities(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de futuros de commodities negociados na CME.
        
        Args:
            Symbols (str): Símbolos dos futuros de commodities para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de futuros de commodities da CME
        """
        return self._request_endpoint(
            "getCMEFuturesCommodities",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getFuturesOptionsB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de opções sobre futuros negociadas na B3.
        
        Args:
            Symbols (str): Símbolos das opções sobre futuros para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de opções sobre futuros da B3
        """
        return self._request_endpoint(
            "getFuturesOptionsB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    def getOptionsOnEquitiesB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
        """
        Obtém dados de opções sobre ações negociadas na B3.
        
        Args:
            Symbols (str): Símbolos das opções sobre ações para consulta (obrigatório)
            InitialDate (str): Data inicial da consulta (obrigatório)
            FinalDate (str): Data final da consulta (opcional)
            Fields (str): Campos específicos a retornar
            Interval (str): Intervalo dos dados
            IgnDefault (str): Ignorar valores padrão
            Lang (str): Idioma da resposta
            Page (int): Número da página
            Rows (int): Quantidade de linhas por página
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos (default: "False")
            isActive (str): Filtrar apenas símbolos ativos
            
        Returns:
            dict: Dados de opções sobre ações da B3
        """
        return self._request_endpoint(
            "getOptionsOnEquitiesB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            Interval=Interval,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull,
            isActive=isActive
        )

    # ====================================
    # MÉTODOS DE EVENTOS CORPORATIVOS 
    # ====================================

    def getAdjQuoteHistory(self, Symbols, InitialDate, FinalDate: Optional[Union[str, DynamicDate]] = None, NominalValue: Optional[bool] = None, MissingValues: Optional[bool] = None, Page: Optional[int] = None, Rows: Optional[int] = None, Format: Optional[ResponseFormat] = None):
        """
        Retorna o histórico completo de cotações ajustadas aos proventos de um ativo específico.
        
        Este endpoint fornece preços de abertura, fechamento, máximo, mínimo, volume negociado e 
        fatores de ajuste aplicados devido a eventos corporativos como dividendos, splits, bonificações, etc.
        
        Args:
            Symbols (str): Código de identificação do ativo na bolsa de valores (ticker symbol) (obrigatório)
                          Exemplos: PETR4 (Petrobras PN), VALE3 (Vale ON), ITUB4 (Itaú Unibanco PN)
            InitialDate (str): Data de início do período para consulta no formato YYYY-MM-DD (ISO 8601) (obrigatório)
                              Aceita datas dinâmicas: DynamicDate.YESTERDAY, DynamicDate.LAST_BUSINESS_DAY, DynamicDate.FIRST_BUSINESS_DAY_PREV_MONTH
            FinalDate (str | DynamicDate): Data de fim do período para consulta no formato YYYY-MM-DD (ISO 8601) (opcional)
                           Se não informado: retorna dados apenas da data inicial
            NominalValue (bool): Define se os valores nominais (não ajustados) devem ser incluídos na resposta (opcional)
                               True: retorna valores ajustados + nominais para comparação
                               False: apenas valores ajustados (padrão)
            MissingValues (bool): Define se deve preencher dados ausentes com valores específicos (opcional)
                                Útil para análises que requerem continuidade temporal (padrão: False)
            Page (int): Número da página para paginação dos resultados (opcional)
                       Inicia em 1, se não informado: retorna a primeira página
            Rows (int): Quantidade máxima de registros por página (opcional)
                       Máximo geral: 1.000 registros, Formato Excel: automaticamente ajustado para 10.000 registros
            Format (ResponseFormat): Formato de serialização da resposta da API (opcional)
                         Opções: ResponseFormat.JSON (padrão), ResponseFormat.XML, ResponseFormat.CSV, ResponseFormat.EXCEL
            
        Returns:
            BDSResult: Histórico de cotações ajustadas com preços corrigidos por proventos e eventos corporativos
                      Inclui preços ajustados, volumes, quantidades e fatores de correção aplicados
        """
        return self._request_endpoint(
            "getAdjQuoteHistory",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            NominalValue=NominalValue,
            MissingValues=MissingValues,
            Page=Page,
            Rows=Rows,
            Format=Format
        )

    def getCorporateActions(self, Symbols, InitialDate, FinalDate: Optional[Union[str, DynamicDate]] = None, EvtActnTpCd: Optional[CorporateActionType] = None, Page: Optional[int] = None, Rows: Optional[int] = None, Format: Optional[ResponseFormat] = None):
        """
        Retorna informações detalhadas sobre eventos corporativos de ativos listados na bolsa.
        
        Tipos de eventos corporativos incluem distribuição de proventos (dividendos, JCP, bonificações),
        alterações no capital (splits, grupamentos, incorporações), direitos de subscrição e outros eventos
        que afetam o preço e quantidade de ações.
        
        Args:
            Symbols (str): Código de identificação do ativo na bolsa de valores (ticker symbol) (obrigatório)
                          Exemplos: PETR4 (Petrobras PN), VALE3 (Vale ON), ITUB4 (Itaú Unibanco PN)
            InitialDate (str): Data de início do período para consulta no formato YYYY-MM-DD (ISO 8601) (obrigatório)
                              Aceita datas dinâmicas: DynamicDate.YESTERDAY, DynamicDate.LAST_BUSINESS_DAY, DynamicDate.FIRST_BUSINESS_DAY_PREV_MONTH
            FinalDate (str | DynamicDate): Data de fim do período para consulta no formato YYYY-MM-DD (ISO 8601) (opcional)
                           Se não informado: busca eventos apenas na data inicial
            EvtActnTpCd (CorporateActionType): Filtra por tipo específico de evento corporativo (opcional)
                              Códigos principais:
                              - CorporateActionType.DIVIDEND: Dividendo
                              - CorporateActionType.INTEREST_ON_EQUITY: Juros sobre Capital Próprio
                              - CorporateActionType.STOCK_SPLIT: Desdobramento (Split)
                              - CorporateActionType.STOCK_GROUPING: Grupamento
                              - CorporateActionType.INCORPORATION: Incorporação
                              - CorporateActionType.MERGER: Fusão
                              E muitos outros... (veja CorporateActionType para lista completa)
            Page (int): Número da página para paginação dos resultados (opcional)
                       Inicia em 1, se não informado: retorna a primeira página
            Rows (int): Quantidade máxima de registros por página (opcional)
                       Máximo geral: 1.000 registros, Formato Excel: automaticamente ajustado para 10.000 registros
            Format (ResponseFormat): Formato de serialização da resposta da API (opcional)
                         Opções: ResponseFormat.JSON (padrão), ResponseFormat.XML, ResponseFormat.CSV, ResponseFormat.EXCEL
            
        Returns:
            BDSResult: Lista de eventos corporativos com detalhes completos incluindo datas, valores, 
                      tipos de evento e informações societárias
        """
        return self._request_endpoint(
            "getCorporateActions",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            EvtActnTpCd=EvtActnTpCd,
            Page=Page,
            Rows=Rows,
            Format=Format
        )


    def getCurvesB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None):
        """Obtém dados de curvas (Curves B3)."""
        return self._request_endpoint(
            "getCurvesB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull
        )

    def getEconomicIndicatorsB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None):
        """Obtém indicadores econômicos B3."""
        return self._request_endpoint(
            "getEconomicIndicatorsB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull
        )

    def getScheduleCriB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None):
        """Obtém agenda de CRI da B3."""
        return self._request_endpoint(
            "getScheduleCriB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull
        )

    def getScheduleCraB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None):
        """Obtém agenda de CRA da B3."""
        return self._request_endpoint(
            "getScheduleCraB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull
        )

    def getDebenturesB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None):
        """Obtém dados de debêntures da B3."""
        return self._request_endpoint(
            "getDebenturesB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull
        )

    def getCorpActB3(self, Symbols, RefDate, Fields=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None):
        """Obtém eventos corporativos B3 (forma alternativa corporativa)."""
        return self._request_endpoint(
            "getCorpActB3",
            Symbols=Symbols,
            RefDate=RefDate,
            Fields=Fields,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull
        )

    def getVolSB3(self, Symbols, InitialDate, FinalDate=None, Fields=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None):
        """Obtém dados de volatilidade (VolS) da B3."""
        return self._request_endpoint(
            "getVolSB3",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull
        )

    def getRegulatoryListed(self, Symbols, InitialDate, FinalDate=None, Fields=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None):
        """Obtém dados regulatórios de ativos listados."""
        return self._request_endpoint(
            "getRegulatoryListed",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull
        )

    def getRegulatoryOTC(self, Symbols, InitialDate, FinalDate=None, Fields=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None):
        """Obtém dados regulatórios de operações OTC."""
        return self._request_endpoint(
            "getRegulatoryOTC",
            Symbols=Symbols,
            InitialDate=InitialDate,
            FinalDate=FinalDate,
            Fields=Fields,
            IgnDefault=IgnDefault,
            Lang=Lang,
            Page=Page,
            Rows=Rows,
            Format=Format,
            IgnNull=IgnNull
        )

    def getFundsCVM175(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
            """
            Obtém dados de fundos CVM (atualizados pela resolução Nº 175 da CVM).

            Args:
                Symbols (str): Símbolos dos fundos para consulta (obrigatório)
                InitialDate (str): Data inicial da consulta (obrigatório)
                FinalDate (str): Data final da consulta (opcional)
                Fields (str): Campos específicos a retornar
                Interval (str): Intervalo dos dados
                IgnDefault (str): Ignorar valores padrão
                Lang (str): Idioma da resposta
                Page (int): Número da página
                Rows (int): Quantidade de linhas por página
                Format (str): Formato de retorno (default: "Json")
                IgnNull (str): Se deve retornar valores nulos (default: "False")
                isActive (str): Filtrar apenas símbolos ativos
                
            Returns:
                dict: Dados de ações da B3 para os símbolos especificados
            """
            return self._request_endpoint(
                "getFundsCVM175",
                Symbols=Symbols,
                InitialDate=InitialDate,
                FinalDate=FinalDate,
                Fields=Fields,
                Interval=Interval,
                IgnDefault=IgnDefault,
                Lang=Lang,
                Page=Page,
                Rows=Rows,
                Format=Format,
                IgnNull=IgnNull,
                isActive=isActive
            )
    
    def getFundsAnbima175(self, Symbols, InitialDate, FinalDate=None, Fields=None, Interval=None, IgnDefault=None, Lang=None, Page=None, Rows=None, Format=None, IgnNull=None, isActive=None):
            """
            Obtém dados de fundos Anbima (atualizados pela resolução Nº 175 da CVM).

            Args:
                Symbols (str): Símbolos dos fundos para consulta (obrigatório)
                InitialDate (str): Data inicial da consulta (obrigatório)
                FinalDate (str): Data final da consulta (opcional)
                Fields (str): Campos específicos a retornar
                Interval (str): Intervalo dos dados
                IgnDefault (str): Ignorar valores padrão
                Lang (str): Idioma da resposta
                Page (int): Número da página
                Rows (int): Quantidade de linhas por página
                Format (str): Formato de retorno (default: "Json")
                IgnNull (str): Se deve retornar valores nulos (default: "False")
                isActive (str): Filtrar apenas símbolos ativos
                
            Returns:
                dict: Dados de ações da B3 para os símbolos especificados
            """
            return self._request_endpoint(
                "getFundsAnbima175",
                Symbols=Symbols,
                InitialDate=InitialDate,
                FinalDate=FinalDate,
                Fields=Fields,
                Interval=Interval,
                IgnDefault=IgnDefault,
                Lang=Lang,
                Page=Page,
                Rows=Rows,
                Format=Format,
                IgnNull=IgnNull,
                isActive=isActive
            )