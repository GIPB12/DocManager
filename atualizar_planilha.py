
import os
import re
import sys
import unicodedata
import tkinter as tk

from tkinter import ttk, messagebox
from datetime import datetime
from decimal import Decimal, InvalidOperation

import shutil
import openpyxl
from openpyxl import load_workbook
from tksheet import Sheet


TIPOS_SERVICO = {
    "CONTABIL": "CONTÁBIL",
    "NAO CONTABIL": "NÃO CONTÁBIL",
    "AUDITORES": "AUDITORES",
}


def obter_pasta_aplicacao():
    """
    Retorna a pasta do programa.
    Funciona tanto executando o .py quanto o .exe.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))


def normalizar_texto(texto):
    """
    Remove acentos e converte o texto para maiúsculas.
    Usado somente para comparar os tipos de serviço.
    """
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )
    return texto.upper().strip()


def converter_valor(valor_texto):
    """
    Converte valores brasileiros, como:
    100,00
    1.250,75
    350
    """
    valor_texto = valor_texto.strip()

    padrao = r"(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d{1,2})?"

    if not re.fullmatch(padrao, valor_texto):
        raise ValueError("Valor inválido. Use, por exemplo, 100,00.")

    valor_limpo = valor_texto.replace(".", "").replace(",", ".")

    try:
        valor = Decimal(valor_limpo)
    except InvalidOperation:
        raise ValueError("Não foi possível interpretar o valor.")

    if valor < 0:
        raise ValueError("O valor não pode ser negativo.")

    return valor


def formatar_valor(valor):
    """
    Formata um Decimal no padrão brasileiro.
    Exemplo: 1250.75 -> 1.250,75
    """
    texto = "{:.2f}".format(valor)
    inteiro, decimal = texto.split(".")

    grupos = []
    while inteiro:
        grupos.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]

    return ".".join(grupos) + "," + decimal


def interpretar_nome(nome_arquivo):
    """
    Extrai todos os campos que conseguir do nome do arquivo.
    Se algum campo estiver inválido, retorna os demais dados encontrados
    e descreve o problema em "erro". Apenas arquivos totalmente válidos
    podem ser registrados na planilha.
    """
    nome_sem_extensao = os.path.splitext(nome_arquivo)[0]
    resultado = {
        "arquivo": nome_arquivo,
        "data": "",
        "data_texto": "",
        "data_obj": None,
        "descricao": "",
        "valor": "",
        "valor_texto": "",
        "tipo": "",
        "tipo_informado": "",
        "status": "Inválido",
        "erro": "",
    }
    problemas = []

    # Extrai o valor entre parênteses e o texto final (tipo informado).
    correspondencia = re.search(
        r"\(\s*([^()]*)\s*\)\s*(.*?)\s*$",
        nome_sem_extensao
    )

    parte_inicial = nome_sem_extensao
    tipo_original = ""
    if correspondencia:
        valor_texto = correspondencia.group(1).strip()
        tipo_original = correspondencia.group(2).strip()
        resultado["valor_texto"] = valor_texto
        resultado["tipo_informado"] = tipo_original
        parte_inicial = nome_sem_extensao[:correspondencia.start()].strip()

        try:
            resultado["valor"] = converter_valor(valor_texto)
        except ValueError as erro:
            problemas.append("Valor: {}".format(erro))

        tipo_normalizado = normalizar_texto(tipo_original)
        tipo = TIPOS_SERVICO.get(tipo_normalizado)
        if tipo is not None:
            resultado["tipo"] = tipo
        else:
            problemas.append(
                "Tipo de serviço não reconhecido: '{}'".format(
                    tipo_original or "não informado"
                )
            )
    else:
        problemas.append(
            "Não foi encontrado um valor entre parênteses seguido do tipo de serviço."
        )

    # Extrai a data e a descrição mesmo que o tipo ou valor estejam errados.
    inicio = re.match(
        r"^(\d{2}\.\d{2}\.\d{2})\s+(.+?)\s*$",
        parte_inicial
    )
    if inicio:
        data_texto = inicio.group(1)
        resultado["data_texto"] = data_texto
        resultado["descricao"] = inicio.group(2).strip()

        try:
            data = datetime.strptime(data_texto, "%d.%m.%y")
            resultado["data"] = data.strftime("%d/%m/%Y")
            resultado["data_obj"] = data
        except ValueError:
            problemas.append("Data inválida: '{}'".format(data_texto))

        if not resultado["descricao"]:
            problemas.append("A descrição está vazia.")
    else:
        problemas.append(
            "O nome deve começar com a data no formato dd.mm.aa e depois conter a descrição."
        )

    if not problemas:
        resultado["status"] = "Válido"
        resultado["erro"] = ""
    else:
        resultado["status"] = "Inválido"
        resultado["erro"] = " | ".join(problemas)

    return resultado


class SistemaDocumentos(ttk.Frame):

    def __init__(self, master, app):
        super().__init__(master)

        self.app = app

        # Mantém a referência usada pelo código existente,
        # mas agora ela representa a tela, não a janela principal.
        self.janela = self

        self.pasta_aplicacao = obter_pasta_aplicacao()
        self.pasta_novos = os.path.join(
            self.pasta_aplicacao,
            "NOVOS"
        )

        self.resultados = []

        self.criar_interface()
        self.verificar_pasta()

    def criar_interface(self):
        """Monta a tela de validação e registro no padrão visual da aplicação."""
        estilo = ttk.Style(self)
        estilo.configure(
            "Documentos.TFrame",
            background="#F5F6F8",
        )
        estilo.configure(
            "Documentos.TLabel",
            background="#F5F6F8",
            foreground="#202938",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Documentos.Titulo.TLabel",
            background="#F5F6F8",
            foreground="#202938",
            font=("Segoe UI", 15, "bold"),
        )
        estilo.configure(
            "Documentos.Subtitulo.TLabel",
            background="#F5F6F8",
            foreground="#667085",
            font=("Segoe UI", 9),
        )
        estilo.configure(
            "Documentos.Card.TFrame",
            background="#FFFFFF",
            relief="solid",
            borderwidth=1,
        )
        estilo.configure(
            "Documentos.CardLabel.TLabel",
            background="#FFFFFF",
            foreground="#202938",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Documentos.Muted.TLabel",
            background="#FFFFFF",
            foreground="#667085",
            font=("Segoe UI", 9),
        )
        estilo.configure(
            "Documentos.Resumo.TLabel",
            background="#EAF2FF",
            foreground="#175CD3",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 8),
        )
        estilo.configure(
            "Documentos.TButton",
            font=("Segoe UI", 9),
            padding=(10, 8),
        )
        estilo.configure(
            "Documentos.Primary.TButton",
            font=("Segoe UI", 9, "bold"),
            padding=(12, 8),
        )

        self.configure(
            style="Documentos.TFrame",
            padding=(22, 16, 22, 18),
        )
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Cabeçalho e navegação
        cabecalho = ttk.Frame(self, style="Documentos.TFrame")
        cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        cabecalho.columnconfigure(1, weight=1)

        ttk.Button(
            cabecalho,
            text="← Voltar ao menu",
            command=self.app.mostrar_menu,
            style="Documentos.TButton",
        ).grid(row=0, column=0, sticky="w", padx=(0, 16))

        bloco_titulo = ttk.Frame(cabecalho, style="Documentos.TFrame")
        bloco_titulo.grid(row=0, column=1, sticky="w")

        ttk.Label(
            bloco_titulo,
            text="Atualização da Planilha",
            style="Documentos.Titulo.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            bloco_titulo,
            text="Valide os documentos e registre os lançamentos nas planilhas mensais.",
            style="Documentos.Subtitulo.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        # Cartão de pasta e ações
        card_acoes = ttk.Frame(
            self,
            style="Documentos.Card.TFrame",
            padding=14,
        )
        card_acoes.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        card_acoes.columnconfigure(0, weight=1)

        ttk.Label(
            card_acoes,
            text="PASTA DE ENTRADA",
            style="Documentos.Muted.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.label_pasta = ttk.Label(
            card_acoes,
            text="Pasta: " + self.pasta_novos,
            style="Documentos.CardLabel.TLabel",
            anchor="w",
        )
        self.label_pasta.grid(
            row=1, column=0, columnspan=3, sticky="ew", pady=(0, 12)
        )

        botoes = ttk.Frame(card_acoes, style="Documentos.Card.TFrame")
        botoes.grid(row=2, column=0, sticky="ew")

        ttk.Button(
            botoes,
            text="Ler pasta NOVOS",
            command=self.ler_arquivos,
            style="Documentos.Primary.TButton",
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            botoes,
            text="Abrir pasta NOVOS",
            command=self.abrir_pasta,
            style="Documentos.TButton",
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            botoes,
            text="Registrar na planilha",
            command=self.registrar_planilhas,
            style="Documentos.Primary.TButton",
        ).pack(side="left")

        # Cartão da tabela
        card_tabela = ttk.Frame(
            self,
            style="Documentos.Card.TFrame",
            padding=10,
        )
        card_tabela.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        card_tabela.columnconfigure(0, weight=1)
        card_tabela.rowconfigure(1, weight=1)

        ttk.Label(
            card_tabela,
            text="RESULTADO DA VALIDAÇÃO",
            style="Documentos.Muted.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        # tksheet permite destacar células individuais, ao contrário do
        # ttk.Treeview, que aplica cores por linha inteira.
        self.tabela = Sheet(
            card_tabela,
            headers=[
                "Arquivo", "Data", "Descrição", "Valor",
                "Tipo de serviço", "Validação"
            ],
            data=[],
            show_x_scrollbar=True,
            show_y_scrollbar=True,
            height=300,
            width=1050,
        )
        self.tabela.enable_bindings((
            "single_select", "row_select", "column_select",
            "arrowkeys", "copy", "rc_select", "double_click_column_resize",
            "column_width_resize", "row_height_resize"
        ))
        self.ajustar_larguras_colunas([])
        self.tabela.set_all_row_heights(height=30)
        self.tabela.grid(row=1, column=0, sticky="nsew")

        # Resumo no rodapé
        self.label_resumo = ttk.Label(
            self,
            text="Nenhum arquivo analisado.",
            style="Documentos.Resumo.TLabel",
            anchor="w",
        )
        self.label_resumo.grid(row=3, column=0, sticky="ew")

    def ajustar_larguras_colunas(self, linhas):
        """Ajusta a largura de cada coluna conforme o conteúdo exibido.

        Há limites mínimos e máximos para evitar colunas muito estreitas
        ou que ocupem a janela inteira por causa de uma mensagem longa.
        """
        cabecalhos = [
            "Arquivo", "Data", "Descrição", "Valor",
            "Tipo de serviço", "Validação"
        ]
        larguras_minimas = [130, 100, 130, 100, 140, 180]
        larguras_maximas = [460, 170, 400, 160, 240, 520]
        larguras = []

        for indice, cabecalho in enumerate(cabecalhos):
            maior_tamanho = len(cabecalho)
            for linha in linhas:
                if indice < len(linha):
                    conteudo = "" if linha[indice] is None else str(linha[indice])
                    maior_tamanho = max(maior_tamanho, len(conteudo))

            # Aproximação de pixels por caractere, com espaço para margens.
            largura_calculada = maior_tamanho * 8 + 28
            largura = max(larguras_minimas[indice], largura_calculada)
            largura = min(larguras_maximas[indice], largura)
            larguras.append(largura)

        self.tabela.set_column_widths(larguras)

    def verificar_pasta(self):
        if not os.path.isdir(self.pasta_novos):
            try:
                os.makedirs(self.pasta_novos)
            except OSError as erro:
                messagebox.showerror(
                    "Erro",
                    "Não foi possível criar a pasta NOVOS:\n"
                    + str(erro)
                )

    def ler_arquivos(self):
        # Limpa os destaques anteriores antes de carregar a nova leitura.
        try:
            self.tabela.dehighlight_all(redraw=False)
        except (AttributeError, TypeError):
            pass
        self.tabela.set_sheet_data([])
        self.resultados = []

        if not os.path.isdir(self.pasta_novos):
            messagebox.showerror(
                "Pasta não encontrada",
                "A pasta NOVOS não existe:\n" + self.pasta_novos
            )
            return

        try:
            nomes = sorted(os.listdir(self.pasta_novos))
        except OSError as erro:
            messagebox.showerror(
                "Erro de leitura",
                "Não foi possível ler a pasta:\n" + str(erro)
            )
            return

        arquivos = []
        for nome in nomes:
            caminho = os.path.join(self.pasta_novos, nome)
            # Nesta etapa, analisamos apenas arquivos, não subpastas.
            if os.path.isfile(caminho):
                arquivos.append(nome)

        validos = 0
        invalidos = 0
        linhas_tabela = []
        celulas_com_erro_por_linha = []

        for nome in arquivos:
            resultado = interpretar_nome(nome)
            self.resultados.append(resultado)

            if resultado["status"] == "Válido":
                validos += 1
            else:
                invalidos += 1

            # Campos com erro ficam vazios na tabela. Os dados brutos continuam
            # disponíveis em resultado para compor a mensagem de validação.
            data_exibicao = (
                resultado["data"] if resultado.get("data_obj") is not None else ""
            )
            descricao_exibicao = resultado.get("descricao", "")
            valor_exibicao = (
                formatar_valor(resultado["valor"])
                if resultado.get("valor") not in ("", None) else ""
            )
            tipo_exibicao = resultado.get("tipo", "")

            mensagem_validacao = (
                "Válido" if resultado["status"] == "Válido"
                else resultado["erro"]
            )

            linhas_tabela.append([
                resultado["arquivo"],
                data_exibicao,
                descricao_exibicao,
                valor_exibicao,
                tipo_exibicao,
                mensagem_validacao,
            ])

            celulas_com_erro = []
            if resultado.get("data_obj") is None:
                celulas_com_erro.append(1)  # Data
            if not resultado.get("descricao"):
                celulas_com_erro.append(2)  # Descrição
            if resultado.get("valor") in ("", None):
                celulas_com_erro.append(3)  # Valor
            if not resultado.get("tipo"):
                celulas_com_erro.append(4)  # Tipo de serviço
            celulas_com_erro_por_linha.append(celulas_com_erro)

        self.tabela.set_sheet_data(linhas_tabela, reset_col_positions=True)
        self.ajustar_larguras_colunas(linhas_tabela)
        self.tabela.set_all_row_heights(height=30)

        # Arquivos válidos ficam com texto verde em todas as colunas.
        # Arquivos inválidos ficam com texto vermelho; apenas os campos
        # inválidos recebem também fundo vermelho-claro.
        for indice, resultado in enumerate(self.resultados):
            if resultado["status"] == "Válido":
                for coluna in range(6):
                    self.tabela.highlight_cells(
                        row=indice,
                        column=coluna,
                        fg="#008000",
                        redraw=False,
                    )
                continue

            for coluna in range(6):
                self.tabela.highlight_cells(
                    row=indice,
                    column=coluna,
                    fg="#C00000",
                    redraw=False,
                )

            for coluna in celulas_com_erro_por_linha[indice]:
                self.tabela.highlight_cells(
                    row=indice,
                    column=coluna,
                    bg="#FFD6D6",
                    fg="#C00000",
                    redraw=False,
                )

            # A mensagem explica o erro; permanece sem ocultar o motivo.
            self.tabela.highlight_cells(
                row=indice,
                column=5,
                bg="#FFF2CC",
                fg="#C00000",
                redraw=False,
            )

        self.tabela.refresh()
        self.label_resumo.config(
            text=(
                "Arquivos encontrados: {} | Válidos: {} | "
                "Com problemas: {}"
            ).format(len(arquivos), validos, invalidos)
        )

    def abrir_pasta(self):
        if not os.path.isdir(self.pasta_novos):
            self.verificar_pasta()

        try:
            os.startfile(self.pasta_novos)
        except Exception as erro:
            messagebox.showerror(
                "Erro",
                "Não foi possível abrir a pasta:\n" + str(erro)
            )

    
    def registrar_planilhas(self):
        if not self.resultados:
            messagebox.showwarning(
                "Atenção",
                "Clique primeiro em 'Ler pasta NOVOS'."
            )
            return

        pasta_modelo = os.path.join(
            self.pasta_aplicacao, "MODELO"
        )
        pasta_planilhas = os.path.join(
            self.pasta_aplicacao, "PLANILHAS"
        )

        if not os.path.isdir(pasta_modelo):
            messagebox.showerror(
                "Modelo não encontrado",
                "Crie a pasta MODELO e coloque nela a planilha original."
            )
            return

        modelos = [
            nome for nome in os.listdir(pasta_modelo)
            if nome.lower().endswith(".xlsx")
            and not nome.startswith("~$")
        ]

        if len(modelos) != 1:
            messagebox.showerror(
                "Modelo inválido",
                "A pasta MODELO deve conter exatamente um arquivo .xlsx."
            )
            return

        caminho_modelo = os.path.join(pasta_modelo, modelos[0])

        try:
            os.makedirs(pasta_planilhas, exist_ok=True)
        except OSError as erro:
            messagebox.showerror(
                "Erro",
                "Não foi possível criar PLANILHAS:\n" + str(erro)
            )
            return

        registrados = 0
        ignorados = 0
        arquivados = 0
        erros = []

        for resultado in self.resultados:
            # Arquivos inválidos permanecem em NOVOS para correção.
            if resultado["status"] != "Válido":
                continue

            nome_arquivo = resultado["arquivo"]
            caminho_origem = os.path.join(
                self.pasta_novos, nome_arquivo
            )

            # Evita tentar processar uma cópia que já foi movida
            # desde a última leitura da pasta.
            if not os.path.isfile(caminho_origem):
                erros.append(
                    "{}: o arquivo não foi encontrado na pasta NOVOS."
                    .format(nome_arquivo)
                )
                continue

            data = resultado["data_obj"]
            nome_planilha = nome_planilha_mensal(data, caminho_modelo)
            caminho_planilha = os.path.join(
                pasta_planilhas, nome_planilha
            )

            try:
                # Se ainda não existe, copia o modelo original.
                if not os.path.exists(caminho_planilha):
                    shutil.copy2(caminho_modelo, caminho_planilha)

                    wb = load_workbook(caminho_planilha)
                    try:
                        renomear_abas_mensais(wb, data)
                        wb.save(caminho_planilha)
                    finally:
                        wb.close()

                wb = load_workbook(caminho_planilha)
                situacao = "ignorado"

                try:
                    ws = localizar_aba(wb, resultado["tipo"])
                    situacao = inserir_lancamento(ws, resultado)

                    # Só consideramos registrado depois que save() termina.
                    if situacao == "registrado":
                        wb.save(caminho_planilha)
                finally:
                    wb.close()

                if situacao != "registrado":
                    # Por exemplo, quando o usuário recusa um lançamento
                    # possivelmente duplicado. O arquivo continua em NOVOS.
                    ignorados += 1
                    continue

                registrados += 1

                # Arquiva somente depois de salvar a planilha com sucesso.
                pasta_destino = os.path.join(
                    self.pasta_aplicacao,
                    resultado["tipo"],
                    str(data.year),
                    "{:02d}".format(data.month)
                )
                os.makedirs(pasta_destino, exist_ok=True)

                # Nunca sobrescreve outro arquivo com o mesmo nome.
                caminho_destino = os.path.join(
                    pasta_destino, nome_arquivo
                )
                if os.path.exists(caminho_destino):
                    base, extensao = os.path.splitext(nome_arquivo)
                    contador = 1
                    while True:
                        nome_alternativo = "{} ({}){}".format(
                            base, contador, extensao
                        )
                        caminho_destino = os.path.join(
                            pasta_destino, nome_alternativo
                        )
                        if not os.path.exists(caminho_destino):
                            break
                        contador += 1

                shutil.move(caminho_origem, caminho_destino)
                arquivados += 1

            except Exception as erro:
                # Em caso de erro, não tentamos remover o arquivo de NOVOS.
                erros.append(
                    "{}: {}".format(nome_arquivo, str(erro))
                )

        mensagem = (
            "Processamento concluído.\n\n"
            "Lançamentos registrados: {}\n"
            "Arquivos armazenados: {}\n"
            "Arquivos inválidos ou com falha permanecem em NOVOS."
        ).format(
            registrados, ignorados, arquivados, len(erros)
        )

        if erros:
            mensagem += "\n\nDetalhes:\n" + "\n".join(erros[:10])

        if len(erros) > 10:
            mensagem += "\n... e outros erros."

        messagebox.showinfo("Resultado", mensagem)

        # Atualiza a tabela para mostrar apenas o que ainda está em NOVOS.
        self.ler_arquivos()


MESES = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL",
    "MAIO", "JUNHO", "JULHO", "AGOSTO",
    "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]


def nome_planilha_mensal(data, caminho_modelo):
    nome_modelo = os.path.splitext(
        os.path.basename(caminho_modelo)
    )[0]

    return "{} {:02d} {}.xlsx".format(
        data.year, data.month, nome_modelo
    )


def localizar_aba(wb, tipo):
    for nome in wb.sheetnames:
        texto = normalizar_texto(nome)

        if tipo == "NÃO CONTÁBIL":
            if "NAO" in texto and "CONTABIL" in texto:
                return wb[nome]

        elif tipo == "CONTÁBIL":
            if "CONTABIL" in texto and "NAO" not in texto:
                return wb[nome]

        elif tipo == "AUDITORES":
            if "AUDITORES" in texto:
                return wb[nome]

    raise ValueError(
        "Não foi encontrada a aba do tipo: " + tipo
    )


def renomear_abas_mensais(wb, data):
    mes_ano = "{}-{:02d}".format(
        MESES[data.month - 1], data.year % 100
    )

    for nome_original in list(wb.sheetnames):
        texto = normalizar_texto(nome_original)

        if "NAO" in texto and "CONTABIL" in texto:
            sufixo = "NÃO-Contábil"
        elif "AUDITORES" in texto:
            sufixo = "Auditores"
        elif "CONTABIL" in texto:
            sufixo = "Contábil"
        else:
            continue

        wb[nome_original].title = "{} - {}".format(
            mes_ano, sufixo
        )


def valor_excel_para_decimal(valor):
    if valor is None or valor == "":
        return None

    try:
        return Decimal(str(valor)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None


def data_excel_para_data(valor):
    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, str):
        for formato in ("%d/%m/%Y", "%d.%m.%Y"):
            try:
                return datetime.strptime(
                    valor.strip(), formato
                ).date()
            except ValueError:
                pass

    return None


def encontrar_duplicidade(
    ws, data, descricao, valor, coluna_data, coluna_valor
):
    descricao_procurada = normalizar_texto(descricao)
    data_procurada = data.date()

    for linha in range(9, 39):
        descricao_existente = ws.cell(linha, 2).value
        data_existente = ws.cell(linha, coluna_data).value
        valor_existente = ws.cell(linha, coluna_valor).value

        if not descricao_existente:
            continue

        data_convertida = data_excel_para_data(data_existente)
        valor_convertido = valor_excel_para_decimal(
            valor_existente
        )

        if (
            normalizar_texto(str(descricao_existente))
            == descricao_procurada
            and data_convertida == data_procurada
            and valor_convertido
            == valor.quantize(Decimal("0.01"))
        ):
            return linha

    return None


def encontrar_linha_vazia(ws, coluna_valor):
    for linha in range(9, 39):
        descricao = ws.cell(linha, 2).value
        valor = ws.cell(linha, coluna_valor).value

        if descricao in (None, "") and valor in (None, ""):
            return linha

    return None


def inserir_lancamento(ws, resultado):
    tipo = resultado["tipo"]

    # Colunas variam conforme a aba do modelo.
    if tipo == "CONTÁBIL":
        coluna_data = 4
        coluna_valor = 5
    else:
        coluna_data = 3
        coluna_valor = 4

    data = resultado["data_obj"]
    descricao = resultado["descricao"]
    valor = resultado["valor"]

    duplicada = encontrar_duplicidade(
        ws, data, descricao, valor,
        coluna_data, coluna_valor
    )

    if duplicada is not None:
        continuar = messagebox.askyesno(
            "Possível duplicidade",
            "Já existe um lançamento semelhante na linha {}.\n\n"
            "Descrição: {}\nData: {}\nValor: {}\n\n"
            "Deseja registrar mesmo assim?".format(
                duplicada,
                descricao,
                data.strftime("%d/%m/%Y"),
                formatar_valor(valor)
            )
        )

        if not continuar:
            return "ignorado"

    linha = encontrar_linha_vazia(ws, coluna_valor)

    if linha is None:
        raise ValueError(
            "A aba está sem linhas disponíveis entre 9 e 38. "
            "O lançamento não foi registrado."
        )

    ws.cell(linha, 2).value = descricao

    celula_data = ws.cell(linha, coluna_data)
    celula_data.value = data
    celula_data.number_format = "dd/mm/yyyy"

    # Ajusta a largura para exibir a data e os valores completos.
    ws.column_dimensions[
        openpyxl.utils.get_column_letter(coluna_data)
    ].width = 16

    ws.column_dimensions[
        openpyxl.utils.get_column_letter(coluna_valor)
    ].width = 18

    celula_valor = ws.cell(linha, coluna_valor)
    celula_valor.value = float(valor)
    celula_valor.number_format = '"R$" #,##0.00'

    return "registrado"
