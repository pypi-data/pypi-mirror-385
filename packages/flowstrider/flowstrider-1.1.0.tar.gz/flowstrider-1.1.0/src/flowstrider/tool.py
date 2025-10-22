# SPDX-FileCopyrightText: 2025 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: BSD-3-Clause

import argparse

# For localization:
# import ctypes
import locale
import os
import pathlib
import sys
import typing
from json.decoder import JSONDecodeError

from colorama import just_fix_windows_console
from openpyxl.utils.exceptions import InvalidFileException

from flowstrider import __version__, rules, settings, storage
from flowstrider.converters import (
    dfd_to_dot_converter,
    metadata_xsxl_converter,
    threats_to_file_converter,
)
from flowstrider.helpers.warnings import WarningsCounter
from flowstrider.models import dataflowdiagram, threat, threat_management
from flowstrider.rules.collections import all_collections


def main():
    # Initialize Localization
    try:
        if os.name != "posix":
            locale_info = locale.getlocale()
            if locale_info:
                locale_info = locale_info[0]
        else:
            locale.setlocale(locale.LC_ALL, "")
            locale_info = locale.getlocale(locale.LC_MESSAGES)
            if locale_info:
                locale_info = locale_info[0]

        if locale_info[:2] == "de":
            lang_sys_string = "de"
        else:
            lang_sys_string = "en"
    except Exception:
        lang_sys_string = "en"

    # Set system language
    settings.init_localization(lang_sys_string, "sys")

    global _
    _ = settings.lang_sys.gettext

    exit_code = 0

    just_fix_windows_console()  # Fixes ANSI escape chars for windows

    # Parse command line
    parser = argparse.ArgumentParser("flowstrider")
    subparsers = parser.add_subparsers(
        required=True, dest="subcommand", help="Subcommand"
    )

    # Threat elicitation
    parser_elicit = subparsers.add_parser("elicit", help=_("Elicit threats."))
    parser_elicit.add_argument(
        "dfd_path",
        type=pathlib.Path,
        help=_("Path to dataflow diagram (in .json) you want to elicit."),
    )
    parser_elicit.add_argument(
        "--management-path",
        type=pathlib.Path,
        help=_(
            "Path to threat management information"
            + " file (.json). Will be created if it does not exist."
        ),
    )
    parser_elicit.add_argument(
        "--output-path",
        type=pathlib.Path,
        help=_(
            "Path to save the results as PDF to. Will not be saved as PDF if this "
            + "argument is missing."
        ),
    )
    parser_elicit.add_argument(
        "--fail-on-threat",
        choices=["off", "undecided", "todo", "all"],
        default="off",
        help=_(
            "Tool fails when it identifies a threat with the given management state."
        ),
    )
    parser_elicit.add_argument(
        "--out-lang",
        choices=["en", "de"],
        default=lang_sys_string,
        help=_("Changes output language for elicitation and PDF."),
    )

    # check for metadata to add
    parser_metadata = subparsers.add_parser(
        "metadata", help=_("Give list of metadata you may want to add.")
    )
    parser_metadata.add_argument(
        "dfd_path",
        type=pathlib.Path,
        help=_("Path to dataflow diagram in (.json) you want the metadata from."),
    )
    parser_metadata.add_argument(
        "output_path",
        type=pathlib.Path,
        help=_("Path to save the metadata XLSX file to."),
    )
    parser_metadata.add_argument(
        "--out-lang",
        choices=["en", "de"],
        default=lang_sys_string,
        help=_("Changes output language for XLSX file."),
    )

    # update metadata from xlsx file
    parser_update = subparsers.add_parser(
        "update", help=_("Update metadata for a dfd.json from metadata.xlsx file.")
    )
    parser_update.add_argument(
        "dfd_path",
        type=pathlib.Path,
        help=_("Path to dataflow diagram (in .json) you want to update."),
    )
    parser_update.add_argument(
        "metadata_path",
        type=pathlib.Path,
        help=_("Path to metadata file (in .xlsx) you want to add."),
    )

    # Info
    subparsers.add_parser("info", help=_("Print version information."))

    args = parser.parse_args()

    match args.subcommand:
        case "elicit":
            exit_code = elicit_cmd(
                args.dfd_path,
                args.management_path,
                args.output_path,
                args.fail_on_threat,
                args.out_lang,
            )
        case "metadata":
            exit_code = metadata_cmd(args.dfd_path, args.output_path, args.out_lang)
        case "update":
            exit_code = update_cmd(args.dfd_path, args.metadata_path)
        case "info":
            print(
                _("FlowStrider - FlowStrider automates data flow-based threat modeling")
            )
            print(_("Version {vers}").format(vers=__version__))
            print(_("Copyright (C) 2025 German Aerospace Center DLR"))

    # Inform of warnings
    if WarningsCounter.count > 0:
        print()
        print(
            settings.C_WARNING
            + wrap(
                settings.lang_sys.ngettext(
                    "There was 1 warning!",
                    "There were {i} warnings!",
                    WarningsCounter.count,
                ).format(i=WarningsCounter.count)
            )
            + settings.C_DEFAULT
        )

    sys.exit(exit_code)


