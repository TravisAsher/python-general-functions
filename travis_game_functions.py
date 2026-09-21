"""
Name:     Functions for Games
Purpose:  A collection of various functions that I produced while playing Video Games

Author:   Travis Asher

Created:  9/21/26
"""




def qck_input(prompt):
    user_val = input(prompt)
    if user_val.strip().lower() in ['exit', 'quit']:
        raise KeyboardInterrupt("User manually terminated the script.")
    return user_val
# --- END FUNCTION ---------------------------------------------------------------------------



def ftl_store_qckconvert(gen_output = False):
    categories = ["Hire", "Player", "Items", "Repair", "Augmentations", "Drones", "Systems",
                  "Weapons"]
    canon_dict = {
        'hire': 'Crew',
        'player': 'Player General Stock',
        'items': 'Store General Stock',
        'repair': 'Hull',
        'augmentations': 'General',
        'drones': 'General',
        'systems': 'General',
        'weapons': 'General'
    }
    
    used_categories = set()
    output = ""
    cont = True
    while cont == True:
        # Crash prevention: if len(used_categories) == len(categories), all categories are used up
        if len(used_categories) == len(categories):
            print("You've selected all possible tab heading categories. Function will now "
                  "shut down...\n")
            cont = False
        filtered_cats = [cat for cat in categories if cat not in used_categories]
        
        print("Welcome. What category shall we update?")
        print(f"Categories include: \n'{filtered_cats}'\n")
        print("  --> Type CHECK to view current output progress.")
        print("  --> Type END   to finish and output your text.")
        print("  --> Type EXIT  at any time to terminate this function.")
        start_selection = qck_input("\nEnter your input below:\n").strip().lower()
        print("\n\n-----\n")
        
        if start_selection == "check":
            print(f"Current output text is: '{output}'.\n")
            print("\n-----\n")
            continue # Goes back to the start of the loop immediately
            
        elif start_selection == "end":
            cont = False
            continue
            
                
        # --- THE FUNNEL ---
        elif start_selection not in canon_dict:
            if len(start_selection) > 0:
                match = next((key for key in canon_dict if key.startswith(start_selection)), None)
                if match:
                    print(f"Auto-matching abbreviation to: '{match}'...\n")
                    start_selection = match  # Instant override!
                else:
                    print("Command not recognized. Please try again.\n")
                    continue
            else:
                print("Input cannot be empty.\n")
                continue
            
            
        # --- THE USED-CATEGORY GUARDIAN ---
        if (start_selection[0].upper() + start_selection[1:]) in used_categories:
            print(f"Error: You have already updated the '{start_selection}' category for this "
                  "store! Please choose a different tab.\n")
            print("\n-----\n")
            continue   
            
                
        # --- THE MAIN LOGIC GATE ---
        if start_selection in canon_dict:
            matched_category = canon_dict[start_selection]
            print(f"You are filling out for: '{start_selection}'.\n")
            
            # 1. HANDLE GENERAL (Augmentations, Drones, Systems, Weapons)
            if matched_category == "General":
                tab_name = start_selection[0].upper() + start_selection[1:]
                
                # Lock them in until BOTH inputs are perfectly matched
                while True:
                    print("_"*95)
                    print("%% |SALE OBJECT| %%\n")
                    obj_input = qck_input("Enter up to 3 items [comma-separated]: \n")
                    print("\n\n-----\n")
                    objects = [x.strip() for x in obj_input.split(",") if x.strip()]
                    
                    print("_"*95)
                    print("%% |ITEM COSTS| %%\n")
                    cost_input = qck_input("Enter the scrap costs for each item "
                                           "[comma-separated]:\n")
                    print("\n\n-----\n")
                    costs = [x.strip() for x in cost_input.split(",") if x.strip()]
                    
                    # Guard 1: Must be less than 4 items, but non-empty
                    if len(objects) > 3 or len(objects) == 0:
                        print("Error: You must enter at least one item and only up to 3 items."
                              " Restarting inputs...\n")
                        continue  # Jumps back to the start of this while loop
                        
                    # Guard 2: Costs must match items
                    if len(costs) != len(objects):
                        print(f"Error: Mismatch! You entered '{len(objects)}' items but"
                              " '{len(costs)}' costs. Restarting inputs...\n")
                        continue
                        
                    break  # Success! Both conditions met, exit the validation loop
                
                # Run your function and add it to the final text
                tab_output = f"{tab_name}: " 
                for index in range(len(objects)):
                    item_cost = f"'{objects[index]}' for '{costs[index]}' scrap, "
                    if index == len(objects)-1:
                        if index == 0:
                            item_cost = item_cost[:-2] + "."
                        else:
                            item_cost = "and " + item_cost[:-2] + "."
                    tab_output += item_cost
                
                output += tab_output + "\n\n"
                print(f"Added text: '{tab_output}'\n")
                print("\n\n-----\n")
                # We take note of the used category by adding this category to used_categories
                used_categories.add(start_selection[0].upper() + start_selection[1:])
                
                
            # 2. HANDLE ITEMS (Store General Stock)
            elif matched_category == 'Store General Stock':
                tab_name = start_selection[0].upper() + start_selection[1:]

                while True:
                    print("_"*95)
                    print("%% |GENERAL STORE STOCK| %%\n")
                    print("Enter the store's stocked amounts of fuel, missiles, and drone "
                          "parts, respectively [3 items; comma-separated]: ")
                    amount_input = qck_input("\n")
                    print("\n\n-----\n")
                    amounts = [x.strip() for x in amount_input.split(",") if x.strip()]
                
                    print("_"*95)
                    print("%% |GENERAL ITEM COSTS| %%\n")
                    print("Enter the respective cost of each fuel, missile, and drone part "
                          "[3 items; comma-separated]: ")
                    cost_input = qck_input("\n")
                    print("\n\n-----\n")
                    costs = [x.strip() for x in cost_input.split(",") if x.strip()]
                
                    # Guard 1: Must be exactly 3 items
                    if len(amounts) != 3:
                        print("Error: You must enter exactly 3 items. Restarting inputs...\n")
                        continue  # Jumps back to the start of this while loop
                        
                    # Guard 2: Costs must match items
                    if len(costs) != len(amounts):
                        print(f"Error: Mismatch! You entered '{len(amounts)}' amounts but"
                              " '{len(costs)}' costs. Restarting inputs...\n")
                        continue
                        
                    break  # Success! Both conditions met, exit the validation loop
                
                # Run your function and add it to the final text
                tab_output = f"{tab_name}: " 
                for index in range(len(amounts)):
                    item_cost = f"'{amounts[index]}' for '{costs[index]}' scrap, "
                    if index == len(amounts)-1:
                        item_cost = "and " + item_cost[:-2] + "."
                    tab_output += item_cost
                
                output += tab_output + "\n\n"
                print(f"Added text: '{tab_output}'\n")
                print("\n\n-----\n")
                # We take note of the used category by adding this category to used_categories
                used_categories.add(start_selection[0].upper() + start_selection[1:])
                
                
            # 3. HANDLE INVENTORY (Player General Stock)
            elif matched_category == 'Player General Stock':
                
                while True:
                    print("_"*95)
                    print("%% |PLAYER GENERAL STOCK| %%\n")
                    print("Enter your current stocks of fuel, missiles, drone parts, scrap, "
                          "and your current hull level, respectively [5 items; comma-separated]: ")
                    amount_input = qck_input("\n")
                    print("\n\n-----\n")
                    amounts = [x.strip() for x in amount_input.split(",") if x.strip()]
                    
                    # Guard: Must be exactly 5 items
                    if len(amounts) != 5:
                        print("Error: You must enter exactly 5 items. Try that again.\n")
                        continue
                    
                    break # The condition was met, exit the validation loop
                
                # Run your function and add it to the final text
                tab_output = "In your ship's inventory, you currently have: "
                inv_stock = ["fuel", "missile(s)", "drone part(s)", "scrap", "hull level"]
                for index in range(len(amounts)):
                    item_amount = f"'{amounts[index]}' '{inv_stock[index]}', "
                    if index == len(amounts)-1:
                        # We just replace item_amount
                        item_amount = f"and '{amounts[index]}' remaining '{inv_stock[index]}'(s)."
                    tab_output += item_amount
                
                output += tab_output + "\n\n"
                print(f"Added text: '{tab_output}'\n")
                print("\n\n-----\n")
                # We take note of the used category by adding this category to used_categories
                used_categories.add(start_selection[0].upper() + start_selection[1:])
                
                
            # 4. HANDLE HIRE (Crew)
            elif matched_category == "Crew":
                tab_name = start_selection[0].upper() + start_selection[1:]
                
                # Lock them in until BOTH inputs are perfectly matched
                while True:
                    print("_"*95)
                    print("%% |NAMES FOR CREW HIRES| %%\n")
                    chr_input = qck_input("Enter up to 3 characters [comma-separated]: \n")
                    print("\n\n-----\n")
                    characters = [x.strip() for x in chr_input.split(",") if x.strip()]
                    
                    print("_"*95)
                    print("%% |RACES OF CREW HIRES| %%\n")
                    race_input = qck_input("Enter the race for each of the respective characters"
                                           " [comma-separated]: \n")
                    print("\n\n-----\n")
                    races = [x.strip() for x in race_input.split(",") if x.strip()]
                    
                    print("_"*95)
                    print("%% |COSTS FOR CREW HIRES| %%\n")
                    cost_input = qck_input("Enter the scrap costs for each respective character"
                                           " [comma-separated]: \n")
                    print("\n\n-----\n")
                    costs = [x.strip() for x in cost_input.split(",") if x.strip()]
                    
                    print("_"*95)
                    print("%% |SPECIALTIES OF CREW HIRES| %%\n")
                    print("Enter special notes about each character, such as high-level skills.")
                    print("If nothing of note, be sure to at least input a single character for"
                          " each of the listed characters.")
                    print("Use any sort of punctuation marks in your descriptions EXCEPT FOR "
                          "commas (these are reserved for separating inputs): \n")
                    print("  --> Input ' ', 'n', 'null', or 'False' to notate no specialties")
                    special_input = qck_input("\n")
                    print("\n\n-----\n")
                    no_specials = ['', 'n', 'null', 'False']
                    specials = [x.strip() for x in special_input.split(",")]
                    specials = ['nothing of any particular note' if x in no_specials else x for 
                                x in specials]
                    
                    
                    # Guard 1: Must be less than 4 items, but non-empty
                    if len(characters) > 3 or len(characters) == 0:
                        print("Error: You must enter at least one item and only up to 3 items."
                              " Restarting inputs...\n")
                        continue
                        
                    # Guard 2: All four lists from input must have matching length
                    if len(characters) == len(races) == len(costs) == len(specials):
                        break  # Success! Perfect condition met, exit the validation loop
                    else:
                        print("Error: All four inputs must have equal values (this means that "
                              "each of your inputs need to have an identical number of commas"
                              " within them). Restarting inputs...\n")
                        continue
                    
                # Run your function and add it to the final text
                tab_output = f"{tab_name}: " 
                for index in range(len(characters)):
                    chr_cost = f"'{characters[index]}' is of the '{races[index]}' race with the"
                    " notable characteristics '{specials[index]}' and can be purchased for"
                    " '{costs[index]}' scrap, "
                    if index == len(characters)-1:
                        if index == 0:
                            chr_cost = chr_cost[:-2] + "."
                        else:
                            chr_cost = "and " + chr_cost[:-2] + "."
                    tab_output += chr_cost
                
                output += tab_output + "\n\n"
                print(f"Added text: '{tab_output}'\n")
                print("\n\n-----\n")
                # We take note of the used category by adding this category to used_categories
                used_categories.add(start_selection[0].upper() + start_selection[1:])
                
            
            # 5. HANDLE REPAIR (Hull)
            elif matched_category == 'Hull':
                
                while True:
                    print("_"*95)
                    print("%% |HULL REPAIR COSTS| %%\n")
                    print("Enter the cost to fix 1 hull bar and to fix all missing hull bars,"
                          " respectively [2 items; comma-separated]: ")
                    cost_input = qck_input("\n")
                    print("\n\n-----\n")
                    costs = [x.strip() for x in cost_input.split(",") if x.strip()]
                    
                    # Guard: Must be exactly 2 items
                    if len(costs) != 2:
                        print("Error: You must enter exactly 2 items. Try that again.\n")
                        continue
                    
                    break # The condition was met, exit the validation loop
                
                # Run your function and add it to the final text
                tab_output = f"To repair your ship, it will cost '{costs[0]}' to fix 1 hull bar; "
                "to fully repair your ship, it will cost '{costs[1]}'.\n"
                
                output += tab_output + "\n"
                print(f"Added text: '{tab_output}'\n")
                print("\n\n-----\n")
                # We take note of the used category by adding this category to used_categories
                used_categories.add(start_selection[0].upper() + start_selection[1:])
            
        else:
            print("Command not recognized. Please try again.\n")

    if gen_output:
        print("Your output text will be returned. Powering down function...\n")
        return output
    
    print("Your output text is printed below:\n")
    print(output)
