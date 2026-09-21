"""
Name:     Useful Functions
Purpose:  To serve as a reference for useful functions that I have computed before that I might
desire to use later.

Author:   Travis Asher

Created:  1/21/2018
Updated to Current R: 6/9/26
"""

import re
import numpy as np
import functools as funct
import operator as oper
import pandas as pd
import geopandas as gpd



def reproject_to_UTM(gdf, width_threshold = 6, equator_threshold = 0.5):
    # Restricts all inputs to either Pandas DataFrame objects or subclasses thereof
    if isinstance(gdf,pd.DataFrame):
        # Catches the single instance where `gdf` passes above but is unsuitable for our function
        if not isinstance(gdf,gpd.GeoDataFrame):
            raise TypeError("Please convert your Pandas DataFrame object into a GeoPandas"
                            " GeoDataFrame object.")
    # Eliminates all unacceptable input values
    else:
        raise TypeError("This function only accepts GeoPandas GeoDataFrame objects as input.")
    # We calculate our geodataframes bounding box. If certain conditions are met, our function will
    # raise an error. Our three conditions are (1: "width limit") spilling over the longitude line,
    # (2: "latitude limit") being too close to the poles, and (3: "equator gap") significantly
    # spanning both sides of the equator. Further defining (3), we have 2 further conditions to 
    # follow: if miny<0<maxy, then if (i) maxy - miny > threshold, OR (ii) [(miny < -0.25) AND
    # (maxy > 0.25)], our input is rejected from our function.
    minx, miny, maxx, maxy = gdf.total_bounds
    # 1: "width limit" check
    if maxx - minx > width_threshold:
        raise ValueError("The dataset cross-section is too wide for UTM. Please use a "
                         "continental equal-area projection instead.")
    # 2: "latitude limit" check
    if maxy > 84 or miny < -80:
        raise ValueError("The dataset lies too close to the absolute poles. Please use the"
                         " Universal Polar Stereographic Projection (UPS) instead.")
    # 3: "equator gap" check
    if miny < 0 < maxy:
        if maxy - miny > equator_threshold or (miny < -0.25 and maxy > 0.25):
            raise ValueError("The dataset significantly spans both sides of the equator, which"
                             " breaks UTM hemisphere math. To prevent massive distance "
                             "distortion, use a global equal-area grid or process each "
                             "hemisphere separately.")   
    # With the checks out of the way, we can now proceed
    center_lon = (minx+maxx)/2
    center_lat = (miny+maxy)/2
    zone_number = 1 + int(np.floor((180+center_lon)/6))
    direction = "N" if center_lat >= 0 else "S"
    print(f"Your GeoDataFrame should reproject to 'UTM Zone {zone_number}{direction}'. "
          "Converting to EPSG...\n")
    EPSG = f"EPSG:326{str(zone_number)}" if direction == "N" else f"EPSG:327{str(zone_number)}"    
    reprojected_input = gdf.to_crs(EPSG)
    print(f"Your new crs is `{EPSG}`.\n")
    return reprojected_input
# --- END FUNCTION ---------------------------------------------------------------------------



def abnormal_row_speed(gdf, threshold):
    # 1. Initialize a clean, flat list to serve as your permanent corporate audit log
    abnormal_row_index = []
    # 2. Establish your initial search array of target anomalies
    current_abnormal_index = gdf.query("speed_mph >= @threshold").index.astype(int).tolist()
    k = 0
    # 3. Enter the recursive patching loop
    while len(current_abnormal_index) > 0:
        # CRITICAL REFINE: Isolate and log ONLY the very first tracking point breaching the limit
        first_aberration = current_abnormal_index[0]
        abnormal_row_index.append(first_aberration)
        
        # Drop the first aberration from the active table workspace cleanly
        gdf = gdf.drop(index=first_aberration)
        
        # Recompute the relative step links (the next row automatically looks back to the old
        # point)
        compare_geom = gdf.groupby("v_id")["geometry"].shift(1)
        compare_time = gdf.groupby("v_id")["timestamp"].shift(1)
        
        gdf = gdf.assign(
            delta_dist = gdf.distance(compare_geom), 
            delta_time = (gdf["timestamp"] - compare_time).dt.total_seconds(), 
            speed_mph = lambda df: 
                ((df["delta_dist"] / df["delta_time"]) * (1 / 1609.34) * (3600 / 1))
        )
        
        k += 1
        # Refresh the scan array to verify if any domino tracking points fail the new bridge math
        current_abnormal_index = gdf.query("speed_mph >= @threshold").index.astype(int).tolist()
        
        # Safety breakout wall
        if k > 50:
            print("Loop aborted: Infinite cascade loop detected.")
            break
        
    return gdf, abnormal_row_index
# --- END FUNCTION ---------------------------------------------------------------------------



def canon_schema_translate_df(df, canonical_schema):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Function only accepts Pandas DataFrame type input.")
    # 1. Invert the master schema to create a flat string lookup dictionary
    flat_rename_map = {}
    # Default behavior: when `.rename(columns = DICT)` is passed "DICT" of dict type, it looks
    # through the column names, sees if it matches any of the UNIQUE key values, and assigns it to
    # the corresponding value on the RHS (if there are multiple values in a list/tuple, it passes
    # the entire list/tuple). Because the associate items to each key are not guaranteed to be
    # unique, we must reverse this layout to feed into `.rename()`: we desire a dictionary of 
    # each unique value in the values of the original dictionary's keys to the keys assigned to 
    # the single canonical schema key as their value.
    # To do this: canonical_schema.items() returns a list of tuples where each tuple has two
    # values: the canonical key and a tuple of its associated values. We use a for loop to 
    # iterably extract each canonical key and its associated aliases, and then use an additional
    # for loop to assign to the (initially) empty dictionary above the alias as a key with value 
    # equal to the canonical key. When this is finished, we return the application of 
    # df.rename(flat_rename_map) as the output.
    for canonical_key, aliases in canonical_schema.items():
        for alias in aliases:
            flat_rename_map[alias] = canonical_key  
    # 2. Let Pandas rename everything in a single, optimized vector pass
    return df.rename(columns=flat_rename_map)
# --- END FUNCTION ---------------------------------------------------------------------------



