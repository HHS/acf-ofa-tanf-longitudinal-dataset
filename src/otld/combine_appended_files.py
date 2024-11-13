import os

import pandas as pd

from otld.paths import inter_dir


def main():
    files = os.listdir(inter_dir)
    federal = []
    state = []
    post_2015 = {}

    # Combine files before 2015
    for file in files:
        df = pd.read_csv(os.path.join(inter_dir, file))
        level = "state" if file.startswith("state") else "federal"

        if file.find("2015_2023") > -1:
            post_2015[level] = df
        elif level == "federal":
            federal.append(df)
        elif level == "state":
            state.append(df)

    state = pd.concat(state)
    federal = pd.concat(federal)

    # print(state)
    # print(federal)

    # Map columns across 2014/2015 disjunction
    # Append pre and post-2015

    return federal, state


if __name__ == "__main__":
    main()
