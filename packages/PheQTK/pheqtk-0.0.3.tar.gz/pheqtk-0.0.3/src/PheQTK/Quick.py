from PheQTK.modules.cohorts.cohorts import get_cohort
from PheQTK.modules.cohorts.covariate_validation import get_covariates
from PheQTK.modules.cohorts.variant_validation import get_variants
# from PheQTK.modules.phecodes.phecodes import get_phecodes
# from PheQTK.modules.phewass.phewass import run_phewass
# from PheQTK.modules.plots.plots import get_plots


def run():
    print("-------------------------------------------------")
    print("Welcome to PheQTK (The PheWAS Quick Toolkit)")
    print("PheQTK wraps around the PheTK package to automate PheWAS analyses.")
    print("-------------------------------------------------")
    print("PheQTK currently automates the following PheTK modules:")
    print("1. Cohorts Module")
    print("2. Phecodes Module (coming soon!)")
    print("3. PheWAS Module (coming soon!)")
    print("4. Plots Module (coming soon!)")

    user_option = input("\nEnter the number of the module you'd like to run (to run all modules, enter 'all'): ")
    user_option = user_option.strip().lower()

    if user_option == "all":
        print("Running all modules...")

        print("Starting Cohorts Module...")
        variants = get_variants()
        covariates = get_covariates()
        get_cohort(variants, covariates)
        print("Cohorts Module complete.")

        # print("Starting Phecodes Module...")
        # phecodes = get_phecodes()
        # print("Phecodes Module complete.")

        # print("Starting PheWAS Module...")
        # phewass = run_phewass()
        # print("PheWAS Module complete.")

        # print("Starting Plot Module...")
        # plots = get_plots()
        # print("Plot Module complete.")

    elif user_option == "1":

        print("Starting Cohorts Module...")
        variants = get_variants()               # get variants from the user
        covariates = get_covariates()           # get covariates from the user
        get_cohort(variants, covariates)        # use PheTK to generate cohorts with covariates
        print("Cohorts Module complete.")

    # elif user_option == "2":
        # phecodes = get_phecodes()

    # elif user_option == "3":
        # phewass = run_phewass()

    # elif user_option == "4":
        # plots = get_plots()


if __name__ == "__main__":
    run()
