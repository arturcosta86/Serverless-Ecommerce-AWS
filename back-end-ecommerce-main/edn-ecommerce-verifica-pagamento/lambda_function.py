import os
import json
import boto3
import logging

# Configuração do logger para que os logs apareçam no CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Inicializa o client do S3 e Step Functions usando o Boto3 (SDK da AWS para Python)
s3 = boto3.client('s3')
sfn = boto3.client('stepfunctions')

# Variável de ambiente do S3
S3_BUCKET = os.environ['S3_BUCKET']

# Função principal da Lambda
def lambda_handler(event, _context):
    """
    Esta função é acionada por mensagens na fila SQS e processa o status do pedido.
    Dependendo da validade do número do cartão, o status é atualizado usando Step Functions,
    e o arquivo temporário é removido do S3.
    """

    # Loga o evento recebido para visualização no CloudWatch
    logger.info(f"Evento Recebido: {event}")

    for record in event.get('Records', []):
        try:
            # Processa o corpo da mensagem
            body = json.loads(record['body'])
            pedido_id = body.get("pedidoId")
            status = body.get("status", "pago")
            numero = body.get("numero", "")

            # Validação dos campos obrigatórios
            if not pedido_id or not numero:
                logger.warning("Mensagem inválida: pedidoId ou numero ausente")
                continue

            # Recupera o taskToken do S3
            response = s3.get_object(
                Bucket=os.environ['S3_BUCKET'],
                Key=f"tokens/pedido-{pedido_id}.json"
            )
            dados = json.loads(response['Body'].read())
            task_token = dados['taskToken']
            produtos = dados.get('produtos', [])
            total = dados.get('total', 0)

            # Verificação simples: se o número do cartão não for numérico ou não tiver 16 dígitos, é fraude
            if not numero.isdigit() or len(numero) != 16:
                logger.warning(f"Cartão inválido para o pedido {pedido_id}. Enviando falha.")

                sfn.send_task_success(
                    taskToken=task_token,
                    output=json.dumps({
                        "pedidoId": pedido_id,
                        "status": "cancelado",
                        "produtos": produtos,
                        "total": total,
                        "motivo": "Número do cartão inválido"
                    })
                )

                s3.delete_object(
                    Bucket=S3_BUCKET,
                    Key=f"tokens/pedido-{pedido_id}.json"
                )
                continue

            # Cartão válido, envia sucesso
            if numero.isdigit() and len(numero) == 16:
                sfn.send_task_success(
                    taskToken=task_token,
                    output=json.dumps({
                        "pedidoId": pedido_id,
                        "status": "pago",
                        "produtos": produtos,
                        "total": total,
                        "motivo": None
                    })
                )

                # Deleta o token do S3 após o processamento bem-sucedido
                s3.delete_object(
                    Bucket=os.environ['S3_BUCKET'],
                    Key=f"tokens/pedido-{pedido_id}.json"
                )

                logger.info(f"Pedido {pedido_id} processado com sucesso.")

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")

    return {
        "statusCode": 200,
        "body": json.dumps("Processamento finalizado.")
    }