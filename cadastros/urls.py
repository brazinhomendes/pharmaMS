from django.urls import path
from . import views

app_name = 'cadastros'

urlpatterns = [
    path('produtos/', views.produtos, name='produtos'),
    path('produtos/novo/', views.produto_novo, name='produto_novo'),
    path('produtos/<int:pk>/editar/', views.produto_editar, name='produto_editar'),
    path('produtos/<int:pk>/', views.produto_detalhe, name='produto_detalhe'),
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/novo/', views.cliente_novo, name='cliente_novo'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente_editar'),
    path('fornecedores/', views.fornecedores, name='fornecedores'),
    path('fornecedores/novo/', views.fornecedor_novo, name='fornecedor_novo'),
    path('fornecedores/<int:pk>/editar/', views.fornecedor_editar, name='fornecedor_editar'),
    path('api/produtos/buscar/', views.api_buscar_produto, name='api_buscar_produto'),
    path('etiquetas/', views.etiquetas_lista, name='etiquetas_lista'),
    path('etiquetas/modelos/', views.etiquetas_modelos, name='etiquetas_modelos'),
    path('etiquetas/modelos/novo/', views.etiqueta_modelo_novo, name='etiqueta_modelo_novo'),
    path('etiquetas/modelos/<int:pk>/editar/', views.etiqueta_modelo_editar, name='etiqueta_modelo_editar'),
    path('etiquetas/imprimir/', views.etiquetas_imprimir, name='etiquetas_imprimir'),
    path('etiquetas/<int:pk>/pdf/', views.etiquetas_pdf, name='etiquetas_pdf'),
    path('curva-abc/', views.curva_abc, name='curva_abc'),
    path('curva-abc/calcular/', views.curva_abc_calcular, name='curva_abc_calcular'),
    path('api/curva-abc/', views.api_curva_abc, name='api_curva_abc'),
]