CMD_LEFT_CHAR_WIDTH = settings.CMD_LEFT_CHAR_WIDTH
CMD_MAX_CHAR_WIDTH = settings.CMD_MAX_CHAR_WIDTH
wrap = dfd_to_dot_converter.wrap_text


def elicit_cmd(
    dfd_path: pathlib.Path,
    management_path: typing.Optional[pathlib.Path],
    output_path: typing.Optional[pathlib.Path],
    fail_on_threat: str,
    out_lang: str,
):
    # Set output language
    settings.init_localization(out_lang, "out")

    # Attempt to open dfd file
    try:
        with open(dfd_path) as dfd_file:
            serialized_dfd = dfd_file.read()
    except FileNotFoundError:
        print(
            _(
                "Error: Specified file '{path}' not found. Check that the file"
                + " exists and that the location is correct."
            ).format(path=dfd_path)
        )
        return 1
    except IsADirectoryError:
        print(
            _(
                "Error: '{path}' is a directory, please specify the path to a"
                + " .json file."
            ).format(path=dfd_path)
        )
        return 1
    except PermissionError:
        print(
            _(
                "Error: No permission to access '{path}'."
                + "Please specify a valid path to a"
                + " .json file."
            ).format(path=dfd_path)
        )
        return 1

    # Deserialize dfd file in memory
    try:
        dfd: dataflowdiagram.DataflowDiagram = storage.deserialize_dfd(serialized_dfd)
    except JSONDecodeError as error:
        print(
            _("Error: There is a json error in file '{path}':\n{err}.").format(
                path=dfd_path, err=error
            )
        )
        return 1

    if management_path is not None and management_path.exists():
        # Attempt to open management file if it exists
        try:
            with open(management_path) as management_file:
                serialized_threat_management_database = management_file.read()
        except IsADirectoryError:
            print(
                _(
                    "Error: '{path}' is a directory, please specify the path to a"
                    + " .json file."
                ).format(path=management_path)
            )
            return 1
        except PermissionError:
            print(
                _(
                    "Error: No permission to access '{path}'."
                    + " Please specify a valid path to a"
                    + " .json file."
                ).format(path=management_path)
            )
            return 1

        # Deserialize management file in memory
        try:
            threat_management_database: threat_management.ThreatManagementDatabase = (
                storage.deserialize_threat_management_database(
                    serialized_threat_management_database
                )
            )
        except JSONDecodeError as error:
            print(
                _("Error: There is a json error in file '{path}':\n{err}.").format(
                    path=dfd_path, err=error
                )
            )
            return 1
    else:
        # No threat management file given or file does not exist,
        # initialize a new database.
        threat_management_database: threat_management.ThreatManagementDatabase = (
            threat_management.ThreatManagementDatabase()
        )

    # Elicit threats using rules
    results: typing.List[threat.Threat] = rules.elicit(dfd)

    # Update threat management DB
    threat_management_database.update(results, dfd)

    if management_path is not None:
        # Write changes to management file
        try:
            with open(management_path, "w") as management_file:
                serialized_threat_management_database = (
                    storage.serialize_threat_management_database(
                        threat_management_database
                    )
                )
                management_file.write(serialized_threat_management_database)
        except PermissionError:
            print(
                _(
                    "Error: No permission to access '{path}'."
                    + "Please specify a valid path to a"
                    + " .json file."
                ).format(path=management_path)
            )
            return 1

    if fail_on_threat == "off":
        # Only print the threats when not in CI/CD mode, otherwise it will be confusing
        print_threats(dfd, results, threat_management_database)

    if output_path is not None and not output_path.is_dir():
        # Create dfd images and generate pdf with image and threats
        dfd_to_dot_converter.render_dfd(dfd)
        threats_to_file_converter.create_threats_pdf(
            results, dfd, threat_management_database, output_path
        )
        print()
        print(
            wrap(
                _(
                    "Results saved as PDF to "
                    + "'{path}'. "
                    + "Diagram"
                    + " saved as PNG, SVG and Graphviz to the output/visualization"
                    + " folder."
                ).format(path=output_path)
            )
        )
    else:
        print()
        print(wrap(_("No or wrong output path specified. Threats were not saved.")))

    if management_path is not None:
        print()
        print(
            wrap(
                _("Threat management states saved as JSON to ")
                + str(management_path)
                + "."
            )
        )

    fail_result = threat_management_database.should_fail(results, dfd, fail_on_threat)
    if len(fail_result) > 0:
        print(
            wrap(
                _(
                    "The following threats caused a failure. Selected level: {level}"
                ).format(level=fail_on_threat)
            )
        )
        print_threats(dfd, fail_result, threat_management_database)
        return 1
    else:
        return 0


