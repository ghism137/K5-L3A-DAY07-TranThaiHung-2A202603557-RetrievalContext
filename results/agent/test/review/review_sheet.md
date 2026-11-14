# Bảng chấm tay — test (ẩn tên hệ thống)

Mỗi câu có hai hệ thống (1 và 2) theo thứ tự xáo trộn; tên cấu hình nằm ở `blind_key.json` (chỉ mở sau khi chấm xong). Tiền tố ID chunk được che thành `c:`. Điền nhãn vào `review_labels.json` (mục `item` trùng tiêu đề từng khối).

## Thang chấm (BENCHMARK.md)

- **context_grade** (câu có đáp án): 0 = context không có evidence; 1 = có nhưng thiếu điều kiện hoặc nguồn; 2 = đủ evidence và nguồn. Chấm trên *context cuối* của hệ thống, kể cả khi hệ thống từ chối.
- **answer_grade** (câu có đáp án): 0 = sai/thiếu evidence, hoặc từ chối; 1 = đúng một phần; 2 = đúng và đủ.
- **citation_support**: một `true/false` cho từng citation: chunk được trích có *thực sự* hỗ trợ câu trả lời (ID hợp lệ chưa đủ). Hệ thống từ chối thì danh sách rỗng.
- **abstention_correct** (câu thiếu evidence): `true` chỉ khi hệ thống từ chối và không thêm khẳng định vô căn cứ.

---

## n01 — có đáp án

**Câu hỏi:** Within Sub-Saharan Africa, which country was the largest international bond issuer in 2025, and how much did it raise?

**Đáp án mong đợi:** Kenya, which raised $3.5 billion in 2025.

**Evidence gold:** trang 64: "Kenya, the largest issuer in the region, raised $3.5 billion in 2025."

**Key facts:** ['Kenya, the largest issuer in the region', '$3.5 billion in 2025']

### n01#1 — Hệ thống 1

- Trạng thái: **answered** (answer); số lượt tìm: 1
- Truy vấn: `largest international bond issuer in Sub-Saharan Africa 2025`

**Câu trả lời trả về:** In 2025, Kenya was the largest international bond issuer in Sub-Saharan Africa, raising $3.5 billion. This issuance was part of a strategy to prepay its 2027 and 2028 maturity obligations ahead of schedule [c:p0064:002].

**Citation 1:** `c:p0064:002`

> The restoration of access to capital markets has been particularly consequential for Sub-Saharan Africa, which accounted for 64 percent of IDA-eligible countries’ total public sector issuances (figure 1.19). The public sectors of eight countries in Sub-Saharan Africa collectively raised approximately $11.8 billion by end-December 2025, a marked 36.2 percent increase over 2024. Several issuers returned after prolonged absences: Kenya, the largest issuer in the region, raised $3.5 billion in 2025. The country returned to bond markets to prepay its 2027 and 2028 maturity obligations ahead of schedule. Côte d’Ivoire raised a total of $2.5 billion in 2025.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0064:002] (page 64)
The restoration of access to capital markets has been particularly consequential for Sub-Saharan Africa, which accounted for 64 percent of IDA-eligible countries’ total public sector issuances (figure 1.19). The public sectors of eight countries in Sub-Saharan Africa collectively raised approximately $11.8 billion by end-December 2025, a marked 36.2 percent increase over 2024. Several issuers returned after prolonged absences: Kenya, the largest issuer in the region, raised $3.5 billion in 2025. The country returned to bond markets to prepay its 2027 and 2028 maturity obligations ahead of schedule. Côte d’Ivoire raised a total of $2.5 billion in 2025.

[c:p0066:002] (page 66)
Average interest rates on new bond issuances among IDA-eligible countries in Sub-Saharan Africa increased 1.1 percentage point in 2025, to 9.8 percent. As IDA-eligible countries’ reliance on bond markets grows, it comes at much higher risk and cost relative to official lending.

[c:p0064:003] (page 64)
Importantly, a substantial share of proceeds from the two countries’ debt offerings funded their liability management operations, refinancing upcoming bullet maturities, and thereby easing rollover pressures. Nigeria, the third-largest issuer in the region, raised $2.3 billion in a dual-tranche international bond issue that was divided into one tranche with a 10-year maturity at 8.625 percent and a second, 20-year maturity tranche at 9.125 percent. Remarkably, Uganda’s share of domestic currency government debt held by nonresidents reached $2.8 billion in 2025, indicating strong demand for high-yield debt from international investors. Among countries in other regions, Uzbekistan recorded the highest international bond issuance among IDA-eligible countries in 2025, at $3.9 billion.
```

</details>

### n01#2 — Hệ thống 2

- Trạng thái: **answered** (answer); số lượt tìm: 1
- Truy vấn: `largest international bond issuer Sub-Saharan Africa 2025`

**Câu trả lời trả về:** In 2025, Kenya was the largest international bond issuer in Sub-Saharan Africa, raising $3.5 billion. This issuance was aimed at prepaying its 2027 and 2028 maturity obligations ahead of schedule, and a significant portion of the proceeds was used for liability management operations, including refinancing upcoming bullet maturities to ease rollover pressures [c:p0064:002].

**Citation 1:** `c:p0064:002`

> onged absences: Kenya, the largest issuer in the region, raised $3.5 billion in 2025. The country returned to bond markets to prepay its 2027 and 2028 maturity obligations ahead of schedule. Côte d’Ivoire raised a total of $2.5 billion in 2025. Importantly, a substantial share of proceeds from the two countries’ debt offerings funded their liability management operations, refinancing upcoming bullet maturities, and thereby easing rollover pressures. Nigeria, the third-largest issuer in the region, raised $2.3 billion in a dual-tranche international bond issue that was divided into one tranche with a 10-year maturity at 8.625 percent and a second, 20-year maturity tranche at 9.125 percent. Remarkably, Uganda’s share of domestic currency government debt held by nonresidents reached $2.8 bill

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0064:002] (page 64)
onged absences: Kenya, the largest issuer in the region, raised $3.5 billion in 2025. The country returned to bond markets to prepay its 2027 and 2028 maturity obligations ahead of schedule. Côte d’Ivoire raised a total of $2.5 billion in 2025. Importantly, a substantial share of proceeds from the two countries’ debt offerings funded their liability management operations, refinancing upcoming bullet maturities, and thereby easing rollover pressures. Nigeria, the third-largest issuer in the region, raised $2.3 billion in a dual-tranche international bond issue that was divided into one tranche with a 10-year maturity at 8.625 percent and a second, 20-year maturity tranche at 9.125 percent. Remarkably, Uganda’s share of domestic currency government debt held by nonresidents reached $2.8 bill

[c:p0043:000] (page 43)
the goal of lengthening the maturity profiles of their portfolios and reducing the cost of servicing these obligations. In 2025, Kenya issued new bonds of $3.5 billion that were used to execute two debt buyback operations, the largest from an IDA-eligible country, at $1.2 billion. The proceeds were used to smooth the maturity profile of existing liabilities by refinancing near-term liabilities with longer-dated debt, including the $900 million Eurobond maturing in 2027 and the $1 billion Eurobond maturing in 2028. (Refer to the “Debt Reorganization, 2025” section for a more detailed discussion on the liability management operations implemented in 2025.) New bond issuance from the PNG sector of LMICs also increased in 2025, albeit at a slower pace of 18.7 percent and about half the volume o

[c:p0054:003] (page 54)
private creditors. For Sub-Saharan African issuers, the combination of higher coupons and shorter maturities signals a particularly adverse shift in financing conditions that compounds already-constrained fiscal positions. These dynamics reinforce the importance of transparent debt management and underscore the role that concessional financing from the World Bank Group plays in helping the most vulnerable governments avoid excessive reliance on high-cost market borrowing. Box 1.5 Early 2026 Data Show No Signs of Slowdown in LMIC Bond Market Activity (continued)
```

</details>

---

## n02 — có đáp án

**Câu hỏi:** For which food groups do countries with heavier debt burdens relative to exports import from a wider variety of suppliers?

**Đáp án mong đợi:** Oils and fats, and legumes, nuts, and seeds.

**Evidence gold:** trang 100: "By contrast, higher debt burdens are associated with greater import source diversity for oils and fats, and for legumes, nuts, and seeds."

**Key facts:** ['greater import source diversity for oils and fats', 'legumes, nuts, and seeds']

### n02#1 — Hệ thống 1

- Trạng thái: **answered** (answer); số lượt tìm: 3
- Truy vấn: `food groups countries heavier debt burdens relative to exports import wider variety of suppliers`; `food groups import reliance diversification suppliers debt burdens`; `food groups import reliance diversification suppliers debt burdens`

**Câu trả lời trả về:** Countries with heavier debt burdens relative to exports tend to import from a wider variety of suppliers across different food groups. This is indicated by the relationship between import reliance and source diversification, which captures complementary dimensions of food import exposure. The variation in reliance on imported supply across food groups reflects differences in domestic production capacity, tradability, storability, perishability, and the structure of global suppliers. Specifically, net import reliance varies substantially across the six food groups that make up the Healthy Diet Basket, suggesting that countries with high debt-to-export ratios may diversify their import sources to enhance resilience against external shocks [c:p0096:001][c:p0101:002].

**Citation 1:** `c:p0096:001`

> During external shocks, higher import costs can therefore coincide with weaker economic and external buffers; export earnings may also decline, further increasing pressure on foreign exchange resources and raising the debt-to-exports ratio, even without an increase in the debt stock. Import Reliance and Debt Burdens Across Food Groups Aggregate food import shares do not show how strongly the domestic supply of individual food groups depends on international markets. Net import reliance— net imports as a share of domestic supply quantity—varies substantially across the six food groups making up the Healthy Diet Basket (Bai, Herforth et al. 2025; Herforth et al. 2025).

**Citation 2:** `c:p0101:002`

