from src.PheQTK.modules.cohorts.cohorts import get_cohort
from src.PheQTK.modules.cohorts.covariate_validation import get_covariates
from src.PheQTK.modules.cohorts.variant_validation import get_variants
# from src.PheQTK.modules.phecodes.phecodes import get_phecodes
# from src.PheQTK.modules.phewass.phewass import run_phewass
# from src.PheQTK.modules.plots.plots import get_plots


def main():
    print("Welcome to PheQTK!")

    """
    1. Cohorts Module
        instantiate class Cohort object for _All of Us_ database version 7 
        get variant ids from user and generate cohorts by variant id
        get covariate information from user and generate covariate files by variant id
    """
    # get variants from the user
    variants = get_variants()

    # get covariates from the user
    covariates = get_covariates()

    # use PheTK to generate cohorts with covariates
    get_cohort(variants, covariates)

    """
    2. Phecodes Module
    """
    # phecodes = get_phecodes()

    """
    3. PheWAS Module
    """
    # phewass = run_phewass()

    """
    4. Plots Module
    """
    # plots = get_plots()


if __name__ == "__main__":
    main()
