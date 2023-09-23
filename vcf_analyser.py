import itertools
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
from typing import List, Dict

def open_file(path: str) -> pd.DataFrame:
    """
    Opens a csv file created by the data_grepper.sh script and adds the correct headers
    """
    #file: pd.DataFrame = pd.read_csv(path, sep="\t", names=["ID", "REF", "ALT", "SVTYPE", "SVLEN", "END", "AF", "PASSAGE", "CULTURE", "DR", "DV"])
    file: pd.DataFrame = pd.read_csv(path, sep="\t")
    file[["PASSAGE"]] = file[["PASSAGE"]].fillna(method="ffill")
    return file


def merge_formater(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a dataframe in the format of the merger
    ID  |   REF |   ... |   PASSAGE 1   |   PASSAGE 2   |   PASSAGE 3 ...
    1   |   x   |   ... |   TRUE        |   TRUE        |   FALSE
    2   |   x   |   ... |   TRUE        |   FALSE       |   TRUE
    """
    # Get a list of unique passages names in the dataframe
    passages: list = df["PASSAGE"].unique()

    # Creates a dataframe in a list containing each unique passage
    passage_df_list: list = []
    for passage in passages:
        passage_df_list.append(df.loc[df["PASSAGE"] == passage])

    merge_df = passage_df_list[0].rename(columns={"PASSAGE": passage_df_list[0]["PASSAGE"].unique()[0]})
    for i in range(1, len(passage_df_list)):
        # Rename the PASSAGE column to the passage value
        passage_df_list[i] = passage_df_list[i].rename(columns={"PASSAGE": passage_df_list[i]["PASSAGE"].unique()[0]})
        merge_df: pd.DataFrame = merge_df.copy().merge(passage_df_list[i], how="outer", on=["POS", "END", "ALT"])
        # delete all the duplicated _y columns
        merge_df = merge_df.loc[:, ~merge_df.columns.str.endswith("_y")]
        # remove _x from the columns
        merge_df.columns = merge_df.columns.str.rstrip("_x")
        # Move the passage column to the left
        passage_column_names: list = merge_df.filter(regex=("P[0-9]{2}")).columns.values.tolist()
        merge_df = merge_df[[c for c in merge_df if c not in passage_column_names] + passage_column_names]

    # Fill the columns with boolean values
    for passage in passages:
        merge_df[passage] = merge_df[passage].replace({passage: True})
        merge_df[passage] = merge_df[passage].fillna(False)


    merge_df = merge_df.drop_duplicates()
    return merge_df

def all_combinations(al: List[str]) -> List[List[str]]:
    """
    Makes all possible combinations of size 1 to n where n is the total number of element in the given list
    """
    return itertools.chain.from_iterable(
        itertools.combinations(al, i+1)
        for i in range(len(al))
    ) 

def make_venn_diag_3(df: pd.DataFrame) -> None:
    # TODO: trouver un moyen de le faire dynamiquement
    df: pd.DataFrame = df.copy()
    columns_to_compare: List[str] = df.filter(regex=("P[0-9]{2}")).columns.values.tolist()
    # generate a list
    comp_list: List[List[str]] = all_combinations(columns_to_compare)
    value_dict: Dict[List[str], int] = {}
    for c in comp_list:
        var_0: bool = True if (columns_to_compare[0] in c) else False
        var_1: bool = True if (columns_to_compare[1] in c) else False
        var_2: bool = True if (columns_to_compare[2] in c) else False

        number_of_rows: int = df.loc[
            (df[columns_to_compare[0]] == var_0) &
            (df[columns_to_compare[1]] == var_1) &
            (df[columns_to_compare[2]] == var_2)
        ]

        value_dict[",".join(c)] = number_of_rows.shape[0]

    venn3(subsets=(value_dict[columns_to_compare[0]], 
                   value_dict[columns_to_compare[1]],
                   value_dict[columns_to_compare[0]+','+columns_to_compare[1]], 
                   value_dict[columns_to_compare[2]], 
                   value_dict[columns_to_compare[0]+','+columns_to_compare[2]],
                   value_dict[columns_to_compare[1]+','+columns_to_compare[2]],
                   value_dict[columns_to_compare[0]+','+columns_to_compare[1]+','+columns_to_compare[2]]),
          set_labels=(columns_to_compare[0],
                      columns_to_compare[1],
                      columns_to_compare[2]))
    plt.show()


    

    
file: pd.DataFrame = open_file("vcf_merge.csv")
file2 = merge_formater(file)
make_venn_diag_3(file2)
