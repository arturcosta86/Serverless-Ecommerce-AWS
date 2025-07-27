import os
import json
import boto3
import logging

from decimal import Decimal

# Configuração do logger para que os logs apareçam no CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Inicializa o client do DynamoDB usando o Boto3 (SDK da AWS para Python)
dynamodb = boto3.resource('dynamodb')

# Variável de ambiente da tabela do DynamoDB
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

# Função para montar os headers de CORS (Cross-Origin Resource Sharing)
def get_cors_headers():
    """
    Retorna os cabeçalhos CORS para permitir que requisições de origens diferentes acessem a Lambda.
    A origem permitida pode ser configurada por variável de ambiente (CORS_ORIGIN).
    """

    origin = os.environ.get('CORS_ORIGIN') 
    return {
        "Access-Control-Allow-Origin": origin,             # Origem permitida (configurável por variável de ambiente)
        "Access-Control-Allow-Headers": "Content-Type",    # Cabeçalhos permitidos
        "Access-Control-Allow-Methods": "OPTIONS,POST",    # Métodos permitidos
        "Content-Type": "application/json"                 # Tipo de conteúdo da resposta
    }


# Função de conversão de Decimal para float
def decimal_default(obj):
    """
    Converte todos os floats de um objeto (dict ou list) para Decimal.
    Necessária porque o json.dumps não consegue serializar o tipo Decimal retornado pelo DynamoDB.
    """

    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

# Função principal da Lambda
def lambda_handler(event, _context):
    """
    Esta função é acionada por um API Gateway.
    Se a requisição for do tipo OPTIONS, responde com os cabeçalhos CORS.
    Caso contrário, consulta o DynamoDB para listar itens da tabela.
    """

    # Loga o evento recebido para visualização no CloudWatch
    logger.info(f"Evento Recebido: {event}")

    # Verifica se a requisição é do tipo OPTIONS (pré-verificação do CORS)
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": get_cors_headers(),
            "body": json.dumps({ "message": "CORS preflight" })
        }

    try:
        response = table.scan()  # Busca todos os itens da tabela
        itens = response.get("Items", [])
        logger.info(f"[DynamoDB] {len(itens)} itens encontrados.")

        # Retorna a resposta com os itens encontrados, convertendo Decimal para float
        return {
            "statusCode": 200,
            "headers": get_cors_headers(),
            "body": json.dumps(itens, default=decimal_default)
        }

    except Exception as e:
        # Em caso de erro, loga com stack trace para análise posterior
        logger.error(f"Falha ao listar pedidos: {str(e)}", exc_info=True)

        # Se ocorrer algum erro, a mensagem de erro é enviada no corpo da resposta.
        return {
            "statusCode": 500,
            "headers": get_cors_headers(),
            "body": json.dumps({ "message": "Erro ao listar pedidos", "erro": str(e) })
        }
