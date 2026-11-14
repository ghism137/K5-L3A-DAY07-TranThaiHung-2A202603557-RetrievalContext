"""Advanced challenge benchmark: International Debt Report 2026, 280 pages, all pages indexed.

    python -m src.adv_build_benchmark

Writes benchmark/advanced/questions.json. Questions were written from the ORIGINAL page images (and the PDF text layer),
before any pipeline output was looked at, and answers were checked against the page images by the author-assistant
(AI-proposed; the student reviews every item). Dev and test use disjoint pages. Each answerable question belongs to ONE
main group: table, diagram (image/schematic/infographic), chart, multihop, text. Unanswerable questions are in group
"abstain" and carry an absence_check that src.adv_verify_benchmark re-runs on all 280 pages.

Group definitions used here (the report has no photographs; its only images are decorative cover art):
  table    a printed table or list table (Table 1.1, Table 1.2, Country Groups appendix)
  diagram  a schematic or an infographic whose meaning is spatial: the three-tier architecture (Figure 3B.1), the annotated
           reading guide with a sample country profile, and the hierarchical creditor block diagram (Figure 2) of country profiles
  chart    a statistical chart read by axis, legend or printed data labels (bar, stacked bar, waterfall, line)
  multihop evidence from at least two pages or two figure panels, combined by a comparison or a calculation
  text     conditional information from running text
"""
from __future__ import annotations

import json

from . import config

OUT_DIR = config.BENCHMARK_DIR / "advanced"
ORIGIN = "ai_proposed_author_review_pending"
VERIFIED = "page image read against the original on 2026-11-15"

Q: list[dict] = []


def add(qid, split, group, question, answer, gold, why, *, tolerance=None, checks=None, tags=None):
    Q.append({"id": qid, "split": split, "group": group, "tags": tags or [], "question": question,
              "answerable": True, "expected_behavior": "search_and_answer", "expected_answer": answer,
              "tolerance": tolerance, "gold": gold, "checks": checks or [], "why": why, "origin": ORIGIN,
              "verified": VERIFIED})


def absent(qid, split, question, reason, regexes, *, visual_note=None):
    Q.append({"id": qid, "split": split, "group": "abstain", "tags": [], "question": question,
              "answerable": False, "expected_behavior": "search_and_abstain", "absence_reason": reason,
              "absence_check": {"regexes_over_all_pages": regexes, "visual_note": visual_note},
              "origin": ORIGIN, "verified": VERIFIED})


def g(page, kind, locator, evidence):
    return {"page": page, "kind": kind, "locator": locator, "evidence": evidence}


def need(page, *tokens, required=True):
    return {"page": page, "contains": list(tokens), "required": required}


# ------------------------------------------------------------------------------------------------- DEV (15 + 3)
add("d01", "dev", "table", "In Table 1.1, what was the debt stock owed to multilateral creditors in 2022, in US$ billion?",
    "1,236.5 (US$ billion)", [g(28, "table", "Table 1.1, row 'Multilateral creditors', column 2022", "1,236.5")],
    "Single cell lookup with row, column and unit.", checks=[need(28, "1,236.5")], tags=["lookup"])
add("d02", "dev", "table", "By how much did the long-term external debt stock of low- and middle-income countries increase between 2015 and 2025 according to Table 1.1?",
    "2,624.3 US$ billion (7,020.9 in 2025 minus 4,396.6 in 2015)",
    [g(28, "table", "Table 1.1, row 'Long-term', columns 2015 and 2025", "4,396.6 and 7,020.9")],
    "Difference of two cells in one row.", tolerance="±0.1", checks=[need(28, "7,020.9", "4,396.6")], tags=["calculation"])
add("d03", "dev", "table", "By how much did the debt stock owed to the World Bank (IBRD and IDA) increase between 2015 and 2025 in Table 1.1?",
    "220.7 US$ billion (498.7 minus 278.0)",
    [g(28, "table", "Table 1.1, row 'World Bank (IBRD and IDA)', columns 2015 and 2025", "278.0 and 498.7")],
    "Difference of two cells in a row whose label spans two lines.", tolerance="±0.1", checks=[need(28, "498.7", "278.0")], tags=["calculation"])
