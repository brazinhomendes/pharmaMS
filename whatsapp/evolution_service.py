import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class EvolutionAPIService:
    def __init__(self, config):
        self.config = config
        self.base_url = config.api_url.rstrip('/')
        self.headers = {
            'apikey': config.api_key,
            'Content-Type': 'application/json',
        }

    def criar_instancia(self):
        url = f'{self.base_url}/instance/create'
        payload = {
            'instanceName': self.config.nome_instancia,
            'integration': 'WHATSAPP-BAILEYS',
        }
        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=30)
            return resp.json()
        except Exception as e:
            logger.error(f'Erro ao criar instancia: {e}')
            return {'error': str(e)}

    def conectar_instancia(self):
        url = f'{self.base_url}/instance/connect/{self.config.nome_instancia}'
        try:
            resp = requests.get(url, headers=self.headers, timeout=30)
            return resp.json()
        except Exception as e:
            logger.error(f'Erro ao conectar instancia: {e}')
            return {'error': str(e)}

    def status_instancia(self):
        url = f'{self.base_url}/instance/connectionState/{self.config.nome_instancia}'
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            return resp.json()
        except Exception as e:
            logger.error(f'Erro ao consultar status: {e}')
            return {'error': str(e)}

    def enviar_mensagem(self, numero, mensagem):
        url = f'{self.base_url}/message/sendText/{self.config.nome_instancia}'
        payload = {
            'number': numero,
            'text': mensagem,
        }
        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=30)
            data = resp.json()
            return {
                'success': 'key' in data,
                'message_id': data.get('key', {}).get('id', ''),
                'data': data,
            }
        except Exception as e:
            logger.error(f'Erro ao enviar mensagem: {e}')
            return {'success': False, 'error': str(e)}

    def configurar_webhook(self, webhook_url):
        url = f'{self.base_url}/webhook/setWebhook/{self.config.nome_instancia}'
        payload = {
            'enabled': True,
            'url': webhook_url,
            'webhookByEvents': False,
            'events': [
                'MESSAGES_UPSERT',
                'SEND_MESSAGE',
                'CONNECTION_UPDATE',
            ],
        }
        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=30)
            return resp.json()
        except Exception as e:
            logger.error(f'Erro ao configurar webhook: {e}')
            return {'error': str(e)}

    def verificar_webhook(self):
        url = f'{self.base_url}/webhook/find/{self.config.nome_instancia}'
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            return resp.json()
        except Exception as e:
            logger.error(f'Erro ao verificar webhook: {e}')
            return {'error': str(e)}
