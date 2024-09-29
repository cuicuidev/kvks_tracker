from enum import Enum

from . import benchmark

class Scenarios(Enum):

    # CLICKING
    vt_pasu_rasp_novice = benchmark.Scenario(name="VT Pasu Rasp Novice", thresholds=(550,650,750,850))
    vt_pasu_rasp_intermediate = benchmark.Scenario(name="VT Pasu Rasp Intermediate", thresholds=(750,850,950,1050))
    vt_pasu_rasp_advanced = benchmark.Scenario(name="VT Pasu Rasp Advanced", thresholds=(940,1040,1120,1270))

    vt_bounceshot_novice = benchmark.Scenario(name="VT Bounceshot Novice", thresholds=(500,600,700,800))
    vt_bounceshot_intermediate = benchmark.Scenario(name="VT Bounceshot Intermediate", thresholds=(600,700,800,900))
    vt_bounceshot_advanced = benchmark.Scenario(name="VT Bounceshot Advanced", thresholds=(800,900,1000,1150))

    vt_1w6ts_rasp_novice = benchmark.Scenario(name="VT 1w6ts Rasp Novice", thresholds=(650,750,850,950))
    vt_1w5ts_rasp_intermediate = benchmark.Scenario(name="VT 1w5ts Rasp Intermediate", thresholds=(1000,1100,1200,1300))
    vt_1w3ts_rasp_advanced = benchmark.Scenario(name="VT 1w3ts Rasp Advanced", thresholds=(1280,1380,1460,1580))

    vt_multiclick_120_novice = benchmark.Scenario(name="VT Multiclick 120 Novice", thresholds=(1160,1260,1360,1460))
    vt_multiclick_120_intermediate = benchmark.Scenario(name="VT Multiclick 120 Intermediate", thresholds=(1360,1460,1560,1660))
    vt_multiclick_120_advanced = benchmark.Scenario(name="VT Multiclick 120 Advanced", thresholds=(1630,1770,1890,2000))

    # TRACKING
    vt_smoothbot_novice = benchmark.Scenario(name="VT Smoothbot Novice", thresholds=(2300,2500,3100,3500))
    vt_smoothbot_intermediate = benchmark.Scenario(name="VT Smoothbot Intermediate", thresholds=(3050,3450,3850,4250))
    vt_smoothbot_advanced = benchmark.Scenario(name="VT Smoothbot Advanced", thresholds=(3300,3600,3950,4300))
    
    vt_preciseorb_novice = benchmark.Scenario(name="VT PreciseOrb Novice", thresholds=(1300,1600,1900,2200))
    vt_preciseorb_intermediate = benchmark.Scenario(name="VT PreciseOrb Intermediate", thresholds=(1650,2050,2450,2850))
    vt_preciseorb_advanced = benchmark.Scenario(name="VT PreciseOrb Advanced", thresholds=(2500,2850,3250,3650))

    vt_plaza_novice = benchmark.Scenario(name="VT Plaza Novice", thresholds=(2150,2450,2850,3050))
    vt_plaza_intermediate = benchmark.Scenario(name="VT Plaza Intermediate", thresholds=(2680,2980,3280,3530))
    vt_plaza_advanced = benchmark.Scenario(name="VT Plaza Advanced", thresholds=(3275,3475,3600,3800))
    
    vt_air_novice = benchmark.Scenario(name="VT Air Novice", thresholds=(1900,2200,2500,2800))
    vt_air_intermediate = benchmark.Scenario(name="VT Air Intermediate", thresholds=(2450,2700,2950,3200))
    vt_air_advanced = benchmark.Scenario(name="VT Air IntermedAdvancediate", thresholds=(3000,3250,3500,3750))
    
    # SWITCHING
    vt_psalmts_novice = benchmark.Scenario(name="VT psalmTS Novice", thresholds=(620,690,760,830))
    vt_psalmts_intermediate = benchmark.Scenario(name="VT psalmTS Intermediate", thresholds=(810,880,950,1020))
    vt_psalmts_advanced = benchmark.Scenario(name="VT psalmTS Advanced", thresholds=(1080,1160,1200,1330))
    
    vt_skyts_novice = benchmark.Scenario(name="VT skyTS Novice", thresholds=(780,860,950,1040))
    vt_skyts_intermediate = benchmark.Scenario(name="VT skyTS Intermediate", thresholds=(1030,1130,1220,1300))
    vt_skyts_advanced = benchmark.Scenario(name="VT skyTS Advanced", thresholds=(1300,1430,1500,1600))
    
    vt_evats_novice = benchmark.Scenario(name="VT evaTS Novice", thresholds=(450,510,560,620))
    vt_evats_intermediate = benchmark.Scenario(name="VT evaTS Intermediate", thresholds=(550,600,650,700))
    vt_evats_advanced = benchmark.Scenario(name="VT evaTS Advanced", thresholds=(680,740,780,830))
    
    vt_bouncets_novice = benchmark.Scenario(name="VT bounceTS Novice", thresholds=(490,550,610,680))
    vt_bouncets_intermediate = benchmark.Scenario(name="VT bounceTS Intermediate", thresholds=(630,670,710,760))
    vt_bouncets_advanced = benchmark.Scenario(name="VT bounceTS Advanced", thresholds=(820,920,970,1050))
    
    # STRAFING
    vt_anglestrafe_intermediate = benchmark.Scenario(name="VT AngleStrafe Intermediate", thresholds=(740,830,920,1000))
    vt_anglestrafe_advanced = benchmark.Scenario(name="VT AngleStrafe Advanced", thresholds=(880,1020,1150,1230))
    
    vt_arcstrafe_intermediate = benchmark.Scenario(name="VT ArcStrafe Intermediate", thresholds=(660,750,850,940))
    vt_arcstrafe_advanced = benchmark.Scenario(name="VT ArcStrafe Advanced", thresholds=(940,1080,1150,1230))
    
    vt_patstrafe_intermediate = benchmark.Scenario(name="VT PatStrafe Intermediate", thresholds=(2260,2620,2800,3050))
    vt_patstrafe_advanced = benchmark.Scenario(name="VT PatStrafe Advanced", thresholds=(3050,3240,3400,3500))
    
    vt_airstrafe_intermediate = benchmark.Scenario(name="VT AirStrafe Intermediate", thresholds=(2800,3000,3200,3400))
    vt_airstrafe_advanced = benchmark.Scenario(name="VT AirStrafe Advanced", thresholds=(3400,3600,3700,3825))