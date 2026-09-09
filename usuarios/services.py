from django.utils import timezone
from .models import SolicitacaoLiberacao, RegraLiberacao, HistoricoCancelamento, tem_perfil_aprovador


class LiberacaoService:

    @staticmethod
    def solicitar(tipo, usuario, empresa, objeto=None, motivo='', valor=None):
        regras = RegraLiberacao.objects.filter(
            empresa=empresa, tipo=tipo, ativo=True
        )
        precisa_aprovacao = False
        for regra in regras:
            if valor is not None and valor < regra.valor_minimo:
                continue
            if not _usuario_tem_perfil(usuario, regra.perfil_aprovador):
                precisa_aprovacao = True
                break

        if not precisa_aprovacao:
            return True, None

        solicitacao = SolicitacaoLiberacao.objects.create(
            empresa=empresa,
            tipo=tipo,
            usuario=usuario,
            motivo=motivo,
        )
        if objeto:
            _associar_objeto(solicitacao, tipo, objeto)

        return False, solicitacao

    @staticmethod
    def aprovar(solicitacao, aprovador):
        solicitacao.status = 'aprovado'
        solicitacao.aprovador = aprovador
        solicitacao.data_aprovacao = timezone.now()
        solicitacao.save()

        tipo = solicitacao.tipo
        objeto = _get_objeto(solicitacao)

        if tipo == 'cancelar_venda' and solicitacao.venda:
            solicitacao.venda.status = 'cancelada'
            solicitacao.venda.save()
            HistoricoCancelamento.objects.create(
                empresa=solicitacao.empresa,
                tipo='venda',
                objeto_id=solicitacao.venda.id,
                objeto_str=str(solicitacao.venda),
                usuario=aprovador,
                motivo=solicitacao.motivo,
                liberacao=solicitacao,
            )

        elif tipo == 'cancelar_dav' and solicitacao.dav:
            solicitacao.dav.status = 'cancelado'
            solicitacao.dav.save()
            HistoricoCancelamento.objects.create(
                empresa=solicitacao.empresa,
                tipo='dav',
                objeto_id=solicitacao.dav.id,
                objeto_str=str(solicitacao.dav),
                usuario=aprovador,
                motivo=solicitacao.motivo,
                liberacao=solicitacao,
            )

        elif tipo == 'cancelar_nfce' and solicitacao.nfce:
            solicitacao.nfce.status = 'cancelada'
            solicitacao.nfce.save()
            HistoricoCancelamento.objects.create(
                empresa=solicitacao.empresa,
                tipo='nfce',
                objeto_id=solicitacao.nfce.id,
                objeto_str=str(solicitacao.nfce),
                usuario=aprovador,
                motivo=solicitacao.motivo,
                liberacao=solicitacao,
            )

    @staticmethod
    def rejeitar(solicitacao, aprovador, observacao=''):
        solicitacao.status = 'rejeitado'
        solicitacao.aprovador = aprovador
        solicitacao.observacao_aprovador = observacao
        solicitacao.data_aprovacao = timezone.now()
        solicitacao.save()


def _usuario_tem_perfil(user, perfil_necessario):
    if perfil_necessario == 'admin':
        return user.perfil in ('admin_master', 'admin_empresa')
    return user.perfil == perfil_necessario


def _associar_objeto(solicitacao, tipo, objeto):
    if tipo == 'cancelar_venda':
        solicitacao.venda = objeto
    elif tipo == 'cancelar_dav':
        solicitacao.dav = objeto
    elif tipo == 'cancelar_nfce':
        solicitacao.nfce = objeto
    if objeto:
        solicitacao.save()


def _get_objeto(solicitacao):
    return (
        solicitacao.venda or solicitacao.dav or solicitacao.nfce
    )