> Import reliance and source diversification capture complementary dimensions of food import exposure and together provide a broader indication of resilience in access to healthy diets when external shocks occur. Heterogeneity across food groups in both dimensions may reflect differences in domestic production capacity, tradability, storability, and perishability, as well as in the structure and concentration of global suppliers.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0096:001] (page 96)
During external shocks, higher import costs can therefore coincide with weaker economic and external buffers; export earnings may also decline, further increasing pressure on foreign exchange resources and raising the debt-to-exports ratio, even without an increase in the debt stock. Import Reliance and Debt Burdens Across Food Groups Aggregate food import shares do not show how strongly the domestic supply of individual food groups depends on international markets. Net import reliance— net imports as a share of domestic supply quantity—varies substantially across the six food groups making up the Healthy Diet Basket (Bai, Herforth et al. 2025; Herforth et al. 2025).

[c:p0096:000] (page 96)
in healthy diet unaffordability over time, a broader outcome that reflects both food costs and people’s economic resources.

Food Import Shares in Poorer Economies
Across the sample, which consists predominantly of LMICs, the share of food in merchandise imports generally declines as income per capita rises (figure 2.13, panel a). By contrast, economies with larger external debt burdens relative to exports also tend to have higher food import shares (figure 2.13, panel b).5 Both relationships matter for an economy’s capacity to manage food import exposure. Lower-income economies may have less room to absorb increases in import costs, and a high debt-to-exports ratio indicates that external debt is large relative to export earnings.

[c:p0095:004] (page 95)
Previous analysis in International Debt Report 2025 showed that higher external debt burdens were associated with higher levels of unaffordability of healthy diets across countries (World Bank 2025). This section extends that analysis by examining food import exposure as one important source of vulnerability to external shocks, including the importance of food in merchandise imports, reliance on imported supply across food groups, and the diversification of import sources. It also examines associations between external debt burdens and changes

[c:p0101:002] (page 101)
Import reliance and source diversification capture complementary dimensions of food import exposure and together provide a broader indication of resilience in access to healthy diets when external shocks occur. Heterogeneity across food groups in both dimensions may reflect differences in domestic production capacity, tradability, storability, and perishability, as well as in the structure and concentration of global suppliers.
```

</details>

### n02#2 — Hệ thống 2

- Trạng thái: **answered** (answer); số lượt tìm: 3
- Truy vấn: `food groups countries heavier debt burdens relative to exports import wider variety of suppliers`; `food import reliance debt burdens variety of suppliers`; `food groups import variety suppliers debt burdens`

**Câu trả lời trả về:** Countries with heavier debt burdens relative to exports show a higher net import reliance on specific food groups. Among these, the highest median reliance is for oils and fats, which stands at 63% of domestic supply. This indicates that countries with significant debt burdens tend to import a wider variety of suppliers for oils and fats compared to other food groups, reflecting their vulnerability to external shocks and the need for diverse import sources to stabilize their food supply amidst economic pressures [c:p0096:001].

**Citation 1:** `c:p0096:001`

> bt is large relative to export earnings. During external shocks, higher import costs can therefore coincide with weaker economic and external buffers; export earnings may also decline, further increasing pressure on foreign exchange resources and raising the debt-to-exports ratio, even without an increase in the debt stock. Import Reliance and Debt Burdens Across Food Groups Aggregate food import shares do not show how strongly the domestic supply of individual food groups depends on international markets. Net import reliance— net imports as a share of domestic supply quantity—varies substantially across the six food groups making up the Healthy Diet Basket (Bai, Herforth et al. 2025; Herforth et al. 2025). Among net importing economies, median reliance is highest for oils and fats, at 63.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0096:001] (page 96)
bt is large relative to export earnings. During external shocks, higher import costs can therefore coincide with weaker economic and external buffers; export earnings may also decline, further increasing pressure on foreign exchange resources and raising the debt-to-exports ratio, even without an increase in the debt stock. Import Reliance and Debt Burdens Across Food Groups Aggregate food import shares do not show how strongly the domestic supply of individual food groups depends on international markets. Net import reliance— net imports as a share of domestic supply quantity—varies substantially across the six food groups making up the Healthy Diet Basket (Bai, Herforth et al. 2025; Herforth et al. 2025). Among net importing economies, median reliance is highest for oils and fats, at 63.

[c:p0095:003] (page 95)
especially in lower-income countries (FAO and World Bank 2018). Previous analysis in International Debt Report 2025 showed that higher external debt burdens were associated with higher levels of unaffordability of healthy diets across countries (World Bank 2025). This section extends that analysis by examining food import exposure as one important source of vulnerability to external shocks, including the importance of food in merchandise imports, reliance on imported supply across food groups, and the diversification of import sources. It also examines associations between external debt burdens and changes

[c:p0103:001] (page 103)
nificant during 2019–21 and remained similarly strong and significant during 2021–23. In these periods, economies with higher debt stocks relative to export earnings tended to experience larger increases, or smaller declines, in healthy diet unaffordability. A doubling of the debt-to-exports ratio was associated with a more adverse change in unaffordability of approximately 1.6–1.8 percentage points. During 2023–25, the relationship weakened again and was no longer statistically significant. As revealed in this section, food import vulnerability reflects both reliance on imported supply and the concentration of import sources, and these dimensions can coincide with high external debt burdens. The period analysis adds an outcome perspective, showing that higher debt burdens are more strongl
```

</details>

---

## q16 — có đáp án

**Câu hỏi:** When the European Union's support to Ukraine is excluded, by how much did LMICs' debt stock owed to multilateral creditors increase?

**Đáp án mong đợi:** It increased 7.0 percent, to $1.4 trillion.

**Evidence gold:** trang 38: "when the European Union’s support to Ukraine is excluded, debt stock owed to multilateral creditors increased 7.0 percent to $1.4 trillion"

**Key facts:** ['support to Ukraine is excluded', '7.0 percent to $1.4 trillion']

### q16#1 — Hệ thống 1

- Trạng thái: **abstain** (invalid_or_missing_citations); số lượt tìm: 1
- Truy vấn: `When the European Union's support to Ukraine is excluded, by how much did LMICs' debt stock owed to multilateral creditors increase?`

**Câu trả lời trả về:** Không đủ bằng chứng để trả lời.

<details><summary>Bản nháp model viết nhưng bị loại do citation không hợp lệ (không tính là câu trả lời)</summary>

When the European Union's support to Ukraine is excluded, LMICs' debt stock owed to multilateral creditors increased by 7.0 percent, reaching $1.4 trillion in 2026. In contrast, the overall debt stock owed to multilateral creditors increased by 9.6 percent to $1.5 trillion in 2025, including the EU's support to Ukraine. This indicates a significant difference in the growth rate when the EU's contributions are considered or excluded.

citations khai báo: ['c:p0038:001']

</details>

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0038:001] (page 38)
leration Loans for Ukraine initiative, the cumulative countercyclical lending by these institutions decelerated in 2025. (Box 1.4 describes the international support for Ukraine through this initiative.) LMICs’ debt stock owed to multilateral creditors increased 9.6 percent to $1.5 trillion in 2025. However, when the European Union’s support to Ukraine is excluded, debt stock owed to multilateral creditors increased 7.0 percent to $1.4 trillion in 2026. Box 1.4 International Support for Ukraine: The G-7 Extraordinary Revenue Acceleration A Surge in Lending, Concentrated Among Official Creditors Financial support for Ukraine from bilateral and multilateral creditors has reached unprecedented levels since the start of the Ukraine War in February 2022. Official creditors, including the Group

[c:p0044:002] (page 44)
g-term debt inflows decreased from 46.2 percent in 2024 to 24.8 percent in 2025. Net debt inflows from official multilateral creditors accounted for 89.4 percent of the official flows, increasing 3.8 percent to $74.1 billion in 2025. Inflows from official bilateral creditors almost doubled to $8.8 billion but accounted for a moderate 10.6 percent share of total official flows. Increased extraordinary financing from the European Union and select bilateral creditors toward the Extraordinary Revenue Acceleration Loans for Ukraine initiative raised the total official inflows of LMICs in 2025. When Ukraine is excluded, LMICs’ net debt inflows from official multilateral creditors decreased 42.4 percent to $42.7 billion in 2025. For this group of countries, official bilateral creditors recorded a

[c:p0038:000] (page 38)
LMICs’ debt stock owed to all other creditor groups also increased in 2025. Debt stock owed to official creditors (public institutions such as national governments and international organizations) increased 8.4 percent in 2025, to $2.0 trillion. Lending by official bilateral creditors (national governments and their agencies) also showed a comeback, increasing 4.7 percent in 2025 after a 3.4 percent retrenchment in 2024. Support from multilateral institutions such as the World Bank Group and the IMF continued to be positive in 2025, but at a decreasing pace when compared to the COVID-19 pandemic era. Except for the multilateral support to Ukraine provided under the Extraordinary Revenue Acceleration Loans for Ukraine initiative, the cumulative countercyclical lending by these institutions
```

</details>

### q16#2 — Hệ thống 2

- Trạng thái: **abstain** (invalid_or_missing_citations); số lượt tìm: 1
- Truy vấn: `When the European Union's support to Ukraine is excluded, by how much did LMICs' debt stock owed to multilateral creditors increase?`

**Câu trả lời trả về:** Không đủ bằng chứng để trả lời.

<details><summary>Bản nháp model viết nhưng bị loại do citation không hợp lệ (không tính là câu trả lời)</summary>

When the European Union's support to Ukraine is excluded, LMICs' debt stock owed to multilateral creditors increased by 7.0 percent to $1.4 trillion in 2026. In contrast, the overall debt stock owed to multilateral creditors increased by 9.6 percent to $1.5 trillion in 2025, including the EU's support to Ukraine. This indicates a significant difference in the growth rates when EU support is considered or excluded.

citations khai báo: ['[c:p0038:001]']

</details>

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0038:001] (page 38)
Except for the multilateral support to Ukraine provided under the Extraordinary Revenue Acceleration Loans for Ukraine initiative, the cumulative countercyclical lending by these institutions decelerated in 2025. (Box 1.4 describes the international support for Ukraine through this initiative.) LMICs’ debt stock owed to multilateral creditors increased 9.6 percent to $1.5 trillion in 2025. However, when the European Union’s support to Ukraine is excluded, debt stock owed to multilateral creditors increased 7.0 percent to $1.4 trillion in 2026.

[c:p0044:003] (page 44)
Increased extraordinary financing from the European Union and select bilateral creditors toward the Extraordinary Revenue Acceleration Loans for Ukraine initiative raised the total official inflows of LMICs in 2025. When Ukraine is excluded, LMICs’ net debt inflows from official multilateral creditors decreased 42.4 percent to $42.7 billion in 2025. For this group of countries, official bilateral creditors recorded a strong increase of 43.7 percent in 2025, to $5.3 billion, which remained below the $17.2 billion decade average recorded, before plummeting in 2024.

[c:p0031:000] (page 31)
When China is excluded, the cumulative external debt stock of MICs increased at a much faster pace—by 9.1 percent in 2025, to $6.9 trillion in 2025. An increase of that magnitude has not been seen since 2017 and was concentrated among the 10 largest LMIC borrowers other than China. 1 These borrowers account for 59.5 percent of all LMIC external debt. Half of them recorded double-digit increases in their borrowing levels in 2025, led by a 29.2 percent increase in Ukraine’s debt stock, to $250.3 billion, following continued and unprecedented support from the Group of Seven countries and multilateral creditors. Argentina, Colombia, South Africa, and Türkiye also experienced double-digit increases in their external debt positions.
```

