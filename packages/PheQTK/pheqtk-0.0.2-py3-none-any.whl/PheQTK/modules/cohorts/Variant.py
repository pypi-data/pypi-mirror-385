from dataclasses import dataclass


@dataclass
class Variant:
    variant_id: str
    chromosome: int
    position: int
    ref_allele: str
    alt_allele: str
    cohort_file: str
    covariate_file: str

    def __str__(self) -> str:
        return (f"-------------------------------------------------\n"
                f"Variant ID: {self.variant_id}\n"
                f"-------------------------------------------------\n"
                f"Chromosome: {self.chromosome}\n"
                f"Position: {self.position}\n"
                f"Reference Allele: {self.ref_allele}\n"
                f"Alternate Allele: {self.alt_allele}\n"
                f"-------------------------------------------------"
                )
