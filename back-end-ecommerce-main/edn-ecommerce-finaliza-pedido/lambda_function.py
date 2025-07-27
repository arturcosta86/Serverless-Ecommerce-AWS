import os
import boto3
import json
import logging
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

# Helper para converter floats para o formato Decimal do DynamoDB
def convert_floats_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    return obj

def lambda_handler(event, context):
    # Loga o evento inteiro para depuração
    logger.info(f"Evento Recebido para finalizar pedido: {json.dumps(event)}")

    try:
        # O input da Step Function é o próprio evento
        payload = event

        # Se o payload for uma string JSON (vindo de um TaskToken), faz o parse.
        if isinstance(payload, str):
            payload = json.loads(payload)

        # ==================================================================
        # CORREÇÃO CRÍTICA APLICADA AQUI
        # Garante que estamos usando 'pedidoId' (com 'I' maiúsculo)
        # ==================================================================
        pedidoId = payload.get('pedidoId')

        if not pedidoId:
            raise KeyError("A chave 'pedidoId' não foi encontrada no evento de entrada.")

        produtos = payload.get('produtos', [])
        total = payload.get('total', 0)
        status = payload.get('status', 'desconhecido')
        motivo = payload.get('motivo', None)
        timestamp = int(datetime.timestamp(datetime.now()))

        item = {
            "pedidoId": pedidoId, # Chave da partição
            "produtos": convert_floats_to_decimal(produtos),
            "total": convert_floats_to_decimal(total),
            "status": status,
            "timestamp": timestamp 
        }

        if status == "cancelado" and motivo:
            item["motivo"] = motivo

        # Loga o item que será salvo para depuração
        logger.info(f"Item a ser salvo no DynamoDB: {json.dumps(item, default=str)}")

        table.put_item(Item=item)
        logger.info(f"[DynamoDB] Pedido {pedidoId} salvo com sucesso com status '{status}'.")

        return { "status": f"Pedido {status}" }

    except Exception as e:
        logger.error(f"[ERRO GERAL] Falha ao processar pedido: {str(e)}", exc_info=True)
        raise e