def canon_schema_invert(canonical_schema):
    flat_rename_map = {}
    for canonical_key, aliases in canonical_schema.items():
        for alias in aliases:
            flat_rename_map[alias] = canonical_key  
    return flat_rename_map
# --- END FUNCTION ---------------------------------------------------------------------------



def mad_thresh(df):
    arr = np.asarray(df)
    # We check to see if input is workable with our operations using np.issubdtype()
    if not np.issubdtype(arr.dtype, np.number):
        raise TypeError("Calculations can only be performed on numeric data types.")
    master_med = np.median(arr, axis=0)
    abs_dist = np.abs(arr - master_med)
    mad = np.median(abs_dist, axis=0)
    thresh_interval = (master_med - 4*mad, master_med + 4*mad)
    low, high = thresh_interval
    mask = (arr > low) & (arr < high)
    abberation_check = (~mask).any(axis=1)
    return abberation_check
# --- END FUNCTION ---------------------------------------------------------------------------



def mad_thresh_nan(df):
    arr = np.asarray(df)
    if not np.issubdtype(arr.dtype, np.number):
        raise TypeError("Calculations can only be performed on numeric data types.")
    master_med = np.nanmedian(arr, axis=0)
    abs_dist = np.abs(arr - master_med)
    mad = np.nanmedian(abs_dist, axis=0)
    thresh_interval = (master_med - 4*mad, master_med + 4*mad)
    low, high = thresh_interval
    mask = (arr > low) & (arr < high)
    abberation_check = (~mask).any(axis=1)
    return abberation_check
# --- END FUNCTION ---------------------------------------------------------------------------



def qck_cut(pattern, string, maxsplit = 0, flags = 0, return_end = False):
    """
    Displays `re.split()` results for a single regular expression applied to a string. `Maxsplit` 
    is by default 0 (which makes it inactive), `flags` is also 0 by default (which means no flags 
    are present), and an optional parameter, `return_end`, is available as a boolean to return the
    back end of the cut only; 'return_end' is set to `False` by default. Validates and processes
    regex patterns with flexible flag handling.

    Parameters
    ----------
    pattern : str
        A regular expression
    string : str
        A string to be parsed
    maxsplit : int, optional
        An integer that indicates the max number of splits that can occur. The default is 0.
    flags : int, str, re.RegexFlag, or list/tuple, optional
        Regex modifiers. Accepts native flags, friendly strings (e.g., 'i', 're.M'), 
        or collections of them; very flexible. Defaults to 0.
    return_end : bool, optional
        Optional boolean selection to return just the final part of the split string. The default 
        is False.

    Returns
    -------
    str
        Returns a list of string objects that represent what remains from the .split() operation. 
        If `return_end` is `True`, returns only the last value in the list instead.

    Notes:
    ------
    When a list of flags is provided, the function converts them into a single 
    piped sequence using `functools.reduce` and `operator.or_`. 
    
    The `.reduce()` method works by applying the passed function recursively across the list 
    elements until a single, combined `re.RegexFlag` bitmask remains. 
    
    The passed function, `.oper.or_` works by taking two arguments, `a` and `b`, and combining 
    them using the bitwise OR operator (`a | b`).
    """
    
    # --- Flag Handling -----------------------------------------------
    if flags != 0:
        # Indicates the `flags` parameter was passed an argument
        reg_flag = r"(?i)^(?:re\.)?([ailmsux])$"
        ailmsux = ['A', 'I', 'L', 'M', 'S', 'U', 'X']
        ailmsux_re = [re.ASCII, re.IGNORECASE, re.LOCALE, re.MULTILINE, re.DOTALL, re.UNICODE,
                      re.VERBOSE]
        ailmsux_dict = dict(zip(ailmsux, ailmsux_re))
        
        # 1. Handle a list/tuple collection
        if isinstance(flags, (list,tuple)):
            # Checks to see if all elements of passed flags list are of the correct type
            flag_truth = [
                True if isinstance(elmt, re.RegexFlag) else bool(re.search(reg_flag, str(elmt)))
                for elmt in flags
                ]
            
            if not all(flag_truth):
                raise TypeError(
                    "'flags` collection elements must be re.RegexFlag objects or valid "
                    "flag strings."
                    )
        
            # Helper to safely clean strings or pass through re.RegexFlag objects
            coerced_flags = []
            for elmt in flags:
                if isinstance(elmt, re.RegexFlag):
                    coerced_flags.append(elmt)
                else:
                    elmt_split = elmt.split(sep=".")
                    elmt_flag_val = elmt_split[-1].upper()
                    coerced_flags.append(ailmsux_dict[elmt_flag_val])
            # Lock out mutually exclusive combinations before reducing
            if (
                (re.ASCII in coerced_flags and re.UNICODE in coerced_flags) or 
                (re.ASCII in coerced_flags and re.LOCALE in coerced_flags)
            ):
                raise ValueError("Incompatible flag combinations detected.")

            flags = funct.reduce(oper.or_, coerced_flags)
                    
        # 2. Handle a single string flag input (e.g., "re.I" or "x")
        elif isinstance(flags, str):
            if not bool(re.search(reg_flag, str(flags))):
                raise TypeError(
                    "String input for flags must be a single character in [ailmsux] or of the "
                    "form 're.~'"
                    )
                
            flag_split = flags.split(sep=".")
            flag_val = flag_split[-1].upper()
            flags = ailmsux_dict[flag_val]
                    
        # 3. Handle a single re.RegexFlag object
        elif isinstance(flags, re.RegexFlag):
            pass
        
        # 4. Handle all other data types
        else:
            raise TypeError(
                "`flags` variable only accepts re.RegexFlag, valid strings, or lists/tuples of "
                "the preceding."
                )
        
    # --- Core Engine Execution -----------------------------------------------        
    result = re.split(pattern, string, maxsplit = maxsplit, flags = flags)
    amount = len(result)
    print(f"\nPattern: '{pattern}' | String: '{string}'\n  -->  \n")
    for i in list(range(0,amount)):
        print(f"Index[{i}]: {result[i]} \n")
    return result if not return_end else result[-1]
# --- END FUNCTION ---------------------------------------------------------------------------



def qck_search(pattern, string, flags = 0):
    """
    Performs a search via `re.search()` using the regular expression `pattern` over the string
    `string`. Displays each group of string values that are isolated by the search; this 
    corresponds to the function 'capturing' sections surrounded by parentheses (unless using
    r"(:...") regex syntax). Returns the group or groups of string values that result in the form 
    of a re.Match type value if the search is successful or a `NoneType` object if it is not. The
    re.Match method `.groups()` can be applied to the output to easily view the resulting tuple of
    grouped strings. Validates and processes regex patterns with flexible flag handling.

    Parameters
    ----------
    pattern : str
        The regular expression pattern to compile.
    string : str
        The target string to search.
    flags : int, str, re.RegexFlag, or list/tuple, optional
        Regex modifiers. Accepts native flags, friendly strings (e.g., 'i', 're.M'), 
        or collections of them; very flexible. Defaults to 0.

    Returns
    -------
    result : re.Match or NoneType
        Returns a re.Match object if successful or a NoneType object if it fails

    Notes:
    ------
    When a list of flags is provided, the function converts them into a single 
    piped sequence using `functools.reduce` and `operator.or_`. 
    
    The `.reduce()` method works by applying the passed function recursively across the list 
    elements until a single, combined `re.RegexFlag` bitmask remains. 
    
    The passed function, `.oper.or_` works by taking two arguments, `a` and `b`, and combining 
    them using the bitwise OR operator (`a | b`).
    """
    
    # --- Flag Handling -----------------------------------------------
    if flags != 0:
        # Indicates the `flags` parameter was passed an argument
        reg_flag = r"(?i)^(?:re\.)?([ailmsux])$"
        ailmsux = ['A', 'I', 'L', 'M', 'S', 'U', 'X']
        ailmsux_re = [re.ASCII, re.IGNORECASE , re.LOCALE, re.MULTILINE, re.DOTALL, re.UNICODE,
                      re.VERBOSE]
        ailmsux_dict = dict(zip(ailmsux, ailmsux_re))
        
        # 1. Handle a list/tuple collection
        if isinstance(flags, (list,tuple)):
            # Checks to see if all elements of passed flags list are of the correct type
            flag_truth = [
                True if isinstance(elmt, re.RegexFlag) else bool(re.search(reg_flag, str(elmt)))
                for elmt in flags
                ]
            
            if not all(flag_truth):
                raise TypeError(
                    "'flags` collection elements must be re.RegexFlag objects or valid "
                    "flag strings."
                    )
        
            # Helper to safely clean strings or pass through re.RegexFlag objects
            coerced_flags = []
            for elmt in flags:
                if isinstance(elmt, re.RegexFlag):
                    coerced_flags.append(elmt)
                else:
                    elmt_split = elmt.split(sep=".")
                    elmt_flag_val = elmt_split[-1].upper()
                    coerced_flags.append(ailmsux_dict[elmt_flag_val])
            # Lock out mutually exclusive combinations before reducing
            if (
                (re.ASCII in coerced_flags and re.UNICODE in coerced_flags) or 
                (re.ASCII in coerced_flags and re.LOCALE in coerced_flags)
            ):
                raise ValueError("Incompatible flag combinations detected.")

            flags = funct.reduce(oper.or_, coerced_flags)
                    
        # 2. Handle a single string flag input (e.g., "re.I" or "x")
        elif isinstance(flags, str):
            if not bool(re.search(reg_flag, str(flags))):
                raise TypeError(
                    "String input for flags must be a single character in [ailmsux] or of the "
                    "form 're.~'"
                    )
                
            flag_split = flags.split(sep=".")
            flag_val = flag_split[-1].upper()
            flags = ailmsux_dict[flag_val]
                    
        # 3. Handle a single re.RegexFlag object
        elif isinstance(flags, re.RegexFlag):
            pass
        
        # 4. Handle all other data types
        else:
            raise TypeError(
                "`flags` variable only accepts re.RegexFlag, valid strings, or lists/tuples of "
                "the preceding."
                )

    # --- Core Engine Execution -----------------------------------------------
    result = re.search(pattern, string, flags = flags)
    
    # If regex finds nothing, it returns None.
    if result is None:
        print(f"\nPattern: '{pattern}' | String: '{string}'\n  -->  NO MATCH FOUND\n")
        return None
        
    # The method `.groups()` will extract the actual tuple of the captured parenthesis sections
    captured_groups = result.groups()
    amount = len(captured_groups)
    
    print(f"\nPattern: '{pattern}' | String: '{string}'\n  -->  \n")
    for i in list(range(0, amount)):
        print(f"Group[{i+1}]: {captured_groups[i]} \n") # Groups start counting at 1
        
    return result
# --- END FUNCTION ---------------------------------------------------------------------------



def qck_multisplit(pattern, string, maxsplit = 0, flags = 0, track = False):
    """
    Displays re.split() results for potentially lists of patterns and strings. Has an optional
    parameter that can be passed in order to keep track of multiple variables over the course of 
    the function that outputs the information as a Pandas DataFrame object when the loops 
    terminate; otherwise, will output a list of lists of the split string results or a single list 
    of the split string results if pattern and string are strings.  Validates and processes regex
    patterns with flexible flag handling.

    Parameters
    ----------
    pattern : str or list/tuple of str
        The regular expression pattern(s) to compile and split by.
    string : str or list/tuple of str
        The target string(s) to execute the split operations over.
    maxsplit : int, optional
        An integer that indicates the max number of splits that can occur. The default is 0.
    flags : int, str, re.RegexFlag, or list/tuple, optional
        Regex modifiers. Accepts native flags, friendly strings (e.g., 'i', 're.M'), 
        or collections of them; very flexible. Defaults to 0.
    track : bool, optional
        A boolean value that indicates whether or not you want to keep track of pattern_idx, 
        pattern, string_idx, string, num_pieces, amount, and split_results for all combinations 
        of patterns and strings as a Pandas DataFrame object and have it as a return output. 
        Defaults to False.
        
    Returns
    -------
    result : Pandas DataFrame, list of list of str, list of str
        If track is set to True, function will output tracked values in a Pandas DataFrame.
        Otherwise, will output a list of lists of strings if either pattern or string are a list 
        or a single list of strings if both pattern and string are single strings.

    Notes:
    ------
    When a list of flags is provided, the function converts them into a single 
    piped sequence using `functools.reduce` and `operator.or_`. 
    
    The `.reduce()` method works by applying the passed function recursively across the list 
    elements until a single, combined `re.RegexFlag` bitmask remains. 
    
    The passed function, `.oper.or_` works by taking two arguments, `a` and `b`, and combining 
    them using the bitwise OR operator (`a | b`).
    """
    
    # --- Flag Handling -----------------------------------------------
    if flags != 0:
        # Indicates the `flags` parameter was passed an argument
        reg_flag = r"(?i)^(?:re\.)?([ailmsux])$"
        ailmsux = ['A', 'I', 'L', 'M', 'S', 'U', 'X']
        ailmsux_re = [re.ASCII, re.IGNORECASE, re.LOCALE, re.MULTILINE, re.DOTALL, re.UNICODE,
                      re.VERBOSE]
        ailmsux_dict = dict(zip(ailmsux, ailmsux_re))
        
        # 1. Handle a list/tuple collection
        if isinstance(flags, (list,tuple)):
            # Checks to see if all elements of passed flags list are of the correct type
            flag_truth = [
                True if isinstance(elmt, re.RegexFlag) else bool(re.search(reg_flag, str(elmt)))
                for elmt in flags
                ]
            
            if not all(flag_truth):
                raise TypeError(
                    "'flags` collection elements must be re.RegexFlag objects or valid "
                    "flag strings."
                    )
        
            # Helper to safely clean strings or pass through re.RegexFlag objects
            coerced_flags = []
            for elmt in flags:
                if isinstance(elmt, re.RegexFlag):
                    coerced_flags.append(elmt)
                else:
                    elmt_split = elmt.split(sep=".")
                    elmt_flag_val = elmt_split[-1].upper()
                    coerced_flags.append(ailmsux_dict[elmt_flag_val])
            # Lock out mutually exclusive combinations before reducing
            if (
                (re.ASCII in coerced_flags and re.UNICODE in coerced_flags) or 
                (re.ASCII in coerced_flags and re.LOCALE in coerced_flags)
            ):
                raise ValueError("Incompatible flag combinations detected.")

            flags = funct.reduce(oper.or_, coerced_flags)
                    
        # 2. Handle a single string flag input (e.g., "re.I" or "x")
        elif isinstance(flags, str):
            if not bool(re.search(reg_flag, str(flags))):
                raise TypeError(
                    "String input for flags must be a single character in [ailmsux] or of the "
                    "form 're.~'"
                    )
                
            flag_split = flags.split(sep=".")
            flag_val = flag_split[-1].upper()
            flags = ailmsux_dict[flag_val]
                    
        # 3. Handle a single re.RegexFlag object
        elif isinstance(flags, re.RegexFlag):
            pass
        
        # 4. Handle all other data types
        else:
            raise TypeError(
                "`flags` variable only accepts re.RegexFlag, valid strings, or lists/tuples of "
                "the preceding."
                )

    # --- Tracking DataFrame Setup --------------------------------------------   
    tracking_data = [] if track else None
    
    # --- Core Engine Execution -----------------------------------------------
    # If either pattern or string are passed as a single string, we wrap them in a list to make 
    # the code universal
    patterns = [pattern] if isinstance(pattern, str) else pattern
    strings = [string] if isinstance(string, str) else string
    # Run the matrix extraction
    for p_idx, p in enumerate(patterns):
        for s_idx, s in enumerate(strings):
            result = re.split(p, s, maxsplit = maxsplit, flags = flags)
            amount = len(result)
            
            print(f"\nPattern: '{p}' | String: '{s}'\n  -->  \n")
            for i in range(amount):
                print(f"Index[{i}]: {result[i]} \n")
                
            # If track = True, we update the tracking_data each loop
            if track:
                tracking_data.append({
                    "pattern_idx": p_idx,
                    "pattern": p,
                    "string_idx": s_idx,
                    "string": s,
                    "num_pieces": amount,
                    "split_results": result
                    })
                
    # --- Smart Return Logic --------------------------------------------------
    if track:
        df_tracking = pd.DataFrame(tracking_data)
        return df_tracking
        
    # If the original inputs were just plain single strings, return a single direct list
    if isinstance(pattern, str) and isinstance(string, str):
        return result
        
    # Default case: return a clean list of lists containing all the split arrays from the run
    return [re.split(p, s, maxsplit=maxsplit, flags=flags) for p in patterns for s in strings]
# --- END FUNCTION ---------------------------------------------------------------------------



