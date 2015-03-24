TIMEZONE=3*60*60
from cl_lib.cl_db import db
from cl_lib.cl_email import e_mail

class p311:
    def __init__(self, set_path, browse_path):
        import os
        self.db=db(os.path.join(set_path,'311-p.db'),'files')
        self.db.check('id integer primary key autoincrement not null, filename text, date int, orgname text, format text')
        self.db.runSQL('create table if not exists results (id integer primary key autoincrement not null, file_id int, filename text, date int, type text, result text, result_descr text, modified int)')
        self.files_table='files'
        self.results_table='results'
        self.in_path=os.path.join(browse_path, 'IN')
        self.out_path=os.path.join(browse_path, 'OUT')
        self.in_processed=os.path.join(self.in_path, 'PROCESSED')
        self.in_error=os.path.join(self.in_path, 'ERROR')
        self.out_processed=os.path.join(self.out_path, 'PROCESSED')
        self.out_error=os.path.join(self.out_path, 'ERROR')
        self.cr_views()
        
        self.check()
        updates=self.have_updates()
        if updates:
            html=self.generate_html(updates)
            #print(html)
            self.eml=e_mail()
            self.eml.email_html(['i.kononenko@vlg.tnb.ru','i.yakhimovich@vlg.tnb.ru','m.kvasnikov@vlg.tnb.ru'], '311-П. Итоги дня', html)
            #self.eml.email_html(['m.kvasnikov@vlg.tnb.ru'], '311-П. Итоги дня', html)
        
    def cur_date(self):
        import time
        t=time.gmtime()
        return int(time.mktime((t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, t.tm_wday, t.tm_yday, t.tm_isdst)))+TIMEZONE

    def check(self):
        def check_new_files(self):
            def get_311_attrs(self, filename):
                import time
                import datetime

                fmt={'TXT':502, 'XML':510}
                versfmt=fmt[filename.upper()[-3:]]

                orgname=''
                mdate=''
                try:
                    if versfmt==502:
                        for l in open(os.path.join(self.out_path,filename), encoding='cp866'):
                            if 'НаимНП:' in l or 'ФИОИП:' in l:
                                orgname=l.replace('НаимНП:','').replace('ФИОИП:','').replace(',',' ').replace('\n','')
                            if 'ДатаСооб:' in l:
                                mdate=l.replace('ДатаСооб:','').replace('\n','')

                    if versfmt==510:
                        import xml.etree.ElementTree as ET
                        tree = ET.parse(os.path.join(self.out_path,filename))
                        root = tree.getroot()

                        for doc in root.findall('Документ'):
                            mdate=doc.attrib['ДатаСооб']
                            for svnp in doc.findall('СвНП'):
                                if svnp.findall('НПРО'):
                                    for npro in svnp.findall('НПРО'):
                                        orgname='{0}'.format(npro.attrib['НаимОрг'])
                                if svnp.findall('НПФЛ'):
                                    for npfl in svnp.findall('НПФЛ'):
                                        for fio in npfl.findall('ФИОФЛ'):
                                            orgname='{0} {1} {2}'.format(fio.attrib['Фамилия'], fio.attrib['Имя'], fio.attrib['Отчество'] if 'Отчество' in fio.attrib else '')
                                if svnp.findall('НПИП'):
                                    for npfl in svnp.findall('НПИП'):
                                        for fio in npfl.findall('ФИОИП'):
                                            orgname='{0} {1} {2}'.format(fio.attrib['Фамилия'], fio.attrib['Имя'], fio.attrib['Отчество'] if 'Отчество' in fio.attrib else '')
                        
                    mdate=int(time.mktime(datetime.datetime.strptime(mdate, "%d.%m.%Y").timetuple()))
                except Exception as err:
                    print('Error in processing {0}. {1}'.format(filename, err))
                return orgname, mdate, versfmt
            
            def add_new(self, new_file):
                orgname, mdate, versfmt = get_311_attrs(self,new_file)
                if orgname=='':
                    return False
                elif self.db.runSQL("insert into {0}(filename, date, orgname, format) VALUES('{1}',{2},'{3}','{4}')".format(self.files_table, new_file, mdate, orgname, versfmt)):
                    return True

            import os
            import shutil
            db_files = self.db.runSQL('select filename from {}'.format(self.files_table))
            db_files = [f[0] for f in db_files]
            new_files = [f for f in os.listdir(self.out_path) if (os.path.isfile(os.path.join(self.out_path,f)) and f.upper().startswith('S'))]

            for f in new_files:
                if f not in db_files and add_new(self,f):
                    print('File {0} processed'.format(f))
                    shutil.move(os.path.join(self.out_path,f),self.out_processed)
                else:
                    shutil.move(os.path.join(self.out_path,f),self.out_error)

        
        def check_result_cb(self):
            def get_file_id(self,filename):
                t=self.db.runSQL("select id from {0} where filename='{1}'".format(self.files_table, filename))
                if t:
                    return t[0][0]
                else:
                    return False
            
            def add_cb_confirm(self, f):
                if f.upper().startswith('2Z'):
                    cont_files, result, result_text, fdate = read2zfile(self,f)
                else:
                    cont_files, result, result_text, fdate = read_xml_confirm(self,f)
                if not cont_files:
                    return False
                s="insert into {0}(file_id, filename, date, type, result, result_descr, modified) values({1},'{2}',{3},'{4}','{5}','{6}',{7})"
                for cf in cont_files:
                    idf=get_file_id(self,cf)
                    if idf:
                        self.db.runSQL(s.format(self.results_table,idf, f, fdate,'cb', result, result_text, self.cur_date()))
                    else:
                        return False
                return True

            def read_xml_confirm(self,filename):
                import time
                import datetime
                
                files=set()
                result=False
                result_text=''
                fdate=0

                try:
                    import xml.etree.ElementTree as ET
                    tree = ET.parse(os.path.join(self.in_path,filename))
                    root = tree.getroot()

                    result_text=root.find('REZ_ARH').text
                    fdate=root.find('DATE_UV').text.replace('/','.')
                    result=True if result_text=='принят' else False
                    fdate=int(time.mktime(datetime.datetime.strptime(fdate, "%d.%m.%Y").timetuple()))
                    
                    for name in root.findall('NAME'):
                        for name_rec in name.findall('NAME_REC'):
                            for name_es in name_rec.findall('NAME_ES'):
                                files.add(name_es.text)
                except Exception as err:
                    print('Error in processing file {0}. {1}'.format(f,err))

                return files, result, result_text, fdate

            def read2zfile(self, f):
                import os
                import time
                import datetime
                files=set()
                result=False
                result_text=''
                fdate=0

                try:
                    files_section=False
                    for l in open(os.path.join(self.in_path,f)):
                        l=l.replace('\n','')
                        if l.upper().startswith('S') and (l.upper().endswith('.XML') or l.upper().endswith('.TXT')):
                            files.add(l)
                            files_section=True
                        if files_section and not l.upper().startswith('S'):
                            result_text=l
                            files_section=False
                        if l.upper().startswith('ДАТА НАПРАВЛЕНИЯ УВЕДОМЛЕНИЯ'):
                            fdate=l.upper().replace('ДАТА НАПРАВЛЕНИЯ УВЕДОМЛЕНИЯ ','').replace('\n','')
                            fdate=int(time.mktime(datetime.datetime.strptime(fdate, "%d.%m.%Y").timetuple()))
                        if result_text=='принят':
                            result=True
                except Exception as err:
                    print('Exception in processing {0}. {1}'.format(f, err))
                return files, result, result_text, fdate
                
            import os
            import shutil
            new_files = [f for f in os.listdir(self.in_path) if (os.path.isfile(os.path.join(self.in_path,f)) and f.upper().startswith('2Z') or (f.upper().startswith('UV') and f.upper().endswith('XML')) )]

            for f in new_files:
                if add_cb_confirm(self,f):
                    print('File {0} processed'.format(f))
                    shutil.move(os.path.join(self.in_path,f),self.in_processed)
                else:
                    shutil.move(os.path.join(self.in_path,f),self.in_error)
                
        def check_result_frp(self):
            def add_frp_confirm(self, filename, file_id, fdate, tp, result, result_text):
                s="insert into {0}(file_id, filename, date, type, result, result_descr, modified) values({1},'{2}',{3},'{4}','{5}','{6}',{7})"
                self.db.runSQL(s.format(self.results_table, file_id, filename, fdate, tp, result, result_text, self.cur_date()))
            
            def get_file_id(self,filename):
                res=self.db.runSQL("select id from {0} where filename like('%{1}')".format(self.files_table, filename[3:]))
                if res:
                    return res[0][0]
                else:
                    return None
            def read_status(self, filename, versfmt, tp):
                res=False
                res_descr=''
                mdate=0

                try:
                    if versfmt==502:
                        such_dict={
                            'nal':'НаимОшибки:Нет ошибок (электронное сообщение принято)',
                            'fss':'НаимОшибки:сообщение получено',
                            'pfr':'НаимОшибки:сообщение получено'
                            }
                        such=such_dict[tp]

                        for l in open(os.path.join(self.in_path,filename), encoding='cp866'):
                            if 'НаимОшибки:' in l:
                                if such in l:
                                    res=True
                                    res_descr=such.replace('НаимОшибки:','')
                                else:
                                    res_descr=l.replace('\n','')
                            if 'ДатаСооб:' in l:
                                mdate=l.replace('ДатаСооб:','').replace('\n','')
                    if versfmt==510:
                        import xml.etree.ElementTree as ET
                        tree = ET.parse(os.path.join(self.in_path,filename))
                        root = tree.getroot()

                        for doc in root.findall('Документ'):
                            mdate=doc.attrib['ДатаСооб']
                            if tp=='nal':
                                res_descr=doc.attrib['РезОбр']
                                if res_descr=='Сообщение принято':
                                    res=True
                            if tp=='fss':
                                for errs in doc.findall('Ошибки'):
                                    res_descr=errs.attrib['НаимОшибки']
                                    if res_descr=='Нет ошибок (электронное сообщение принято)':
                                        res=True
                            if tp=='pfr':
                                for errs in doc.findall('Ошибки'):
                                    res_descr=errs.attrib['НаимОшибки']
                                    if res_descr=='сообщение получено' or res_descr=='Нет ошибок (электронное сообщение принято)':
                                        res=True
                    import time
                    import datetime
                    mdate=int(time.mktime(datetime.datetime.strptime(mdate, "%d.%m.%Y").timetuple()))
                except Exception as err:
                    print('Exception in processing {0}. {1}'.format(filename, err))
                return res, res_descr, mdate
                                
            def read_frp_file(self,filename):

                fmt={'TXT':502, 'XML':510}
                versfmt=fmt[filename.upper()[-3:]]
                frp={'F': 'nal', 'R': 'fss', 'P': 'pfr'}
                tp=frp[filename[2]]

                file_id=get_file_id(self,filename)
                if file_id:
                    res, res_descr, mdate = read_status(self, filename, versfmt, tp)
                    if mdate!=0:
                        add_frp_confirm(self, filename, file_id, mdate, tp, res, res_descr)
                        return True
                    else:
                        return False
                else:
                    return False

            import os
            import shutil
            new_files = [f for f in os.listdir(self.in_path) if (os.path.isfile(os.path.join(self.in_path,f)) and f.upper().startswith('S'))]

            for f in new_files:
                if read_frp_file(self,f):
                    print('File {0} processed'.format(f))
                    shutil.move(os.path.join(self.in_path,f),self.in_processed)
                else:
                    shutil.move(os.path.join(self.in_path,f),self.in_error)
               
        check_new_files(self)
        check_result_cb(self)
        check_result_frp(self)

    def have_updates(self):
        return self.db.runSQL("select * from stat")

    def generate_html(self, updates):
        def ts2dt(ts):
            import time
            t=time.gmtime(ts+TIMEZONE)
            return '{0}{1}.{2}{3}.{4}'.format('0' if t.tm_mday<10 else '' , t.tm_mday, '0' if t.tm_mon<10 else '' , t.tm_mon, t.tm_year)

                
        r="""<html>
<head>
<style type='text/css'>
table, th, td
{
font-family: Verdana,Arial,sans-serif;
font-size: 12px;
border-style: solid;
border-color: black;
border-width: 1px;
border-collapse: collapse;
text-align: center;
padding:10px;
}

.green
{
background-color: green;
color: white;
}

.red
{
background-color: red;
color: white;
}

.yellow
{
background-color: yellow;
color: black;
}

.gray
{
background-color: gray;
color: white;
}
</style>
</head>
<body>"""
        r+="<table cols=5 class='gray'>\n<tr>\n<td>Файл</td>\n<td>ЦБ</td>\n<td>Налоговая</td>\n<td>ФСС</td>\n<td>ПФР</td>\n</tr>"
        empty="<td>&nbsp</td>\n"
        for u in updates:
            if (u[0].upper().startswith('SBC') and (u[4]!='True' or u[8]!='True' or u[12]!='True' or u[16]!='True')) or (u[1]=='510' and (u[4]!='True' or u[8]!='True')):
                r+="<tr class='yellow'>\n"
            else:
                r+="<tr class='green'>\n"
            r+='<td>{0}<br>{1}<br>{2}</td>\n'.format(u[0], u[2] ,ts2dt(u[3]))

            for n in (4,8,12,16):
                if u[n]=='True':
                    r+="<td class='green'>{0}<br>{1}</td>\n".format(u[n+1], ts2dt(u[n+2]))
                elif u[n]=='False':
                    r+="<td class='red'>{0}<br>{1}</td>\n".format(u[n+1], ts2dt(u[n+2]))
                else:
                    r+=empty
            r+='</tr>\n'
        r+='</table>\n</body>\n</html>'
        return r

    def cr_views(self):
        self.db.runSQL(
            """create view if not exists stat as
select f.filename, f.format, f.orgname, f.date as fdate, cb.cb_result, cb.cb_rd, cb.cb_date, cb.cb_mod, nal.nal_result, nal.nal_rd, nal.nal_date, nal.nal_mod, fss.fss_result, fss.fss_rd, fss.fss_date, fss.fss_mod,  pfr.pfr_result, pfr.pfr_rd, pfr.pfr_date, pfr.pfr_mod from
files f
left join (select file_id, result as cb_result, result_descr as cb_rd, [date] as cb_date, modified as cb_mod from results where type='cb') cb on f.id=cb.file_id
left join (select file_id, result as nal_result, result_descr as nal_rd, [date] as nal_date, modified as nal_mod from results where type='nal') nal on f.id=nal.file_id
left join (select file_id, result as fss_result, result_descr as fss_rd, [date] as fss_date, modified as fss_mod from results where type='fss') fss on f.id=fss.file_id
left join (select file_id, result as pfr_result, result_descr as pfr_rd, [date] as pfr_date, modified as pfr_mod from results where type='pfr') pfr on f.id=pfr.file_id
where max(coalesce(cb.cb_mod, 0), coalesce(nal.nal_mod, 0), coalesce(fss.fss_mod, 0), coalesce(pfr.pfr_mod, 0))=cast(strftime('%s',date('now')) as int)
or ((f.format=510) and (cb.cb_result is null or nal.nal_result is null))
or (f.filename like('SBC%.%') and (cb.cb_result is null or nal.nal_result is null or fss.fss_result isnull or pfr.pfr_result is null))
"""
                       )

