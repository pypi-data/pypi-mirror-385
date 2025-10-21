
class Common:
    def __init__(self, core):
        self._core = core

    # ====================================
    #         MÉTODOS DE DATAS 
    # ====================================

    def addDays(self, ReferenceDate, Source=None, Days=None, BusinessDay=None, Format=None, IgnNull=None):
        """
        Adiciona ou subtrai dias de uma data de referência, considerando dias úteis e feriados.
        
        Args:
            ReferenceDate (str): Data para a qual se deseja adicionar ou subtrair dias (obrigatório)
            Source (str): Fonte da data. Se não informado, será utilizada a fonte ANBIMA
            Days (int): Número de dias a adicionar/subtrair
            BusinessDay (str): Lista de feriados. Se não informado, será utilizado o padrão de dias úteis (DU)
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos ou não (default: "False")
            
        Returns:
            dict: Resultado com a data modificada e contagem de dias
        """
        return self._core._BDSCore__make_request(
            self._core.common_url,
            "calendar/v1/getAddDays",
            ReferenceDate=ReferenceDate,
            Source=Source,
            Days=Days,
            BusinessDay=BusinessDay,
            Format=Format,
            IgnNull=IgnNull
        )

    def decodeDynamicDate(self, ReferenceDate, DynamicDates, SourceName=None, Format=None, IgnNull=None):
        """
        Decodifica datas dinâmicas baseadas em uma data de referência.
        
        Args:
            ReferenceDate (str): Data para a qual se deseja decodificar (obrigatório)
            DynamicDates (str): Data dinâmica para decodificação (obrigatório)
            SourceName (str): Fonte da data. Se não informado, será utilizada a fonte ANBIMA
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos ou não (default: "False")
            
        Returns:
            list: Lista de datas decodificadas
        """
        return self._core._BDSCore__make_request(
            self._core.common_url,
            "calendar/v1/getDateDecode",
            ReferenceDate=ReferenceDate,
            DynamicDates=DynamicDates,
            SourceName=SourceName,
            Format=Format,
            IgnNull=IgnNull
        )

    def encodeDynamicDate(self, ReferenceDate, ReferenceDateBase, SourceName=None, Format=None, IgnNull=None):
        """
        Codifica datas baseadas em uma data de referência.
        
        Args:
            ReferenceDate (str): Data de referência para codificação (obrigatório)
            ReferenceDateBase (str): Data base para codificação (obrigatório)
            SourceName (str): Fonte da data. Se não informado, será utilizada a fonte ANBIMA
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos ou não (default: "False")
            
        Returns:
            list: Lista de datas codificadas
        """
        return self._core._BDSCore__make_request(
            self._core.common_url,
            "calendar/v1/getDateEncode",
            ReferenceDate=ReferenceDate,
            ReferenceDateBase=ReferenceDateBase,
            SourceName=SourceName,
            Format=Format,
            IgnNull=IgnNull
        )

    def diffDates(self, ReferenceDate, ComparisonDate, Source=None, BusinessDay=None, Format=None, IgnNull=None):
        """
        Calcula a diferença entre duas datas, considerando dias úteis e feriados.
        
        Args:
            ReferenceDate (str): Data inicial para cálculo (obrigatório)
            ComparisonDate (str): Data final para cálculo (obrigatório)
            Source (str): Fonte da data. Se não informado, será utilizada a fonte ANBIMA
            BusinessDay (str): Lista de feriados. Se não informado, será utilizado o padrão de dias úteis (DU)
            Format (str): Formato de retorno (default: "Json")
            IgnNull (str): Se deve retornar valores nulos ou não (default: "False")
            
        Returns:
            dict: Resultado com a diferença entre as datas
        """
        return self._core._BDSCore__make_request(
            self._core.common_url,
            "calendar/v1/getDifferenceBetweenTwoDays",
            ReferenceDate=ReferenceDate,
            ComparisonDate=ComparisonDate,
            Source=Source,
            BusinessDay=BusinessDay,
            Format=Format,
            IgnNull=IgnNull
        )