from hestia_earth.schema import EmissionMethodTier, TermTermType

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import get_organic_fertiliser_N_total, get_ecoClimateZone
from .utils import get_FracLEACH_H
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.fertiliser": "True",
        "completeness.water": "True",
        "inputs": [
            {
                "@type": "Input",
                "value": "",
                "term.termType": "organicFertiliser",
                "optional": {
                    "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
                }
            },
            {
                "@type": "Input",
                "value": "",
                "term.termType": "fertiliserBrandName",
                "properties": [{"@type": "Property", "value": "", "key.termType": "organicFertiliser"}]
            }
        ],
        "site": {
            "@type": "Site",
            "measurements": [{"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"}]
        },
        "optional": {
            "practices": [{"@type": "Practice", "value": "", "term.termType": "waterRegime"}]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "sd": "",
        "min": "",
        "max": "",
        "methodTier": "tier 1",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'no3ToGroundwaterOrganicFertiliser'
TIER = EmissionMethodTier.TIER_1.value


def _emission(value: float, sd: float, min: float, max: float):
    emission = _new_emission(term=TERM_ID, model=MODEL, value=value, min=min, max=max, sd=sd)
    emission['methodTier'] = TIER
    return emission


def _run(cycle: dict):
    N_total = get_organic_fertiliser_N_total(cycle)
    value, min, max, sd = get_FracLEACH_H(cycle, TERM_ID)
    converted_N_total = N_total * get_atomic_conversion(Units.KG_NO3, Units.TO_N)
    return [_emission(
        converted_N_total * value,
        converted_N_total * sd,
        converted_N_total * min,
        converted_N_total * max
    )]


def _should_run(cycle: dict):
    N_organic_fertiliser = get_organic_fertiliser_N_total(cycle)
    ecoClimateZone = get_ecoClimateZone(cycle)
    fertiliser_complete = _is_term_type_complete(cycle, 'fertiliser')
    water_complete = _is_term_type_complete(cycle, TermTermType.WATER)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    N_organic_fertiliser=N_organic_fertiliser,
                    ecoClimateZone=ecoClimateZone,
                    term_type_fertiliser_complete=fertiliser_complete,
                    term_type_water_complete=water_complete)

    should_run = all([N_organic_fertiliser is not None, ecoClimateZone, fertiliser_complete, water_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []
