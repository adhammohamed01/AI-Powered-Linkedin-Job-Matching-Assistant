def scrape_jobs(
    job_title: str,
    locations: list,
    job_type_inputs: str ,
    remote_filter_input: str,
    experience_level_inputs: str,
):
    import logging
    import os
    import pandas as pd
    import re
    from datetime import datetime
    from bs4 import BeautifulSoup
    from linkedin_jobs_scraper import LinkedinScraper
    from linkedin_jobs_scraper.events import Events, EventData
    from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
    from linkedin_jobs_scraper.filters import (
        RelevanceFilters,
        TimeFilters,
        TypeFilters,
        OnSiteOrRemoteFilters,
        ExperienceLevelFilters,
    )

    # ------------------------
    # Mapping user input to enums
    # ------------------------
    TYPE_FILTERS_MAP = {
        "full time": TypeFilters.FULL_TIME,
        "part time": TypeFilters.PART_TIME,
        "contract": TypeFilters.CONTRACT,
        "temporary": TypeFilters.TEMPORARY,
        "volunteer": TypeFilters.VOLUNTEER,
        "internship": TypeFilters.INTERNSHIP,
        "other": TypeFilters.OTHER,
    }

    REMOTE_FILTERS_MAP = {
        "on-site": OnSiteOrRemoteFilters.ON_SITE,
        "remote": OnSiteOrRemoteFilters.REMOTE,
        "hybrid": OnSiteOrRemoteFilters.HYBRID,
    }

    EXPERIENCE_LEVEL_MAP = {
        "from 0 to 6 months": ExperienceLevelFilters.INTERNSHIP,
        "from 0 to 2 years": ExperienceLevelFilters.ENTRY_LEVEL,
        "from 2 to 5 years": ExperienceLevelFilters.ASSOCIATE,
        "from 5 to 10 years": ExperienceLevelFilters.MID_SENIOR,
        "from 10 to 15 years": ExperienceLevelFilters.DIRECTOR,
        "15+ years": ExperienceLevelFilters.EXECUTIVE,
    }
    type_withoutspace=job_type_inputs.strip()
    remote_withoutspace=remote_filter_input.strip()
    experience_withoutspace=experience_level_inputs.strip()
    # Convert user input to filter enums
    job_types = TYPE_FILTERS_MAP.get(job_type_inputs) if type_withoutspace else None
    remote_filter = REMOTE_FILTERS_MAP.get(remote_filter_input) if remote_withoutspace else None
    experience_levels = EXPERIENCE_LEVEL_MAP.get(experience_level_inputs) if experience_withoutspace else None

    # ------------------------
    # Logging and scraper setup
    # ------------------------
    logging.basicConfig(level=logging.INFO)

    job_postings = []
    csv_filename = "../data/jobs.csv"

    def on_data(data: EventData):
        raw_description = getattr(data, 'description_html', None) or data.description
        soup = BeautifulSoup(raw_description, 'html.parser')
        full_description = soup.get_text(separator=' ', strip=True)
        full_description = re.sub(r'(Show more\s*)?(Show less\s*)?$', '', full_description, flags=re.IGNORECASE)

        print(
            "[ON_DATA]",
            data.title,
            data.company,
            data.company_link,
            data.date,
            data.link,
            data.insights,
            len(full_description),
        )
        job_postings.append(
            [
                data.job_id,
                data.location,
                data.title,
                data.company,
                data.date,
                data.link,
                full_description,
            ]
        )
        df = pd.DataFrame(
            job_postings,
            columns=[
                "Job_ID", "Location", "Title", "Company", "Date", "Link", "Description"
            ],
        )
        df.to_csv(csv_filename, index=False)
        print(f"Saved job postings to {csv_filename}")

    def on_error(error):
        print("[ON_ERROR]", error)

    def on_end():
        print(f"[ON_END] Scraping completed. Data saved to {csv_filename}")

    scraper = LinkedinScraper(
        chrome_executable_path=None,
        chrome_binary_location=None,
        chrome_options=None,
        headless=True,
        max_workers=1,
        slow_mo=0.5,
        page_load_timeout=40,
    )

    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, on_error)
    scraper.on(Events.END, on_end)
    if job_types and remote_filter and experience_levels:
        filters = QueryFilters(
            relevance=RelevanceFilters.RECENT,
            time=TimeFilters.MONTH,
            type=job_types,
            on_site_or_remote=remote_filter,
            experience=experience_levels
        )
    elif job_types and remote_filter:
        filters = QueryFilters(
            relevance=RelevanceFilters.RECENT,
            time=TimeFilters.MONTH,
            type=job_types,
            on_site_or_remote=remote_filter
        )
    elif job_types and experience_levels:
        filters = QueryFilters(
            relevance=RelevanceFilters.RECENT,
            time=TimeFilters.MONTH,
            type=job_types,
            experience=experience_levels
        )
    elif remote_filter and experience_levels:
        filters = QueryFilters(
            relevance=RelevanceFilters.RECENT,
            time=TimeFilters.MONTH,
            on_site_or_remote=remote_filter,
            experience=experience_levels
        )
    elif job_types:
        filters = QueryFilters(
            relevance=RelevanceFilters.RECENT,
            time=TimeFilters.MONTH,
            type=job_types
        )
    elif remote_filter:
        filters = QueryFilters(
            relevance=RelevanceFilters.RECENT,
            time=TimeFilters.MONTH,
            on_site_or_remote=remote_filter
        )
    elif experience_levels:
        filters = QueryFilters(
            relevance=RelevanceFilters.RECENT,
            time=TimeFilters.MONTH,
            experience=experience_levels
        )
        
    else:
        filters = QueryFilters(
            relevance=RelevanceFilters.RECENT,
            time=TimeFilters.MONTH
        )


    queries = [
        Query(
            query=job_title,
            options=QueryOptions(
                locations=locations,
                apply_link=True,
                skip_promoted_jobs=True,
                page_offset=0,
                limit=200,
                filters=filters,
            ),
        )
    ]

    scraper.run(queries)
    return scraper
