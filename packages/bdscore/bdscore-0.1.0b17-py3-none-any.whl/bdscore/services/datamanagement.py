

class DataManagement:

    def __init__(self, core):
        self._core = core

    def getFamilies(
        self,
        FamilyId=None,
        Status=None,
        FilterId=None,
        SourceId=None,
        AttributeId=None,
        NotebookId=None,
        CadasterId=None,
        TableId=None,
        Lang=None,
        Page=None,
        Rows=None
    ):
        """
        Método para consultar famílias de dados

        @param FamilyId: ID da família de dados
        @param Status: Status da família de dados
        @param FilterId: ID do filtro
        @param SourceId: ID da fonte de dados
        @param AttributeId: ID do atributo
        @param NotebookId: ID do caderno
        @param CadasterId: ID do cadastro
        @param TableId: ID da tabela
        @param Lang: Idioma da resposta
        @param Page: Número da página
        @param Rows: Número de linhas por página
        @return: Resposta da API DataManagement
        """
        url = f"{self._core.datamanagement_url}/Family"
        params = {}
        if FamilyId is not None: params["FamilyId"] = FamilyId
        if Status is not None: params["Status"] = Status
        if FilterId is not None: params["FilterId"] = FilterId
        if SourceId is not None: params["SourceId"] = SourceId
        if AttributeId is not None: params["AttributeId"] = AttributeId
        if NotebookId is not None: params["NotebookId"] = NotebookId
        if CadasterId is not None: params["CadasterId"] = CadasterId
        if TableId is not None: params["TableId"] = TableId
        if Lang is not None: params["Lang"] = Lang
        if Page is not None: params["Page"] = Page
        if Rows is not None: params["Rows"] = Rows

        return self._core._BDSCore__request(
            method="get",
            url=url,
            params=params
        )

    def getValues(
        self,
        FamilyId,
        InitialDate,
        SeriesId=None,
        Interval=None,
        AttributesId=None,
        CadastersId=None,
        FinalDate=None,
        IsActive=None,
        Lang=None,
        Page=None,
        Rows=None
    ):
        """
        Consulta valores de séries temporais de acordo com os parâmetros da API DataManagement.
        Parâmetros obrigatórios: FamilyId, InitialDate
        """
        if not FamilyId or not InitialDate:
            raise ValueError("Os parâmetros 'FamilyId' e 'InitialDate' são obrigatórios.")

        url = f"{self._core.datamanagement_url}/Values"
        params = {
            "FamilyId": FamilyId,
            "InitialDate": InitialDate,
        }
        if SeriesId is not None: params["SeriesId"] = SeriesId
        if Interval is not None: params["Interval"] = Interval
        if AttributesId is not None: params["AttributesId"] = AttributesId
        if CadastersId is not None: params["CadastersId"] = CadastersId
        if FinalDate is not None: params["FinalDate"] = FinalDate
        if Lang is not None: params["Lang"] = Lang
        if Page is not None: params["Page"] = Page
        if Rows is not None: params["Rows"] = Rows

        return self._core._BDSCore__request(
            method="get",
            url=url,
            params=params
        )

    def getCurves(
        self,
        ReferenceDate,
        Name=None,
        Fields=None,
        Format=None,
        Lang=None,
        Page=None,
        Rows=None
    ):
        """
        Consulta curvas de juros e rendimentos calculadas.
        
        Args:
            ReferenceDate (str): Data de referência para a consulta (obrigatório)
                                Ex: "2024-01-01", "D-1" (dia anterior), "last" (último disponível)
            Name (str): Nome da curva específica (opcional)
                       Ex: "SOFR_USD", "DI_BRL", "TREASURIES_USD"
            Fields (str): Campos específicos a retornar (opcional)
                         Ex: ":all" para todos os campos, ou campos específicos separados por vírgula
            Format (str): Formato de retorno (opcional)
                         Ex: "json", "xml", "csv"
            Lang (str): Idioma da resposta (opcional)
            Page (int): Número da página para paginação (opcional)
            Rows (int): Número de linhas por página (opcional)
            
        Returns:
            BDSResult: Objeto com os dados das curvas de juros
            
        Example:
            # Buscar curva SOFR_USD do dia anterior
            curves = bds.datamanagement.getCurves(
                ReferenceDate="D-1",
                Name="SOFR_USD",
                Fields=":all",
                Format="json"
            )
            print(curves.data.to_df())
        """
        if not ReferenceDate:
            raise ValueError("O parâmetro 'ReferenceDate' é obrigatório.")

        url = f"{self._core.datamanagement_url}/Calculate/Curves"
        params = {
            "ReferenceDate": ReferenceDate,
        }
        if Name is not None: params["Name"] = Name
        if Fields is not None: params["Fields"] = Fields
        if Format is not None: params["Format"] = Format
        if Lang is not None: params["Lang"] = Lang
        if Page is not None: params["Page"] = Page
        if Rows is not None: params["Rows"] = Rows

        return self._core._BDSCore__request(
            method="get",
            url=url,
            params=params
        )
    
    def getCadasterAttributes(
        self,
        Id: int = None,
        FamilyId: int = None,
        CategoryId: int = None,
        StyleId: int = None,
        Type: str = None,
        SerieId: int = None,
        FilterId: int = None,
        ListId: int = None,
        IncludeCategories: bool = None,
        **kwargs
    ):
        """
        Obtém atributos de cadastro (cadaster attributes) do DMS.
        Todos os filtros do endpoint /Attribute/Cadaster estão disponíveis.

        Parâmetros:
            Id (int): Id do atributo
            FamilyId (int): Id da família
            CategoryId (int): Id da categoria
            StyleId (int): Id do estilo
            Type (str): Tipo do atributo
            SerieId (int): Id da série
            FilterId (int): Id do filtro
            ListId (int): Id da lista
            Lang (str): Idioma da resposta
            Page (int): Página para paginação
            Rows (int): Linhas por página
            IncludeCategories (bool): Incluir categorias relacionadas
            kwargs: Parâmetros adicionais suportados pela API

        Returns:
            BDSResult: Lista de atributos de cadastro
        """
        params = {}
        if Id is not None: params['Id'] = Id
        if FamilyId is not None: params['FamilyId'] = FamilyId
        if CategoryId is not None: params['CategoryId'] = CategoryId
        if StyleId is not None: params['StyleId'] = StyleId
        if Type is not None: params['Type'] = Type
        if SerieId is not None: params['SerieId'] = SerieId
        if FilterId is not None: params['FilterId'] = FilterId
        if ListId is not None: params['ListId'] = ListId
        if IncludeCategories is not None: params['IncludeCategories'] = IncludeCategories
        params.update(kwargs)
        return self._core._BDSCore__request(
            method="get",
            url=f"{self._core.datamanagement_url}/Attribute/Cadaster",
            params=params
        )

    def getSerialAttributes(
        self,
        Id: int = None,
        FamilyId: int = None,
        CategoryId: int = None,
        StyleId: int = None,
        TableId: int = None,
        Type: int = 1,
        SerieId: int = None,
        FilterId: int = None,
        ListId: int = None,
        IncludeFamilies: bool = None,
        IncludeCategories: bool = None,
        **kwargs
    ):
        """
        Obtém atributos seriais (serial attributes) do DMS.
        Todos os filtros do endpoint /Attribute/Cadaster estão disponíveis, com Type=1 por padrão.

        Parâmetros:
            Id (int): Id do atributo
            FamilyId (int): Id da família
            CategoryId (int): Id da categoria
            StyleId (int): Id do estilo
            TableId (int): Id da tabela
            Type (int): Tipo do atributo (1 = Serial; 2 = Cadastral; ambos se não especificar)
            SerieId (int): Id da série
            FilterId (int): Id do filtro
            ListId (int): Id da lista
            Lang (str): Idioma da resposta
            Page (int): Página para paginação
            Rows (int): Linhas por página
            IncludeFamilies (bool): Incluir famílias relacionadas
            IncludeCategories (bool): Incluir categorias relacionadas
            kwargs: Parâmetros adicionais suportados pela API

        Returns:
            BDSResult: Lista de atributos seriais
        """
        params = {}
        if Id is not None: params['Id'] = Id
        if FamilyId is not None: params['FamilyId'] = FamilyId
        if CategoryId is not None: params['CategoryId'] = CategoryId
        if StyleId is not None: params['StyleId'] = StyleId
        if TableId is not None: params['TableId'] = TableId
        if Type is not None: params['Type'] = Type
        if SerieId is not None: params['SerieId'] = SerieId
        if FilterId is not None: params['FilterId'] = FilterId
        if ListId is not None: params['ListId'] = ListId
        if IncludeFamilies is not None: params['IncludeFamilies'] = IncludeFamilies
        if IncludeCategories is not None: params['IncludeCategories'] = IncludeCategories
        params.update(kwargs)
        return self._core._BDSCore__request(
            method="get",
            url=f"{self._core.datamanagement_url}/Attribute/Serial",
            params=params
        )

    def getSeries(
        self,
        Id: int = None,
        FamilyId: int = None,
        FilterId: int = None,
        ListId: int = None,
        SerieName: str = None,
        SourceId: int = None,
        IsActive: bool = None,
        IncludeLists: bool = None,
        search: str = None,
        **kwargs
    ):
        """
        Obtém séries do DMS (endpoint /Serie).
        Todos os filtros do endpoint estão disponíveis.

        Parâmetros:
            Id (int): Id da série
            FamilyId (int): Id da família
            FilterId (int): Id do filtro
            ListId (int): Id da lista
            SerieName (str): Nome da série
            SourceId (int): Id da fonte
            IsActive (bool): Se a série está ativa
            Lang (str): Idioma da resposta
            Page (int): Página para paginação
            Rows (int): Linhas por página
            IncludeLists (bool): Incluir listas relacionadas
            search (str): Texto de busca
            kwargs: Parâmetros adicionais suportados pela API

        Returns:
            BDSResult: Lista de séries
        """
        params = {}
        if Id is not None: params['Id'] = Id
        if FamilyId is not None: params['FamilyId'] = FamilyId
        if FilterId is not None: params['FilterId'] = FilterId
        if ListId is not None: params['ListId'] = ListId
        if SerieName is not None: params['SerieName'] = SerieName
        if SourceId is not None: params['SourceId'] = SourceId
        if IsActive is not None: params['IsActive'] = IsActive
        if IncludeLists is not None: params['IncludeLists'] = IncludeLists
        if search is not None: params['search'] = search
        params.update(kwargs)
        return self._core._BDSCore__request(
            method="get",
            url=f"{self._core.datamanagement_url}/Serie",
            params=params
        )