add("d04", "dev", "table", "In Table 1.1, in which year did the debt stock owed to the IMF (use of credit and SDR allocations) first exceed US$300 billion, and what was it?",
    "2021, at 386.4 US$ billion (it was 214.6 in 2020)",
    [g(28, "table", "Table 1.1, row 'IMF (Use of credit and SDR allocations)', columns 2020-2021", "214.6 then 386.4")],
    "Scan a row for a threshold crossing.", checks=[need(28, "386.4", "214.6")], tags=["threshold"])

add("d05", "dev", "chart", "In Figure B1.3.1, how many low-income countries are in the IDA-only group?",
    "23", [g(37, "chart", "Figure B1.3.1, stacked bar 'IDA-only countries', dark-blue (low-income) segment label", "23")],
    "Read a printed data label for one stack segment.", tags=["label"])
add("d06", "dev", "chart", "In Figure B1.3.1, which lending group contains the single high-income country?",
    "The IDA-only group (orange high-income segment labelled 1 on top of the IDA-only bar)",
    [g(37, "chart", "Figure B1.3.1, orange segment labelled 1 above 'IDA-only countries'", "1 high-income")],
    "Identify a legend colour and map it to a bar.", tags=["legend"])
add("d07", "dev", "chart", "According to Figure 2.10 panel b, how many LIC-DSF upgrades were recorded in 2025?",
    "6", [g(88, "chart", "Figure 2.10 panel b 'Number of upgrades', bar 2025, label 6", "6")],
    "Read a printed value from the right panel of a two-panel waterfall chart.", tags=["label"])
add("d08", "dev", "chart", "In Figure 2.10 panel a, in which year was the number of LIC-DSF downgrades highest, and how many were there?",
    "2021, with 7 downgrades (plotted as -7)", [g(88, "chart", "Figure 2.10 panel a 'Number of downgrades', bar 2021, label -7", "-7")],
    "Compare bars with negative labels.", tags=["extreme", "sign"])

add("d09", "dev", "diagram", "In Azerbaijan's country profile, how much of its public and publicly guaranteed debt is owed to the Asian Development Bank, in US$ million?",
    "1,925 (US$ million)", [g(150, "diagram", "Figure 2 creditor block diagram, 'MULTILATERAL' row, block 'Asian Dev. Bank'", "1,925")],
    "Read a block of a hierarchical creditor diagram.", tags=["blocks"])
add("d10", "dev", "diagram", "In Azerbaijan's country profile, which creditor type holds the largest share of public and publicly guaranteed debt: multilateral, bilateral or private creditors? Give the amounts.",
    "Private creditors, 5,133 US$ million, just above multilateral at 5,111; bilateral is 797",
    [g(150, "diagram", "Figure 2, row 'PUBLIC & PUBLICLY GUARANTEED - BY CREDITOR TYPE'", "Multilateral 5,111; bilateral 797; private creditors 5,133")],
    "Compare three labelled blocks that are almost equal in width.", tags=["blocks", "comparison"])
add("d11", "dev", "diagram", "In Kenya's country profile, which bilateral creditor is the largest, and how much is owed to it, in US$ million?",
    "China, 4,923 (US$ million)", [g(202, "diagram", "Figure 2 creditor block diagram, 'BILATERAL' row, block 'China'", "4,923")],
    "Read the largest block of a second-level creditor row.", tags=["blocks"])

add("d12", "dev", "multihop", "Between 2020 and 2025, how many more LIC-DSF downgrades than upgrades were recorded according to Figure 2.10?",
    "7 more downgrades (22 downgrades in panel a minus 15 upgrades in panel b)",
    [g(88, "chart", "Figure 2.10 panel a, final bar '2020-25'", "-22"), g(88, "chart", "Figure 2.10 panel b, final bar '2020-25'", "15")],
    "Combine the totals of two panels.", checks=[need(88, "22 were downgraded")], tags=["two panels", "calculation"])
