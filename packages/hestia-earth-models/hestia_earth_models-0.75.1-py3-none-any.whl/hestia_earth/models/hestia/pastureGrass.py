from hestia_earth.schema import SiteSiteType, TermTermType
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.term import download_term

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.practice import _new_practice
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "site": {
            "@type": "Site",
            "siteType": "permanent pasture"
        }
    }
}
RETURNS = {
    "Practice": {
        "key.@id": "genericGrassPlant",
        "value": "100"
    }
}
TERM_ID = 'pastureGrass'
KEY_TERM_ID = 'genericGrassPlant'


def _practice():
    practice = _new_practice(term=TERM_ID, model=MODEL, value=100)
    practice['key'] = linked_node(download_term(KEY_TERM_ID, TermTermType.LANDCOVER))
    return practice


def _should_run(cycle: dict):
    site_type = cycle.get('site', {}).get('siteType')
    is_permanent_pasture = site_type == SiteSiteType.PERMANENT_PASTURE.value

    logRequirements(cycle, model=MODEL, term=TERM_ID,
                    is_permanent_pasture=is_permanent_pasture)

    should_run = all([is_permanent_pasture])
    logShouldRun(cycle, MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return _practice() if _should_run(cycle) else None
