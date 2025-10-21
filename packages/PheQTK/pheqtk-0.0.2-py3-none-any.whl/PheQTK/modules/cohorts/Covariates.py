from dataclasses import dataclass


@dataclass
class Covariates:
    natural_age: bool = False
    age_at_last_event: bool = False
    ehr_length: bool = False
    dx_code_occurrence_count: bool = False
    dx_condition_count: bool = False
    genetic_ancestry: bool = False
    first_n_pcs: int = 10
    drop_nulls: bool = False

    def __str__(self) -> str:
        return (f"-------------------------------------------------\n"
                f"Covariates\n"
                f"-------------------------------------------------\n"
                f"natural_age = {self.natural_age}\n"
                f"age_at_last_event = {self.age_at_last_event}\n"
                f"ehr_length = {self.ehr_length}\n"
                f"dx_code_occurrence_count = {self.dx_code_occurrence_count}\n"
                f"dx_condition_count = {self.dx_condition_count}\n"
                f"genetic_ancestry = {self.genetic_ancestry}\n"
                f"first_n_pcs = {self.first_n_pcs}\n"
                f"drop_nulls = {self.drop_nulls}\n"
                f"-------------------------------------------------\n\n"
                )
