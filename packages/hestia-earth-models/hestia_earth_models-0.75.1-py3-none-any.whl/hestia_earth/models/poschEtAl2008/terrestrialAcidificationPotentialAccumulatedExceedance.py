from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.impact_assessment import impact_country_value
from hestia_earth.models.utils.indicator import _new_indicator
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "or": {
            "country": {"@type": "Term", "termType": "region"},
            "site": {
                "@type": "Site",
                "region": {"@type": "Term", "termType": "region"}
            }
        },
        "emissionsResourceUse": [{"@type": "Indicator", "value": "", "term.termType": "emission"}]
    }
}
RETURNS = {
    "Indicator": {
        "value": ""
    }
}
LOOKUPS = {
    "region-emission-terrestrialAcidificationPotentialAccumulatedExceedance": ""
}
TERM_ID = 'terrestrialAcidificationPotentialAccumulatedExceedance'

LOOKUP = f"{list(LOOKUPS.keys())[0]}.csv"


def run(impact_assessment: dict):
    value = impact_country_value(MODEL, TERM_ID, impact_assessment, f"{list(LOOKUPS.keys())[0]}.csv",
                                 default_world_value=True)
    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    value=value)
    logShouldRun(impact_assessment, MODEL, TERM_ID, value is not None)
    return _new_indicator(term=TERM_ID, model=MODEL, value=value)