</details>

---

## q17 — có đáp án

**Câu hỏi:** Which kind of repayment weighs most heavily on the cash-borrowing requirements of the poorest countries?

**Đáp án mong đợi:** Domestic debt amortization dominates gross financing needs for low-income countries.

**Evidence gold:** trang 90: "Consequently, domestic debt amortization dominates GFNs for LICs"

**Key facts:** ['domestic debt amortization dominates GFNs for LICs']

### q17#1 — Hệ thống 1

- Trạng thái: **abstain** (model_abstain); số lượt tìm: 1
- Truy vấn: `Which kind of repayment weighs most heavily on the cash-borrowing requirements of the poorest countries?`

**Câu trả lời trả về:** Không đủ bằng chứng để trả lời.

*Lý do model nêu:* The passages do not contain specific information about which kind of repayment weighs most heavily on the cash-borrowing requirements of the poorest countries.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0084:002] (page 84)
In many countries, shocks that initially generated temporary financing needs have contributed to persistently higher debt stocks, debt service burdens, and rollover requirements.

The Impact of Higher Debt on Fiscal Space and Financing Pressures
The accumulation of public debt has been accompanied by a substantial increase in debt service burdens in LMICs over the past 25 years. The median total debt service in countries eligible for International Development Association (IDA) assistance increased from about 15 percent of government revenues (excluding grants) in 2000 to over 40 percent in 2025. During the same period,

[c:p0092:000] (page 92)
borrowing increases exposure to exchange rate and refinancing shocks. At the same time, high debt limits countries’ ability to borrow to close financing gaps. Countries are therefore left increasingly exposed to shocks, with minimal fiscal and financial buffers.

[c:p0084:001] (page 84)
Debt Sustainability and Fiscal Pressures
External shocks have compounded preexisting fiscal pressures and increased debt vulnerabilities in LMICs. These countries require substantial investment to raise productivity, create jobs, and advance broader development objectives. Financing these needs depends on mobilizing domestic resources, attracting domestic and foreign private capital, and, where necessary, borrowing through public channels. In this context, part of the increase in public debt reflects efforts to finance infrastructure, human capital, and other investments that can support long-term growth. However, slower global growth, policy uncertainty, trade fragmentation, geopolitical tensions, and commodity-price volatility have affected both the availability and cost of financing.
```

</details>

### q17#2 — Hệ thống 2

- Trạng thái: **abstain** (model_abstain); số lượt tìm: 1
- Truy vấn: `Which kind of repayment weighs most heavily on the cash-borrowing requirements of the poorest countries?`

**Câu trả lời trả về:** Không đủ bằng chứng để trả lời.

*Lý do model nêu:* The passages do not contain specific information about which kind of repayment weighs most heavily on the cash-borrowing requirements of the poorest countries.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0085:001] (page 85)
ncertainty of premium embedded in borrowing costs. These developments have contributed to a sustained increase in gross financing needs (GFNs) in IDA countries. Higher debt service burdens have important implications for fiscal space and refinancing needs. A larger share of government revenues must be allocated to interest payments, leaving fewer resources available for public investment and other policy priorities. At the same time, the need to Figure 2.8 Debt Service as Percentage of Government Revenues for IDA-Eligible Countries, 2000–25 Percent of revenues 0 10 20 30 40 50 20002001200220032004200520062007200820092010201120122013201420152016201720182019202020212022202320242025 Domestic debt service (average) External debt service (average) Sources: Original calculations based on the Wor

[c:p0084:001] (page 84)
nd advance broader development objectives. Financing these needs depends on mobilizing domestic resources, attracting domestic and foreign private capital, and, where necessary, borrowing through public channels. In this context, part of the increase in public debt reflects efforts to finance infrastructure, human capital, and other investments that can support long-term growth. However, slower global growth, policy uncertainty, trade fragmentation, geopolitical tensions, and commodity-price volatility have affected both the availability and cost of financing. In many countries, shocks that initially generated temporary financing needs have contributed to persistently higher debt stocks, debt service burdens, and rollover requirements. The Impact of Higher Debt on Fiscal Space and Financin

[c:p0075:000] (page 75)
Implications External Debt, External Shocks, and Vulnerability in LMICs Low- and middle-income countries (LMICs) are facing historically high global uncertainty at a time when external debt stocks have reached historic highs, debt service pressures remain elevated, fiscal space is limited in many countries, and global bond yields continue to rise, tightening financial conditions. This combination matters because external shocks can be more difficult to absorb when governments already face substantial financing needs and limited room to respond. The key vulnerability therefore lies not in exposure to global shocks alone but in how those shocks interact with already-high debt burdens. Adverse developments in trade, commodity markets, growth, exchange rates, and tighter global financing condi
```

</details>

---

## q18 — có đáp án

**Câu hỏi:** In the food import analysis, what external-debt-to-exports threshold is used as a reference point, and where does it come from?

**Đáp án mong đợi:** External debt stocks of at least 150 percent of exports, based on the threshold applied under the Heavily Indebted Poor Countries (HIPC) Initiative.

**Evidence gold:** trang 96: "external debt stocks are at least 150 percent of exports, as a reference point based on the threshold applied under the Heavily Indebted Poor Countries (HIPC) Initiative"

**Key facts:** ['150 percent of exports', 'Heavily Indebted Poor Countries']

### q18#1 — Hệ thống 1

- Trạng thái: **answered** (answer); số lượt tìm: 1
- Truy vấn: `food import analysis external-debt-to-exports threshold reference point`

**Câu trả lời trả về:** In the food import analysis, the external-debt-to-exports threshold used as a reference point is at least 150 percent. This threshold is based on the criteria applied under the Heavily Indebted Poor Countries (HIPC) Initiative [c:p0096:003].

**Citation 1:** `c:p0096:003`

> int based on the threshold applied under the Heavily Indebted Poor Countries (HIPC) Initiative,6 and where net imports account for at least 30 percent of domestic supply in a given food group. The figure intends to identify the coexistence of these two sources of vulnerability, rather than to assess whether higher external debt is associated with greater reliance on food imports. This overlap is most common for oils and fats: 34 economies—about 42 percent of net importers in the group—meet both thresholds. The corresponding shares are about 28 percent for legumes, nuts, and seeds; 27 percent for starchy staples; 23 percent for animal-source foods; 16 percent for vegetables; and 15 percent for fruits.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0095:003] (page 95)
especially in lower-income countries (FAO and World Bank 2018). Previous analysis in International Debt Report 2025 showed that higher external debt burdens were associated with higher levels of unaffordability of healthy diets across countries (World Bank 2025). This section extends that analysis by examining food import exposure as one important source of vulnerability to external shocks, including the importance of food in merchandise imports, reliance on imported supply across food groups, and the diversification of import sources. It also examines associations between external debt burdens and changes

[c:p0096:003] (page 96)
int based on the threshold applied under the Heavily Indebted Poor Countries (HIPC) Initiative,6 and where net imports account for at least 30 percent of domestic supply in a given food group. The figure intends to identify the coexistence of these two sources of vulnerability, rather than to assess whether higher external debt is associated with greater reliance on food imports. This overlap is most common for oils and fats: 34 economies—about 42 percent of net importers in the group—meet both thresholds. The corresponding shares are about 28 percent for legumes, nuts, and seeds; 27 percent for starchy staples; 23 percent for animal-source foods; 16 percent for vegetables; and 15 percent for fruits.

