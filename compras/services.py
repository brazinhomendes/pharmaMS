from datetime import date
from django.db.models import Sum, Count
from .models import SugestaoCompra, ItemSugestaoCompra
from cadastros.models import Produto
from estoque.models import Lote
from vendas.models import Venda, ItemVenda


class SugestaoCompraService:

    @staticmethod
    def gerar_sugestoes(empresa, data_inicio, data_fim, apenas_curva_a=False):
        produtos = Produto.objects.filter(empresa=empresa, estoque_minimo__gt=0)
        if apenas_curva_a:
            produtos = produtos.filter(curva_abc='A')

        sugestao = SugestaoCompra.objects.create(
            empresa=empresa,
            data_inicio_analise=data_inicio,
            data_fim_analise=data_fim,
        )

        days_in_period = (data_fim - data_inicio).days or 1

        for produto in produtos:
            estoque_atual = Lote.objects.filter(
                empresa=empresa, produto=produto
            ).aggregate(total=Sum('quantidade'))['total'] or 0

            vendas_periodo = ItemVenda.objects.filter(
                produto=produto,
                venda__empresa=empresa,
                venda__status='finalizada',
                venda__data_venda__date__gte=data_inicio,
                venda__data_venda__date__lte=data_fim,
            ).aggregate(total=Count('id'))['total'] or 0

            if vendas_periodo > 0:
                daily_sales = vendas_periodo / days_in_period
                dias_estoque = int(estoque_atual / daily_sales) if daily_sales > 0 else 999
                sugestao_compra = max(0, int((daily_sales * 30) - estoque_atual))
            else:
                daily_sales = 0
                dias_estoque = 999
                sugestao_compra = 0

            if dias_estoque < 15:
                prioridade = 'alta'
            elif dias_estoque < 30:
                prioridade = 'media'
            else:
                prioridade = 'baixa'

            ItemSugestaoCompra.objects.create(
                sugestao=sugestao,
                produto=produto,
                estoque_atual=estoque_atual,
                estoque_minimo=produto.estoque_minimo,
                vendas_periodo=vendas_periodo,
                dias_estoque=dias_estoque,
                sugestao_compra=sugestao_compra,
                prioridade=prioridade,
            )

        return sugestao
