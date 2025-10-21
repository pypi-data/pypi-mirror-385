from enum import Enum
from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.blank_node import get_total_value
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import match_lookup_value
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.property import _get_nitrogen_tan_content
from hestia_earth.models.utils.organicFertiliser import get_cycle_inputs as get_organicFertiliser_inputs
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.fertiliser": "",
        "inputs": [
            {
                "@type": "Input",
                "value": "",
                "term.termType": "organicFertiliser",
                "properties": [{"@type": "Property", "value": "", "term.@id": "totalAmmoniacalNitrogenContentAsN"}]
            },
            {
                "@type": "Input",
                "value": "",
                "term.termType": "fertiliserBrandName",
                "properties": [{"@type": "Property", "value": "", "key.termType": "organicFertiliser"}]
            }
        ]
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
TERM_ID = 'nh3ToAirOrganicFertiliser'
TIER = EmissionMethodTier.TIER_1.value


class Classification(Enum):
    LIQUID_SLURRY_SEWAGESLUDGE = 'Liquid, Slurry, Sewage Sludge'
    SOLID = 'Solid'
    COMPOST = 'Compost'
    GREEN_MANURE = 'Green Manure'


NH3_TAN_FACTOR = {
    Classification.LIQUID_SLURRY_SEWAGESLUDGE: 0.307877242878561,
    Classification.SOLID: 0.685083144186046,
    Classification.COMPOST: 0.710000000000000,
    Classification.GREEN_MANURE: 0
}


def _emission(value: float):
    emission = _new_emission(term=TERM_ID, model=MODEL, value=value)
    emission['methodTier'] = TIER
    return emission


def _grouped_value(group: dict):
    classification = group.get('classification')
    return list_sum(group.get('values')) * NH3_TAN_FACTOR[classification]


def _run(organic_fertiliser_values: list):
    value = sum(list(map(_grouped_value, organic_fertiliser_values)))
    return [_emission(value)]


def _get_N_grouped_values(cycle: dict, classification: Classification):
    inputs = get_organicFertiliser_inputs(cycle)
    values = [
        list_sum(get_total_value([i])) * _get_nitrogen_tan_content(i) / 100 for i in inputs
        if match_lookup_value(i, col_name=LOOKUPS['organicFertiliser'], col_value=classification.value)
    ]
    values = [0] if len(values) == 0 and _is_term_type_complete(cycle, 'fertiliser') else values
    return {'classification': classification, 'values': values}


def _grouped_values_log(group: dict):
    return ';'.join([group.get('classification').value, str(list_sum(group.get('values')))])


def _should_run(cycle: dict):
    lqd_slurry_sluge_values = _get_N_grouped_values(cycle, Classification.LIQUID_SLURRY_SEWAGESLUDGE)
    solid_values = _get_N_grouped_values(cycle, Classification.SOLID)
    compost_values = _get_N_grouped_values(cycle, Classification.COMPOST)
    green_manure_values = _get_N_grouped_values(cycle, Classification.GREEN_MANURE)
    organic_fertiliser_values = [lqd_slurry_sluge_values, solid_values, compost_values, green_manure_values]

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    lqd_slurry_sluge_values=_grouped_values_log(lqd_slurry_sluge_values),
                    solid_values=_grouped_values_log(solid_values),
                    compost_values=_grouped_values_log(compost_values),
                    green_manure_values=_grouped_values_log(green_manure_values))

    should_run = all([len(v.get('values')) > 0 for v in organic_fertiliser_values])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, organic_fertiliser_values


def run(cycle: dict):
    should_run, organic_fertiliser_values = _should_run(cycle)
    return _run(organic_fertiliser_values) if should_run else []
