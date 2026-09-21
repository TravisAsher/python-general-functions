# Python General Functions, Shortcuts, and Help Operations
This document contains the general functions that I have created or use in Python, the general shortcuts that I use to navigate the Spyder environment, and a help operations comparison between R and Python. The document is currently split between two function types: general functions and functions that I use for video games.


## Current Spyder Shortcuts:
### Panel Navigation:
*Ctrl + Shift + 1* = Focus to Editor  
*Ctrl + Shift + 2* = Focus to Console  
*Ctrl + Shift + 3* = Focus to Help  
*Ctrl + Shift + 4* = Focus to Plot  
*Ctrl + Shift + 5* = Focus to Variables/Environment  
*Ctrl + Shift + 6* = Focus to History


### Other:
*Ctrl + Shift + Z* = Comment/Uncomment Section  
*Ctrl + Return* = Run Code  
*Alt + Return* = Run Current Line and Advance  
*Ctrl + Alt + Return* = Run Code from Start to Current Selection  
*Alt + Shift + Return* = Run Code Starting from Current Selection  
*Ctrl + R* = Find and Replace Text  
*Ctrl + Shift + E* = Generate Docstring (only usable within a function definition)  
*Ctrl + Alt + I* = Activate Code Formatter

### Not Keyboard Shortcuts:
* In Spyder, insert a section by typing "# %%" followed by the title; this functions similarly to "Insert a section" in RStudio  
* In Spyder, to query a method of a data type, use the format "datatype.method?"; for example, to query the method ".sort_values()" of the pandas.DataFrame type, we input "pandas.DataFrame.sort_values?" into the console
    > <sub>**IMPORTANT NOTE**: If the pandas library is imported under a different name, such as `import pandas as pd` -> `pd`, then replace the initial `pandas` with `pd`: `pd.DataFrame.sort_values?`</sub>
* In Spyder, when working with the `pathlib` library, the initial "Run file" {*Ctrl + Return*} sets the current working directory to that script's path/folder

## Help Operations R/Python Comparison:

| Intention | Python Framework | R Framework |
| :--- | :--- | :--- |
| **Inspect Object Data Structure** | `type(obj)` or `obj.dtypes` | `str(obj)` or `attributes()` |
| **Read Specific Function Docs** | `help(func)` | `?func` or `help(func)` |
| **Search Globally by Concept Keyword** | ~~none~~ | `??"keyword"` or `help.search()` |
| **List Available Package Methods** | `dir(library)` | `ls("package:name")` |
| **Quick Argument Verification** | `help(func)` | `args(func)` |


## Current General Functions:
* **`reproject_to_UTM`**: Takes in a Pandas GeoDataFrame object, checks various conditions to see if a UTM  projection is an appropriate choice for the GeoDataFrame, determines that specific UTM if it exists, and then returns the reprojected GeoDataFrame object.

* **`abnormal_row_speed`**: Takes in a Pandas GeoDataFrame object and a threshold, calculates the speed of each object in a `v_id` group in miles/hour, compares these values to the threshold value, and outputs a numpay boolean array object of if a respective row is outside of the threshold or not.

* **`canon_schema_translate_df`**: Inverts a given dictionary schema and renames the inputted dataframe's columns to the new canonical schema.

* **`canon_schema_invert`**: Inverts a given dictionary schema and returns the result.

* **`mad_thresh`**: Calculates the MAD (median absolute deviation) value of a bounding box, determines if a value lies outside of this MAD, and returns a numpy boolean array indicating if a given row lies within the MAD (returns `True`) or not (returns `False`).

* **`mad_thresh_nan`**: Updated form of mad_thresh that can handle NaN values, due to using `np.nanmedian()` as opposed to `np.median()`.

* **`qck_cut()`**: Displays `re.split()` results for a single regular expression applied to a string. `Maxsplit` is by default 0 (which makes it inactive), `flags` is also 0 by default (which means no flags are present), and an optional parameter, `return_end`, is available as a boolean to return the back end of the cut only; `return_end` is set to `False` by default. Validates and processes regex patterns with flexible flag handling.

* **`qck_search()`**: Performs a search via `re.search()` using the regular expression `pattern` over the string `string`. Displays each group of string values that are isolated by the search; this corresponds to the function 'capturing' sections surrounded by parentheses (unless using `r"(:...")` regex syntax). Returns the group or groups of string values that result in the form of a `re.Match` type value if the search is successful or a `NoneType` object if it is not. The `re.Match` method `.groups()` can be applied to the output to easily view the resulting tuple of grouped strings. Validates and processes regex patterns with flexible flag handling.

