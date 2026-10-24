
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ctypes

class ListadorArquivos(ttk.Frame):

    def __init__(self, master, app):
        super().__init__(master)

        self.app = app
        self.configure(style="Listador.TFrame")
        self.configure(padding=0)

        self.pasta_selecionada = None
        self.arquivos_encontrados = []

        self.criar_interface()

    def criar_interface(self):
        """Monta a tela usando ttk e o mesmo padrão visual da aplicação."""
        estilo = ttk.Style(self)
        estilo.configure("Listador.TFrame", background="#F5F6F8")
        estilo.configure(
            "Listador.TLabel",
            background="#F5F6F8",
            foreground="#202938",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Listador.Titulo.TLabel",
            background="#F5F6F8",
            foreground="#202938",
            font=("Segoe UI", 15, "bold"),
        )
        estilo.configure(
            "Listador.Subtitulo.TLabel",
            background="#F5F6F8",
            foreground="#667085",
            font=("Segoe UI", 9),
        )
        estilo.configure(
            "Listador.Card.TFrame",
            background="#FFFFFF",
            relief="solid",
            borderwidth=1,
        )
        estilo.configure(
            "Listador.CardLabel.TLabel",
            background="#FFFFFF",
            foreground="#202938",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Listador.Muted.TLabel",
            background="#FFFFFF",
            foreground="#667085",
            font=("Segoe UI", 9),
        )
        estilo.configure(
            "Listador.Quantidade.TLabel",
            background="#EAF2FF",
            foreground="#175CD3",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 6),
        )
        estilo.configure(
            "Listador.Primary.TButton",
            font=("Segoe UI", 9, "bold"),
            padding=(12, 8),
        )
        estilo.configure(
            "Listador.TButton",
            font=("Segoe UI", 9),
            padding=(10, 8),
        )

        self.configure(style="Listador.TFrame", padding=(22, 16, 22, 18))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        # Cabeçalho e navegação
        cabecalho = ttk.Frame(self, style="Listador.TFrame")
        cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        cabecalho.columnconfigure(1, weight=1)

        ttk.Button(
            cabecalho,
            text="← Voltar ao menu",
            command=self.app.mostrar_menu,
            style="Listador.TButton",
        ).grid(row=0, column=0, sticky="w", padx=(0, 16))

        bloco_titulo = ttk.Frame(cabecalho, style="Listador.TFrame")
        bloco_titulo.grid(row=0, column=1, sticky="w")
        ttk.Label(
            bloco_titulo,
            text="Listador de Arquivos",
            style="Listador.Titulo.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            bloco_titulo,
            text="Consulte os arquivos de uma pasta e gere um relatório.",
            style="Listador.Subtitulo.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        # Cartão de seleção da pasta
        card_pasta = ttk.Frame(
            self, style="Listador.Card.TFrame", padding=14
        )
        card_pasta.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        card_pasta.columnconfigure(0, weight=1)

        ttk.Label(
            card_pasta,
            text="PASTA PARA ANALISAR",
            style="Listador.Muted.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        linha_pasta = ttk.Frame(card_pasta, style="Listador.Card.TFrame")
        linha_pasta.grid(row=1, column=0, sticky="ew")
        linha_pasta.columnconfigure(0, weight=1)

        self.label_pasta = ttk.Label(
            linha_pasta,
            text="Nenhuma pasta selecionada",
            style="Listador.CardLabel.TLabel",
            anchor="w",
        )
        self.label_pasta.grid(row=0, column=0, sticky="ew", padx=(0, 12), ipady=7)

        self.botao_pasta = ttk.Button(
            linha_pasta,
            text="Selecionar pasta…",
            command=self.selecionar_pasta,
            style="Listador.Primary.TButton",
        )
        self.botao_pasta.grid(row=0, column=1, sticky="e")

        # Opções e contador
        linha_opcoes = ttk.Frame(self, style="Listador.TFrame")
        linha_opcoes.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        linha_opcoes.columnconfigure(0, weight=1)

        self.incluir_subpastas = tk.BooleanVar(value=True)
        self.checkbox = ttk.Checkbutton(
            linha_opcoes,
            text="Incluir arquivos das subpastas",
            variable=self.incluir_subpastas,
            command=self.atualizar_lista,
        )
        self.checkbox.grid(row=0, column=0, sticky="w")

        self.label_quantidade = ttk.Label(
            linha_opcoes,
            text="Arquivos encontrados: 0",
            style="Listador.Quantidade.TLabel",
        )
        self.label_quantidade.grid(row=0, column=1, sticky="e")

        # Área de listagem
        card_lista = ttk.Frame(
            self, style="Listador.Card.TFrame", padding=10
        )
        card_lista.grid(row=3, column=0, sticky="nsew", pady=(0, 14))
        card_lista.columnconfigure(0, weight=1)
        card_lista.rowconfigure(1, weight=1)

        ttk.Label(
            card_lista,
            text="ARQUIVOS ENCONTRADOS",
            style="Listador.Muted.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        area_texto = ttk.Frame(card_lista, style="Listador.Card.TFrame")
        area_texto.grid(row=1, column=0, sticky="nsew")
        area_texto.columnconfigure(0, weight=1)
        area_texto.rowconfigure(0, weight=1)

        self.lista_arquivos = tk.Text(
            area_texto,
            font=("Consolas", 9),
            bg="#FFFFFF",
            fg="#344054",
            insertbackground="#175CD3",
            selectbackground="#D6E7FF",
            selectforeground="#202938",
            relief="flat",
            wrap="none",
            padx=10,
            pady=8,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#EAECF0",
            highlightcolor="#84ADFF",
            state="normal",
        )
        self.lista_arquivos.grid(row=0, column=0, sticky="nsew")

        scrollbar_y = ttk.Scrollbar(
            area_texto, orient="vertical", command=self.lista_arquivos.yview
        )
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x = ttk.Scrollbar(
            area_texto, orient="horizontal", command=self.lista_arquivos.xview
        )
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.lista_arquivos.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )

        # Ações no rodapé
        rodape = ttk.Frame(self, style="Listador.TFrame")
        rodape.grid(row=4, column=0, sticky="ew")
        for coluna in range(3):
            rodape.columnconfigure(coluna, weight=1, uniform="acoes")

        self.botao_atualizar = ttk.Button(
            rodape,
            text="Atualizar lista",
            command=self.atualizar_lista,
            style="Listador.TButton",
        )
        self.botao_atualizar.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.botao_txt = ttk.Button(
            rodape,
            text="Gerar arquivo TXT",
            command=self.gerar_txt,
            style="Listador.Primary.TButton",
        )
        self.botao_txt.grid(row=0, column=1, sticky="ew", padx=4)

        self.botao_imprimir = ttk.Button(
            rodape,
            text="Imprimir relatório",
            command=self.imprimir_relatorio,
            style="Listador.TButton",
        )
        self.botao_imprimir.grid(row=0, column=2, sticky="ew", padx=(8, 0))

    # -----------------------------
    # SELECIONAR PASTA
    # -----------------------------

    def selecionar_pasta(self):

        pasta = filedialog.askdirectory(
            parent=self.winfo_toplevel(),
            title="Selecione a pasta que deseja analisar"
        )

        if not pasta:
            return

        self.pasta_selecionada = pasta

        self.label_pasta.configure(
            text=pasta
        )

        self.atualizar_lista()

    # -----------------------------
    # ATUALIZAR LISTA
    # -----------------------------

    def atualizar_lista(self):

        if not self.pasta_selecionada:
            return

        self.arquivos_encontrados = []

        try:

            if self.incluir_subpastas.get():

                for raiz, diretorios, arquivos in os.walk(
                    self.pasta_selecionada
                ):

                    for nome in arquivos:

                        caminho = os.path.join(
                            raiz,
                            nome
                        )

                        self.arquivos_encontrados.append(
                            caminho
                        )

            else:

                for nome in os.listdir(
                    self.pasta_selecionada
                ):

                    caminho = os.path.join(
                        self.pasta_selecionada,
                        nome
                    )

                    if os.path.isfile(caminho):

                        self.arquivos_encontrados.append(
                            caminho
                        )

            self.arquivos_encontrados.sort(
                key=lambda x: x.lower()
            )

            self.lista_arquivos.delete(
                "1.0",
                tk.END
            )

            for caminho in self.arquivos_encontrados:

                caminho_relativo = os.path.relpath(
                    caminho,
                    self.pasta_selecionada
                )

                self.lista_arquivos.insert(
                    tk.END,
                    caminho_relativo + "\n"
                )

            quantidade = len(
                self.arquivos_encontrados
            )

            self.label_quantidade.configure(
                text=f"Arquivos encontrados: {quantidade}"
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                f"Não foi possível ler a pasta.\n\n{erro}"
            )

    # -----------------------------
    # CRIAR CONTEÚDO DO RELATÓRIO
    # -----------------------------

    def criar_conteudo_relatorio(self):

        conteudo = []

        conteudo.append(
            "RELATÓRIO DE ARQUIVOS"
        )

        conteudo.append(
            "=" * 50
        )

        conteudo.append("")

        conteudo.append(
            "Pasta analisada:"
        )

        conteudo.append(
            self.pasta_selecionada
        )

        conteudo.append("")

        conteudo.append(
            "ARQUIVOS ENCONTRADOS:"
        )

        conteudo.append(
            "-" * 50
        )

        for caminho in self.arquivos_encontrados:

            caminho_relativo = os.path.relpath(
                caminho,
                self.pasta_selecionada
            )

            conteudo.append(
                caminho_relativo
            )

        conteudo.append("")

        conteudo.append(
            "=" * 50
        )

        conteudo.append(
            "Quantidade total de arquivos encontrados: "
            f"{len(self.arquivos_encontrados)}"
        )

        return "\n".join(conteudo)

    # -----------------------------
    # GERAR TXT
    # -----------------------------

    def gerar_txt(self):

        if not self.pasta_selecionada:

            messagebox.showwarning(
                "Atenção",
                "Selecione uma pasta antes de gerar o relatório."
            )

            return

        if not self.arquivos_encontrados:

            messagebox.showwarning(
                "Atenção",
                "Nenhum arquivo foi encontrado."
            )

            return

        caminho_saida = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            title="Salvar relatório",
            defaultextension=".txt",
            initialfile="relatorio_arquivos.txt",
            filetypes=[
                ("Arquivo de texto", "*.txt")
            ]
        )

        if not caminho_saida:
            return

        try:

            conteudo = self.criar_conteudo_relatorio()

            with open(
                caminho_saida,
                "w",
                encoding="utf-8"
            ) as arquivo_txt:

                arquivo_txt.write(
                    conteudo
                )

            messagebox.showinfo(
                "Sucesso",
                "Relatório gerado com sucesso!"
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                f"Não foi possível salvar o relatório.\n\n{erro}"
            )

    # -----------------------------
    # IMPRIMIR RELATÓRIO
    # -----------------------------


    def imprimir_relatorio(self):

        if not self.pasta_selecionada:

            messagebox.showwarning(
                "Atenção",
                "Selecione uma pasta antes de imprimir o relatório."
            )

            return

        if not self.arquivos_encontrados:

            messagebox.showwarning(
                "Atenção",
                "Nenhum arquivo foi encontrado."
            )

            return

        try:

            # -------------------------------------------------
            # O conteúdo é exatamente o mesmo do arquivo TXT
            # -------------------------------------------------

            conteudo = self.criar_conteudo_relatorio()

            # Divide o relatório em linhas
            linhas = conteudo.splitlines()

            # -------------------------------------------------
            # Estrutura PRINTDLG do Windows
            # -------------------------------------------------

            class PRINTDLG(ctypes.Structure):

                _fields_ = [
                    ("lStructSize", ctypes.c_uint32),
                    ("hwndOwner", ctypes.c_void_p),
                    ("hDevMode", ctypes.c_void_p),
                    ("hDevNames", ctypes.c_void_p),
                    ("hDC", ctypes.c_void_p),
                    ("Flags", ctypes.c_uint32),
                    ("nFromPage", ctypes.c_uint16),
                    ("nToPage", ctypes.c_uint16),
                    ("nMinPage", ctypes.c_uint16),
                    ("nMaxPage", ctypes.c_uint16),
                    ("nCopies", ctypes.c_uint16),
                    ("hInstance", ctypes.c_void_p),
                    ("lCustData", ctypes.c_void_p),
                    ("lpfnPrintHook", ctypes.c_void_p),
                    ("lpfnSetupHook", ctypes.c_void_p),
                    ("lpPrintTemplateName", ctypes.c_wchar_p),
                    ("lpSetupTemplateName", ctypes.c_wchar_p),
                    ("hPrintTemplate", ctypes.c_void_p),
                    ("hSetupTemplate", ctypes.c_void_p),
                ]

            # -------------------------------------------------
            # Abre a janela nativa de impressão do Windows
            # -------------------------------------------------

            print_dlg = PRINTDLG()

            print_dlg.lStructSize = ctypes.sizeof(PRINTDLG)

            print_dlg.hwndOwner = self.winfo_toplevel().winfo_id()

            # PD_RETURNDC
            # Retorna o Device Context da impressora selecionada.
            print_dlg.Flags = 0x00000100

            print_dlg.nFromPage = 1
            print_dlg.nToPage = 1
            print_dlg.nMinPage = 1
            print_dlg.nMaxPage = 65535
            print_dlg.nCopies = 1

            comdlg32 = ctypes.windll.comdlg32

            resultado = comdlg32.PrintDlgW(
                ctypes.byref(print_dlg)
            )

            # -------------------------------------------------
            # Usuário cancelou a impressão
            # -------------------------------------------------

            if not resultado:

                return

            hdc = print_dlg.hDC

            if not hdc:

                messagebox.showerror(
                    "Erro",
                    "Não foi possível obter a impressora selecionada."
                )

                return

            # -------------------------------------------------
            # Configuração da impressão
            # -------------------------------------------------

            gdi32 = ctypes.windll.gdi32

            class DOCINFO(ctypes.Structure):

                _fields_ = [
                    ("cbSize", ctypes.c_int),
                    ("lpszDocName", ctypes.c_wchar_p),
                    ("lpszOutput", ctypes.c_wchar_p),
                    ("lpszDatatype", ctypes.c_wchar_p),
                    ("fwType", ctypes.c_uint32),
                ]

            doc_info = DOCINFO()

            doc_info.cbSize = ctypes.sizeof(DOCINFO)

            doc_info.lpszDocName = "Relatório de Arquivos"

            # -------------------------------------------------
            # Inicia o documento
            # -------------------------------------------------

            if gdi32.StartDocW(
                hdc,
                ctypes.byref(doc_info)
            ) <= 0:

                gdi32.DeleteDC(hdc)

                messagebox.showerror(
                    "Erro",
                    "Não foi possível iniciar a impressão."
                )

                return

            # -------------------------------------------------
            # Configurações da página
            # -------------------------------------------------

            # DPI da impressora
            dpi_x = gdi32.GetDeviceCaps(
                hdc,
                88
            )

            dpi_y = gdi32.GetDeviceCaps(
                hdc,
                90
            )

            # Área imprimível
            largura_pagina = gdi32.GetDeviceCaps(
                hdc,
                8
            )

            altura_pagina = gdi32.GetDeviceCaps(
                hdc,
                10
            )

            # Margens aproximadas
            margem_esquerda = int(
                dpi_x * 0.7
            )

            margem_superior = int(
                dpi_y * 0.7
            )

            # -------------------------------------------------
            # Criação da fonte
            # -------------------------------------------------

            class LOGFONTW(ctypes.Structure):

                _fields_ = [
                    ("lfHeight", ctypes.c_long),
                    ("lfWidth", ctypes.c_long),
                    ("lfEscapement", ctypes.c_long),
                    ("lfOrientation", ctypes.c_long),
                    ("lfWeight", ctypes.c_long),
                    ("lfItalic", ctypes.c_ubyte),
                    ("lfUnderline", ctypes.c_ubyte),
                    ("lfStrikeOut", ctypes.c_ubyte),
                    ("lfCharSet", ctypes.c_ubyte),
                    ("lfOutPrecision", ctypes.c_ubyte),
                    ("lfClipPrecision", ctypes.c_ubyte),
                    ("lfQuality", ctypes.c_ubyte),
                    ("lfPitchAndFamily", ctypes.c_ubyte),
                    ("lfFaceName", ctypes.c_wchar * 32),
                ]

            fonte = LOGFONTW()

            # Aproximadamente 10 pontos
            fonte.lfHeight = -int(
                dpi_y * 10 / 72
            )

            fonte.lfWidth = 0
            fonte.lfWeight = 400

            # Fonte monoespaçada para manter
            # o relatório visualmente semelhante ao TXT
            fonte.lfPitchAndFamily = 0x31

            fonte.lfFaceName = "Consolas"

            hfonte = gdi32.CreateFontIndirectW(
                ctypes.byref(fonte)
            )

            if not hfonte:

                gdi32.AbortDoc(hdc)
                gdi32.DeleteDC(hdc)

                messagebox.showerror(
                    "Erro",
                    "Não foi possível criar a fonte para impressão."
                )

                return

            fonte_anterior = gdi32.SelectObject(
                hdc,
                hfonte
            )

            # -------------------------------------------------
            # Tamanho da linha
            # -------------------------------------------------

            tamanho_texto = ctypes.create_unicode_buffer(
                "Ag"
            )

            class SIZE(ctypes.Structure):

                _fields_ = [
                    ("cx", ctypes.c_long),
                    ("cy", ctypes.c_long),
                ]

            tamanho = SIZE()

            gdi32.GetTextExtentPoint32W(
                hdc,
                tamanho_texto,
                2,
                ctypes.byref(tamanho)
            )

            altura_linha = tamanho.cy + 4

            # -------------------------------------------------
            # Número aproximado de linhas por página
            # -------------------------------------------------

            linhas_por_pagina = int(
                (
                    altura_pagina
                    - margem_superior
                    - int(dpi_y * 0.7)
                )
                / altura_linha
            )

            if linhas_por_pagina < 1:

                linhas_por_pagina = 1

            # -------------------------------------------------
            # Impressão
            # -------------------------------------------------

            pagina_aberta = False
            linha_atual = 0

            try:

                while linha_atual < len(linhas):

                    # Nova página
                    if not pagina_aberta:

                        if gdi32.StartPage(hdc) <= 0:

                            raise Exception(
                                "Não foi possível iniciar a página."
                            )

                        pagina_aberta = True

                    y = margem_superior

                    linhas_impressas = 0

                    while (
                        linha_atual < len(linhas)
                        and linhas_impressas < linhas_por_pagina
                    ):

                        linha = linhas[linha_atual]

                        # Mantém linhas vazias do relatório
                        if linha:

                            gdi32.TextOutW(
                                hdc,
                                margem_esquerda,
                                y,
                                linha,
                                len(linha)
                            )

                        y += altura_linha

                        linha_atual += 1
                        linhas_impressas += 1

                    # Finaliza página
                    if gdi32.EndPage(hdc) <= 0:

                        raise Exception(
                            "Não foi possível finalizar a página."
                        )

                    pagina_aberta = False

                # Finaliza documento
                gdi32.EndDoc(hdc)

            except Exception as erro:

                if pagina_aberta:

                    try:
                        gdi32.AbortPage(hdc)
                    except:
                        pass

                gdi32.AbortDoc(hdc)

                raise erro

            finally:

                # Restaura fonte
                if fonte_anterior:

                    gdi32.SelectObject(
                        hdc,
                        fonte_anterior
                    )

                if hfonte:

                    gdi32.DeleteObject(
                        hfonte
                    )

                gdi32.DeleteDC(
                    hdc
                )

            messagebox.showinfo(
                "Impressão",
                "Relatório enviado para a impressora."
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro de impressão",
                f"Não foi possível imprimir o relatório.\n\n{erro}"
            )
