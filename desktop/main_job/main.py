import os
import glob
import io
import json
import zipfile
import warnings
import datetime
from dateutil import parser
import traceback
import logging
from logging.handlers import RotatingFileHandler

import requests
import pandas as pd

warnings.filterwarnings("ignore")

# GLOBALS

VERSION = "0.0.3"

HOME = os.getenv("HOME")
if HOME is None:
    HOME = os.path.expanduser("~")

POST_SCORE_ENDPOINT = "http://localhost:8000/tracking/score"
API_LAST_UPLOAD_ENDPOINT = "http://localhost:8000/tracking/latest"
LATEST_CLIENT_VERSION_ENDPOINT = "http://localhost:8000/download/latest"
LOGS_ENDPOINT = "http://localhost:8000/analytics/errors"

MIRRORS = [
    "http://localhost:8000/download/desktop_client.zip"
    ]

DOTFILES_DIR = os.path.join(HOME, ".kvkstracker")

# LOGGING
logger = logging.getLogger("kvks_tracker")
logger.setLevel(logging.INFO)

log_file = "kvks_tracker.log"
log_type = log_file.split(".")[0]

handler = RotatingFileHandler(log_file, maxBytes=1_048_576, backupCount=1)
handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s | [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)

def post_logs(log_string, error, headers):
    global LOGS_ENDPOINT, log_type

    try:
        response = requests.post(LOGS_ENDPOINT, json={"logs" : log_string, "error" : error, "type": log_type}, headers=headers)
        if response.status_code == 201:
            logger.info(f"Error logs sucessfully sent to {LOGS_ENDPOINT}")
        else:
            logger.error(f"HTTP error posting error logs to {LOGS_ENDPOINT}. Status code: {response.status_code}.")
    except requests.RequestException as e:
        logger.error(f"Client error posting error log to {LOGS_ENDPOINT}: {e}")

def log_exception(exc: type[BaseException], headers: dict[str, str]):
    with open(log_file) as file:
        log_string = file.read()
    exc_info = "".join(traceback.format_exception(None, exc, exc.__traceback__))
    logger.error(f"Exception occurred: {exc_info}")
    post_logs(log_string, exc_info, headers)


# MAIN LOGIC
def parse_csv(path, headers):
    global logger
    logger.info(f"Reading csv: {path}")

    try: 
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

    except Exception as e:
        log_exception(e, headers)

    return score_dict



def get_last_upload_time_from_api(headers: dict[str, str]):
    global logger, API_LAST_UPLOAD_ENDPOINT
    logger.info(f"Getting last uploaded datetime from {API_LAST_UPLOAD_ENDPOINT}")
    try:
        response = requests.get(API_LAST_UPLOAD_ENDPOINT, headers=headers)
        if response.status_code == 200:
            local_created_at = response.json().get("local_created_at")
            if local_created_at is not None:
                local_created_at = local_created_at.get("$date")
            return parser.isoparse(local_created_at).astimezone(datetime.UTC)
        else:
            return datetime.datetime.min.replace(tzinfo=datetime.UTC)
    except Exception as e:
        log_exception(e, headers)
        exit(code=1)

def post_data(json_data, headers):
    global logger, POST_SCORE_ENDPOINT
    logger.info(f"Posting data to {POST_SCORE_ENDPOINT}")
    try:
        response = requests.post(POST_SCORE_ENDPOINT, json=json_data, headers=headers)
        return response
    except Exception as e:
        log_exception(e, headers)

def walk_and_post_new_files(path: str, headers: dict[str, str], last_uploaded: datetime) -> None:
    global logger
    logger.info(f"Walking {path}")
    try: 
        data_files = glob.glob(os.path.join(path, "*.csv"))

        files_with_times = []

        for filepath in data_files:
            file_modified_time = datetime.datetime.fromtimestamp(os.path.getctime(filepath)).replace(tzinfo=datetime.UTC)
            files_with_times.append((filepath, file_modified_time))

        sorted_files = sorted(files_with_times, key=lambda x: x[1])

        for filepath, file_modified_time in sorted_files:
            if file_modified_time > last_uploaded:
                logger.info(f"Posting new file {filepath} (created at {file_modified_time})")
                json_data = parse_csv(filepath, headers)
                response = post_data(json_data, headers)
                if response.status_code == 200:
                    logger.info(f"File {filepath} uploaded successfully.")
    except Exception as e:
        log_exception(e, headers)

def check_for_updates(headers):
    global logger, LATEST_CLIENT_VERSION_ENDPOINT
    logger.info(f"Checking for updates at {LATEST_CLIENT_VERSION_ENDPOINT}")
    try:
        response = requests.get(LATEST_CLIENT_VERSION_ENDPOINT)
        upstream_client_version = response.json()["desktop_client_version"]
        local_client_version = VERSION
        if upstream_client_version > local_client_version:
            update(headers)
    except Exception as e:
        log_exception(e, headers)

def update(headers):
    global logger, DOTFILES_DIR, MIRRORS
    logger.info(f"Updating the desktop client")
    try:
        with open(os.path.join(DOTFILES_DIR, "config.json")) as file:
            install_dir = json.load(file)["install_dir"]
            app_file = os.path.join(install_dir, "app.zip")
            
        for mirror in MIRRORS:
            logger.info(f"Trying mirror {mirror}")
            try:
                with requests.get(mirror, stream=True) as response:
                    response.raise_for_status()
                    with open(app_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                break
            except requests.RequestException:
                pass
        else:
            raise Exception(f"None of the following mirrors worked: {MIRRORS}")

        with zipfile.ZipFile(app_file, 'r') as zip_ref:
            zip_ref.extractall(install_dir)

        os.remove(app_file)        
        os.startfile(os.path.join(install_dir, "kvks_tracker.exe"))
        exit(code=0)
    except Exception as e:
        log_exception(e, headers)
        exit(code=1)


def main() -> None:
    global logger, HOME
    logger.info("Initializing tracker")
    try:
        logger.info("Loading config.json")
        config_path = os.path.join(HOME, ".kvkstracker/config.json")
        with open(config_path) as f:
            config = json.load(f)
            path = os.path.join(config.get("kvks_dir"), "FPSAimTrainer/stats")

        logger.info("Loading credentials.json")
        credentials_path = os.path.join(HOME, ".kvkstracker/credentials.json")
        with open(credentials_path) as f:
            access_token = json.load(f)["access_token"]
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

        check_for_updates(headers)

        last_uploaded = get_last_upload_time_from_api(headers)
        logger.info(f"Last uploaded timestamp: {last_uploaded}")

        walk_and_post_new_files(path, headers, last_uploaded)
    except Exception as e:
        log_exception(e, headers)

if __name__ == "__main__":
    main()