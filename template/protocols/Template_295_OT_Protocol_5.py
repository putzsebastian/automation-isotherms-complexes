from opentrons import protocol_api
import ast

metadata = {
    'protocolName': 'Isotherm Step 5 - Transfer for measurement',
    'author': 'S. Putz',
    'description': "Transfer of binding supernatant to measurement plate"
}
requirements = {"robotType": "OT-2", "apiLevel": "2.19"}

# Helper parsers to allow templating placeholders (2, 100;500)
# and real values after substitution.
def _parse_replicates(value):
    try:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            s = value.strip()
            # If placeholder not yet replaced, default to 1 for simulation
            if s.startswith('[[') and s.endswith(']]'):
                return 1
            return int(float(s))
    except Exception:
        return 1
    return 1

def _parse_float(val, default):
    try:
        if isinstance(val, str) and val.strip().startswith("[["):
            return float(default)
        return float(val)
    except Exception:
        return float(default)
        
def _parse_concentrations(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        s = value.strip()
        # If placeholder not yet replaced, default to one item for simulation
        if s.startswith('[[') and s.endswith(']]'):
            return [1]
        # Try Python literal list/tuple first
        try:
            parsed = ast.literal_eval(s)
            if isinstance(parsed, (list, tuple)):
                return list(parsed)
        except Exception:
            pass
        # Fallback: comma-separated
        if ',' in s:
            parts = [p.strip() for p in s.split(',') if p.strip() != '']
            return parts if parts else [1]
        if len(s) > 0:
            return [s]
    return [1]


def run(protocol: protocol_api.ProtocolContext):
    # Template placeholders (replace these during templating)
    REPLICATES = '[[REPLICATES]]'
    MEASUREMENT_VOLUME = '[[MEASUREMENT_VOLUME]]'

    # 1) Compute number of transfers
    replicates = _parse_replicates(REPLICATES)
    measurement_volume = _parse_float(MEASUREMENT_VOLUME, 200)

    # modules (slot 1)
    hs_mod = protocol.load_module('heaterShakerModuleV1', 1)
    hs_mod.open_labware_latch()
    deep_plate = hs_mod.load_labware('nest_96_wellplate_2ml_deep')
    hs_mod.close_labware_latch()

    # labware
    well_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 5)
    tiprack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 10)
    tiprack_300.set_offset(-0.1,1.4,0.0)
    # pipettes
    p300m = protocol.load_instrument('p300_multi_gen2', mount='left', tip_racks=[tiprack_300])
    protocol.load_instrument('p300_single_gen2', mount='right')

    # 2) Column-wise transfers using 8-channel pipette
    num_columns = replicates
    if num_columns <= 0:
        return

    source_columns = deep_plate.columns()[:num_columns]
    dest_columns = well_plate.columns()[:num_columns]

    source_locations = [col[0].bottom(2) for col in source_columns]

    p300m.transfer(
        measurement_volume,
        source_locations,
        dest_columns,
        mix_before=(3, 300),
        new_tip='always'
    )

    hs_mod.open_labware_latch()


