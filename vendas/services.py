from datetime import date
from .models import RegraComissao, ComissaoVenda, Promocao


def aplicar_promocoes(venda):
    today = date.today()
    weekday = str(today.isoweekday())

    promos = Promocao.objects.filter(
        empresa=venda.empresa,
        ativo=True,
        data_inicio__lte=today,
        data_fim__gte=today,
    )
    promos_lista = [p for p in promos if not p.dias_semana or weekday in p.dias_semana.split(',')]

    total_desconto = 0

    for item in venda.itens.all():
        if not item.produto_id:
            continue

        promo = next(
            (p for p in promos_lista if p.tipo == 'produto' and p.produto_id == item.produto_id),
            None
        )

        if not promo and item.produto.classe_terapeutica_id:
            promo = next(
                (p for p in promos_lista if p.tipo == 'classe' and p.classe_terapeutica_id == item.produto.classe_terapeutica_id),
                None
            )

        if not promo:
            promo = next((p for p in promos_lista if p.tipo == 'geral'), None)

        if not promo:
            continue

        quantidade = item.quantidade
        preco_atual = float(item.preco_unitario)
        novo_preco = preco_atual

        if promo.tipo == 'quantidade':
            if promo.quantidade_minima and quantidade >= promo.quantidade_minima:
                pague = promo.quantidade_cobrar or promo.quantidade_minima
                novo_preco = round(preco_atual * pague / quantidade, 2)
        elif promo.tipo == 'combo':
            if promo.preco_promocional:
                novo_preco = round(float(promo.preco_promocional) / quantidade, 2)
        elif promo.percentual_desconto:
            novo_preco = round(preco_atual * (1 - float(promo.percentual_desconto) / 100), 2)

        if novo_preco != preco_atual:
            item.preco_unitario = novo_preco
            item.subtotal = round(novo_preco * quantidade, 2)
            item.save()
            total_desconto += round((preco_atual - novo_preco) * quantidade, 2)

    return total_desconto


def calcular_comissao(venda):
    vendedor = venda.vendedor
    if not vendedor:
        return

    regras = RegraComissao.objects.filter(
        empresa=venda.empresa,
        ativo=True,
        data_inicio__lte=date.today(),
    ).filter(
        data_fim__isnull=True
    ) | RegraComissao.objects.filter(
        empresa=venda.empresa,
        ativo=True,
        data_inicio__lte=date.today(),
        data_fim__gte=date.today(),
    )

    regras_geral = regras.filter(tipo='geral').first()
    regras_vendedor = regras.filter(tipo='vendedor', vendedor=vendedor).first()

    for item in venda.itens.all():
        percentual = None

        regra_produto = regras.filter(
            tipo='produto', produto=item.produto
        ).first()
        if regra_produto:
            percentual = regra_produto.percentual

        if percentual is None and item.produto.classe_terapeutica:
            regra_classe = regras.filter(
                tipo='classe',
                classe_terapeutica=item.produto.classe_terapeutica,
            ).first()
            if regra_classe:
                percentual = regra_classe.percentual

        if percentual is None and regras_vendedor:
            percentual = regras_vendedor.percentual

        if percentual is None and regras_geral:
            percentual = regras_geral.percentual

        if percentual is not None:
            ComissaoVenda.objects.create(
                empresa=venda.empresa,
                venda=venda,
                vendedor=vendedor,
                item_venda=item,
                percentual=percentual,
                valor_base=item.subtotal,
                valor_comissao=item.subtotal * percentual / 100,
            )
