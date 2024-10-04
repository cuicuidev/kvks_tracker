import io
import pandas as pd
from datetime import datetime
from pydantic import BaseModel
from typing import List

class Kill(BaseModel):
    kill_n: int
    timestamp: datetime
    bot: str
    weapon: str
    ttk: float
    shots: int
    hits: int
    accuracy: float
    damage_done: float
    damage_possible: float
    efficiency: float
    cheated: bool
    overshots: float

class KovaaksScore(BaseModel):
    kills: List[Kill]

    n_kills: int
    deaths: int
    fight_time: float
    time_remaining: float
    avg_ttk: float
    damage_done: float
    damage_possible: float
    total_overshots: int
    damage_taken: float
    hit_count: int
    miss_count: int
    midairs: int
    midaired: int
    directs: int
    directed: int
    reloads: int
    distance_traveled: float
    mbs_points: float
    score: float
    scenario: str
    hash: str
    game_version: str
    challenge_start: datetime
    pause_count: int
    pause_duration: float
    input_lag: float
    max_fps_config: float
    sens_scale: str
    sens_increment: float
    horiz_sens: float
    vert_sens: float
    dpi: int
    fov: int
    fovscale: str
    hide_gun: bool
    crosshair: str
    crosshair_scale: float
    crosshair_color: str
    resolution: str
    avg_fps: float
    resolution_scale: float

csv_file_path = 'D:\SteamLibrary\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats\VT 1w5ts Rasp Intermediate - Challenge - 2024.09.24-23.17.19 Stats.csv'

def parse_csv(path):
    with open(path) as file:
        raw_csv = file.read()
    
    kills_section, misc_section, results_section, config_section = raw_csv.split("\n\n")
    kills_df = pd.read_csv(io.StringIO(kills_section))
    kills_df.columns = kills_df.columns.str.lower().str.replace(" ", "_").str.replace("#", "n")
    kills_df["timestamp"] = pd.to_datetime(kills_df["timestamp"])
    kills_df["ttk"] = kills_df["ttk"].str[:-1].astype(float)

    misc_df = pd.read_csv(io.StringIO(misc_section))
    misc_df.columns = misc_df.columns.str.lower().str.replace(" ", "_")
    misc_df = misc_df[["damage_possible"]]

    results_df = pd.read_csv(io.StringIO(results_section), header=None).set_index(0).T
    results_df.columns = results_df.columns.str[:-1].str.lower().str.replace(" ", "_")

    config_df = pd.read_csv(io.StringIO(config_section), header=None).set_index(0).T
    config_df.columns = config_df.columns.str[:-1].str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")

    score_df = pd.concat([results_df, config_df, misc_df], axis=1)

    score_df["n_kills"] = score_df["kills"].astype(float)
    score_df = score_df.drop("kills", axis=1)
    score_df["hide_gun"] = score_df["hide_gun"].map({"true" : True, "false" : False})

    numeric_cols = ["deaths", "fight_time", "time_remaining", "avg_ttk", "damage_done", "total_overshots", "damage_taken", "hit_count",
                    "miss_count", "midairs", "midaired", "directs", "directed", "reloads", "distance_traveled", "mbs_points", "score", "pause_count", "pause_duration",
                    "input_lag", "max_fps_config", "sens_increment", "horiz_sens", "vert_sens", "dpi", "fov", "crosshair_scale", "avg_fps", "resolution_scale"]
    
    score_df["challenge_start"] = pd.to_datetime(score_df["challenge_start"])
    for col in numeric_cols:
        score_df[col] = score_df[col].astype(float)
    score_dict = score_df.to_dict(orient="records")[0]
    kills_dict = kills_df.to_dict(orient="records")
    kills_list = [Kill(**kill) for kill in kills_dict]

    score_dict["kills"] = kills_list

    score = KovaaksScore(**score_dict)
    return score



parse_csv(csv_file_path)