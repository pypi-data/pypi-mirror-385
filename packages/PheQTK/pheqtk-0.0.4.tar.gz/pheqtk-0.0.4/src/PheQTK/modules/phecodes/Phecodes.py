from dataclasses import dataclass


@dataclass
class Phecodes:
    phecode_version: str = "X"
    icd_version: str = "US"
    phecode_map_file_path: str | None = None
    output_file_name: str = "aou_phecode_counts.csv"

    def __str__(self) -> str:
        return (f"-------------------------------------------------\n"
                f"Phecodes\n"
                f"-------------------------------------------------\n"
                f"phecode_version = {self.phecode_version}\n"
                f"icd_version = {self.icd_version}\n"
                f"phecode_map_file_path = {self.phecode_map_file_path}\n"
                f"output_file_name = {self.output_file_name}\n"
                f"-------------------------------------------------\n\n")
