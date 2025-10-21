from PheTK.Phecode import Phecode


def get_phecodes():
    # instantiate class Phecode and provide some basic information
    phecode = Phecode(platform="aou")

    # generate phecode profiles/counts
    phecode.count_phecode(
        phecode_version="X",
        icd_version="US",
        phecode_map_file_path=None,
        output_file_name="aou_phecode_counts.csv"
    )