def print_threats(
    dfd: dataflowdiagram.DataflowDiagram,
    results: typing.List[threat.Threat],
    threat_management_database: threat_management.ThreatManagementDatabase,
):
    # Switch to output language
    _ = settings.lang_out.gettext

    # Used rule collections:
    print()
    print(wrap(_("Used rule collections:")))

    collection_names_list = []
    for collection in all_collections:
        for tag in collection.tags:
            if tag in dfd.tags:
                collection_names_list.append(collection.name)
                break
    collection_names = ", ".join(collection_names_list)
    print(wrap(collection_names))
    print()

    # Print number of threats
    if len(results) == 0:
        print(wrap(_("There were no threats found.")) + "\n")
        return 0

    # Count and divide threats by source and severity for better overview
    threats_by_source = {}
    threats_by_source_and_severity = {}
    threat_sources_occurences = {}  # How often each single source occurs
    threats_involved_locations = []
    for threat_ in results:
        source = threat_.source
        severity = threat_.severity
        location = threat.location_str(threat_.location, dfd)

        if source not in threats_by_source:
            threats_by_source[source] = []
            threat_sources_occurences[source] = 0
        threats_by_source[source].append(threat_)

        if (source, severity) not in threats_by_source_and_severity:
            threats_by_source_and_severity[(source, severity)] = []
            threat_sources_occurences[source] += 1
        threats_by_source_and_severity[(source, severity)].append(threat_)

        if location not in threats_involved_locations:
            threats_involved_locations.append(location)

    # Disregard the counter for sources who appear only once
    for source, occurences in threat_sources_occurences.items():
        if occurences == 1:
            threat_sources_occurences[source] = 0
        else:
            threat_sources_occurences[source] = 1

    print(
        wrap(
            settings.lang_out.ngettext(
                "One threat has been found.",
                "{count} threats have been found.",
                len(results),
            ).format(count=len(results))
            + " ("
            + settings.lang_out.ngettext(
                "One different threat",
                "{count} different threats",
                len(threats_by_source),
            ).format(count=len(threats_by_source))
            + " "
            + settings.lang_out.ngettext(
                "and a total of one involved location",
                "and a total of {count} involved locations",
                len(threats_involved_locations),
            ).format(count=len(threats_involved_locations))
            + ".)"
        )
        + "\n"
    )

    # Print each individual combination of threat source and severity so results are
    # ...primarily sorted by severity and by source secondarily
    for i, ((source, severity), threats_) in enumerate(
        threats_by_source_and_severity.items(), 1
    ):
        if threat_sources_occurences[source] > 0:
            source_occurence = threat_sources_occurences[source]
            threat_sources_occurences[source] += 1
            print(
                settings.C_HEADER
                + wrap(
                    _("#{number} Threat source: {src}").format(number=i, src=source)
                    + " ("
                    + str(source_occurence)
                    + ")"
                )
                + settings.C_DEFAULT
            )
        else:
            print(
                settings.C_HEADER
                + wrap(_("#{number} Threat source: {src}").format(number=i, src=source))
                + settings.C_DEFAULT
            )

        print()

        # Print description
        temp_string = wrap(
            threats_[0].short_description, CMD_MAX_CHAR_WIDTH - CMD_LEFT_CHAR_WIDTH - 1
        )
        temp_strings = temp_string.split("\n")
        print(
            (CMD_LEFT_CHAR_WIDTH - len(_("Description:"))) * " " + _("Description:"),
            end="",
        )
        for i in range(len(temp_strings)):
            if i == 0:
                print(" " + temp_strings[i])
            else:
                print((CMD_LEFT_CHAR_WIDTH + 1) * " " + temp_strings[i])

        # Print severity
        print(
            (CMD_LEFT_CHAR_WIDTH - len(_("Severity:"))) * " "
            + _("Severity:")
            + " "
            + settings.C_WARNING
            + str(round(severity, 2))
            + settings.C_DEFAULT
        )

        # Print long description
        temp_string = wrap(
            threats_[0].long_description, CMD_MAX_CHAR_WIDTH - CMD_LEFT_CHAR_WIDTH - 1
        )
        temp_strings = temp_string.split("\n")
        print(
            (CMD_LEFT_CHAR_WIDTH - len(_("Long Description:"))) * " "
            + _("Long Description:"),
            end="",
        )
        for i in range(len(temp_strings)):
            if i == 0:
                print(" " + temp_strings[i])
            else:
                print((CMD_LEFT_CHAR_WIDTH + 1) * " " + temp_strings[i])

        # Print mitigation options
        for mitigation_option in threats_[0].mitigation_options:
            temp_string = wrap(
                mitigation_option, CMD_MAX_CHAR_WIDTH - CMD_LEFT_CHAR_WIDTH - 1
            )
            temp_strings = temp_string.split("\n")
            print(
                (CMD_LEFT_CHAR_WIDTH - len(_("Mitigation Option:"))) * " "
                + _("Mitigation Option:"),
                end="",
            )
            for i in range(len(temp_strings)):
                if i == 0:
                    print(" " + temp_strings[i])
                else:
                    print((CMD_LEFT_CHAR_WIDTH + 1) * " " + temp_strings[i])

        # Print requirements
        if len(threats_[0].requirement) > 0:
            temp_string = wrap(
                threats_[0].requirement, CMD_MAX_CHAR_WIDTH - CMD_LEFT_CHAR_WIDTH - 1
            )
            temp_strings = temp_string.split("\n")
            print(
                (CMD_LEFT_CHAR_WIDTH - len(_("Requirement:"))) * " "
                + _("Requirement:"),
                end="",
            )
            for i in range(len(temp_strings)):
                if i == 0:
                    print(" " + temp_strings[i])
                else:
                    print((CMD_LEFT_CHAR_WIDTH + 1) * " " + temp_strings[i])

        # Print each location where the threat occurs
        temp_string = _("Locations:")
        print((CMD_LEFT_CHAR_WIDTH - len(temp_string)) * " " + temp_string)
        for threat_ in threats_:
            temp_string = wrap(
                f"{threat_.location_str(dfd)}:",
                CMD_MAX_CHAR_WIDTH - CMD_LEFT_CHAR_WIDTH - 1,
            )
            temp_strings = temp_string.split("\n")
            for i in range(len(temp_strings)):
                print((CMD_LEFT_CHAR_WIDTH + 1) * " " + temp_strings[i])

            # Print status
            req_status_list = threat_.req_status.split("\n")
            for status in req_status_list:
                if status != "":
                    temp_string = wrap(
                        status, CMD_MAX_CHAR_WIDTH - CMD_LEFT_CHAR_WIDTH - 3
                    )
                    temp_strings = temp_string.split("\n")
                    for i in range(len(temp_strings)):
                        print(
                            settings.C_WARNING
                            + (CMD_LEFT_CHAR_WIDTH + 3) * " "
                            + temp_strings[i]
                            + settings.C_DEFAULT
                        )

            # Print management state and explanation
            threat_management_item = threat_management_database.get(threat_, dfd)
            temp_string = wrap(
                _("Management State:")
                + " {content}".format(content=threat_management_item.management_state),
                CMD_MAX_CHAR_WIDTH - CMD_LEFT_CHAR_WIDTH - 1,
            )
            temp_strings = temp_string.split("\n")
            for i in range(len(temp_strings)):
                print((CMD_LEFT_CHAR_WIDTH + 1) * " " + temp_strings[i])

            if len(threat_management_item.explanation) > 0:
                temp_string = wrap(
                    _("Management Explanation:")
                    + " {content}".format(content=threat_management_item.explanation),
                    CMD_MAX_CHAR_WIDTH - CMD_LEFT_CHAR_WIDTH - 1,
                )
                temp_strings = temp_string.split("\n")
                for i in range(len(temp_strings)):
                    print((CMD_LEFT_CHAR_WIDTH + 1) * " " + temp_strings[i])
            print()
        print()

    # Add references for used rule sets:
    if len(threats_) > 0:
        print(settings.C_HEADER + wrap(_("References:")) + settings.C_DEFAULT)
        for collection in all_collections:
            for tag in collection.tags:
                if tag in dfd.tags:
                    print()
                    print(wrap(collection.name + ":"))
                    for ref in collection.references:
                        print(wrap(text_to_wrap=ref, include_hyphen=False))

    return 0


