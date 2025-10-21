
import pandas as pd
import xlsxwriter
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import logging
from typing import List, Optional, Dict, Any
import math

from bdscore.enums import ResponseFormat, DynamicDate, BooleanString
from bdscore.result import BDSResult

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Utils:
    """
    Classe para métodos utilitários e análises avançadas da BDS DataSolution.
    """
    
    def __init__(self, bds_core):
        """
        Inicializa a classe Utils.
        
        Args:
            bds_core: Instância da classe BDSCore para acessar os serviços
        """
        self.bds_core = bds_core

    def corporateActionsReport(
        self,
        symbols: List[str],
        initialDate: str,
        finalDate: str,
        outputFile: str = "analise_comparativa.xlsx",
        responseFormat: ResponseFormat = ResponseFormat.JSON
    ) -> str:
        """
        Realiza análise comparativa entre dados do getEquitiesB3 e getAdjQuoteHistory.

        Converte o código legacy do cliente em um método unificado que:
        - Coleta dados de ambas as APIs
        - Realiza análise estatística comparativa
        - Gera relatório Excel formatado
        - Calcula discrepâncias e estatísticas

        Args:
            symbols (List[str]): Lista de símbolos para análise (ex: ['PETR4', 'VALE3'])
            initialDate (str): Data de início no formato 'YYYY-MM-DD'
            finalDate (str): Data de fim no formato 'YYYY-MM-DD'
            outputFile (str): Nome do arquivo Excel de saída
            responseFormat (ResponseFormat): Formato de resposta da API

        Returns:
            str: Mensagem de status da análise

        Raises:
            ValueError: Se parâmetros inválidos
            RuntimeError: Se erro na coleta de dados ou geração do relatório
        """
        try:
            logger.info(f"Iniciando análise comparativa para {len(symbols)} símbolos")
            logger.info(f"Período: {initialDate} até {finalDate}")

            # Validar parâmetros
            if not symbols or not isinstance(symbols, list):
                raise ValueError("symbols deve ser uma lista não-vazia")

            if not initialDate or not finalDate:
                raise ValueError("initialDate e finalDate são obrigatórios")

            # Estruturas para armazenar dados
            all_data_b3 = []
            all_data_adj = []
            summary_stats = []
            all_merged_data = []  # Para gráficos

            # Processar cada símbolo
            for i, symbol in enumerate(symbols, 1):
                logger.info(f"Processando {symbol} ({i}/{len(symbols)})")

                try:
                    # Coletar dados do getEquitiesB3
                    logger.info(f"Coletando dados B3 para {symbol}")
                    result_b3 = self.bds_core.datapack.getEquitiesB3(
                        Symbols=[symbol],
                        InitialDate=initialDate,
                        FinalDate=finalDate,
                        Format=responseFormat
                    )

                    # Coletar dados do getAdjQuoteHistory
                    logger.info(f"Coletando dados históricos ajustados para {symbol}")
                    result_adj = self.bds_core.datapack.getAdjQuoteHistory(
                        Symbols=[symbol],
                        InitialDate=initialDate,
                        FinalDate=finalDate,
                        Format=responseFormat
                    )

                    # Converter para DataFrame
                    df_b3 = result_b3.data.to_df()
                    df_adj = result_adj.data.to_df()

                    if df_b3.empty or df_adj.empty:
                        logger.warning(f"Dados vazios para {symbol}")
                        continue

                    # Diagnóstico: logar colunas reais
                    logger.info(f"Colunas df_b3 para {symbol}: {list(df_b3.columns)}")
                    logger.info(f"Colunas df_adj para {symbol}: {list(df_adj.columns)}")

                    # Preparar dados B3
                    df_b3_processed = df_b3.copy()
                    df_b3_processed['Symbol'] = symbol
                    df_b3_processed['Source'] = 'B3'
                    df_b3_processed['Date'] = pd.to_datetime(df_b3_processed.get('Date', df_b3_processed.get('TradingDate')))

                    # Preparar dados ajustados
                    df_adj_processed = df_adj.copy()
                    df_adj_processed['Symbol'] = symbol
                    df_adj_processed['Source'] = 'AdjustedHistory'
                    df_adj_processed['Date'] = pd.to_datetime(df_adj_processed.get('Date', df_adj_processed.get('TradingDate')))

                    # Análise comparativa por data
                    merged_data = self._compare_symbol_data(df_b3_processed, df_adj_processed, symbol)

                    # Armazenar dados processados
                    all_data_b3.append(df_b3_processed)
                    all_data_adj.append(df_adj_processed)
                    all_merged_data.append((symbol, merged_data))

                    # Calcular estatísticas do símbolo
                    symbol_stats = self._calculate_symbol_statistics(merged_data, symbol)
                    summary_stats.append(symbol_stats)

                    logger.info(f"Processamento de {symbol} concluído")

                except Exception as e:
                    logger.error(f"Erro ao processar {symbol}: {str(e)}")
                    continue

            # Gerar relatório Excel
            self._generate_excel_report(
                all_data_b3,
                all_data_adj,
                summary_stats,
                outputFile,
                True,
                all_merged_data
            )

            success_count = len(summary_stats)
            logger.info(f"Análise concluída: {success_count}/{len(symbols)} símbolos processados")

            return f"Análise concluída com sucesso! {success_count} símbolos processados. Relatório salvo em: {outputFile}"

        except Exception as e:
            logger.error(f"Erro na análise comparativa: {str(e)}")
            raise RuntimeError(f"Falha na análise comparativa: {str(e)}") from e

    def _compare_symbol_data(self, df_b3: pd.DataFrame, df_adj: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Compara dados de um símbolo entre B3 e AdjustedHistory.
        
        Args:
            df_b3: DataFrame com dados do B3
            df_adj: DataFrame com dados ajustados
            symbol: Símbolo sendo analisado
            
        Returns:
            DataFrame com comparação por data
        """
        # Mapear colunas reais para nomes padronizados
        b3_map = {
            'lastPric': 'Close',
            'maxPric': 'High',
            'minPric': 'Low',
            'tradAvrgPric': 'Avg',
            'ntlFinVol': 'Volume',
        }
        adj_map = {
            'adjClosePrice': 'Close',
            'adjHighPrice': 'High',
            'adjLowPrice': 'Low',
            'adjAvgPrice': 'Avg',
            'adjVolume': 'Volume',
        }

        # Renomear colunas para padronizar
        df_b3_ren = df_b3.rename(columns=b3_map)
        df_adj_ren = df_adj.rename(columns=adj_map)

        # Garantir coluna Date
        df_b3_ren['Date'] = pd.to_datetime(df_b3_ren['referenceDate'])
        df_adj_ren['Date'] = pd.to_datetime(df_adj_ren['referenceDate'])

        # Forçar colunas padronizadas para float
        for col in ['Close', 'High', 'Low', 'Avg', 'Volume']:
            if col in df_b3_ren:
                df_b3_ren[col] = pd.to_numeric(df_b3_ren[col], errors='coerce')
            if col in df_adj_ren:
                df_adj_ren[col] = pd.to_numeric(df_adj_ren[col], errors='coerce')

        # Merge por data
        merge_cols = ['Date', 'Close', 'High', 'Low', 'Avg', 'Volume']
        merged = pd.merge(
            df_b3_ren[[c for c in merge_cols if c in df_b3_ren.columns]],
            df_adj_ren[[c for c in merge_cols if c in df_adj_ren.columns]],
            on='Date',
            suffixes=('_B3', '_Adj'),
            how='outer'
        )
        merged['Symbol'] = symbol

        # Calcular diferenças percentuais para colunas padronizadas
        for col in ['Close', 'High', 'Low', 'Avg', 'Volume']:
            if f'{col}_B3' in merged.columns and f'{col}_Adj' in merged.columns:
                merged[f'{col}_Diff_Pct'] = (
                    (merged[f'{col}_Adj'] - merged[f'{col}_B3']) / merged[f'{col}_B3'] * 100
                ).round(4)
        return merged

    def _calculate_symbol_statistics(self, merged_data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """
        Calcula estatísticas para um símbolo.
        
        Args:
            merged_data: DataFrame com dados comparativos
            symbol: Símbolo analisado
            
        Returns:
            Dicionário com estatísticas do símbolo
        """

        stats = {'Symbol': symbol, 'TotalDays': len(merged_data)}
        b3_cols = [col for col in merged_data.columns if col.endswith('_B3')]
        adj_cols = [col for col in merged_data.columns if col.endswith('_Adj')]
        if b3_cols:
            stats['DaysWithB3Data'] = (merged_data[b3_cols].notna().any(axis=1)).sum()
        else:
            stats['DaysWithB3Data'] = 0
        if adj_cols:
            stats['DaysWithAdjData'] = (merged_data[adj_cols].notna().any(axis=1)).sum()
        else:
            stats['DaysWithAdjData'] = 0

        # Estatísticas de diferenças percentuais
        diff_columns = [col for col in merged_data.columns if col.endswith('_Diff_Pct')]
        for col in diff_columns:
            clean_data = merged_data[col].dropna()
            if not clean_data.empty:
                stats[f'{col}_Mean'] = clean_data.mean()
                stats[f'{col}_Std'] = clean_data.std()
                stats[f'{col}_Max'] = clean_data.max()
                stats[f'{col}_Min'] = clean_data.min()
                stats[f'{col}_AbsMean'] = clean_data.abs().mean()
        return stats

    def _generate_excel_report(
        self,
        all_data_b3: List[pd.DataFrame],
        all_data_adj: List[pd.DataFrame],
        summary_stats: List[Dict],
        output_file: str,
        include_summary: bool,
        all_merged_data: List
    ):
        """
        Gera relatório Excel formatado com os resultados da análise.
        
        Args:
            all_data_b3: Lista de DataFrames com dados B3
            all_data_adj: Lista de DataFrames com dados ajustados
            summary_stats: Lista com estatísticas por símbolo
            output_file: Nome do arquivo de saída
            include_summary: Se deve incluir aba de resumo
            all_merged_data: Lista de tuplas (symbol, merged_data) para gráficos
        """
        logger.info(f"Gerando relatório Excel: {output_file}")
        
        with xlsxwriter.Workbook(output_file) as workbook:
            # Formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4F81BD',
                'font_color': 'white',
                'border': 1
            })
            header_center_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4F81BD',
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })
            
            number_format = workbook.add_format({'num_format': '#,##0.0000'})
            percent_format = workbook.add_format({'num_format': '0.00%'})
            date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
            
            # Aba de resumo estatístico
            if include_summary and summary_stats:
                summary_df = pd.DataFrame(summary_stats)
                worksheet = workbook.add_worksheet('Resumo_Estatistico')
                # Escrever headers
                for col_num, column in enumerate(summary_df.columns):
                    worksheet.write(0, col_num, column, header_format)
                # Escrever dados
                for row_num, row_data in enumerate(summary_df.itertuples(index=False), 1):
                    for col_num, value in enumerate(row_data):
                        if isinstance(value, float):
                            worksheet.write(row_num, col_num, value, number_format)
                        else:
                            worksheet.write(row_num, col_num, value)
                # Ajustar largura das colunas
                for col_num, column in enumerate(summary_df.columns):
                    worksheet.set_column(col_num, col_num, 15)

            # Nova aba para gráficos e dados
            chart_sheet = workbook.add_worksheet('Graficos')
            color_b3 = '#0f121a'
            color_adj = '#ee2841'
            row_offset = 0
            data_col = 40
            max_rows = 0
            for idx, (symbol, merged_data) in enumerate(all_merged_data):
                merged_data = merged_data.sort_values('Date')
                n_rows = len(merged_data)
                # Gráfico de linha (Close) usando as colunas do ticker correspondente
                line_chart = workbook.add_chart({'type': 'line'})
                line_chart.add_series({
                    'name': f'{symbol} Nominal (B3)',
                    'categories': ['Graficos', 2, data_col, n_rows+1, data_col],
                    'values':     ['Graficos', 2, data_col+1, n_rows+1, data_col+1],
                    'line': {'color': color_b3, 'width': 2},
                })
                line_chart.add_series({
                    'name': f'{symbol} Ajustada',
                    'categories': ['Graficos', 2, data_col, n_rows+1, data_col],
                    'values':     ['Graficos', 2, data_col+2, n_rows+1, data_col+2],
                    'line': {'color': color_adj, 'width': 2},
                })
                line_chart.set_title({'name': f'{symbol} - Cotação Nominal x Ajustada'})
                line_chart.set_x_axis({'name': 'Data', 'date_axis': True})
                line_chart.set_y_axis({'name': 'Preço'})
                line_chart.set_legend({'position': 'bottom'})
                chart_sheet.insert_chart(row_offset+1, 0, line_chart, {'x_scale': 4, 'y_scale': 1.2})
                # Título mesclado acima do bloco de dados
                chart_sheet.merge_range(0, data_col, 0, data_col+2, symbol, header_center_format)
                # Cabeçalhos
                chart_sheet.write(1, data_col, 'Date', header_format)
                chart_sheet.write(1, data_col+1, 'Close_B3', header_format)
                chart_sheet.write(1, data_col+2, 'Close_Adj', header_format)
                # Dados
                for i, row in enumerate(merged_data.itertuples(index=False), 0):
                    chart_sheet.write_datetime(i+2, data_col, getattr(row, 'Date'), date_format)
                    val_b3 = getattr(row, 'Close_B3', None)
                    val_adj = getattr(row, 'Close_Adj', None)
                    if isinstance(val_b3, (int, float)) and not (isinstance(val_b3, float) and (math.isnan(val_b3) or math.isinf(val_b3))):
                        chart_sheet.write_number(i+2, data_col+1, val_b3, number_format)
                    else:
                        chart_sheet.write(i+2, data_col+1, '')
                    if isinstance(val_adj, (int, float)) and not (isinstance(val_adj, float) and (math.isnan(val_adj) or math.isinf(val_adj))):
                        chart_sheet.write_number(i+2, data_col+2, val_adj, number_format)
                    else:
                        chart_sheet.write(i+2, data_col+2, '')
                max_rows = max(max_rows, len(merged_data))
                row_offset += 20
                data_col += 4  # espaço entre blocos
            
            # Dados B3 consolidados
            if all_data_b3:
                combined_b3 = pd.concat(all_data_b3, ignore_index=True)
                worksheet = workbook.add_worksheet('Dados_B3')
                self._write_dataframe_to_worksheet(
                    worksheet, combined_b3, header_format, number_format, date_format
                )
            
            # Dados ajustados consolidados
            if all_data_adj:
                combined_adj = pd.concat(all_data_adj, ignore_index=True)
                worksheet = workbook.add_worksheet('Dados_Ajustados')
                self._write_dataframe_to_worksheet(
                    worksheet, combined_adj, header_format, number_format, date_format
                )
        
        logger.info(f"Relatório Excel gerado com sucesso: {output_file}")

    def _write_dataframe_to_worksheet(self, worksheet, df, header_format, number_format, date_format):
        """
        Escreve DataFrame para uma worksheet do Excel com formatação.
        
        Args:
            worksheet: Worksheet do xlsxwriter
            df: DataFrame para escrever
            header_format: Formato para headers
            number_format: Formato para números
            date_format: Formato para datas
        """
        # Headers
        for col_num, column in enumerate(df.columns):
            worksheet.write(0, col_num, column, header_format)
        
        # Dados
        for row_num, row_data in enumerate(df.itertuples(index=False), 1):
            for col_num, value in enumerate(row_data):
                column_name = df.columns[col_num]
                
                if pd.isna(value):
                    worksheet.write(row_num, col_num, '')
                elif 'Date' in column_name and pd.api.types.is_datetime64_any_dtype(df[column_name]):
                    worksheet.write(row_num, col_num, value, date_format)
                elif isinstance(value, (int, float)) and not pd.isna(value):
                    worksheet.write(row_num, col_num, value, number_format)
                else:
                    worksheet.write(row_num, col_num, str(value))
        
        # Ajustar largura das colunas
        for col_num, column in enumerate(df.columns):
            worksheet.set_column(col_num, col_num, 15)
