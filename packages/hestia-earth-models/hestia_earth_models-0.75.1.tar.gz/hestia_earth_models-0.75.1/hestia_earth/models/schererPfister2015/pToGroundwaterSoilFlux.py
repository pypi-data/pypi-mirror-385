from hestia_earth.schema import EmissionMethodTier

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from . import MODEL
from .utils import get_liquid_slurry_sludge_P_total

REQUIREMENTS = {
    "Cycle": {
        "endDate": "",
        "inputs": [{"@type": "Input", "value": "", "term.termType": "organicFertiliser"}],
        "site": {
            "@type": "Site",
            "country": {"@type": "Term", "termType": "region"},
            "measurements": [
                {"@type": "Measurement", "value": "", "term.@id": "drainageClass"}
            ]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
LOOKUPS = {
    "organicFertiliser": "OrganicFertiliserClassification"
}
TERM_ID = 'pToGroundwaterSoilFlux'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float):
    emission = _new_emission(term=TERM_ID, model=MODEL, value=value)
    emission['methodTier'] = TIER
    return emission


def _run(cycle: dict, drainageClass: list):
    P_total, _ = get_liquid_slurry_sludge_P_total(cycle)
    value = 0.07 * (1 + P_total * 0.2/80) * (0 if drainageClass > 4 else 1)
    return [_emission(value)]


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    drainageClass = most_relevant_measurement_value(measurements, 'drainageClass', end_date)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    drainageClass=drainageClass)

    should_run = all([drainageClass])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, drainageClass


def run(cycle: dict):
    should_run, drainageClass = _should_run(cycle)
    return _run(cycle, drainageClass) if should_run else []