def qck_findall(pattern, string, flags = 0, track = False):
    """
    Performs the pattern expression operations  're.findall()'. If passed a list of patterns or a
    list of strings, will perform operation on all combinations of patterns and strings. Has an
    optional parameter that can be passed in order to keep track of multiple variables over the
    course of the function that outputs the information as a Pandas DataFrame object when the 
    loops terminate; otherwise, will output various lists of lists, strings, and tuples based on 
    how many capture groups the patterns have; and a list of strings or tuples results if pattern 
    and string are strings.  Validates and processes regex patterns with flexible flag handling.

    Parameters
    ----------
    pattern : str or list/tuple of str
        The regular expression pattern(s) to compile and search by.
    string : str or list/tuple of str
        The target string(s) to execute the search operations over.
    flags : int, str, re.RegexFlag, or list/tuple, optional
        Regex modifiers. Accepts native flags, friendly strings (e.g., 'i', 're.M'), 
        or collections of them; very flexible. Defaults to 0.
    track : bool, optional
        A boolean value that indicates whether or not you want to keep track of pattern_idx, 
        pattern, string_idx, string, num_matches, and find_results for all combinations of 
        patterns and strings as a Pandas DataFrame object and have it as a return output. 
        Defaults to False.

    Returns
    -------
    result : pandas.DataFrame or list of str or list of tuple or list of list
        - If `track=True`: Returns a consolidated pandas DataFrame.
        - If `track=False` (Single Input): Returns a list of strings, or a list of tuples 
          if multiple capture groups are present in the pattern.
        - If `track=False` (Multi-Input Matrix): Returns a 2D nested list containing 
          lists of strings, lists of tuples, or trivial/degenerate lists for unmatched runs.

    Notes:
    ------
    When a list of flags is provided, the function converts them into a single 
    piped sequence using `functools.reduce` and `operator.or_`. 
    
    The `.reduce()` method works by applying the passed function recursively across the list 
    elements until a single, combined `re.RegexFlag` bitmask remains. 
    
    The passed function, `.oper.or_` works by taking two arguments, `a` and `b`, and combining 
    them using the bitwise OR operator (`a | b`).
    """
    
    # --- Flag Handling -----------------------------------------------
    if flags != 0:
        # Indicates the `flags` parameter was passed an argument
        reg_flag = r"(?i)^(?:re\.)?([ailmsux])$"
        ailmsux = ['A', 'I', 'L', 'M', 'S', 'U', 'X']
        ailmsux_re = [re.ASCII, re.IGNORECASE, re.LOCALE, re.MULTILINE, re.DOTALL, re.UNICODE,
                      re.VERBOSE]
        ailmsux_dict = dict(zip(ailmsux, ailmsux_re))
        
        # 1. Handle a list/tuple collection
        if isinstance(flags, (list,tuple)):
            # Checks to see if all elements of passed flags list are of the correct type
            flag_truth = [
                True if isinstance(elmt, re.RegexFlag) else bool(re.search(reg_flag, str(elmt)))
                for elmt in flags
                ]
            
            if not all(flag_truth):
                raise TypeError(
                    "'flags` collection elements must be re.RegexFlag objects or valid "
                    "flag strings."
                    )
        
            # Helper to safely clean strings or pass through re.RegexFlag objects
            coerced_flags = []
            for elmt in flags:
                if isinstance(elmt, re.RegexFlag):
                    coerced_flags.append(elmt)
                else:
                    elmt_split = elmt.split(sep=".")
                    elmt_flag_val = elmt_split[-1].upper()
                    coerced_flags.append(ailmsux_dict[elmt_flag_val])
            # Lock out mutually exclusive combinations before reducing
            if (
                (re.ASCII in coerced_flags and re.UNICODE in coerced_flags) or 
                (re.ASCII in coerced_flags and re.LOCALE in coerced_flags)
            ):
                raise ValueError("Incompatible flag combinations detected.")

            flags = funct.reduce(oper.or_, coerced_flags)
                    
        # 2. Handle a single string flag input (e.g., "re.I" or "x")
        elif isinstance(flags, str):
            if not bool(re.search(reg_flag, str(flags))):
                raise TypeError(
                    "String input for flags must be a single character in [ailmsux] or of the "
                    "form 're.~'"
                    )
                
            flag_split = flags.split(sep=".")
            flag_val = flag_split[-1].upper()
            flags = ailmsux_dict[flag_val]
                    
        # 3. Handle a single re.RegexFlag object
        elif isinstance(flags, re.RegexFlag):
            pass
        
        # 4. Handle all other data types
        else:
            raise TypeError(
                "`flags` variable only accepts re.RegexFlag, valid strings, or lists/tuples of "
                "the preceding."
                )
    
    # --- Tracking DataFrame Setup --------------------------------------------   
    tracking_data = [] if track else None
    
    # --- Core Engine Execution -----------------------------------------------
    # If either pattern or string are passed as a single string, we wrap them in a list to make 
    # the code universal
    patterns = [pattern] if isinstance(pattern, str) else pattern
    strings = [string] if isinstance(string, str) else string
    # Run the matrix extraction
    for p_idx, p in enumerate(patterns):
        for s_idx, s in enumerate(strings):
            result = re.findall(p, s, flags = flags)
            print(f"Pattern: '{p}' | String: '{s}'\n  -->  {result}\n")

            # If track = True, we update the tracking_data each loop
            if track:
                tracking_data.append({
                    "pattern_idx": p_idx,
                    "pattern": p,
                    "string_idx": s_idx,
                    "string": s,
                    "num_matches": len(result),  # Can be 0!
                    "find_results": result
                    })

    # --- Smart Return Logic --------------------------------------------------
    if track:
        df_tracking = pd.DataFrame(tracking_data)
        return df_tracking
        
    # If the original inputs were just plain single strings, return a single direct list
    if isinstance(pattern, str) and isinstance(string, str):
        return result
        
    # Default case: return a clean list of lists containing all the split arrays from the run
    return [re.findall(p, s, flags = flags) for p in patterns for s in strings]
# --- END FUNCTION ---------------------------------------------------------------------------



def add_time(in_hour, in_min, in_sec, time_s):
    """
    Increments inputed hour, minute, and second time (in military format) by desired seconds. 
    All of the preceding functions work to calculate the exact time of day an event ends on 
    based on its start time and the event's duration in seconds. Its inputs are,  respectively, 
    the starting hour (from 0 to 23), the starting minute, that starting second, and the amount 
    of seconds that the event lasts. Its outputs are, respectively, the ending hour (from 1 to 
    12), the ending minute, the ending second, and whether or not it is AM or PM.'''

    Parameters
    ----------
    in_hour : TYPE
        DESCRIPTION.
    in_min : TYPE
        DESCRIPTION.
    in_sec : TYPE
        DESCRIPTION.
    time_s : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.
    """

    time = sec_to_hrminsec(time_s)
    if in_sec + time[2] < 60:
        tot_sec = in_sec + time[2]
        tot_hrmin = inc_min(in_min + time[1], in_hour, time[0])
        tot_min = tot_hrmin[1]
        tot_hour = tot_hrmin[0]
    else:
        tot_sec = (in_sec + time[2]) % 60
        tot_hrmin = inc_min(in_min + time[1] + 1, in_hour, time[0])
        tot_min = tot_hrmin[1]
        tot_hour = tot_hrmin[0]
    milt_time = (tot_hour, tot_min, tot_sec)
    if milt_time[0] == 0:
        adj_hour = 12
        period = "AM"
    elif 0 < milt_time[0] < 12:
        adj_hour = milt_time[0]
        period = "AM"
    elif milt_time[0] == 12:
        adj_hour = 12
        period = "PM"
    elif milt_time[0] > 12:
        adj_hour = milt_time[0] - 12
        period = "PM"
    fin_time = (adj_hour, tot_min, tot_sec, period)
    return fin_time
# --- END FUNCTION ---------------------------------------------------------------------------



