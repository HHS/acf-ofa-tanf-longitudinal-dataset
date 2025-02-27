Command Line Applications
=========================

The OFA TANF Longitudinal Dataset (OTLD) package was primarily developed
to handle the initial appending of OFA's financial and caseload TANF
data. To make future creation of appended files simpler and Tableau
related datasets simpler, however, we created a set of command line
applications that enable appending new data and creating output
datasets. This documentation describes these applications and their
usage.

Append
------

Description
~~~~~~~~~~~

The tanf-append command can be used to append a new year of data to an
existing appended data set. For example, given a dataset spanning
1997-1998, tanf-append can be used to append new data from 1999. Use
tanf-append-gui for a graphical user interface (GUI).

Examples
~~~~~~~~

.. code-block::

   > tanf-append caseload appended/CaseloadDataWide.xlsx -d to_append

.. code-block::

   > tanf-append caseload appended/CaseloadDataWide.xlsx -a to_append/fy_2024_tanf_caseload.xlsx to_append/fy_2024_ssp_caseload.xlsx to_append/fy_2024_tanfssp_caseload.xlsx

.. code-block::

   > set sheets="{""caseload"": {""TANF"": {""family"": ""fycy2024-families"", ""recipient"": ""fycy2024-recipients""}, ""SSP_MOE"": {""family"": ""Avg Month Num Fam"", ""recipient"": ""Avg Mo. Num Recipient""}, ""TANF_SSP"": {""family"": ""fycy2024-families"", ""recipient"": ""Avg Mo. Num Recipient""}}}"

   > tanf-append caseload appended/CaseloadDataWide.xlsx -d to_append -s %sheets%

.. code-block::

   > set sheets="{""financial"": {""Total"": ""B. Total Expenditures"", ""Federal"": ""C.1 Federal Expenditures"", ""State"": ""C.2 State Expenditures""}}"

   > tanf-append financial appended/FinancialDataWide.xlsx -d to_append -s %sheets%

.. code-block::

   > set footnotes="{""TANF"": [[""From 2002-2005 Guam's caseload data was imputed""], [""Another footnote""]], ""SSP_MOE"": [[""A third footnote""]]}"

   > tanf-append caseload appended/CaseloadDataWide.xlsx -d to_append -f %footnotes%

.. code-block::

   > tanf-append-gui

Documentation
~~~~~~~~~~~~~

-  usage: tanf-append [-h] (-a TO_APPEND [TO_APPEND …] \| -d DIRECTORY)
   [-s SHEETS] kind appended
-  positional arguments:

   -  kind: The type of data to append. Should be either caseload or
      financial.
   -  appended: The path to the base file (in wide format) containing
      appended data.

-  options:

   -  -h, –help: Show help message and exit.
   -  -a TO_APPEND [TO_APPEND …], –append TO_APPEND [TO_APPEND …]: List
      of files to append to the base file. One of -a or -d must be
      specified.
   -  -d Directory, –dir Directory: Directory in which to find files to
      append. One of -a or -d must be specified.
   -  -s SHEETS, –sheets SHEETS: List of sheets to extract from files to
      append. Only necessary if the default sheet options are failing.
      Should be a JSON formatted string (`see examples <#examples>`__).
   - -f FOOTNOTES, --footnotes FOOTNOTES: List of footnotes to include in appended files. Should be a JSON formatted string (`see examples <#examples>`__)
   - -t, --tableau: Generate an additional file without headers or footers suitable for use in the creation of tableau files.

Tableau
-------

.. _description-1:

Description
~~~~~~~~~~~

The tanf-tableau command generates Tableau-specific datasets. Use tanf-tableau-gui
for a GUI.

.. _documentation-1:

Examples
~~~~~~~~

.. code-block::

   > tanf-tableau financial appended/FinancialDataWide.xlsx tableau/data -i pce.csv

.. code-block::

   > tanf-tableau caseload appended/CaseloadDataWide.xlsx tableau/data

.. code-block::

   > tanf-tableau-gui

Documentation
~~~~~~~~~~~~~

-  usage: tanf-tableau [-h] [-i INFLATION] kind wide destination
-  positional arguments:

   -  kind: Input data type. Should be either caseload or financial.
   -  wide: Path to appended data in wide format.
   -  destination: Where to save the resultant dataset.

-  options:

   -  -h, –help: Show help message and exit.
   -  -i INFLATION: Path to the file containing PCE information. Used in
      calculating inflation-adjusted figures

.. _examples-1:
