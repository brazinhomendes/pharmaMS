from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import (
    MedicamentoControlado, Receituario, ItemReceituario,
    ProfissionalSaude, MovimentacaoSNGPC, RelatorioSNGPC, ClasseTerapeuticaSNGPC,
)


@login_required
def index(request):
    empresa = request.empresa
    controlados_count = MedicamentoControlado.objects.filter(empresa=empresa).count()
    receitas_count = Receituario.objects.filter(empresa=empresa).count()
    movimentos_count = MovimentacaoSNGPC.objects.filter(empresa=empresa).count()
    relatorios_count = RelatorioSNGPC.objects.filter(empresa=empresa).count()
    return render(request, 'sngpc/index.html', {
        'controlados_count': controlados_count,
        'receitas_count': receitas_count,
        'movimentos_count': movimentos_count,
        'relatorios_count': relatorios_count,
    })


@login_required
def controlados(request):
    empresa = request.empresa
    medicamentos = MedicamentoControlado.objects.filter(
        empresa=empresa
    ).select_related('produto', 'classe_terapeutica')
    return render(request, 'sngpc/controlados.html', {
        'medicamentos': medicamentos,
    })


@login_required
def receitas(request):
    empresa = request.empresa
    receituarios = Receituario.objects.filter(
        empresa=empresa
    ).select_related('profissional')
    return render(request, 'sngpc/receitas.html', {
        'receituarios': receituarios,
    })


@login_required
def receita_nova(request):
    empresa = request.empresa
    if request.method == 'POST':
        profissional_id = request.POST.get('profissional')
        profissional = get_object_or_404(ProfissionalSaude, pk=profissional_id)
        receita = Receituario.objects.create(
            empresa=empresa,
            numero_receita=request.POST.get('numero_receita'),
            paciente_nome=request.POST.get('paciente_nome'),
            paciente_cpf=request.POST.get('paciente_cpf', ''),
            profissional=profissional,
            data_emissao=request.POST.get('data_emissao'),
            data_validade=request.POST.get('data_validade'),
            observacoes=request.POST.get('observacoes', ''),
        )
        medicamento_ids = request.POST.getlist('medicamento')
        quantidades = request.POST.getlist('quantidade')
        posologias = request.POST.getlist('posologia')
        for i, med_id in enumerate(medicamento_ids):
            if med_id:
                medicamento = get_object_or_404(MedicamentoControlado, pk=med_id)
                qtd = quantidades[i] if i < len(quantidades) else 1
                pos = posologias[i] if i < len(posologias) else ''
                ItemReceituario.objects.create(
                    receituario=receita,
                    medicamento=medicamento,
                    quantidade=qtd,
                    posologia=pos,
                )
        messages.success(request, f'Receita #{receita.numero_receita} cadastrada.')
        return redirect('sngpc:receitas')
    profissionais = ProfissionalSaude.objects.filter(ativo=True)
    medicamentos = MedicamentoControlado.objects.filter(empresa=empresa).select_related('produto')
    return render(request, 'sngpc/receita_form.html', {
        'profissionais': profissionais,
        'medicamentos': medicamentos,
    })


@login_required
def movimentos(request):
    empresa = request.empresa
    movimentacoes = MovimentacaoSNGPC.objects.filter(
        empresa=empresa
    ).select_related('medicamento', 'medicamento__produto', 'receituario')
    return render(request, 'sngpc/movimentos.html', {
        'movimentacoes': movimentacoes,
    })


@login_required
def relatorios(request):
    empresa = request.empresa
    relatorios_list = RelatorioSNGPC.objects.filter(empresa=empresa)
    return render(request, 'sngpc/relatorios.html', {
        'relatorios': relatorios_list,
    })


@login_required
def gerar_relatorio(request):
    empresa = request.empresa
    if request.method == 'POST':
        RelatorioSNGPC.objects.create(
            empresa=empresa,
            tipo=request.POST.get('tipo'),
            periodo_inicio=request.POST.get('periodo_inicio'),
            periodo_fim=request.POST.get('periodo_fim'),
        )
        messages.success(request, 'Relatório SNGPC gerado com sucesso.')
        return redirect('sngpc:relatorios')
    return redirect('sngpc:relatorios')
