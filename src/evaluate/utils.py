

from playwright.async_api import Page


import re

import json5
from .step_score import *
from .task_score import *


def read_file(file_path):
    """Read labeled data"""
    return_list = []
    with open(file_path, encoding='utf-8') as f:
        test_data = json5.load(f)
    for task in test_data:
        task_name = task["task"]
        evaluation_data = task["evaluation"]
        reference_task_length = task["reference_task_length"]
        task_name_id = task["index"]
        reference_evaluate_steps = []
        for i, evaluation in enumerate(evaluation_data):
            match_function = evaluation["match_function_name"]
            if "url" in match_function:
                try:
                    key = evaluation["content"]["key"]
                    reference_answer = evaluation["content"]["reference_answer"]
                    reference_evaluate_steps.append({"match_function": match_function,
                                                     "key": key, "reference_answer": reference_answer, "score": 0})
                except:
                    print(
                        f"url error in task {task_name_id}, step {i}, match_function: {match_function}")
                    exit(1)
            elif "element_path" in match_function:
                try:
                    reference_answer = evaluation["content"]["reference_answer"]
                    method = evaluation["method"]
                    netloc = evaluation["content"]["netloc"]
                    reference_evaluate_steps.append({"match_function": match_function, "method": method,
                                                     "reference_answer": reference_answer, "netloc": netloc,
                                                     "score": 0})
                except:
                    print(
                        f"element_path error in task {task_name_id}, step {i}, match_function: {match_function}")
                    exit(1)
            elif "element_value" in match_function:
                try:
                    reference_answer = evaluation["content"]["reference_answer"]
                    netloc = evaluation["content"]["netloc"]
                    if "path" in evaluation["content"].keys():
                        path = evaluation["content"]["path"]
                        reference_evaluate_steps.append({"match_function": match_function,
                                                         "reference_answer": reference_answer, "netloc": netloc,
                                                         "path": path, "score": 0})
                    else:
                        reference_evaluate_steps.append({"match_function": match_function,
                                                         "reference_answer": reference_answer, "netloc": netloc,
                                                         "score": 0})
                except:
                    print(
                        f"element_value error in task {task_name_id}, step {i}, match_function: {match_function}")
                    exit(1)
        return_list.append(
            [task_name, task_name_id, reference_task_length, reference_evaluate_steps])

    return return_list


def get_netloc(url: str) -> str:
    """Extract the domain name, for example, extract 'zhihu' from 'zhihu.com', extract 'google' from 'www.google.com.hk' """
    url = urlparse(url)
    try:
        if url.netloc.startswith("www"):
            netloc = re.findall(".*?\.(.*?)\..*?", url.netloc)[0]
        else:
            netloc = re.findall("(.*?)\..*?", url.netloc)[0]
    except:
        netloc = ""
    return netloc


# async def step_evaluate(page: Page, evaluate_steps=[], input_path=None, element_value=None):
#     """Evaluate step score"""
#     step_score = 0
#     match_result = []
#     for evaluate in evaluate_steps:
#         if evaluate["score"] != 1:
#             match_function = evaluate["match_function"]
#             if match_function == "url_exactly_match":
#                 score = URLEvaluator.url_exact_match(
#                     page.url, evaluate["reference_answer"], evaluate["key"])
#             elif match_function == "url_included_match":
#                 score = URLEvaluator.url_include_match(
#                     page.url, evaluate["reference_answer"], evaluate["key"])
#             elif match_function == "url_semantic_match":
#                 score = await URLEvaluator.url_semantic_match(
#                     page.url, evaluate["reference_answer"], evaluate["key"])
#                 # print(score, "url_semantic_match")
#             elif match_function == "element_path_exactly_match":
#                 input_netloc = get_netloc(page.url)
#                 method = evaluate["method"]
#                 score = ElementEvaluator.path_exact_match(
#                     input_path, evaluate["reference_answer"], method, await page.content(), input_netloc,
#                     evaluate["netloc"])
#                 # print(score, "path_exact_match:", input_path,
#                 #       "***", evaluate["reference_answer"])
#             elif match_function == "element_path_included_match":
#                 pass
#                 # * Temporarily not doing

#             elif match_function == "element_value_exactly_match":
#                 if input_path is not None and element_value is not None:
#                     input_netloc = get_netloc(page.url)

