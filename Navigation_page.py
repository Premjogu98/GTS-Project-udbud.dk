from selenium import webdriver
import time
import html
import sys, os
from datetime import datetime,timedelta
import Global_var
import wx
import string
import html
import re
from Scraping_things import scrap_data


app = wx.App()

def ChromeDriver():
    browser = webdriver.Chrome(executable_path=str(f"C:\\chromedriver.exe"))
    browser.get("https://www.udbud.dk/Pages/Tenders/News")
    browser.maximize_window()
    time.sleep(5)
    tr_count = 1
    tender_link = []
    loop = True
    while loop == True:
        for tr in browser.find_elements_by_xpath('//*[@id="datagridtenders_1F8CBE3E"]/tbody/tr'):
            Contract_type = ''
            Title = ''
            title_href = ''
            Contracting_Authority = ''
            announced_date = ''
            Deadline = ''
            for Contract_type in browser.find_elements_by_xpath(f'//*[@id="datagridtenders_1F8CBE3E"]/tbody/tr[{str(tr_count)}]/td[1]'):
                Contract_type = Contract_type.get_attribute('innerText').strip()
                break
            for title_href in browser.find_elements_by_xpath(f'//*[@id="datagridtenders_1F8CBE3E"]/tbody/tr[{str(tr_count)}]/td[2]/a'):
                title_href = title_href.get_attribute('href').strip()
                break
            for Title in browser.find_elements_by_xpath(f'//*[@id="datagridtenders_1F8CBE3E"]/tbody/tr[{str(tr_count)}]/td[2]'):
                Title = Title.get_attribute('innerText').strip()
                break
            for Contracting_Authority in browser.find_elements_by_xpath(f'//*[@id="datagridtenders_1F8CBE3E"]/tbody/tr[{str(tr_count)}]/td[3]'):
                Contracting_Authority = Contracting_Authority.get_attribute('innerText').strip()
                break
            for announced_date in browser.find_elements_by_xpath(f'//*[@id="datagridtenders_1F8CBE3E"]/tbody/tr[{str(tr_count)}]/td[6]'):
                announced_date = announced_date.get_attribute('innerText').strip()
                break
            for Deadline in browser.find_elements_by_xpath(f'//*[@id="datagridtenders_1F8CBE3E"]/tbody/tr[{str(tr_count)}]/td[7]'):
                Deadline = Deadline.get_attribute('innerText').strip()
                break

            datetime_object = datetime.strptime(announced_date, '%d-%m-%Y')
            publish_date = datetime_object.strftime("%d-%m-%Y")

            datetime_object_pub = datetime.strptime(publish_date, '%d-%m-%Y')
            User_Selected_date = datetime.strptime(str(Global_var.From_Date), '%d-%m-%Y')
            timedelta_obj = datetime_object_pub - User_Selected_date
            day = timedelta_obj.days
            if day >= 0:
                if Contract_type != 'EU-udbud':
                    detail = f'tender_link:{title_href},Tender_title:{Title},puchaser:{Contracting_Authority},Deadline:{Deadline}'
                    tender_link.append(detail)
                    print('Publish Date Alive')
                    tr_count += 1
                else:
                    print('This Tender EU-udbud')
                    tr_count += 1
            else:
                print('Publish Date Dead')
                print(f'Total link Collected: {str(len(tender_link))}')
                nav_link(tender_link,browser)
        for Next_page in browser.find_elements_by_xpath('//*[@id="datagridtenders_1F8CBE3E_next"]'):
            Next_page.click()
            break
        tr_count = 1
        time.sleep(2)

def nav_link(tender_link,browser):
    for href in tender_link:
        error = False
        while error == False:
            try:
                tender_href = href.partition("tender_link:")[2].partition(",Tender_title:")[0].strip()
                browser.get(tender_href)
                time.sleep(2)
                get_htmlsource = ''
                for html_table in browser.find_elements_by_xpath('//*[@class="details-table"]'):
                    html_table = html_table.get_attribute('outerHTML').strip()
                    html_table = html_table.replace('href="/','https://www.udbud.dk/')
                    get_htmlsource += html_table
                    break
                if get_htmlsource == '':
                    for html_table in browser.find_elements_by_xpath('//*[@class="details-table details-table-big"]'):
                        html_table = html_table.get_attribute('outerHTML').strip()
                        html_table = html_table.replace('href="/','https://www.udbud.dk/')
                        get_htmlsource += html_table
                        break
                    if get_htmlsource == '':
                        wx.MessageBox(' get_htmlsource Blank ','udbud.dk', wx.OK | wx.ICON_ERROR)
                if get_htmlsource != '':
                    scrap_data(get_htmlsource,href)
                    print(f'Total: {str(len(tender_link))} Deadline Not given: {Global_var.deadline_Not_given} duplicate: {Global_var.duplicate} inserted: {Global_var.inserted} expired: {Global_var.expired} QC Tenders: {Global_var.QC_Tenders}')
                error = True
            except Exception as e:
                exc_type , exc_obj , exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("Error ON : " , sys._getframe().f_code.co_name + "--> " + str(e) , "\n" , exc_type , "\n" , fname , "\n" ,exc_tb.tb_lineno)
                error = False
    wx.MessageBox(f'Total: {str(len(tender_link))}\nDeadline Not given: {Global_var.deadline_Not_given}\nduplicate: {Global_var.duplicate}\ninserted: {Global_var.inserted}\nexpired: {Global_var.expired}\nQC Tenders: {Global_var.QC_Tenders}','udbud.dk', wx.OK | wx.ICON_INFORMATION)
    browser.close()
    sys.exit()

ChromeDriver()