from PheTK.PheWAS import PheWAS


def run_phewass():
    # instantiate class PheWAS object and provide information for the PheWAS run
    phewas = PheWAS(
        phecode_version="X",
        phecode_count_csv_path="aou_phecode_counts.csv",
        cohort_csv_path="rs61738161_cohort_with_covariates.csv",
        sex_at_birth_col="sex_at_birth",
        covariate_cols=["age_at_last_event", "sex_at_birth", "pc1", "pc2", "pc3", "pc4", "pc5"],
        independent_variable_of_interest="case",
        min_cases=50,
        min_phecode_count=2,
        output_file_name="rs61738161_phewas_results.csv"
    )

    # run PheWAS
    phewas.run()

