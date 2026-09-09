from django.db.models import Sum, F
from django.utils import timezone
from .models import Produto, ClassificacaoABC
from vendas.models import Venda, ItemVenda


class ABCService:
    def calcular(self, empresa, data_inicio, data_fim):
        vendas = Venda.objects.filter(
            empresa=empresa,
            status='finalizada',
            data_venda__date__gte=data_inicio,
            data_venda__date__lte=data_fim,
        )
        if not vendas.exists():
            return {'total_produtos': 0, 'total_vendas': 0, 'a': 0, 'b': 0, 'c': 0}

        itens = ItemVenda.objects.filter(
            venda__in=vendas
        ).values('produto').annotate(
            total_vendido=Sum(F('quantidade') * F('preco_unitario'))
        ).order_by('-total_vendido')

        total_geral = sum(item['total_vendido'] or 0 for item in itens)
        if total_geral == 0:
            return {'total_produtos': 0, 'total_vendas': 0, 'a': 0, 'b': 0, 'c': 0}

        acumulado = 0
        for item in itens:
            item['percentual'] = (item['total_vendido'] or 0) / total_geral * 100
            acumulado += item['percentual']
            if acumulado <= 80:
                item['classe'] = 'A'
            elif acumulado <= 95:
                item['classe'] = 'B'
            else:
                item['classe'] = 'C'

        hoje = timezone.localdate()
        for item in itens:
            Produto.objects.filter(pk=item['produto'], empresa=empresa).update(
                curva_abc=item['classe'],
                ultima_classificacao_abc=hoje,
            )

        ClassificacaoABC.objects.create(
            empresa=empresa,
            total_produtos=itens.count(),
            total_vendas_periodo=total_geral,
            concluida=True,
        )

        contagens = {'A': 0, 'B': 0, 'C': 0}
        for item in itens:
            contagens[item['classe']] += 1

        return {
            'total_produtos': itens.count(),
            'total_vendas': total_geral,
            'a': contagens['A'],
            'b': contagens['B'],
            'c': contagens['C'],
        }