[c:p0096:002] (page 96)
th et al. 2025). Among net importing economies, median reliance is highest for oils and fats, at 63.6 percent, followed by starchy staples, at 36.9 percent, and legumes, nuts, and seeds, at 34.1 percent. Median reliance is lower for animal-source foods, at 28.0 percent, and for vegetables and fruits, at 17.4 percent and 13.4 percent, respectively. To identify economies where high reliance on food imports and elevated external debt burdens overlap, figure 2.13 applies two reference thresholds. For many economies, high import reliance coincides with elevated external debt burdens. Figure 2.14 highlights economies where external debt stocks are at least 150 percent of exports, as a reference point based on the threshold applied under the Heavily Indebted Poor Countries (HIPC) Initiative,6 and
```

</details>

### q18#2 — Hệ thống 2

- Trạng thái: **answered** (answer); số lượt tìm: 1
- Truy vấn: `food import analysis external-debt-to-exports threshold reference point`

**Câu trả lời trả về:** In the food import analysis, the external-debt-to-exports threshold used as a reference point is 150 percent. This threshold is based on the criteria applied under the Heavily Indebted Poor Countries (HIPC) Initiative. The analysis aims to identify economies where high reliance on food imports coincides with elevated external debt burdens, specifically where net imports account for at least 30 percent of domestic supply in a given food group [c:p0096:003].

**Citation 1:** `c:p0096:003`

> To identify economies where high reliance on food imports and elevated external debt burdens overlap, figure 2.13 applies two reference thresholds. For many economies, high import reliance coincides with elevated external debt burdens. Figure 2.14 highlights economies where external debt stocks are at least 150 percent of exports, as a reference point based on the threshold applied under the Heavily Indebted Poor Countries (HIPC) Initiative,6 and where net imports account for at least 30 percent of domestic supply in a given food group. The figure intends to identify the coexistence of these two sources of vulnerability, rather than to assess whether higher external debt is associated with greater reliance on food imports.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0096:003] (page 96)
To identify economies where high reliance on food imports and elevated external debt burdens overlap, figure 2.13 applies two reference thresholds. For many economies, high import reliance coincides with elevated external debt burdens. Figure 2.14 highlights economies where external debt stocks are at least 150 percent of exports, as a reference point based on the threshold applied under the Heavily Indebted Poor Countries (HIPC) Initiative,6 and where net imports account for at least 30 percent of domestic supply in a given food group. The figure intends to identify the coexistence of these two sources of vulnerability, rather than to assess whether higher external debt is associated with greater reliance on food imports.

[c:p0095:004] (page 95)
Previous analysis in International Debt Report 2025 showed that higher external debt burdens were associated with higher levels of unaffordability of healthy diets across countries (World Bank 2025). This section extends that analysis by examining food import exposure as one important source of vulnerability to external shocks, including the importance of food in merchandise imports, reliance on imported supply across food groups, and the diversification of import sources. It also examines associations between external debt burdens and changes

[c:p0097:000] (page 97)
Figure 2.13 Food Import Exposure, Income, and External Debt Burdens, 2025 a. Food-import share and income level b. Food-import share and debt burden Food imports (% of merchandise imports) Food imports (% of merchandise imports) 50 40 30 20 10 0 50 40 30 20 10 0 103,000 10,000 GNI per capita, 2025 (log scale)

External debt stocks
(% of exports, log scale)

30,000 100,000 20 50 100 200 400 700
Population, 2025 5 million 25 million 100 million 500 million 1,000 million Sources: Original calculations based on data from the World Bank Group International Debt Statistics and World Development Indicators databases.
```

</details>

---

## q19 — có đáp án

**Câu hỏi:** In 2020, how many IDA-eligible countries published fully accessible public debt data according to the Debt Reporting Heat Map?

**Đáp án mong đợi:** 36 countries, 47 percent of the 76 countries covered.

**Evidence gold:** trang 109: "In 2020, only 36 IDA-eligible countries, 47 percent of the 76 countries covered by the heat map, published fully accessible public debt data."

**Key facts:** ['only 36 IDA-eligible countries', '47 percent of the 76 countries']

### q19#1 — Hệ thống 1

- Trạng thái: **answered** (answer); số lượt tìm: 1
- Truy vấn: `In 2020, how many IDA-eligible countries published fully accessible public debt data according to the Debt Reporting Heat Map?`

**Câu trả lời trả về:** In 2020, 36 IDA-eligible countries, which is 47 percent of the 76 countries covered by the Debt Reporting Heat Map, published fully accessible public debt data. This represents a significant improvement in public debt disclosure practices among IDA-eligible borrowers over the years [c:p0109:002].

**Citation 1:** `c:p0109:002`

> In 2020, only 36 IDA-eligible countries, 47 percent of the 76 countries covered by the heat map, published fully accessible public debt data. The 2025 heat map found that 54 countries, or 72 percent, had fully accessible public debt data, a 25-percentage-point gain from 2020 (figure 3.1). Data accessibility in Sub-Saharan African countries has also improved significantly, rising from 19 countries (50 percent of countries in the region) that published fully accessible data in 2020, to 29 countries (or 76 percent) in 2025 despite a regression in accessibility of data in some countries.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0109:002] (page 109)
In 2020, only 36 IDA-eligible countries, 47 percent of the 76 countries covered by the heat map, published fully accessible public debt data. The 2025 heat map found that 54 countries, or 72 percent, had fully accessible public debt data, a 25-percentage-point gain from 2020 (figure 3.1). Data accessibility in Sub-Saharan African countries has also improved significantly, rising from 19 countries (50 percent of countries in the region) that published fully accessible data in 2020, to 29 countries (or 76 percent) in 2025 despite a regression in accessibility of data in some countries.

[c:p0110:000] (page 110)
Figure 3.1 Public Debt Disclosures by IDA-Eligible Countries, Accessibility and Coverage, 2020 and 2025 0 10 20 30 40 50 60 2020 2025 2020 2025 Accessibility Coverage All IDA-eligible countries Sub-Saharan Africa Other regions Source: World Bank Debt Reporting Heat Map, 2020 and 2025.

Note: IDA = International Development Association.

[c:p0109:001] (page 109)
The World Bank Group tracks progress in borrowing countries’ public debt dissemination practices on an annual basis. Its assessment of these outcomes is presented in a heat map that measures the strengths and weaknesses of the dissemination practices in 76 IDA-eligible countries across nine key indicators: data accessibility, instrument coverage, sectoral coverage, information on recently contracted external loans, periodicity, time lag, debt management strategy, annual borrowing plan, and additional statistics and memo items.2 The Debt Reporting Heat Map shows that, over the past five years, IDA-eligible borrowers have made significant progress in public debt disclosure practices.
```

</details>

### q19#2 — Hệ thống 2

- Trạng thái: **abstain** (invalid_or_missing_citations); số lượt tìm: 1
- Truy vấn: `In 2020, how many IDA-eligible countries published fully accessible public debt data according to the Debt Reporting Heat Map?`

**Câu trả lời trả về:** Không đủ bằng chứng để trả lời.

<details><summary>Bản nháp model viết nhưng bị loại do citation không hợp lệ (không tính là câu trả lời)</summary>

In 2020, 36 IDA-eligible countries, which is 47 percent of the 76 countries covered by the Debt Reporting Heat Map, published fully accessible public debt data. This represents a significant progress in public debt disclosure practices among these countries.

citations khai báo: ['c:p0109:002']

</details>

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0109:002] (page 109)
wers have made significant progress in public debt disclosure practices. In 2020, only 36 IDA-eligible countries, 47 percent of the 76 countries covered by the heat map, published fully accessible public debt data. The 2025 heat map found that 54 countries, or 72 percent, had fully accessible public debt data, a 25-percentage-point gain from 2020 (figure 3.1). Data accessibility in Sub-Saharan African countries has also improved significantly, rising from 19 countries (50 percent of countries in the region) that published fully accessible data in 2020, to 29 countries (or 76 percent) in 2025 despite a regression in accessibility of data in some countries. These countries include Ethiopia, where data accessibility had deteriorated since it defaulted on its international bond in 2023, and Se

[c:p0110:000] (page 110)
Figure 3.1 Public Debt Disclosures by IDA-Eligible Countries, Accessibility and Coverage, 2020 and 2025 0 10 20 30 40 50 60 2020 2025 2020 2025 Accessibility Coverage All IDA-eligible countries Sub-Saharan Africa Other regions Source: World Bank Debt Reporting Heat Map, 2020 and 2025. Note: IDA = International Development Association. Improvements in data accessibility identified by the heat map are mirrored in enhanced timeliness and accuracy of reporting to the World Bank Group DRS. This is a mandatory reporting requirement for all countries that borrow from the International Bank for Reconstruction and Development (IBRD) and IDA. Borrowers are increasingly meeting this requirement in accordance with the reporting timetable and are providing more comprehensive information on borrowing by

[c:p0109:001] (page 109)
ound debt management of total public debt liabilities is more critical than ever. The World Bank Group tracks progress in borrowing countries’ public debt dissemination practices on an annual basis. Its assessment of these outcomes is presented in a heat map that measures the strengths and weaknesses of the dissemination practices in 76 IDA-eligible countries across nine key indicators: data accessibility, instrument coverage, sectoral coverage, information on recently contracted external loans, periodicity, time lag, debt management strategy, annual borrowing plan, and additional statistics and memo items.2 The Debt Reporting Heat Map shows that, over the past five years, IDA-eligible borrowers have made significant progress in public debt disclosure practices. In 2020, only 36 IDA-eligib
```

</details>

---

## q20 — có đáp án

**Câu hỏi:** What rules govern how the World Bank handles loan data supplied by lenders for reconciliation?

**Đáp án mong đợi:** A July 2026 protocol by the Chief Statistician sets out the terms on which creditor data are shared and the confidentiality rules, assuring creditors the data are used strictly for reconciliation.

**Evidence gold:** trang 119: "It sets out the terms on which these data are shared and the confidentiality rules that apply to them, providing reassurance for creditors that the data will be used strictly for purposes of data reconciliation."

**Key facts:** ['confidentiality rules that apply', 'strictly for purposes of data reconciliation']

### q20#1 — Hệ thống 1

- Trạng thái: **answered** (answer); số lượt tìm: 1
- Truy vấn: `rules govern how the World Bank handles loan data supplied by lenders for reconciliation`

**Câu trả lời trả về:** The World Bank handles loan data supplied by lenders for reconciliation under specific rules outlined in the "Protocol on the Handling of Creditor Data Submitted to the World Bank Debtor Reporting System," published in July 2026. This protocol establishes the terms for data sharing and confidentiality rules, ensuring that the data will be used strictly for reconciliation purposes. This approach aims to reassure creditors about the handling of their detailed information, which is crucial for the reconciliation exercise. The World Bank is also working to broaden participation in this process beyond the current G-7 and Paris Club bilateral creditors, with ongoing discussions to include additional bilateral creditors in future reconciliation exercises [c:p0119:001].

**Citation 1:** `c:p0119:001`

> tion of standardized reporting norms to sustain concordance between debtor and creditor data. Efforts are already under way to broaden participation beyond the current group of G-7 and Paris Club bilateral creditors. Ongoing discussions with key Group of Twenty creditors are positive, and the expectation is that additional bilateral creditors will participate in the next end-2025 data reconciliation exercise. In this context, an important development is the publication in July 2026 by the World Bank Group Chief Statistician of the “Protocol on the Handling of Creditor Data Submitted to the World Bank Debtor Reporting System” (Chief Statistician 2026). It sets out the terms on which these data are shared and the confidentiality rules that apply to them, providing reassurance for creditors t

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0119:002] (page 119)
a are shared and the confidentiality rules that apply to them, providing reassurance for creditors that the data will be used strictly for purposes of data reconciliation. This has been an important factor in the creditors’ decision to share the very detailed information required for the reconciliation exercise. Over time, the plan is to extend participation to all official creditors, both bilateral and multilateral, and to encourage private creditors to participate. The World Bank Group is actively engaged in devising mechanisms to streamline and automate the reconciliation process (refer to box 3.1 on the Indonesia Loan Clearing Module Pilot Project). There is also a proposal to integrate a creditor reporting module into the DRS cloud-based platform to enable creditors to submit data ele

