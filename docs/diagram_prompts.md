# Diagram Prompts for DQ HOL Medium Article

Use these prompts with Gemini to generate the article images.

---

## dq-00-cover.png (Cover Image)

```
Create a technical diagram in a hand-drawn sketch style (Excalidraw aesthetic with slightly wobbly lines and hand-written font). White background. Dimensions: 1200x1500 portrait.

Title at top (bold, hand-written): "Stop Building Data Quality Frameworks from Scratch"
Subtitle (lighter, hand-written): "15 Snowflake Notebooks. Zero External Tools. Production-Ready."

PRIMARY VISUAL (center, ~60% of image):
A vertical flow diagram showing 4 layers stacked top to bottom, connected by hand-drawn arrows:

Layer 1 (top): "RAW" label with 4 small hand-drawn table icons in a row, colored bronze (#B45309). Labels: ERP, CRM, Gov, Bank. Small shield icons on each table indicating quality checks.

Layer 2: "SILVER" label with 2 larger hand-drawn table icons, colored silver (#6B7280). Labels: INT_CUSTOMERS, INT_TRANSACTIONS. A small "DT" badge (Dynamic Tables) on each. Hand-drawn arrows flow down from the 4 RAW tables into these 2.

Layer 3: "GOLD" label with 2 hand-drawn table icons, colored gold (#D97706). Labels: DIM_CUSTOMER, FACT_TRANSACTIONS. A small "dbt" badge on each. Hand-drawn arrows flow down from Silver.

Layer 4 (bottom): "DQ LAYER" label in Snowflake Blue (#29B5E8). Contains 5 small hand-drawn icons in a row: magnifying glass (DMFs), document (Rules Catalog), brain (Cortex AI), bell (Alerts), chart (Dashboard). Dotted hand-drawn lines connect back up to all three layers above.

SIDE ANNOTATIONS (right side, small hand-written text):
- Next to RAW: "ROW_COUNT, FRESHNESS, NULL_COUNT"
- Next to SILVER: "National ID, IBAN, Phone, Duplicates"
- Next to GOLD: "Expectations, Cross-Reference Integrity"
- Next to DQ: "AI Rule Discovery, Anomaly Detection"

BOTTOM STRIP:
Three hand-drawn rounded boxes in a row:
- "15" / "Notebooks" (Snowflake Blue #29B5E8 fill)
- "20+" / "Data Metric Functions" (Green #10B981 fill)
- "$5" / "Total Compute Cost" (Gold #D97706 fill)

Color palette: Snowflake Blue #29B5E8, Bronze #B45309, Silver #6B7280, Gold #D97706, Green #10B981, Dark text #1F2937, Light text #6B7280. White background.

Style notes:
- Everything should feel hand-drawn with slightly wobbly lines and hand-written Virgil font
- Same Excalidraw aesthetic as the other diagrams in this series
- The medallion layers (RAW to SILVER to GOLD) should be visually distinct through color and size
```

---

## dq-01-tool-sprawl.png (The Problem)

```
Create a technical diagram in a hand-drawn sketch style (Excalidraw aesthetic with slightly wobbly lines and hand-written font). White background. Dimensions: 1200x600 pixels.

Title (top-left, bold): "The DQ Tool Sprawl Problem"

LEFT SIDE (labeled "TYPICAL STACK"):
6 separate tool boxes arranged in a messy, scattered layout, connected by tangled red (#EF4444) lines:
- "Airflow" (small box, dark gray #374151)
- "Great Expectations" (small box, dark gray)
- "Metadata Catalog" (small box, dark gray)
- "dbt Cloud" (small box, dark gray)
- "Slack Bot" (small box, dark gray)
- "BI Dashboard" (small box, dark gray)
A frustrated stick figure in the center with question marks above their head.
Label below: "6 tools, 6 failure points" in Red (#EF4444)

RIGHT SIDE (labeled "NATIVE SNOWFLAKE"):
One large rounded rectangle in Snowflake Blue (#29B5E8) containing 6 neatly organized items:
- "DMFs" (small rounded pill)
- "Horizon Tags" (small rounded pill)
- "Native Alerts" (small rounded pill)
- "dbt in Snowflake" (small rounded pill)
- "Cortex AI" (small rounded pill)
- "Cost Visibility" (small rounded pill)
A happy stick figure next to it.
Label below: "1 platform, zero maintenance" in Green (#10B981)

A large arrow between left and right sides, colored green (#10B981), labeled "Simplify"

Color palette:
- Snowflake Blue (#29B5E8) for Snowflake elements
- Dark Gray (#374151) for external tools
- Green (#10B981) for the solution side
- Red (#EF4444) for the problem side
- Amber (#F59E0B) for warning highlights

Style notes:
- The left side should look chaotic and tangled
- The right side should look clean and organized
- Visual contrast tells the story in 3 seconds
```

