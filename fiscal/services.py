from datetime import datetime
from decimal import Decimal
from django.db import transaction
from .models import NFCe, ConfiguracaoFiscal, NFe


class NFCeService:

    UF_PARA_CODIGO = {
        'RO': '11', 'AC': '12', 'AM': '13', 'RR': '14', 'PA': '15',
        'AP': '16', 'TO': '17', 'MA': '21', 'PI': '22', 'CE': '23',
        'RN': '24', 'PB': '25', 'PE': '26', 'AL': '27', 'SE': '28',
        'BA': '29', 'MG': '31', 'ES': '32', 'RJ': '33', 'SP': '35',
        'PR': '41', 'SC': '42', 'RS': '43', 'MS': '50', 'MT': '51',
        'GO': '52', 'DF': '53',
    }

    @staticmethod
    def _calcular_dv(chave_sem_dv):
        multiplicadores = [2, 3, 4, 5, 6, 7, 8, 9]
        soma = 0
        for i, char in enumerate(reversed(chave_sem_dv)):
            digito = int(char)
            mult = multiplicadores[i % len(multiplicadores)]
            soma += digito * mult
        resto = soma % 11
        if resto == 0 or resto == 1:
            return 0
        return 11 - resto

    @classmethod
    def gerar_chave_acesso(cls, empresa_cnpj, uf, data_emissao, modelo, serie, numero, cnf, tipo_emissao, cnpj_cpf_destinatario=''):
        cnpj_limpo = ''.join(c for c in empresa_cnpj if c.isdigit()).zfill(14)
        uf_str = str(uf).upper().strip()
        uf_cod = cls.UF_PARA_CODIGO.get(uf_str, uf_str).zfill(2)
        data = data_emissao
        if hasattr(data, 'strftime'):
            data_emissao_str = data.strftime('%y%m')
        else:
            data_emissao_str = data
        if len(data_emissao_str) != 4:
            data_emissao_str = datetime.now().strftime('%y%m')
        modelo_str = str(modelo).zfill(2)
        serie_str = str(serie).zfill(3)
        numero_str = str(numero).zfill(9)
        tp_emis = str(tipo_emissao).zfill(1)
        cnf_str = str(cnf).zfill(8)
        chave_sem_dv = f'{uf_cod}{data_emissao_str}{cnpj_limpo}{modelo_str}{serie_str}{numero_str}{tp_emis}{cnf_str}'
        dv = cls._calcular_dv(chave_sem_dv)
        return f'{chave_sem_dv}{dv}'

    @classmethod
    def gerar_xml_nfce(cls, venda, emitente, nfce_obj):
        cliente = venda.cliente
        if cliente and cliente.cpf_cnpj:
            cpf_cnpj_dest = ''.join(c for c in cliente.cpf_cnpj if c.isdigit())
            nome_dest = cliente.nome
            end_dest = f'{cliente.endereco}, {cliente.bairro}'
        else:
            cpf_cnpj_dest = ''
            nome_dest = 'CONSUMIDOR NAO IDENTIFICADO'
            end_dest = ''

        cnpj_emit = ''.join(c for c in emitente.cnpj if c.isdigit())
        ie_emit = emitente.ie or ''

        items_xml = ''
        n_item = 1
        total_produtos = Decimal('0.00')
        for item in venda.itens.all():
            v_prod = Decimal(str(item.subtotal))
            total_produtos += v_prod
            ncm = item.produto.ncm or '00000000'
            items_xml += f'''<det nItem="{n_item}">
                <prod>
                    <cProd>{item.produto.pk}</cProd>
                    <xProd>{item.produto.nome}</xProd>
                    <NCM>{ncm}</NCM>
                    <CFOP>5102</CFOP>
                    <uCom>{item.produto.unidade or 'UN'}</uCom>
                    <qCom>{item.quantidade}</qCom>
                    <vUnCom>{item.preco_unitario}</vUnCom>
                    <vProd>{v_prod}</vProd>
                    <cEANTrib>SEM GTIN</cEANTrib>
                </prod>
                <imposto>
                    <ICMS><ICMS00><orig>0</orig><CST>00</CST><modBC>3</modBC><vBC>0</vBC><pICMS>0</pICMS><vICMS>0</vICMS></ICMS00></ICMS>
                    <PIS><PISOutr><CST>99</CST><vBC>0</vBC><pPIS>0</pPIS><vPIS>0</vPIS></PISOutr></PIS>
                    <COFINS><COFINSOutr><CST>99</CST><vBC>0</vBC><pCOFINS>0</pCOFINS><vCOFINS>0</vCOFINS></COFINSOutr></COFINS>
                </imposto>
            </det>'''
            n_item += 1

        pagamento = venda.forma_pagamento
        tpag_map = {
            'dinheiro': '01', 'credito': '03', 'debito': '04',
            'pix': '17', 'convenio': '03', 'credito_pbm': '03',
            'debito_pbm': '04', 'vale': '13', 'multi': '99',
        }
        tpag = tpag_map.get(pagamento, '99')

        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<NFCe xmlns="http://www.portalfiscal.inf.br/nfe">
    <infNFe Id="NFe{nfce_obj.chave_acesso}" versao="4.00">
        <ide>
            <cUF>{cls.UF_PARA_CODIGO.get(emitente.uf.upper(), emitente.uf)}</cUF>
            <cNF>{nfce_obj.chave_acesso[35:43]}</cNF>
            <natOp>VENDA</natOp>
            <mod>65</mod>
            <serie>{nfce_obj.serie}</serie>
            <nNF>{nfce_obj.numero}</nNF>
            <dhEmi>{nfce_obj.data_emissao.strftime("%Y-%m-%dT%H:%M:%S-03:00")}</dhEmi>
            <tpNF>1</tpNF>
            <idDest>1</idDest>
            <tpEmis>{nfce_obj.tipo_emissao}</tpEmis>
            <cDV>{nfce_obj.chave_acesso[43]}</cDV>
            <tpAmb>1</tpAmb>
            <finNFe>1</finNFe>
            <indFinal>1</indFinal>
            <indPres>1</indPres>
            <procEmi>0</procEmi>
            <verProc>pharmaMS 1.0</verProc>
        </ide>
        <emit>
            <CNPJ>{cnpj_emit}</CNPJ>
            <xNome>{emitente.nome}</xNome>
            <xFant>{emitente.nome}</xFant>
            <enderEmit>
                <xLgr>{emitente.endereco}</xLgr>
                <xBairro>{emitente.bairro}</xBairro>
                <xCpl></xCpl>
                <cMun>3550308</cMun>
                <xMun>{emitente.cidade}</xMun>
                <UF>{emitente.uf}</UF>
                <CEP>{''.join(c for c in emitente.cep if c.isdigit()) if emitente.cep else ''}</CEP>
            </enderEmit>
            <IE>{ie_emit}</IE>
            <CRT>1</CRT>
        </emit>
        <dest>
            <CNPJ_CPF>{cpf_cnpj_dest or '00000000000000'}</CNPJ_CPF>
            <xNome>{nome_dest}</xNome>
            <enderDest>
                <xLgr>{end_dest}</xLgr>
            </enderDest>
            <indIEDest>9</indIEDest>
        </dest>
        {items_xml}
        <total>
            <ICMSTot>
                <vBC>0.00</vBC>
                <vICMS>0.00</vICMS>
                <vICMSDeson>0.00</vICMSDeson>
                <vFCP>0.00</vFCP>
                <vBCST>0.00</vBCST>
                <vST>0.00</vST>
                <vFCPST>0.00</vFCPST>
                <vFCPSTRet>0.00</vFCPSTRet>
                <vProd>{total_produtos}</vProd>
                <vFrete>0.00</vFrete>
                <vSeg>0.00</vSeg>
                <vDesc>{venda.desconto}</vDesc>
                <vII>0.00</vII>
                <vIPI>0.00</vIPI>
                <vIPIDev>0.00</vIPIDev>
                <vPIS>0.00</vPIS>
                <vCOFINS>0.00</vCOFINS>
                <vOutro>0.00</vOutro>
                <vNF>{venda.total}</vNF>
            </ICMSTot>
        </total>
        <pag>
            <detPag>
                <indPag>0</indPag>
                <tPag>{tpag}</tPag>
                <vPag>{venda.total}</vPag>
            </detPag>
        </pag>
    </infNFe>
