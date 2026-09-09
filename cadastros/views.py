from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Produto, Cliente, Fornecedor, ClasseTerapeutica, Laboratorio, ClassificacaoABC
from .services import ABCService
from .models import ModeloEtiqueta, ImpressaoEtiqueta, ItemImpressaoEtiqueta
from estoque.models import Lote


@login_required
def produtos(request):
    empresa = request.empresa
    lista = Produto.objects.filter(empresa=empresa)
    return render(request, 'cadastros/produtos.html', {'produtos': lista})


@login_required
def produto_novo(request):
    empresa = request.empresa
    classes = ClasseTerapeutica.objects.filter(ativo=True)
    laboratorios = Laboratorio.objects.filter(ativo=True)

    if request.method == 'POST':
        dados = request.POST
        produto = Produto.objects.create(
            empresa=empresa,
            codigo_barras=dados.get('codigo_barras', ''),
            nome=dados['nome'],
            descricao=dados.get('descricao', ''),
            classe_terapeutica_id=dados.get('classe_terapeutica') or None,
            laboratorio_id=dados.get('laboratorio') or None,
            principio_ativo=dados.get('principio_ativo', ''),
            concentracao=dados.get('concentracao', ''),
            tipo_medicamento=dados.get('tipo_medicamento', 'comum'),
            precisa_receita=dados.get('precisa_receita') == 'on',
            unidade=dados.get('unidade', 'UN'),
            preco_custo=dados.get('preco_custo', 0),
            preco_venda=dados.get('preco_venda', 0),
            margem_lucro=dados.get('margem_lucro', 0),
            ncm=dados.get('ncm', ''),
            cest=dados.get('cest', ''),
            codigo_anvisa=dados.get('codigo_anvisa', ''),
            estoque_minimo=dados.get('estoque_minimo', 0),
            estoque_maximo=dados.get('estoque_maximo', 0),
            controlado_anvisa=dados.get('controlado_anvisa') == 'on',
        )
        messages.success(request, 'Produto cadastrado com sucesso.')
        return redirect('cadastros:produtos')

    return render(request, 'cadastros/produto_form.html', {
        'classes': classes,
        'laboratorios': laboratorios,
    })


@login_required
def produto_editar(request, pk):
    empresa = request.empresa
    produto = get_object_or_404(Produto, pk=pk, empresa=empresa)
    classes = ClasseTerapeutica.objects.filter(ativo=True)
    laboratorios = Laboratorio.objects.filter(ativo=True)

    if request.method == 'POST':
        dados = request.POST
        produto.codigo_barras = dados.get('codigo_barras', '')
        produto.nome = dados['nome']
        produto.descricao = dados.get('descricao', '')
        produto.classe_terapeutica_id = dados.get('classe_terapeutica') or None
        produto.laboratorio_id = dados.get('laboratorio') or None
        produto.principio_ativo = dados.get('principio_ativo', '')
        produto.concentracao = dados.get('concentracao', '')
        produto.tipo_medicamento = dados.get('tipo_medicamento', 'comum')
        produto.precisa_receita = dados.get('precisa_receita') == 'on'
        produto.unidade = dados.get('unidade', 'UN')
        produto.preco_custo = dados.get('preco_custo', 0)
        produto.preco_venda = dados.get('preco_venda', 0)
        produto.margem_lucro = dados.get('margem_lucro', 0)
        produto.ncm = dados.get('ncm', '')
        produto.cest = dados.get('cest', '')
        produto.codigo_anvisa = dados.get('codigo_anvisa', '')
        produto.estoque_minimo = dados.get('estoque_minimo', 0)
        produto.estoque_maximo = dados.get('estoque_maximo', 0)
        produto.controlado_anvisa = dados.get('controlado_anvisa') == 'on'
        produto.save()
        messages.success(request, 'Produto atualizado com sucesso.')
        return redirect('cadastros:produtos')

    return render(request, 'cadastros/produto_form.html', {
        'produto': produto,
        'classes': classes,
        'laboratorios': laboratorios,
    })


@login_required
def produto_detalhe(request, pk):
    empresa = request.empresa
    produto = get_object_or_404(Produto, pk=pk, empresa=empresa)
    return render(request, 'cadastros/produto_detalhe.html', {'produto': produto})


@login_required
def clientes(request):
    empresa = request.empresa
    lista = Cliente.objects.filter(empresa=empresa)
    return render(request, 'cadastros/clientes.html', {'clientes': lista})


