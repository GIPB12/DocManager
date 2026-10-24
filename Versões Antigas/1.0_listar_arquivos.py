
import os
import subprocess
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
import ctypes

class ListadorArquivos:

    def __init__(self, janela):

        self.janela = janela
        self.janela.title("Listador de Arquivos")
        self.janela.geometry("760x580")
        self.janela.resizable(False, False)
        self.janela.configure(bg="#f2f2f2")

        self.pasta_selecionada = None
        self.arquivos_encontrados = []

        self.criar_interface()

    def criar_interface(self):

        titulo = tk.Label(
            self.janela,
            text="Listador de Arquivos",
            font=("Arial", 20, "bold"),
            bg="#f2f2f2",
            fg="#222222"
        )
        titulo.place(x=0, y=25, width=760, height=30)

        subtitulo = tk.Label(
            self.janela,
            text="Selecione uma pasta e gere um relatório em TXT.",
            font=("Arial", 10),
            bg="#f2f2f2",
            fg="#555555"
        )
        subtitulo.place(x=0, y=60, width=760, height=20)

        # -----------------------------
        # SELEÇÃO DA PASTA
        # -----------------------------

        frame_pasta = tk.Frame(
            self.janela,
            bg="#ffffff",
            bd=1,
            relief="solid"
        )
        frame_pasta.place(x=25, y=95, width=710, height=55)

        self.label_pasta = tk.Label(
            frame_pasta,
            text="Nenhuma pasta selecionada",
            font=("Arial", 10),
            bg="#ffffff",
            fg="#555555",
            anchor="w"
        )
        self.label_pasta.place(
            x=15,
            y=0,
            width=520,
            height=55
        )

        self.botao_pasta = tk.Button(
            frame_pasta,
            text="Selecionar pasta",
            command=self.selecionar_pasta,
            font=("Arial", 9, "bold"),
            bg="#1976D2",
            fg="white",
            activebackground="#1565C0",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        )
        self.botao_pasta.place(
            x=545,
            y=10,
            width=145,
            height=35
        )

        # -----------------------------
        # CHECKBOX
        # -----------------------------

        self.incluir_subpastas = tk.BooleanVar(value=True)

        self.checkbox = tk.Checkbutton(
            self.janela,
            text="Incluir arquivos das subpastas",
            variable=self.incluir_subpastas,
            command=self.atualizar_lista,
            font=("Arial", 9),
            bg="#f2f2f2",
            activebackground="#f2f2f2",
            fg="#333333"
        )
        self.checkbox.place(
            x=25,
            y=160,
            width=250,
            height=25
        )

        # -----------------------------
        # QUANTIDADE
        # -----------------------------

        self.label_quantidade = tk.Label(
            self.janela,
            text="Arquivos encontrados: 0",
            font=("Arial", 11, "bold"),
            bg="#f2f2f2",
            fg="#333333"
        )
        self.label_quantidade.place(
            x=450,
            y=160,
            width=285,
            height=25
        )

        # -----------------------------
        # LISTA DE ARQUIVOS
        # -----------------------------

        frame_lista = tk.Frame(
            self.janela,
            bg="#ffffff",
            bd=1,
            relief="solid"
        )
        frame_lista.place(
            x=25,
            y=195,
            width=710,
            height=280
        )

        self.lista_arquivos = tk.Text(
            frame_lista,
            font=("Consolas", 9),
            bg="#ffffff",
            fg="#333333",
            relief="flat",
            wrap="none"
        )
        self.lista_arquivos.place(
            x=5,
            y=5,
            width=650,
            height=270
        )

        scrollbar = tk.Scrollbar(
            frame_lista,
            orient="vertical",
            command=self.lista_arquivos.yview
        )
        scrollbar.place(
            x=660,
            y=5,
            width=20,
            height=270
        )

        self.lista_arquivos.configure(
            yscrollcommand=scrollbar.set
        )

        # -----------------------------
        # BOTÕES
        # -----------------------------

        frame_botoes = tk.Frame(
            self.janela,
            bg="#f2f2f2"
        )
        frame_botoes.place(
            x=25,
            y=500,
            width=710,
            height=50
        )

        # Atualizar
        self.botao_atualizar = tk.Button(
            frame_botoes,
            text="Atualizar lista",
            command=self.atualizar_lista,
            font=("Arial", 9, "bold"),
            bg="#777777",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        )
        self.botao_atualizar.place(
            x=0,
            y=5,
            width=220,
            height=40
        )

        # Gerar TXT
        self.botao_txt = tk.Button(
            frame_botoes,
            text="Gerar arquivo TXT",
            command=self.gerar_txt,
            font=("Arial", 9, "bold"),
            bg="#1976D2",
            fg="white",
            activebackground="#1565C0",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        )
        self.botao_txt.place(
            x=245,
            y=5,
            width=220,
            height=40
        )

        # Imprimir
        self.botao_imprimir = tk.Button(
            frame_botoes,
            text="Imprimir relatório",
            command=self.imprimir_relatorio,
            font=("Arial", 9, "bold"),
            bg="#388E3C",
            fg="white",
            activebackground="#2E7D32",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        )
        self.botao_imprimir.place(
            x=490,
            y=5,
            width=220,
            height=40
        )

    # -----------------------------
    # SELECIONAR PASTA
    # -----------------------------

    def selecionar_pasta(self):

        pasta = filedialog.askdirectory(
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

            print_dlg.hwndOwner = self.janela.winfo_id()

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



if __name__ == "__main__":

    janela = tk.Tk()

    app = ListadorArquivos(
        janela
    )

    janela.mainloop()