[c:p0119:001] (page 119)
tion of standardized reporting norms to sustain concordance between debtor and creditor data. Efforts are already under way to broaden participation beyond the current group of G-7 and Paris Club bilateral creditors. Ongoing discussions with key Group of Twenty creditors are positive, and the expectation is that additional bilateral creditors will participate in the next end-2025 data reconciliation exercise. In this context, an important development is the publication in July 2026 by the World Bank Group Chief Statistician of the “Protocol on the Handling of Creditor Data Submitted to the World Bank Debtor Reporting System” (Chief Statistician 2026). It sets out the terms on which these data are shared and the confidentiality rules that apply to them, providing reassurance for creditors t

[c:p0107:003] (page 107)
to the World Bank Group Debtor Reporting System (DRS) with data made available by bilateral creditors. Consequently, asymmetries between the two data sets have
```

</details>

### q20#2 — Hệ thống 2

- Trạng thái: **answered** (answer); số lượt tìm: 1
- Truy vấn: `rules govern how the World Bank handles loan data supplied by lenders for reconciliation`

**Câu trả lời trả về:** The World Bank handles loan data supplied by lenders for reconciliation under specific rules outlined in the "Protocol on the Handling of Creditor Data Submitted to the World Bank Debtor Reporting System," published in July 2026. This protocol establishes the terms for data sharing and confidentiality rules, ensuring that the data is used strictly for reconciliation purposes. Additionally, the World Bank is evaluating new standards and protocols for debt data reconciliation, supported by technology solutions to improve data quality and efficiency. A pilot project in Indonesia has demonstrated the feasibility of continuous synchronization and validation of debtor and creditor data, facilitating better information sharing between creditors and local debt management offices. As of May 2026, this platform had successfully exchanged and validated 761 loan records, indicating progress in the reconciliation process ([c:p0119:001], [c:p0120:000], [c:p0120:002]).

**Citation 1:** `c:p0119:001`

> Efforts are already under way to broaden participation beyond the
current group of G-7 and Paris Club bilateral creditors. Ongoing discussions with key Group of Twenty creditors are positive, and the expectation is that additional bilateral creditors will participate in the next end-2025 data reconciliation exercise. In this context, an important development is the publication in July 2026 by the World Bank Group Chief Statistician of the “Protocol on the Handling of Creditor Data Submitted to the World Bank Debtor Reporting System” (Chief Statistician 2026). It sets out the terms on which these data are shared and the confidentiality rules that apply to them, providing reassurance for creditors that the data will be used strictly for purposes of data reconciliation.

**Citation 2:** `c:p0120:000`

> Box 3.1 The Indonesia Loan Clearing Module Pilot Project
New standards and protocols for debt data reconciliation supported by innovative information technology solutions to systematically digitalize and automatically reconcile public loan data have the potential to ensure better quality recording and save time and effort. The World Bank Group is already evaluating such standards and protocols. In 2025, it launched a pilot project in Indonesia, funded by the Japanese Ministry of Finance, to develop a Loan Clearing Module to facilitate information sharing between borrowers and official creditors. This module acts as a platform for information sharing between creditors’ data systems and those of local debt management offices.

**Citation 3:** `c:p0120:002`

> Implementation of the pilot project in Indonesia has already demonstrated the technical feasibility of continuous synchronization and validation of debtor and creditor data. The debt office has already automatically transferred World Bank Group loan data and uploaded them into the local debt system; as of May 2026, the platform had successfully exchanged and validated a total of 761 loan records, and 642 subefforts are under way to cover other official creditors. Once fully operational, the Loan Clearing Module codes could be made available to other countries, potentially serving as an international platform for debt data reconciliation, providing a new, real-time source of fully validated debt statistics.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0120:000] (page 120)
Box 3.1 The Indonesia Loan Clearing Module Pilot Project
New standards and protocols for debt data reconciliation supported by innovative information technology solutions to systematically digitalize and automatically reconcile public loan data have the potential to ensure better quality recording and save time and effort. The World Bank Group is already evaluating such standards and protocols. In 2025, it launched a pilot project in Indonesia, funded by the Japanese Ministry of Finance, to develop a Loan Clearing Module to facilitate information sharing between borrowers and official creditors. This module acts as a platform for information sharing between creditors’ data systems and those of local debt management offices.

[c:p0119:001] (page 119)
Efforts are already under way to broaden participation beyond the
current group of G-7 and Paris Club bilateral creditors. Ongoing discussions with key Group of Twenty creditors are positive, and the expectation is that additional bilateral creditors will participate in the next end-2025 data reconciliation exercise. In this context, an important development is the publication in July 2026 by the World Bank Group Chief Statistician of the “Protocol on the Handling of Creditor Data Submitted to the World Bank Debtor Reporting System” (Chief Statistician 2026). It sets out the terms on which these data are shared and the confidentiality rules that apply to them, providing reassurance for creditors that the data will be used strictly for purposes of data reconciliation.

[c:p0120:002] (page 120)
Implementation of the pilot project in Indonesia has already demonstrated the technical feasibility of continuous synchronization and validation of debtor and creditor data. The debt office has already automatically transferred World Bank Group loan data and uploaded them into the local debt system; as of May 2026, the platform had successfully exchanged and validated a total of 761 loan records, and 642 subefforts are under way to cover other official creditors. Once fully operational, the Loan Clearing Module codes could be made available to other countries, potentially serving as an international platform for debt data reconciliation, providing a new, real-time source of fully validated debt statistics.
```

</details>

---

## s01 — có đáp án

**Câu hỏi:** What share of the long-term component of LMICs' net debt inflows in 2025 came from private creditors?

**Đáp án mong đợi:** 75.2 percent.

**Evidence gold:** trang 40: "these creditors accounted for 75.2 percent of the total long-term component"

**Key facts:** ['75.2 percent of the total long-term component']

### s01#1 — Hệ thống 1

- Trạng thái: **answered** (answer); số lượt tìm: 1
- Truy vấn: `share of the long-term component of LMICs' net debt inflows in 2025 from private creditors`

**Câu trả lời trả về:** In 2025, private creditors accounted for 75.2 percent of the total long-term component of LMICs' net debt inflows, which amounted to $251.1 billion. When excluding China, this share increased to 80.8 percent, with net debt inflows from private creditors reaching $358.3 billion, reflecting a significant increase in lending volume from both bondholders and commercial banks [c:p0040:000][c:p0041:000].

**Citation 1:** `c:p0040:000`

> Trends in External Debt Flows, 2015–25
Net debt inflows (disbursements minus principal repayments) to LMICs grew for a third consecutive year, more than doubling in 2025 to $423.5 billion. From a maturity standpoint, short-term net debt inflows recorded a more than fivefold increase in 2025, to $89.4 billion, and long-term net debt inflows doubled, to $334.1 billion, approximately 78.9 percent of the total volume of net inflows. This increase in long-term net debt inflows was due to the return to lending to LMICs by private creditors in 2025; these creditors accounted for 75.2 percent of the total long-term component and increased their lending volume by 180.5 percent to $251.1 billion.

**Citation 2:** `c:p0041:000`

> When China, which has recorded four consecutive years of net debt outflows, is excluded, LMICs’ net debt inflows increased to a record $527.6 billion in 2025 (figure 1.4). The yearly increase is more than twice the 2024 total volume and is due to record-high net debt inflows from private creditors, which accounted for 80.8 percent of long-term inflows. This group of countries’ net debt inflows from private creditors more than tripled in 2025, to $358.3 billion, with lending from both bondholders and commercial banks recording nearly threefold increases of $177.0 billion and $181.4 billion, respectively. PNG and PPG sector borrowers held an equal share of the volume of these inflows, but obligations to bondholders and commercial banks differed.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0040:000] (page 40)
Trends in External Debt Flows, 2015–25
Net debt inflows (disbursements minus principal repayments) to LMICs grew for a third consecutive year, more than doubling in 2025 to $423.5 billion. From a maturity standpoint, short-term net debt inflows recorded a more than fivefold increase in 2025, to $89.4 billion, and long-term net debt inflows doubled, to $334.1 billion, approximately 78.9 percent of the total volume of net inflows. This increase in long-term net debt inflows was due to the return to lending to LMICs by private creditors in 2025; these creditors accounted for 75.2 percent of the total long-term component and increased their lending volume by 180.5 percent to $251.1 billion.

[c:p0041:000] (page 41)
When China, which has recorded four consecutive years of net debt outflows, is excluded, LMICs’ net debt inflows increased to a record $527.6 billion in 2025 (figure 1.4). The yearly increase is more than twice the 2024 total volume and is due to record-high net debt inflows from private creditors, which accounted for 80.8 percent of long-term inflows. This group of countries’ net debt inflows from private creditors more than tripled in 2025, to $358.3 billion, with lending from both bondholders and commercial banks recording nearly threefold increases of $177.0 billion and $181.4 billion, respectively. PNG and PPG sector borrowers held an equal share of the volume of these inflows, but obligations to bondholders and commercial banks differed.

[c:p0044:002] (page 44)
Net debt flows from official creditors to LMICs increased 7.7 percent to $83.0 billion in 2025, after an 18.2 percent decrease in 2024. As financing from the aftermath of the COVID-19 pandemic has continued to taper off, official creditors’ share of total long-term debt inflows decreased from 46.2 percent in 2024 to 24.8 percent in 2025. Net debt inflows from official multilateral creditors accounted for 89.4 percent of the official flows, increasing 3.8 percent to $74.1 billion in 2025. Inflows from official bilateral creditors almost doubled to $8.8 billion but accounted for a moderate 10.6 percent share of total official flows.
```

</details>

### s01#2 — Hệ thống 2

- Trạng thái: **abstain** (invalid_or_missing_citations); số lượt tìm: 1
- Truy vấn: `share of the long-term component of LMICs' net debt inflows in 2025 from private creditors`

