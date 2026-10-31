import os
import re
import sys
import zipfile
import tkinter as tk
from tkinter import ttk, messagebox


TIPOS_DOCUMENTOS = ("CONTÁBIL", "NÃO CONTÁBIL", "AUDITORES")


def obter_pasta_aplicacao():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def identificar_ano_mes(nome_planilha):
    """
    Espera nomes no padrão utilizado pelo DocManager:
    AAAA MM Nome da planilha.xlsx
    """
    nome = os.path.splitext(os.path.basename(nome_planilha))[0]
    correspondencia = re.match(r"^\s*(\d{4})\s+(\d{1,2})(?:\s+|$)", nome)

    if not correspondencia:
        return None

    ano = int(correspondencia.group(1))
    mes = int(correspondencia.group(2))

    if not 1 <= mes <= 12:
        return None

    return ano, mes


class CompactadorDocumentos(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.pasta_aplicacao = obter_pasta_aplicacao()
        self.pasta_planilhas = os.path.join(self.pasta_aplicacao, "PLANILHAS")
        self.pasta_fechamentos = os.path.join(self.pasta_aplicacao, "FECHAMENTOS")

        self.criar_interface()
        self.carregar_planilhas()

    def criar_interface(self):
        estilo = ttk.Style(self)
        estilo.configure("Compactador.TFrame", background="#F5F6F8")
        estilo.configure(
            "Compactador.Titulo.TLabel",
            background="#F5F6F8",
            foreground="#202938",
            font=("Segoe UI", 15, "bold"),
        )
        estilo.configure(
            "Compactador.Subtitulo.TLabel",
            background="#F5F6F8",
            foreground="#667085",
            font=("Segoe UI", 9),
        )
        estilo.configure(
            "Compactador.Card.TFrame",
            background="#FFFFFF",
            relief="solid",
            borderwidth=1,
        )
        estilo.configure(
            "Compactador.Primary.TButton",
            font=("Segoe UI", 9, "bold"),
            padding=(12, 8),
        )
        estilo.configure(
            "Compactador.TButton",
            font=("Segoe UI", 9),
            padding=(10, 8),
        )

        self.configure(style="Compactador.TFrame", padding=(22, 16, 22, 18))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        cabecalho = ttk.Frame(self, style="Compactador.TFrame")
        cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        cabecalho.columnconfigure(1, weight=1)

        ttk.Button(
            cabecalho,
            text="← Voltar ao menu",
            command=self.app.mostrar_menu,
            style="Compactador.TButton",
        ).grid(row=0, column=0, sticky="w", padx=(0, 16))

        bloco_titulo = ttk.Frame(cabecalho, style="Compactador.TFrame")
        bloco_titulo.grid(row=0, column=1, sticky="w")

        ttk.Label(
            bloco_titulo,
            text="Fechamento mensal",
            style="Compactador.Titulo.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            bloco_titulo,
            text="Selecione uma planilha para reunir o arquivo Excel e seus documentos em um ZIP.",
            style="Compactador.Subtitulo.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        card = ttk.Frame(self, style="Compactador.Card.TFrame", padding=14)
        card.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)

        ttk.Label(
            card,
            text="PLANILHAS DISPONÍVEIS",
            background="#FFFFFF",
            foreground="#667085",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        area_tabela = ttk.Frame(card)
        area_tabela.grid(row=1, column=0, sticky="nsew")
        area_tabela.columnconfigure(0, weight=1)
        area_tabela.rowconfigure(0, weight=1)

        self.tabela = ttk.Treeview(
            area_tabela,
            columns=("planilha", "periodo", "status"),
            show="headings",
            selectmode="browse",
            height=12,
        )
        self.tabela.heading("planilha", text="Nome da planilha")
        self.tabela.heading("periodo", text="Período")
        self.tabela.heading("status", text="Status do fechamento")
        self.tabela.column("planilha", width=540, anchor="w")
        self.tabela.column("periodo", width=110, anchor="center")
        self.tabela.column("status", width=180, anchor="center")
        self.tabela.tag_configure("existente", foreground="#16803C")
        self.tabela.tag_configure("inexistente", foreground="#667085")
        self.tabela.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(
            area_tabela, orient="vertical", command=self.tabela.yview
        )
        barra.grid(row=0, column=1, sticky="ns")
        self.tabela.configure(yscrollcommand=barra.set)

        botoes = ttk.Frame(card)
        botoes.grid(row=2, column=0, sticky="ew", pady=(12, 0))

        ttk.Button(
            botoes,
            text="Atualizar lista",
            command=self.carregar_planilhas,
            style="Compactador.TButton",
        ).pack(side="left")

        ttk.Button(
            botoes,
            text="Abrir pasta Fechamentos",
            command=self.abrir_pasta_fechamentos,
            style="Compactador.TButton",
        ).pack(side="left", padx=8)

        ttk.Button(
            botoes,
            text="Criar / atualizar fechamento",
            command=self.compactar_selecionada,
            style="Compactador.Primary.TButton",
        ).pack(side="right")

        rodape = ttk.Frame(self, style="Compactador.TFrame")
        rodape.grid(row=2, column=0, sticky="ew")
        rodape.columnconfigure(0, weight=1)

        self.label_status = ttk.Label(
            rodape,
            text="Selecione uma planilha para iniciar.",
            style="Compactador.Subtitulo.TLabel",
        )
        self.label_status.grid(row=0, column=0, sticky="w")

    def carregar_planilhas(self):
        self.tabela.delete(*self.tabela.get_children())

        if not os.path.isdir(self.pasta_planilhas):
            self.label_status.config(
                text="A pasta PLANILHAS ainda não existe."
            )
            return

        try:
            nomes = sorted(
                nome
                for nome in os.listdir(self.pasta_planilhas)
                if nome.lower().endswith(".xlsx")
                and not nome.startswith("~$")
                and os.path.isfile(os.path.join(self.pasta_planilhas, nome))
            )
        except OSError as erro:
            messagebox.showerror(
                "Erro",
                "Não foi possível consultar PLANILHAS:\n{}".format(erro),
            )
            return

        adicionadas = 0
        for nome in nomes:
            periodo = identificar_ano_mes(nome)
            if periodo is None:
                periodo_texto = "Nome fora do padrão"
            else:
                periodo_texto = "{:02d}/{}".format(periodo[1], periodo[0])

            status = self.obter_status_fechamento(periodo)
            tag = "existente" if status == "Já existe" else "inexistente"
            self.tabela.insert(
                "", "end", values=(nome, periodo_texto, status), tags=(tag,)
            )
            adicionadas += 1

        self.label_status.config(
            text="{} planilha(s) encontrada(s).".format(adicionadas)
        )

    def obter_caminho_zip(self, periodo):
        if periodo is None:
            return None
        ano, mes = periodo
        nome_zip = "{:04d} {:02d} Fechamento Campos e Associados.zip".format(
            ano, mes
        )
        return os.path.join(self.pasta_fechamentos, nome_zip)

    def obter_status_fechamento(self, periodo):
        caminho_zip = self.obter_caminho_zip(periodo)
        if caminho_zip and os.path.isfile(caminho_zip):
            return "Já existe"
        return "Não existe"

    def compactar_selecionada(self):
        selecionados = self.tabela.selection()
        if not selecionados:
            messagebox.showwarning(
                "Seleção necessária",
                "Selecione uma planilha antes de compactar.",
            )
            return

        valores = self.tabela.item(selecionados[0], "values")
        nome_planilha = valores[0]
        periodo = identificar_ano_mes(nome_planilha)

        if periodo is None:
            messagebox.showerror(
                "Nome de planilha inválido",
                "Não foi possível identificar o ano e o mês pelo nome:\n\n"
                "{}\n\nO padrão esperado é AAAA MM Nome.xlsx.".format(
                    nome_planilha
                ),
            )
            return

        ano, mes = periodo
        caminho_planilha = os.path.join(self.pasta_planilhas, nome_planilha)

        try:
            os.makedirs(self.pasta_fechamentos, exist_ok=True)
        except OSError as erro:
            messagebox.showerror(
                "Erro",
                "Não foi possível criar a pasta Fechamentos:\n{}".format(erro),
            )
            return

        nome_zip = "{:04d} {:02d} Fechamento Campos e Associados.zip".format(
            ano, mes
        )
        caminho_zip = self.obter_caminho_zip(periodo)
        caminho_zip_temporario = caminho_zip + ".tmp"
        fechamento_existente = os.path.isfile(caminho_zip)

        if fechamento_existente:
            substituir = messagebox.askyesno(
                "Fechamento já existe",
                "Já existe um fechamento para {:02d}/{}:\n\n{}\n\n"
                "Deseja ATUALIZAR esse fechamento com os arquivos atuais?".format(
                    mes, ano, nome_zip
                ),
            )
            if not substituir:
                return

        arquivos_adicionados = 0
        documentos_por_tipo = {tipo: 0 for tipo in TIPOS_DOCUMENTOS}

        try:
            with zipfile.ZipFile(
                caminho_zip_temporario,
                mode="w",
                compression=zipfile.ZIP_DEFLATED,
            ) as arquivo_zip:
                # A planilha fica na raiz do ZIP.
                arquivo_zip.write(caminho_planilha, arcname=nome_planilha)
                arquivos_adicionados += 1

                # Reproduz dentro do ZIP a organização de pastas do sistema.
                for tipo in TIPOS_DOCUMENTOS:
                    pasta_mes = os.path.join(
                        self.pasta_aplicacao,
                        tipo,
                        str(ano),
                        "{:02d}".format(mes),
                    )

                    if not os.path.isdir(pasta_mes):
                        continue

                    for nome in sorted(os.listdir(pasta_mes)):
                        caminho_documento = os.path.join(pasta_mes, nome)
                        if not os.path.isfile(caminho_documento):
                            continue

                        caminho_relativo = os.path.join(
                            tipo, str(ano), "{:02d}".format(mes), nome
                        )
                        arquivo_zip.write(
                            caminho_documento,
                            arcname=caminho_relativo.replace(os.sep, "/"),
                        )
                        arquivos_adicionados += 1
                        documentos_por_tipo[tipo] += 1

            # Só substitui o fechamento anterior depois que o novo ZIP foi
            # criado por completo. Em caso de falha, o arquivo antigo permanece.
            os.replace(caminho_zip_temporario, caminho_zip)

        except (OSError, zipfile.BadZipFile, RuntimeError) as erro:
            try:
                if os.path.exists(caminho_zip_temporario):
                    os.remove(caminho_zip_temporario)
            except OSError:
                pass

            messagebox.showerror(
                "Erro na compactação",
                "Não foi possível criar o fechamento:\n{}".format(erro),
            )
            return

        total_documentos = sum(documentos_por_tipo.values())
        resumo = (
            "Fechamento criado com sucesso!\n\n"
            "Arquivo: {}\n"
            "Local: {}\n\n"
            "Planilha: 1\n"
            "Documentos CONTÁBEIS: {}\n"
            "Documentos NÃO CONTÁBEIS: {}\n"
            "Documentos AUDITORES: {}\n"
            "Total de arquivos no ZIP: {}"
        ).format(
            nome_zip,
            self.pasta_fechamentos,
            documentos_por_tipo["CONTÁBIL"],
            documentos_por_tipo["NÃO CONTÁBIL"],
            documentos_por_tipo["AUDITORES"],
            arquivos_adicionados,
        )

        if total_documentos == 0:
            resumo += (
                "\n\nAtenção: nenhuma pasta de documentos continha arquivos "
                "para este mês. O ZIP contém somente a planilha."
            )

        self.carregar_planilhas()
        self.label_status.config(
            text="Último fechamento {}: {}".format(
                "atualizado" if fechamento_existente else "criado", nome_zip
            )
        )
        messagebox.showinfo(
            "Fechamento atualizado" if fechamento_existente else "Compactação concluída",
            resumo.replace(
                "Fechamento criado com sucesso!",
                "Fechamento atualizado com sucesso!"
                if fechamento_existente
                else "Fechamento criado com sucesso!",
                1,
            ),
        )

    def abrir_pasta_fechamentos(self):
        os.makedirs(self.pasta_fechamentos, exist_ok=True)
        try:
            os.startfile(self.pasta_fechamentos)
        except AttributeError:
            messagebox.showerror(
                "Não disponível",
                "A abertura automática da pasta está disponível no Windows.",
            )
        except OSError as erro:
            messagebox.showerror(
                "Erro",
                "Não foi possível abrir a pasta:\n{}".format(erro),
            )
