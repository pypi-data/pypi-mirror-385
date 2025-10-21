from PheQTK.helpers.regex_patterns import VARIANT_PATTERN
from PheQTK.modules.cohorts.Variant import Variant
from PheQTK.helpers.response_validation import validate_yes_no_response


def get_variants() -> list[Variant]:
    variants = []

    # ask user for variant ids
    raw_variants = input("Enter variant id(s): (example: 20-13093478-G-A, 20-13091168-C-T):")

    # split the variants by comma
    raw_variants = raw_variants.split(",")

    # use regex to validate variant ids
    for unverified_variant in raw_variants:

        # remove whitespace
        unverified_variant = unverified_variant.strip()

        # verify variant format
        variant = VARIANT_PATTERN.match(unverified_variant)

        if variant:
            # if valid variant format, extract the values
            chrom = int(variant.group("chrom"))
            pos = int(variant.group("pos"))
            ref = variant.group("ref").upper()
            alt = variant.group("alt").upper()

            # create file names and id for each variant
            variant_id = f"{chrom}_{pos}_{ref}_{alt}"
            cohort_file = f"{variant_id}_cohort.csv"
            covariate_file = f"{variant_id}_cohort_covariates.csv"

            # create a new variant object with the extracted values
            new_variant = Variant(variant_id, chrom, pos, ref, alt, cohort_file, covariate_file)
            variants.append(new_variant)
        else:
            print(f"'{unverified_variant}' is not a valid variant id. Restarting variant module...\n")
            return get_variants()

    # show the user the variants that we read
    print("\nYou entered the following variant(s):")
    for variant in variants:
        print(f"{variant}")

    # verify variants are correct before building cohorts
    user_confirmation = input("Is the variant information correct? (y/n): ")
    confirmation = validate_yes_no_response(user_confirmation)

    if not confirmation:
        get_variants()

    print("Variant information saved.\n\n Next step: setting covariates...")
    return variants