**Câu trả lời trả về:** Không đủ bằng chứng để trả lời.

<details><summary>Bản nháp model viết nhưng bị loại do citation không hợp lệ (không tính là câu trả lời)</summary>

In 2025, private creditors accounted for 80.8 percent of the long-term component of LMICs' net debt inflows, which amounted to $358.3 billion. This represented a significant increase, with private net debt flows more than tripling compared to previous years. The total long-term net debt inflows for LMICs were $443.1 billion, indicating that private creditors played a dominant role in this segment of the debt market in 2025.

citations khai báo: ['c:p0041:000']

</details>

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0040:001] (page 40)
ate net debt flows are highly procyclical in nature, and the return of private investors has been highly correlated with LMICs’ ongoing economic growth since the COVID-19 downturn in 2020. In 2025, LMIC economies, as measured by their GNI, grew 5.1 percent, to a cumulative $40.2 trillion. In 2025, net debt inflows from private creditors were nearly evenly divided between bond issuance and lending by commercial banks, at $130.4 billion and $120.7 billion, respectively. Net debt inflows from banks and other private creditors, which had retrenched 71.3 percent to $17.6 billion in 2024, saw the biggest increase, reaching volumes not seen since 2018. Although public sector borrowing from these creditors recorded a 19.4 percent decrease to $34.2 billion in 2025, the return was mostly attributed

[c:p0040:000] (page 40)
Trends in External Debt Flows, 2015–25 Net debt inflows (disbursements minus principal repayments) to LMICs grew for a third consecutive year, more than doubling in 2025 to $423.5 billion. From a maturity standpoint, short-term net debt inflows recorded a more than fivefold increase in 2025, to $89.4 billion, and long-term net debt inflows doubled, to $334.1 billion, approximately 78.9 percent of the total volume of net inflows. This increase in long-term net debt inflows was due to the return to lending to LMICs by private creditors in 2025; these creditors accounted for 75.2 percent of the total long-term component and increased their lending volume by 180.5 percent to $251.1 billion. Private net debt flows are highly procyclical in nature, and the return of private investors has been hi

[c:p0041:000] (page 41)
When China, which has recorded four consecutive years of net debt outflows, is excluded, LMICs’ net debt inflows increased to a record $527.6 billion in 2025 (figure 1.4). The yearly increase is more than twice the 2024 total volume and is due to record-high net debt inflows from private creditors, which accounted for 80.8 percent of long-term inflows. This group of countries’ net debt inflows from private creditors more than tripled in 2025, to $358.3 billion, with lending from both bondholders and commercial banks recording nearly threefold increases of $177.0 billion and $181.4 billion, respectively. PNG and PPG sector borrowers held an equal share of the volume of these inflows, but obligations to bondholders and commercial banks differed. Net debt inflows to public sector entities fro
```

</details>

---

## s02 — có đáp án

**Câu hỏi:** Among net importing economies, for which food group is median net import reliance highest, and what is the value?

**Đáp án mong đợi:** Oils and fats, at 63.6 percent.

**Evidence gold:** trang 96: "median reliance is highest for oils and fats, at 63.6 percent"

**Key facts:** ['oils and fats, at 63.6 percent']

### s02#1 — Hệ thống 1

- Trạng thái: **answered** (answer); số lượt tìm: 1
- Truy vấn: `Among net importing economies, for which food group is median net import reliance highest, and what is the value?`

**Câu trả lời trả về:** Among net importing economies, the food group with the highest median net import reliance is oils and fats, with a value of 63.6 percent [c:p0096:002].

**Citation 1:** `c:p0096:002`

> th et al. 2025). Among net importing economies, median reliance is highest for oils and fats, at 63.6 percent, followed by starchy staples, at 36.9 percent, and legumes, nuts, and seeds, at 34.1 percent. Median reliance is lower for animal-source foods, at 28.0 percent, and for vegetables and fruits, at 17.4 percent and 13.4 percent, respectively. To identify economies where high reliance on food imports and elevated external debt burdens overlap, figure 2.13 applies two reference thresholds. For many economies, high import reliance coincides with elevated external debt burdens. Figure 2.14 highlights economies where external debt stocks are at least 150 percent of exports, as a reference point based on the threshold applied under the Heavily Indebted Poor Countries (HIPC) Initiative,6 and

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0096:002] (page 96)
th et al. 2025). Among net importing economies, median reliance is highest for oils and fats, at 63.6 percent, followed by starchy staples, at 36.9 percent, and legumes, nuts, and seeds, at 34.1 percent. Median reliance is lower for animal-source foods, at 28.0 percent, and for vegetables and fruits, at 17.4 percent and 13.4 percent, respectively. To identify economies where high reliance on food imports and elevated external debt burdens overlap, figure 2.13 applies two reference thresholds. For many economies, high import reliance coincides with elevated external debt burdens. Figure 2.14 highlights economies where external debt stocks are at least 150 percent of exports, as a reference point based on the threshold applied under the Heavily Indebted Poor Countries (HIPC) Initiative,6 and

[c:p0099:001] (page 99)
ludes only economy-food-group observations with positive net import reliance; it does not show observations with zero net import reliance or net exporters. Net import reliance is calculated as net imports (imports minus exports) relative to domestic supply quantity after aggregating commodities within each Healthy Diet Basket food group. Values may exceed 100 percent because of stock changes or timing and measurement differences between trade and supply data. Panels include 87, 80, 64, 84, 55, and 73 economies, respectively. Two observations with net import reliance above 150 percent are omitted from the display. External debt data refer to 2025 for 101 economies and to 2024 for Algeria and Guinea, for which 2025 data are unavailable. Colors identify the income classification of highlighte

[c:p0099:000] (page 99)
Share of exports (%) 100 200 300 400 500 700 600 800 Share of exports (%) 100 200 300 400 500 700 600 800 Net import reliance (%) 150 125 100 75 50 25 0 Net import reliance (%) 150 125 100 75 50 25 0 e. Fruits f. Vegetables MNG GMB MNE SUR BTN MNGPRY COMSTP CPV VCT SLV CIV CPV KAZ MNE SLV GMB FJ I KGZ Low income Lower-middle income Upper-middle incomeIncome group Population, 2025 5 million 25 million 100 million 500 million 1,000 million Sources: Original calculations based on data from the World Bank Group’s International Debt Statistics and World Development Indicators databases, and from the Food and Agriculture Organization of the United Nations’ Food Balance Sheets. Note: The figure includes only economy-food-group observations with positive net import reliance; it does not show obser
```

</details>

### s02#2 — Hệ thống 2

- Trạng thái: **answered** (answer); số lượt tìm: 1
- Truy vấn: `Among net importing economies, for which food group is median net import reliance highest, and what is the value?`

**Câu trả lời trả về:** Among net importing economies, the food group with the highest median net import reliance is oils and fats, with a value of 63.6 percent [c:p0096:002].

**Citation 1:** `c:p0096:002`

> Among net importing economies, median reliance is highest for oils and fats, at 63.6 percent, followed by starchy staples, at 36.9 percent, and legumes, nuts, and seeds, at 34.1 percent. Median reliance is lower for animal-source foods, at 28.0 percent, and for vegetables and fruits, at 17.4 percent and 13.4 percent, respectively.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0096:002] (page 96)
Among net importing economies, median reliance is highest for oils and fats, at 63.6 percent, followed by starchy staples, at 36.9 percent, and legumes, nuts, and seeds, at 34.1 percent. Median reliance is lower for animal-source foods, at 28.0 percent, and for vegetables and fruits, at 17.4 percent and 13.4 percent, respectively.

[c:p0099:001] (page 99)
Note: The figure includes only economy-food-group observations with positive net import reliance; it does not show observations with zero net import reliance or net exporters. Net import reliance is calculated as net imports (imports minus exports) relative to domestic supply quantity after aggregating commodities within each Healthy Diet Basket food group. Values may exceed 100 percent because of stock changes or timing and measurement differences between trade and supply data. Panels include 87, 80, 64, 84, 55, and 73 economies, respectively. Two observations with net import reliance above 150 percent are omitted from the display. External debt data refer to 2025 for 101 economies and to 2024 for Algeria and Guinea, for which 2025 data are unavailable.

[c:p0098:000] (page 98)
Figure 2.14 Net Importing Economies and External Debt Burdens, by Food Group, Income Group, and Population, 2025 Share of exports (%)

100 200 300 400 500 700 600 800
Net import reliance (%)

150 CPV MNE VCT TUN COM BTN YEM LBN GNB COLSLVSTP MNG SENVUTKENECU FJ I NIC DOM HND JOR JAM GMB 125 100 75 50 25 0
Net import reliance (%)

150 125 100 75 50 25 0
Share of exports (%)

100 200 300 400 500 700 600 800 a. Starchy staples b. Oils and fats
Share of exports (%)

100 200 300 400 500 700 600 800
Share of exports (%)

100 200 300 400 500 700 600 800
Net import reliance (%)

