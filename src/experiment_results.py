import pandas as pd
from pandas import json_normalize
import json5
import json
import re
import os
import argparse
import toml


def merge_all_result(input_path):
    all_task_id = os.listdir(input_path)
    all_task_path = [item for item in all_task_id if os.path.isdir(
        os.path.join(input_path, item))]
    out_file_path = input_path + "/result"
    task_list = []
    for simgle_task in all_task_path:
        simgle_task_result_path = input_path + "/" + simgle_task + "/result.json"
        if os.path.isfile(simgle_task_result_path):
            with open(simgle_task_result_path) as f:
                simgle_task_result = json.load(f)
            task_list.append(simgle_task_result)
    task_list = sorted(task_list, key=lambda x: x['task_index'])
    if not os.path.exists(out_file_path):
        os.makedirs(out_file_path)
    out_json_file_path = out_file_path + '/out.json'
    with open(out_json_file_path, 'w') as json_file:
        json.dump(task_list, json_file)
    return out_file_path


def score_rate(score):
    first, second = score.split("/")
    return float(first) / float(second)


def read_result(file_path):
    with open(file_path) as f:
        data = json.load(f)
    last_action_result_list = []
    for items in data:
        data_dic = {}
        data_dic["task_id"] = items["task_id"]
        data_dic["task_name"] = items["confirmed_task"]
        data_dic["action_history"] = items["action_history"]
        data_dic["steps"] = items["num_step"]
        data_dic["task_score"] = items["step_score"][-1]
        data_dic["task_score_rate"] = score_rate(items["step_score"][-1])
        data_dic["reward_count"] = len(items["evaluation"])
        last_action_result_list.append(data_dic)
    return last_action_result_list


def calculate_total_score(scores):
    molecular_sum = sum(float(x.split('/')[0]) for x in scores)
    denominator_sum = sum(float(x.split('/')[1]) for x in scores)
    final_score = molecular_sum / denominator_sum
    return final_score


def evaluate(file_path):
    input_file_path = file_path + "/out.json"
    result_file_path = file_path + "/experiment_result.json"
    all_data = read_result(input_file_path)
    df = pd.DataFrame(all_data)
    df["step_score"] = df["task_score"].apply(lambda x: float(x.split("/")[0]))
    df["step_score"] = df["task_score"].apply(lambda x: float(x.split("/")[0]))
    df["efficiency_score"] = df["step_score"] / df["steps"]
    df["score_df_1"] = df["task_score"].apply(lambda x: float(
        x.split("/")[1]) - float(x.split("/")[0]) == 1.0)

    df["task_finish"] = df["task_score"].apply(lambda x: float(
        x.split("/")[1]) - float(x.split("/")[0]) == 0)

    df_evaluate = df[["task_name", "steps", "task_score", "task_finish", "task_score_rate",
                      "step_score", "efficiency_score", "score_df_1"]]

    step_score_rate = calculate_total_score(df_evaluate['task_score'])

    completion_rate = df_evaluate[df_evaluate["task_finish"]
                                  == True].shape[0] / df_evaluate.shape[0]

    score_df_1 = df_evaluate[df_evaluate["score_df_1"]
                             == True].shape[0] / df_evaluate.shape[0]

    average_step_score_rate = df_evaluate["task_score_rate"].mean()
    average_efficiency_score = df_evaluate["efficiency_score"].mean()

    result_dict = {}
    result_dict["task_counts"] = df_evaluate.shape[0]
    result_dict["average_step_score_rate"] = average_step_score_rate
    result_dict["average_efficiency_score"] = average_efficiency_score
    result_dict["step_score_rate"] = step_score_rate
    result_dict["completion_rate"] = completion_rate
    result_dict["score_df_1"] = score_df_1

    with open(result_file_path, 'w') as json_file:
        json.dump(result_dict, json_file)


def get_evaluate_result(input_result_path):
    out_file_path = merge_all_result(input_result_path)
    evaluate(file_path=out_file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config_path", help="Path to the TOML configuration file.", type=str, metavar='config',
                        default=f"{os.path.join('config', 'demo_mode.toml')}")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config = None
    try:
        with open(os.path.join(base_dir, args.config_path) if not os.path.isabs(args.config_path) else args.config_path,
                  'r') as toml_config_file:
            config = toml.load(toml_config_file)
            print(
                f"Configuration File Loaded - {os.path.join(base_dir, args.config_path)}")
    except FileNotFoundError:
        print(f"Error: File '{args.config_path}' not found.")
    except toml.TomlDecodeError:
        print(f"Error: File '{args.config_path}' is not a valid TOML file.")

    out_file_path = config["basic"]["save_file_dir"]

    get_evaluate_result(out_file_path)
