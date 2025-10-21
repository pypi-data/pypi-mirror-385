"""
This helper function asks the user if they want to update the covariates.
"""
from PheQTK.helpers.response_validation import validate_yes_no_response, validate_digit_response
from PheQTK.modules.cohorts.Covariates import Covariates


def get_covariates():

    # instantiate Covariates object
    covariates = Covariates()

    # print default covariates settings
    print(f"{covariates}")

    # ask user for covariate settings
    is_natural_age = input("Do you want to add natural age as a covariate? (y/n): ")
    is_natural_age = validate_yes_no_response(is_natural_age)
    if is_natural_age:
        setattr(covariates, "natural_age", True)

    is_age_at_last_event = input("Do you want to add age at last event as a covariate? (y/n) ")
    is_age_at_last_event = validate_yes_no_response(is_age_at_last_event)
    if is_age_at_last_event:
        setattr(covariates, "age_at_last_event", True)

    is_ehr_length = input("Do you want to add EHR length as a covariate? (y/n): ")
    is_ehr_length = validate_yes_no_response(is_ehr_length)
    if is_ehr_length:
        setattr(covariates, "ehr_length", True)

    is_dx_code_occurrence_count = input("Do you want to add diagnosis code occurrence count as a covariate? (y/n): ")
    is_dx_code_occurrence_count = validate_yes_no_response(is_dx_code_occurrence_count)
    if is_dx_code_occurrence_count:
        setattr(covariates, "dx_code_occurrence_count", True)

    is_dx_condition_count = input("Do you want to add diagnosis condition count as a covariate? (y/n): ")
    is_dx_condition_count = validate_yes_no_response(is_dx_condition_count)
    if is_dx_condition_count:
        setattr(covariates, "dx_condition_count", True)

    is_genetic_ancestry = input("Do you want to add genetic ancestry as a covariate? (y/n): ")
    is_genetic_ancestry = validate_yes_no_response(is_genetic_ancestry)
    if is_genetic_ancestry:
        setattr(covariates, "genetic_ancestry", True)

    is_first_n_pcs = input("Do you want to add the first n PCs as a covariate? (y/n): ")
    is_first_n_pcs = validate_yes_no_response(is_first_n_pcs)
    if is_first_n_pcs:
        user_input = input("Enter the number of PCs to include: ")
        user_input = validate_digit_response(user_input)
        setattr(covariates, "first_n_pcs", user_input)

    is_drop_nulls = input("Do you want to drop rows with NULL covariates? (y/n): ")
    is_drop_nulls = validate_yes_no_response(is_drop_nulls)
    if is_drop_nulls:
        setattr(covariates, "drop_nulls", True)

    # verify covariates are correct before building cohorts
    print("\nYour covariates were updated:\n")
    print(covariates)
    user_confirmation = input("Is this information correct? (y/n): ")
    confirmation = validate_yes_no_response(user_confirmation)

    if not confirmation:
        print("\nCovariates were not updated. Restarting covariate selection...\n")
        get_covariates()

    return covariates

