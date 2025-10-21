from hestia_earth.schema import EmissionMethodTier, TermTermType

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.cycle import get_crop_residue_decomposition_N_total
from hestia_earth.models.utils.completeness import _is_term_type_complete
from hestia_earth.models.utils.emission import _new_emission
from .n2OToAirSoilFlux_utils import _should_run, _get_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "True",
        "products": [{
            "@type": "Product",
            "value": "",
            "term.termType": "cropResidue",
            "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
        }],
        "site": {
            "@type": "Site",
            "measurements": [
                {"@type": "Measurement", "value": "", "term.@id": "totalNitrogenPerKgSoil"},
                {"@type": "Measurement", "value": "", "term.@id": "organicCarbonPerKgSoil"},
                {"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"},
                {"@type": "Measurement", "value": "", "term.@id": "clayContent"},
                {"@type": "Measurement", "value": "", "term.@id": "sandContent"},
                {"@type": "Measurement", "value": "", "term.@id": "soilPh"}
            ]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 2"
    }]
}
LOOKUPS = {
    "cropResidue": "decomposesOnField",
    "crop": "cropGroupingStehfestBouwman",
    "ecoClimateZone": "STEHFEST_BOUWMAN_2006_N2O-N_FACTOR"
}
TERM_ID = 'n2OToAirCropResidueDecompositionDirect'
TIER = EmissionMethodTier.TIER_2.value


def _emission(value: float):
    emission = _new_emission(term=TERM_ID, model=MODEL, value=value)
    emission['methodTier'] = TIER
    return emission


def _run(cycle: dict, content_list_of_items: list, N_total: float):
    n2OToAirSoilFlux = _get_value(cycle, content_list_of_items, N_total, TERM_ID)
    N_crop_residue = get_crop_residue_decomposition_N_total(cycle)
    value = N_crop_residue / N_total * n2OToAirSoilFlux if all([
        N_crop_residue, N_total
    ]) else 0
    return [_emission(value)]


def run(cycle: dict):
    default_should_run, N_total, content_list_of_items = _should_run(cycle, TERM_ID, TIER)
    term_type_complete = _is_term_type_complete(cycle, TermTermType.CROPRESIDUE)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    term_type_cropResidue_complete=term_type_complete)

    should_run = all([default_should_run, term_type_complete])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)

    return _run(cycle, content_list_of_items, N_total) if should_run else []
