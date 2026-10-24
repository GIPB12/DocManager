<div align="center">

**🇧🇷 Português** | [🇺🇸 English](README.en.md)

# DocManager

**Sistema desktop em Python para listagem de arquivos, geração de relatórios e organização de documentos com atualização de planilhas Excel.**

</div>

## Sobre o projeto

O **DocManager** foi criado para simplificar tarefas repetitivas de gerenciamento de arquivos. A versão 1.0 era um único script para listar arquivos e gerar relatórios. Na versão 2.0, o projeto evoluiu para uma aplicação com módulos separados, interface gráfica e processamento de documentos para planilhas de despesas.

## Funcionalidades

### Listagem de arquivos

- Seleção de uma pasta e listagem dos arquivos encontrados.
- Opção de incluir subpastas.
- Exportação da listagem para arquivo TXT.
- Impressão de relatório no Windows.

### Organização de documentos e planilhas

- Leitura dos documentos colocados na pasta `NOVOS`.
- Extração de data, descrição, valor e tipo de serviço a partir do nome do arquivo.
- Validação das informações e indicação visual de dados inválidos.
- Criação de planilhas mensais a partir de um modelo Excel.
- Identificação de possíveis lançamentos duplicados, com confirmação antes do registro.
- Registro dos documentos nas planilhas correspondentes.
- Movimentação dos documentos processados para pastas por tipo de serviço, ano e mês.
- Manutenção dos arquivos com erro na pasta `NOVOS` para correção.
- Arquivamento dos documentos somente após salvar o lançamento na planilha.

## Evolução do projeto

| Versão | Descrição |
| --- | --- |
| **1.0** | Script único para listagem de arquivos e geração de relatórios. |
| **2.0** | Aplicação modular com interface gráfica, validação de documentos, organização de arquivos e integração com planilhas Excel. |

O histórico da versão 1.0 e um módulo anterior de organização estão armazenados em `Versões Antigas/`. **Os três arquivos Python na raiz são os módulos da versão atual.**

## Tecnologias

- **Python** — lógica da aplicação.
- **Tkinter / ttk** — interface gráfica.
- **Tksheet** — visualização dos dados em tabela.
- **OpenPyXL** — leitura e atualização de arquivos Excel.
- **Pillow** — suporte a imagens presentes no modelo de planilha.

## Estrutura do projeto

```text
DocManager/
├── main.py       # Inicialização e interface principal
├── listador_arquivos.py      # Listagem e relatórios
├── atualizar_planilha.py     # Validação e atualização de planilhas
├── MODELO/                   # Modelo Excel utilizado pelo sistema
├── PLANILHAS/                # Planilhas geradas (não versionadas)
├── Versões Antigas/          # Histórico de versões e módulo anterior
├── README.md
├── README.en.md
├── requirements.txt
└── .gitignore
```

Durante o uso, o fluxo de documentos utiliza a pasta `NOVOS` e organiza os arquivos processados em pastas de serviço, ano e mês, por exemplo:

```text
Sistema/
├── NOVOS/
├── MODELO/
├── PLANILHAS/
├── CONTÁBIL/
│   └── 2026/
│       └── 10/
├── NÃO CONTÁBIL/
└── AUDITORES/
```

As pastas por tipo de serviço são criadas/utilizadas conforme o processamento dos documentos.

## Padrão dos nomes dos documentos

O processamento automático espera nomes no formato:

```text
dd.mm.aa descrição (valor) tipo de serviço.ext
```

Exemplo:

```text
11.10.26 descrição teste (100,00) contábil.pdf
```

Tipos de serviço previstos: **CONTÁBIL**, **NÃO CONTÁBIL** e **AUDITORES**. A validação identifica campos incorretos e destaca os problemas na tabela. A inserção no modelo utiliza as linhas 9 a 38 de cada aba.

## Instalação e execução

1. Clone o repositório e acesse sua pasta:

   ```bash
   git clone https://github.com/GIPB12/DocManager.git
   cd DocManager
   ```

2. Instale as dependências:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Verifique se a pasta `MODELO` contém **exatamente um arquivo `.xlsx`**, com as abas de CONTÁBIL, NÃO CONTÁBIL e AUDITORES. A pasta `NOVOS` é criada automaticamente quando a tela de validação é aberta.

4. Inicie a aplicação:

   ```bash
   python main.py
   ```

> **Compatibilidade:** o projeto foi desenvolvido para Windows. Para utilizar no Windows 7, é necessário escolher versões do Python e das dependências compatíveis com esse sistema operacional.

## Observações

- O título da janela ainda aparece como `Sistema de Documentos`, conforme o código atual. Alterar o nome do repositório e do arquivo principal não modifica esse título automaticamente.
- A função de nomeação das planilhas ainda utiliza um nome fixo no código; isso não é alterado pela documentação.

- Não publique documentos reais nem planilhas com informações confidenciais.
- A pasta `PLANILHAS` contém arquivos gerados durante a utilização e não precisa ser versionada.
- O comando de clonagem considera que o repositório será publicado como `GIPB12/DocManager`.

## Autor

**Giovanni Pinheiro Bonifatto**  
[GitHub](https://github.com/GIPB12) · [LinkedIn](https://www.linkedin.com/in/giovanni-bonifatto)
