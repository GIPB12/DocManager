
import tkinter as tk
from tkinter import ttk

from atualizar_planilha import SistemaDocumentos
from listador_arquivos import ListadorArquivos

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
            font=("Segoe UI", 12, "bold"),
            padding=14
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

        conteudo = tk.Frame(tela, bg=self.cor_fundo)
        conteudo.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=650
        )

        ttk.Label(
            conteudo,
            text="DocManager - Sistema de Documentos",
            style="Titulo.TLabel"
        ).pack(pady=(0, 8))

        ttk.Label(
            conteudo,
            text="Selecione o serviço que deseja utilizar.",
            style="Descricao.TLabel"
        ).pack(pady=(0, 30))

        self.criar_opcao(
            conteudo,
            titulo="Validação e organização",
            descricao=(
                "Validar nomes de documentos, conferir informações "
                "e registrar lançamentos nas planilhas."
            ),
            comando=self.abrir_validacao
        )

        self.criar_opcao(
            conteudo,
            titulo="Listagem e relatórios",
            descricao=(
                "Listar arquivos de uma pasta, incluir subpastas, "
                "gerar relatórios TXT e imprimir."
            ),
            comando=self.abrir_relatorios
        )

        ttk.Label(
            conteudo,
            text="Sistema de uso interno",
            style="Descricao.TLabel"
        ).pack(pady=(25, 0))

        self.trocar_tela(tela)

    def criar_opcao(self, pai, titulo, descricao, comando):
        cartao = tk.Frame(
            pai,
            bg=self.cor_cartao,
            highlightbackground="#DCE2E8",
            highlightthickness=1,
            padx=22,
            pady=18
        )
        cartao.pack(fill="x", pady=8)

        tk.Label(
            cartao,
            text=titulo,
            font=("Segoe UI", 13, "bold"),
            bg=self.cor_cartao,
            fg=self.cor_texto,
            anchor="w"
        ).pack(fill="x")

        tk.Label(
            cartao,
            text=descricao,
            font=("Segoe UI", 10),
            bg=self.cor_cartao,
            fg="#65717C",
            anchor="w",
            justify="left",
            wraplength=580
        ).pack(fill="x", pady=(6, 14))

        ttk.Button(
            cartao,
            text="Abrir serviço",
            style="Menu.TButton",
            command=comando
        ).pack(anchor="e")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacao(root)
    root.mainloop()
