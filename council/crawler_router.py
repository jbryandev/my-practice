from council.crawlers import edmond, el_reno, lawton, \
    midwest_city, moore, norman, okc, tulsa

def crawler_router(department, progress_recorder):
    crawler = None
    # Route the request to the appropriate crawler
    if department.agency == "City of Edmond":
        crawler = edmond.EdmondCrawler(department)

    elif department.agency.agency_name == "City of El Reno":
        crawler = el_reno.ElRenoCrawler(department)

    elif department.agency.agency_name == "City of Lawton":
        crawler = lawton.LawtonCrawler(department)

    elif department.agency.agency_name == "City of Midwest City":
        pass

    elif department.agency.agency_name == "City of Moore":
        pass

    elif department.agency.agency_name == "City of Oklahoma City":
        pass

    elif department.agency.agency_name == "City of Norman":
        pass

    elif department.agency.agency_name == "City of Tulsa":
        pass

    if crawler:
        # Start the crawler and record progress
        crawler.crawl(progress_recorder)


def midwest_city_crawler(calling_department, progress_recorder):
    """ Edmond Crawler function. """
    descr = 'Connecting to City website...'
    set_progress(progress_recorder, 0, 15, descr, 2)
    agendas_url = calling_department.agendas_url

    descr = 'Connection succeeded. Getting agenda list...'
    set_progress(progress_recorder, 1, 15, descr, 2)
    agendas_list = midwest_city.retrieve_agendas(agendas_url)

    descr = 'Searching for matching department agendas...'
    set_progress(progress_recorder, 2, 15, descr, 2)
    matched_agendas = midwest_city.match_agendas(agendas_list, calling_department.department_name)

    i = 1
    j = 0

    for agenda in matched_agendas:
        total = len(matched_agendas)
        descr = "Processing agenda " + str(i) + " of " + str(total) + "..."
        set_progress(progress_recorder, i+2, total+3, descr, 1)
        agenda_url = agenda.get("agenda_url")

        if not agenda_exists(agenda_url):
            j += 1
            new_agenda = Agenda(
                agenda_date=agenda.get("agenda_date"),
                agenda_title=agenda.get("agenda_title"),
                agenda_url=agenda_url,
                agenda_text="", # will be generated upon user request
                pdf_link=agenda_url,
                date_added=datetime.now(tz=get_current_timezone()),
                department=calling_department
            )
            new_agenda.save()
        i += 1

    descr = "Finished processing. Found " + str(j) + " new agendas."
    set_progress(progress_recorder, 14, 15, descr, 2)

def moore_crawler(calling_department, progress_recorder):
    """ Moore Crawler function. """
    progress_recorder.set_progress(0, 15, description="Connecting to City website...")
    time.sleep(2)
    agendas_url = calling_department.agendas_url

    progress_recorder.set_progress(
        1, 15, description="Connection succeeded. Getting agenda list...")
    time.sleep(2)
    agendas_list = moore.retrieve_agendas(agendas_url)

    progress_recorder.set_progress(
        2, 15, description="Searching for matching department agendas...")
    time.sleep(2)
    matched_agendas = moore.match_agendas(agendas_list, calling_department.department_name)

    i = 1
    j = 0

    for agenda in matched_agendas:
        progress_desc = "Processing agenda " + str(i) + " of " + str(len(matched_agendas)) + "..."
        progress_recorder.set_progress(i+2, len(matched_agendas)+3, description=progress_desc)
        time.sleep(1)
        agenda_url = moore.get_agenda_url(agenda.get("agenda_detail"))

        if agenda_url:
            if not agenda_exists(agenda_url):
                j += 1
                new_agenda = Agenda(
                    agenda_date=agenda.get("agenda_date"),
                    agenda_title=agenda.get("agenda_title"),
                    agenda_url=agenda_url,
                    agenda_text="", # will be generate upon user request
                    pdf_link=agenda_url,
                    date_added=datetime.now(tz=get_current_timezone()),
                    department=calling_department
                )
                new_agenda.save()
        i += 1

    progress_desc = "Finished processing. Found " + str(j) + " new agendas."
    progress_recorder.set_progress(14, 15, description=progress_desc)
    time.sleep(2)

