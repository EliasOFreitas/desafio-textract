# Desafio de Código: OCR com AWS Textract e Python

Este repositório contém a solução desenvolvida para o desafio de código da DIO, utilizando Python e o serviço de OCR **AWS Textract**. A solução foi estruturada para permitir o desenvolvimento e testes locais offline (sem depender imediatamente de uma conta na AWS), mantendo a compatibilidade completa com o serviço em nuvem.

---

## 📌 Visão Geral da Solução

O objetivo do desafio é processar uma imagem de lista de compras (`lista_compras.png`), enviar seus bytes para o serviço AWS Textract (ou ler um cache local do JSON retornado) e extrair do resultado apenas o texto das linhas identificadas (`BlockType == "LINE"`).

Para permitir que o código seja testado sem a biblioteca `boto3` e sem credenciais da AWS configuradas localmente, adotou-se uma estratégia de **fallback com cache em `response.json`**. As importações da AWS permanecem comentadas durante a fase de testes locais, evitando o erro `ModuleNotFoundError: No module named 'boto3'`.

---

## 🧠 Estrutura de Retorno do AWS Textract

A API do AWS Textract (método `DetectDocumentText`) retorna uma estrutura hierárquica em JSON no campo `Blocks`:

1. **`PAGE`:** Bloco raiz que representa a página completa. Contém o relacionamento (`Relationships`) do tipo `CHILD` com a lista de IDs de todas as linhas da página.
2. **`LINE`:** Representa uma linha inteira de texto. É a unidade de extração do nosso projeto. Contém:
   - `Text`: A string contendo o texto extraído da linha.
   - `Confidence`: O nível de precisão/confiança do algoritmo (0 a 100%).
   - `Geometry`: Coordenadas espaciais de delimitação (`BoundingBox` e `Polygon`).
   - `Relationships`: IDs dos blocos de palavras (`WORD`) que compõem a linha.
3. **`WORD`:** Representa palavras individuais identificadas na imagem.

---

## 💻 Código Fonte Final (`main.py`)

Abaixo está o código final ajustado para lidar com problemas de acentuação no Windows (UTF-8) e execução offline com fallback:

```python
import json
from pathlib import Path
import sys

# import boto3
# from botocore.exceptions import ClientError
# from mypy_boto3_textract.type_defs import DetectDocumentTextResponseTypeDef

# Força o terminal a exibir caracteres em UTF-8 (corrige acentos no Windows) 
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")


def detect_file_text() -> None:
    client = boto3.client("textract")

    file_path = str(Path(__file__).parent / "images" / "lista_compras.png")
    with open(file_path, "rb") as f:
        document_bytes = f.read()

    try:
        response = client.detect_document_text(Document={"Bytes": document_bytes})
        with open("response.json", "w", encoding="utf-8") as response_file:
            response_file.write(json.dumps(response))
    except ClientError as e:
        print(f"Erro processando documento: {e}")


def get_lines() -> list[str]:
    try:
        with open("response.json", "r", encoding="utf-8") as f:
            data: DetectDocumentTextResponseTypeDef = json.loads(f.read())
            blocks = data["Blocks"]
        return [block["Text"] for block in blocks if block["BlockType"] == "LINE"]  # type: ignore
    except IOError:
        detect_file_text()
    return []


if __name__ == "__main__":
    for line in get_lines():
        print(line)
```

---

## 🛠️ Destaques da Implementação

1. **Testes Locais Offline (Sem AWS CLI / boto3):**
   - Com a criação prévia do arquivo `response.json` idêntico ao modelo da AWS, a função `get_lines()` lê os dados salvos em disco.
   - Ao manter as linhas de `import boto3` comentadas, o script roda em qualquer ambiente Python padrão sem disparar `ModuleNotFoundError`.

2. **Tratamento de Codificação de Caracteres (UTF-8):**
   - **No Terminal:** O trecho `sys.stdout.reconfigure(encoding="utf-8")` garante que acentos (`ã`, `ç`, `é`, etc.) sejam exibidos corretamente no Windows (CMD / PowerShell / VS Code).
   - **Na Leitura do Arquivo:** O parâmetro `encoding="utf-8"` na função `open()` previne corrupção de caracteres ao carregar o JSON.

3. **Caminho Relativo Dinâmico:**
   - O caminho da imagem utiliza `Path(__file__).parent / "images" / "lista_compras.png"`, garantindo que o arquivo seja localizado independentemente do diretório de onde o script for chamado.

4. **Transição para Execução Real na AWS:**
   - Quando desejar integrar à conta gratuita da AWS:
     1. Instale o boto3: `pip install boto3 mypy-boto3-textract`.
     2. Descomente as linhas de importação (`import boto3` e exceções).
     3. Configure o AWS CLI (`aws configure`).
     4. Remova o arquivo `response.json` local para forçar uma nova requisição à API do Textract.

---

## 📂 Estrutura de Diretórios do Projeto

```text
desafio-textract/
│
├── images/
│   └── lista_compras.png      # Imagem utilizada para o OCR
│
├── response.json               # JSON bruto de resposta (modelo Textract)
├── main.py                     # Script principal em Python
└── README.md                   # Documentação do projeto
```
