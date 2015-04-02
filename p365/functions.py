from p365.models import File, Sent, Result
from os.path import join
from datetime import datetime
from re import search

def handle_file(f):
    fname = f.name
    orig_name = get_original_filename(fname).upper()
    text = f.read().decode('cp866')

    count = File.objects.filter(name=orig_name).count()
    if count:
        current_file=File.objects.get(name=orig_name)

    if fname.upper()[:3] in ('PNO', 'ROO', 'RPO', 'ZNO'):
        #if file already loaded then do nothing
        if not count:
            doc_date, orgname = get_doc_date_n_org_name(text)
            prefix = fname.upper()[:3]
            new_file = File(name=fname.upper(), orgname=orgname, doc_date=doc_date, prefix=prefix)
            new_file.save()
    
    elif count and fname.upper()[:2] in ('PB', 'BO', 'BV', 'BN'):
        #processing PB1, PB2, BOS, BNS, BV
        prefix = re_search(r'(?P<param>(PB[12]|BV|BOS|BNS))', fname)
        doc_date = get_sent_file_doc_date(text, prefix)
        sent_file=Sent(
            in_file = current_file,
            name = fname.upper(),
            doc_date = doc_date,
            prefix = prefix
            )
        sent_file.save()
    
    elif count and fname.upper()[:6] in ('KWTFCB'):
        prefix = 'KWTFCB'
        if current_file.sent_set.filter(name=fname.replace('KWTFCB_','')):
            sent_file = current_file.sent_set.get(name=fname.replace('KWTFCB_',''))
            doc_date, processed, description = get_kwt_file_doc_date(text)
            result_file=Result(
                out_file = sent_file,
                name = fname.upper(),
                doc_date = doc_date,
                prefix = prefix,
                processed = processed,
                description = description
                )
            result_file.save()

    elif fname.upper()[:6] in ('IZVTUB'):
        pass

def re_search(rexp, text):
    #uses param as named parameter
    re_find = search(rexp,text)
    return re_find.group('param') if re_find else ''

def get_original_filename(filename):
    #re_search=search(r'(?P<filename>(PNO|ROO|RPO|ZNO)\d{8}_\d{12}_\d{6}\.(TXT|txt))',filename)
    #return re_search.group('filename') if re_search else None
    return re_search(r'(?P<param>(PNO|ROO|RPO|ZNO)\d{8}_\d{12}_\d{6}\.(TXT|txt))', filename)

def get_doc_date_n_org_name(text):
    orgname = re_search(r'(НаимНП|ФИОИП|Плательщ):(?P<param>[^\r\n]+)\r\n', text).replace(',', ' ')
    doc_date = re_search(r'(ДатаРешОт|ДатаРешПр|ДатаЗапр|ДатаПоруч):(?P<param>\d{2}\.\d{2}\.\d{4})\r\n', text)
    return datetime.strptime(doc_date, "%d.%m.%Y"), orgname

def get_sent_file_doc_date(text, prefix):
    if prefix in ('PB1', 'PB2'):
        doc_date = datetime.strptime(re_search(r'\r\n(?P<param>\d{4}-\d{2}-\d{2})@@@\r\n', text), "%Y-%m-%d") #YYYY-MM-DD
    else:
        doc_date = datetime.strptime(re_search(r'ДатаСооб:(?P<param>\d{2}\.\d{2}\.\d{4})\r\n', text), "%d.%m.%Y") #DD.MM.YYYY
    return doc_date

def get_kwt_file_doc_date(text):
    #doc_date, processed, description
    doc_date = datetime.strptime(re_search(r'\r\n(?P<param>\d{4}-\d{2}-\d{2})@@@\r\n', text), "%Y-%m-%d")
    result_code = re_search(r'###\r\n(?P<param>[^@]+)@@@', text)
    if result_code == '20':
        return doc_date, True, '20 - Принят'
    else:
        return doc_date, False, result_code