def metadata_cmd(dfd_path: pathlib.Path, output_path: pathlib.Path, out_lang: str):
    # Set output language
    settings.init_localization(out_lang, "out")

    # Attempt to open file
    try:
        with open(dfd_path) as dfd_file:
            serialized_dfd = dfd_file.read()
    except FileNotFoundError:
        print(
            _(
                "Error: Specified file '{path}' not found. Check that the file"
                + " exists and that the location is correct."
            ).format(path=dfd_path)
        )
        return 1
    except IsADirectoryError:
        print(
            _(
                "Error: '{path}' is a directory. Please specify the path to a"
                + " .json file."
            ).format(path=dfd_path)
        )
        return 1
    except PermissionError:
        print(
            _(
                "Error: No permission to access '{path}'."
                + "Please specify a valid path to a"
                + " .json file."
            ).format(path=dfd_path)
        )
        return 1

    # Deserialize file in memory
    try:
        dfd: dataflowdiagram.DataflowDiagram = storage.deserialize_dfd(serialized_dfd)
    except JSONDecodeError as error:
        print(
            _("Error: There is a json error in file '{path}':\n{err}.").format(
                path=dfd_path, err=error
            )
        )
        return 1

    metadata_xsxl_converter.metadata_check(dfd, output_path)
    print(
        _(
            "Metadata file of diagram '{id}' saved to"
            + " '{out_path}'.\nAfter modifying the metadata"
            + " you can update the data-flow diagram with the command 'update'."
        ).format(id=dfd.id, out_path=output_path)
    )
    return 0