add("d13", "dev", "multihop", "Which country had the larger total external debt stock in 2025, Kenya or Azerbaijan, and by how much, in US$ million?",
    "Kenya, by 33,986 US$ million (46,313 minus 12,327)",
    [g(202, "diagram", "Kenya profile, headline 'TOTAL EXTERNAL DEBT STOCK, 2025'", "46,313"),
     g(150, "diagram", "Azerbaijan profile, headline 'TOTAL EXTERNAL DEBT STOCK, 2025'", "12,327")],
    "Compare headline figures from two country pages.", checks=[need(202, "46,313"), need(150, "12,327")], tags=["two pages", "calculation"])

add("d14", "dev", "text", "What average interest rate did IDA-eligible countries face on new commitments in 2025, and how does that compare with the past?",
    "8.2 percent, the highest since the late 1980s",
    [g(20, "text", "Key Takeaways, bullet 'The countries that can least afford it are paying the most to borrow'",
       "average interest rate of 8.2 percent on new commitments during the year, the highest since the late 1980s")],
    "Conditional statement with a historical comparison.", checks=[need(20, "8.2 percent", "highest since the late 1980s")])
add("d15", "dev", "text", "What share of LMICs' new disbursements in 2025 came from public sector bond issuances, and how large was the issuance?",
    "68.1 percent of new disbursements; $250.6 billion, up 34.6 percent",
    [g(20, "text", "Key Takeaways, bullet 'The bond market reopened for LMICs'",
       "public sector bond issuances accounted for 68.1 percent of new disbursements in 2025, increasing 34.6 percent to $250.6 billion")],
    "Two linked facts from one sentence.", checks=[need(20, "68.1 percent", "$250.6 billion")])

absent("d16", "dev", "What was Ireland's total external debt stock at the end of 2025?",
       "Ireland is not covered: the report profiles low- and middle-income countries and the word never appears.",
       [r"\bIreland\b"])
absent("d17", "dev", "According to the report, what was the average inflation rate in Kenya in 2025?",
       "Kenya's profile gives debt ratios and terms, not inflation; 'inflation rate' never appears.",
       [r"\binflation rate\b", r"Kenya.{0,80}inflation", r"inflation.{0,80}Kenya"])
absent("d18", "dev", "What does Figure 2.30 show about debt service in IDA-eligible countries?",
       "Chapter 2 ends at Figure 2.16; Figure 2.30 does not exist.", [r"Figure 2\.(1[7-9]|[2-9]\d)\b"])

# ------------------------------------------------------------------------------------------------ TEST (24 + 6)
add("t01", "test", "table", "In Table 1.2, what were net debt inflows from the IMF to IDA-eligible countries in 2020, in US$ billion?",
    "15.2 (US$ billion)", [g(63, "table", "Table 1.2, row 'IMF', column 2020", "15.2")],
    "Single cell lookup in a nested row.", checks=[need(63, "15.2")], tags=["lookup"])
add("t02", "test", "table", "By how much did long-term PPG net debt inflows to IDA-eligible countries change between 2020 and 2025 in Table 1.2?",
    "A fall of 21.9 US$ billion (66.3 in 2020 to 44.4 in 2025)",
    [g(63, "table", "Table 1.2, memorandum row 'Long-term PPG', columns 2020 and 2025", "66.3 and 44.4")],
    "Difference of two cells in a memorandum row; sign matters.", tolerance="±0.1", checks=[need(63, "66.3", "44.4")], tags=["calculation", "sign"])
add("t03", "test", "table", "In Table 1.2, in which year were total net debt inflows to IDA-eligible countries highest, and what was the amount?",
    "2021, at 85.9 US$ billion", [g(63, "table", "Table 1.2, row 'Net debt inflows', maximum over 2015-2025", "85.9 in 2021")],
    "Find the maximum of a row.", checks=[need(63, "85.9")], tags=["extreme"])
