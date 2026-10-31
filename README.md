<div align="center">

**🇧🇷 Português** | [🇺🇸 English](README.en.md)

# DocManager

**Sistema desktop em Python para listagem de arquivos, geração de relatórios, organização de documentos, atualização de planilhas Excel e compactação de arquivos.**

</div>

## Sobre o projeto

O **DocManager** foi criado para simplificar tarefas repetitivas de gerenciamento de arquivos e documentos. A versão 1.0 era um único script para listar arquivos e gerar relatórios. Na versão 2.0, o projeto evoluiu para uma aplicação modular, com interface gráfica e processamento de documentos para planilhas de despesas.

A aplicação reúne ferramentas independentes em uma interface principal, permitindo executar tarefas de listagem, organização e compactação de documentos.

## Funcionalidades

### Interface principal

- Menu principal com acesso aos módulos do sistema.
- Organização dos ícones dos módulos lado a lado.
- Interface adaptável ao redimensionamento da janela, mantendo os elementos principais visíveis.

### Listagem de arquivos

- Seleção de uma pasta e listagem dos arquivos encontrados.
- Opção de incluir subpastas.
- Exportação da listagem para arquivo TXT.
- Impressão de relatório no Windows.

### Organização de documentos e planilhas

- Leitura dos documentos colocados na pasta `NOVOS`.
- Extração de data, descrição, valor e tipo de serviço a partir do nome do arquivo.
- Validação das informações e indicação visual de dados inválidos.
- Exibição dos dados identificados para conferência antes do processamento.
- Criação de planilhas mensais a partir de um modelo Excel.
- Identificação de possíveis lançamentos duplicados, com confirmação antes do registro.
- Registro dos documentos nas planilhas correspondentes.
- Movimentação dos documentos processados para pastas por tipo de serviço, ano e mês.
- Manutenção dos arquivos com erro na pasta `NOVOS` para correção.
- Arquivamento dos documentos somente após salvar o lançamento na planilha.

### Compactação de documentos

- Listagem das planilhas mensais disponíveis na pasta `PLANILHAS`.
- Seleção da planilha que será compactada.
- Geração de um arquivo ZIP contendo a planilha selecionada e os documentos relacionados a ela.
- Inclusão dos documentos organizados por tipo de serviço, contemplando `CONTÁBIL`, `NÃO CONTÁBIL` e `AUDITORES`.

## Evolução do projeto

| Versão | Descrição |
| --- | --- |
| **1.0** | Script único para listagem de arquivos e geração de relatórios. |
| **2.0** | Aplicação modular com interface gráfica, validação de documentos, organização de arquivos e integração com planilhas Excel. |
| **2.x** | Evolução da interface principal e inclusão do módulo de compactação de planilhas e documentos relacionados em arquivos ZIP. |

O histórico da versão 1.0 e um módulo anterior de organização estão armazenados em `Versões Antigas/`. Os arquivos Python na raiz compõem a versão atual.

## Tecnologias

- **Python** — lógica da aplicação.
- **Tkinter / ttk** — interface gráfica.
- **Tksheet** — visualização dos dados em tabela.
- **OpenPyXL** — leitura e atualização de arquivos Excel.
- **Pillow** — suporte a imagens presentes no modelo de planilha.
- **Bibliotecas padrão do Python** — operações com arquivos, diretórios e compactação ZIP.

## Estrutura do projeto

```text
DocManager/
├── main.py                    # Inicialização e interface principal
├── listador_arquivos.py       # Listagem e relatórios
├── atualizar_planilha.py     # Validação e atualização de planilhas
├── Versões Antigas/          # Histórico de versões e módulo anterior
├── README.md
├── README.en.md
├── requirements.txt
└── .gitignore
```

A pasta `MODELO` é necessária para o funcionamento do processamento de planilhas, mas não é distribuída no repositório, pois contém o modelo original utilizado na operação. O usuário deve disponibilizar localmente o arquivo de modelo correspondente.

Durante o uso, o fluxo de documentos utiliza a pasta `NOVOS`, a pasta `MODELO` e a pasta `PLANILHAS`. Os documentos processados são organizados por tipo de serviço, ano e mês. Exemplo:

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

As pastas de serviço são criadas ou utilizadas conforme o processamento dos documentos. A pasta `NOVOS` é criada automaticamente quando a tela de validação é aberta.

## Padrão dos nomes dos documentos

O processamento automático espera nomes no formato:

```text
dd.mm.aa descrição (valor) tipo de serviço.ext
```

Exemplo:

```text
11.10.26 descrição teste (100,00) contábil.pdf
```

Tipos de serviço previstos: **CONTÁBIL**, **NÃO CONTÁBIL** e **AUDITORES**. Os nomes dos tipos devem utilizar os rótulos em português esperados pelo sistema. A validação identifica campos incorretos e destaca os problemas na tabela. A inserção no modelo utiliza as linhas 9 a 38 de cada aba.

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

3. Disponibilize localmente a pasta `MODELO` com **exatamente um arquivo `.xlsx`**, contendo as abas de CONTÁBIL, NÃO CONTÁBIL e AUDITORES. O modelo original não é disponibilizado no GitHub. A pasta `NOVOS` é criada automaticamente quando a tela de validação é aberta.

4. Inicie a aplicação:

   ```bash
   python main.py
   ```

> **Compatibilidade:** o projeto foi desenvolvido para Windows. Para utilizar no Windows 7, é necessário escolher versões do Python e das dependências compatíveis com esse sistema operacional.

## Observações

- A pasta `PLANILHAS` contém arquivos gerados durante a utilização e não precisa ser versionada.
- Não publique documentos reais nem planilhas com informações confidenciais.
- O módulo de compactação depende da estrutura de pastas e dos documentos relacionados à planilha selecionada.
- O repositório não inclui o modelo Excel original; ele deve ser fornecido separadamente para a operação do módulo de atualização de planilhas.

## Autor

**Giovanni Pinheiro Bonifatto**  
[GitHub](https://github.com/GIPB12) · [LinkedIn](https://www.linkedin.com/in/giovanni-bonifatto)
