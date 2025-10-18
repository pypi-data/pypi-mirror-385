import pandas as pd
from besos import eppy_funcs as ef
from besos.evaluator import EvaluatorEP
from besos.parameters import Parameter, GenericSelector
from besos.problem import EPProblem
from besos.objectives import MeterReader

import accim.sim.accis_single_idf_funcs as accis
import accim.parametric_and_optimisation.funcs_for_besos.param_accis as bf

building = ef.get_building('TestModel_onlyGeometryForVRFsystem_2zones_CalcVent_V2310.idf')

accis.addAccis(
    idf=building,
    ScriptType='vrf_mm',
    SupplyAirTempInputMethod='temperature difference',
    Output_keep_existing=False,
    Output_type='standard',
    Output_freqs=['hourly'],
    # EnergyPlus_version='9.4',
    TempCtrl='temperature',
    Output_gen_dataframe=True,
)

# gv = [i for i in building.idfobjects['EnergyManagementSystem:GlobalVariable']]

building.newidfobject(
    key='OUTPUT:METER',
    Key_Name='Electricity:Facility',
    Reporting_Frequency='RunPeriod'
)

building.newidfobject(
    key='OUTPUT:METER',
    Key_Name='Electricity:HVAC',
    Reporting_Frequency='RunPeriod'
)

# available_outputs = print_available_outputs_mod(building)

comfstand_range = [1, 2, 3]
cat_range = [1, 2, 3]
comfmod_range = [3]

samples = pd.DataFrame(columns=['ComfStand', 'CAT', 'ComfMod', 'CATcoolOffset', 'CATheatOffset'])

index_val = 0
for i in comfstand_range:
    # samples.loc[index_val, 'ComfStand'] = i
    for j in cat_range:
        # samples.loc[index_val, 'CAT'] = j
        for k in comfmod_range:
            samples.loc[index_val, 'ComfMod'] = k
            samples.loc[index_val, 'ComfStand'] = i
            samples.loc[index_val, 'CAT'] = j
            samples.loc[index_val, 'CATcoolOffset'] = 2
            samples.loc[index_val, 'CATheatOffset'] = 2

            index_val = index_val + 1

samples_filtered = bf.drop_invalid_param_combinations(samples)

##

parameters = [
    Parameter(
        name='ComfStand',
        # selector=GenericSelector(set=change_adaptive_coeff),
        selector=GenericSelector(set=bf.modify_ComfStand),
        # value_descriptors=CategoryParameter(options=comfstand_range)
    ),
    Parameter(
        name='CAT',
        # selector=GenericSelector(set=change_PMV_setpoints),
        selector=GenericSelector(set=bf.modify_CAT),
        # value_descriptors=CategoryParameter(options=cat_range)
    ),
    Parameter(
        name='ComfMod',
        # selector=GenericSelector(set=change_PMV_setpoints),
        selector=GenericSelector(set=bf.modify_ComfMod),
        # value_descriptors=CategoryParameter(options=comfmod_range)
    ),
    Parameter(
        name='CATcoolOffset',
        # selector=GenericSelector(set=change_PMV_setpoints),
        selector=GenericSelector(set=bf.modify_CATcoolOffset),
        # value_descriptors=CategoryParameter(options=comfmod_range)
    ),
    Parameter(
        name='CATheatOffset',
        # selector=GenericSelector(set=change_PMV_setpoints),
        selector=GenericSelector(set=bf.modify_CATheatOffset),
        # value_descriptors=CategoryParameter(options=comfmod_range)
    ),

]

# Objectives

# objs_comfhours = []
# for i in range(len(available_outputs.variablereaderlist)):
#     if 'hour' in available_outputs.variablereaderlist[i][1].lower():
#         objs_comfhours.append(
#             VariableReader(
#                 key_value=available_outputs.variablereaderlist[i][0],
#                 variable_name=available_outputs.variablereaderlist[i][1],
#                 frequency=available_outputs.variablereaderlist[i][2],
#                 name=available_outputs.variablereaderlist[i][1]
#             )
#         )

#

objectives = [
    MeterReader("Electricity:Facility", name="Total Electricity Usage"),
    MeterReader("Electricity:HVAC", name="HVAC Electricity Usage"),

    # VariableReader(
    #     key_value='Whole Building',
    #     variable_name='Facility Total HVAC Electricity Demand Rate',
    #     frequency='Hourly',
    #     name='HVAC Electricity usage'
    # )
]

problem = EPProblem(
    inputs=parameters,
    # outputs=objectives+objs_comfhours
    outputs=objectives
)


evaluator = EvaluatorEP(
    problem=problem,
    building=building,
    out_dir='outdir'
)

outputs = evaluator.df_apply(
    samples_filtered,
    keep_input=True,
    keep_dirs=True,
    # out_dir='outdir',
    processes=5
)

# outputs_mod = outputs
# outputs_mod['energy ratio'] = outputs_mod['HVAC Electricity Usage'] / outputs_mod['Total Electricity Usage']


# generated_buildings = [evaluator.generate_building(df=samples_short, index=i, file_name=f'short_sample_row_{i}') for i in range(5)]
evaluator.generate_building(df=samples, index=0, file_name='num_0')
evaluator.generate_building(df=samples, index=1, file_name='num_1')
evaluator.generate_building(df=samples, index=2, file_name='num_2')
# evaluator.generate_building(df=samples_short, index=3, file_name='num_3')
# evaluator.generate_building(df=samples_short, index=4, file_name='num_4')
