from scrapers.global_deep_crawler import GLOBAL_COMPREHENSIVE_CATALOG

print("Catalog size:", len(GLOBAL_COMPREHENSIVE_CATALOG))
for i, opp in enumerate(GLOBAL_COMPREHENSIVE_CATALOG):
    print(f"[{i+1}] {opp['title']} | {opp['institution']} -> {opp['raw_link']}")
