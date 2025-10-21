from PheTK.Cohort import Cohort


def get_cohort(variants, covariates):
    cohort = Cohort(platform="aou", aou_db_version=7)

    # create cohorts for each variant
    for variant in variants:
        # generate cohorts by genotype
        cohort.by_genotype(
            chromosome_number=int(variant.chromosome),
            genomic_position=int(variant.position),
            ref_allele=variant.ref_allele,
            alt_allele=variant.alt_allele,
            case_gt=["0/1", "1/1"],
            control_gt="0/0",
            reference_genome="GRCh38",
            mt_path=None,
            output_file_name=variant.cohort_file
        )
        print(f"Cohort for {variant.name} created.")

    # add covariates to cohorts
    for variant in variants:
        cohort.add_covariates(
            cohort_csv_path=variant.cohort_file,
            natural_age=bool(covariates.natural_age),
            age_at_last_event=bool(covariates.age_at_last_event),
            sex_at_birth=True,
            ehr_length=bool(covariates.ehr_length),
            dx_code_occurrence_count=bool(covariates.dx_code_occurrence_count),
            dx_condition_count=bool(covariates.dx_condition_count),
            genetic_ancestry=bool(covariates.genetic_ancestry),
            first_n_pcs=int(covariates.first_n_pcs),
            drop_nulls=bool(covariates.drop_nulls),
            output_file_name=variant.covariate_file
        )
        print(f"Covariates for {variant.name} added.")

# TODO: implement the mt_path option
# TODO: add option to use different reference genome
# TODO: allow user to change case_gt, control_gt