def sec_to_hrminsec(time_s):
    """
    Converts time in seconds to time in hours, minutes, and seconds. Used in add_time function.

    Parameters
    ----------
    time_s : TYPE
        DESCRIPTION.

    Returns
    -------
    add_hour : TYPE
        DESCRIPTION.
    add_min : TYPE
        DESCRIPTION.
    add_sec : TYPE
        DESCRIPTION.
    """

    if time_s < 60:
        add_sec = time_s
        add_min = 0
        add_hour = 0
    else:
        add_sec = time_s % 60
        time_m = int(time_s / 60)
        if time_m < 60:
            add_min = time_m
            add_hour = 0
        else:
            add_min = time_m % 60
            add_hour = int(time_m / 60)
    return (add_hour, add_min, add_sec)
# --- END FUNCTION ---------------------------------------------------------------------------



def inc_min(mint, in_hour, time_h):
    """
    Used in add_time function

    Parameters
    ----------
    mint : TYPE
        DESCRIPTION.
    in_hour : TYPE
        DESCRIPTION.
    time_h : TYPE
        DESCRIPTION.

    Returns
    -------
    tot_hour : TYPE
        DESCRIPTION.
    tot_min : TYPE
        DESCRIPTION.
    """

    if mint < 60:
        tot_min = mint
        tot_hour = inc_hour(in_hour + time_h)
    else:
        tot_min = mint % 60
        tot_hour = inc_hour(in_hour + time_h + 1)
    return (tot_hour, tot_min)
# --- END FUNCTION ---------------------------------------------------------------------------



def inc_hour(hour):
    """
    Used in add_time function

    Parameters
    ----------
    hour : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.
    """

    if hour < 25:
        tot_hour = hour
    else:
        if hour % 24 == 0:
            tot_hour = 24
        else:
            tot_hour = hour % 24
    return tot_hour
# --- END FUNCTION ---------------------------------------------------------------------------



def gen_prime(n):
    """
    This function generates the first n number of prime numbers

    Parameters
    ----------
    n : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.
    """

    start1 = 2
    start2 = 3
    collection = [start1, start2]
    test_int = collection[len(collection) - 1] + 1
    while len(collection) < n:
        prime_check = 0
        for i in range(0, len(collection) - 1):
            if test_int % collection[i] == 0:
                prime_check += 1
            else:
                pass
        if prime_check == 0:
            collection = collection + [test_int]
            test_int = collection[len(collection) - 1] + 1
        else:
            test_int += 1
    return collection
# --- END FUNCTION ---------------------------------------------------------------------------



def gen_twinprimes(n):
    """
    This function generates the first n number of twin prime numbers. It makes use of the
    gen_prime() function in its procedure

    Parameters
    ----------
    n : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.
    """

    twin_primes = []
    # Our first test run is done on the first n primes using gen_prime(). Since we know that 
    # (2,3) is not a twin prime, we are certain that our first run will not be sufficient to
    # calculate the first n twin primes.
    test_twins = gen_prime(n)
    for i in range(1, n - 2):
        if test_twins[i + 1] - test_twins[i] == 2:
            twin_primes = twin_primes + [0]
            spot = len(twin_primes) - 1
            twin_primes[spot] = [test_twins[i], test_twins[i + 1]]
        else:
            pass
    test_next = n + 1
    while len(twin_primes) < 10:
        check = gen_prime(test_next)[test_next - 2 :]
        if check[1] - check[0] == 2:
            twin_primes = twin_primes + [0]
            spot = len(twin_primes) - 1
            twin_primes[spot] = [check[0], check[1]]
        else:
            pass
        test_next += 1
        # The below if statement is for debugging purposes only to prevent overflow. This 
        # line well be suppressed unless needed. if test_next > 1000:
        # twin_primes = ["o","v","e","r","f","l","o","w","e","r"]
    return twin_primes
# --- END FUNCTION ---------------------------------------------------------------------------



def even_or_odd(x):
    """
    This function determines whether input is odd, even, or not a real number. If input is a 
    real number but not an integer, function will indicate this

    Parameters
    ----------
    x : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.
    """

    if type(x) != int and type(x) != float:
        return False
        print("Your input needs to be a real number. C'mon man, be reasonable.")
    else:
        if type(x) == float:
            return False
            print("Your input needs to be an integer to be even or odd.")
        else:
            if x % 2 == 0:
                e_or_o = "e"
                return e_or_o
                print("Integer {} is even.".format(x))
            else:
                e_or_o = "o"
                return e_or_o
                print("Integer {} is odd.".format(x))
# --- END FUNCTION ---------------------------------------------------------------------------



def add_even_odd(n):
    """
    This function adds all the even entries and all of the odd entries separately and reports
    both respective sums. Uses the even_or_odd() function

    Parameters
    ----------
    n : TYPE
        DESCRIPTION.

    Returns
    -------
    None
    """

    even_sum = 0
    odd_sum = 0
    for i in n:
        if even_or_odd(i) != False:
            if even_or_odd(i) == "e":
                even_sum = even_sum + i
            else:
                odd_sum = odd_sum + i
        else:
            pass
    print(
        "The sum of even values in {} is {}. The sum of odd values in {} is {}.".format(
            n, even_sum, n, odd_sum
        )
    )
# --- END FUNCTION ---------------------------------------------------------------------------



def print_list_separately(list_input, intro=False, outro=False):
    """
    This function takes a list and prints each of its values on a separate line with a space 
    in between. A prefacing text to be printed before the list value may be included if desired;
    similarly for an outro text

    Parameters
    ----------
    list_input : TYPE
        DESCRIPTION.
    intro : TYPE, optional
        DESCRIPTION. The default is False.
    outro : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    None
    """

    if intro == False:
        pass
    else:
        print(intro)
        print("\n")
    limit = len(list_input)
    for i in range(0, limit):
        if i == limit - 1:
            print(list_input[i], ".", sep="")
        else:
            print(list_input[i])
            print("\n")
    if outro == False:
        pass
    else:
        print("\n")
        print(outro)
# --- END FUNCTION ---------------------------------------------------------------------------



