from mammoth_commons.datasets import CSV
from mammoth_commons.integration import loader
from typing import List, Optional
from mammoth_commons.externals import pd_read_csv


@loader(
    namespace="mammotheu",
    version="v0049",
    python="3.13",
    packages=("pandas",),
)
def data_custom_csv(
    path: str = "",
    delimiter: str = ",",
    numeric: Optional[
        List[str]
    ] = None,  # numeric = ["age", "duration", "campaign", "pdays", "previous"]
    categorical: Optional[
        List[str]
    ] = None,  # ["job", "marital", "education", "default", "housing", "loan", "contact", "poutcome"]
    label: Optional[str] = None,
    skip_invalid_lines: bool = True,
) -> CSV:
    """
    <img src="https://pandas.pydata.org/static/img/pandas_white.svg" alt="Based on Pandas" style="background-color: #000099; float: left; margin-right: 15px; margin-top: 5px; margin-bottom: 5px; height: 60px;"/>

    Loads a CSV file that contains numeric, categorical, and predictive data columns
    separated by a user-defined delimiter. Each row corresponds to a different data sample,
    with the first one sometimes holding column names (this is automatically detected).
    To use all data in the file and automate discovery of numerical and categorical columns,
    as well as of delimiters, use the `auto csv` loader instead. Otherwise, set here all loading
    parameters.
    A <a href="https://pandas.pydata.org/">pandas</a> CSV reader is employed internally.

    Args:
        path: The local file path or a web URL of the file.
        numeric: A list of comma-separated column names that hold numeric data.
        categorical: A list of comma-separated column names that hold categorical data.
        label: The name of the categorical column that holds predictive label for each data sample.
        delimiter: Which character to split loaded csv rows with.
        skip_invalid_lines: Whether to skip invalid lines being read instead of creating an error.
    """
    if not path.endswith(".csv"):
        raise Exception("A file or url with .csv extension is needed.")
    if isinstance(categorical, str):
        categorical = [cat.strip() for cat in categorical.split(",")]
    if isinstance(numeric, str):
        numeric = [num.strip() for num in numeric.split(",")]
    raw_data = pd_read_csv(
        path,
        on_bad_lines="skip" if skip_invalid_lines else "error",
        delimiter=delimiter,
    )
    if raw_data.shape[1] == 1:
        raise Exception(
            "Only one column was found. This often indicates that the wrong delimiter was specified."
        )
    if label not in raw_data:
        raise Exception(
            f"The dataset has no column name `{label}` to set as a label."
            f"\nAvailable columns are: {', '.join(raw_data.columns)}"
        )
    for col in categorical:
        if col not in raw_data:
            raise Exception(
                f"The dataset has no column name `{col}` to add to categorical attributes."
                f"\nAvailable column are: {', '.join(raw_data.columns)}"
            )
    for col in numeric:
        if col not in raw_data:
            raise Exception(
                f"The dataset has no column name `{col}` to add to numerical attributes."
                f"\nAvailable columns are: {', '.join(raw_data.columns)}"
            )
    csv_dataset = CSV(
        raw_data,
        num=numeric,
        cat=categorical,
        labels=label,
    )
    return csv_dataset
