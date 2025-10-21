######
ut_arr
######

********
Overview
********

.. start short_desc

**Utilities to manage Arrays**

.. end short_desc

************
Installation
************

.. start installation

Package ``ut_array`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ut_arr

***************
Package logging
***************

(c.f.: **Appendix**: `Package Logging`)

*************
Package files
*************

Classification
==============

The Files of Package ``ut_arr`` could be classified into the follwing file types (c.f.: **Appendix**: `Python Terminology`):

#. **Special files**

   a. *py.typed*

#. **Special modules**

   a. *__init__.py* 
   #. *__version__.py*

#. **Modules**

   #. **Modules for dictionaries**

      a. *dic.py*

   #. **Modules for dictionaries of arrays**

      a. *doaod.py*
      #. *doa.py*

   #. **Modules for dictionaries of callables**

      a. *doc.py**

   #. **Modules for dictionaries of dataframes**

      a. *dopddf.py*

Package Modules
===============

Overview
--------

The Modules of Package ``ut_arr`` could be classified into the follwing module types:

#. *Modules for arrays*
#. *Modules for arrays of arrays*
#. *Modules for arrays of basic objects*

******************
Modules for arrays
******************

The Module type ``Modules for arrays`` contains only the module ``arr.py``.


Module: arr.py
==============

The Module ``arr.py`` contains only the static class ``Arr``.

Class: Arr
----------

The Class ``Arr`` contains the following methods:

Arr Methods
^^^^^^^^^^^

  .. Arr-methods-label:
  .. table:: *Arr methods*

   +-----------------------+---------------------------------------------------+
   |Name                   |Short description                                  |
   +=======================+===================================================+
   |append                 |Append item to the array                           |
   +-----------------------+---------------------------------------------------+
   |append_unique          |Append item to the array if the item is not in the |
   |                       |array.                                             |
   +-----------------------+---------------------------------------------------+
   |apply_function         |Apply function with the keyword arguments to all   |
   |                       |non empty array elements.                          |
   +-----------------------+---------------------------------------------------+
   |apply_replace          |Replace source by target to all array elements.    |
   +-----------------------+---------------------------------------------------+
   |apply_str              |Apply function str to all non empty array elements.|
   +-----------------------+---------------------------------------------------+
   |encode                 |Join array elements with blank separator and encode|
   |                       |result string.                                     |
   +-----------------------+---------------------------------------------------+
   |ex_intersection        |Intersection of first array with second array.     |
   +-----------------------+---------------------------------------------------+
   |extend                 |Extend first array with second array.              |
   +-----------------------+---------------------------------------------------+
   |get_key_value          |Get next array item value without line feed for the|
   |                       |given index or the given default value if the item |
   |                       |value is identical to the given value without line |
   |                       |feeds.                                             |
   +-----------------------+---------------------------------------------------+
   |get_item               |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |get_text               |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |get_text_spli          |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |intersection           |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |is_empty               |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |is_not_empty           |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |join_not_none          |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |length                 |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |merge                  |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |sh_dic_from_keys_values|Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |sh_dic_zip             |Join elements of array of dicts.                   |
   +-----------------------+---------------------------------------------------+
   |sh_item                |Show True if an element exists in the array        |
   +-----------------------+---------------------------------------------------+
   |sh_item_if             |Show True if an element exists in the array        |
   +-----------------------+---------------------------------------------------+
   |sh_item_lower          |Show True if an element exists in the array        |
   +-----------------------+---------------------------------------------------+
   |sh_item_str            |Show True if an element exists in the array        |
   +-----------------------+---------------------------------------------------+
   |sh_item0               |Deduplicate array of dicts.                        |
   +-----------------------+---------------------------------------------------+
   |sh_item0_if            |Deduplicate array of dicts.                        |
   +-----------------------+---------------------------------------------------+
   |sh_subarray            |Deduplicate array of dicts.                        |
   +-----------------------+---------------------------------------------------+
   |to_dic                 |Show arr. of arrays created from arr. of dict.     |
   |                       |by using any key- and all value-arrays             |
   +-----------------------+---------------------------------------------------+
   |yield_items            |Convert array of dictionaries to array of          |
   |                       |arrays controlled by key- and value-switch.        |
   +-----------------------+---------------------------------------------------+

***************************
Modules for array of arrays
***************************

The Module type ``Modules for array of arrays`` contains only the module ``aoa.py``.

Module: aoa.py
==============

The Module ``aoa.py`` contains only the static class ``AoA``.

aoa.py Class: AoA
------------------

The static Class ``AoA`` contains the subsequent methods.

AoA Methods
^^^^^^^^^^^

  .. AoA-Methods-label:
  .. table:: *AoA Methods*

   +-----------------+-----------------------------------------+
   |Name             |Short description                        |
   +=================+=========================================+
   |concatinate      |Concatinate all arrays of array of arrays|
   +-----------------+-----------------------------------------+
   |csv_writerows    |Write array of arrays to csv file        |
   +-----------------+-----------------------------------------+
   |nvl              |Replace empty array of arrays            |
   +-----------------+-----------------------------------------+
   |to_aod           |Convert array of arrays to array of      |
   |                 |dictionaries using an array of keys      |
   +-----------------+-----------------------------------------+
   |to_arr_from_2cols|Convert array of arrays to array using   |
   |                 |a 2-dimensional index array              |
   +-----------------+-----------------------------------------+
   |to_doa_from_2cols|Convert array of arrays to dictionary of |
   |                 |arrays using a 2-dimensionl index array  |
   +-----------------+-----------------------------------------+
   |to_dic_from_2cols|Convert array of arrays to dictionary by |
   |                 |using a 2-dimensional index array        |
   +-----------------+-----------------------------------------+

AoA Method: concatinate
^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Concatinate all arrays of array of arrays.

Parameter
"""""""""

  .. Parameter-of-AoA-Method-concatinate-label:
  .. table:: *Parameter of: AoA Method: concatinate*

   +-------+-----+-------+---------------+
   |Name   |Type |Default|Description    |
   +=======+=====+=======+===============+
   |aoa    |TyAoA|       |Array of arrays|
   +-------+-----+-------+---------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-Method-concatinate-label:
  .. table:: *Return Value of: AoA Method: concatinate*

   +-------+-----+-----------+
   |Name   |Type |Description|
   +=======+=====+===========+
   |arr_new|TyArr|new array  |
   +-------+-----+-----------+

AoA Method: csv_writerows
^^^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Write Array of Arrays to Csv file defined by the path string 
using the function "writerows" of module "csv".

Parameter
"""""""""

  .. Parameter-of-AoA-Method-csv_writerows-label:
  .. table:: *Parameter of: AoA Method: csv_writerows*

   +------+------+----------------+
   |Name  |Type  |Description     |
   +======+======+================+
   |aoa   |TyAoA |Array of arrays |
   +------+------+----------------+
   |path  |TyPath|Path string     |
   +------+------+----------------+
   |kwargs|TyDic |Keyword aruments|
   +------+------+----------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-Method-AoA-writerows-label:
  .. table:: *Return Value of: AoA Method: csv_writerows*

   +------+------+----------------+
   |Name  |Type  |Description     |
   +======+======+================+
   |      |None  |                |
   +------+------+----------------+

AoA Method: nvl
^^^^^^^^^^^^^^^

Description
"""""""""""

Return the empty array if the Array of Arrays is None.

Parameter
"""""""""

  .. Parameter-of-AoA-Method-nvl-label:
  .. table:: *Parameter of: AoA Method nvl*

   +-------+-----+-------+-------------------+
   |Name   |Type |Default|Description        |
   +=======+=====+=======+===================+
   |aoa    |TyAoA|       |Array of arrays    |
   +-------+-----+-------+-------------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-method-AoA.nvl-label:
  .. table:: *Return Value of: AoA Method: nvl*

   +-------+-----+-------------------+
   |Name   |Type |Description        |
   +=======+=====+===================+
   |aoa_new|TyAoA|new Array of arrays|
   +-------+-----+-------------------+

AoA Method: to_aod
^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Convert array of arrays to array of Dictionaries.

Parameter
"""""""""

  .. Parameter-of-AoA-Method-to_aod-label:
  .. table:: *Parameter of: AoA Method: to_aod*

   +----+-----+-------+---------------+
   |Name|Type |Default|Description    |
   +====+=====+=======+===============+
   |aoa |TyAoA|       |Array of arrays|
   +----+-----+-------+---------------+
   |keys|TyArr|       |Array of keys  |
   +----+-----+-------+---------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-Method-to_aod-label:
  .. table:: *Return Value of: AoA Method: to_aod*

   +----+-----+---------------------+
   |Name|Type |Description          |
   +====+=====+=====================+
   |aod |TyAoD|array of dictionaries|
   +----+-----+---------------------+

AoA Method: to_arr_from_2cols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Convert Array of Arrays to unique array with distinct elements by
selecting 2 columns of each Array as elements of the new array using a
2-dimensional index-array.

Parameter
"""""""""

  .. Parameter-of-AoA-Method-to_arr_from_2cols-label:
  .. table:: *Parameter of: AoA Method: to_arr_from_2cols*

   +----+-----+-------+----------------+
   |Name|Type |Default|Description     |
   +====+=====+=======+================+
   |aoa |TyAoA|       |Array of arrays |
   +----+-----+-------+----------------+
   |a_ix|TyAoI|       |Array of integer|
   +----+-----+-------+----------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-Method-to_arr_from_2cols-label:
  .. table:: *Return Value of: AoA Method: to_arr_from_2cols*

   +----+-----+-------------------+
   |Name|Type |Description        |
   +====+=====+===================+
   |arr |TyArr|Array              |
   +----+-----+-------------------+

AoA Method: to_doa_from_2cols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Convert array of arrays to dictionary of unique arrays (array with distinct elements)

#. Select 2 columns of each array as key-, value-candidates of the new dictionary
   using a 2-dimensional index-array. 

#. If the new key exists then 
   the new value extends the key value as unique array, 
   
# otherwise
   the new value is assigned as unique array to the key.

Parameter
"""""""""

  .. Parameter-of-AoA-Method-to_doa_from_2cols-label:
  .. table:: *Parameter of: AoA Method: to_doa_from_2cols*

   +----+-----+-------+----------------+
   |Name|Type |Default|Description     |
   +====+=====+=======+================+
   |aoa |TyAoA|       |Array of arrays |
   +----+-----+-------+----------------+
   |a_ix|TyAoI|       |Array of integer|
   +----+-----+-------+----------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-Method-to_doa_from_2cols-label:
  .. table:: *Return Value of: AoA Method: to_doa_from_2cols*

   +----+-----+-------------------+
   |Name|Type |Description        |
   +====+=====+===================+
   |doa |TyDoA|Dictionry of arrays|
   +----+-----+-------------------+

AoA Method: to_dic_from_2cols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Convert array of arrays to dictionary by selecting 2 columns of each array as
key-, value-candidates of the new dictionary if the key is not none using a
2-dimensional index-array.

Parameter
"""""""""

  .. Parameter-of-AoA-Method-to_dic_from_2cols-label:
  .. table:: *Parameter of: AoA Method: to_dic_from_2cols*

   +----+-----+-------+----------------+
   |Name|Type |Default|Description     |
   +====+=====+=======+================+
   |aoa |TyAoA|       |Array of arrays |
   +----+-----+-------+----------------+
   |a_ix|TyAoI|       |Array of integer|
   +----+-----+-------+----------------+

Return Value
""""""""""""

  .. Return-Value-of-AoA-Method-to_dic_from_2cols-label:
  .. table:: *Return Value of: AoA Method: to_dic_from_2col**

   +----+-----+-----------+
   |Name|Type |Description|
   +====+=====+===========+
   |dic |TyDic|Dictionary |
   +----+-----+-----------+

****************************
Modules for array of objects
****************************

  .. Modules-for-array-of-dictionaries-label:
  .. table:: **Modules-for-array-of-dictionaries**

   +------+----------------+
   |Name  |Description     |
   +======+================+
   |aoo.py|Array of objects|
   +------+----------------+

Module: aoo.py
==============

The Module ``aoo.py`` contains the single static class ``AoO``;

aoo.py Class: AoO
-----------------

Methods
^^^^^^^

  .. AoO-Methods-label:
  .. table:: *AoO Methods*

   +---------+------------------------+
   |Name     |short Description       |
   +=========+========================+
   |to_unique|Concatinate array arrays|
   +---------+------------------------+

AoO Method: to_unique
^^^^^^^^^^^^^^^^^^^^^
   
Deduplicate array of objects

Parameter
"""""""""

  .. Parameter-of-AoO-Method-to_unique-label:
  .. table:: *Parameter of: AoO Method: to_unique*

   +----+-----+----------------+
   |Name|Type |Description     |
   +====+=====+================+
   |aoo |TyAoO|Array of objects|
   +----+-----+----------------+
   
Return Value
""""""""""""

  .. Return-Value-of-AoO-Method-to_unique-label:
  .. table:: *Return Value of: AoO Method: to_unique*

   +-------+-----+--------------------+
   |Name   |Type |Description         |
   +=======+=====+====================+
   |aoo_new|TyAoO|New array of objects|
   +-------+-----+--------------------+
   
**************
Module: aos.py
**************

Classes
=======

The Module ``aos.py`` contains the single static class ``AoS``;

Class: AoS
----------

AoS Methods
^^^^^^^^^^^

  .. AoS-Methods-label:
  .. table:: *AoS Methods*

   +-------------------------+------------------------------------------+
   |Name                     |short Description                         |
   +=========================+==========================================+
   |nvl                      |Replace empty array of strings            |
   +-------------------------+------------------------------------------+
   |sh_a_date                |Convert array of strings to array of dates|
   +-------------------------+------------------------------------------+
   |to_lower                 |Convert array of strings to array of      |
   |                         |lowered strings.                          |
   +-------------------------+------------------------------------------+
   |to_unique                |Deduplicate array of arrays               |
   +-------------------------+------------------------------------------+
   |to_unique_lower          |Convert array of strings to deduplicted   |
   |                         |array of lowered strings.                 |
   +-------------------------+------------------------------------------+
   |to_unique_lower_invariant|Convert array of arrays to array of arrays|
   +-------------------------+------------------------------------------+

Method: AoS.to_unique
^^^^^^^^^^^^^^^^^^^^^
   
Parameter
"""""""""

  .. Parameter-of-AoS-method-to_unique-label:
  .. table:: *Parameter of: AoS Method: to_unique*

   +----+-----+-------+----------------+
   |Name|Type |Default|Description     |
   +====+=====+=======+================+
   |aoo |TyAoO|       |array of objects|
   +----+-----+-------+----------------+

Return Value
""""""""""""

  .. Return Value-of-AoS-Method-to_unique-label:
  .. table:: *Return Value of: AoS Method: to_unique*

   +-------+-----+--------------------+
   |Name   |Type |Description         |
   +=======+=====+====================+
   |aoo_new|TyAoO|new array of objects|
   +-------+-----+--------------------+

########
Appendix
########

***************
Package Logging
***************

Description
===========

Logging use the module **log.py** of the logging package **ut_log**.
The module supports two Logging types:

#. **Standard Logging** (std) or 
#. **User Logging** (usr).

The Logging type can be defined by one of the values 'std' or 'usr' of the parameter log_type; 'std' is the default.
The different Logging types are configured by one of the following configuration files:

#. **log.std.yml** or 
#. **log.usr.yml** 
  
The configuration files can be stored in different configuration directories (ordered by increased priority):

#. <package directory of the log package **ut_log**>/**cfg**,
#. <package directory of the application package **ui_eviq_srr**>/**cfg**,
#. <application directory of the application **eviq**>/**cfg**,

The active configuration file is the configuration file in the directory with the highest priority.

Examples
========
  
Site-packages-path = **/appl/eviq/.pyenv/versions/3.11.12/lib/python3.11/site-packages**
Log-package = **ut_log**
Application-package = **ui_eviq_srr**
Application-home-path = **/appl/eviq**
  
.. Examples-of-log-configuration-files-label:
.. table:: **Examples of log configuration-files**

   +-----------------------------------------------------------------------------------+
   |Log Configuration                                                                  |
   +----+-------------------+----------------------------------------------+-----------+
   |Type|Directory Type     |Directory                                     |File       |
   +====+===================+==============================================+===========+
   |std |Log package        |<Site-packages-path>/<Log-package>/cfg        |log.std.yml|
   |    +-------------------+----------------------------------------------+           |
   |    |Application package|<Site-packages-path>/<application-package>/cfg|           |
   |    +-------------------+----------------------------------------------+           |
   |    |Application        |<application-home-path>/cfg                   |           |
   +----+-------------------+----------------------------------------------+-----------+
   |usr |Log package        |<site-packages-path>/ut_log/cfg               |log.usr.yml|
   |    +-------------------+----------------------------------------------+           |
   |    |Application package|<site-packages-path>/ui_eviq_srr/cfg          |           |
   |    +-------------------+----------------------------------------------+           |
   |    |Application        |<application-path>/cfg                        |           |
   +----+-------------------+----------------------------------------------+-----------+

Log message types
=================

Logging defines log file path names for the following log message types: .

#. *debug*
#. *info*
#. *warning*
#. *error*
#. *critical*

Log types and Log directories
-----------------------------

Single or multiple Application log directories can be used for each message type:

.. Log-types-and-Log-directories-label:
.. table:: *Log types and directoriesg*

   +--------------+---------------+
   |Log type      |Log directory  |
   +--------+-----+--------+------+
   |long    |short|multiple|single|
   +========+=====+========+======+
   |debug   |dbqs |dbqs    |logs  |
   +--------+-----+--------+------+
   |info    |infs |infs    |logs  |
   +--------+-----+--------+------+
   |warning |wrns |wrns    |logs  |
   +--------+-----+--------+------+
   |error   |errs |errs    |logs  |
   +--------+-----+--------+------+
   |critical|crts |crts    |logs  |
   +--------+-----+--------+------+

Application parameter for logging
---------------------------------

.. Application-parameter-used-in-log-naming-label:
.. table:: *Application parameter used in log naming*

   +-----------------+--------------+-----+------------------+-------+-----------+
   |Name             |Decription    |Value|Description       |Default|Example    |
   +=================+==============+=====+==================+=======+===========+
   |appl_data        |data directory|     |                  |       |/data/eviq |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |tenant           |tenant name   |UMH  |                  |       |UMH        |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |package          |package name  |     |                  |       |ui_eviq_srr|
   +-----------------+--------------+-----+------------------+-------+-----------+
   |cmd              |command       |     |                  |       |evupreg    |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |log_type         |Logging Type  |std: |Standard logging  |std    |std        |
   |                 |              +-----+------------------+       |           |
   |                 |              |usr: |User Logging      |       |           |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |log_ts_type      |Logging       |ts:  |Sec since 1.1.1970|ts     |ts         |
   |                 |timestamp     +-----+------------------+       |           |
   |                 |type          |dt:  |Datetime          |       |           |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |log_sw_single_dir|Use single log|True |use single dir.   |True   |True       |
   |                 |directory     +-----+------------------+       |           |
   |                 |              |False|use muliple dir.  |       |           |
   +-----------------+--------------+-----+------------------+-------+-----------+

Log files naming
----------------

Naming Conventions (table format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Naming-conventions-for-logging-file-paths-label:
.. table:: *Naming conventions for logging file paths*

   +--------+----------------------------------------------+-------------------+
   |Type    |Directory                                     |File               |
   +========+==============================================+===================+
   |debug   |/<appl_data>/<tenant>/RUN/<package>/<cmd>/debs|debs_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |critical|/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|crts_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |error   |/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|errs_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |info    |/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|infs_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |warning |/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|rnsg_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+

Naming Conventions (tree format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

 <appl_data>   Application data folder
 │
 └── <tenant>  Application tenant folder
     │
     └── RUN  Applications RUN folder for Application log files
         │
         └── <package>  RUN folder of Application package: <package>
             │
             └── <cmd>  RUN folder of Application command <cmd>
                 │
                 ├── debs  Application command debug messages folder
                 │   │
                 │   └── debs_<ts>_<pid>.log  debug messages for
                 │                            run of command <cmd>
                 │                            with pid <pid> at <ts>
                 │
                 └── logs  Application command log messages folder
                     │
                     ├── crts_<ts>_<pid>.log  critical messages for
                     │                        run of command <cmd>
                     │                        with pid <pid> at <ts>
                     ├── errs_<ts>_<pid>.log  error messages for
                     │                        run of command <cmd>
                     │                        with pid <pid> at <ts>
                     ├── infs_<ts>_<pid>.log  info messages for
                     │                        run of command <cmd>
                     │                        with pid <pid> at <ts>
                     └── wrns_<ts>_<pid>.log  warning messages for
                                              run of command <cmd>
                                              with pid <pid> at <ts>

Naming Examples (table format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Naming-conventions-for-logging-file-paths-label:
.. table:: *Naming conventions for logging file paths*

   +--------+--------------------------------------------+--------------------------+
   |Type    |Directory                                   |File                      |
   +========+============================================+==========================+
   |debug   |/appl/eviq/UMH/RUN/ui_eviq_srr/evdomap/debs/|debs_1750096540_354710.log|
   +--------+--------------------------------------------+--------------------------+
   |critical|/appl/eviq/UMH/RUN/ui_eviq_srr/evdomap/logs/|crts_1749971151_240257.log|
   +--------+                                            +--------------------------+
   |error   |                                            |errs_1749971151_240257.log|
   +--------+                                            +--------------------------+
   |info    |                                            |infs_1750096540_354710.log|
   +--------+                                            +--------------------------+
   |warning |                                            |wrns_1749971151_240257.log|
   +--------+--------------------------------------------+--------------------------+

Naming Examples (tree format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

  /data/eviq/UMH/RUN/ui_eviq_srr/evdomap  Run folder of
  │                                       of function evdomap
  │                                       of package ui_eviq_srr
  │                                       for teanant UMH
  │                                       of application eviq
  │
  ├── debs  debug folder of Application function: evdomap
  │   │
  │   └── debs_1748609414_314062.log  debug messages for run 
  │                                   of function evdomap     
  │                                   using pid: 314062 at: 1748609414
  │
  └── logs  log folder of Application function: evdomap
      │
      ├── errs_1748609414_314062.log  error messages for run
      │                               of function evdomap     
      │                               with pid: 314062 at: 1748609414
      ├── infs_1748609414_314062.log  info messages for run
      │                               of function evdomap     
      │                               with pid: 314062 at: 1748609414
      └── wrns_1748609414_314062.log  warning messages for run
                                      of function evdomap     
                                      with pid: 314062 at: 1748609414

Configuration files
===================

log.std.yml (jinja2 yml file)
-----------------------------

Content
^^^^^^^

.. log.std.yml-label:
.. code-block:: jinja

 version: 1

 disable_existing_loggers: False

 loggers:

     # standard logger
     std:
         # level: NOTSET
         level: DEBUG
         handlers:
             - std_debug_console
             - std_debug_file
             - std_info_file
             - std_warning_file
             - std_error_file
             - std_critical_file

 handlers:
 
     std_debug_console:
         class: 'logging.StreamHandler'
         level: DEBUG
         formatter: std_debug
         stream: 'ext://sys.stderr'

     std_debug_file:
         class: 'logging.FileHandler'
         level: DEBUG
         formatter: std_debug
         filename: '{{dir_run_debs}}/debs_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_info_file:
         class: 'logging.FileHandler'
         level: INFO
         formatter: std_info
         filename: '{{dir_run_infs}}/infs_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_warning_file:
         class: 'logging.FileHandler'
         level: WARNING
         formatter: std_warning
         filename: '{{dir_run_wrns}}/wrns_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_error_file:
         class: 'logging.FileHandler'
         level: ERROR
         formatter: std_error
         filename: '{{dir_run_errs}}/errs_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true
 
     std_critical_file:
         class: 'logging.FileHandler'
         level: CRITICAL
         formatter: std_critical
         filename: '{{dir_run_crts}}/crts_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_critical_mail:
         class: 'logging.handlers.SMTPHandler'
         level: CRITICAL
         formatter: std_critical_mail
         mailhost : localhost
         fromaddr: 'monitoring@domain.com'
         toaddrs:
             - 'dev@domain.com'
             - 'qa@domain.com'
         subject: 'Critical error with application name'
 
 formatters:

     std_debug:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_info:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_warning:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_error:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_critical:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_critical_mail:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'

Jinja2-variables
^^^^^^^^^^^^^^^^

.. log.std.yml-Jinja2-variables-label:
.. table:: *log.std.yml Jinja2 variables*

   +------------+-----------------------------+-------------------------------------------+
   |Name        |Definition                   |Example                                    |
   +============+=============================+===========================================+
   |dir_run_debs|debug run directory          |/data/eviq/UMH/RUN/ui_eviq_srr/evupreg/debs|
   +------------+-----------------------------+-------------------------------------------+
   |dir_run_infs|info run directory           |/data/eviq/UMH/RUN/ui_eviq_srr/evupreg/logs|
   +------------+-----------------------------+                                           |
   |dir_run_wrns|warning run directory        |                                           |
   +------------+-----------------------------+                                           |
   |dir_run_errs|error run directory          |                                           |
   +------------+-----------------------------+                                           |
   |dir_run_crts|critical error run directory |                                           |
   +------------+-----------------------------+-------------------------------------------+
   |ts          |Timestamp since 1970 in [sec]|1749483509                                 |
   |            |if log_ts_type == 'ts'       |                                           |
   |            +-----------------------------+-------------------------------------------+
   |            |Datetime in timezone Europe/ |20250609 17:38:29 GMT+0200                 |
   |            |Berlin if log_ts_type == 'dt'|                                           |
   +------------+-----------------------------+-------------------------------------------+
   |pid         |Process ID                   |79133                                      |
   +------------+-----------------------------+-------------------------------------------+

***************
Python Glossary
***************

.. _python-modules:

Python Modules
==============

Overview
--------

  .. Python-Modules-label:
  .. table:: *Python Modules*

   +--------------+---------------------------------------------------------+
   |Name          |Definition                                               |
   +==============+==========+==============================================+
   |Python modules|Files with suffix ``.py``; they could be empty or contain|
   |              |python code; other modules can be imported into a module.|
   +--------------+---------------------------------------------------------+
   |special Python|Modules like ``__init__.py`` or ``main.py`` with special |
   |modules       |names and functionality.                                 |
   +--------------+---------------------------------------------------------+

.. _python-functions:

Python Modules
Python Function
===============

Overview
--------

  .. Python-Function-label:
  .. table:: *Python Function*

   +---------------+---------------------------------------------------------+
   |Name           |Definition                                               |
   +===============+==========+==============================================+
   |Python function|Files with suffix ``.py``; they could be empty or contain|
   |               |python code; other modules can be imported into a module.|
   +---------------+---------------------------------------------------------+
   |special Python |Modules like ``__init__.py`` or ``main.py`` with special |
   |modules        |names and functionality.                                 |
   +---------------+---------------------------------------------------------+

.. _python-packages:

Python Packages
===============

Overview
--------

  .. Python Packages-Overview-label:
  .. table:: *Python Packages Overview*

   +---------------------+---------------------------------------------+
   |Name                 |Definition                                   |
   +=====================+=============================================+
   |Python package       |Python packages are directories that contains|
   |                     |the special module ``__init__.py`` and other |
   |                     |modules, sub packages, files or directories. |
   +---------------------+---------------------------------------------+
   |Python sub-package   |Python sub-packages are python packages which|
   |                     |are contained in another python package.     |
   +---------------------+---------------------------------------------+
   |Python package       |directory contained in a python package.     |
   |sub-directory        |                                             |
   +---------------------+---------------------------------------------+
   |Python package       |Python package sub-directories with a special|
   |special sub-directory|meaning like data or cfg                     |
   +---------------------+---------------------------------------------+

Special python package sub-directories
--------------------------------------

  .. Special-python-package-sub-directory-Examples-label:
  .. table:: *Special python package sub-directories*

   +-------+------------------------------------------+
   |Name   |Description                               |
   +=======+==========================================+
   |bin    |Directory for package scripts.            |
   +-------+------------------------------------------+
   |cfg    |Directory for package configuration files.|
   +-------+------------------------------------------+
   |data   |Directory for package data files.         |
   +-------+------------------------------------------+
   |service|Directory for systemd service scripts.    |
   +-------+------------------------------------------+

.. _python-files:

Python Files
============

Overview
--------

  .. Python-files-label:
  .. table:: *Python files*

   +--------------+---------------------------------------------------------+
   |Name          |Definition                                               |
   +==============+==========+==============================================+
   |Python modules|Files with suffix ``.py``; they could be empty or contain|
   |              |python code; other modules can be imported into a module.|
   +--------------+---------------------------------------------------------+
   |Python package|Files within a python package.                           |
   |files         |                                                         |
   +--------------+---------------------------------------------------------+
   |Python dunder |Python modules which are named with leading and trailing |
   |modules       |double underscores.                                      |
   +--------------+---------------------------------------------------------+
   |special       |Files which are not modules and used as python marker    |
   |Python files  |files like ``py.typed``.                                 |
   +--------------+---------------------------------------------------------+
   |special Python|Modules like ``__init__.py`` or ``main.py`` with special |
   |modules       |names and functionality.                                 |
   +--------------+---------------------------------------------------------+

.. _python-special-files:

Python Special Files
--------------------

  .. Python-special-files-label:
  .. table:: *Python special files*

   +--------+--------+--------------------------------------------------------------+
   |Name    |Type    |Description                                                   |
   +========+========+==============================================================+
   |py.typed|Type    |The ``py.typed`` file is a marker file used in Python packages|
   |        |checking|to indicate that the package supports type checking. This is a|
   |        |marker  |part of the PEP 561 standard, which provides a standardized   |
   |        |file    |way to package and distribute type information in Python.     |
   +--------+--------+--------------------------------------------------------------+

.. _python-special-modules:

Python Special Modules
----------------------

  .. Python-special-modules-label:
  .. table:: *Python special modules*

   +--------------+-----------+----------------------------------------------------------------+
   |Name          |Type       |Description                                                     |
   +==============+===========+================================================================+
   |__init__.py   |Package    |The dunder (double underscore) module ``__init__.py`` is used to|
   |              |directory  |execute initialisation code or mark the directory it contains   |
   |              |marker     |as a package. The Module enforces explicit imports and thus     |
   |              |file       |clear namespace use and call them with the dot notation.        |
   +--------------+-----------+----------------------------------------------------------------+
   |__main__.py   |entry point|The dunder module ``__main__.py`` serves as package entry point |
   |              |for the    |point. The module is executed when the package is called by the |
   |              |package    |interpreter with the command **python -m <package name>**.      |
   +--------------+-----------+----------------------------------------------------------------+
   |__version__.py|Version    |The dunder module ``__version__.py`` consist of assignment      |
   |              |file       |statements used in Versioning.                                  |
   +--------------+-----------+----------------------------------------------------------------+

Python classes
==============

Overview
--------

  .. Python-classes-overview-label:
  .. table:: *Python classes overview*

   +-------------------+---------------------------------------------------+
   |Name               |Description                                        |
   +===================+===================================================+
   |Python class       |A class is a container to group related methods and|
   |                   |variables together, even if no objects are created.|
   |                   |This helps in organizing code logically.           |
   +-------------------+---------------------------------------------------+
   |Python static class|A class which contains only @staticmethod or       |
   |                   |@classmethod methods and no instance-specific      |
   |                   |attributes or methods.                             |
   +-------------------+---------------------------------------------------+

Python methods
==============

Overview
--------

  .. Python-methods-overview-label:
  .. table:: *Python methods overview*

   +--------------+-------------------------------------------+
   |Name          |Description                                |
   +==============+===========================================+
   |Python method |Python functions defined in python modules.|
   +--------------+-------------------------------------------+
   |Python class  |Python functions defined in python classes.|
   |method        |                                           |
   +--------------+-------------------------------------------+
   |Python special|Python class methods with special names and|
   |class method  |functionalities.                           |
   +--------------+-------------------------------------------+

Python class methods
--------------------

  .. Python-class-methods-label:
  .. table:: *Python class methods*

   +--------------+----------------------------------------------+
   |Name          |Description                                   |
   +==============+==============================================+
   |Python no     |Python function defined in python classes and |
   |instance      |decorated with @classmethod or @staticmethod. |
   |class method  |The first parameter conventionally called cls |
   |              |is a reference to the current class.          |
   +--------------+----------------------------------------------+
   |Python        |Python function defined in python classes; the|
   |instance      |first parameter conventionally called self is |
   |class method  |a reference to the current class object.      |
   +--------------+----------------------------------------------+
   |special Python|Python class functions with special names and |
   |class method  |functionalities.                              |
   +--------------+----------------------------------------------+

Python special class methods
----------------------------

  .. Python-methods-examples-label:
  .. table:: *Python methods examples*

   +--------+-----------+--------------------------------------------------------------+
   |Name    |Type       |Description                                                   |
   +========+===========+==============================================================+
   |__init__|class      |The special method ``__init__`` is called when an instance    |
   |        |object     |(object) of a class is created; instance attributes can be    |
   |        |constructor|defined and initalized in the method. The method us a single  |
   |        |method     |parameter conventionally called ``self`` to access the object.|
   +--------+-----------+--------------------------------------------------------------+

#################
Table of Contents
#################

.. contents:: **Table of Content**