add("t04", "test", "table", "By how much did net debt inflows from the World Bank to IDA-eligible countries change between 2020 and 2025 in Table 1.2?",
    "An increase of 1.5 US$ billion (13.3 in 2020 to 14.8 in 2025)",
    [g(63, "table", "Table 1.2, row 'World Bank', columns 2020 and 2025", "13.3 and 14.8")],
    "Difference of two cells.", tolerance="±0.1", checks=[need(63, "13.3", "14.8")], tags=["calculation"])
add("t05", "test", "table", "How many countries are listed in the East Asia and Pacific regional group in the Country Groups appendix?",
    "16", [g(269, "table", "Country Groups, Regional Groups, list 'East Asia and Pacific'", "Cambodia ... Viet Nam (16 names)")],
    "Count the entries of one list; the region page p138 also states '16 countries'.", checks=[need(269, "East Asia and Pacific", "Viet Nam")], tags=["count"])
add("t06", "test", "table", "In the Country Groups appendix, which data-reporting status code is shown next to China?",
    "(P), meaning preliminary data", [g(269, "table", "Country Groups, East Asia and Pacific list, entry 'China (P)'", "China (P)")],
    "Read a code in a list; the code legend is on p136 (A as reported, E estimated, P preliminary).", checks=[need(269, "China (P)")], tags=["lookup"])

add("t07", "test", "chart", "In Figure 3.3, how many loans and tranches were matched at End-2024?",
    "3,762", [g(113, "chart", "Figure 3.3, orange line 'Loans matched', End-2024 point label", "3,762")],
    "Read a printed point label on the right axis series.", checks=[need(113, "Figure 3.3")], tags=["label"])
add("t08", "test", "chart", "In Figure 3.3, what was the debt outstanding reported at End-2023, in US$ billion?",
    "61.8 (US$ billion)", [g(113, "chart", "Figure 3.3, dark-blue bar End-2023, label 61.8", "61.8")],
    "Read a bar label on the left axis series.", tags=["label"])
add("t09", "test", "chart", "In Figure 3.2, in which year was the share of countries reporting by March the highest?",
    "2025 (about 56 percent)", [g(111, "chart", "Figure 3.2, dark-blue 'March' bars, maximum over 2020-2025", "2025, about 56")],
    "Compare unlabeled bars of one series across years.", checks=[need(111, "Figure 3.2")], tags=["extreme"])
add("t10", "test", "chart", "In Figure 3.2, in which year was the share of late reporters and nonreporters the lowest?",
    "2025 (about 6 percent; p110 text gives 5.8 percent)", [g(111, "chart", "Figure 3.2, gold 'Late reporters and nonreporters' bars, minimum", "2025, about 6")],
    "Compare small unlabeled bars; 2023 is close (about 7).", checks=[need(111, "Figure 3.2")], tags=["extreme"])
add("t11", "test", "chart", "In Figure 3.1, approximately how many Sub-Saharan African countries are shown with debt coverage in 2025?",
    "About 24 (accept 23 to 25)", [g(110, "chart", "Figure 3.1, 'Coverage' group, 2025, light-blue bar (Sub-Saharan Africa)", "about 24")],
    "Estimate a bar height from the axis.", tolerance="23-25", checks=[need(110, "Figure 3.1")], tags=["estimate"])

add("t12", "test", "diagram", "In Figure 3B.1, what is Tier 2 called and what does it provide?",
    "Tier 2 is IDS (International Debt Statistics): 'Trusted, transparent statistics'",
    [g(132, "diagram", "Figure 3B.1, middle box", "Tier 2 / IDS / Trusted, transparent statistics")],
    "Identify one box of a three-box schematic.", checks=[need(132, "Figure 3B.1", "IDS")], tags=["schematic"])
add("t13", "test", "diagram", "What text is written on the dashed feedback arrow in Figure 3B.1?",
    "'Gaps and findings strengthen reporting' (it runs from Tier 3 back to Tier 1)",
    [g(132, "diagram", "Figure 3B.1, dashed loop below the three tiers", "Gaps and findings strengthen reporting")],
    "Read an arrow label; text alone does not say where the arrow goes.", checks=[need(132, "Gaps and findings strengthen reporting")], tags=["schematic", "arrow"])
