import download_history as g_t
import requests
from bs4 import BeautifulSoup
import math

full_names = []
companies = []

def run():
    url = g_t.all_companies

    g_t.download_all_histories(url, companies, full_names)
#    g_t.get_full_names_companies(url, full_names)
    good_companies = []

    analyzed = 0
    companies_size = len(companies)
    current_percent = -1
    for company in companies:
        history_prices = []
        get_history(company, history_prices)
        min_price = min(history_prices)

        analyzed += 1
        if int(analyzed / companies_size * 100) != current_percent:
            current_percent = int(analyzed / companies_size * 100)
            print(str(current_percent) + " % ANALYZING\n")
        if len(history_prices) > 5:
            for i in range(5):
                if history_prices[i] < min_price*1.15 and history_prices[i] > min_price*0.85:
                    if profit(companies.index(company)):
                        print("Znaleziono w: " + company + "\n")
                        good_companies.append(company)
                        break
    show_result(good_companies)


def get_history(name, history_prices):
    if g_t.isfile("Historical prices/" + name + '.csv') == False:
        return # file not exist

    file = open("Historical prices/" + name + '.csv', 'r')

    lines = file.read().split("\n")
    del lines[0] # delete info line

    for line in lines:
        values = line.split(",")
        history_prices.append(float(values[4]))

    file.close()


def profit(index):
    full_name = full_names[index]
    url = "http://www.bankier.pl/gielda/notowania/akcje/" + full_name + "/wyniki-finansowe"

    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    counter = 0
    for link in soup.findAll('tr'):
        if counter is 4: # 4th line
            text = link.text.replace(' ' and chr(160), '').split('\n')
            a = link.text.replace(chr(160), '')
            if text[-1] is '': # last word is empty
                del text[-1]
            del text[:-4] # delete everything beside last 4 numbers

            if len(text) != 4:
                return False

#            if int(text[-1]) > int(text[-2]):
#                return True
            if int(text[-1]) > 0: # profit
                return True
            else:
                return False
        elif counter > 4:
            return False

        counter += 1

    return False


def get_last_stock_date():
    if not g_t.isfile("Historical prices/TPE.csv"):
        return

    file = open("Historical prices/TPE.csv", 'r')
    lines = file.read().split('\n')
    file.close()

    if len(lines) < 2:
        return

    line = lines[1].split(',')
    return line[0]


def show_result(companies):
    current_date = get_last_stock_date()
    compare = False
    to_compare = []

    if g_t.isfile("past_good_companies.csv"):
        file = open("past_good_companies.csv", 'r')
        lines = file.read().split('\n')
        file.close()

        if len(lines[-1]) < 3:
            del lines[-1]


        if len(lines) >= 2:
            line = lines[2].split(',')
            if line[0] is not current_date:
                compare = True

        for i in range(1, len(lines)):
            to_compare.append(lines[i])

    file = open("past_good_companies.csv", 'w')
    file.write(str(current_date) + '\n')

    print("Znaleziono: " + str(len(companies)) + " firm:\n")
    i = 1
    for company in companies:
        print('[' + str(i) + ']   ' + company + '\n')
        file.write(str(company) + '\n')
        i += 1

    if compare:
        compare_results(to_compare, companies)


def compare_results(first_list, main_list):
    added_elements = []

    # copy list
    for element in main_list:
        added_elements.append(element)

    for element_first_list in first_list:
        if find_in_list(added_elements, element_first_list):
            added_elements.remove(element_first_list)

    print('\nIlosc firm, które dopiero zaczely byc dobre: ' + str(len(added_elements)) + '\n')

    for i in range(len(added_elements)):
        print('[' + str(i) + ']   ' + str(added_elements[i]) + '\n')


def find_in_list(my_list, to_find):
    for element in my_list:
        if element == to_find:
            return True

    return False


run()