def print_list_fields_var_rows(data, fields, num_rows, intro=False, outro=False):
    """
    This function takes a list of tuples, a list of fields, an integer number of rows, 
    (optionally) an introductory text, and (optionally) an outro text and prints the intro 
    followed by dictionaries for each rows field into each field name followed by an outro

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.
    fields : TYPE
        DESCRIPTION.
    num_rows : TYPE
        DESCRIPTION.
    intro : TYPE, optional
        DESCRIPTION. The default is False.
    outro : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    None
    """

    if len(data[0]) != len(fields):
        return (
            "The number of columns in your input data must match the length of your fields input."
        )
    else:
        pass
    if intro == False:
        pass
    else:
        print(intro)
        print("\n")
    assign = {}
    for row in range(0, num_rows):
        for col in range(0, len(fields)):
            assign[fields[col]] = data[row][col]
        print(assign)
        print("\n")
    if outro == False:
        pass
    else:
        print(outro)
# --- END FUNCTION ---------------------------------------------------------------------------



def list_to_dict(lst):
    """
    This function takes each entry 'k' of a passed list object and maps it to key 'entry_j' 
    such that the statement 'lst[j] == k' is True

    Parameters
    ----------
    lst : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.
    """

    if type(lst) != list:
        if type(lst) == tuple:
            pass
        else:
            return "Function 'list_to_dict' only takes input of the tuple or list types."
    key = {}
    dum_list = []
    lst_deg = len(lst)
    for i in range(0, lst_deg):
        dum_list.append("entry_{}".format(i))
    for i in range(0, lst_deg):
        key[dum_list[i]] = lst[i]
    return key
# --- END FUNCTION ---------------------------------------------------------------------------



def MarkovState_Calculator(trans, start, chain_num, dec_place=5):
    """This function performs a Markov chain process on an initial state vector 'start' with
    transition matrix 'trans' for a total number of 'chain_num' Markov chains. It takes as input
    four variables: 'trans' as a numpy matrix, 'start' as a tuple, 'chain_num' as a nonzero 
    positive integer, and an optional 'dec_place' as a nonzero positive integer that defaults to 
    a value of 5. Once called, the function will prompt the user to indicate one of three possible
    output options to be provided as input: 'Final' to output only the final vector which results
    from 'chain_num' Markov chains, 'All' to output a list of each of the state vectors that 
    result from each Markov chain (in order), or 'Other' to output a certain number of the last
    state vectors that result from their Markov chain applications. If 'Other' is selected, the 
    user is once again prompted for input, this time to specify an 'input' number of state 
    vectors from the tail of the Markov chain procedure to be included as a list in the output. 
    This 'input' number of tail values must be both nonzero positive as well as less than
    'chain_num' number of total Markov chains to be performed. For the sake of computation, if 
    the desired number of Markov chains is greater than one million, the function will terminate
    unless the user specifies to override this precaution via input.

    Parameters
    ----------
    trans : TYPE
        DESCRIPTION.
    start : TYPE
        DESCRIPTION.
    chain_num : TYPE
        DESCRIPTION.
    dec_place : TYPE, optional
        DESCRIPTION. The default is 5.

    Returns
    -------
    TYPE
        DESCRIPTION.
    """

    # Our function begins by determining if the passed input values are acceptable values to 
    # use to perform the intended calculations for output. We begin with checks on 'trans':
    if type(trans) != np.matrix:
        return "The input 'trans' must be of the type 'np.matrix' from the numpy module."
    elif len(trans) != len(trans.transpose()):
        return (
        "The rank of matrix 'trans' must be equal to the rank of its "
        "tranpose 'trans.transpose()'."
        )
    R = len(trans)

    # Next, we perform checks on 'start':
    if type(start) not in [tuple, list]:
        return "The input 'start' must be either of type 'tuple' or 'list'."
    elif type(start) in [tuple, list]:
        if len(start) != R:
            return "The length of input 'start' must match the dimension of matrix 'trans'."
        type_start = [type(item) for item in start]
        if not set(type_start).issubset(set([int, float])):
            return "Each entry of 'start' must be either of the 'float' or 'int' type."

    # Our next check is on 'chain_num':
    if type(chain_num) != int:
        return "The input 'chain_num' must be a positive nonzero integer."
    elif chain_num < 1:
        return "The input 'chain_num' cannot be 0 or a negative integer."
    elif chain_num > 1000000:
        override_check = input(
            "The specified number of 'chain_num' Markov chains will be computationally expensive "
            "and may crash the program. Do you still wish to proceed? Respond with either 'Yes' "
            "to proceed or anything else to ovveride:\n"
        )
        if override_check not in ["Yes", "yes"]:
            return

    # If all other inputs are acceptable, our last check is performed on 'dec_place':
    if type(dec_place) != int:
        return "The input 'dec_place' must be a positive integer."
    elif dec_place < 0:
        return "The input 'dec_place' cannot be a negative integer without losing all meaning."

    # If all of the above checks are passed, the function will proceed to Markov chain 
    # procedure, beginning by prompting the user for input.
    init_proceed = False
    while init_proceed == False:
        output_type = input(
            "Would you like to receive the resultant vector of {} chains of your Markov process, "
            "would you like to receive a list containing the resultant vector of every step of "
            "this Markov process, or would you like to receive a certain number of the last "
            "iterations of this Markov process? Respond 'Final' for the first option, 'All' "
            "for the second option, or 'Other' for the third option:\n".format(
                chain_num
            )
        )
        if output_type in ["Final", "final", "f", "last", "l"]:
            init_proceed = True
            nxt = start * trans
            for n in range(1, chain_num):
                nxt = nxt * trans
            # The following rounds each entry in nxt and appends it to the empty matrix 'rounded'
            rounded = []
            for n in range(len(trans)):
                rounded_n = round(nxt.item(n), dec_place)
                rounded.append(rounded_n)
            return rounded
        if output_type in ["All", "all", "a"]:
            init_proceed = True
            nxt = start * trans
            first = []
            for m in range(len(trans)):
                rounded_m = round(nxt.item(m), dec_place)
                first.append(rounded_m)
            rounded_all = [first]
            for n in range(1, chain_num):
                nxt = nxt * trans
                rounded = []
                for m in range(len(trans)):
                    rounded_m = round(nxt.item(m), dec_place)
                    rounded.append(rounded_m)
                rounded_all.append(rounded)
            return rounded_all
        if output_type in ["Other", "other", "o"]:
            init_proceed = True
            proceed = False
            while proceed == False:
                tail_num = input(
                    "The output of this function will be a list of the last specified number "
                    "N applications of the Markov process. What number of last entries would "
                    "you like to receive? Respond with a nonzero positive integer less than the"
                    "number of Markov chains:\n"
                )
                int_check = True
                try:
                    int(tail_num)
                except ValueError:
                    int_check = False
                if int_check == True:
                    if all((int(tail_num) > 0, int(tail_num) < chain_num)):
                        proceed = True
                        nxt = start * trans
                        rounded_all = []
                        for n in range(1, chain_num - int(tail_num)):
                            nxt = nxt * trans
                        for n in range(chain_num - int(tail_num), chain_num):
                            rounded = []
                            nxt = nxt * trans
                            for m in range(len(trans)):
                                rounded_m = round(nxt.item(m), dec_place)
                                rounded.append(rounded_m)
                            rounded_all.append(rounded)
                        return rounded_all
                    elif int(tail_num) < 0:
                        print(
                            "'{}' is an invalid integer. Please enter a positive nonzero "
                            "integer:\n".format(                                
                                int(tail_num)
                            )
                        )
                    else:
                        print(
                            "'{}' is an invalid integer. Please enter an integer less than "
                            "the number of Markov chains in the process:\n".format(int(tail_num))
                        )
                else:
                    print("Your response is not an integer.\n")
        else:
            print("Your input must be either 'Final', 'All', or 'Other'.")
