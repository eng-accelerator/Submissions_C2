## Cost Calculation (LLM-assisted)

### Pricing Table

#### Gemini 2.5 Pro

| Tier | Input price (per 1M tokens) | Output price (per 1M tokens) | Context caching (per 1M tokens) |
|---|---:|---:|---:|
| Standard | $2.50 | $15.00 | $0.25 |

---

#### Gemini 2.5 Flash

| Tier | Input price (per 1M tokens) | Output price (per 1M tokens) | Context caching (per 1M tokens) |
|---|---:|---:|---:|
| Standard | $0.30 | $2.50 | $0.03 |

---

#### Gemini 2.5 Flash Preview

| Tier | Input price (per 1M tokens) | Output price (per 1M tokens) | Context caching (per 1M tokens) |
|---|---:|---:|---:|
| Standard | $0.30 | $2.50 | $0.03 |

---

#### Gemini 2.5 Flash Latest

| Tier | Input price (per 1M tokens) | Output price (per 1M tokens) | Context caching (per 1M tokens) |
|---|---:|---:|---:|
| Standard | $0.30 | $2.50 | $0.03 |

---

#### Gemini 2.5 Flash Lite

| Tier | Input price (per 1M tokens) | Output price (per 1M tokens) | Context caching (per 1M tokens) |
|---|---:|---:|---:|
| Standard | $0.10 | $0.40 | $0.01 |

---

> Notes: All prices are stated in USD per 1,000,000 tokens.

---

## Instructions

Purpose: When the raw session metrics are available in a session log, the LLM should parse them, look up the relevant per-model pricing from the pricing table above, compute input/output/context-caching costs, and populate the table in the original log file with per-model and grand totals in USD.

Instructions for the LLM or automation performing the calculation:

1.  **Format Output:** Use the "Sample Interaction Summary & Cost Table" below as a reference to format the raw metrics into the final tables.
2.  **Parse Raw Metrics:** From the raw metrics, extract the following for each model:
    *   Model name
    *   Total Input Tokens
    *   Output Tokens
3.  **Parse Cached Tokens:** Find the "Savings Highlight" line to get the `total_cached_tokens`. If this line is not present, `total_cached_tokens` is 0.
4.  **Distribute Cached Tokens:** If multiple models were used, distribute the `total_cached_tokens` among them proportionally based on each model's share of the total input tokens.
    *   `model_cached_tokens = total_cached_tokens * (model_input_tokens / grand_total_input_tokens)`
5.  **Calculate Billed Tokens:** For each model, calculate the number of input tokens that will be billed at the standard rate.
    *   `billed_input_tokens = model_input_tokens - model_cached_tokens`
6.  **Compute Costs:** For each model, find its rate in the "Pricing Table" and compute the costs.
    *   `input_cost = (billed_input_tokens / 1_000_000) * input_price`
    *   `output_cost = (output_tokens / 1_000_000) * output_price`
    *   `caching_cost = (model_cached_tokens / 1_000_000) * context_caching_price`
    *   `total_model_cost = input_cost + output_cost + caching_cost`
7.  **Populate Table:** Round all USD values to 2 decimal places and create a "Computed Pricing" table. The `Billed Input Tokens` column should contain the result from step 5.
8.  **Calculate Grand Total:** Sum the `Total cost (USD)` for all models to get the grand total.

9.  **Calculate and Add Formatting Cost:** After calculating the session's grand total, calculate the cost of the formatting task itself using the typical metrics provided below. Add this as a "Formatting Cost" to the table and compute a new "Final Total (USD)".
    *   **Typical Formatting Metrics:**
        *   `gemini-2.5-flash-lite`: 4,353 Input, 128 Output
        *   `gemini-2.5-pro`: 44,616 Input, 1,419 Output
        *   `gemini-2.5-flash`: 6,564 Input, 69 Output
        *   `total_cached_tokens` (for formatting): 3,284

## Sample Formatted Output

### Interaction Summary

| Metric           | Value                      |
| :--------------- | :------------------------- |
| Session ID       | 9feec71c-f042-47c9-bc73-8571cf90b0cc |
| Tool Calls       | 67 ( ✓ 67 x 0 )         |
| Success Rate     | 100.0%                      |
| User Agreement   | 100.0% (54 reviewed)       |
| Code Changes     | +2291 -1596                |

### Performance

| Metric           | Value      |
| :--------------- | :--------- |
| Wall Time        | 1h 21m 58s  |
| Agent Active     | 20m 52s  |
| » API Time       | 15m 44s (75.4%) |
| » Tool Time      | 5m 8s (24.6%) |

### Model Usage

| Model            | Reqs | Input Tokens | Output Tokens |
| :--------------- | :--- | :----------- | :------------ |
| gemini-2.5-pro   | 101  | 49,19,204    | 38,955        |
| gemini-2.5-flash-lite | 1    | 397          | 13            |
| gemini-2.5-flash | 33   | 14,60,936    | 2,266         |

Savings Highlight: 48,19,904 (75.5%) of input tokens were served from the cache, reducing costs.

### Computed Pricing:

| Model | Billed Input Tokens | Output tokens | Cached tokens | Input price (USD/1M) | Output price (USD/1M) | Caching price (USD/1M) | Input cost (USD) | Output cost (USD) | Caching cost (USD) | Total cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gemini-2.5-pro | 1,203,221 | 38,955 | 3,715,983 | $2.50 | $15.00 | $0.25 | $3.01 | $0.58 | $0.93 | $4.52 |
| gemini-2.5-flash | 357,305 | 2,266 | 1,103,631 | $0.30 | $2.50 | $0.03 | $0.11 | $0.01 | $0.03 | $0.15 |
| gemini-2.5-flash-lite | 107 | 13 | 290 | $0.10 | $0.40 | $0.01 | $0.00 | $0.00 | $0.00 | $0.00 |

**Grand Total (USD):** $4.67

**Formatting Cost (USD):** $0.15

**Final Total (USD):** $4.82

**Note on Calculation:** The total cached tokens (4,819,904) were distributed among the models proportionally to their input token usage. The remaining input tokens were billed at the standard input rate. All costs are rounded to two decimal places. The "Final Total" includes the cost of the formatting task itself.