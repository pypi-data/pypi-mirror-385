from __future__ import annotations
import logging
import random
import json
from typing import Tuple, Callable, Union, List, Dict, Any

logger = logging.getLogger(__name__)


def generate_random_number(
    lower_bound: float,
    upper_bound: float,
    generate_integers: bool = False
) -> str:
    """
    Generate a random number within the specified bounds.
    
    Parameters
    ----------
    lower_bound : float
        The lower bound (inclusive)
    upper_bound : float  
        The upper bound (inclusive for integers, exclusive for floats)
    generate_integers : bool
        If True, generate integers; if False, generate floating point numbers
        
    Returns
    -------
    str
        A random number of the specified type within the given bounds, formatted as a string
    """
    logger.info(f"Generating random number between {lower_bound} and {upper_bound}, integers: {generate_integers}")
    
    if lower_bound > upper_bound:
        raise ValueError("Lower bound must be less than or equal to upper bound")
    
    if generate_integers:
        random_number = random.randint(int(lower_bound), int(upper_bound))
        logger.info(f"Generated random integer: {random_number}")
        return str(random_number)
    else:
        random_number = random.uniform(lower_bound, upper_bound)
        logger.info(f"Generated random float: {random_number}")
        return str(random_number)


def generate_random_choice(
    options: List[str]
) -> str:
    """
    Make a random choice from a list of options.
    
    Parameters
    ----------
    options : List[str]
        List of options to choose from
        
    Returns
    -------
    str
        A randomly selected option from the list
    """
    logger.info(f"Making random choice from {len(options)} options: {options}")
    
    if not options:
        raise ValueError("Options list cannot be empty")
    
    choice = random.choice(options)
    logger.info(f"Made random choice: {choice}")
    return str(choice)


def generate_random_batch(
    requests: List[Dict[str, Any]]
) -> str:
    """
    Generate a batch of random results for multiple named requests.
    
    Parameters
    ----------
    requests : List[Dict[str, Any]]
        List of request dictionaries, each containing:
        - name: str - identifier for the request
        - type: str - either "number" or "choice" 
        - For type "number":
          - lower_bound: float
          - upper_bound: float
          - generate_integers: bool (optional, default False)
        - For type "choice":
          - options: List[str]
          
    Returns
    -------
    str
        JSON string mapping request names to their results
    """
    logger.info(f"Processing batch of {len(requests)} random requests")
    
    results = {}
    
    for request in requests:
        name = request.get("name")
        request_type = request.get("type")
        
        if not name:
            raise ValueError("Each request must have a 'name' field")
        if not request_type:
            raise ValueError(f"Request '{name}' must have a 'type' field")
            
        logger.info(f"Processing request '{name}' of type '{request_type}'")
        
        if request_type == "number":
            lower_bound = request.get("lower_bound")
            upper_bound = request.get("upper_bound")
            generate_integers = request.get("generate_integers", False)
            
            if lower_bound is None or upper_bound is None:
                raise ValueError(f"Request '{name}' of type 'number' must have 'lower_bound' and 'upper_bound'")
                
            result = generate_random_number(lower_bound, upper_bound, generate_integers)
            
        elif request_type == "choice":
            options = request.get("options")
            
            if not options:
                raise ValueError(f"Request '{name}' of type 'choice' must have 'options'")
                
            result = generate_random_choice(options)
            
        else:
            raise ValueError(f"Request '{name}' has invalid type '{request_type}'. Must be 'number' or 'choice'")
            
        results[name] = result
        logger.info(f"Request '{name}' completed with result: {result}")
    
    json_result = json.dumps(results)
    logger.info(f"Batch processing completed. Results: {json_result}")
    return json_result


def generate_random_number_tool() -> Tuple[dict, Callable]:
    """Returns the tool specification and function for the random number generator tool."""
    spec = {
        "type": "function",
        "name": "generate_random_number",
        "description": "Generate a random number (integer or float) within specified bounds. Useful for creating varied examples, generating data for problems, or adding randomness to educational content.",
        "parameters": {
            "type": "object",
            "properties": {
                "lower_bound": {
                    "type": "number",
                    "description": "The lower bound for the random number (inclusive)"
                },
                "upper_bound": {
                    "type": "number", 
                    "description": "The upper bound for the random number (inclusive for integers, exclusive for floats)"
                },
                "generate_integers": {
                    "type": "boolean",
                    "description": "If true, generate integers; if false, generate floating point numbers"
                }
            },
            "required": ["lower_bound", "upper_bound"]
        }
    }
    return spec, generate_random_number


def generate_random_choice_tool() -> Tuple[dict, Callable]:
    """Returns the tool specification and function for the random choice tool."""
    spec = {
        "type": "function",
        "name": "generate_random_choice",
        "description": "Make a random selection from a list of options. Useful for creating multiple choice answers, selecting random examples, or adding variety to educational content.",
        "parameters": {
            "type": "object",
            "properties": {
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of options to randomly choose from (e.g., ['A', 'B', 'C', 'D'] or ['red', 'blue', 'green'])"
                }
            },
            "required": ["options"]
        }
    }
    return spec, generate_random_choice


def generate_random_batch_tool() -> Tuple[dict, Callable]:
    """Returns the tool specification and function for the batch random generation tool."""
    spec = {
        "type": "function",
        "name": "generate_random_batch",
        "description": "Generate multiple random results in a single call with named requests. Each request can be either a random number or random choice. Returns a JSON string mapping request names to their results.",
        "parameters": {
            "type": "object",
            "properties": {
                "requests": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Identifier for this request (e.g., 'numerator', 'denominator', 'x', 'y')"
                            },
                            "type": {
                                "type": "string",
                                "enum": ["number", "choice"],
                                "description": "Type of random generation: 'number' for random numbers, 'choice' for random selection"
                            },
                            "lower_bound": {
                                "type": "number",
                                "description": "For type 'number': the lower bound (inclusive)"
                            },
                            "upper_bound": {
                                "type": "number",
                                "description": "For type 'number': the upper bound (inclusive for integers, exclusive for floats)"
                            },
                            "generate_integers": {
                                "type": "boolean",
                                "description": "For type 'number': if true, generate integers; if false, generate floating point numbers"
                            },
                            "options": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "For type 'choice': list of options to randomly choose from"
                            }
                        },
                        "required": ["name", "type"],
                        "additionalProperties": False
                    },
                    "description": "List of named random generation requests"
                }
            },
            "required": ["requests"]
        }
    }
    return spec, generate_random_batch 