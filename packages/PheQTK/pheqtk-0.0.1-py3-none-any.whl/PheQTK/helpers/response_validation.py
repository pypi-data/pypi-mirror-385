"""
This file contains functions for validating user responses.
"""


# recursively asks for a valid response from the user
def validate_yes_no_response(response) -> bool:
    response = response.lower()

    if response == "y" or response == "yes":
        return True
    elif response == "n" or response == "no":
        return False
    else:
        print("Invalid choice.")
        new_response = input("Please enter 'y' for yes or 'n' for no.")
        return validate_yes_no_response(new_response)


# recursively asks for a valid number from the user
def validate_digit_response(response) -> int:
    response = response.strip()

    try:
        return int(response)
    except ValueError:
        print(f"{response} is not a valid number.")
        new_response = input("Please enter a number.")
        return validate_digit_response(new_response)


# recursively asks for a valid covariate name from the user
def validate_single_covariate(response) -> str:
    valid_names = ["natural_age",
                   "age_at_last_event",
                   "sex_at_birth"
                   "ehr_length",
                   "dx_code_occurrence_count",
                   "dx_condition_count",
                   "genetic_ancestry"
                   "first_n_pcs",
                   "drop_nulls"
                   ]
    if response in valid_names:
        return response
    else:
        print("Invalid covariate name.")
        new_response = input("Enter a valid covariate name.")
        return validate_single_covariate(new_response)
