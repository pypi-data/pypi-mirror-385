from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import impact_emission_lookup_value
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "emissionsResourceUse": [{"@type": "Indicator", "value": "", "term.termType": "emission"}]
    }
}
RETURNS = {
    "Indicator": {
        "value": ""
    }
}
LOOKUPS = {
    "emission": "po4-EqEutrophicationExcludingFateCml2001Baseline"
}
TERM_ID = 'eutrophicationPotentialExcludingFate'


def _indicator(value: float): return _new_indicator(term=TERM_ID, model=MODEL, value=value)


def run(impact_assessment: dict):
    value = impact_emission_lookup_value(MODEL, TERM_ID, impact_assessment, LOOKUPS['emission'])
    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    value=value)
    logShouldRun(impact_assessment, MODEL, TERM_ID, value is not None)
    return _indicator(value) if value is not None else None
