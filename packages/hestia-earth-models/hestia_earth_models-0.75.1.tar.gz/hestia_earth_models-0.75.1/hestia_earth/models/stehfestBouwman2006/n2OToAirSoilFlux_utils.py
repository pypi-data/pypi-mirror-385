import math
from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.tools import list_sum, non_empty_list

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.cycle import (
    get_crop_residue_decomposition_N_total, get_excreta_N_total,
    get_organic_fertiliser_N_total, get_inorganic_fertiliser_N_total
)
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.ecoClimateZone import get_ecoClimateZone_lookup_value
from hestia_earth.models.utils.crop import get_crop_lookup_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.excreta": "True",
        "completeness.cropResidue": "True",
        "completeness.fertiliser": "True",
        "inputs": [{
            "@type": "Input",
            "value": "",
            "term.units": ["kg", "kg N"],
            "term.termType": ["organicFertiliser", "inorganicFertiliser", "excreta"],
            "optional": {
                "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
            }
        }],
        "products": [{
            "@type": "Product",
            "value": "",
            "term.termType": ["cropResidue", "excreta"],
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
    "crop": "cropGroupingStehfestBouwman",
    "ecoClimateZone": "STEHFEST_BOUWMAN_2006_N2O-N_FACTOR"
}
TERM_ID = 'n2OToAirSoilFlux'
TIER = EmissionMethodTier.TIER_2.value
N2O_FACTORS_BY_CROP = {
    'Cereals': 0,
    'Grass': -0.3502,
    'Legume': 0.3783,
    'Other': 0.4420,
    'W-Rice': -0.8850,
    'None': 0.5870
}


def _emission(value: float):
    emission = _new_emission(term=TERM_ID, model=MODEL, value=value)
    emission['methodTier'] = TIER
    return emission


def _get_crop_crouping(product: dict):
    term_id = product.get('term', {}).get('@id') if product else None
    return get_crop_lookup_value(MODEL, TERM_ID, term_id, 'cropGroupingStehfestBouwman')


def _should_run(cycle: dict, term=TERM_ID, tier=TIER):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    clay = most_relevant_measurement_value(measurements, 'clayContent', end_date)
    sand = most_relevant_measurement_value(measurements, 'sandContent', end_date)
    organicCarbonPerKgSoil = most_relevant_measurement_value(measurements, 'organicCarbonPerKgSoil', end_date)
    soilPh = most_relevant_measurement_value(measurements, 'soilPh', end_date)
    ecoClimateZone = most_relevant_measurement_value(measurements, 'ecoClimateZone', end_date)
    product = find_primary_product(cycle)
    crop_grouping = _get_crop_crouping(product) if product else None
    crop_grouping_allowed = crop_grouping in N2O_FACTORS_BY_CROP

    N_crop_residue = get_crop_residue_decomposition_N_total(cycle)
    N_organic_fertiliser = get_organic_fertiliser_N_total(cycle)
    N_inorganic_fertiliser = get_inorganic_fertiliser_N_total(cycle)
    N_excreta = get_excreta_N_total(cycle)
    N_total = list_sum(non_empty_list([
        N_crop_residue,
        N_organic_fertiliser,
        N_inorganic_fertiliser,
        N_excreta
    ]))
    content_list_of_items = [clay, sand, organicCarbonPerKgSoil, soilPh, ecoClimateZone, crop_grouping]

    logRequirements(cycle, model=MODEL, term=term,
                    clay=clay,
                    sand=sand,
                    organicCarbonPerKgSoil=organicCarbonPerKgSoil,
                    soilPh=soilPh,
                    ecoClimateZone=ecoClimateZone,
                    crop_grouping=crop_grouping,
                    crop_grouping_allowed=crop_grouping_allowed,
                    N_total=N_total,
                    N_crop_residue=N_crop_residue,
                    N_organic_fertiliser=N_organic_fertiliser,
                    N_inorganic_fertiliser=N_inorganic_fertiliser,
                    N_excreta=N_excreta)

    should_run = all([
        all(content_list_of_items),
        N_total >= 0,
        crop_grouping_allowed
    ])
    logShouldRun(cycle, MODEL, term, should_run, methodTier=tier)
    return should_run, N_total, content_list_of_items


def _organic_carbon_factor(organicCarbonPerKgSoil: float):
    return 0 if organicCarbonPerKgSoil < 10 else (0.0526 if organicCarbonPerKgSoil <= 30 else 0.6334)


def _soilph_factor(soilPh: float):
    return 0 if soilPh < 5.5 else (-0.4836 if soilPh > 7.3 else -0.0693)


def _sand_factor(sand: float, clay: float):
    return 0 if sand > 65 and clay < 18 else (-0.1528 if sand < 65 and clay < 35 else 0.4312)


def _get_value(cycle: dict, content_list_of_items: list, N_total: float, term=TERM_ID):
    clay, sand, organicCarbonPerKgSoil, soilPh, ecoClimateZone, crop_grouping = content_list_of_items

    carbon_factor = _organic_carbon_factor(organicCarbonPerKgSoil)
    soil_factor = _soilph_factor(soilPh)
    sand_factor = _sand_factor(sand, clay)
    eco_factor = get_ecoClimateZone_lookup_value(ecoClimateZone, 'STEHFEST_BOUWMAN_2006_N2O-N_FACTOR')
    crop_grouping_factor = N2O_FACTORS_BY_CROP[crop_grouping]
    sum_factors = sum([carbon_factor, soil_factor, sand_factor, eco_factor or 0, crop_grouping_factor])
    conversion_unit = get_atomic_conversion(Units.KG_N2O, Units.TO_N)

    try:
        value = min(
            0.072 * N_total,
            math.exp(0.475 + 0.0038 * N_total + sum_factors) -
            math.exp(0.475 + sum_factors)
        )
    except OverflowError:
        value = 0.072 * N_total

    debugValues(cycle, model=MODEL, term=term,
                carbon_factor=carbon_factor,
                soil_factor=soil_factor,
                sand_factor=sand_factor,
                eco_factor=eco_factor,
                crop_grouping_factor=crop_grouping_factor,
                sum_factors=sum_factors,
                conversion_unit=conversion_unit)

    return value * conversion_unit


def _run(cycle: dict, content_list_of_items: list, N_total: float):
    value = _get_value(cycle, content_list_of_items, N_total)
    return [_emission(value)]


def run(cycle: dict):
    should_run, N_total, content_list_of_items = _should_run(cycle)
    return _run(cycle, content_list_of_items, N_total) if should_run else []