@login_required
def cliente_novo(request):
    empresa = request.empresa
    if request.method == 'POST':
        dados = request.POST
        Cliente.objects.create(
            empresa=empresa,
            nome=dados['nome'],
            cpf_cnpj=dados.get('cpf_cnpj', ''),
            rg=dados.get('rg', ''),
            data_nascimento=dados.get('data_nascimento') or None,
            endereco=dados.get('endereco', ''),
            bairro=dados.get('bairro', ''),
            cidade=dados.get('cidade', ''),
            uf=dados.get('uf', ''),
            cep=dados.get('cep', ''),
            telefone=dados.get('telefone', ''),
            celular=dados.get('celular', ''),
            email=dados.get('email', ''),
            sexo=dados.get('sexo', ''),
            observacoes=dados.get('observacoes', ''),
        )
        messages.success(request, 'Cliente cadastrado com sucesso.')
        return redirect('cadastros:clientes')
    return render(request, 'cadastros/cliente_form.html')


@login_required
def cliente_editar(request, pk):
    empresa = request.empresa
    cliente = get_object_or_404(Cliente, pk=pk, empresa=empresa)
    if request.method == 'POST':
        dados = request.POST
        cliente.nome = dados['nome']
        cliente.cpf_cnpj = dados.get('cpf_cnpj', '')
        cliente.rg = dados.get('rg', '')
        cliente.data_nascimento = dados.get('data_nascimento') or None
        cliente.endereco = dados.get('endereco', '')
        cliente.bairro = dados.get('bairro', '')
        cliente.cidade = dados.get('cidade', '')
        cliente.uf = dados.get('uf', '')
        cliente.cep = dados.get('cep', '')
        cliente.telefone = dados.get('telefone', '')
        cliente.celular = dados.get('celular', '')
        cliente.email = dados.get('email', '')
        cliente.sexo = dados.get('sexo', '')
        cliente.observacoes = dados.get('observacoes', '')
        cliente.save()
        messages.success(request, 'Cliente atualizado com sucesso.')
        return redirect('cadastros:clientes')
    return render(request, 'cadastros/cliente_form.html', {'cliente': cliente})


@login_required
def fornecedores(request):
    empresa = request.empresa
    lista = Fornecedor.objects.filter(empresa=empresa)
    return render(request, 'cadastros/fornecedores.html', {'fornecedores': lista})


@login_required
def fornecedor_novo(request):
    empresa = request.empresa
    if request.method == 'POST':
        dados = request.POST
        Fornecedor.objects.create(
            empresa=empresa,
            nome=dados['nome'],
            cnpj=dados.get('cnpj', ''),
            ie=dados.get('ie', ''),
            endereco=dados.get('endereco', ''),
            bairro=dados.get('bairro', ''),
            cidade=dados.get('cidade', ''),
            uf=dados.get('uf', ''),
            cep=dados.get('cep', ''),
            telefone=dados.get('telefone', ''),
            celular=dados.get('celular', ''),
            email=dados.get('email', ''),
            contato_nome=dados.get('contato_nome', ''),
            observacoes=dados.get('observacoes', ''),
        )
        messages.success(request, 'Fornecedor cadastrado com sucesso.')
        return redirect('cadastros:fornecedores')
    return render(request, 'cadastros/fornecedor_form.html')


@login_required
def fornecedor_editar(request, pk):
    empresa = request.empresa
    fornecedor = get_object_or_404(Fornecedor, pk=pk, empresa=empresa)
    if request.method == 'POST':
        dados = request.POST
        fornecedor.nome = dados['nome']
        fornecedor.cnpj = dados.get('cnpj', '')
        fornecedor.ie = dados.get('ie', '')
        fornecedor.endereco = dados.get('endereco', '')
        fornecedor.bairro = dados.get('bairro', '')
        fornecedor.cidade = dados.get('cidade', '')
        fornecedor.uf = dados.get('uf', '')
        fornecedor.cep = dados.get('cep', '')
        fornecedor.telefone = dados.get('telefone', '')
        fornecedor.celular = dados.get('celular', '')
        fornecedor.email = dados.get('email', '')
        fornecedor.contato_nome = dados.get('contato_nome', '')
        fornecedor.observacoes = dados.get('observacoes', '')
        fornecedor.save()
        messages.success(request, 'Fornecedor atualizado com sucesso.')
        return redirect('cadastros:fornecedores')
    return render(request, 'cadastros/fornecedor_form.html', {'fornecedor': fornecedor})


@login_required
def api_buscar_produto(request):
    empresa = request.empresa
    termo = request.GET.get('q', '')
    if not empresa or not termo:
        return JsonResponse([], safe=False)
    produtos = Produto.objects.filter(empresa=empresa, nome__icontains=termo)[:20]
    resultados = [
        {
            'id': p.id,
            'nome': p.nome,
            'preco_venda': str(p.preco_venda),
            'codigo_barras': p.codigo_barras,
        }
        for p in produtos
    ]
    return JsonResponse(resultados, safe=False)