add("t14", "test", "diagram", "Which tier is described as 'Actionable knowledge' in Figure 3B.1, and what does its acronym stand for?",
    "Tier 3, IDR, the International Debt Report", [g(132, "diagram", "Figure 3B.1, right box and Note line", "Tier 3 / IDR / Actionable knowledge; IDR = International Debt Report")],
    "Combine a box label with the acronym note below the figure.", checks=[need(132, "Actionable knowledge")], tags=["schematic"])
add("t15", "test", "diagram", "In the sample country profile on the reading-guide page, which country is shown, and what are its total external debt stock and its change from 2024?",
    "Belize; 1,609 US$ million; up 2.6 percent from 2024",
    [g(136, "diagram", "Annotated sample profile, header and headline figure", "BELIZE, 1,609, +2.6% from 2024")],
    "Read the headline of a screenshot-style sample.", checks=[need(136, "BELIZE")], tags=["annotated sample"])
add("t16", "test", "diagram", "In the sample profile on the reading-guide page, what are the average maturity and interest rate on new commitments from official creditors?",
    "24 years maturity and 3.6 percent interest rate (grace period 4 years)",
    [g(136, "diagram", "Annotated sample profile, Figure 4 card 'Official creditors'", "24 yrs, 4 yrs, 3.6%")],
    "Read small text inside a sample card.", tags=["annotated sample", "small text"])

add("t17", "test", "multihop", "Which country had the larger total external debt stock in 2025, Jordan or Peru, and by how much, in US$ million?",
    "Peru, by 43,751 US$ million (94,270 minus 50,519)",
    [g(230, "diagram", "Peru profile, headline total external debt stock 2025", "94,270"), g(200, "diagram", "Jordan profile, headline", "50,519")],
    "Compare headline figures from two country pages.", checks=[need(230, "94,270"), need(200, "50,519")], tags=["two pages", "calculation"])
add("t18", "test", "multihop", "What was the combined total external debt stock of Zambia and the Dominican Republic in 2025, in US$ million?",
    "84,917 US$ million (28,633 plus 56,284)",
    [g(262, "diagram", "Zambia profile, headline", "28,633"), g(175, "diagram", "Dominican Republic profile, headline", "56,284")],
    "Sum of headline figures from two country pages.", checks=[need(262, "28,633"), need(175, "56,284")], tags=["two pages", "calculation"])
add("t19", "test", "multihop", "What share of the total external debt stock of all low- and middle-income countries at end-2025 was owed by Sub-Saharan African countries?",
    "About 10.8 percent (1,020 of 9,445 US$ billion)",
    [g(143, "diagram", "Sub-Saharan Africa profile, headline", "1,020 US$ billion"), g(137, "diagram", "All low- and middle-income countries profile, headline", "9,445 US$ billion")],
    "Ratio of a regional headline to the aggregate headline; both pages are in US$ billion.", tolerance="10.7-10.9", checks=[need(143, "1,020"), need(137, "9,445")], tags=["two pages", "calculation"])
add("t20", "test", "multihop", "By how much did the total external debt stock of East Asia and Pacific exceed that of South Asia at end-2025, in US$ billion?",
    "2,358 US$ billion (3,313 minus 955)",
    [g(138, "diagram", "East Asia and Pacific profile, headline", "3,313"), g(142, "diagram", "South Asia profile, headline", "955")],
    "Difference of two regional headlines.", checks=[need(138, "3,313"), need(142, "955")], tags=["two pages", "calculation"])

add("t21", "test", "text", "By how much did the external debt of low-income countries rise in 2025?",
    "8.9 percent, to $262.4 billion (the biggest increase since 2020)",
    [g(19, "text", "Key Takeaways, bullet 'Debt accumulation accelerated sharply in 2025'",
       "for low-income countries, climbing 8.9 percent to $262.4 billion, the biggest increase since 2020")],
    "Pick the low-income sub-clause out of a sentence that also covers LMICs and IDA-eligible countries.", checks=[need(19, "8.9 percent to $262.4 billion")])
