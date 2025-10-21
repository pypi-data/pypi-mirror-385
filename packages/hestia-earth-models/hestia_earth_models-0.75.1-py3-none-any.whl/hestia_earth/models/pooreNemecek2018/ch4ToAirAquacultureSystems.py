from enum import Enum
from hestia_earth.schema import EmissionMethodTier, SiteSiteType, TermTermType
from hestia_earth.utils.model import find_term_match, filter_list_term_type
from hestia_earth.utils.tools import list_sum, list_average

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import _filter_list_term_unit
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.temperature import TemperatureLevel, get_level
from hestia_earth.models.utils.blank_node import get_total_value
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.aquacultureManagement import valid_site_type
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "endDate": "",
        "products": [{
            "@type": "Product",
            "value": "",
            "term.termType": "excreta",
            "term.units": "kg VS"
        }],
        "practices": [
            {"@type": "Practice", "value": "", "term.@id": "excretionIntoWaterBody"},
            {"@type": "Practice", "value": "", "term.@id": "slaughterAge"},
            {"@type": "Practice", "value": "", "term.@id": "yieldOfPrimaryAquacultureProductLiveweightPerM2"}
        ],
        "site": {
            "@type": "Site",
            "or": [
                {
                    "measurements": [
                        {"@type": "Measurement", "value": "", "term.@id": "temperatureAnnual"},
                        {"@type": "Measurement", "value": "", "term.@id": "waterDepth"}
                    ]
                },
                {
                    "siteType": "sea or ocean",
                    "measurements": [
                        {"@type": "Measurement", "value": "", "term.@id": "slowFlowingWater"},
                        {"@type": "Measurement", "value": "", "term.@id": "fastFlowingWater"}
                    ]
                }
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
TERM_ID = 'ch4ToAirAquacultureSystems'
TIER = EmissionMethodTier.TIER_1.value
FAST_FLOWING_WATER = 'fastFlowingWater'
SLOW_FLOWING_WATER = 'slowFlowingWater'
WATER_DEPTH = 'waterDepth'
Conv_Aquaculture_CH4C_CH4CAir_2m = 0.22
Conv_Aquaculture_CH4C_CH4CAir_0_2m = 0.61225
Conv_Aquaculture_CH4Cmax = 0.50239375369354


class MOC(Enum):
    FAST = 'fastWater'
    SLOW_LOW_TEMP = 'slowWaterLowTemp'
    SLOW_HIGH_TEMP = 'slowWaterHighTemp'
    MARINE_FLOW = SiteSiteType.SEA_OR_OCEAN.value


OC_Aqua = {
    TemperatureLevel.LOW: 0.3,
    TemperatureLevel.MEDIUM: 0.3,
    TemperatureLevel.HIGH: 0.6
}
MOC_Aqua = {
    MOC.FAST: 0,
    MOC.SLOW_LOW_TEMP: 0.2,
    MOC.SLOW_HIGH_TEMP: 0.45,
    MOC.MARINE_FLOW: 0.04
}
MOC_FROM_SYS = {
    MOC.FAST: lambda system, *args: system == FAST_FLOWING_WATER,
    MOC.SLOW_LOW_TEMP: lambda system, temp_level: system == SLOW_FLOWING_WATER and temp_level != TemperatureLevel.HIGH,
    MOC.SLOW_HIGH_TEMP: lambda system, temp_level: system == SLOW_FLOWING_WATER and temp_level == TemperatureLevel.HIGH,
    MOC.MARINE_FLOW: lambda system, *args: system == SiteSiteType.SEA_OR_OCEAN.value
}


def _emission(value: float):
    emission = _new_emission(term=TERM_ID, model=MODEL, value=value)
    emission['methodTier'] = TIER
    return emission


def _oc(temp: float): return OC_Aqua.get(get_level(temperature=temp), 0)


def _oc_flow(temp: float, system: str):
    temp_level = get_level(temperature=temp)
    oc_flow_key = next((key for key in MOC_FROM_SYS if MOC_FROM_SYS[key](system, temp_level)), None)
    return MOC_Aqua.get(oc_flow_key, 0)


def _Conv_Aquaculture_CH4C_CH4CAir(waterDepth: float):
    return Conv_Aquaculture_CH4C_CH4CAir_2m if waterDepth > 2 else Conv_Aquaculture_CH4C_CH4CAir_0_2m


def _run(excretaKgVs: float, temp: float, system: str, waterDepth: float, yield_per_m2: float, slaughterAge: int):
    value = min(
        excretaKgVs * _oc(temp) * _oc_flow(temp, system) * _Conv_Aquaculture_CH4C_CH4CAir(waterDepth),
        Conv_Aquaculture_CH4Cmax * slaughterAge / yield_per_m2
    ) * get_atomic_conversion(Units.KG_CH4, Units.TO_C)
    return [_emission(value)]


def _get_term_id(node: dict):
    return node.get('term', {}).get('@id', {}) if node else None


def _should_run(cycle: dict):

    products = cycle.get('products', [])
    excr_products = filter_list_term_type(products, TermTermType.EXCRETA)
    excretaKgVs = list_sum(get_total_value(_filter_list_term_unit(excr_products, Units.KG_VS)), default=None)

    practices = cycle.get('practices', [])
    yield_per_m2 = list_sum(
        find_term_match(practices, 'yieldOfPrimaryAquacultureProductLiveweightPerM2').get('value', []), default=None
    )
    slaughterAge = list_sum(find_term_match(practices, 'slaughterAge').get('value', []), default=None)

    site = cycle.get('site', {})
    end_date = cycle.get('endDate')
    measurements = site.get('measurements', [])
    temp = most_relevant_measurement_value(measurements, 'temperatureAnnual', end_date)
    slowFlowingWater = find_term_match(measurements, SLOW_FLOWING_WATER)
    fastFlowingWater = find_term_match(measurements, FAST_FLOWING_WATER)
    waterDepth = list_average(find_term_match(measurements, WATER_DEPTH).get('value', []))

    system = _get_term_id(slowFlowingWater) or _get_term_id(fastFlowingWater) or site.get('siteType')

    set_to_zero = not valid_site_type(cycle)  # if site is not water, set value to 0

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    excretaKgVs=excretaKgVs,
                    temp=temp,
                    system=system,
                    waterDepth=waterDepth,
                    yield_of_target_species=yield_per_m2,
                    slaughterAge=slaughterAge,
                    set_to_zero=set_to_zero)

    should_run = all([
        excretaKgVs, temp, system, waterDepth, yield_per_m2, slaughterAge
    ]) or set_to_zero
    logShouldRun(cycle, MODEL, TERM_ID, should_run, methodTier=TIER)
    return should_run, excretaKgVs, temp, system, waterDepth, yield_per_m2, slaughterAge, set_to_zero


def run(cycle: dict):
    should_run, excretaKgVs, temp, system, waterDepth, yield_per_m2, slaughterAge, set_to_zero = _should_run(cycle)
    return [_emission(0)] if set_to_zero else \
        _run(excretaKgVs, temp, system, waterDepth, yield_per_m2, slaughterAge) if should_run else []
