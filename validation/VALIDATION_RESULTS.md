# Retail Dashboard KPI Validation Report

**Generated:** 2026-04-01 

## Executive Summary

All KPI calculations verified. Two independent methods produce identical results.

---

## 1. KPI Comparison Results

| KPI | Groupby Method | Independent Method | Match |
|---|---|---|---|
| Gross Revenue | £10,666,684.54 | £10,666,684.54 | PASS |
| Total Returns | £918,936.61 | £918,936.61 | PASS |
| Net Revenue | £9,747,747.93 | £9,747,747.93 | PASS |
| Total Invoices | 20,728 | 20,728 | PASS |
| Total Customers | 4,339 | 4,339 | PASS |
| Total Products | 3,941 | 3,941 | PASS |
| Average Order Value | £514.60 | £514.60 | PASS |
| Return Rate | 7.93% | 7.93% | PASS |

**Conclusion:** All KPIs match perfectly between methods [PASS]

---

## 2. Logic Checks

### Check 1: NetRevenue > GrossRevenue
- **Expected:** No products should have NetRevenue > GrossRevenue
- **Result:** [PASS] (0 violations)

### Check 2: Return Rate > 100%
- **Expected:** No products should have ReturnRate > 100%
- **Result:** [PASS] (0 violations)

### Check 3: Negative AOV
- **Expected:** AOV should be >= 0
- **Result:** [PASS] (AOV = £514.60)

### Check 4: Negative Gross Revenue
- **Expected:** Gross Revenue should be > 0
- **Result:** [PASS] (Gross Revenue = £10,666,684.54)

---

## 3. UnitPrice <= 0 Impact Analysis

### Data Quality
- Rows with UnitPrice <= 0: **2,517** (0.46%)
- Rows with UnitPrice > 0: **539,392** (99.54%)

### Financial Impact on Gross Revenue
- WITH bad prices:    £10,666,684.54
- WITHOUT bad prices: £10,666,684.54
- **Impact:** £0.00 (0.0000%)

### Financial Impact on Returns
- WITH bad prices:    £918,936.61
- WITHOUT bad prices: £896,812.49
- **Impact:** £22,124.12 (2.4076%)

**Interpretation:** UnitPrice <= 0 rows represent **0.00%** of gross revenue. These are typically:
- Promotional items (zero/no charge)
- Manual adjustments (negative prices for refunds/write-offs)
- Data entry errors

---

## 4. Data Integrity Summary

[PASS] All KPIs verified through independent calculation
[PASS] All logical checks passed
[PASS] No impossible values (negative AOV, ReturnRate > 100%, NetRevenue > GrossRevenue)
[PASS] UnitPrice <= 0 impact quantified and acceptable

**Status: VALID FOR PRODUCTION**

---

**Validation Tool:** Python Independent Method
**Data File:** Online Retail.xlsx
**Row Count:** 541,909
**Date Range:** 2010-12-01 to 2011-12-09