150 125 100 75 50 25 0
Net import reliance (%)
```

</details>

---

## s03 — có đáp án

**Câu hỏi:** How do accrual-based and cash-basis recording of debt transactions differ?

**Đáp án mong đợi:** Accrual-based accounting recognizes transactions when obligations arise; the cash basis method records payments when they are made.

**Evidence gold:** trang 126: "some compilers adopt accrual-based accounting (recognizing transactions when obligations arise), whereas others use the cash basis method (recording payments when they are made)"

**Key facts:** ['accrual-based accounting', 'cash basis method']

### s03#1 — Hệ thống 1

- Trạng thái: **abstain** (model_abstain); số lượt tìm: 1
- Truy vấn: `How do accrual-based and cash-basis recording of debt transactions differ?`

**Câu trả lời trả về:** Không đủ bằng chứng để trả lời.

*Lý do model nêu:* The passages do not contain sufficient evidence to directly compare accrual-based and cash-basis recording of debt transactions.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0126:001] (page 126)
Asymmetries in debt data also stem from a whole range of factors, including differences in coverage, timing of recording, institutional practice, and delayed reporting by borrowers and creditors. Coverage often differs—debtor-based systems may exclude private nonguaranteed borrowing, whereas creditor-side data likely capture these flows more comprehensively. Recording practices vary: some compilers adopt accrual-based accounting (recognizing transactions when obligations arise), whereas others use the cash basis method (recording payments when they are made). These divergent practices lead to timing and value mismatches. Another common source of asymmetry is valuation, which uses different exchange rates or accounting methods.

[c:p0112:003] (page 112)
Rather, they arise from several factors including differences in definitions, reporting practices, and institutional coordination. On the debtor side, these factors include (a) weak debt management, which limits timely, comprehensive recording of debt liabilities; (b) time lags in reporting new commitments and disbursements; (c) understatement of arrears, particularly penalty interest charges, often due to the complexity of how these are calculated; (d) failure to report, which results in estimated data by World Bank Group staff; and (e) misclassification of direct and guaranteed export credits.

[c:p0114:000] (page 114)
Other reasons for asymmetries between the debtor and creditor data include recording of indemnification of payment arrears to private creditors on guaranteed export credits typically captured in debtor data only when a formal debt restructuring takes place. This problem is compounded by the fact that most creditors do not publish information on loans they have guaranteed. There is also an absence of a standard methodology applicable to both debtors and creditors for recording forgiveness of bilateral claims and bilateral debt swaps that extinguish external debt obligations in return for investment of the local currency equivalent in a dedicated fund for specific expenditures such as education or measures to mitigate climate change.
```

</details>

### s03#2 — Hệ thống 2

- Trạng thái: **abstain** (model_abstain); số lượt tìm: 1
- Truy vấn: `How do accrual-based and cash-basis recording of debt transactions differ?`

**Câu trả lời trả về:** Không đủ bằng chứng để trả lời.

*Lý do model nêu:* The passages do not contain sufficient evidence to directly compare accrual-based and cash-basis recording of debt transactions.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0126:001] (page 126)
overage of the key debt databases. Asymmetries in debt data also stem from a whole range of factors, including differences in coverage, timing of recording, institutional practice, and delayed reporting by borrowers and creditors. Coverage often differs—debtor-based systems may exclude private nonguaranteed borrowing, whereas creditor-side data likely capture these flows more comprehensively. Recording practices vary: some compilers adopt accrual-based accounting (recognizing transactions when obligations arise), whereas others use the cash basis method (recording payments when they are made). These divergent practices lead to timing and value mismatches. Another common source of asymmetry is valuation, which uses different exchange rates or accounting methods. For example, compilations ba

[c:p0125:001] (page 125)
times the case, the primary challenge to the accuracy, credibility, and comparability of debt data is asymmetries, particularly between debtor- and creditor-reported figures. Addressing Debt Asymmetries Is Key to Debt Transparency Asymmetries in debt data arise primarily from inconsistent methodological definitions and accounting practices in debtor and creditor countries and other institutions that compile and disseminate debt data. These divergent practices present a minefield for users trying to compare debtor and creditor data or to make cross-country comparisons across groups of debtors or creditors. In extreme cases discrepancies as large as 30 percent of gross domestic product have been observed in debt stock figures purporting to have the same coverage. Issues as simple as classifi

[c:p0114:000] (page 114)
Other reasons for asymmetries between the debtor and creditor data include recording of indemnification of payment arrears to private creditors on guaranteed export credits typically captured in debtor data only when a formal debt restructuring takes place. This problem is compounded by the fact that most creditors do not publish information on loans they have guaranteed. There is also an absence of a standard methodology applicable to both debtors and creditors for recording forgiveness of bilateral claims and bilateral debt swaps that extinguish external debt obligations in return for investment of the local currency equivalent in a dedicated fund for specific expenditures such as education or measures to mitigate climate change. The reconciliation process has strengthened dialogue and u
```

</details>

---

## s04 — có đáp án

**Câu hỏi:** In what year was the Debtor Reporting System (DRS) initially established?

**Đáp án mong đợi:** 1951.

**Evidence gold:** trang 114: "Initially established in 1951 for institutional purposes to collect accurate and timely data on external public debt"

**Key facts:** ['established in 1951']

### s04#1 — Hệ thống 1

- Trạng thái: **answered** (answer); số lượt tìm: 2
- Truy vấn: `Debtor Reporting System (DRS) established year`; `history of Debtor Reporting System (DRS)`

**Câu trả lời trả về:** The Debtor Reporting System (DRS) was instituted in 1951, originating from the World Bank Group's need to monitor and assess the financial position of its borrowers [c:p0028:004].

**Citation 1:** `c:p0028:004`

> The primary source for these data is reports to the World Bank Group’s Debtor Reporting System (DRS) from member countries that have received either International Bank for Reconstruction and Development loans or International Development Association credits, and that have outstanding obligations to the World Bank Group. The DRS, instituted in 1951, has its origins in the World Bank Group’s need to monitor and assess the financial position of its borrowers. Comprehensive information on data sources and the methodology used to compile the statistics presented in this report can be found in the appendix under “Data Sources.” The following describes the key concepts and data sources.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0121:003] (page 121)
The modernization and expansion of the DRS serves as an important anchor for structuring the capacity-building program in debt data management. It currently covers about 120 World Bank Group borrowing countries and more than 50,000 active loan records, with approximately 2,500–3,000 new loans reported each year. Maintaining a system of this scale and ensuring the integrity of the data require sustained investment in national reporting capacity. Practical training sessions are not limited to familiarizing debt managers with the new and very different DRS reporting structure. They include equally, if not more, important training in how to implement international statistical standards to categorize and compile debt data.

[c:p0116:004] (page 116)
The development of the new DRS platform and its rollout are being coordinated with the Commonwealth Secretariat (Meridian) and the Debt Management and Financial Analysis System of UN Trade and Development (UNCTAD), which provide the debt management software currently used by about 80 percent of DRS reporting countries. The goal is a seamless extraction, validation, and automated pass-through of data recorded by the borrowers in these systems to

[c:p0116:000] (page 116)
where appropriate artificial intelligence, to streamline and simplify the reporting process, assist reporters with queries about reporting protocols, and validate the consistency of data. The new DRS framework, which will be finalized and rolled out in the coming year, represents a major step forward in strengthening the global debt data architecture.

[c:p0028:004] (page 28)
The primary source for these data is reports to the World Bank Group’s Debtor Reporting System (DRS) from member countries that have received either International Bank for Reconstruction and Development loans or International Development Association credits, and that have outstanding obligations to the World Bank Group. The DRS, instituted in 1951, has its origins in the World Bank Group’s need to monitor and assess the financial position of its borrowers. Comprehensive information on data sources and the methodology used to compile the statistics presented in this report can be found in the appendix under “Data Sources.” The following describes the key concepts and data sources.
```

</details>

### s04#2 — Hệ thống 2

- Trạng thái: **answered** (answer); số lượt tìm: 1
- Truy vấn: `Debtor Reporting System (DRS) established year`

**Câu trả lời trả về:** The Debtor Reporting System (DRS) was instituted in 1951, originating from the World Bank Group's need to monitor and assess the financial position of its borrowers.  

[c:p0028:003]

**Citation 1:** `c:p0028:003`

> ese data is reports to the World Bank Group’s Debtor Reporting System (DRS) from member countries that have received either International Bank for Reconstruction and Development loans or International Development Association credits, and that have outstanding obligations to the World Bank Group. The DRS, instituted in 1951, has its origins in the World Bank Group’s need to monitor and assess the financial position of its borrowers. Comprehensive information on data sources and the methodology used to compile the statistics presented in this report can be found in the appendix under “Data Sources.” The following describes the key concepts and data sources. • The DRS follows international standards and defines external debt as the outstanding amount of actual current liabilities in both dome

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0107:003] (page 107)
to the World Bank Group Debtor Reporting System (DRS) with data made available by bilateral creditors. Consequently, asymmetries between the two data sets have

[c:p0028:003] (page 28)
ese data is reports to the World Bank Group’s Debtor Reporting System (DRS) from member countries that have received either International Bank for Reconstruction and Development loans or International Development Association credits, and that have outstanding obligations to the World Bank Group. The DRS, instituted in 1951, has its origins in the World Bank Group’s need to monitor and assess the financial position of its borrowers. Comprehensive information on data sources and the methodology used to compile the statistics presented in this report can be found in the appendix under “Data Sources.” The following describes the key concepts and data sources. • The DRS follows international standards and defines external debt as the outstanding amount of actual current liabilities in both dome

