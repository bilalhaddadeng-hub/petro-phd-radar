import re

files_to_check = [
    r"C:\Users\admin\.gemini\antigravity\scratch\petro_phd_radar_bot\scrapers\global_deep_crawler.py",
    r"C:\Users\admin\.gemini\antigravity\brain\d69fd1b1-6f29-4622-bc09-abe3f05e5081\phd_widget.html",
    r"C:\Users\admin\.gemini\antigravity\scratch\petro_phd_radar_bot\dashboard.html"
]

replacements = {
    "https://www.eni.com/it-IT/carriere/formazione.html": "https://www.polito.it/didattica/dottorato-di-ricerca/ammissione-al-dottorato",
    "https://theses.ifpen.fr/sujet-caprock-integrity-ccus": "https://theses.ifpen.fr/",
    "https://theses.ifpen.fr/sujet-hydrogen-pore-scale-flow": "https://theses.ifpen.fr/",
    "https://euraxess.ec.europa.eu/jobs/msca-miningbrines-subsurface": "https://euraxess.ec.europa.eu/jobs/search",
    "https://euraxess.ec.europa.eu/jobs/freiberg-hydrogen-storage": "https://tu-freiberg.de/en/grafa",
    "https://euraxess.ec.europa.eu/jobs/tudelft-subsurface-sciml": "https://www.tudelft.nl/citg/over-faculteit/afdelingen/geoscience-engineering",
    "https://dpe.ac.at/jobs-career/": "https://geoenergy.engineering/",
    "https://www.uis.no/en/research/phd-programmes": "https://www.uis.no/en",
    "https://www.ifpenergiesnouvelles.com/carrieres/offres-demploi-et-de-stage": "https://www.ifpenergiesnouvelles.fr/",
    "https://www.ogs.it/it/concorsi-e-selezioni": "https://www.ogs.it/it",
    "https://www.agh.edu.pl/en/doctoral-school": "https://sd.agh.edu.pl/en/",
    "https://careers.slb.com/early-careers/research-and-technology": "https://careers.slb.com/early-careers",
    "https://www.ntnu.edu/studies/phing/petroleum": "https://www.ntnu.edu/phd",
    "https://www.upg-ploiesti.ro/en": "https://www.upg-ploiesti.ro/",
    "https://www.ku.ac.ae/": "https://cpg.kfupm.edu.sa/academics/departments/department-of-petroleum-engineering/graduate-programs/"
}

for fpath in files_to_check:
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        changes = 0
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                changes += 1
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"File {fpath}: replaced {changes} broken URLs.")
    except Exception as e:
        print(f"Error on {fpath}: {e}")
