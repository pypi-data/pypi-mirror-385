from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.emission import _new_emission
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "emissions": [
            {"@type": "Emission", "value": "", "term.@id": "n2OToAirExcretaDirect"}
        ]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 1"
    }]
}
TERM_ID = 'n2ToAirExcreta'
TIER = EmissionMethodTier.TIER_1.value
_N2O_TERM_ID = 'n2OToAirExcretaDirect'


def _emission(value: float):
    emission = _new_emission(term=TERM_ID, model=MODEL, value=value)
    emission['methodTier'] = TIER
    return emission


def _run(n2o_value: float):
    value = 3 * n2o_value / get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    return [_emission(value)]


def _should_run(cycle: dict):
    n2o = find_term_match(cycle.get('emissions', []), _N2O_TERM_ID)
    n2o_value = list_sum(n2o.get("value", []), default=None)

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    **{_N2O_TERM_ID: n2o_value})

    should_run = all([n2o_value is not None])
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, n2o_value


def run(cycle: dict):
    should_run, n2o_value = _should_run(cycle)
    return _run(n2o_value) if should_run else []
