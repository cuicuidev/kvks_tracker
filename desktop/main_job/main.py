import os
import glob

import datetime
from dateutil import parser

import json

import pandas as pd

import io
import pandas as pd

import requests

HOME = os.getenv("HOME")
POST_SCORE_ENDPOINT = "http://localhost:8000/tracking/score"
API_LAST_UPLOAD_ENDPOINT = "http://localhost:8000/tracking/latest"

def parse_csv(path):
    with open(path) as file:
        raw_csv = file.read()
    
    kills_section, misc_section, results_section, config_section = raw_csv.split("\n\n")
    kills_df = pd.read_csv(io.StringIO(kills_section))
    kills_df.columns = kills_df.columns.str.lower().str.replace(" ", "_").str.replace("#", "n")
    kills_df["timestamp"] = pd.to_datetime(kills_df["timestamp"]).apply(lambda x: x.isoformat()[:-3]).dt.tz_convert(tz=datetime.UTC)
    kills_df["ttk"] = kills_df["ttk"].str[:-1].astype(float)

    misc_df = pd.read_csv(io.StringIO(misc_section))
    misc_df.columns = misc_df.columns.str.lower().str.replace(" ", "_")
    misc_df = misc_df[["damage_possible"]]

    results_df = pd.read_csv(io.StringIO(results_section), header=None).set_index(0).T
    results_df.columns = results_df.columns.str[:-1].str.lower().str.replace(" ", "_")

    config_df = pd.read_csv(io.StringIO(config_section), header=None).set_index(0).T
    config_df.columns = config_df.columns.str[:-1].str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")

    score_df = pd.concat([results_df.reset_index(drop=True), config_df.reset_index(drop=True), misc_df], axis=1)

    score_df["n_kills"] = score_df["kills"].astype(float)
    score_df = score_df.drop("kills", axis=1)
    score_df["hide_gun"] = score_df["hide_gun"].map({"true" : True, "false" : False})

    numeric_cols = ["deaths", "fight_time", "time_remaining", "avg_ttk", "damage_done", "total_overshots", "damage_taken", "hit_count",
                    "miss_count", "midairs", "midaired", "directs", "directed", "reloads", "distance_traveled", "mbs_points", "score", "pause_count", "pause_duration",
                    "input_lag", "max_fps_config", "sens_increment", "horiz_sens", "vert_sens", "dpi", "fov", "crosshair_scale", "avg_fps", "resolution_scale"]
    
    score_df["challenge_start"] = pd.to_datetime(score_df["challenge_start"]).apply(lambda x: x.isoformat()[:-3]).dt.tz_convert(tz=datetime.UTC)
    for col in numeric_cols:
        score_df[col] = score_df[col].astype(float)

    score_dict = score_df.to_dict(orient="records")[0]
    kills_dict = kills_df.to_dict(orient="records")

    score_dict["kills"] = kills_dict

    return score_dict



def get_last_upload_time_from_api(headers):
    response = requests.get(API_LAST_UPLOAD_ENDPOINT, headers=headers)
    if response.status_code == 200:
        return parser.isoparse(response.json().get("created_at")).astimezone(datetime.UTC)
    else:
        return datetime.datetime.min.replace(tzinfo=datetime.UTC)

def post_data(json_data, headers):
    response = requests.post(POST_SCORE_ENDPOINT, json=json_data, headers=headers)
    return response

def walk_and_post_new_files(path: str, headers: dict[str, str], last_uploaded: datetime) -> None:
    data_files = glob.glob(os.path.join(path, "*.csv"))

    for filepath in data_files:
        file_modified_time = datetime.datetime.fromtimestamp(os.path.getctime(filepath)).replace(tzinfo=datetime.UTC)
        if file_modified_time > last_uploaded:
            print(f"Posting new file {filepath} (modified at {file_modified_time})...")
            json_data = parse_csv(filepath)
            response = post_data(json_data, headers)
            if response.status_code == 200:
                print(f"File {filepath} uploaded successfully.")

def main() -> None:
    config_path = os.path.join(HOME, ".kvkstracker/config.json")
    with open(config_path) as f:
        config = json.load(f)
        path = os.path.join(config.get("kvks_dir"), "FPSAimTrainer/stats")

    credentials_path = os.path.join(HOME, ".kvkstracker/credentials.json")
    with open(credentials_path) as f:
        access_token = json.load(f)["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    last_uploaded = get_last_upload_time_from_api(headers)
    print(f"Last uploaded timestamp: {last_uploaded}")

    walk_and_post_new_files(path, headers, last_uploaded)

if __name__ == "__main__":
    main()