@login_required
def curva_abc(request):
    empresa = request.empresa
    ultima = ClassificacaoABC.objects.filter(empresa=empresa).first()
    produtos_a = Produto.objects.filter(empresa=empresa, curva_abc='A')
    produtos_b = Produto.objects.filter(empresa=empresa, curva_abc='B')
    produtos_c = Produto.objects.filter(empresa=empresa, curva_abc='C')
    context = {
        'total_a': produtos_a.count(),
        'total_b': produtos_b.count(),
        'total_c': produtos_c.count(),
        'produtos_a': produtos_a,
        'produtos_b': produtos_b,
        'produtos_c': produtos_c,
        'ultima_classificacao': ultima,
    }
    return render(request, 'cadastros/curva_abc.html', context)


@login_required
def curva_abc_calcular(request):
    if request.method == 'POST':
        empresa = request.empresa
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        if not data_inicio or not data_fim:
            messages.error(request, 'Informe o período para o cálculo.')
            return redirect('cadastros:curva_abc')
        service = ABCService()
        stats = service.calcular(empresa, data_inicio, data_fim)
        messages.success(
            request,
            f'ABC calculado: A={stats["a"]}, B={stats["b"]}, C={stats["c"]} '
            f'- Total produtos: {stats["total_produtos"]}'
        )
        return redirect('cadastros:curva_abc')
    return redirect('cadastros:curva_abc')


@login_required
def api_curva_abc(request):
    empresa = request.empresa
    total_a = Produto.objects.filter(empresa=empresa, curva_abc='A').count()
    total_b = Produto.objects.filter(empresa=empresa, curva_abc='B').count()
    total_c = Produto.objects.filter(empresa=empresa, curva_abc='C').count()
    ultima = ClassificacaoABC.objects.filter(empresa=empresa).first()
    return JsonResponse({
        'A': total_a,
        'B': total_b,
        'C': total_c,
        'ultima_classificacao': ultima.data_calculo.isoformat() if ultima else None,
    })


@login_required
def etiquetas_lista(request):
    empresa = request.empresa
    lista = ImpressaoEtiqueta.objects.filter(empresa=empresa).select_related('modelo', 'usuario')
    return render(request, 'cadastros/etiquetas.html', {'impressoes': lista})


@login_required
def etiquetas_modelos(request):
    empresa = request.empresa
    lista = ModeloEtiqueta.objects.filter(ativo=True)
    return render(request, 'cadastros/etiquetas_modelos.html', {'modelos': lista})


@login_required
def etiqueta_modelo_novo(request):
    if request.method == 'POST':
        dados = request.POST
        ModeloEtiqueta.objects.create(
            nome=dados['nome'],
            largura_mm=dados.get('largura_mm', 40),
            altura_mm=dados.get('altura_mm', 25),
            margem_superior=dados.get('margem_superior', 3),
            margem_inferior=dados.get('margem_inferior', 3),
            margem_esquerda=dados.get('margem_esquerda', 3),
            margem_direita=dados.get('margem_direita', 3),
            colunas=dados.get('colunas', 3),
            linhas=dados.get('linhas', 8),
            mostrar_nome=dados.get('mostrar_nome') == 'on',
            mostrar_preco=dados.get('mostrar_preco') == 'on',
            mostrar_codigo_barras=dados.get('mostrar_codigo_barras') == 'on',
            mostrar_preco_custo=dados.get('mostrar_preco_custo') == 'on',
            mostrar_laboratorio=dados.get('mostrar_laboratorio') == 'on',
            mostrar_validade=dados.get('mostrar_validade') == 'on',
            fonte_tamanho=dados.get('fonte_tamanho', 10),
            cabecalho=dados.get('cabecalho', ''),
            rodape=dados.get('rodape', ''),
        )
        messages.success(request, 'Modelo de etiqueta criado com sucesso.')
        return redirect('cadastros:etiquetas_modelos')
    return render(request, 'cadastros/etiqueta_modelo_form.html')


