"""
ENUMs para padronização de valores fixos da biblioteca BDS DataSolution.

Este módulo centraliza todos os valores constantes utilizados na API,
fornecendo autocomplete e validação para os desenvolvedores.
"""

from enum import Enum


class ResponseFormat(Enum):
    """
    Formatos de resposta suportados pela API DataPack.
    
    Permite diferentes formatos de serialização conforme a necessidade:
    - JSON: Ideal para integração programática
    - XML: Compatibilidade com sistemas legados
    - CSV: Análise em planilhas e ferramentas de BI
    - EXCEL: Relatórios executivos (formato de matriz)
    """
    JSON = "json"
    XML = "xml"  
    CSV = "csv"
    EXCEL = "excel"


class DynamicDate(Enum):
    """
    Datas dinâmicas aceitas pela API DataPack.
    
    Facilita consultas com datas relativas organizadas por categorias:
    
    ## Datas Básicas Relativas
    - YESTERDAY: Dia anterior (D-1)
    - LAST_BUSINESS_DAY: Último dia útil (C-1)  
    - FIRST_BUSINESS_DAY_PREV_MONTH: Primeiro dia útil do mês anterior (PDU_MES-1)
    
    ## Unidades de Tempo
    - CALENDAR_DAYS: Dias corridos (C)
    - BUSINESS_DAYS: Dias úteis (D)
    - WEEK: Semana (S)
    - MONTH: Mês (M)
    - YEAR: Ano (A)
    
    ## Períodos Semanais
    - FIRST_CALENDAR_DAY_WEEK: Primeiro dia corrido semanal (PDC_SEM)
    - FIRST_BUSINESS_DAY_WEEK: Primeiro dia útil semanal (PDU_SEM)
    - LAST_BUSINESS_DAY_WEEK: Último dia útil semanal (UDU_SEM)
    - LAST_CALENDAR_DAY_WEEK: Último dia corrido semanal (UDC_SEM)
    
    ## Períodos Mensais
    - FIRST_CALENDAR_DAY_MONTH: Primeiro dia corrido do mês (PDC_MES)
    - FIRST_BUSINESS_DAY_MONTH: Primeiro dia útil do mês (PDU_MES)
    - LAST_BUSINESS_DAY_MONTH: Último dia útil do mês (UDU_MES)
    - LAST_CALENDAR_DAY_MONTH: Último dia corrido do mês (UDC_MES)
    
    ## Períodos Semestrais
    - FIRST_CALENDAR_DAY_SEMESTER: Primeiro dia corrido do semestre (PDC_SMT)
    - FIRST_BUSINESS_DAY_SEMESTER: Primeiro dia útil do semestre (PDU_SMT)
    - LAST_BUSINESS_DAY_SEMESTER: Último dia útil do semestre (UDU_SMT)
    - LAST_CALENDAR_DAY_SEMESTER: Último dia corrido do semestre (UDC_SMT)
    
    ## Períodos Anuais
    - FIRST_CALENDAR_DAY_YEAR: Primeiro dia corrido do ano (PDC_ANO)
    - FIRST_BUSINESS_DAY_YEAR: Primeiro dia útil do ano (PDU_ANO)
    - LAST_BUSINESS_DAY_YEAR: Último dia útil do ano (UDU_ANO)
    - LAST_CALENDAR_DAY_YEAR: Último dia corrido do ano (UDC_ANO)
    
    ## Extremos da Série
    - FIRST_DATA: Primeiro dado da série (FIRST)
    - LAST_DATA: Último dado da série (LAST)
    """
    
    # Datas Básicas Relativas
    YESTERDAY = "D-1"
    LAST_BUSINESS_DAY = "C-1"
    FIRST_BUSINESS_DAY_PREV_MONTH = "PDU_MES-1"
    
    # Unidades de Tempo
    CALENDAR_DAYS = "C"
    BUSINESS_DAYS = "D"
    WEEK = "S"
    MONTH = "M"
    YEAR = "A"
    
    # Períodos Semanais
    FIRST_CALENDAR_DAY_WEEK = "PDC_SEM"
    FIRST_BUSINESS_DAY_WEEK = "PDU_SEM"
    LAST_BUSINESS_DAY_WEEK = "UDU_SEM"
    LAST_CALENDAR_DAY_WEEK = "UDC_SEM"
    
    # Períodos Mensais
    FIRST_CALENDAR_DAY_MONTH = "PDC_MES"
    FIRST_BUSINESS_DAY_MONTH = "PDU_MES"
    LAST_BUSINESS_DAY_MONTH = "UDU_MES"
    LAST_CALENDAR_DAY_MONTH = "UDC_MES"
    
    # Períodos Semestrais
    FIRST_CALENDAR_DAY_SEMESTER = "PDC_SMT"
    FIRST_BUSINESS_DAY_SEMESTER = "PDU_SMT"
    LAST_BUSINESS_DAY_SEMESTER = "UDU_SMT"
    LAST_CALENDAR_DAY_SEMESTER = "UDC_SMT"
    
    # Períodos Anuais
    FIRST_CALENDAR_DAY_YEAR = "PDC_ANO"
    FIRST_BUSINESS_DAY_YEAR = "PDU_ANO"
    LAST_BUSINESS_DAY_YEAR = "UDU_ANO"
    LAST_CALENDAR_DAY_YEAR = "UDC_ANO"
    
    # Extremos da Série
    FIRST_DATA = "FIRST"
    LAST_DATA = "LAST"


