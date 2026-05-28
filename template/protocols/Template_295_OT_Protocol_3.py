from opentrons import protocol_api

metadata = {
    'protocolName': 'Isotherm Step 3 - Binding',
    'author': 'S. Putz',
    'description': "Transfer ligand to filterplate and fill filterplate."
}
requirements = {"robotType": "OT-2", "apiLevel": "2.19"}

def run(protocol: protocol_api.ProtocolContext):
    # =====================
    # Modules
    # =====================
    hs_mod = protocol.load_module('heaterShakerModuleV1', '1')
    hs_mod.open_labware_latch()
    # Load custom filter plate onto Heater-Shaker (no adapter)
    try:
        filter_plate = hs_mod.load_labware('cytiva_96_filterwellplate_1ml')
    except Exception:
        protocol.comment('Custom labware cytiva_96_filterwellplate_1ml not found; using nest_96_wellplate_200ul_flat as simulation fallback.')
        filter_plate = hs_mod.load_labware('nest_96_wellplate_200ul_flat')
    hs_mod.close_labware_latch()

    # =====================
    # Labware
    # =====================
    tiprack_300_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tiprack_300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 7)
    tiprack_300_3 = protocol.load_labware('opentrons_96_tiprack_300ul', 10)
    tiprack_300_1.set_offset(-0.1,1.5,0.0)


    reservoir_3 = protocol.load_labware('nest_12_reservoir_15ml', 6)
    reservoir_2 = protocol.load_labware('nest_12_reservoir_15ml', 8)
    reservoir_1 = protocol.load_labware('nest_12_reservoir_15ml', 9)

    mixing_plate = protocol.load_labware('nest_96_wellplate_2ml_deep', 11)

    # =====================
    # Pipettes
    # =====================
    p300s = protocol.load_instrument('p300_single_gen2', mount='right', tip_racks=[tiprack_300_2])
    p300m = protocol.load_instrument('p300_multi_gen2', mount='left', tip_racks=[tiprack_300_1])


    # =====================
    # Parameters (templated placeholders with safe defaults for simulation)
    # =====================
    raw_replicates = '[[REPLICATES]]'
    raw_total_volume = '[[TOTAL_VOLUME]]'
    raw_ligand_concs = '[[LIGAND_CONCENTRATIONS]]'  # semicolon-separated string
    raw_num_ligands = '[[NUMBER_OF_LIGAND_CONCENTRATIONS]]'

    # Parse or set fallbacks when placeholders are not yet replaced
    try:
        replicates = int(raw_replicates)  # number of replicate columns per salt condition
    except Exception:
        replicates = 3

    try:
        total_volume = float(raw_total_volume)
    except Exception:
        total_volume = 100.0

    if '[[' in raw_ligand_concs:
        ligand_concs = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8']
    else:
        ligand_concs = [s.strip() for s in raw_ligand_concs.split(';') if s.strip()]

    try:
        number_of_ligand_concentrations = int(raw_num_ligands)
    except Exception:
        number_of_ligand_concentrations = len(ligand_concs) if len(ligand_concs) > 0 else 8

    vol_per_well = total_volume

    # Safety checks and info
    total_required_columns = 12
    if total_required_columns > 12:
        protocol.pause(f'Required columns ({total_required_columns}) exceed 96-well plate capacity (12 columns). Adjust 2 or 2.')

    # =====================
    # Step 1: Transfer ligands to filterplate
    # Use 8-channel pipette, tips from Slot 4, then return tips for reuse.
    # =====================

    p300m.pick_up_tip()
    for i in range(replicates):
        p300m.flow_rate.aspirate=400
        p300m.flow_rate.dispense=400
        p300m.transfer(total_volume, mixing_plate.columns()[i][0], filter_plate.columns()[i][0].bottom(z=16), mix_before=(15,300), new_tip='never')
        p300m.flow_rate.aspirate=100
        p300m.flow_rate.dispense=100
    p300m.return_tip()

    # =====================
    # Step 2: Transfer buffer to filterplate columns without ligand
    # Use 8-channel pipette, tips from Slot 4, then return tips for reuse.
    # =====================
    p300m.pick_up_tip()
    for i in range(replicates, 12):
        if i>=3:
            p300m.transfer(total_volume, reservoir_2.wells()[i], filter_plate.columns()[i][0].bottom(z=16), new_tip='never')
        else:
            p300m.transfer(total_volume, reservoir_2.wells()[3], filter_plate.columns()[i][0].bottom(z=16), new_tip='never')
    p300m.return_tip()

    protocol.comment('Protocol complete. Buffers and ligands transferred using templated parameters.')