---

## dq-02-dmf-lifecycle.png (Core Concept)

```
Create a technical diagram in a hand-drawn sketch style (Excalidraw aesthetic with slightly wobbly lines and hand-written font). White background. Dimensions: 1200x800 pixels.

Title (top-left, bold): "The DQ Lifecycle: From Detection to Resolution"

LAYOUT: A circular flow diagram with 10 numbered steps arranged clockwise in an oval:

1. "DETECT" (top, Snowflake Blue #29B5E8 circle) - small DMF icon
2. "DECIDE" (Green #10B981 circle) - checkmark/X icon
3. "LOG" (Dark Gray #374151 circle) - document icon
4. "ALERT" (Red #EF4444 circle) - bell icon
5. "INVESTIGATE" (Amber #F59E0B circle) - magnifying glass icon
6. "REMEDIATE" (Green #10B981 circle) - wrench icon
7. "REPORT" (Snowflake Blue #29B5E8 circle) - chart icon
8. "GOVERN" (Dark Gray #374151 circle) - shield icon
9. "OPTIMIZE" (Gold #D97706 circle) - dollar sign icon
10. "AUTOMATE" (Snowflake Blue #29B5E8 circle) - brain/AI icon

Green arrows (#10B981) connecting each step clockwise.

CENTER of the oval: "Snowflake Native" in Snowflake Blue, with a small snowflake logo.

Below each step, a small label in light gray (#6B7280):
1. "DMFs" 2. "Expectations" 3. "DQ_ISSUES_LOG" 4. "SYSTEM$SEND_EMAIL" 5. "Drill-down SQL" 6. "Quarantine + Resolve" 7. "Dashboard Views" 8. "Horizon Tags" 9. "Cost per DMF" 10. "Cortex AI"

ANNOTATION (bottom-right corner):
"Most workshops stop at step 1." in Red (#EF4444), with a small arrow pointing to "DETECT".
"This lab covers all 10." in Green (#10B981).

Style notes:
- Each circle should be roughly the same size
- The flow should feel like a continuous cycle, not a linear pipeline
- The center label anchors the message: all of this runs natively in Snowflake
```

---

## dq-03-architecture.png (Full Architecture)

