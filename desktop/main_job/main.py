import os
import glob

import datetime
from dateutil import parser

import json

import io
import warnings

import pandas as pd

import requests

warnings.filterwarnings("ignore")

VERSION = "0.0.1"

HOME = os.getenv("HOME")
if HOME is None:
    HOME = os.path.expanduser("~")
POST_SCORE_ENDPOINT = "http://localhost:8000/tracking/score"
API_LAST_UPLOAD_ENDPOINT = "http://localhost:8000/tracking/latest"
LATEST_CLIENT_VERSION_ENDPOINT = "http://localhost:8000/download/latest"

def parse_csv(path):
    with open(path) as file:
        raw_csv = file.read()
    
    kills_section, misc_section, results_section, config_section = raw_csv.split("\n\n")
    kills_df = pd.read_csv(io.StringIO(kills_section))
    kills_df.columns = kills_df.columns.str.lower().str.replace(" ", "_").str.replace("#", "n")
    kills_df["timestamp"] = pd.to_datetime(kills_df["timestamp"]).dt.tz_localize(tz=datetime.UTC).apply(lambda x: x.isoformat())
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
    
    score_df["challenge_start"] = pd.to_datetime(score_df["challenge_start"]).dt.tz_localize(tz=datetime.UTC).apply(lambda x: x.isoformat())
    local_created_at = datetime.datetime.fromtimestamp(os.path.getctime(path)).replace(tzinfo=datetime.UTC).isoformat()
    for col in numeric_cols:
        score_df[col] = score_df[col].astype(float)

    score_dict = score_df.to_dict(orient="records")[0]
    kills_dict = kills_df.to_dict(orient="records")

    score_dict["kills"] = kills_dict
    score_dict["local_created_at"] = local_created_at

    def remove_nans(d):
        return {k: v for k, v in d.items() if not (isinstance(v, float) and pd.isna(v))}

    score_dict = remove_nans(score_dict)
    score_dict["kills"] = [remove_nans(kill) for kill in score_dict["kills"]]

    return score_dict



def get_last_upload_time_from_api(headers):
    response = requests.get(API_LAST_UPLOAD_ENDPOINT, headers=headers)
    if response.status_code == 200:
        local_created_at = response.json().get("local_created_at")
        if local_created_at is not None:
            local_created_at = local_created_at.get("$date")
        return parser.isoparse(local_created_at).astimezone(datetime.UTC)
    else:
        return datetime.datetime.min.replace(tzinfo=datetime.UTC)

def post_data(json_data, headers):
    response = requests.post(POST_SCORE_ENDPOINT, json=json_data, headers=headers)
    return response

def walk_and_post_new_files(path: str, headers: dict[str, str], last_uploaded: datetime) -> None:

    data_files = glob.glob(os.path.join(path, "*.csv"))

    files_with_times = []

    for filepath in data_files:
        file_modified_time = datetime.datetime.fromtimestamp(os.path.getctime(filepath)).replace(tzinfo=datetime.UTC)
        files_with_times.append((filepath, file_modified_time))

    sorted_files = sorted(files_with_times, key=lambda x: x[1])

    for filepath, file_modified_time in sorted_files:
        if file_modified_time > last_uploaded:
            print(f"Posting new file {filepath} (modified at {file_modified_time})...")
            json_data = parse_csv(filepath)
            response = post_data(json_data, headers)
            if response.status_code == 200:
                print(f"File {filepath} uploaded successfully.")

def check_for_updates():
    response = requests.get(LATEST_CLIENT_VERSION_ENDPOINT)
    upstream_client_version = response.json()["desktop_client_version"]
    local_client_version = VERSION
    if upstream_client_version > local_client_version:
        update()

def update():
    response = requests.get(LATEST_CLIENT_VERSION_ENDPOINT)

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

    check_for_updates()

    last_uploaded = get_last_upload_time_from_api(headers)
    print(f"Last uploaded timestamp: {last_uploaded}")

    walk_and_post_new_files(path, headers, last_uploaded)

if __name__ == "__main__":
    main()