import json

from pathlib import Path
import sys

#import boto3
#from botocore.exceptions import ClientError
#from mypy_boto3_textract.type_defs import DetectDocumentTextResponseTypeDef

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