# --- END FUNCTION ---------------------------------------------------------------------------



def preimages_of_Y_when_min_is_rm(Y, unique=False):
    """
    Takes a positive integer n-tuple and outputs a list of n+1-tuples where new entries are from 
    the set of values ranging from the 1 to the minimum value of the list. By default, all
    permutations are outputted; however, if optional parameter 'unique' is set to be True, only 
    the unique permutations are outputted.

    Parameters
    ----------
    Y : TYPE
        DESCRIPTION.
    unique : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    TYPE
        DESCRIPTION.
    """

    # We make sure our input is a list:
    if type(Y) != list:
        if type(Y) == tuple:
            Y = list(Y)
        else:
            return "Input must be of either the list or tuple type."
    # We make sure our list has values that are positive integers:
    for item in Y:
        if type(item) != int:
            return "Input's entries must be positive integers."
        else:
            if item <= 0:
                return "Input's entries must be greater than zero."
    # We perform the indicated calculation:
    pre_image = []
    for i in range(1, min(Y) + 1):
        pre_image.append([i] + Y)
        for j in range(1, len(Y) + 1):
            pre_image.append(Y[0:j] + [i] + Y[j:])
    if unique == True:
        tuple_list = [tuple(item) for item in pre_image]
        tuple_set = set(tuple_list)
        pre_image = [list(item) for item in tuple_set]
    return pre_image
# --- END FUNCTION ---------------------------------------------------------------------------



def gen_randint(number=1, minim=1, maxum=10, rep=True, return_dummy=False):
    """
    Generates 'number' amount of random integers between the values of 'minim' and 'maxum'; 
    these default to 1, 1, and 10 respectively. By default, repetition is accepted, but one 
    can specify to return only unique integers by changing 'rep'. If returning unique integers, 
    one can indicated if they want to also return the actual list of generated integers that
    included repeat values

    Parameters
    ----------
    number : TYPE, optional
        DESCRIPTION. The default is 1.
    minim : TYPE, optional
        DESCRIPTION. The default is 1.
    maxum : TYPE, optional
        DESCRIPTION. The default is 10.
    rep : TYPE, optional
        DESCRIPTION. The default is True.
    return_dummy : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    TYPE
        DESCRIPTION.
    """

    # Check that number, minim, and maxum are integers:
    chk_list = [number, minim, maxum]
    compare2str = ["number", "minim", "maxim"]  ### For referring back to in feedback
    chk_type = [type(item) for item in chk_list]
    if all(item == int for item in chk_type) == False:
        bool_chk = [item != int for item in chk_type]
        invalids = [compare2str[i] for i in range(0, 3) if bool_chk[i]]
        feedback = (
        "Your input(s) for '{}' are invalid. 'number', 'minim', and 'maxum' "
        "must be integers."
        ).format(
            invalids
        )
        return feedback
    else:
        # Check that number, minim, and maxum are positive:
        pos_chk = [x > 0 for x in chk_list]
        if all(pos_chk) == False:
            invalids2 = [compare2str[i] for i in range(0, 3) if pos_chk[i]]
            feedback2 = (
                "Your input(s) for '{}' are invalid. 'number', 'minim', and 'maxum' must be "
                "greater than zero.".format(invalids2)
            )
            return feedback2

    # Check that rep and return_dummy are booleans:
    chk_list2 = [rep, return_dummy]
    compare2str2 = ["rep", "return_dummy"]
    chk_type2 = [type(item) for item in chk_list2]
    if all(item == bool for item in chk_type2) == False:
        bool_chk2 = [item != bool for item in chk_type2]
        invalids3 = [compare2str2[i] for i in range(0, 2) if bool_chk2[i]]
        feedback3 = (
            "Your input(s) for '{}' are invalid. 'rep' and 'return_dummy' must be "
            " booleans.".format(
                invalids3
            )
        )
        return feedback3

    if rep == True:
        rand_vect = list(np.random.randint(minim, maxum + 1, number))
        return rand_vect
    else:

        # Check that requested data are valid:
        if number > 1 + maxum - minim:
            return "You cannot have more unique results than available numbers to choose from."

        thresh = 1
        first = list(np.random.randint(minim, maxum + 1, 1))
        build_vect = [first]
        dummy_vect = [first]
        while thresh < number:
            next_num = list(np.random.randint(minim, maxum + 1, 1))
            dummy_vect.append(next_num)
            if next_num not in build_vect:
                build_vect.append(next_num)
                thresh += 1
        retrn = {}
        retrn["return_vector"] = build_vect
        if return_dummy == True:
            retrn["dummy_vector"] = dummy_vect
        return retrn
# --- END FUNCTION ---------------------------------------------------------------------------