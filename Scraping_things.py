import time
from datetime import datetime
import Global_var
from Insert_On_Datbase import insert_in_Local
import sys , os
import string
import time
from datetime import datetime,timedelta
import html
import re
import wx
import dateparser
app = wx.App()


def remove_html_tag(string):
    cleanr = re.compile('<.*?>')
    main_string = re.sub(cleanr, '', string)
    return main_string

def scrap_data(get_htmlsource,Detail):

    Tender_detail_outerhtml = get_htmlsource.replace('-\t','').replace('-\n','').replace('\t','').replace('\n','').replace('\xa0','')
    Tender_detail_outerhtml = html.unescape(str(Tender_detail_outerhtml))
    Tender_detail_outerhtml = re.sub(' +', ' ', str(Tender_detail_outerhtml))

    SegField = []
    for data in range(42):
        SegField.append('')

    error = True
    while error == True:
        try:
            Email = Tender_detail_outerhtml.partition("E-mail:")[2].partition("</a>")[0].strip()
            Email = remove_html_tag(Email)
            SegField[1] = Email

            Address = Tender_detail_outerhtml.partition("Adresse</td>")[2].partition("</td>")[0].strip()
            Address = remove_html_tag(Address)
            if 'WWW' in Address:
                Address = Address.partition("WWW")[0].strip()

            Contact_person = Tender_detail_outerhtml.partition("Kontaktperson</td>")[2].partition("</td>")[0].strip()
            Contact_person = remove_html_tag(Contact_person)

            Tel = Tender_detail_outerhtml.partition("Telefon:")[2].partition("</td>")[0].strip()
            Tel = remove_html_tag(Tel)

            SegField[2] = f'{Address}<br>\nContact Person: {Contact_person}<br>\nEmail: {Email}<br>\nTel: {Tel}' 

            SegField[12] = Detail.partition("puchaser:")[2].partition(",Deadline:")[0].strip()

            Title = Detail.partition("Tender_title:")[2].partition(",puchaser:")[0].strip()
            Title = Title.lstrip('-')
            SegField[19] =  Title.strip()

            document_type = Tender_detail_outerhtml.partition("Dokumenttype</td>")[2].partition("</td>")[0].strip()
            document_type = remove_html_tag(document_type)

            Description_of_tasks = Tender_detail_outerhtml.partition("Opgavebeskrivelse</td>")[2].partition("</td>")[0].strip()
            Description_of_tasks = remove_html_tag(Description_of_tasks)

            Job_type = Tender_detail_outerhtml.partition("Opgavetype</td>")[2].partition("</td>")[0].strip()
            Job_type = remove_html_tag(Job_type)

            award_criteria = Tender_detail_outerhtml.partition("Tildelingskriterier</td>")[2].partition("</td>")[0].strip()
            award_criteria = remove_html_tag(award_criteria)

            announced = Tender_detail_outerhtml.partition("Annonceret</td>")[2].partition("</td>")[0].strip()
            announced = remove_html_tag(announced)

            Deadline = Detail.partition("Deadline:")[2].replace('\n',' ').strip()

            main_Deadline = Deadline[0:10]
            datetime_object = dateparser.parse(str(main_Deadline))
            if datetime_object != '':
                Deadline = datetime_object.strftime("%Y-%m-%d")
                SegField[24] = Deadline.strip()

            CPV_Code = Tender_detail_outerhtml.partition("CPV kode</td>")[2].partition("</td>")[0].replace('\n',' ').strip()
            CPV_Code = remove_html_tag(CPV_Code)

            SegField[18] = f'{SegField[19]}<br>\nOpgavebeskrivelse: {Description_of_tasks}<br>\nDokumenttype: {document_type}<br>\nOpgavetype: {Job_type}<br>\nTildelingskriterier: {award_criteria}<br>\nAnnonceret: {announced}<br>\nDeadline: {Deadline}<br>\nCPV Code: {CPV_Code}'

            SegField[31] = 'udbud.dk'
            SegField[27] = "0"
            SegField[22] = "0"
            SegField[26] = "0.0"
            SegField[7] = "DK"
            SegField[14] = '2'
            SegField[16] = '1'
            SegField[17] = '0'
            SegField[28] = Detail.partition("tender_link:")[2].partition(",Tender_title:")[0].strip()

            CPV_Code = re.sub(' +', ' ', str(CPV_Code))
            ReplyStrings = CPV_Code
            if ReplyStrings != "":
                copy_cpv = ""
                Cpv_status = True
                all_string = ""
                try:
                    while Cpv_status == True:
                        phoneNumRegex = re.compile(r'\d\d\d\d\d\d\d\d-')
                        CPv_main = phoneNumRegex.search(ReplyStrings)
                        mainNumber = CPv_main.groups()
                        if CPv_main:
                            copy_cpv = CPv_main.group(), ", "
                            ReplyStrings = ReplyStrings.replace(CPv_main.group(), "")
                        else:
                            Cpv_status = False
                        result = "".join(str(x) for x in copy_cpv)
                        result = result.replace("-", "").strip()
                        result2 = result.replace("\n", "")
                        # print(result2)
                        all_string += result2
                except:
                    pass
                print(all_string.strip(","))
                SegField[36] = all_string.rstrip(',')
            else:
                SegField[36] = ""

            for SegIndex in range(len(SegField)):
                print(SegIndex, end=' ')
                print(SegField[SegIndex])
                SegField[SegIndex] = html.unescape(str(SegField[SegIndex]))
                SegField[SegIndex] = str(SegField[SegIndex]).replace("'", "''")
            
            if len(SegField[19]) > 250:
                    SegField[19] = SegField[19][:247] + '...'

            if SegField[19] == '':
                wx.MessageBox(' Short Desc Blank ','udbud.dk', wx.OK | wx.ICON_INFORMATION)
            else:
                check_date(SegField,get_htmlsource)
            error = False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",
                  exc_tb.tb_lineno)
            error = True
            time.sleep(5)


def check_date(SagField,get_htmlsource):

    deadline = str(SagField[24])
    curdate = datetime.now()
    curdate_str = curdate.strftime("%Y-%m-%d")
    try:
        if deadline != '':
            datetime_object_deadline = datetime.strptime(deadline, '%Y-%m-%d')
            datetime_object_curdate = datetime.strptime(curdate_str, '%Y-%m-%d')
            timedelta_obj = datetime_object_deadline - datetime_object_curdate
            day = timedelta_obj.days
            if day > 0:
                insert_in_Local(get_htmlsource, SagField)
            else:
                print("Expired Tender")
                Global_var.expired += 1
        else:
            print("Deadline Not Given")
            Global_var.deadline_Not_given += 1
    except Exception as e:
        exc_type , exc_obj , exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Error ON : " , sys._getframe().f_code.co_name + "--> " + str(e) , "\n" , exc_type , "\n" , fname , "\n" ,exc_tb.tb_lineno)
    