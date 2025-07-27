import os
import json
import uuid
import boto3
import logging

# Configuração do logger para que os logs apareçam no CloudWatch
logger = loggiimport os
import json
import uuid
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
sfn = boto3.client('stepfunctions')

def get_cors_headers():
    origin = os.environ.get('CORS_ORIGIN') 
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST",
        "Content-Type": "application/json"
    }

def lambda_handler(event, _context):
    logger.info(f"Evento Recebido: {event}")
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": get_cors_headers(), "body": ""}

    try:
        if "body" in event and isinstance(event["body"], str):
            body = json.loads(event["body"])
        else:
            body = event
        produtos = body["produtos"]
        total = body["total"]
    except Exception as e:
        logger.warning(f"Erro nos dados recebidos: {str(e)}")
        return {"statusCode": 400, "headers": get_cors_headers(), "body": json.dumps({"error": f"Erro nos dados recebidos: {str(e)}"}) }

    pedidoId = str(uuid.uuid4())

    # CORREÇÃO APLICADA AQUI
    input_data = {
        "pedidoId": pedidoId,
        "produtos": produtos,
        "total": total
    }

    try:
        sfn.start_execution(
            stateMachineArn=os.environ['STATE_MACHINE_ARN'],
            input=json.dumps(input_data)
        )
    except Exception as e:
        logger.error(f"Erro ao iniciar Step Function: {str(e)}")
        return {"statusCode": 500, "headers": get_cors_headers(), "body": json.dumps({"error": "Erro ao iniciar o pedido"}) }

    logger.info(f"Pedido iniciado com ID: {pedidoId}")
    return {
        "statusCode": 200,
        "headers": get_cors_headers(),
        # CORREÇÃO APLICADA AQUI
        "body": json.dumps({
            "message": "Pedido iniciado",
            "pedidoId": pedidoId
        })
    }```

#### **2. Função: `aguarda-pagamento`**
*   **O que muda:** A chave ao extrair o ID do pedido do evento.

```python
import os
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.client('s3')
S3_BUCKET = os.environ['S3_BUCKET']

def lambda_handler(event, _context):
    logger.info(f"Evento Recebido: {event}")
    try:
        task_token = event['taskToken']
        # CORREÇÃO APLICADA AQUI
        pedidoId = event['pedidoId']
        produtos = event['produtos']
        total = event['total']

        logger.info(f"[Processando Pedido] ID: {pedidoId}, Total: {total}, Produtos: {produtos}")
        s3_key = f"tokens/pedido-{pedidoId}.json"

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps({
                "taskToken": task_token,
                "produtos": produtos,
                "total": total
            }),
            ContentType="application/json"
        )
        logger.info(f"[S3 Upload] Arquivo salvo com sucesso: s3://{S3_BUCKET}/{s3_key}")
        return { "status": "Aguardando pagamento" }
    except Exception as e:
        logger.error(f"Falha ao salvar pedido {pedidoId if 'pedidoId' in locals() else ''}: {str(e)}", exc_info=True)
        raiseng.getLogger()
logger.setLevel(logging.INFO)

# Inicializa o client do Step Functions usando o Boto3 (SDK da AWS para Python)
sfn = boto3.client('stepfunctions')

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

# Função principal da Lambda
def lambda_handler(event, _context):
    """
    Esta função é acionada por um API Gateway.
    Se a requisição for do tipo OPTIONS, responde com os cabeçalhos CORS.
    Caso contrário, inicia uma execução da Step Function para processar um novo pedido,
    enviando os dados recebidos no corpo da requisição.
    """

    # Loga o evento recebido para visualização no CloudWatch
    logger.info(f"Evento Recebido: {event}")

    # Trata requisições do tipo OPTIONS (usado em pré-verificação do CORS)
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": get_cors_headers(),
            "body": ""
        }

    # Tenta extrair os dados da requisição
    try:
        # Se o corpo da requisição for uma string JSON, faz o parse
        if "body" in event and isinstance(event["body"], str):
            body = json.loads(event["body"])
        else:
            body = event # Em alguns testes locais, os dados podem vir direto no evento

        # Extrai os campos esperados
        produtos = body["produtos"]
        total = body["total"]
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        # Caso falte algum campo ou o JSON esteja mal formado
        logger.warning(f"Erro nos dados recebidos: {str(e)}")
        return {
            "statusCode": 400,
            "headers": get_cors_headers(),
            "body": json.dumps({"error": f"Erro nos dados recebidos: {str(e)}"})
        }

    # Gera um ID único e aleatório para identificar o pedido
    pedido_id = str(uuid.uuid4())

    # Monta os dados que serão enviados para a Step Function
    input_data = {
        "pedidoId": pedido_id,
        "produtos": produtos,
        "total": total
    }

    # Tenta iniciar a execução da Step Function com os dados recebidos
    try:
        sfn.start_execution(
            stateMachineArn=os.environ['STATE_MACHINE_ARN'], # ARN da Step Function vindo por variável de ambiente
            input=json.dumps(input_data) # Converte os dados para JSON
        )
    except Exception as e:
        # Em caso de erro na chamada para o Step Functions
        logger.error(f"Erro ao iniciar Step Function: {str(e)}")
        return {
            "statusCode": 500,
            "headers": get_cors_headers(),
            "body": json.dumps({"error": "Erro ao iniciar o pedido"})
        }

    # Loga sucesso da operação e retorna resposta ao cliente
    logger.info(f"Pedido iniciado com ID: {pedido_id}")
    return {
        "statusCode": 200,
        "headers": get_cors_headers(),
        "body": json.dumps({
            "message": "Pedido iniciado",
            "pedidoId": pedido_id
        })
    }
