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


def test_parse_cordis_filters_ended_and_non_doctoral():
    from scrapers.live_sources import parse_cordis
    from datetime import date
    data = {"payload": {"results": [
        {"id": "1", "acronym": "OLD", "title": "Doctoral network on reservoirs", "teaser": "", "endDate": "31 Dec 2019"},
        {"id": "2", "acronym": "NEW", "title": "Doctoral network on CO2 storage", "teaser": "", "endDate": "31 Dec 2029"},
        {"id": "3", "acronym": "NOPHD", "title": "Reservoir sensor", "teaser": "hardware", "endDate": "31 Dec 2029"},
    ]}}
    out = parse_cordis(data, today=date(2026, 11, 16))
    assert [o["link"] for o in out] == ["https://cordis.europa.eu/project/id/2"]


def test_parse_nature_item():
    from scrapers.live_sources import parse_nature
    html = ('<ul><li class="lister__item"><h3 class="lister__header"><a href="  /naturecareers/job/1/x/  ">'
            '<span>PhD in reservoir geoscience</span></a></h3></li></ul>')
    out = parse_nature(html)
    assert out[0]["link"] == "https://www.nature.com/naturecareers/job/1/x/"
    assert "reservoir" in out[0]["title"]


def test_ssrf_guard_and_watch_parse():
    from scrapers.live_sources import is_public_http_url, parse_watch_page, filter_relevant
    assert not is_public_http_url("http://127.0.0.1:8000/x")
    assert not is_public_http_url("file:///etc/passwd")
    assert not is_public_http_url("http://localhost/")
    html = ('<a href="/p1">PhD position in reservoir simulation and CO2 storage</a>'
            '<a href="/p2">Double degree partner: Ufa Petroleum University site</a>')
    items = parse_watch_page(html, "https://uni.example.edu/jobs", "phd")
    titles = [i["title"] for i in filter_relevant(items)]
    assert any("reservoir simulation" in t for t in titles)
    assert not any("Ufa" in t for t in titles)


def test_noise_filter_drops_medical_reservoir():
    from scrapers.live_sources import relevance
    assert relevance("PhD position HIV-1 reservoir dynamics")[1] is False
