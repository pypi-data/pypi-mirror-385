"""
Common utilities for chart generation, particularly for fraction display and label formatting.
"""

from typing import Optional
from fractions import Fraction


def fraction_to_latex(numerator: int, denominator: int) -> str:
    """
    Convert a fraction to LaTeX format for mathematical rendering.
    
    Parameters
    ----------
    numerator : int
        The numerator of the fraction
    denominator : int
        The denominator of the fraction
        
    Returns
    -------
    str
        LaTeX-formatted fraction string
    """
    return rf"$\frac{{{numerator}}}{{{denominator}}}$"


def auto_detect_denominator(interval: float, max_denominator: int = 16) -> Optional[int]:
    """
    Auto-detect the best denominator for a given interval.
    
    Parameters
    ----------
    interval : float
        The interval value to analyze
    max_denominator : int
        Maximum denominator to consider
        
    Returns
    -------
    Optional[int]
        The detected denominator, or None if no simple fraction found
    """
    from fractions import Fraction
    
    # Convert interval to fraction and get the denominator
    try:
        frac = Fraction(interval).limit_denominator(max_denominator)
        # Only return if the fraction is reasonably close to the original
        if abs(float(frac) - interval) < 1e-10:
            return frac.denominator
    except:
        pass
    return None


def decimal_to_fraction_string(value: float, denominator: int, simplify: bool = True, use_latex: bool = True) -> str:
    """
    Convert a decimal value to a fraction string with the given denominator.
    
    Parameters
    ----------
    value : float
        The decimal value to convert
    denominator : int
        The desired denominator for the fraction
    simplify : bool
        Whether to simplify the fraction. If False, maintains the original denominator.
    use_latex : bool
        Whether to use LaTeX formatting for mathematical rendering.
        
    Returns
    -------
    str
        The fraction as a string (e.g., "$\\frac{1}{4}$", "2/4", "3", "$1\\frac{1}{4}$")
    """
    # Handle negative values
    sign = "-" if value < 0 else ""
    value = abs(value)
    
    # Convert to fraction with the given denominator
    numerator = round(value * denominator)
    
    # Handle whole numbers
    if numerator % denominator == 0:
        whole = numerator // denominator
        return f"{sign}{whole}" if whole != 0 else "0"
    
    if simplify:
        # Create fraction and simplify
        frac = Fraction(numerator, denominator)
        
        # Handle mixed numbers (improper fractions)
        if frac.numerator >= frac.denominator:
            whole_part = frac.numerator // frac.denominator
            remainder = frac.numerator % frac.denominator
            if remainder == 0:
                return f"{sign}{whole_part}"
            else:
                if use_latex:
                    return rf"${sign}{whole_part} \: \frac{{{remainder}}}{{{frac.denominator}}}$"
                return f"{sign}{whole_part} {remainder}/{frac.denominator}"
        else:
            if use_latex:
                return f"{sign}{fraction_to_latex(frac.numerator, frac.denominator)}"
            return f"{sign}{frac.numerator}/{frac.denominator}"
    else:
        # Keep original denominator (no simplification)
        if numerator >= denominator:
            whole_part = numerator // denominator
            remainder = numerator % denominator
            if remainder == 0:
                return f"{sign}{whole_part}"
            else:
                if use_latex:
                    return rf"${sign}{whole_part} \: \frac{{{remainder}}}{{{denominator}}}$"
                return f"{sign}{whole_part} {remainder}/{denominator}"
        else:
            if use_latex:
                return f"{sign}{fraction_to_latex(numerator, denominator)}"
            return f"{sign}{numerator}/{denominator}"


def should_rotate_x_labels(num_ticks: int, is_fractions: bool = False) -> bool:
    """
    Determine if x-axis labels should be rotated based on tick count.
    
    Parameters
    ----------
    num_ticks : int
        Number of x-axis tick labels
    is_fractions : bool
        Whether the labels are fractions
        
    Returns
    -------
    bool
        True if labels should be rotated
    """
    if is_fractions:
        # Rotate fractions sooner due to their width
        return num_ticks > 8
    else:
        # Rotate regular labels when crowded
        return num_ticks > 8


def calculate_adaptive_font_size(num_ticks: int, base_size: int = 18, min_size: int = 8, use_rotation: bool = False) -> int:
    """
    Calculate adaptive font size based on number of ticks to prevent overlap.
    
    Parameters
    ----------
    num_ticks : int
        Number of tick labels
    base_size : int
        Base font size to start with
    min_size : int
        Minimum allowed font size
    use_rotation : bool
        Whether labels will be rotated (allows larger fonts)
        
    Returns
    -------
    int
        Recommended font size
    """
    if use_rotation:
        if num_ticks <= 10:
            return base_size
        elif num_ticks <= 15:
            return max(base_size - 1, min_size)
        elif num_ticks <= 20:
            return max(base_size - 2, min_size)
        elif num_ticks <= 30:
            return max(base_size - 3, min_size)
        else:
            return max(base_size - 4, min_size)
    else:
        if num_ticks <= 6:
            return base_size
        elif num_ticks <= 10:
            return max(base_size - 2, min_size)
        elif num_ticks <= 15:
            return max(base_size - 4, min_size)
        elif num_ticks <= 20:
            return max(base_size - 6, min_size)
        else:
            return min_size
