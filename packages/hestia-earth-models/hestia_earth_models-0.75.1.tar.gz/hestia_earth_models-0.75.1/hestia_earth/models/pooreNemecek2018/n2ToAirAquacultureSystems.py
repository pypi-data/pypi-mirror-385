from hestia_earth.schema import EmissionMethodTier

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import total_excreta, total_excreta_tan
from hestia_earth.models.utils.aquacultureManagement import valid_site_type
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{
            "@type": "Product",
            "value": "",
            "term.termType": "excreta",
            "term.units": "kg N",
            "properties": [
                {"@type": "Property", "value": "", "term.@id": "nitrogenContent"},
                {"@type": "Property", "value": "", "term.@id": "totalAmmoniacalNitrogenContentAsN"}
            ]
        }],
        "practices": [{"@type": "Practice", "value": "", "term.termType": "excretaManagement"}]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
TERM_ID = 'n2ToAirAquacultureSystems'
TIER = EmissionMethodTier.TIER_1.value
EF_Aqua = {'NH3N_N2N': 0.054, 'OtherN_N2N': 0.015}


def _emission(value: float):
    emission = _new_emission(term=TERM_ID, model=MODEL, value=value)
    emission['methodTier'] = TIER
    return emission


def _run(excr_tan: float, excr_n: float):
    value = EF_Aqua['NH3N_N2N'] * excr_tan + (EF_Aqua['OtherN_N2N'] * (excr_n - excr_tan) if excr_n else 0)
    return [_emission(value)]


def _should_run(cycle: dict):
    products = cycle.get('products', [])
    excr_n = total_excreta(products)
    excr_tan = total_excreta_tan(products)

    set_to_zero = not valid_site_type(cycle)  # if site is not water, set value to 0

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    excr_n=excr_n,
                    excr_tan=excr_tan,
                    set_to_zero=set_to_zero)

    should_run = any([excr_n or excr_tan or set_to_zero])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, excr_tan, excr_n, set_to_zero


def run(cycle: dict):
    should_run, excr_tan, excr_n, set_to_zero = _should_run(cycle)
    return [_emission(0)] if set_to_zero else _run(excr_tan, excr_n) if should_run else []
