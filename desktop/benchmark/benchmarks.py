from enum import Enum

from . import core
from scenarios import Scenarios

class Benchmarks(Enum):

    # CLICKING  
    nov_dyn_cli = core.NoviceBenchmark(scenario_a=Scenarios.vt_pasu_rasp_novice, scenario_b=Scenarios.vt_bounceshot_novice)
    int_dyn_cli = core.IntermediateBenchmark(scenario_a=Scenarios.vt_pasu_rasp_intermediate, scenario_b=Scenarios.vt_bounceshot_intermediate)
    adv_dyn_cli = core.AdvancedBenchmark(scenario_a=Scenarios.vt_pasu_rasp_advanced, scenario_b=Scenarios.vt_bounceshot_advanced)

    nov_sta_cli = core.NoviceBenchmark(scenario_a=Scenarios.vt_1w6ts_rasp_novice, scenario_b=Scenarios.vt_multiclick_120_novice)
    int_sta_cli = core.IntermediateBenchmark(scenario_a=Scenarios.vt_1w5ts_rasp_intermediate, scenario_b=Scenarios.vt_multiclick_120_intermediate)
    adv_sta_cli = core.AdvancedBenchmark(scenario_a=Scenarios.vt_1w3ts_rasp_advanced, scenario_b=Scenarios.vt_multiclick_120_advanced)

    # TRACKING
    nov_smo_tra = core.NoviceBenchmark(scenario_a=Scenarios.vt_smoothbot_novice, scenario_b=Scenarios.vt_preciseorb_novice)
    int_smo_tra = core.IntermediateBenchmark(scenario_a=Scenarios.vt_smoothbot_intermediate, scenario_b=Scenarios.vt_preciseorb_intermediate)
    adv_smo_tra = core.AdvancedBenchmark(scenario_a=Scenarios.vt_smoothbot_advanced, scenario_b=Scenarios.vt_preciseorb_advanced)

    nov_rea_tra = core.NoviceBenchmark(scenario_a=Scenarios.vt_plaza_novice, scenario_b=Scenarios.vt_air_novice)
    int_rea_tra = core.IntermediateBenchmark(scenario_a=Scenarios.vt_plaza_intermediate, scenario_b=Scenarios.vt_air_intermediate)
    adv_rea_tra = core.AdvancedBenchmark(scenario_a=Scenarios.vt_plaza_advanced, scenario_b=Scenarios.vt_air_advanced)

    # SWITCHING
    nov_spe_ts = core.NoviceBenchmark(scenario_a=Scenarios.vt_psalmts_novice, scenario_b=Scenarios.vt_skyts_novice)
    int_spe_ts = core.IntermediateBenchmark(scenario_a=Scenarios.vt_psalmts_intermediate, scenario_b=Scenarios.vt_skyts_intermediate)
    adv_spe_ts = core.AdvancedBenchmark(scenario_a=Scenarios.vt_psalmts_advanced, scenario_b=Scenarios.vt_skyts_advanced)

    nov_eva_ts = core.NoviceBenchmark(scenario_a=Scenarios.vt_evats_novice, scenario_b=Scenarios.vt_bouncets_novice)
    int_eva_ts = core.IntermediateBenchmark(scenario_a=Scenarios.vt_evats_intermediate, scenario_b=Scenarios.vt_bouncets_intermediate)
    adv_eva_ts = core.AdvancedBenchmark(scenario_a=Scenarios.vt_evats_advanced, scenario_b=Scenarios.vt_bouncets_advanced)

    # STRAFING
    int_str_cli = core.IntermediateBenchmark(scenario_a=Scenarios.vt_anglestrafe_intermediate, scenario_b=Scenarios.vt_arcstrafe_intermediate)
    adv_str_cli = core.AdvancedBenchmark(scenario_a=Scenarios.vt_anglestrafe_advanced, scenario_b=Scenarios.vt_arcstrafe_advanced)

    int_str_tra = core.IntermediateBenchmark(scenario_a=Scenarios.vt_patstrafe_intermediate, scenario_b=Scenarios.vt_airstrafe_intermediate)
    adv_str_tra = core.AdvancedBenchmark(scenario_a=Scenarios.vt_patstrafe_advanced, scenario_b=Scenarios.vt_airstrafe_advanced)