def norman_crawler(calling_department, progress_recorder):
    """ Norman Crawler function. """
    progress_recorder.set_progress(0, 15, description="Connecting to City website...")
    time.sleep(2)
    agendas_url = calling_department.agendas_url

    progress_recorder.set_progress(
        1, 15, description="Connection succeeded. Getting agenda list...")
    time.sleep(2)
    agendas_list = norman.retrieve_agendas(agendas_url)

    progress_recorder.set_progress(
        2, 15, description="Searching for matching department agendas...")
    time.sleep(2)
    matched_agendas = norman.match_agendas(agendas_list, calling_department.department_name)

    i = 0
    j = 1

    for agenda in matched_agendas:
        progress_desc = "Processing agenda " + str(i) + " of " + str(len(matched_agendas)) + "..."
        progress_recorder.set_progress(i+2, len(matched_agendas)+3, description=progress_desc)
        time.sleep(1)
        agenda_url = agenda.get("agenda_url")

        if not agenda_exists(agenda_url):
            j += 1
            new_agenda = Agenda(
                agenda_date=agenda.get("agenda_date"),
                agenda_title=agenda.get("agenda_title"),
                agenda_url=agenda_url,
                agenda_text="", # will be generated upon user request
                pdf_link=agenda_url,
                date_added=datetime.now(tz=get_current_timezone()),
                department=calling_department
            )
            new_agenda.save()
        i += 1

    progress_desc = "Finished processing. Found " + str(j) + " new agendas."
    progress_recorder.set_progress(14, 15, description=progress_desc)
    time.sleep(2)

def okc_crawler(calling_department, progress_recorder):
    """ OKC Crawler function. """
    progress_recorder.set_progress(0, 15, description="Connecting to City website...")
    time.sleep(2)
    agendas_url = calling_department.agendas_url

    progress_recorder.set_progress(
        1, 15, description="Connection succeeded. Getting agenda list...")
    time.sleep(2)
    agendas_list = okc.retrieve_agendas(agendas_url)

    progress_recorder.set_progress(
        2, 15, description="Searching for matching department agendas...")
    time.sleep(2)
    matched_agendas = okc.match_agendas(agendas_list, calling_department.department_name)

    i = 1
    j = 0

    for agenda in matched_agendas:
        progress_desc = "Processing agenda " + str(i) + " of " + str(len(matched_agendas)) + "..."
        progress_recorder.set_progress(i+2, len(matched_agendas)+3, description=progress_desc)
        time.sleep(1)
        agenda_url = agenda.get("agenda_url")
        agenda_view_link = agenda.get("agenda_view_link")

        if not agenda_exists(agenda_url):
            j += 1
            agenda_text = okc.get_agenda_text(agenda_url)
            pdf_link = okc.get_agenda_pdf(agenda_view_link)
            new_agenda = Agenda(
                agenda_date=agenda.get("agenda_date"),
                agenda_title=agenda.get("agenda_title"),
                agenda_url=agenda_url,
                agenda_text=agenda_text,
                pdf_link=pdf_link,
                date_added=datetime.now(tz=get_current_timezone()),
                department=calling_department
            )
            new_agenda.save()
        i += 1

    progress_desc = "Finished processing. Found " + str(j) + " new agendas."
    progress_recorder.set_progress(14, 15, description=progress_desc)
    time.sleep(2)

def tulsa_crawler(calling_department, progress_recorder):
    """ Tulsa Crawler function. """
    progress_recorder.set_progress(0, 15, description="Connecting to City website...")
    time.sleep(2)
    agendas_url = calling_department.agendas_url

    progress_recorder.set_progress(
        1, 15, description="Connection succeeded. Getting agenda list...")
    time.sleep(2)
    agendas_list = tulsa.retrieve_agendas(agendas_url)

    progress_recorder.set_progress(
        2, 15, description="Searching for matching department agendas...")
    time.sleep(2)
    matched_agendas = tulsa.match_agendas(agendas_list, calling_department.department_name)

    i = 1
    j = 0

    for agenda in matched_agendas:
        progress_desc = "Processing agenda " + str(i) + " of " + str(len(matched_agendas)) + "..."
        progress_recorder.set_progress(i+2, len(matched_agendas)+3, description=progress_desc)
        time.sleep(1)
        agenda_url = agenda.get("agenda_url")

        if not agenda_exists(agenda_url):
            j += 1
            agenda_text = tulsa.get_agenda_content(agenda_url)
            new_agenda = Agenda(
                agenda_date=agenda.get("agenda_date"),
                agenda_title=agenda.get("agenda_title"),
                agenda_url=agenda_url,
                agenda_text=agenda_text,
                pdf_link="",
                date_added=datetime.now(tz=get_current_timezone()),
                department=calling_department
            )
            new_agenda.save()
        i += 1

    progress_desc = "Finished processing. Found " + str(j) + " new agendas."
    progress_recorder.set_progress(14, 15, description=progress_desc)
    time.sleep(2)
