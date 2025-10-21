###############################################################################
# (c) Copyright 2021-2022 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import json
import pickle
import pprint
from argparse import ArgumentParser

from DecayTreeTupleBase.DecayTreeTupleBaseConf import (
    DecayTreeTuple,
    EventTuple,
    MCDecayTreeTuple,
)


def parse_args():
    """Parse command line arguments with `argparse`.

    Returns:
        ArgumentParser-parsed arguments.
    """
    parser = ArgumentParser()
    parser.add_argument("--pkl", required=True, help="Pickle file to read")
    parser.add_argument("--output", required=True, help="Name of output .json file")
    parser.add_argument(
        "--debug", action="store_true", default=False, help="output debug information"
    )
    return parser.parse_args()


def pkl_json_dump(pkl, output, debug=False):
    """Move relevant information from pickle to JSON format.

    Args:
        pkl (str): Pickle file path.
        output (str): Output JSON file path.
        debug (bool, optional): Debug flag. Defaults to False.
    """
    output_dict = {"DecayTreeTuple": [], "MCDecayTreeTuple": [], "EventTuple": []}

    # Open the pickle file
    with open(pkl, "rb") as fp:
        data = pickle.load(fp)

    # Filter the pickle file
    for key in data:
        if isinstance(data[key], DecayTreeTuple):
            output_dict["DecayTreeTuple"].append(key)
        elif isinstance(data[key], MCDecayTreeTuple):
            output_dict["MCDecayTreeTuple"].append(key)
        elif isinstance(data[key], EventTuple):
            output_dict["EventTuple"].append(key)

    if debug:
        print("\nOutput for the .json file:")
        pprint.pprint(output_dict)

    # Save useful information in JSON file
    with open(output, "wt") as f:
        json.dump(output_dict, f)


if __name__ == "__main__":
    args = parse_args()

    pkl_json_dump(args.pkl, args.output, debug=args.debug)