</NFCe>'''

        nfce_obj.xml_enviado = xml
        nfce_obj.save(update_fields=['xml_enviado'])
        return xml

    @classmethod
    @transaction.atomic
    def emitir_nfce(cls, venda, emitente, tipo_emissao='1', justificativa=''):
        config = ConfiguracaoFiscal.objects.filter(empresa=venda.empresa).first()
        if not config:
            from django.core.exceptions import ValidationError
            raise ValidationError('Configure o fiscal antes de emitir NFC-e.')

        numero = str(config.proximo_numero_nfce)
        config.proximo_numero_nfce += 1
        config.save()

        cnf = str(numero).zfill(8)[:8]
        chave = cls.gerar_chave_acesso(
            empresa_cnpj=emitente.cnpj,
            uf=emitente.uf,
            data_emissao=datetime.now(),
            modelo='65',
            serie=config.serie_nfce,
            numero=numero,
            cnf=cnf,
            tipo_emissao=tipo_emissao,
        )

        nfce = NFCe.objects.create(
            empresa=venda.empresa,
            venda=venda,
            numero=numero,
            serie=config.serie_nfce,
            chave_acesso=chave,
            tipo_emissao=tipo_emissao,
            justificativa_contingencia=justificativa,
        )

        cls.gerar_xml_nfce(venda, emitente, nfce)

        if tipo_emissao == '1':
            nfce.status_autorizacao = 'autorizada'
            nfce.protocolo = 'SIMULADO'
            from django.utils import timezone
            nfce.data_autorizacao = timezone.now()
            nfce.save(update_fields=['status_autorizacao', 'protocolo', 'data_autorizacao'])
        else:
            nfce.status_autorizacao = 'pendente'
            nfce.save(update_fields=['status_autorizacao'])

        venda.nfce_emitida = True
        venda.save(update_fields=['nfce_emitida'])

        return nfce

    @classmethod
    def reemitir_pendentes(cls, empresa):
        pendentes = NFCe.objects.filter(empresa=empresa, status_autorizacao='pendente')
        reemitidas = []
        for nfce in pendentes:
            from django.utils import timezone
            nfce.status_autorizacao = 'autorizada'
            nfce.protocolo = 'SIMULADO'
            nfce.data_autorizacao = timezone.now()
            nfce.save(update_fields=['status_autorizacao', 'protocolo', 'data_autorizacao'])
            reemitidas.append(nfce)
        return reemitidas

    @staticmethod
    def imprimir_danfe_nfce(nfce_obj):
        venda = nfce_obj.venda
        if venda.cliente:
            cliente_nome = venda.cliente.nome
            cliente_cpf = venda.cliente.cpf_cnpj or ''
        else:
            cliente_nome = 'CONSUMIDOR NAO IDENTIFICADO'
            cliente_cpf = ''

        items = []
        for item in venda.itens.all():
            items.append({
                'codigo': item.produto.pk,
                'nome': item.produto.nome,
                'qtd': item.quantidade,
                'un': item.produto.unidade or 'UN',
                'vl_unit': float(item.preco_unitario),
                'vl_total': float(item.subtotal),
            })

        return {
            'nfce': nfce_obj,
            'venda': venda,
            'emitente': nfce_obj.empresa,
            'cliente_nome': cliente_nome,
            'cliente_cpf': cliente_cpf,
            'items': items,
        }


class NFeService:

    @classmethod
    def gerar_xml_nfe(cls, venda, emitente, nfe_obj):
        cliente = venda.cliente
        if cliente and cliente.cpf_cnpj:
            cpf_cnpj_dest = ''.join(c for c in cliente.cpf_cnpj if c.isdigit())
            nome_dest = cliente.nome
            end_dest = f'{cliente.endereco}, {cliente.bairro}'
        else:
            cpf_cnpj_dest = ''
            nome_dest = 'CONSUMIDOR NAO IDENTIFICADO'
            end_dest = ''

        cnpj_emit = ''.join(c for c in emitente.cnpj if c.isdigit())
        ie_emit = emitente.ie or ''

        mod = nfe_obj.modelo  # '55' ou '65'

        items_xml = ''
        n_item = 1
        total_produtos = Decimal('0.00')
        for item in venda.itens.all():
            v_prod = Decimal(str(item.subtotal))
            total_produtos += v_prod
            ncm = item.produto.ncm or '00000000'
            cfop = '5102'
            cest = item.produto.cest or ''
            items_xml += f'''\t\t\t<det nItem="{n_item}">
