# -*- coding: utf-8 -*-
import sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scrapers.live_sources import parse_closing_date, relevance, parse_jobsac, filter_relevant, parse_arbeitnow

JOBSAC = """
<div class="j-search-result__result"><div class="j-search-result__text">
<a href="/job/X1/phd-studentship-co2-storage-in-porous-media">PhD Studentship: CO2 storage in porous media</a>
<div class="j-search-result__employer"><b>University of Test</b></div>
<div>Location: Edinburgh</div></div>
<div class="j-search-result__date-logos"><span class="j-search-result__date--blue">21 Dec</span></div></div>
<div class="j-search-result__result"><div class="j-search-result__text">
<a href="/job/X2/head-of-reservoir-engineering">Head of Reservoir Engineering</a>
<div class="j-search-result__employer"><b>BigOil Ltd</b></div></div></div>
"""

def test_closing_date_infers_year():
    assert parse_closing_date("21 Dec", date(2026, 11, 14)) == "2026-12-21"
    assert parse_closing_date("05 Jan", date(2026, 11, 14)) == "2027-01-05"
    assert parse_closing_date("3 March 2027") == "2027-03-03"
    assert parse_closing_date("garbage") is None

def test_relevance_and_level():
    s, ok = relevance("PhD in reservoir simulation for CCUS", "")
    assert s >= 2 and ok
    assert relevance("Senior Reservoir Engineer", "")[1] is False
    assert relevance("PhD in medieval history", "")[0] == 0

def test_parse_and_filter_jobsac():
    items = parse_jobsac(JOBSAC)
    assert len(items) == 2
    assert items[0]["link"].startswith("https://www.jobs.ac.uk/job/X1")
    assert items[0]["institution"] == "University of Test" and items[0]["deadline"].endswith("-12-21")
    kept = filter_relevant(items)
    assert [i["title"] for i in kept] == ["PhD Studentship: CO2 storage in porous media"]

def test_arbeitnow_company_source():
    data = {"data": [{"title": "Master Thesis Geothermal Reservoir", "url": "https://x/y", "company_name": "NewCo GmbH",
                      "location": "Berlin", "tags": [], "description": "<p>thesis on geothermal</p>"}]}
    kept = filter_relevant(parse_arbeitnow(data))
    assert kept and kept[0]["institution"] == "NewCo GmbH"


def test_company_boards_and_adzuna_parsers():
    from scrapers.live_sources import parse_greenhouse, parse_lever, parse_adzuna
    gh = parse_greenhouse("fervoenergy", {"jobs": [{"title": "Geothermal Reservoir Engineering Intern",
                          "absolute_url": "https://x/1", "location": {"name": "Houston"}}]})
    assert filter_relevant(gh)[0]["institution"] == "Fervoenergy"
    lv = parse_lever("acme", [{"text": "Graduate Subsurface Engineer", "hostedUrl": "https://y", "categories": {"location": "Oslo"}, "descriptionPlain": "reservoir"}])
    assert filter_relevant(lv)
    ad = parse_adzuna("gb", {"results": [{"title": "PhD CO2 storage", "redirect_url": "https://z", "company": {"display_name": "Co"}, "location": {"display_name": "Leeds"}, "description": "phd"}]})
    assert filter_relevant(ad)[0]["country"] == "UK"


def test_normalize_country():
    from scrapers.live_sources import normalize_country
    assert normalize_country("Trondheim, Sør-Trøndelag") == "Norway"
    assert normalize_country("Somewhere unknown") == "دولي"
