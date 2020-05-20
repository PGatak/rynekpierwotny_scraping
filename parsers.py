from bs4 import BeautifulSoup
from urllib.parse import urljoin


total_apartments_found = 0
def parse_developer_details(text, task):
    investments = []

    bs = BeautifulSoup(text, "lxml")

    offer_boxes = bs.find_all("div", {"class": "offer-box-holder"})

    for offer_box in offer_boxes:
        investment_details_a = offer_box.find("a", {"class": "offer-box"})
        investment_url = investment_details_a.attrs.get("href", "").strip()

        box = offer_box.find("div", {"class": "offer-box-info-holder"})

        name = box.find("h2")
        address = box.find("div", {"class", "offer-box-address-holder"})
        if not address:
            print("NO ADDRESS")
            continue
        p_city, p_street, *rest = address.find_all("p")

        div_amount = box.find_all("div", {"class": "tac"})[1]

        p_amount = div_amount.find_all("p")[0] if div_amount else []

        try:
            city_parts = [part.strip() for part in str(p_city.text).split(",")]
            city_name = city_parts.pop(0)
            city_district = None
            city_street = None

            if len(city_parts) > 1:
                city_district, city_street = city_parts
            if len(city_parts) == 1:
                city_street = city_parts[0]  # noqa: F841

            investment_data = {
                "name": str(name.text),
                "city_name": city_name,
                # "city_district": city_district,
                # "city_street": city_street,
                # "street": str(p_street.text),
                "url": investment_url,
                "amount": int(p_amount.text),
                "task": task,
            }
            investments.append(investment_data)
            print("\tApartments:", int(p_amount.text))
            global total_apartments_found
            total_apartments_found += int(p_amount.text)
            print("total_apartments_found", total_apartments_found)
        except Exception as e:
            print("ERROR: parsing investment", e)

    return investments
total_investments_found = 0
# KONTENER DEVELOPERÓW
def parse_developer_links(text, current_url):
    bs = BeautifulSoup(text, "lxml")
    #pending już nie jest pustą listą?
    pending_urls = []
    # KONTENERY Z DEVELOPERAMI
    article = bs.find("article")
    # POJEDYNCZY WPIS - DEVELOPER
    divs_panel_body = article.find_all("div", {"class": "panel-body"})
    global total_investments_found
    for panel in divs_panel_body:
        header = panel.find("h2")
        link = header.find("a")
        # LINK DO DEVELOPERA - ŁĄCZENIE
        new_url = link.attrs.get("href", None)
        new_url = urljoin(current_url, new_url)
        developer_name = str(link.text)
        investments_div = panel.find("div", {"class": "fwb"})
        number_of_investments = 0

        if investments_div:
            investments_link = investments_div.find("a")
            if investments_link:
                investments_text = investments_link.text.strip()
                investments_text = investments_text.split(" ")[0]
                if investments_text.isnumeric():
                    number_of_investments = int(investments_text)

        if not number_of_investments:
            print("\tSKIP", developer_name, number_of_investments)
            continue

        total_investments_found += number_of_investments
        print("\tOK", developer_name, number_of_investments)
        print("total_investments_found", total_investments_found)


        pending_urls.append({
            "url": new_url,
            # "details_url": current_url,
            "details": True,
            "developer_name": developer_name,
        })

    # EXTRACT PAGINATION LINK
    pagination = bs.find("ul", {"class": "pagination"})
    link = pagination.find("a", {"rel": "next"})
    if link:
        next_link = link.attrs.get("href")
        next_link = urljoin(current_url, next_link)

        pending_urls.append({
            "url": next_link,
            "details": False,
        })

    return pending_urls