\t\t\t\t<prod>
\t\t\t\t\t<cProd>{item.produto.pk}</cProd>
\t\t\t\t\t<xProd>{item.produto.nome}</xProd>
\t\t\t\t\t<NCM>{ncm}</NCM>
\t\t\t\t\t<CFOP>{cfop}</CFOP>
\t\t\t\t\t<uCom>{item.produto.unidade or 'UN'}</uCom>
\t\t\t\t\t<qCom>{item.quantidade}</qCom>
\t\t\t\t\t<vUnCom>{item.preco_unitario}</vUnCom>
\t\t\t\t\t<vProd>{v_prod}</vProd>
\t\t\t\t\t<cEANTrib>SEM GTIN</cEANTrib>
\t\t\t\t</prod>
\t\t\t\t<imposto>
\t\t\t\t\t<ICMS><ICMS00><orig>0</orig><CST>00</CST><modBC>3</modBC><vBC>0</vBC><pICMS>0</pICMS><vICMS>0</vICMS></ICMS00></ICMS>
\t\t\t\t\t<PIS><PISOutr><CST>99</CST><vBC>0</vBC><pPIS>0</pPIS><vPIS>0</vPIS></PISOutr></PIS>
\t\t\t\t\t<COFINS><COFINSOutr><CST>99</CST><vBC>0</vBC><pCOFINS>0</pCOFINS><vCOFINS>0</vCOFINS></COFINSOutr></COFINS>
\t\t\t\t</imposto>
\t\t\t</det>'''
            n_item += 1

        pagamento = venda.forma_pagamento
        tpag_map = {
            'dinheiro': '01', 'credito': '03', 'debito': '04',
            'pix': '17', 'convenio': '03', 'credito_pbm': '03',
            'debito_pbm': '04', 'vale': '13', 'multi': '99',
        }
        tpag = tpag_map.get(pagamento, '99')

        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<NFe xmlns="http://www.portalfiscal.inf.br/nfe">
\t<infNFe Id="NFe{nfe_obj.chave_acesso}" versao="4.00">
\t\t<ide>
\t\t\t<cUF>{NFCeService.UF_PARA_CODIGO.get(emitente.uf.upper(), emitente.uf)}</cUF>
\t\t\t<cNF>{nfe_obj.chave_acesso[35:43]}</cNF>
\t\t\t<natOp>VENDA</natOp>
\t\t\t<mod>{mod}</mod>
\t\t\t<serie>{nfe_obj.serie}</serie>
\t\t\t<nNF>{nfe_obj.numero}</nNF>
\t\t\t<dhEmi>{nfe_obj.data_emissao.strftime("%Y-%m-%dT%H:%M:%S-03:00")}</dhEmi>
\t\t\t<tpNF>1</tpNF>
\t\t\t<idDest>1</idDest>
\t\t\t<tpEmis>1</tpEmis>
\t\t\t<cDV>{nfe_obj.chave_acesso[43]}</cDV>
\t\t\t<tpAmb>2</tpAmb>
\t\t\t<finNFe>1</finNFe>
\t\t\t<indFinal>1</indFinal>
\t\t\t<indPres>1</indPres>
\t\t\t<procEmi>0</procEmi>
\t\t\t<verProc>pharmaMS 1.0</verProc>
\t\t</ide>
\t\t<emit>
\t\t\t<CNPJ>{cnpj_emit}</CNPJ>
\t\t\t<xNome>{emitente.nome}</xNome>
\t\t\t<xFant>{emitente.nome}</xFant>
\t\t\t<enderEmit>
\t\t\t\t<xLgr>{emitente.endereco}</xLgr>
\t\t\t\t<xBairro>{emitente.bairro}</xBairro>
\t\t\t\t<cMun>3550308</cMun>
\t\t\t\t<xMun>{emitente.cidade}</xMun>
\t\t\t\t<UF>{emitente.uf}</UF>
\t\t\t\t<CEP>{''.join(c for c in emitente.cep if c.isdigit()) if emitente.cep else ''}</CEP>
\t\t\t</enderEmit>
\t\t\t<IE>{ie_emit}</IE>
\t\t\t<CRT>1</CRT>
\t\t</emit>
\t\t<dest>
\t\t\t<CNPJ_CPF>{cpf_cnpj_dest or '00000000000000'}</CNPJ_CPF>
\t\t\t<xNome>{nome_dest}</xNome>
\t\t\t<enderDest>
\t\t\t\t<xLgr>{end_dest}</xLgr>
\t\t\t</enderDest>
\t\t\t<indIEDest>9</indIEDest>
\t\t</dest>
		{items_xml}
		<total>
\t\t\t<ICMSTot>
\t\t\t\t<vBC>0.00</vBC>
\t\t\t\t<vICMS>0.00</vICMS>
\t\t\t\t<vICMSDeson>0.00</vICMSDeson>
\t\t\t\t<vFCP>0.00</vFCP>
\t\t\t\t<vBCST>0.00</vBCST>
\t\t\t\t<vST>0.00</vST>
\t\t\t\t<vFCPST>0.00</vFCPST>
\t\t\t\t<vFCPSTRet>0.00</vFCPSTRet>
\t\t\t\t<vProd>{total_produtos}</vProd>
\t\t\t\t<vFrete>0.00</vFrete>
\t\t\t\t<vSeg>0.00</vSeg>
\t\t\t\t<vDesc>{venda.desconto}</vDesc>
\t\t\t\t<vII>0.00</vII>
\t\t\t\t<vIPI>0.00</vIPI>
\t\t\t\t<vIPIDev>0.00</vIPIDev>
\t\t\t\t<vPIS>0.00</vPIS>
\t\t\t\t<vCOFINS>0.00</vCOFINS>
\t\t\t\t<vOutro>0.00</vOutro>
\t\t\t\t<vNF>{venda.total}</vNF>
\t\t\t</ICMSTot>
\t\t</total>
\t\t<pag>
\t\t\t<detPag>
\t\t\t\t<indPag>0</indPag>
\t\t\t\t<tPag>{tpag}</tPag>
\t\t\t\t<vPag>{venda.total}</vPag>
\t\t\t</detPag>
\t\t</pag>
\t</infNFe>
</NFe>'''

        nfe_obj.xml_enviado = xml
        nfe_obj.save(update_fields=['xml_enviado', 'chave_acesso'])
        return xml

    @classmethod
    @transaction.atomic
    def emitir_nfe(cls, venda, emitente, modelo='55'):
        config = ConfiguracaoFiscal.objects.filter(empresa=venda.empresa).first()
        if not config:
            from django.core.exceptions import ValidationError
            raise ValidationError('Configure o fiscal antes de emitir NF-e.')

        if modelo == '65':
            numero = str(config.proximo_numero_nfce)
            config.proximo_numero_nfce += 1
            serie = config.serie_nfce
        else:
            numero = str(config.proximo_numero_nfe)
            config.proximo_numero_nfe += 1
            serie = config.serie_nfe
        config.save()

        cnf = str(numero).zfill(8)[:8]
        chave = NFCeService.gerar_chave_acesso(
            empresa_cnpj=emitente.cnpj,
            uf=emitente.uf,
            data_emissao=datetime.now(),
            modelo=modelo,
            serie=serie,
            numero=numero,
            cnf=cnf,
            tipo_emissao='1',
        )

        nfe = NFe.objects.create(
            empresa=venda.empresa,
            modelo=modelo,
            serie=serie,
            numero=numero,
            chave_acesso=chave,
            cliente=venda.cliente,
            venda=venda,
            valor_total=venda.total,
            status='pendente',
        )

        cls.gerar_xml_nfe(venda, emitente, nfe)

        nfe.status = 'autorizada'
        nfe.protocolo = 'SIMULADO'
        from django.utils import timezone
        nfe.data_autorizacao = timezone.now()
        nfe.save(update_fields=['status', 'protocolo', 'data_autorizacao'])

        return nfe
