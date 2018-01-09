from urllib import request
from os.path import isfile, exists
from os import makedirs
import requests
from bs4 import BeautifulSoup
import time
import glob, os

search_url = "https://www.google.com/finance?q="
company_WSE = "WSE:"

historical_prices_url = "https://www.google.com/finance/historical?q="
start_date = "&startdate=Jul+2%2C+2012"
google_url = "https://www.google.com"

WIG20 = "http://www.bankier.pl/inwestowanie/profile/quote.html?symbol=WIG20"
all_companies = "http://www.bankier.pl/gielda/notowania/akcje"

def get_companies(url, companies):
    file = None
    if url == WIG20:
        if isfile("WIG20.csv"):
            file = open("WIG20.csv", "r")
            if not isfile("full_WIG20.csv"):
                file.close()
                file = None
    elif url == all_companies:
        if isfile("all_companies.csv"):
            file = open("all_companies.csv", "r")
            if not isfile("full_all_companies.csv"):
                file.close()
                file = None

    if file != None:
        csv_str = str(file.read())
        lines = csv_str.split("\n")

        for line in lines:
            companies.append(line)

        if companies[-1] is "":
            del companies[-1] # delete last enter

        file.close()
        return

    get_companies_from_web(url,companies) # file not found


def get_companies_from_web(url, companies):
    full_names = []
    downloaded = 0

    if url == WIG20:
        companies_size = 20
    else: companies_size = 476

    soup_main = BeautifulSoup(requests.get(url).text, "html.parser")
    for tr_main in soup_main.findAll('tr'):
        transactions = int(str(find_nth(tr_main, 'td', 5)).replace(' ' and chr(160), ''))
        transactions_money = int(str(find_nth(tr_main, 'td', 6)).replace(' ' and chr(160), ''))
        if int(transactions) > 20 and transactions_money > 10000:
            company_name = find_nth(tr_main, 'td', 1).replace('\n', '')
            full_names.append(company_name)
            url_company = "http://www.bankier.pl/inwestowanie/profile/quote.html?symbol=" + company_name
            soup = BeautifulSoup(requests.get(url_company).text, "html.parser")
            for link in soup.findAll('span', {'class': 'profilTicker'}):
                title = link.string
                companies.append(title[2:5])
                downloaded += 1
                print("DOWNLOADED NAMES: " + str(downloaded) + '\n')
                break

    #save all companies to file
    file = None
    if url == WIG20:
        file = open("WIG20.csv", "w")
    elif url == all_companies:
        file = open("all_companies.csv", "w")

    for company in companies:
        #dont write last enter
        if companies[-1] != company:
            file.write(company + '\n')
        else:
            file.write(company)

    save_full_names(url,full_names)
    file.close()

#n counts from 1
def find_nth(string, to_find, n):
    if string.find(to_find) == None:
        return -1

    lines = string.find_all(to_find)

    if len(lines) < n:
        return -1

    return str(lines[n - 1].text)



def number_of_transactions():
    x = 1


def save_full_names(url, full_names):
    file = None
    if url == WIG20:
        file = open("full_WIG20.csv", "w")
    elif url == all_companies:
        file = open("full_all_companies.csv", "w")

    if file is None:
        return

    for name in full_names:
        #dont write last enter
        if full_names[-1] != name:
            file.write(name + '\n')
        else:
            file.write(name)

    file.close()

def saved_history(url):
    if isfile("Historical prices/date.txt") is False:
        return False

    file = open("Historical prices/date.txt", 'r')
    lines = file.read().split("\n")

    for line in lines:
        if url == WIG20 and line.find("WIG20") != -1 and line.find(time.strftime("%d/%m/%Y")) != -1:
            file.close()
            return True
        elif url == all_companies and line.find("all_companies") != -1 and line.find(time.strftime("%d/%m/%Y")) != -1:
            file.close()
            return True

    file.close()
    return False


def download_all_histories(to_analysis, companies, full_names):
    get_companies(to_analysis, companies)
    get_full_names_companies(to_analysis, full_names)

    error = True
    while error:
        error = True
        if len(companies) != len(full_names):
            error = True
            files = glob.glob("*.csv")
            for f in files:
                os.remove(f)

            for it in range(len(companies)):
                del companies[0]

            for it in range(len(full_names)):
                del full_names[0]

            get_companies(to_analysis, companies)
            get_full_names_companies(to_analysis, full_names)
        else: error = False

    current_percent = -1
    downloaded = 0
    companies_size = len(companies)
    if saved_history(to_analysis) is False: #nothing to download
        for name in companies:
            download_history(name)
            downloaded += 1
            if int(downloaded / companies_size  * 100) != current_percent:
                current_percent = int(downloaded / companies_size  * 100)
                print(str(current_percent) + " % DOWNLOADING HISTORY\n")

        save_date_after_download(to_analysis)


def download_history(name):
    history_url = historical_prices_url + company_WSE + name + start_date
    soup = BeautifulSoup(requests.get(history_url).text, "html.parser")
    for link in soup.findAll('a', {'class': 'nowrap'}):
        csv_url = link.get("href")
        csv_response = request.urlopen(csv_url)

        if csv_response is None:
            return

        csv_str = str(csv_response.read())
        lines = csv_str.split("\\n")

        if isfile("Historical prices/" + name + '.csv'):
            f = open("Historical prices/" + name + '.csv', 'r')
            lines_file = f.read().split('\n')
            if len(lines_file) >= 2 and len(lines) >= 2 and lines[1] is lines_file[1]:
                return # no need to save it again

        file = open("Historical prices/" + name + '.csv', 'w')

        if len(lines[-1]) < 5:
            del lines[-1] # delete last enter

        for line in lines:
            #dont write last enter
            if lines[-1] != line:
                file.write(line + '\n')
            else:
                file.write(line)

        file.close()
        return

def save_date_after_download(url):
    if exists("/Historical prices/") is False:
        makedirs("/Historical prices/")

    file = open("Historical prices/date.txt", 'w+')
    lines = file.read().split("\n")

    found = False
    for i in range(len(lines)):
        if url == WIG20 and lines[i].find("WIG20") != -1:
            lines[i] = "WIG20 : " + time.strftime("%d/%m/%Y")
            found = True
        elif url == all_companies and lines[i].find("all_companies") != -1:
            lines[i] = "all_companies : " + time.strftime("%d/%m/%Y")
            found = True

    file.seek(0,0)

    if found is False:
        if url == WIG20:
            lines.append("WIG20 : " + time.strftime("%d/%m/%Y"))
        elif url == all_companies:
            lines.append("all_companies : " + time.strftime("%d/%m/%Y"))

    for line in lines:
        file.write(line + '\n')

    file.close()


def get_full_names_companies(url, full_names):
    file = None

    if url == WIG20:
        if not isfile("full_WIG20.csv"):
            return
        file = open("full_WIG20.csv", "r")
    elif url == all_companies:
        if not isfile("full_all_companies.csv"):
            return
        file = open("full_all_companies.csv", "r")

    lines = file.read().split("\n")
    file.close()

    for line in lines:
        full_names.append(line)