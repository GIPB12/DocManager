
import tkinter as tk
from tkinter import ttk

from atualizar_planilha import SistemaDocumentos
from listador_arquivos import ListadorArquivos
from compactar import CompactadorDocumentos

class Aplicacao:
    def __init__(self, root):
        self.root = root

        self.root.title("DocManager - Sistema de Documentos")
        self.root.geometry("1100x600")
        self.root.minsize(850, 500)

        self.cor_fundo = "#F4F6F8"
        self.cor_cartao = "#FFFFFF"
        self.cor_primaria = "#2457A7"
        self.cor_texto = "#263238"

        self.root.configure(bg=self.cor_fundo)

        self.configurar_estilos()
        self.frame_atual = None

        self.mostrar_menu()

    def configurar_estilos(self):
        estilo = ttk.Style()
        estilo.configure(
            "Titulo.TLabel",
            font=("Segoe UI", 22, "bold"),
            background=self.cor_fundo,
            foreground=self.cor_texto
        )
        estilo.configure(
            "Descricao.TLabel",
            font=("Segoe UI", 10),
            background=self.cor_fundo,
            foreground="#65717C"
        )
        estilo.configure(
            "Menu.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 8)
        )
        estilo.configure(
            "Voltar.TButton",
            font=("Segoe UI", 10),
            padding=6
        )

    def trocar_tela(self, nova_tela):
        if self.frame_atual is not None:
            self.frame_atual.destroy()

        self.frame_atual = nova_tela
        self.frame_atual.pack(fill="both", expand=True)

    def mostrar_menu(self):
        tela = tk.Frame(self.root, bg=self.cor_fundo)

        # Cabeçalho separado dos cards: permanece visível ao redimensionar.
        cabecalho = tk.Frame(tela, bg=self.cor_fundo)
        cabecalho.pack(fill="x", padx=28, pady=(24, 18))

        tk.Label(
            cabecalho,
            text="DocManager",
            font=("Segoe UI", 25, "bold"),
            bg=self.cor_fundo,
            fg=self.cor_primaria
        ).pack()

        tk.Label(
            cabecalho,
            text="Sistema de gerenciamento de documentos",
            font=("Segoe UI", 10),
            bg=self.cor_fundo,
            fg="#65717C"
        ).pack(pady=(3, 10))

        tk.Frame(
            cabecalho,
            bg="#DCE2E8",
            height=1
        ).pack(fill="x", pady=(8, 0))

        tk.Label(
            tela,
            text="Selecione o serviço desejado",
            font=("Segoe UI", 11, "bold"),
            bg=self.cor_fundo,
            fg=self.cor_texto
        ).pack(pady=(4, 14))

        area_cartoes = tk.Frame(tela, bg=self.cor_fundo)
        area_cartoes.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        opcoes = [
            {
                "icone": "✓",
                "titulo": "Validação e organização",
                "descricao": (
                    "Validar nomes de documentos, conferir informações "
                    "e registrar lançamentos nas planilhas."
                ),
                "comando": self.abrir_validacao
            },
            {
                "icone": "▤",
                "titulo": "Listagem e relatórios",
                "descricao": (
                    "Listar arquivos de uma pasta, incluir subpastas, "
                    "gerar relatórios TXT e imprimir."
                ),
                "comando": self.abrir_relatorios
            },
            {
                "icone": "▣",
                "titulo": "Fechamento mensal",
                "descricao": (
                    "Selecionar uma planilha mensal e compactá-la junto "
                    "com os documentos contábeis, não contábeis e auditores."
                ),
                "comando": self.abrir_compactador
            }
        ]

        cartoes = []
        for opcao in opcoes:
            cartoes.append(self.criar_opcao(area_cartoes, **opcao))

        # Reorganiza os cards conforme a largura disponível.
        def reorganizar(event=None):
            largura = area_cartoes.winfo_width()

            if largura >= 900:
                colunas = 3
            elif largura >= 590:
                colunas = 2
            else:
                colunas = 1

            for widget in cartoes:
                widget.grid_forget()

            for coluna in range(3):
                area_cartoes.grid_columnconfigure(coluna, weight=0)

            for coluna in range(colunas):
                area_cartoes.grid_columnconfigure(coluna, weight=1, uniform="cards")

            for indice, cartao in enumerate(cartoes):
                linha = indice // colunas
                coluna = indice % colunas
                cartao.grid(
                    row=linha,
                    column=coluna,
                    sticky="nsew",
                    padx=7,
                    pady=7
                )

            linhas = (len(cartoes) + colunas - 1) // colunas
            for linha in range(linhas):
                area_cartoes.grid_rowconfigure(linha, weight=1)

        area_cartoes.bind("<Configure>", reorganizar)

        rodape = tk.Label(
            tela,
            text="Sistema de uso interno",
            font=("Segoe UI", 9),
            bg=self.cor_fundo,
            fg="#89939C"
        )
        rodape.pack(pady=(0, 12))

        self.trocar_tela(tela)

    def criar_opcao(self, pai, icone, titulo, descricao, comando):
        cartao = tk.Frame(
            pai,
            bg=self.cor_cartao,
            highlightbackground="#DCE2E8",
            highlightthickness=1,
            padx=16,
            pady=18
        )

        conteudo = tk.Frame(cartao, bg=self.cor_cartao)
        conteudo.pack(fill="both", expand=True)

        circulo = tk.Canvas(
            conteudo,
            width=54,
            height=54,
            bg=self.cor_cartao,
            highlightthickness=0
        )
        circulo.pack(pady=(2, 12))
        circulo.create_oval(
            3, 3, 51, 51,
            fill="#EAF1FB",
            outline=""
        )
        circulo.create_text(
            27, 27,
            text=icone,
            fill=self.cor_primaria,
            font=("Segoe UI Symbol", 23, "bold")
        )

        tk.Label(
            conteudo,
            text=titulo,
            font=("Segoe UI", 12, "bold"),
            bg=self.cor_cartao,
            fg=self.cor_texto,
            wraplength=250,
            justify="center"
        ).pack(fill="x")

        tk.Label(
            conteudo,
            text=descricao,
            font=("Segoe UI", 9),
            bg=self.cor_cartao,
            fg="#65717C",
            justify="center",
            wraplength=250
        ).pack(fill="both", expand=True, pady=(8, 16))

        ttk.Button(
            conteudo,
            text="Abrir serviço",
            style="Menu.TButton",
            command=comando
        ).pack()

        return cartao

    def criar_cabecalho(self, pai, titulo):
        cabecalho = tk.Frame(pai, bg=self.cor_fundo)
        cabecalho.pack(fill="x", padx=20, pady=15)

        ttk.Button(
            cabecalho,
            text="← Voltar ao menu",
            style="Voltar.TButton",
            command=self.mostrar_menu
        ).pack(side="left")

        tk.Label(
            cabecalho,
            text=titulo,
            font=("Segoe UI", 17, "bold"),
            bg=self.cor_fundo,
            fg=self.cor_texto
        ).pack(side="left", padx=20)

    def abrir_validacao(self):
        tela = SistemaDocumentos(self.root, self)
        self.trocar_tela(tela)

    def abrir_relatorios(self):
        tela = ListadorArquivos(self.root, self)
        self.trocar_tela(tela)

    def abrir_compactador(self):
        tela = CompactadorDocumentos(self.root, self)
        self.trocar_tela(tela)

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacao(root)
    root.mainloop()