#                     # print(element_value)
#                     # print(await page.locator(input_path).input_value())
#                     if "path" in evaluate.keys():
#                         path_score = ElementEvaluator.path_exact_match(input_path, evaluate["path"], "selector",
#                                                                        await page.content(), input_netloc,
#                                                                        evaluate["netloc"])
#                         if path_score == 0:
#                             # print("Path mismatch in value evaluation")
#                             score = 0
#                         else:
#                             score = ElementEvaluator.element_value_exact_match(
#                                 element_value, evaluate["reference_answer"], input_netloc, evaluate["netloc"])
#                     else:
#                         score = ElementEvaluator.element_value_exact_match(
#                             element_value, evaluate["reference_answer"], input_netloc, evaluate["netloc"])
#                     # print(score, "element_value_exactly_match",
#                     #       element_value, "*", evaluate["reference_answer"])
#                 else:
#                     score = 0
#             elif match_function == "element_value_included_match":
#                 if input_path is not None and element_value is not None:
#                     input_netloc = get_netloc(page.url)
#                     if "path" in evaluate.keys():
#                         path_score = ElementEvaluator.path_exact_match(input_path, evaluate["path"], "selector",
#                                                                        await page.content(), input_netloc,
#                                                                        evaluate["netloc"])
#                         if path_score == 0:
#                             # print("Path mismatch in value evaluation")
#                             score = 0
#                         else:
#                             score = ElementEvaluator.element_value_include_match(
#                                 element_value, evaluate["reference_answer"], input_netloc, evaluate["netloc"])
#                     else:
#                         score = ElementEvaluator.element_value_include_match(
#                             element_value, evaluate["reference_answer"], input_netloc, evaluate["netloc"])
#                     # print(score, "element_value_included_match",
#                     #       element_value, "*", evaluate["reference_answer"])
#                 else:
#                     score = 0
#             elif match_function == "element_value_semantic_match":
#                 if input_path is not None and element_value is not None:
#                     input_netloc = get_netloc(page.url)

#                     if len(element_value) > 0:
#                         if "path" in evaluate.keys():
#                             path_score = ElementEvaluator.path_exact_match(input_path, evaluate["path"], "selector",
#                                                                            await page.content(), input_netloc,
#                                                                            evaluate["netloc"])
#                             if path_score == 0:
#                                 # print("Path mismatch in value evaluation")
#                                 score = 0
#                             else:
#                                 score = await ElementEvaluator.element_value_semantic_match(
#                                     element_value, evaluate["reference_answer"], input_netloc, evaluate["netloc"])
#                         else:
#                             score = await ElementEvaluator.element_value_semantic_match(
#                                 element_value, evaluate["reference_answer"], input_netloc, evaluate["netloc"])
#                         # print(score, "element_value_semantic_match",
#                         #       element_value, "*", evaluate["reference_answer"])
#                 else:
#                     score = 0
#             elif match_function == "text_exact_match":
#                 pass  # TODO
#             elif match_function == "text_include_match":
#                 pass
#             elif match_function == "text_semantic_match":
#                 pass

#             evaluate["score"] = max(evaluate["score"], score)
#         if evaluate["score"] >= 1:
#             match_result.append(
#                 {evaluate["match_function"]: evaluate["reference_answer"]})
#         step_score += evaluate["score"]

#     return evaluate_steps, match_result


