=========
Changelog
=========

..
    [MAJOR.MINOR.PATCH] YYYY-MM-DD
    ===========

    Added
    -----

    Changed
    -------

    Fixed
    -----

[1.1.0] 2025-10-21
========================
Added
-----
- integrated Linddun ruleset into FlowStrider
- implemented a severity factor for prioritization
- automatic language detection and localization
- option to set the language for reports
- ability to specify custom paths for report and management files
- added references to reports and tool output
- enabled Bandit rule checking in Ruff

Changed
-------
- sorted threats in pdf report by severity
- enhanced and expanded documentation (particularly data flow diagram and tool workflow sections)
- refined BSI rules
- replaced isort, Black, and Flake8 with Ruff

Fixed
-----
- minor layout adjustments to the PDF report
- resolved minor issues with attribute handling


[1.0.1] 2025-07-16
========================
Fixed
-----
resolve missing localization files in built package

[1.0.0] 2025-07-16
========================

first release
