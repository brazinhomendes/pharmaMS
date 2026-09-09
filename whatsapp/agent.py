import logging
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


class AgenteWhatsApp:
    def __init__(self, empresa, conversa):
        self.empresa = empresa
        self.conversa = conversa

    def processar(self, mensagem):
        mensagem_lower = mensagem.lower().strip()

        if self.conversa.etapa == 'aguardando_pedido':
            return self._processar_pedido(mensagem)

        if mensagem_lower in ('1', 'um', 'promocao', 'promocoes', 'ofertas'):
            return self._listar_promocoes()

        if mensagem_lower in ('2', 'dois', 'pedido', 'pedidos', 'acompanhar'):
            self.conversa.etapa = 'aguardando_pedido'
            self.conversa.save()
            return 'Informe o numero do seu pedido (ex: 001):'

        if mensagem_lower in ('3', 'tres', 'atendente', 'humano', 'suporte'):
            self.conversa.etapa = 'aguardando_atendente'
            self.conversa.save()
            return (
                'Um atendente sera notificado e entrara em contato em breve.\n'
                'Enquanto isso, envie sua duvida que registramos para o atendente.'
            )

        if mensagem_lower in ('4', 'quatro', 'horario', 'funcionamento'):
            return self._horario_funcionamento()

        if mensagem_lower in ('5', 'cinco', 'localizacao', 'endereco', 'onde'):
            return self._endereco()

        if mensagem_lower in ('6', 'seis', 'estoque', 'disponivel', 'produto'):
            self.conversa.etapa = 'aguardando_pedido'
            self.conversa.save()
            return 'Informe o nome do produto que deseja consultar:'

        return self._menu_inicial()

    def _menu_inicial(self):
        if self.conversa.etapa == 'inicio':
            self.conversa.etapa = 'menu_principal'
            self.conversa.save()
            if self.empresa and hasattr(self.empresa, 'nome'):
                return (
                    f'Ola! Bem-vindo a {self.empresa.nome}! Como posso ajudar?\n\n'
                    '1 - Ver promocoes\n'
                    '2 - Consultar pedido\n'
                    '3 - Falar com atendente\n'
                    '4 - Horario de funcionamento\n'
                    '5 - Nosso endereco\n'
                    '6 - Consultar produto'
                )
            return (
                'Ola! Bem-vindo! Como posso ajudar?\n\n'
                '1 - Ver promocoes\n'
                '2 - Consultar pedido\n'
                '3 - Falar com atendente\n'
                '4 - Horario de funcionamento\n'
                '5 - Nosso endereco\n'
                '6 - Consultar produto'
            )
        return self._menu_inicial()

    def _listar_promocoes(self):
        try:
            from promocoes.models import Promocao
            from django.utils import timezone as tz
            promocoes = Promocao.objects.filter(
                empresa=self.empresa,
                ativo=True,
                data_fim__gte=tz.now().date(),
            )[:5]

            if not promocoes:
                return 'No momento nao temos promocoes ativas. volte em breve!'

            resultado = 'Promocoes ativas:\n\n'
            for i, p in enumerate(promocoes, 1):
                desconto = f' - {p.percentual_desconto}% OFF' if p.percentual_desconto else ''
                resultado += f'{i}. {p.nome}{desconto}\n'
                if p.data_fim:
                    resultado += f'   Valide ate: {p.data_fim.strftime("%d/%m/%Y")}\n'
                resultado += '\n'
            resultado += '1 - Ver mais promocoes\n0 - Voltar ao menu'
            return resultado
        except Exception:
            return 'No momento nao temos promocoes ativas. volte em breve!'

    def _processar_pedido(self, numero_pedido):
        self.conversa.etapa = 'menu_principal'
        self.conversa.save()

        try:
            from pedidos.models import Pedido
            pedido = Pedido.objects.filter(
                empresa=self.empresa,
                numero_pedido=numero_pedido.upper(),
            ).first()

            if not pedido:
                return f'Pedido {numero_pedido} nao encontrado. Verifique o numero e tente novamente.\n\n0 - Voltar ao menu'

            status_map = {
                'pendente': 'Pendente',
                'confirmado': 'Confirmado',
                'em_separacao': 'Em separacao',
                'enviado': 'Enviado',
                'entregue': 'Entregue',
                'cancelado': 'Cancelado',
            }
            status_display = status_map.get(pedido.status, pedido.status)
            resultado = (
                f'Pedido {pedido.numero_pedido}:\n'
                f'Status: {status_display}\n'
            )
            if pedido.total:
                resultado += f'Total: R$ {pedido.total:.2f}\n'
            if pedido.status == 'enviado' and pedido.codigo_rastreio:
                resultado += f'Rastreio: {pedido.codigo_rastreio}\n'
            resultado += '\n0 - Voltar ao menu'
            return resultado
        except Exception:
            return f'Pedido {numero_pedido} nao encontrado. Verifique o numero e tente novamente.\n\n0 - Voltar ao menu'

    def _horario_funcionamento(self):
        agora = timezone.localtime()
        dia_semana = agora.weekday()

        horarios = {
            0: 'Segunda-feira: 08h as 18h',
            1: 'Terca-feira: 08h as 18h',
            2: 'Quarta-feira: 08h as 18h',
            3: 'Quinta-feira: 08h as 18h',
            4: 'Sexta-feira: 08h as 18h',
            5: 'Sabado: 08h as 14h',
            6: 'Domingo: FECHADO',
        }

        resultado = 'Horario de funcionamento:\n\n'
        for dia, horario in horarios.items():
            marcador = ' >> HOJE' if dia == dia_semana else ''
            resultado += f'{horario}{marcador}\n'

        if dia_semana == 6:
            resultado += '\nHoje estamos fechados. Volte amanha!'
        else:
            hora_atual = agora.hour
            if hora_atual < 8:
                resultado += '\nAinda estamos fechados. Abrimos as 08h!'
            elif hora_atual >= 18 or (dia_semana == 5 and hora_atual >= 14):
                resultado += '\nJa fechamos hoje. Volte amanha!'
            else:
                resultado += '\nEstamos abertos agora! Venha nos visitar!'

        resultado += '\n\n0 - Voltar ao menu'
        return resultado

    def _endereco(self):
        if self.empresa and hasattr(self.empresa, 'endereco'):
            endereco_parts = []
            if self.empresa.endereco:
                endereco_parts.append(self.empresa.endereco)
            if self.empresa.bairro:
                endereco_parts.append(self.empresa.bairro)
            if self.empresa.cidade:
                endereco_parts.append(self.empresa.cidade)
            if self.empresa.uf:
                endereco_parts.append(self.empresa.uf)
            if self.empresa.cep:
                endereco_parts.append(f'CEP: {self.empresa.cep}')

            if endereco_parts:
                resultado = 'Nosso endereco:\n\n'
                resultado += '\n'.join(endereco_parts)
                if self.empresa.telefone:
                    resultado += f'\n\nTelefone: {self.empresa.telefone}'
                resultado += '\n\n0 - Voltar ao menu'
                return resultado
        return 'Endereco nao cadastrado. Entre em contato conosco.\n\n0 - Voltar ao menu'