async def step_evaluate(page: Page, evaluate_steps=[], input_path=None, element_value=None):
    """Evaluate step score"""
    step_score = 0
    match_result = []
    for evaluate in evaluate_steps:
        if evaluate["score"] != 1:
            match_function = evaluate["match_function"]
            if match_function == "url_exactly_match":
                score = URLEvaluator.url_exact_match(
                    page.url, evaluate["reference_answer"], evaluate["key"])
            elif match_function == "url_included_match":
                score = URLEvaluator.url_include_match(
                    page.url, evaluate["reference_answer"], evaluate["key"])
            elif match_function == "url_semantic_match":
                score = await URLEvaluator.url_semantic_match(
                    page.url, evaluate["reference_answer"], evaluate["key"])

            elif match_function == "element_path_exactly_match":
                input_netloc = get_netloc(page.url)
                method = evaluate["method"]
                score = await ElementEvaluator.path_exact_match(
                    input_path, evaluate["reference_answer"], method, page, input_netloc,
                    evaluate["netloc"])

            elif match_function == "element_path_included_match":
                pass

            elif match_function == "element_value_exactly_match":
                if input_path is not None and element_value is not None:
                    input_netloc = get_netloc(page.url)

                    if "path" in evaluate.keys():
                        path_score = await ElementEvaluator.path_exact_match(input_path, evaluate["path"], "selector",
                                                                             page, input_netloc,
                                                                             evaluate["netloc"])
                        if path_score == 0:
                            score = 0
                        else:
                            score = ElementEvaluator.element_value_exact_match(
                                element_value, evaluate["reference_answer"], input_netloc, evaluate["netloc"])
                    else:
                        score = ElementEvaluator.element_value_exact_match(
                            element_value, evaluate["reference_answer"], input_netloc, evaluate["netloc"])

                else:
                    score = 0
            elif match_function == "element_value_included_match":
                if input_path is not None and element_value is not None:
                    input_netloc = get_netloc(page.url)
                    if "path" in evaluate.keys():
                        path_score = await ElementEvaluator.path_exact_match(input_path, evaluate["path"], "selector",
                                                                             page, input_netloc,
                                                                             evaluate["netloc"])
                        if path_score == 0:
                            score = 0
                        else:
                            score = ElementEvaluator.element_value_include_match(
                                element_value, evaluate["reference_answer"], input_netloc, evaluate["netloc"])
                    else:
                        score = ElementEvaluator.element_value_include_match(
                            element_value, evaluate["reference_answer"], input_netloc, evaluate["netloc"])
                else:
                    score = 0
            elif match_function == "element_value_semantic_match":
                if input_path is not None and element_value is not None:
                    input_netloc = get_netloc(page.url)

                    if len(element_value) > 0:
                        if "path" in evaluate.keys():
                            path_score = await ElementEvaluator.path_exact_match(input_path, evaluate["path"], "selector",
                                                                                 page, input_netloc,
                                                                                 evaluate["netloc"])
                            if path_score == 0:
                                # print("Path mismatch in value evaluation")
                                score = 0
                            else:
                                score = await ElementEvaluator.element_value_semantic_match(
                                    element_value, evaluate["reference_answer"], input_netloc, evaluate["netloc"])
                        else:
                            score = await ElementEvaluator.element_value_semantic_match(
                                element_value, evaluate["reference_answer"], input_netloc, evaluate["netloc"])
                        # print(score, "element_value_semantic_match",
                        #       element_value, "*", evaluate["reference_answer"])
                else:
                    score = 0
            elif match_function == "text_exact_match":
                pass  # TODO
            elif match_function == "text_include_match":
                pass
            elif match_function == "text_semantic_match":
                pass

            evaluate["score"] = max(evaluate["score"], score)
        if evaluate["score"] >= 1:
            match_result.append(
                {evaluate["match_function"]: evaluate["reference_answer"]})
        step_score += evaluate["score"]

    return evaluate_steps, match_result


def extract_css_selector(selector_str):
    selector_str = selector_str.replace(" ", "")
    match = re.search(r'selector=\'(\w+)\s*>>\s*nth=(\d+)', selector_str)
    if match:
        element_type = match.group(1)
        nth_value = int(match.group(2)) + 1
        nth_value = str(nth_value)
        return element_type + ":nth-of-type(" + nth_value + ")"
    else:
        return None


def extract_element_value(html_content, selector):
    soup = BeautifulSoup(html_content, 'html.parser')
    element = soup.select_one(selector)
    element_value = ""
    if element:
        element_value = element.text
    return element_value


async def evaluate_with_webcanvas(page, selector, target_value, evaluate_steps, reference_evaluate_steps):
    element_value = ""
    if target_value:
        element_value = target_value
    else:
        element_value = await selector.text_content()
    evaluate_steps, match_result = await step_evaluate(page=page, evaluate_steps=evaluate_steps,
                                                       input_path=selector, element_value=element_value)
    total_step_score = 0
    for evaluate in evaluate_steps:
        total_step_score += evaluate["score"]
    step_score_rate = str(
        total_step_score) + " / " + str(len(reference_evaluate_steps))
    task_finished = False
    if total_step_score == len(reference_evaluate_steps):
        task_finished = True
    return evaluate_steps, step_score_rate, match_result, task_finished
