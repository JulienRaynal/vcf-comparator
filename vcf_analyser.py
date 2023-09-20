import pandas as pd

def open_file(path: str) -> pd.DataFrame:
    """
    Opens a csv file created by the data_grepper.sh script and adds the correct headers
    """
    file: pd.DataFrame = pd.read_csv(path, sep="\t", names=["ID", "REF", "ALT", "SVTYPE", "SVLEN", "END", "AF", "PASSAGE", "CULTURE", "DR", "DV"])
    file[["PASSAGE"]] = file[["PASSAGE"]].fillna(method="ffill")
    return file


def merge_formater(df: pd.DataFrame):
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

    # TODO: change the column passage from names like P15 to TRUE if name of FALSE if not 
# TODO: logique pour la boucle
    
    merge_df = passage_df_list[0].copy()
    merge_df = merge_df.rename(columns={"PASSAGE": merge_df["PASSAGE"].unique()[0]})
    for i in range(1, len(passage_df_list)):
        # Rename the PASSAGE column to the passage value
        passage_df_list[i] = passage_df_list[i].rename(columns={"PASSAGE": passage_df_list[i]["PASSAGE"].unique()[0]})
        merge_df: pd.DataFrame = pd.merge(merge_df, passage_df_list[i], how="left", on=["ID", "END"])
        print(merge_df.columns)
        # delete all the duplicated _y columns
        merge_df = merge_df.loc[:, ~merge_df.columns.str.endswith("_y")]
        # remove _x from the columns
        merge_df.columns = merge_df.columns.str.rstrip("_x")
        # Move the passage column to the left
        passage_column_names: list = merge_df.filter(regex=("P[0-9]{2}")).columns.values.tolist()
        print(passage_column_names)
        merge_df = merge_df[[c for c in merge_df if c not in passage_column_names] + passage_column_names]
        print(merge_df.head)

    ## TODO: verifier si trim à 1000, sinon check si même mut dasn le on
    #merge_df: pd.DataFrame = pd.merge(passage_df_list[0], passage_df_list[1], how="left", on=["ID", "END"])
    ## Rename the left join passags to the passage names
    #merge_df = merge_df.rename(columns={"PASSAGE_x": merge_df["PASSAGE_x"].unique()[0]})
    #merge_df = merge_df.rename(columns={"PASSAGE_y": merge_df["PASSAGE_y"].unique()[0]})
    ## delete all the duplicated _y columns
    #merge_df = merge_df.loc[:, ~merge_df.columns.str.endswith("_y")]
    ## remove _x from the columns
    #merge_df.columns = merge_df.columns.str.rstrip("_x")
    ## Move the Passage columns to the left
    #passage_column_names: list = merge_df.filter(regex=("P[0-9]{2}")).columns.values.tolist()
    #print(passage_column_names)
    #merge_df = merge_df[[c for c in merge_df if c not in passage_column_names] + passage_column_names]
    #print(merge_df.head)

    
file: pd.DataFrame = open_file("oscur.txt")
merge_formater(file)
