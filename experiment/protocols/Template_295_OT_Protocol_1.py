from opentrons import protocol_api
import math

metadata = {
    'protocolName': 'Isotherm Step 1 - Dilution',
    'author': 'S. Putz',
    'description': "Dilution of Ligand"
}
requirements = {"robotType": "OT-2", "apiLevel": "2.19"}

def run(protocol: protocol_api.ProtocolContext):
    # -----------------------
    # Placeholder parameters (templated)
    # -----------------------
    PLACEHOLDERS = {
        'REPLICATES': '3',
        'TOTAL_VOLUME': '500',  # per-replicate volume used downstream
        'LIGAND_CONCENTRATIONS': '20.0; 16.0; 12.0; 8.0; 4.0; 2.0; 1.0; 0.0',  # semicolon-separated string
        'LIGAND_STOCK_CONCENTRATION': '20',
        'NUMBER_OF_LIGAND_CONCENTRATIONS': '8'
    }

    # Helper parsing utilities to allow simulation if placeholders are not replaced
    def is_placeholder(val):
        return isinstance(val, str) and val.strip().startswith('[[') and val.strip().endswith(']]')

    def parse_float(val, default):
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            if is_placeholder(val):
                return float(default)
            try:
                return float(val)
            except Exception:
                return float(default)
        return float(default)

    def parse_int(val, default):
        if isinstance(val, int):
            return int(val)
        if isinstance(val, float):
            return int(val)
        if isinstance(val, str):
            if is_placeholder(val):
                return int(default)
            try:
                return int(val)
            except Exception:
                try:
                    return int(float(val))
                except Exception:
                    return int(default)
        return int(default)

    def parse_float_list(val, default_list):
        if isinstance(val, str) and not is_placeholder(val):
            parts = [p.strip() for p in val.split(';') if p.strip()]
            try:
                return [float(p) for p in parts]
            except Exception:
                return list(default_list)
        # if placeholder or non-string, return default
        return list(default_list)

    # Defaults for simulation if placeholders are not replaced
    DEFAULTS = {
        'REPLICATES': 3,
        'TOTAL_VOLUME': 500.0,  # uL, per-replicate volume
        'LIGAND_CONCENTRATIONS': [0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0],  # example uM (8 values)
        'LIGAND_STOCK_CONCENTRATION': 150.0,  # example uM
        'NUMBER_OF_LIGAND_CONCENTRATIONS': 8,
    }

    REPLICATES = parse_int(PLACEHOLDERS['REPLICATES'], DEFAULTS['REPLICATES'])
    TOTAL_VOLUME = parse_float(PLACEHOLDERS['TOTAL_VOLUME'], DEFAULTS['TOTAL_VOLUME'])
    LIG_CONCS = parse_float_list(PLACEHOLDERS['LIGAND_CONCENTRATIONS'], DEFAULTS['LIGAND_CONCENTRATIONS'])
    LIG_STOCK = parse_float(PLACEHOLDERS['LIGAND_STOCK_CONCENTRATION'], DEFAULTS['LIGAND_STOCK_CONCENTRATION'])
    NUM_LIG = parse_int(PLACEHOLDERS['NUMBER_OF_LIGAND_CONCENTRATIONS'], len(LIG_CONCS))

    # sort concentrations ascending as required
    LIG_CONCS = sorted(LIG_CONCS)[:min(NUM_LIG, 8)]  # up to 8 rows (A-H)

    if REPLICATES < 1 or REPLICATES > 12:
        raise RuntimeError('REPLICATES must be between 1 and 12 (mixing plate has 12 columns).')

    # -----------------------
    # Labware
    # -----------------------
    # Tip racks
    tiprack_300_slot4 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tiprack_300_slot7 = protocol.load_labware('opentrons_96_tiprack_300ul', 7)
    tiprack_300_slot10 = protocol.load_labware('opentrons_96_tiprack_300ul', 10)

    # Custom 96 filter-well plate (Slot 1)
    try:
        filter_plate = protocol.load_labware('cytiva_96_filterwellplate_1ml', 1)
    except Exception:
        protocol.comment('WARNING: Custom labware cytiva_96_filterwellplate_1ml not found. Using opentrons_96_wellplate_200ul_pcr_full_skirt as placeholder for simulation.')
        filter_plate = protocol.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt', 1)

    # Reservoirs
    reservoir3 = protocol.load_labware('nest_12_reservoir_15ml', 6)   # wash buffer
    reservoir1 = protocol.load_labware('nest_12_reservoir_15ml', 8)   # ligand, binding buffer
    reservoir2 = protocol.load_labware('nest_12_reservoir_15ml', 9)   # equilibration buffer

    # Mixing plate (96 deep well, 2 mL)
    mixing_plate = protocol.load_labware('nest_96_wellplate_2ml_deep', 11)

    res1_wells = reservoir1.wells()
    ligand_stock_high = res1_wells[0]      # Well 0: high ligand stock
    ligand_stock_low = res1_wells[1]       # Well 1: low ligand stock (1/10)
    binding_buffer1 = res1_wells[2]        # Well 2: binding buffer
    binding_buffer2 = res1_wells[3]        # Well 3: binding buffer
    # -----------------------
    # Pipettes
    # -----------------------
    # Use only Slot 10 tips for multi, Slot 10 for single as specified
    p300m = protocol.load_instrument('p300_multi_gen2', mount='left', tip_racks=[tiprack_300_slot10])
    p300s = protocol.load_instrument('p300_single_gen2', mount='right', tip_racks=[tiprack_300_slot10])

    # -----------------------
    # Helper for mixing target wells after additions
    # -----------------------
    def mix_single_in_place(well, total_volume_ul):
        mix_vol = 300
        p300s.mix(15, mix_vol, well)

    # -----------------------
    # Step 1: Ligand dilutions (1x) in mixing plate (slot 11)
    # One column per replicate -> REPLICATES columns, each containing the full
    # ascending dilution series A (lowest) .. H (highest). This keeps per-well
    # volume close to TOTAL_VOLUME so the 300 uL mix step is effective.
    # -----------------------

    per_well_total = TOTAL_VOLUME * 1.2  # single-replicate volume + 20 % dead-volume overhead

    columns = mixing_plate.columns()  # 12 columns, each is a list [A..H]
    for col_idx in range(REPLICATES):
        col_wells = columns[col_idx]  # 8 wells A..H in this column
        target_rows = col_wells[:len(LIG_CONCS)]
        # For each row (ligand concentration), compute stock and buffer volumes
        for row_idx, c_lig in enumerate(LIG_CONCS):
            desired_1x = c_lig
            if LIG_STOCK <= 0:
                raise RuntimeError('LIGAND_STOCK_CONCENTRATION must be > 0')
            # compute using high stock first
            v_stock_high = per_well_total * (desired_1x / LIG_STOCK)
            use_low_stock = v_stock_high < 20.0  # threshold 20 uL
            if use_low_stock:
                stock_conc = LIG_STOCK / 10.0
                ligand_source = ligand_stock_low
            else:
                stock_conc = LIG_STOCK
                ligand_source = ligand_stock_high
            v_stock = per_well_total * (desired_1x / stock_conc)
            v_buffer = max(0.0, per_well_total - v_stock)

            dest = target_rows[row_idx]
            # Add buffer first with a fresh tip
            if v_buffer > 0:
                # Ensure adequate buffer in current source; advance as needed
                # Use one tip per destination to avoid contaminating buffer pool
                src = binding_buffer1
                p300s.pick_up_tip()
                p300s.transfer(v_buffer, src, [dest], new_tip='never')
                p300s.drop_tip()

            # Add ligand stock with a fresh tip, then mix
            if v_stock > 0:
                src = ligand_source
                p300s.pick_up_tip()
                p300s.transfer(v_stock, src, [dest], new_tip='never')
                # Gentle mix after additions with same tip
                p300s.flow_rate.aspirate=400
                p300s.flow_rate.dispense=400
                mix_single_in_place(dest, per_well_total)
                p300s.drop_tip()
                p300s.flow_rate.aspirate=100
                p300s.flow_rate.dispense=100

    # Protocol complete