class CorporateActionType(Enum):
    """
    Códigos de tipos de eventos corporativos conforme documentação da API.
    
    Organizado por categorias para facilitar o uso:
    
    ## Proventos em Dinheiro
    - DIVIDEND: Distribuição de lucros
    - CAPITAL_RETURN: Devolução aos acionistas
    - CASH_BONUS: Bonus em espécie
    - INTEREST_ON_EQUITY: JCP
    - INCOME: Rendimentos de FIIs
    - INTEREST: Pagamento de juros
    - AMORTIZATION: Pagamento de principal
    - AWARD: Pagamentos especiais
    - MONETARY_UPDATE: Correção monetária
    - NET_INCOME: Rendimento líquido de impostos
    
    ## Proventos em Ações
    - STOCK_BONUS: Distribuição gratuita de ações
    - CAPITAL_RETURN_STOCK: Devolução em ações
    - CAPITAL_RETURN_WITH_REDUCTION: Com redução de ações
    
    ## Alterações no Capital
    - STOCK_SPLIT: Split de ações
    - STOCK_GROUPING: Grupamento de ações
    
    ## Direitos de Subscrição
    - SUBSCRIPTION: Direito de subscrição
    - PRIORITY_SUBSCRIPTION: Direito preferencial
    - SUBSCRIPTION_EXERCISE: Exercício do direito
    - SUBSCRIPTION_WITH_WAIVER: Com renúncia
    - LEFTOVER_SUBSCRIPTION: Sobras não exercidas
    - SUBSCRIPTION_APPROVAL: Aprovação final
    
    ## Reorganizações Societárias
    - INCORPORATION: Fusão com outra empresa
    - MERGER: União de empresas
    - SPIN_OFF_WITH_CAPITAL_REDUCTION: Divisão da empresa
    - SPIN_OFF_WITH_CAPITAL_AND_QUANTITY_REDUCTION: Divisão com redução
    - ASSET_CONVERSION: Mudança de classe de ações
    - DISSENT: Direito de retirada
    
    ## Operações Especiais
    - FRACTION_CANCELLATION: Eliminação de frações
    - FRACTION_AUCTION: Venda de frações
    - FRACTION_DONATION: Distribuição gratuita
    - FRACTION_ADMINISTRATION: Gestão de frações
    - FRACTION_PURCHASE: Aquisição de frações
    - FRACTION_SALE: Venda de frações
    - UPDATE: Atualização de dados
    - MULTIPLE_EVENT: Múltiplos eventos simultâneos
    - RETRACTION: Cancelamento de evento
    - PARTIAL_FIXED_INCOME_REDEMPTION: Resgate parcial
    - FIXED_INCOME_REDEMPTION: Resgate total
    - VARIABLE_INCOME_REDEMPTION: Resgate de ações
    """
    
    # Proventos em Dinheiro
    DIVIDEND = 10
    CAPITAL_RETURN = 11
    CASH_BONUS = 12
    INTEREST_ON_EQUITY = 13
    INCOME = 14
    INTEREST = 16
    AMORTIZATION = 17
    AWARD = 18
    MONETARY_UPDATE = 19
    NET_INCOME = 98
    
    # Proventos em Ações
    STOCK_BONUS = 20
    CAPITAL_RETURN_STOCK = 21
    CAPITAL_RETURN_WITH_REDUCTION = 22
    
    # Alterações no Capital
    STOCK_SPLIT = 30
    STOCK_GROUPING = 40
    
    # Direitos de Subscrição
    SUBSCRIPTION = 50
    PRIORITY_SUBSCRIPTION = 51
    SUBSCRIPTION_EXERCISE = 52
    SUBSCRIPTION_WITH_WAIVER = 53
    LEFTOVER_SUBSCRIPTION = 99
    SUBSCRIPTION_APPROVAL = 101
    
    # Reorganizações Societárias
    INCORPORATION = 60
    MERGER = 70
    SPIN_OFF_WITH_CAPITAL_REDUCTION = 80
    SPIN_OFF_WITH_CAPITAL_AND_QUANTITY_REDUCTION = 81
    ASSET_CONVERSION = 95
    DISSENT = 96
    
    # Operações Especiais
    FRACTION_CANCELLATION = 71
    FRACTION_AUCTION = 72
    FRACTION_DONATION = 73
    FRACTION_ADMINISTRATION = 74
    FRACTION_PURCHASE = 75
    FRACTION_SALE = 76
    UPDATE = 90
    MULTIPLE_EVENT = 91
    RETRACTION = 92
    PARTIAL_FIXED_INCOME_REDEMPTION = 93
    FIXED_INCOME_REDEMPTION = 94
    VARIABLE_INCOME_REDEMPTION = 97


class BooleanString(Enum):
    """
    Valores booleanos em formato string aceitos pela API.
    
    Alguns parâmetros da API requerem valores booleanos como string:
    - TRUE: "True"
    - FALSE: "False"
    """
    TRUE = "True"
    FALSE = "False"


# Aliases para facilitar importação
Format = ResponseFormat
Date = DynamicDate
Corporate = CorporateActionType
Boolean = BooleanString