```
Create a technical diagram in a hand-drawn sketch style (Excalidraw aesthetic with slightly wobbly lines and hand-written font). White background. Dimensions: 1200x800 pixels.

Title (top-left, bold): "Lab Architecture: 4 Sources, 3 Layers, 1 Platform"

LAYOUT: Left-to-right flow diagram with 4 vertical columns.

COLUMN 1 - "SOURCES" (leftmost):
4 small boxes stacked vertically:
- "SAP ERP" (30 rows) - dark gray #374151
- "Salesforce CRM" (25 rows) - dark gray
- "Gov Portal" (10 rows) - dark gray
- "Bank Feed" (50 rows) - dark gray
Small red dots on some boxes (indicating quality issues):
- Red dot on ERP: "invalid IDs"
- Red dot on CRM: "NULL fields"
- Red dot on Bank: "stale data, outliers"

COLUMN 2 - "RAW" (Bronze #B45309 background strip):
4 table icons: STG_ERP, STG_CRM, STG_GOV, STG_TXN
Label below: "System DMFs: ROW_COUNT, FRESHNESS, NULL_COUNT"
Small shield icons in Snowflake Blue on each table.

COLUMN 3 - "SILVER + GOLD":
Top half (Silver #6B7280 background strip):
2 table icons: INT_CUSTOMERS, INT_TRANSACTIONS
Label: "Dynamic Tables (auto-refresh)"
Badge: "Custom DMFs: National ID, IBAN, Phone, Duplicates"

Bottom half (Gold #D97706 background strip):
2 table icons: DIM_CUSTOMER, FACT_TRANSACTIONS
Label: "dbt in Snowflake"
Badge: "Expectations, Cross-Reference Integrity"

COLUMN 4 - "DQ LAYER" (Snowflake Blue #29B5E8 background strip):
5 items stacked vertically:
- "Rules Catalog" (document icon)
- "Cortex AI" (brain icon)
- "Issues Log" (list icon)
- "Alerts" (bell icon)
- "Dashboard" (chart icon)
Dotted blue lines (#29B5E8) connecting back to all three layer columns.

Green arrows (#10B981) flowing left to right between columns.

BOTTOM ANNOTATION:
"Total: 115 records, 20+ DMFs, 12 rules, 3 dashboard options" in dark gray.

Color palette:
- Snowflake Blue (#29B5E8) for DQ layer and monitoring elements
- Bronze (#B45309) for RAW layer
- Silver (#6B7280) for Silver layer
- Gold (#D97706) for Gold layer
- Dark Gray (#374151) for source systems and text
- Green (#10B981) for flow arrows
- Red (#EF4444) for quality issue indicators
```

---

## dq-04-cost-comparison.png (Optional: Cost Decision)

```
Create a technical diagram in a hand-drawn sketch style (Excalidraw aesthetic with slightly wobbly lines and hand-written font). White background. Dimensions: 1200x600 pixels.

Title (top-left, bold): "DMF Scheduling: The 12x Cost Difference"

LAYOUT: Side-by-side comparison with a divider line in the middle.

LEFT PANEL - "TRIGGER_ON_CHANGES":
A timeline showing 24 hours (midnight to midnight) as a horizontal line.
5 small green (#10B981) check marks at irregular intervals along the timeline (representing when data changes arrive).
Label below: "5 evaluations/day"
Cost box: "$0.15/day" in green text.
Caption: "Runs only when data changes. Ideal for TIER 1 (mission-critical)."

RIGHT PANEL - "CRON (HOURLY)":
Same 24-hour timeline.
24 amber (#F59E0B) check marks at every hour mark, evenly spaced.
19 of them have a small "no change" label in light gray (indicating wasted runs).
Label below: "24 evaluations/day"
Cost box: "$1.80/day" in red (#EF4444) text.
Caption: "Runs every hour regardless. 79% wasted for this table."

CENTER DIVIDER:
Large text: "12x" in bold red (#EF4444), with an arrow pointing from right to left.
Below: "Choose based on SLA tier, not habit."

BOTTOM ROW - Three tier boxes:
- TIER 1 (Green): "TRIGGER_ON_CHANGES" / "Mission-critical feeds"
- TIER 2 (Amber): "CRON 0 6,18 * * *" / "Twice daily, important tables"  
- TIER 3 (Dark Gray): "CRON 0 6 * * 1" / "Weekly, reference data"

Color palette:
- Green (#10B981) for efficient/trigger approach
- Amber (#F59E0B) for moderate/cron approach
- Red (#EF4444) for waste/cost highlights
- Dark Gray (#374151) for text and tier 3
- Snowflake Blue (#29B5E8) for tier labels

Style notes:
- The right panel should visually feel "heavier" and more cluttered than the left
- The 12x label should be the first thing the eye hits
```
