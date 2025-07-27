import os
import json
import boto3
import logging

# Configuração do logger para que os logs apareçam no CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Inicializa o client do SQS usando o Boto3 (SDK da AWS para Python)
sqs = boto3.client('sqs')

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
    Esta função é acionada por uma requisição HTTP (via API Gateway) logo após o pagamento de um pedido.
    Ela valida os dados recebidos, monta uma mensagem com as informações do pagamento e envia para uma fila SQS,
    onde será processada posteriormente por outra etapa do sistema.
    Também trata requisições de pré-vôo CORS para permitir chamadas do front-end.
    """

    # Loga o evento recebido para visualização no CloudWatch
    logging.info(f"Evento recebido: {event}")

    # Responde requisições de pré-vôo CORS
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": get_cors_headers(),
            "body": json.dumps({ "message": "CORS preflight" })
        }

    # Tenta fazer o parse do corpo da requisição
    try:
        body = json.loads(event["body"])
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        logging.warning(f"Erro ao interpretar body: {str(e)}")
        return {
            "statusCode": 400,
            "headers": get_cors_headers(),
            "body": json.dumps({ "message": "Body inválido ou ausente" })
        }

    # Extrai dados do body
    pedido_id = body.get("pedidoid")
    status = body.get("status", "pago")
    numero = body.get("numero")

    # Validação simples dos campos obrigatórios
    if not pedido_id or not numero:
        return {
            "statusCode": 400,
            "headers": get_cors_headers(),
            "body": json.dumps({ "message": "pedidoid e numero do cartão são obrigatórios" })
        }

    # Tenta enviar mensagem para a fila SQS
    try:
        sqs.send_message(
            QueueUrl=os.environ['SQS_URL'],
            MessageBody=json.dumps({
                "pedidoid": pedido_id,
                "status": status,
                "numero": numero
            })
        )

        # Loga o sucesso do envio da mensagem para o SQS
        logging.info(f"Mensagem enviada para SQS com pedidoid: {pedido_id}")

        # Retorna isso para front-end cenário feliz
        return {
            "statusCode": 200,
            "headers": get_cors_headers(),
            "body": json.dumps({ "message": f"Pagamento enviado para processamento. Pedido {pedido_id}" })
        }

    except Exception as e:
        # Loga qualquer erro ocorrido no envio da mensagem para a fila
        logging.error(f"Erro ao enviar mensagem para SQS: {str(e)}")

        # Retorna isso para front-end cenário de exceção
        return {
            "statusCode": 500,
            "headers": get_cors_headers(),
            "body": json.dumps({ "message": "Erro ao processar pagamento" })
        }
