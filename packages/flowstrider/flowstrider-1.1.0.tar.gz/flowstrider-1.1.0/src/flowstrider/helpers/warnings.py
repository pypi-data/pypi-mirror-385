# SPDX-FileCopyrightText: 2025 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass


@dataclass
class WarningsCounter:
    """This class is supposed to hold the information of how many warnings were output
    during the execution of the program. Every warning should call the classmethod of
    this class. The total number of warnings is being displayed at the end of the
    program for better visibility (Warnings might go unnoticed if they appear somewhere
    throughout the output and are not mentioned at the end).
    """

    count = 0

    @classmethod
    def add_warning(cls):
        cls.count += 1
