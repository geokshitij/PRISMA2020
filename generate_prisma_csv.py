import pandas as pd
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = REPO_ROOT / "inst" / "extdata" / "PRISMA.csv"
OUTPUT_PATH = REPO_ROOT / "PRISMA_data.csv"

SEARCH_QUERY = (
    "( TITLE-ABS-KEY ( ( 'earth observation' OR 'remote sensing' OR satellite ) "
    "AND ( 'machine learning' OR 'deep learning' OR 'artificial intelligence' ) "
    "AND ( 'streamflow' OR 'river flow' OR runoff OR discharge ) AND ( forecast* "
    "OR predict* OR model* OR simula* ) ) ) AND PUBYEAR > 2014 AND PUBYEAR < 2026 "
    "AND ( LIMIT-TO ( SRCTYPE , 'j' ) ) AND ( LIMIT-TO ( DOCTYPE , 'ar' ) ) AND "
    "( LIMIT-TO ( LANGUAGE , 'English' ) )"
)

REVIEW_OBJECTIVE = (
    "Systematically identify, analyse, and synthesise studies using Earth "
    "Observation data with machine learning approaches for streamflow forecasting."
)

COUNTS = {
    "initial_hits": 611,
    "database_results": 611,
    "records_screened": 438,
    "records_excluded": 356,
    "dbr_sought_reports": 82,
    "dbr_notretrieved_reports": 2,
    "dbr_assessed": 80,
    "dbr_excluded": 2,
    "new_studies": 78,
    "new_reports": None,
    "total_studies": 78,
    "total_reports": 78,
}

PRE_SCREEN_FILTER_NOTE = (
    # "Records removed before screening:\n"
    "Year < 2015 and non-English articles"
)

RECORDS_EXCLUDED_BOX_TEXT = (
    "Records excluded:\n"
    "- Not streamflow-focused (n = 232)\n"
    "- No machine-learning approach (n = 104)\n"
    "- No Earth Observation input (n = 20)"
)

EXCLUSION_REASONS = [
    ("Not streamflow-focused", 232),
    ("No machine-learning approach", 104),
    ("No Earth Observation input", 20),
]


def build_exclusion_tooltip(reasons):
    lines = ["Abstract screening exclusions summary (n = 356):"]
    lines.extend(
        f"- {text} (n = {count})" for text, count in reasons
    )
    return "\n".join(lines)


def sanitize_tooltip(text):
    if text is None:
        return None
    return text.replace("'", "&#39;")


def sanitize_boxtext(text):
    if text is None:
        return None
    return text.replace("'", "&#39;")


def main():
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Template not found at {TEMPLATE_PATH}. Please verify the repository structure."
        )

    reason_total = sum(count for _, count in EXCLUSION_REASONS)
    if reason_total != COUNTS["records_excluded"]:
        raise ValueError(
            "Exclusion reasons total "
            f"{reason_total} does not match records_excluded {COUNTS['records_excluded']}"
        )

    prisma_df = pd.read_csv(TEMPLATE_PATH)

    sentinel = object()

    def update_row(key, *, n_value=sentinel, boxtext=None, tooltips=None):
        mask = prisma_df["data"] == key
        if not mask.any():
            return
        if n_value is not sentinel:
            prisma_df.loc[mask, "n"] = pd.NA if n_value is None else n_value
        if boxtext is not None:
            prisma_df.loc[mask, "boxtext"] = sanitize_boxtext(boxtext)
        if tooltips is not None:
            prisma_df.loc[mask, "tooltips"] = sanitize_tooltip(tooltips)

    # Disable previous studies and other sources columns
    update_row("previous_studies", n_value=None)
    update_row("previous_reports", n_value=None)
    update_row("website_results", n_value=None)
    update_row("organisation_results", n_value=None)
    update_row("citations_results", n_value=None)
    update_row("register_results", n_value=None)
    update_row("register_specific_results", n_value=None)
    update_row("database_specific_results", n_value=None)
    update_row("other_sought_reports", n_value=None)
    update_row("other_notretrieved_reports", n_value=None)
    update_row("other_assessed", n_value=None)
    update_row("other_excluded", n_value=None)

    # Identification pathway values
    update_row(
        "database_results",
        n_value=COUNTS["database_results"],
        tooltips=(
            "Scopus search executed on 2025-11-05\n"
            f"Initial hits before limits: {COUNTS['initial_hits']}\n"
            "Filters applied: publication year 2015-2025, journals, English, article type\n"
            "Records exported for screening: 438\n"
            f"Advanced query: {SEARCH_QUERY}"
        ),
    )
    update_row(
        "duplicates",
        n_value=173,
        boxtext=PRE_SCREEN_FILTER_NOTE,
        tooltips=(
            f"Initial Scopus hits before filters: {COUNTS['initial_hits']}\n"
            "Applied limits: publication year 2015-2025, journal articles, "
            "English language, document type=article\n"
            "Records removed: 173 (year < 2015 or non-English)\n"
            "Post-filter records exported: 438"
        ),
    )
    update_row("excluded_automatic", n_value=None)
    update_row("excluded_other", n_value=None)

    # Screening pathway values
    update_row("records_screened", n_value=COUNTS["records_screened"])
    update_row(
        "records_excluded",
        n_value=COUNTS["records_excluded"],
        boxtext=RECORDS_EXCLUDED_BOX_TEXT,
        tooltips=build_exclusion_tooltip(EXCLUSION_REASONS),
    )

    # Full-text assessment pathway values
    update_row("dbr_sought_reports", n_value=COUNTS["dbr_sought_reports"])
    update_row("dbr_notretrieved_reports", n_value=COUNTS["dbr_notretrieved_reports"])
    update_row("dbr_assessed", n_value=COUNTS["dbr_assessed"])
    update_row(
        "dbr_excluded",
        n_value="Full-text exclusions, 2",
        tooltips="Two reports excluded at full-text stage (e.g. conference abstracts).",
    )

    # Included studies
    update_row("new_studies", n_value=COUNTS["new_studies"])
    update_row("new_reports", n_value=COUNTS["new_reports"])
    update_row("total_studies", n_value=COUNTS["total_studies"])
    update_row("total_reports", n_value=COUNTS["total_reports"])
    update_row("total_studies_ma", n_value=None)
    update_row("total_reports_ma", n_value=None)

    update_row(
        "identification",
        tooltips=(
            "Review objective:\n"
            f"{REVIEW_OBJECTIVE}"
        ),
    )

    prisma_df.to_csv(OUTPUT_PATH, index=False, na_rep="")
    print("Successfully created PRISMA_data.csv")


if __name__ == "__main__":
    main()