[c:p0116:000] (page 116)
where appropriate artificial intelligence, to streamline and simplify the reporting process, assist reporters with queries about reporting protocols, and validate the consistency of data. The new DRS framework, which will be finalized and rolled out in the coming year, represents a major step forward in strengthening the global debt data architecture. The reporting framework is being expanded to introduce more comprehensive instrument-level reporting, including additional information on loan characteristics, debtor and creditor guarantees, collateral arrangements, debt reorganization, creditor attributes, and emerging financing instruments such as total return swaps, third party discounted buybacks, and asset-backed financing. The reporting requirements are designed to capture a comprehens
```

</details>

---

## u03 — THIẾU EVIDENCE (đúng là phải từ chối)

**Câu hỏi:** What does the report project the total external debt stock of low- and middle-income countries will be at the end of 2028?

**Vì sao không trả lời được:** The report analyses 2025 outcomes. Its only forward-looking statements are that IDA-eligible countries' borrowing costs are 'projected to increase' (no figure, p67) and timelines for the revised debt framework (p88-89); it gives no projected debt stock.

### u03#1 — Hệ thống 1

- Trạng thái: **abstain** (model_abstain); số lượt tìm: 3
- Truy vấn: `total external debt stock of low- and middle-income countries at the end of 2028`; `total external debt stock of low- and middle-income countries 2028 projection`; `external debt stock low- and middle-income countries 2028`

**Câu trả lời trả về:** Không đủ bằng chứng để trả lời.

*Lý do model nêu:* The passages do not contain projections for the total external debt stock of low- and middle-income countries at the end of 2028.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0028:000] (page 28)
Table 1.1 External Debt Stock of Low- and Middle-Income Countries, 2015–25 US$ (billion) 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 Debt stock 5,915.7 6,136.4 6,933.1 7,382.3 7,757.7 8.182.1 8,829.2 8,726.3 8,889.6 8,949.6 9,445.0 Long-term 4,396.6 4,661.3 5,130.5 5,372.6 5,728.8 6,140.5 6,587.9 6,481.8 6,568.3 6,618.7 7,020.9 Official creditors 1,019.3 1,077.0 1,179.0 1,250.2 1,315.3 1,483.2 1,683.8 1,717.2 1,815.5 1,839.4 1,993.3 Bilateral creditors 366.6 393.9 432.8 453.8 462.5 493.5 489.5 480.7 493.7 477.0 499.6 Multilateral creditors 652.7 683.2 746.2 796.4 852.8 989.7 1,194.3 1,236.5 1,321.8 1,362.4 1,493.7 World Bank (IBRD and IDA) 278.0 288.6 311.7 321.3 339.5 375.2 387.5 405.0 435.7 463.1 498.7 IMF (Use of credit and SDR allocations) 100.5 103.8 114.5 142.0 162.2 214.6

[c:p0035:002] (page 35)
igations is held by the PNG sector of the economy. This type of debt increased 7.0 percent to $1.9 trillion in 2025, and the debt stock of public sector entities owed to commercial banks and other private creditors saw a much larger increase of 15.1 percent, to $385.7 billion in 2025. Figure 1.2 Creditor Composition of External Debt Stock in Low- and Middle-Income Countries, 2015–25 US$ (trillion) 0 2 4 6 8 10 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 Multilateral creditors (incl. IMF) Bilateral creditors Bondholders Banks and other private creditors Short-term Source: World Bank Group International Debt Statistics database. Note: IMF = International Monetary Fund.

[c:p0030:002] (page 30)
ICs than the overall MIC figure suggests. Figure 1.1 External Debt Stocks of Low- and Middle-Income Countries, 2015–25 0 2 4 6 8 10 US$ (trillion) 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 Low- and middle-income countries China IDA-eligible countries Other low- and middle-income countries Source: World Bank Group International Debt Statistics database. Note: IDA = International Development Association.
```

</details>

### u03#2 — Hệ thống 2

- Trạng thái: **abstain** (model_abstain); số lượt tìm: 3
- Truy vấn: `total external debt stock of low- and middle-income countries at the end of 2028`; `project total external debt stock low- and middle-income countries end of 2028`; `external debt stock low- and middle-income countries projection 2028`

**Câu trả lời trả về:** Không đủ bằng chứng để trả lời.

*Lý do model nêu:* The passages do not contain projections for the total external debt stock of low- and middle-income countries at the end of 2028.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0028:000] (page 28)
Table 1.1 External Debt Stock of Low- and Middle-Income Countries, 2015–25 US$ (billion)

[c:p0027:000] (page 27)
and Debt Flows as of End-2025 Trends in External Debt, 2015–25
Renewed global inflationary pressures, geopolitical tensions, and decreased fiscal space continued to put substantial pressure on the external debt positions of low- and middle-income countries (LMICs) in 2025. LMICs’ external borrowing levels reached a record $9.4 trillion at the end of the year, increasing 5.5 percent from $8.9 trillion in 2024. LMIC external debt has grown about 60 percent over the past decade, and the 2025 increase was the largest since the easing of the COVID-19 pandemic in 2021. The change in debt stock was driven by net debt inflows of $423.5 billion, a more than twofold increase from 2024, as well as by some debt forgiveness and the upward accounting effect of US dollar depreciation.

[c:p0061:002] (page 61)
The Middle East, North Africa, Afghanistan, and Pakistan region, despite recording improvements in debt service and interest ratios, saw its external debt-to-GNI ratio rise from 26.7 percent to 29.4 percent, the largest single-year increase of any region, signaling continued debt stock accumulation.

Figure 1.17 External Debt Stock to Exports of Low-Income, Middle-Income, IDA-Eligible, and Low- and Middle-Income Countries (Excluding China), 2015–25 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 202 5 0 50 100 150 200 250 300 350 Percent Low-income countries IDA-eligible countries Middle-income countries Low- and middle-income countries (excl. China)

Source: World Bank Group International Debt Statistics database.

Note: IDA = International Development Association.

[c:p0060:003] (page 60)
Total debt service and interest payments relative to export earnings both declined Figure 1.16 Ratio of External Debt Stock to GNI of Low-Income, Middle-Income, IDA-Eligible, and Low- and Middle-Income Countries (Excluding China), 2015–25 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 0 10 20 30 40 50 60 Percent Low-income countries IDA-eligible countries Middle-income countries Low- and middle-income countries (excl. China)

Source: World Bank Group International Debt Statistics database.

Note: GNI = gross national income; IDA = International Development Association.
```

</details>

---

## u04 — THIẾU EVIDENCE (đúng là phải từ chối)

**Câu hỏi:** By how much did changes in gold prices alter the external-debt-to-exports ratios of commodity-exporting low- and middle-income countries in 2025?

**Vì sao không trả lời được:** The report discusses commodity price shocks and debt but never mentions gold.

### u04#1 — Hệ thống 1

- Trạng thái: **abstain** (model_abstain); số lượt tìm: 1
- Truy vấn: `changes in gold prices external-debt-to-exports ratios commodity-exporting low- and middle-income countries 2025`

**Câu trả lời trả về:** Không đủ bằng chứng để trả lời.

*Lý do model nêu:* The passages do not contain specific information about how changes in gold prices altered the external-debt-to-exports ratios of commodity-exporting low- and middle-income countries in 2025.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0060:002] (page 60)
ternal debt-to-exports ratio increased from 113.0 percent in 2024 to 114.9 percent in 2025 but remains approximately 15.6 percentage points below the decade average, reflecting an overall improvement since 2015, driven by export growth rather than debt reduction (figure 1.17). Total debt service and interest payments relative to export earnings both declined Figure 1.16 Ratio of External Debt Stock to GNI of Low-Income, Middle-Income, IDA-Eligible, and Low- and Middle-Income Countries (Excluding China), 2015–25 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 0 10 20 30 40 50 60 Percent Low-income countries IDA-eligible countries Middle-income countries Low- and middle-income countries (excl. China) Source: World Bank Group International Debt Statistics database. Note: GNI = gross na

[c:p0083:001] (page 83)
ce. Economies with weaker capacity need to strengthen tax revenue mobilization and improve fiscal transparency. Figure 2.6 Foreign Exchange Accumulation in Low- and Middle-Income Countries, 2026 –2 0 Percent change from a year earlier 4 2 8 6 Jan Feb Mar Apr May Jun Commodity exporters Commodity importers Commodity importers (excl. China) Sources: Original calculations based on data from Haver Analytics; International Monetary Fund; World Bank Group. Note: Figure shows year-on-year changes in foreign exchange in US dollars. Aggregates are computed as weighted averages. Sample includes up to 40 commodity exporters and 34 commodity importers.

[c:p0059:000] (page 59)
Key Debt Indicators, 2015–25 In 2025, LMICs’ external debt ratios remained mainly stable from the peak levels recorded during the COVID-19 pandemic in 2020; however, aggregate improvement was uneven, with debt stock ratios rising or holding flat while debt service and interest payment ratios declined across most borrower groups. This change in ratios reflects a combination of strong export and income growth, the completion of debt restructuring agreements in several IDA-eligible countries, and the depreciation of the US dollar, which inflated the dollar-measured value of both debt stocks and GNI simultaneously through an accounting effect, partly moderating ratio movements in both directions. Ratios of debt to national income and exports are valuable indicators of countries’ ability to ser
```

</details>

### u04#2 — Hệ thống 2

- Trạng thái: **abstain** (model_abstain); số lượt tìm: 1
- Truy vấn: `changes in gold prices external-debt-to-exports ratios commodity-exporting low- and middle-income countries 2025`

**Câu trả lời trả về:** Không đủ bằng chứng để trả lời.

*Lý do model nêu:* The passages do not contain evidence regarding the specific impact of changes in gold prices on the external-debt-to-exports ratios of commodity-exporting low- and middle-income countries in 2025.

<details><summary>Context cuối gửi cho model</summary>

```
[c:p0083:001] (page 83)
Economies with weaker capacity need to strengthen tax revenue mobilization and improve fiscal transparency.

Figure 2.6 Foreign Exchange Accumulation in Low- and Middle-Income Countries, 2026 –2 0 Percent change from a year earlier 4 2 8 6 Jan Feb Mar Apr May Jun Commodity exporters Commodity importers Commodity importers (excl. China) Sources: Original calculations based on data from Haver Analytics; International Monetary Fund; World Bank Group.

Note: Figure shows year-on-year changes in foreign exchange in US dollars. Aggregates are computed as weighted averages. Sample includes up to 40 commodity exporters and 34 commodity importers.

[c:p0061:002] (page 61)
The Middle East, North Africa, Afghanistan, and Pakistan region, despite recording improvements in debt service and interest ratios, saw its external debt-to-GNI ratio rise from 26.7 percent to 29.4 percent, the largest single-year increase of any region, signaling continued debt stock accumulation.

Figure 1.17 External Debt Stock to Exports of Low-Income, Middle-Income, IDA-Eligible, and Low- and Middle-Income Countries (Excluding China), 2015–25 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 202 5 0 50 100 150 200 250 300 350 Percent Low-income countries IDA-eligible countries Middle-income countries Low- and middle-income countries (excl. China)

Source: World Bank Group International Debt Statistics database.

Note: IDA = International Development Association.

[c:p0060:003] (page 60)
Total debt service and interest payments relative to export earnings both declined Figure 1.16 Ratio of External Debt Stock to GNI of Low-Income, Middle-Income, IDA-Eligible, and Low- and Middle-Income Countries (Excluding China), 2015–25 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 0 10 20 30 40 50 60 Percent Low-income countries IDA-eligible countries Middle-income countries Low- and middle-income countries (excl. China)

Source: World Bank Group International Debt Statistics database.

Note: GNI = gross national income; IDA = International Development Association.
```

</details>
