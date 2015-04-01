from p311.models import File, Result
from os.path import join
from xml.etree.ElementTree import fromstring
from datetime import datetime

def handle_file(f):
    
    fname = f.name
    count = File.objects.filter(name__endswith=fname[3:]).count()
    if count:
        current_file=File.objects.get(name__endswith=fname[3:])

    if fname.upper()[:3] in ('SBC', 'SFC'):
        #if file already loaded then do nothing
        if not count:
            doc_date, orgname = get_doc_date_n_org_name(f)
            new_file = File(name=fname, orgname=orgname, doc_date=doc_date)
            new_file.save()
    elif count and fname.upper()[:3] in ('SBF', 'SBP', 'SBR', 'SFF', 'SFE', 'SBE'):
        doc_date, service, processed, description = get_FRP_process_status(f)
        r = Result(
            src_file=current_file,
            service=service,
            processed=processed,
            description=description,
            name=fname,
            doc_date=doc_date)
        r.save()
    elif fname.upper()[:3] in ('UVA', 'UVB'):
        process_UV_file(f)

def get_doc_date_n_org_name(f):
    root = fromstring(f.read())
    for doc in root.findall('Документ'):
        doc_date=doc.attrib['ДатаСооб']
        for svnp in doc.findall('СвНП'):
            if svnp.findall('НПРО'):
                for npro in svnp.findall('НПРО'):
                    return datetime.strptime(doc_date, "%d.%m.%Y"), '{0}'.format(npro.attrib['НаимОрг'])
            if svnp.findall('НПФЛ'):
                for npfl in svnp.findall('НПФЛ'):
                    for fio in npfl.findall('ФИОФЛ'):
                        return datetime.strptime(doc_date, "%d.%m.%Y"), '{0} {1} {2}'.format(
                            fio.attrib['Фамилия'], 
                            fio.attrib['Имя'], 
                            fio.attrib['Отчество'] if 'Отчество' in fio.attrib else ''
                            )
            if svnp.findall('НПИП'):
                for npfl in svnp.findall('НПИП'):
                    for fio in npfl.findall('ФИОИП'):
                        return datetime.strptime(doc_date, "%d.%m.%Y"), '{0} {1} {2}'.format(
                            fio.attrib['Фамилия'], 
                            fio.attrib['Имя'], 
                            fio.attrib['Отчество'] if 'Отчество' in fio.attrib else ''
                            )

def process_UV_file(f):
    fname=f.name
    service='cb'
    root = fromstring(f.read())
    description=root.find('REZ_ARH').text
    doc_date=datetime.strptime(root.find('DATE_UV').text, "%d/%m/%Y")
    processed=True if description=='принят' else False
                    
    for name in root.findall('NAME'):
        for name_rec in name.findall('NAME_REC'):
            for name_es in name_rec.findall('NAME_ES'):
                if File.objects.filter(name=name_es.text).count():
                    current_file=File.objects.get(name=name_es.text)
                    r = Result(
                        src_file=current_file,
                        service=service,
                        processed=processed,
                        description=description,
                        name=fname,
                        doc_date=doc_date)
                    r.save()

def get_FRP_process_status(f):
    #returns doc_date, service, processed, description
    frp={
        'F':{
            'service': 'nal',
            'success_text':['Сообщение принято']
            },
        'R':{
            'service': 'fss',
            'success_text':['Нет ошибок (электронное сообщение принято)']
            },
        'P':{
            'service': 'pfr',
            'success_text':['сообщение получено', 'Нет ошибок (электронное сообщение принято)']
            },
        }
    tp=frp[f.name[2]]
    processed=False
    description=''
    root = fromstring(f.read())
    for doc in root.findall('Документ'):
        doc_date=doc.attrib['ДатаСооб']
        if tp['service']=='nal':
            description=doc.attrib['РезОбр']
            if description in tp['success_text']:
                processed=True
        elif tp['service'] in ['fss', 'pfr']:
            for errs in doc.findall('Ошибки'):
                description=errs.attrib['НаимОшибки']
                if description in tp['success_text']:
                    processed=True
    return datetime.strptime(doc_date, "%d.%m.%Y"), tp['service'], processed, description