* **`qck_multisplit()`**: Displays `re.split()` results for potentially lists of patterns and strings. Has an optional parameter that can be passed in order to keep track of multiple variables over the course of the function that outputs the information as a `Pandas DataFrame` object when the loops terminate; otherwise, will output a list of lists of the split string results or a single list of the split string results if pattern and string are strings. Validates and processes regex patterns with flexible flag handling.

* **`qck_findall()`**: Performs the pattern expression operations  `re.findall()`. If passed a list of patterns or a list of strings, will perform operation on all combinations of patterns and strings. Has an optional parameter that can be passed in order to keep track of multiple variables over the course of the function that outputs the information as a `Pandas DataFrame` object when the loops terminate; otherwise, will output various lists of lists, strings, and tuples based on how many capture groups the patterns have; and a list of strings or tuples results if pattern and string are strings. Validates and processes regex patterns with flexible flag handling.

* **`add_time()`**: Increments inputed hour, minute, and second time (in military format) by desired seconds. All of the preceding functions work to calculate the exact time of day an event ends on based on its start time and the event's duration in seconds. Its inputs are, respectively, the starting hour (from 0 to 23), the starting minute, that starting second, and the amount of seconds that the event lasts. Its outputs are, respectively, the ending hour (from 1 to 12), the ending minute, the ending second, and whether or not it is AM or PM.

* **`sec_to_hrminsec()`**: Converts time in seconds to time in hours, minutes, and seconds. Used in add_time function.

* **`inc_min()`**: Used in add_time function.

* **`inc_hour()`**: Used in add_time function.

* **`gen_prime()`**: This function generates the first n number of prime numbers.

* **`gen_twinprimes()`**: This function generates the first n number of twin prime numbers. It makes use of the gen_prime() function in its procedure.

* **`even_or_odd()`**: This function determines whether input is odd, even, or not a real number. If input is a real number but not an integer, function will indicate this.

* **`add_even_odd()`**: This function adds all the even entries and all of the odd entries separately and reports both respective sums. Uses the even_or_odd() function.

* **`print_list_separately()`**: This function takes a list and prints each of its values on a separate line with a space in between. A prefacing text to be printed before the list value may be included if desired; similarly for an outro text.

* **`print_list_fields_var_rows()`**: This function takes a list of tuples, a list of fields, an integer number of rows, (optionally) an introductory text, and (optionally) an outro text and prints the intro followed by dictionaries for each rows field into each field name followed by an outro.

* **`list_to_dict()`**: This function takes each entry 'k' of a passed list object and maps it to key 'entry_j' such that the statement 'lst[j] == k' is True.

* **`MarkovState_Calculator()`**: This function performs a Markov chain process on an initial state vector 'start' with transition matrix 'trans' for a total number of 'chain_num' Markov chains. It takes as input four variables: 'trans' as a numpy matrix, 'start' as a tuple, 'chain_num' as a nonzero positive integer, and an optional 'dec_place' as a nonzero positive integer that defaults to a value of 5. Once called, the function will prompt the user to indicate one of three possible output options to be provided as input: 'Final' to output only the final vector which results from 'chain_num' Markov chains, 'All' to output a list of each of the state vectors that result from each Markov chain (in order), or 'Other' to output a certain number of the last state vectors that result from their Markov chain applications. If 'Other' is selected, the user is once again prompted for input, this time to specify an 'input' number of state vectors from the tail of the Markov chain procedure to be included as a list in the output. This 'input' number of tail values must be both nonzero positive as well as less than 'chain_num' number of total Markov chains to be performed. For the sake of computation, if the desired number of Markov chains is greater than one million, the function will terminate unless the user specifies to override this precaution via input.

* **`preimages_of_Y_when_min_is_rm()`**: This function takes a positive integer n-tuple and outputs a list of n+1-tuples where new entries are from the set of values ranging from the 1 to the minimum value of the list. By default, all permutations are outputted; however, if optional parameter 'unique' is set to be True, only the unique permutations are outputted.

* **`gen_randint()`**: Takes a positive integer n-tuple and outputs a list of n+1-tuples where new entries are from the set of values ranging from the 1 to the minimum value of the list. By default, all permutations are outputted; however, if optional parameter 'unique' is set to be True, only the unique permutations are outputted.


## Current Game Functions:
* **`qck_input`**: Extends the default `input()` function to allow keywords `EXIT` or `QUIT` to automatically break out of the function

* **`ftl_store_qckconvert()`**: A user-input focused program that allows the user to quickly summarize the relevant stats useful for a store in the game, FTL, and translates them into human-interpreted language 

* **`PoE_attribute_tracker()`**: This function allows the user to adjust attribute values for their character from an initial blank state. Things it will do: adjust integer increments or decrements to the included attributes, decline (most) unacceptable input attempts, continue to iterate until the user indicates that they are finished. Things it will not do: accept float value adjustments to handle user input with multiple colons.