add("t22", "test", "text", "In 2025, how much more did remittances to LMICs exceed foreign direct investment, and what happened to FDI between 2011 and 2025?",
    "Remittances were about $294.5 billion more than FDI; FDI contracted by 25.5 percent from 2011 to 2025",
    [g(21, "text", "Key Takeaways, bullet 'Other financial flows to LMICs continue to diverge'",
       "FDI contract by 25.5 percent from 2011 to 2025 ... remittances were about $294.5 billion more than FDI")],
    "Two conditioned facts from one bullet.", checks=[need(21, "25.5 percent", "$294.5 billion")])
add("t23", "test", "text", "What happened to the debt-to-income ratio of IDA-eligible countries in 2025, and why?",
    "It fell from 42.1 percent to 41.2 percent, because economic growth outpaced debt accumulation and some countries benefited from debt restructuring",
    [g(21, "text", "Key Takeaways, bullet 'Debt burdens eased in IDA-eligible countries but rose elsewhere'",
       "debt-to-income ratio fell from 42.1 percent to 41.2 percent, as economic growth outpaced debt accumulation, and some countries benefited from debt restructuring")],
    "Value change plus its stated causes.", checks=[need(21, "42.1 percent to 41.2 percent")])
add("t24", "test", "text", "Which source mainly supplies the report's data on exports and imports, and which edition of the Balance of Payments Manual do the balance of payments data follow?",
    "The International Monetary Fund (supplemented by UN Trade and Development reports and country data); the sixth edition of the IMF Balance of Payments Manual",
    [g(267, "text", "Data Sources, second half of the page",
       "Data on exports and imports ... are drawn mainly from the International Monetary Fund ... sixth edition of the International Monetary Fund's Balance of Payments Manual")],
    "Two linked facts from different sentences.", checks=[need(267, "sixth edition", "drawn mainly from the International Monetary Fund")])

absent("t25", "test", "What was Switzerland's total external debt stock at the end of 2025?",
       "Switzerland is not covered and is not even named as a creditor.", [r"\bSwitzerland\b"])
absent("t26", "test", "In Figure 3.3, how many loans and tranches were reported at End-2022?",
       "Figure 3.3 shows only End-2021, End-2023 and End-2024; no End-2022 exercise is reported.", [r"end-2022"],
       visual_note="Figure 3.3 (p113) has exactly three bars: End-2021, End-2023, End-2024.")
absent("t27", "test", "What does Figure 3.7 show about creditor data sharing?",
       "Chapter 3 ends at Figure 3.4 (plus Figure 3B.1); Figure 3.7 does not exist.", [r"Figure 3\.[5-9]\b"])
absent("t28", "test", "What does the report project the total external debt stock of low- and middle-income countries will be at the end of 2027?",
       "No projection of the debt stock is given; the only forward-looking statement is that borrowing costs are projected to increase (p67).",
       [r"projected (to )?(total )?external debt", r"external debt[^.]{0,60}(2027|2028|2030)"])
absent("t29", "test", "In Azerbaijan's profile, what average interest rate applied to new commitments from private creditors in 2025?",
       "The Figure 4 card shows '..' for private creditors and the note says Azerbaijan had no new private commitments in 2025.",
       [], visual_note="p150 Figure 4: private creditors card shows '..' and the note says the country did not have new commitments in 2025.")
absent("t30", "test", "How much did Norway lend to low- and middle-income countries in 2025 according to the report?",
       "No creditor-country lending totals are given and Norway is never named.", [r"\bNorway\b"])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ids = [q["id"] for q in Q]
    assert len(ids) == len(set(ids)), "duplicate ids"
    (OUT_DIR / "questions.json").write_text(json.dumps(Q, ensure_ascii=False, indent=2), encoding="utf-8")
    from collections import Counter
    print(f"{len(Q)} questions ->", OUT_DIR / "questions.json")
    for split in ("dev", "test"):
        c = Counter(q["group"] for q in Q if q["split"] == split)
        print(split, dict(c), "answerable", sum(q["answerable"] for q in Q if q["split"] == split))


if __name__ == "__main__":
    main()
