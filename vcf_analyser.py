import numpy as np
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
    if "FILE" in file:
        file[["FILE"]] = file[["FILE"]].fillna(method="ffill")
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

        # Recreate information to not have NA columns
        nan_cols: list = merge_df.loc[:, merge_df.isna().any()].columns
        nan_cols = [col for col in nan_cols if col.endswith("_x")]
        for col in nan_cols:
            merge_df[col].fillna(merge_df[col.replace("_x", "_y")], inplace=True)



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


def merge_variant_callerscompare_variant_caller(df: pd.DataFrame) -> pd.DataFrame:
    df: pd.DataFrame = df.copy()

    # Get a list of unique passages names in the dataframe
    variant_callers: List[str] = df["FILE"].unique()

    # Creates a dataframe in a list containing each unique passage
    variant_caller_df_list: List[pd.DataFrame] = []
    for vc in variant_callers:
        variant_caller_df_list.append(df.loc[df["FILE"] == vc])

    merge_df = variant_caller_df_list[0].rename(columns={"FILE": variant_caller_df_list[0]["FILE"].unique()[0]})
    for i in range(1, len(variant_caller_df_list)):
        # Rename the PASSAGE column to the passage value
        variant_caller_df_list[i] = variant_caller_df_list[i].rename(columns={"FILE": variant_caller_df_list[i]["FILE"].unique()[0]})
        merge_df: pd.DataFrame = merge_df.copy().merge(variant_caller_df_list[i], how="outer", on=["POS", "END", "ALT"])


        # Recreate information to not have NA columns
        nan_cols: list = merge_df.loc[:, merge_df.isna().any()].columns
        nan_cols = [col for col in nan_cols if col.endswith("_x")]
        for col in nan_cols:
            merge_df[col].fillna(merge_df[col.replace("_x", "_y")], inplace=True)



        # delete all the duplicated _y columns
        merge_df = merge_df.loc[:, ~merge_df.columns.str.endswith("_y")]
        # remove _x from the columns
        merge_df.columns = merge_df.columns.str.rstrip("_x")
        # Move the passage column to the left
        passage_column_names: list = merge_df.filter(regex=("P[0-9]{2}")).columns.values.tolist()
        merge_df = merge_df[[c for c in merge_df if c not in passage_column_names] + passage_column_names]

    # Fill the columns with boolean values
    for vc in variant_callers:
        merge_df[vc] = merge_df[vc].replace({vc: True})
        merge_df[vc] = merge_df[vc].fillna(False)


    merge_df = merge_df.drop_duplicates()
    return merge_df

def simplify(df: pd.DataFrame):
    df = df[["CHROM", "POS", "SVTYPE", "SVLEN", "DR" + "DV", "DV", "AF"]]
    new_df = pd.DataFrame()
    if "CHROM" in df.columns:
        new_df["CHROM"] = df["CHROM"]
    if "POS" in df.columns:
        new_df["POS"] = df["POS"]
    if "SVTYPE" in df.columns:
        new_df["SVTYPE"] = df["SVTYPE"]
    if "SVLEN" in df.columns:
        new_df["SVLEN"] = df["SVLEN"]
    if "DR" in df.columns and "DV" in df.columns:
        new_df["LECTURE TOT"] = df["DR"] + df["DV"]
    if "DV" in df.columns:
        new_df["LECTURE SUP"] = df["DV"]
    if "AF" in df.columns:
        new_df["AF"] = df["AF"]

    new_df.to_csv("simple.csv", sep="\t", encoding="utf-8")



file: pd.DataFrame = open_file("vcf_merge.csv")
file2 = merge_formater(file)
simplify(file2)
#file2.to_csv("code_output.csv", sep="\t", encoding="utf-8")
#make_venn_diag_3(file2)

#file2 = merge_variant_callerscompare_variant_caller(file)
#print(file2.loc[(file2["nanovar"] == True) & (file2["cuteSV"] == True)].shape)
#print(file2.loc[file2["ID"] == 22620])