#####################################################################################################################        
class p365:
    def __init__(self, set_path, browse_path):
        import os
        self.db=db(os.path.join(set_path,'365-p.db'),'files')
        self.db.check('id integer primary key autoincrement not null, filename text, date int, orgname text, type text,format text')
        self.db.runSQL('create table if not exists out (id integer primary key autoincrement not null, infile_id int, filename text, type text, modified int)')
        self.db.runSQL('create table if not exists results (id integer primary key autoincrement not null, outfile_id int, filename text, date int, type text, result text, result_descr text, modified int)')
        self.files_table='files'
        self.out_table='out'
        self.results_table='results'
        self.in_path=os.path.join(browse_path, 'IN')
        self.out_path=os.path.join(browse_path, 'OUT')
        self.in_processed=os.path.join(self.in_path, 'PROCESSED')
        self.in_error=os.path.join(self.in_path, 'ERROR')
        self.out_processed=os.path.join(self.out_path, 'PROCESSED')
        self.out_error=os.path.join(self.out_path, 'ERROR')

        self.temp=os.path.join(set_path,'temp')
        self.ptk_path='L:\\PTK PSD\\Post\\Store'
        self.arj='L:\\PTK PSD\\ARJ\\arj.exe'

        if not os.path.exists(self.temp):
            os.makedirs(self.temp)

        self.cr_views()
        
        self.check()
        updates=self.have_updates()
        if updates:
            html=self.generate_html(updates)
            #print(html)
            self.eml=e_mail()
            self.eml.email_html(['i.kononenko@vlg.tnb.ru','i.yakhimovich@vlg.tnb.ru','m.kvasnikov@vlg.tnb.ru'], '365-П. Итоги дня', html)
            #self.eml.email_html(['m.kvasnikov@vlg.tnb.ru'], '365-П. Итоги дня', html)

    def cur_date(self):
        import time
        t=time.gmtime()
        return int(time.mktime((t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, t.tm_wday, t.tm_yday, t.tm_isdst)))+TIMEZONE

    def get_out_file_id(self, src_filename):
        idf=self.db.runSQL("select id from {0} where filename='{1}'".format(self.out_table, src_filename))
        if idf:
            return idf[0][0]
        else:
            return False

    def update_out_status(self, filename, cb_filename, date, ftype, result, result_descr, modified):
        idf=self.get_out_file_id(filename)
        if idf:
            s="insert into {0} (outfile_id, filename, date, type, result, result_descr, modified) values({1},'{2}',{3},'{4}','{5}','{6}',{7})"
            return self.db.runSQL(s.format(self.results_table, idf, cb_filename, date, ftype, result, result_descr, modified))
        else:
            return False

    def check(self):
        def check_in():
            def not_exist(filename):
                db_files=self.db.runSQL("select filename from {0} where filename='{1}'".format(self.files_table, filename))
                if db_files:
                    return False
                else:
                    return True

            def read_attributes(filename):
                dates_str=['ДатаРешОт:','ДатаРешПр:','ДатаЗапр:','ДатаПоруч:']
                org_name_str=['НаимНП:','ФИОИП:', 'Плательщ:']

                orgname=''
                fdate=0
                mformat=''

                try:
                    for l in open(os.path.join(self.in_path,filename), encoding='cp866'):
                        for d in dates_str:
                            if d in l:
                                fdate=l.replace(d,'').replace('\n','')
                        for o in org_name_str:
                            if o in l:
                                orgname=l.replace(o,'').replace(',',' ').replace('\n','')
                        if 'ВерсФорм:' in l:
                            mformat=l.replace('ВерсФорм:','').replace('\n','')
                            
                    import time
                    import datetime
                    fdate=int(time.mktime(datetime.datetime.strptime(fdate, "%d.%m.%Y").timetuple()))
                except Exception as err:
                    print('Exception in processing {0}. {1}'.format(filename, err))

                return orgname, fdate, mformat
                
                
            def add_new(filename):
                orgname, fdate, mformat = read_attributes(filename)
                if orgname=='' or fdate==0:
                    return False
                else:
                    return self.db.runSQL("insert into {0}(filename, date, orgname, type, format) VALUES('{1}',{2},'{3}','{4}','{5}')".format(self.files_table, filename, fdate, orgname, filename[:3],mformat))

            import os
            import shutil
            files = [f for f in os.listdir(self.in_path) if (os.path.isfile(os.path.join(self.in_path,f))and not (f.upper().startswith('IZVTUB') or f.upper().startswith('KWTFCB')))]
            if files:
                print(files)
                for f in files:
                    if not_exist(f) and add_new(f):
                        shutil.move(os.path.join(self.in_path,f),self.in_processed)
                        print('File {0} has been processed'.format(f))
                    else:
                        shutil.move(os.path.join(self.in_path,f),self.in_error)

        def check_out():
            def get_source_fname(filename):
                return filename[filename.find('_')+1:]
                
            def get_type(filename):
                return filename[:filename.find('_')]

            def get_source_id(src_filename):
                idf=self.db.runSQL("select id from {0} where filename='{1}'".format(self.files_table, src_filename))
                if idf:
                    return idf[0][0]
                else:
                    return False

            def add_out_file(filename):
                file_id=get_source_id(get_source_fname(filename))                           
                if file_id:
                    s="insert into {0}(infile_id, filename, type, modified) values ({1}, '{2}', '{3}', {4})"
                    return self.db.runSQL(s.format(self.out_table, file_id, filename, get_type(filename), self.cur_date()))
                else:
                    print("Cannot find source file. File {0} hasn't been processed".format(filename))
                    return False

            import os
            import shutil
            files = [f for f in os.listdir(self.out_path) if (os.path.isfile(os.path.join(self.out_path,f)) and f.upper().endswith('TXT'))]
            if files:
                for f in files:
                    if add_out_file(f):
                        shutil.move(os.path.join(self.out_path,f),self.out_processed)
                        print('File {0} has been processed'.format(f))
                    else:
                        shutil.move(os.path.join(self.out_path,f),self.out_error)

        def check_results_cb():
            def get_content_files(arj_filename_wo_ext, date=''):
                import os
                import shutil
                import glob

                arj_filename=arj_filename_wo_ext+'.ARJ'
                if date=='':
                    yy=arj_filename[20:24]
                    mm=arj_filename[24:26]
                    dd=arj_filename[26:28]
                else:
                    yy, mm, dd = date.split('.')

                if not os.path.exists(os.path.join(self.temp, arj_filename)):
                    ptk_dir='{0}\\{1}\\{2}\\{3}\\'.format(self.ptk_path,yy, mm, dd)
                    mz=glob.glob(os.path.join(ptk_dir,'mz???714.018.??????'))
                    if mz:
                        #print('expand -r {0}mz???714.018.?????? {1}'.format(ptk_dir,self.temp))
                        os.system('expand -r "{0}mz???714.018.??????" "{1}"'.format(ptk_dir, self.temp))
                    if not os.path.exists(os.path.join(self.temp, arj_filename)):
                        print('File not found {0}'.format(arj_filename))
                        return False
                arj_unp_path=os.path.join(self.temp, arj_filename_wo_ext)
                if not os.path.exists(arj_unp_path):
                    os.makedirs(arj_unp_path)
                    os.system('""{0}" e "{1}" "{2}" -u -y"'.format(self.arj, os.path.join(self.temp, arj_filename), arj_unp_path))
                end_files=[f.replace('.vrb','.txt') for f in os.listdir(arj_unp_path) if (os.path.isfile(os.path.join(arj_unp_path,f)) and (f.upper().endswith('VRB') or f.upper().endswith('TXT')))]
                return end_files
            
            def process_cb_file(cb_filename):
                file_lines={}
                try:
                    for lino, l in enumerate(open(os.path.join(self.in_path, cb_filename), encoding='cp866')):
                        file_lines.update({lino:l.replace('\n','').replace('###','').replace('@@@','')})
                    transport_arj=file_lines[0]
                    if file_lines[1]=='01':
                        result=True
                        result_descr='01 - принят ЦБ'
                    else:
                        result=False
                        result_descr=file_lines[1]
                    fdate=file_lines[2].replace('-','.')
                    import time
                    import datetime
                    
                    content_files=get_content_files(transport_arj, fdate)
                    if not content_files:
                        content_files=get_content_files(transport_arj)
                    fdate=int(time.mktime(datetime.datetime.strptime(fdate, "%Y.%m.%d").timetuple()))
                    if content_files:
                        res=True
                        for f in content_files:
                            if not self.update_out_status(f, cb_filename, fdate, 'cb', result, result_descr,  self.cur_date()):
                                print(f)
                                res=False
                        return res                                 
                    else:
                        print('No files to update in {0}'.format(cb_filename))
                        return False
                    
                except Exception as err:
                    print('Exception in processing {0}. {1}'.format(cb_filename, err))
                    return False
                return True
            
            import os
            import shutil
            files = [f for f in os.listdir(self.in_path) if (os.path.isfile(os.path.join(self.in_path,f)) and f.upper().startswith('IZVTUB') and f.upper().endswith('TXT'))]
            if files:
                for f in files:
                    if process_cb_file(f):
                        shutil.move(os.path.join(self.in_path,f),self.in_processed)
                        print('File {0} has been processed'.format(f))
                    else:
                        shutil.move(os.path.join(self.in_path,f),self.in_error)

        def check_results_fns():
            def process_res_fns(fns_filename):
                import time
                import datetime

                file_lines={}
                try:
                    for lino, l in enumerate(open(os.path.join(self.in_path, fns_filename), encoding='cp866')):
                        file_lines.update({lino:l.replace('\n','').replace('###','').replace('@@@','')})
                    out_filename=file_lines[0]+'.txt'
                    if file_lines[1]=='20':
                        result=True
                        result_descr='20 - принят ФНС'
                        fdate=file_lines[2].replace('-','.')
                    else:
                        result=False
                        result_descr=file_lines[1]
                        fdate=file_lines[len(file_lines)-3].replace('-','.')
                        print(out_filename)
                        print(fns_filename)

                    fdate=int(time.mktime(datetime.datetime.strptime(fdate, "%Y.%m.%d").timetuple()))

                    if self.update_out_status(out_filename, fns_filename, fdate, 'nal', result, result_descr,  self.cur_date()):
                        return True
                    else:
                        print("====Error in processing {0}:".format(fns_filename))
                        print('Cannot find out file {0}'.format(out_filename))
                        return False
                except Exception as err:
                    print('Exception in processing {0}. {1}'.format(fns_filename, err))
                    return False
                return True

            
            import os
            import shutil
            files = [f for f in os.listdir(self.in_path) if (os.path.isfile(os.path.join(self.in_path,f)) and f.upper().startswith('KWTFCB') and f.upper().endswith('TXT'))]
            if files:
                for f in files:
                    if process_res_fns(f):
                        shutil.move(os.path.join(self.in_path,f),self.in_processed)
                        print('File {0} has been processed'.format(f))
                    else:
                        shutil.move(os.path.join(self.in_path,f),self.in_error)

        check_in()
        check_out()
        check_results_cb()
        check_results_fns()

    def have_updates(self):
        return self.db.runSQL("select * from stat")

    def generate_html(self, updates):
        def ts2dt(ts):
            import time
            t=time.gmtime(ts+TIMEZONE)
            return '{0}{1}.{2}{3}.{4}'.format('0' if t.tm_mday<10 else '' , t.tm_mday, '0' if t.tm_mon<10 else '' , t.tm_mon, t.tm_year)
        
        r="""<html>
<head>
<style type='text/css'>
table, th, td
{
font-family: Verdana,Arial,sans-serif;
font-size: 12px;
border-style: solid;
border-color: black;
border-width: 1px;
border-collapse: collapse;
text-align: center;
padding:10px;
}

.green
{
background-color: green;
color: white;
}

.yellow
{
background-color: yellow;
color: black;
}

.red
{
background-color: red;
color: white;
}

.blue
{
background-color: skyblue;
color: black;
}

.gray
{
background-color: gray;
color: white;
}

p
{
font-family: Verdana,Arial,sans-serif;
font-size: 11px;
color: gray;
}

</style>
</head>
<body>"""
        r+="<table cols=4 class='gray'>\n<tr>\n<td>Файл</td>\n<td>PB1</td>\n<td>Данные</td>\n<td>PB2</td>\n</tr>\n"
        empty="<td>&nbsp</td>\n"
        for u in updates:
            lcolor = 'blue' if ((u[11]=='True' and u[10]=='cb') and ( (u[20]=='True' and u[19]=='cb') or (u[29]=='True' and u[28]=='cb') ) ) or ((u[11]=='True' and u[10]=='cb') and (u[4] in ['PNO', 'ROO'])) else 'yellow'
            if lcolor!='blue':
                lcolor = 'green' if ((u[11]=='True' and u[10]=='nal') and ( (u[20]=='True' and u[19]=='nal') or (u[29]=='True' and u[28]=='nal') ) ) or ((u[11]=='True' and u[10]=='nal') and (u[4] in ['PNO', 'ROO'])) else 'yellow'
            
            fname='<td>{0}<br>{1}<br>{2}</td>'.format(u[1], u[3], ts2dt(u[2]))
            pb1="<td{0}>{1}<br>{2}</td>".format(" class='red'" if u[11]=='False' else '',u[12] if u[12] else '',ts2dt(u[9]) if u[12] else '')
            dat="<td{0}>{1}<br>{2}</td>".format(" class='red'" if u[20]=='False' else '',u[21] if u[21] else '',ts2dt(u[18]) if u[21] else '')
            pb2="<td{0}>{1}<br>{2}</td>".format(" class='red'" if u[29]=='False' else '',u[30] if u[30] else '',ts2dt(u[27]) if u[30] else '')
            
            r+="<tr class='{0}'>{1}{2}{3}{4}</tr>\n".format(lcolor, fname, pb1, dat, pb2)
            
        r+='</table>\n'
        #r+='<p>Отчет работает в тестовом режиме. Статус отправлен означает что файлы были по крайней мере зашифрованы. </p>\n'
        r+='</body>\n</html>'
        return r
    def cr_views(self):
        self.db.runSQL("""create view if not exists stat as
select f.id, f.filename, f.date, f.orgname, f.type, pb1.*, dat.*, pb2.*
from files f
left join 
(select out.infile_id as pb1_infile_id, out.filename as pb1_fname, out.modified as pb1_mod, results.filename as pb1_kwt_fname, results.date as pb1_kwt_date, results.type as pb1_kwt_type, results.result as pb1_kwt_res, results.result_descr as pb1_kwt_desc, results.modified as pb1_kwt_mod
from out left join results on results.outfile_id=out.id join (select outfile_id, max(id) as max_id from results group by outfile_id) res1 on results.id=res1.max_id
where out.type='PB1') pb1 on f.id=pb1.pb1_infile_id
left join 
(select out.infile_id as dat_infile_id, out.filename as dat_fname, out.modified as dat_mod, results.filename as dat_kwt_fname, results.date as dat_kwt_date, results.type as dat_kwt_type, results.result as dat_kwt_res, results.result_descr as dat_kwt_desc, results.modified as dat_kwt_mod
from out left join results on results.outfile_id=out.id join (select outfile_id, max(id) as max_id from results group by outfile_id) res1 on results.id=res1.max_id
where out.type<>'PB1' and out.type<>'PB2') dat on f.id=dat.dat_infile_id
left join 
(select out.infile_id as pb2_infile_id, out.filename as pb2_fname, out.modified as pb2_mod, results.filename as pb2_kwt_fname, results.date as pb2_kwt_date, results.type as pb2_kwt_type, results.result as pb2_kwt_res, results.result_descr as pb2_kwt_desc, results.modified as pb2_kwt_mod
from out left join results on results.outfile_id=out.id join (select outfile_id, max(id) as max_id from results group by outfile_id) res1 on results.id=res1.max_id
where out.type='PB2') pb2 on f.id=pb2.pb2_infile_id
where
max(coalesce(pb1.pb1_mod, 0), coalesce(pb1.pb1_kwt_mod, 0), coalesce(dat.dat_mod, 0), coalesce(dat.dat_kwt_mod, 0), coalesce(pb2.pb2_mod, 0), coalesce(pb2.pb2_kwt_mod, 0))=cast(strftime('%s',date('now')) as int)
or pb1.pb1_fname is null or pb1.pb1_kwt_fname is null or pb1.pb1_kwt_type<>'nal'
or ( f.type in ('RPO','ZNO') and (dat.dat_fname is null or dat.dat_kwt_fname is null or dat.dat_kwt_type<>'nal') and (pb2.pb2_fname is null or pb2.pb2_kwt_fname is null or pb2.pb2_kwt_type<>'nal') )
"""
                       )
def wd():
    import datetime
    if datetime.datetime.today().weekday()<5:
        return True
    else:
        return False

def init():
    import os
    import sys
    set_fldr=os.path.join(os.path.split(sys.argv[0])[0],os.path.splitext(os.path.split(sys.argv[0])[1])[0])
    if not os.path.exists(set_fldr):
        os.makedirs(set_fldr)
    return set_fldr

if wd():
    set_fldr=init()
    a=p311(set_fldr, 'S:\\CBP\\311P')
    b=p365(set_fldr, 'S:\\CBP\\365P')