@login_required
def etiqueta_modelo_editar(request, pk):
    modelo = get_object_or_404(ModeloEtiqueta, pk=pk)
    if request.method == 'POST':
        dados = request.POST
        modelo.nome = dados['nome']
        modelo.largura_mm = dados.get('largura_mm', 40)
        modelo.altura_mm = dados.get('altura_mm', 25)
        modelo.margem_superior = dados.get('margem_superior', 3)
        modelo.margem_inferior = dados.get('margem_inferior', 3)
        modelo.margem_esquerda = dados.get('margem_esquerda', 3)
        modelo.margem_direita = dados.get('margem_direita', 3)
        modelo.colunas = dados.get('colunas', 3)
        modelo.linhas = dados.get('linhas', 8)
        modelo.mostrar_nome = dados.get('mostrar_nome') == 'on'
        modelo.mostrar_preco = dados.get('mostrar_preco') == 'on'
        modelo.mostrar_codigo_barras = dados.get('mostrar_codigo_barras') == 'on'
        modelo.mostrar_preco_custo = dados.get('mostrar_preco_custo') == 'on'
        modelo.mostrar_laboratorio = dados.get('mostrar_laboratorio') == 'on'
        modelo.mostrar_validade = dados.get('mostrar_validade') == 'on'
        modelo.fonte_tamanho = dados.get('fonte_tamanho', 10)
        modelo.cabecalho = dados.get('cabecalho', '')
        modelo.rodape = dados.get('rodape', '')
        modelo.save()
        messages.success(request, 'Modelo de etiqueta atualizado com sucesso.')
        return redirect('cadastros:etiquetas_modelos')
    return render(request, 'cadastros/etiqueta_modelo_form.html', {'modelo': modelo})


@login_required
def etiquetas_imprimir(request):
    empresa = request.empresa
    modelos = ModeloEtiqueta.objects.filter(ativo=True)
    classes = ClasseTerapeutica.objects.filter(ativo=True)

    produtos = Produto.objects.filter(empresa=empresa, ativo=True).order_by('nome')

    if request.method == 'POST':
        dados = request.POST
        modelo_id = dados.get('modelo')
        tipo_origem = dados.get('tipo_origem', 'produto')
        quantidade_copias = int(dados.get('quantidade_copias', 1))
        produtos_ids = dados.getlist('produtos')
        classe_id = dados.get('classe_terapeutica')

        if not modelo_id:
            messages.error(request, 'Selecione um modelo de etiqueta.')
            return render(request, 'cadastros/etiquetas_imprimir.html', {'modelos': modelos, 'classes': classes, 'produtos': produtos})

        if tipo_origem == 'todos':
            produtos = Produto.objects.filter(empresa=empresa, ativo=True)
        elif tipo_origem == 'classe' and classe_id:
            produtos = Produto.objects.filter(empresa=empresa, ativo=True, classe_terapeutica_id=classe_id)
        elif tipo_origem == 'produto' and produtos_ids:
            produtos = Produto.objects.filter(empresa=empresa, ativo=True, pk__in=produtos_ids)
        elif tipo_origem == 'lote' and produtos_ids:
            produtos = Produto.objects.filter(empresa=empresa, ativo=True, pk__in=produtos_ids)
        else:
            messages.error(request, 'Selecione os produtos ou uma origem válida.')
            return render(request, 'cadastros/etiquetas_imprimir.html', {'modelos': modelos, 'classes': classes, 'produtos': produtos})

        if not produtos.exists():
            messages.error(request, 'Nenhum produto encontrado para imprimir.')
            return render(request, 'cadastros/etiquetas_imprimir.html', {'modelos': modelos, 'classes': classes, 'produtos': produtos})

        impressao = ImpressaoEtiqueta.objects.create(
            empresa=empresa,
            modelo_id=modelo_id,
            tipo_origem=tipo_origem,
            usuario=request.user,
            quantidade_copias=quantidade_copias,
        )

        for produto in produtos:
            lote = None
            if tipo_origem == 'lote':
                lote = Lote.objects.filter(produto=produto, empresa=empresa).order_by('-data_validade').first()
            ItemImpressaoEtiqueta.objects.create(
                impressao=impressao,
                produto=produto,
                lote=lote,
                quantidade=quantidade_copias,
            )

        messages.success(request, 'Impressão de etiquetas criada com sucesso.')
        return redirect('cadastros:etiquetas_pdf', pk=impressao.pk)

    return render(request, 'cadastros/etiquetas_imprimir.html', {'modelos': modelos, 'classes': classes, 'produtos': produtos})


@login_required
def etiquetas_pdf(request, pk):
    empresa = request.empresa
    impressao = get_object_or_404(ImpressaoEtiqueta, pk=pk, empresa=empresa)
    itens = impressao.itens.select_related('produto', 'lote').all()
    modelo = impressao.modelo

    labels = []
    for item in itens:
        for _ in range(item.quantidade):
            labels.append(item)

    return render(request, 'cadastros/etiquetas_pdf.html', {
        'impressao': impressao,
        'modelo': modelo,
        'itens': itens,
        'labels': labels,
    })
