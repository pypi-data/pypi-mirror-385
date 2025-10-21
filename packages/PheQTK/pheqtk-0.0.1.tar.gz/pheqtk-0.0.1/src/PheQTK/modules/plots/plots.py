from PheTK.Plot import Plot


def get_plots():
    p = Plot("rs61738161_phewas_results.csv")

    # generate Manhattan plot
    p.manhattan(
        label_values="p_value",
        phecode_categories=["Cardiovascular"],
        label_count=6,
        save_plot=True
    )

