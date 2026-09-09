from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Empresa
from .forms import EmpresaForm


@login_required
def lista(request):
    empresas = Empresa.objects.all()
    return render(request, 'empresas/lista.html', {'empresas': empresas})


@login_required
def nova(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('empresas:lista')
    else:
        form = EmpresaForm()
    return render(request, 'empresas/form.html', {'form': form})


@login_required
def editar(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            form.save()
            return redirect('empresas:lista')
    else:
        form = EmpresaForm(instance=empresa)
    return render(request, 'empresas/form.html', {'form': form})