def update_cmd(dfd_path: pathlib.Path, metadata_path: pathlib.Path):
    # Set output language (important because attributes have to be initialized,
    # ...localization not actually used for updating (no real output))
    settings.init_localization("en", "out")

    try:
        with open(dfd_path) as dfd_file:
            serialized_dfd = dfd_file.read()
    except FileNotFoundError:
        print(
            _(
                "Error: Specified dfd file '{path}' not found. Check that the file"
                + " exists and that the location is correct."
            ).format(path=dfd_path)
        )
        return 1
    except IsADirectoryError:
        print(
            _(
                "Error: '{path}' is a directory. Please specify the path to a"
                + " .json file."
            ).format(path=dfd_path)
        )
        return 1
    except PermissionError:
        print(
            _(
                "Error: No permission to access '{path}'."
                + "Please specify a valid path to a"
                + " .json file."
            ).format(path=dfd_path)
        )
        return 1

    dfd: dataflowdiagram.DataflowDiagram = storage.deserialize_dfd(serialized_dfd)

    try:
        dfd = metadata_xsxl_converter.update_dfd_json_from_xlsx(dfd, metadata_path)
    except FileNotFoundError:
        print(
            _(
                "Error: Specified file '{path}' not found. Check that the file"
                + " exists and that the location is correct."
            ).format(path=metadata_path)
        )
        return 1
    except InvalidFileException:
        print(
            _(
                "Error: '{path}' is of wrong file format. Please specify the"
                + " path to a .xlsx file."
            ).format(path=metadata_path)
        )
        return 1
    except PermissionError:
        print(
            _(
                "Error: No permission to access '{path}'."
                + "Please specify a valid path to a"
                + " .xlsx file."
            ).format(path=metadata_path)
        )
        return 1

    serialized_dfd = storage.serialize_dfd(dfd)
    with open(dfd_path, "w") as dfd_file:
        dfd_file.write(serialized_dfd)

    print(
        _("Successfully updated diagram '{id}' in file '{path}'.").format(
            id=dfd.id, path=dfd_path
        )
    )
    return 0


if __name__ == "__main__":
    main()
