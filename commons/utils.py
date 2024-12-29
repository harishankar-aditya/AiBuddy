import os
import ast
import json
import logging
import numpy as np
import re


def convert_to_standard_types(response):
    """
    Recursively converts the values in a dictionary to standard Python types.

    Args:
        response (dict): The dictionary to be converted.

    Returns:
        dict: The dictionary with values converted to standard Python types.
    """
    if isinstance(response, dict):
        for key, value in response.items():
            if isinstance(value, np.integer):
                response[key] = int(value)
            elif isinstance(value, np.floating):
                response[key] = float(value)
            elif isinstance(value, np.ndarray):
                response[key] = value.tolist()
            elif isinstance(value, (list, tuple)):
                response[key] = [convert_to_standard_types(item) for item in value]
            elif isinstance(value, dict):
                response[key] = convert_to_standard_types(value)
    return response


def handling_gpt_ouput(gpt_response):
    """
    Attempts to parse the provided GPT response as a list or dictionary, and if that fails,
    extracts the content between the first and last curly braces and evaluates it as a JSON response.

    Args:
        gpt_response (str): The GPT response to be parsed.

    Returns:
        dict: The parsed GPT response as a dictionary, or an empty dictionary if the parsing fails.
    """
    output = {}
    try:
        try:
            # Try parsing the variable as a list
            parsed_variable = ast.literal_eval(gpt_response)
            logging.info("GPT response parsed successfully.")
            if isinstance(parsed_variable, dict):
                # If it's already a list, return it as is
                logging.info("GPT response is already a JSON")
                output = parsed_variable
        except (ValueError, SyntaxError):
            pass

        # Extract content between first and last curly braces
        start_index = gpt_response.find("{")
        end_index = gpt_response.rfind("}")

        if start_index != -1 and end_index != -1:
            extracted_content = gpt_response[start_index : end_index + 1]
            logging.info(
                f"Extracted GPT response as JSON in string format: {extracted_content}"
            )
            output = eval(extracted_content)
            logging.info(
                f"Evaluated(eval()) string JSON response inside list: {output}"
            )
    except Exception as err:
        logging.exception(
            f"handling_gpt_output_failed() - returning empty list :{gpt_response}"
        )
    finally:
        return output
    