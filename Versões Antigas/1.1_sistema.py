
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
    Espera o padrão:
    dd.mm.aa descrição (valor) tipo de serviço.extensão

    Não abre nem modifica o arquivo.
    """
    nome_sem_extensao = os.path.splitext(nome_arquivo)[0]

    # Localiza o valor entre parênteses e o tipo no final.
    padrao_final = (
        r"\(\s*([^()]*)\s*\)\s*"
        r"(não\s+contábil|nao\s+contabil|"
        r"contábil|contabil|auditores)\s*$"
    )

    correspondencia = re.search(
        padrao_final,
        nome_sem_extensao,
        flags=re.IGNORECASE
    )

    if not correspondencia:
        raise ValueError(
            "Não foi encontrado o valor entre parênteses "
            "seguido de um tipo de serviço válido."
        )

    valor_texto = correspondencia.group(1).strip()
    tipo_original = correspondencia.group(2).strip()

    # O conteúdo anterior ao valor contém a data e a descrição.
    parte_inicial = nome_sem_extensao[:correspondencia.start()].strip()

    padrao_inicial = r"^(\d{2}\.\d{2}\.\d{2})\s+(.+?)\s*$"

    inicio = re.match(padrao_inicial, parte_inicial)

    if not inicio:
        raise ValueError(
            "O nome deve começar com a data no formato dd.mm.aa "
            "e depois conter a descrição."
        )

    data_texto = inicio.group(1)
    descricao = inicio.group(2).strip()

    if not descricao:
        raise ValueError("A descrição está vazia.")

    try:
        data = datetime.strptime(data_texto, "%d.%m.%y")
    except ValueError:
        raise ValueError("A data informada não é válida.")

    valor = converter_valor(valor_texto)

    tipo_normalizado = normalizar_texto(tipo_original)
    tipo = TIPOS_SERVICO.get(tipo_normalizado)

    if tipo is None:
        raise ValueError("Tipo de serviço não reconhecido.")

    return {
        "arquivo": nome_arquivo,
        "data": data.strftime("%d/%m/%Y"),
        "data_obj": data,
        "descricao": descricao,
        "valor": valor,
        "tipo": tipo,
        "status": "Válido",
        "erro": "",
    }


class SistemaDocumentos:

    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Sistema de Documentos - Validação")
        self.janela.geometry("1100x600")
        self.janela.minsize(850, 400)

        self.pasta_aplicacao = obter_pasta_aplicacao()
        self.pasta_novos = os.path.join(
            self.pasta_aplicacao, "NOVOS"
        )

        self.resultados = []

        self.criar_interface()
        self.verificar_pasta()

    def criar_interface(self):
        topo = ttk.Frame(self.janela, padding=10)
        topo.pack(fill="x")

        ttk.Label(
            topo,
            text="Validação de documentos",
            font=("Arial", 15, "bold")
        ).pack(anchor="w")

        ttk.Label(
            topo,
            text=(
                "Esta etapa apenas lê os nomes dos arquivos. "
                "Nenhum documento será movido ou alterado."
            )
        ).pack(anchor="w", pady=(5, 10))

        botoes = ttk.Frame(topo)
        botoes.pack(fill="x")

        ttk.Button(
            botoes,
            text="Ler pasta NOVOS",
            command=self.ler_arquivos
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            botoes,
            text="Abrir pasta NOVOS",
            command=self.abrir_pasta
        ).pack(side="left")

        ttk.Button(
            botoes,
            text="Registrar na planilha",
            command=self.registrar_planilhas
        ).pack(side="left", padx=(8, 0))

        self.label_pasta = ttk.Label(
            topo,
            text="Pasta: " + self.pasta_novos
        )
        self.label_pasta.pack(anchor="w", pady=(8, 0))

        quadro = ttk.Frame(self.janela, padding=(10, 0, 10, 10))
        quadro.pack(fill="both", expand=True)

        colunas = (
            "arquivo",
            "data",
            "descricao",
            "valor",
            "tipo",
            "status",
        )

        self.tabela = ttk.Treeview(
            quadro,
            columns=colunas,
            show="headings",
            height=15
        )

        configuracoes = {
            "arquivo": ("Arquivo", 250),
            "data": ("Data", 95),
            "descricao": ("Descrição", 220),
            "valor": ("Valor", 100),
            "tipo": ("Tipo de serviço", 130),
            "status": ("Validação", 250),
        }

        for coluna, (titulo, largura) in configuracoes.items():
            self.tabela.heading(coluna, text=titulo)
            self.tabela.column(
                coluna,
                width=largura,
                minwidth=70,
                anchor="w"
            )

        barra_vertical = ttk.Scrollbar(
            quadro,
            orient="vertical",
            command=self.tabela.yview
        )

        barra_horizontal = ttk.Scrollbar(
            quadro,
            orient="horizontal",
            command=self.tabela.xview
        )

        self.tabela.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set
        )

        self.tabela.grid(row=0, column=0, sticky="nsew")
        barra_vertical.grid(row=0, column=1, sticky="ns")
        barra_horizontal.grid(row=1, column=0, sticky="ew")

        quadro.rowconfigure(0, weight=1)
        quadro.columnconfigure(0, weight=1)

        self.tabela.tag_configure(
            "valido",
            foreground="green"
        )

        self.tabela.tag_configure(
            "erro",
            foreground="red"
        )

        rodape = ttk.Frame(self.janela, padding=(10, 0, 10, 10))
        rodape.pack(fill="x")

        self.label_resumo = ttk.Label(
            rodape,
            text="Nenhum arquivo analisado."
        )
        self.label_resumo.pack(anchor="w")

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
        self.tabela.delete(*self.tabela.get_children())
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

        for nome in arquivos:
            try:
                resultado = interpretar_nome(nome)
                validos += 1

                valores = (
                    resultado["arquivo"],
                    resultado["data"],
                    resultado["descricao"],
                    formatar_valor(resultado["valor"]),
                    resultado["tipo"],
                    resultado["status"],
                )

                tag = "valido"

            except ValueError as erro:
                resultado = {
                    "arquivo": nome,
                    "data": "",
                    "descricao": "",
                    "valor": "",
                    "tipo": "",
                    "status": "Inválido",
                    "erro": str(erro),
                }

                invalidos += 1

                valores = (
                    nome,
                    "",
                    "",
                    "",
                    "",
                    str(erro),
                )

                tag = "erro"

            self.resultados.append(resultado)

            self.tabela.insert(
                "",
                "end",
                values=valores,
                tags=(tag,)
            )

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
            if not os.path.isdir(pasta_planilhas):
                os.makedirs(pasta_planilhas)
        except OSError as erro:
            messagebox.showerror(
                "Erro",
                "Não foi possível criar PLANILHAS:\n" + str(erro)
            )
            return

        registrados = 0
        ignorados = 0
        erros = []

        for resultado in self.resultados:
            if resultado["status"] != "Válido":
                continue

            data = resultado["data_obj"]
            nome_planilha = nome_planilha_mensal(data)
            caminho_planilha = os.path.join(
                pasta_planilhas, nome_planilha
            )

            try:
                # Se ainda não existe, copia o modelo original.
                if not os.path.exists(caminho_planilha):
                    shutil.copy2(caminho_modelo, caminho_planilha)

                    wb = load_workbook(caminho_planilha)
                    renomear_abas_mensais(wb, data)
                    wb.save(caminho_planilha)
                    wb.close()

                wb = load_workbook(caminho_planilha)

                try:
                    ws = localizar_aba(wb, resultado["tipo"])

                    situacao = inserir_lancamento(
                        ws, resultado
                    )

                    if situacao == "registrado":
                        wb.save(caminho_planilha)
                        registrados += 1
                    else:
                        ignorados += 1

                finally:
                    wb.close()

            except Exception as erro:
                erros.append(
                    "{}: {}".format(
                        resultado["arquivo"], str(erro)
                    )
                )

        mensagem = (
            "Processamento das planilhas concluído.\n\n"
            "Lançamentos registrados: {}\n"
            "Lançamentos ignorados: {}\n"
            "Arquivos com erro: {}"
        ).format(registrados, ignorados, len(erros))

        if erros:
            mensagem += "\n\nDetalhes:\n" + "\n".join(erros[:10])

        if len(erros) > 10:
            mensagem += "\n... e outros erros."

        messagebox.showinfo("Resultado", mensagem)


MESES = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL",
    "MAIO", "JUNHO", "JULHO", "AGOSTO",
    "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]


def nome_planilha_mensal(data):
    return "{} {:02d} DESPESAS CAMPOS ASSOCIADOS.xlsx".format(
        data.year, data.month
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


if __name__ == "__main__":
    janela = tk.Tk()
    aplicativo = SistemaDocumentos(janela)
    janela.mainloop()