# --- END FUNCTION ---------------------------------------------------------------------------



def PoE_attribute_tracker(state=True):
    """
    This function allows the user to adjust attribute values for their character from an initial
    blank state. Things it will do: adjust integer increments or decrements to the included
    attributes, decline (most) unacceptable input attempts, continue to iterate until the user
    indicates that they are finished. Things it will not do: accept float value adjustments to
    attributes, handle user input with multiple colons

    Parameters
    ----------
    state : TYPE, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    None
    """

    attributes = [
        "int",
        "str",
        "mel_spd",
        "mel_dam",
        "acc",
        "acc_pc",
        "mana_cost_pc",
        "atk_spd",
        "dex",
        "arm_pc",
        "enrg_shield_pc",
        "life_gen_pc",
        "cst_spd",
        "mov_spd",
        "spl_dam_pc",
        "mel_dam_pc",
        "life_pc",
        "evd_pc",
        "arm_pc",
        "stun_thrsh",
        "Jewel_Socket",
        "life",
        "evd",
        "mana_pc",
        "mana",
        "mana_gen_pc",
        "bow_dam_pc",
        "psn_pc",
        "bow_ailm_dam_pc",
        "proj_spd",
        "proj_dam_pc",
        "bow_atk_spd",
        "crit_pc",
        "lhtn_res_pc",
        "cold_res_pc",
        "fire_res_pc",
    ]
    attributes.sort()
    dum_list = [0] * len(attributes)
    att_list = {}
    for x in attributes:
        att_list["{}".format(x)] = dum_list[attributes.index(x)]
    while state == True:
        get_resp = True
        while get_resp == True:
            print("\nAttributes are: {}".format(attributes))
            response = input(
                "Which attribute do you wish to adjust and by what amount? Make selection in the "
                "form '{attribute}={value}'.\n"
            )
            if type(response) != str:
                print("Input must be a string.\n")
            elif response.rfind("=") == -1:
                print("Your input does not match the required form.\n")
            else:
                int_pass = True
                try:
                    int(response[response.rfind("=") + 1 :])
                except ValueError:
                    int_pass = False
                if int_pass == True:
                    get_resp = False
                else:
                    print(
                        "The value after the colon in your input must be a string of a number \n"
                        )
        att = response[: response.rfind("=")]
        val = int(response[response.rfind("=") + 1 :])
        att_list[att] += val
        print("\n{}".format(att_list))
        request_cont = True
        while request_cont == True:
            cont = input("Would you like to keep going? Select either 'yes' or 'no'.\n")
            if cont not in ["yes", "no", "y", "n"]:
                print("Your input must be either 'yes' or 'no'.\n")
            else:
                request_cont = False
        if cont in ["no", "n"]:
            state = False
# --- END FUNCTION ---------------------------------------------------------------------------