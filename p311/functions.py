from p311.models import File, Result
from os.path import join
from xml.etree.ElementTree import fromstring

def handle_file(f):
    def get_org_name(f):
        root = fromstring(f.read())

        for doc in root.findall('Документ'):
            mdate=doc.attrib['ДатаСооб']
            for svnp in doc.findall('СвНП'):
                if svnp.findall('НПРО'):
                    for npro in svnp.findall('НПРО'):
                        return '{0}'.format(npro.attrib['НаимОрг'])
                if svnp.findall('НПФЛ'):
                    for npfl in svnp.findall('НПФЛ'):
                        for fio in npfl.findall('ФИОФЛ'):
                            return '{0} {1} {2}'.format(
                            	fio.attrib['Фамилия'], 
                            	fio.attrib['Имя'], 
                            	fio.attrib['Отчество'] if 'Отчество' in fio.attrib else ''
                            	)
                if svnp.findall('НПИП'):
                    for npfl in svnp.findall('НПИП'):
                        for fio in npfl.findall('ФИОИП'):
                            return '{0} {1} {2}'.format(
                            	fio.attrib['Фамилия'], 
                            	fio.attrib['Имя'], 
                            	fio.attrib['Отчество'] if 'Отчество' in fio.attrib else ''
                            	)

    fname = f.name 
    if fname.upper()[:3] in ('SBC', 'SFC'):
        f=File(name=fname, orgname=get_org_name(f))
        f.save()