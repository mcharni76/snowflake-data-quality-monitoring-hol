# Publishing Guide

## Repository Identity

**Name:** `snowflake-data-quality-monitoring-hol`
**URL:** `github.com/mcharni/snowflake-data-quality-monitoring-hol`
**Description (GitHub):** "Production-ready Data Quality monitoring with native Snowflake: DMFs, Expectations, Dynamic Tables, dbt, Cortex AI, and Horizon Governance. Full-day hands-on workshop (15 modules)."

**Topics (GitHub tags):**
snowflake, data-quality, data-metric-functions, dbt, dynamic-tables, cortex-ai, data-governance, hands-on-lab, workshop, monitoring, enterprise, dmf, expectations, horizon, data-engineering

## Steps to Publish

```bash
# 1. Initialize git repo
cd /Users/mcharni/Projects/DQ/hol
git init
git add .
git commit -m "v1.1: Data Quality Monitoring with Snowflake - complete workshop"

# 2. Create GitHub repo (public)
gh repo create mcharni/snowflake-data-quality-monitoring-hol \
  --public \
  --description "Production-ready Data Quality monitoring with native Snowflake: DMFs, Expectations, Dynamic Tables, dbt, Cortex AI, and Horizon Governance. Full-day hands-on workshop." \
  --source . \
  --push

# 3. Add topics for discoverability
gh repo edit mcharni/snowflake-data-quality-monitoring-hol \
  --add-topic snowflake,data-quality,data-metric-functions,dbt,dynamic-tables,cortex-ai,data-governance,hands-on-lab,workshop,monitoring

# 4. Tag the release
git tag -a v1.1 -m "v1.1: Polished release with real dbt, DMF costs, cell descriptions"
git push --tags
```

## Discoverability Strategy

### Where People Search for DQ Content

1. **GitHub** -- topics + README keywords + good description
2. **Google** -- README title matches search queries ("data quality monitoring snowflake")
3. **Snowflake Community** -- share link on community.snowflake.com
4. **Medium/LinkedIn** -- write a companion article (see content/medium-articles skill)
5. **Snowflake Quickstarts** -- submit to quickstarts.snowflake.com (requires Snowflake approval)

### SEO-Optimized Elements Already in Place

- README title: "Data Quality Monitoring with Snowflake" (exact search phrase)
- Keywords section at bottom of README
- GitHub topics cover all major search terms
- Architecture diagram in README (increases engagement)
- Badges (visual credibility signals)
- "What Makes This Workshop Unique" comparison table (differentiator)

### Recommended Amplification

1. **LinkedIn post** announcing the repo (tag Snowflake, dbt, data engineering communities)
2. **Medium article** -- "Building Enterprise Data Quality with Zero External Tools" (companion piece)
3. **Snowflake Community post** in the Data Engineering forum
4. **Submit to Snowflake-Labs** -- if approved, gets listed on quickstarts.snowflake.com (highest Snowflake visibility)

## Future: Move to Snowflake-Labs

If you want maximum official visibility:
1. Publish on personal GitHub first (immediate)
2. Get traction (stars, forks, feedback)
3. Submit PR to github.com/Snowflake-Labs with the `sfguide-` prefix
4. Once accepted, redirect personal repo to Snowflake-Labs fork
