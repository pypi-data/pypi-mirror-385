## 7.4.0 (2025-10-20)

### Feat

- add filter option to get_clients for school filter

### Fix

- **data.sampleconfig.yml**: set debugging level to INFO by default

### Refactor

- move cli code from managers.py to cli.py
- **cli**: move command functions to the top of the file to improve readability

## 7.3.0 (2025-10-14)

### Feat

- **tui.editclient**: add key binding for save
- allow setting paths to lgvt convenience files in the config

### Fix

- **cli.py**: respect logging level from config

## 7.2.0 (2025-10-09)

### Feat

- add 'andere' as an option for lrst_last_test_by_encr

### Fix

- **tui.editconfig**: add back title to config editor

## 7.1.0 (2025-10-07)

### Feat

- **api.managers**: improve the formatting of output for get_clients with --client_id
- accept several client_id values for create_documentation

### Fix

- **api.managers**: correctly import telephone numbers from csv

## 7.0.0 (2025-10-06)

### BREAKING CHANGE

- The database now includes two integer variables to describe sessions: min_sessions and n_sessions. The float variable h_sessions is removed.
- Rename and encrypt lrst_last_test_date > lrst_last_test_date_encr and lrst_last_test_by > lrst_last_test_by_encr.
- The name and type of two variables has changed: lrst_diagnosis > lrst_diagnosis_encr, keyword_taetigkeitsbericht > keyword_taet_encr
- The data type of nta_nos_end_grade has changed from String to Integer in the database.

### Feat

- allow the user to set mappings for csv imports in config.yml
- **api.taetigkeitsbericht_from_db**: update the taetigkeitsbericht code to use n_sessions and min_sessions and from config nstudents
- use a min_sessions and n_sessions variable instead of a h_sessions variable
- **db.clients**: encrypt lrst_last_test_date_encr and lrst_last_test_by_encr
- **api.managers**: validate keys in edit_client
- **db.clients**: encrypt lrst_diagnosis_encr and keyword_taet_encr

### Fix

- **db.clients**: fix spelling mistake
- **db.clients**: correct the data type of nta_nos_end_grade and pass only bool to _update_nachteilsausgleich

### Refactor

- **tui.editconfig**: refactor to use compound widgets
- **core.encrypt**: change misleading variable name
- improve type hints
- **core.config**: refactor to use pydantic and simplify to a single configuration file
- **api.managers**: remove unused function

## 6.3.0 (2025-09-18)

### Feat

- **api.managers**: improve error messages when user input is incorrect

## 6.2.0 (2025-09-18)

### Feat

- **tui.editconfig**: add nstudents to school config
- **tui**: add cancel and delete buttons, validation, and bindings
- add option to display clients overview with textual DataTable

### Fix

- **tui.editconfig**: fix crash when deleting items in config_editor
- **sampleconfig.yml**: add nstudents
- **tui**: add missing await, refactor containers and bindings, add test
- **api.managers**: run the ClientsOverview app

### Refactor

- **api.managers**: improve data handling and efficiency in managers

## 6.1.1 (2025-07-30)

### Fix

- **tui.editconfig**: increase the hight of RichLog widget to show all validation failure messages

## 6.1.0 (2025-07-27)

### Feat

- **tui.editclient**: validate lrst_diagnosis

## 6.0.0 (2025-07-23)

### Fix

- add the --min_per_ses parameter back to taetigkeitsbericht to estimate n_sessions correctly

## 6.0.0a1 (2025-07-23)

### Fix

- **tui.editconfig**: insert new form_sets after the last form_set
- **tui.editconfig**: allow adding a path right after renaming a form_set

## 6.0.0a0 (2025-07-22)

### BREAKING CHANGE

- edupsyadmin set_client now requires the flag --key_value_pairs before key-value pairs passed from the cli
- The renaming of ORM attributes nta_notes > nta_nos_notes and n_sessions > h_sessions requires a corresponding renaming of database columns.

### Feat

- **tui.editconfig**: allow adding a form_set
- **tui.editclient**: validate input to the school input widget
- accept multiple client_ids for set_client for bulk edits
- **tui.editclient**: use textual input validation for dates

### Fix

- **taetigkeitsbericht_from_db**: fix variable naming error
- **cli**: remove obsolete min_per_ses argument
- **taetigkeitsbericht_from_db**: accept h_sessions (hours) instead of n_sessions (number of arbitrarily long sessions)

### Refactor

- rename nta_notes > nta_nos_notes and n_sessions > h_sessions

## 5.1.0 (2025-07-15)

### Feat

- **add_convenience_data**: add workaround to fill lrst_last_test_by radio buttons

### Fix

- **editconfig**: do try to set password if password input widget has no value
- **managers**: replace python or with sqlalchemy or_
- **managers**: correct column names
- **cli**: set default value for key_value_pairs in set_client to None

## 5.0.0 (2025-07-14)

## 5.0.0b0 (2025-07-14)

### Fix

- **editclient**: handle checkboxes and bool values correctly
- **clients**: handle string end grade from config by converting it to int
- check what values were changed in the tui within the tui.editclient module
- **managers**: fix enter_client_cli to use only modified values
- **clients**: fix validates method for zeitverlängerung int from string
- **clients**: fix incorrect method name fromisoformat

## 5.0.0a1 (2025-07-13)

### Fix

- **tui.editclient**: set default None for client_id

## 5.0.0a0 (2025-07-13)

### BREAKING CHANGE

- adds lrst_last_test_by and nos_other cols and renames the lrst_last_test col

### Feat

- use tui.editclient for both new clients and editing clients
- move encryption calls to custom TypeDecorator
- **clients**: for gender, convert 'd' to 'x' and document the options f/m/x
- **tui.editclient**: check date input
- **tui.editclient**: hide class_int which is derived from class_name
- **tui.editclient**: hide fields that should not be set by the user
- **tui**: make some fields required and highlight them if no value is set
- **tui.editclient**: add tooltips
- handle all dates the same and add lrst_last_test_by and nos_other cols
- **tui.editconfig**: prevent overwriting an existing password
- **tui.editconfig**: call keyring.set_password when saving config
- **tui.editclient**: add float and date input widgets
- **tui.editconfig**: add password widget
- **tui.editconfig**: insert new schools after the last school
- **tui.editconfig**: close app when save button is pressed
- **tui.editconfig**: add tooltips
- **tui.editconfig**: allow adding paths to a form set
- **tui.editconfig**: allow end users to edit the school_key of an existing school entry
- **cli**: add the edit_config subcommand
- **tui.editconfig**: allow adding a new school to the config
- **tui.editconfig**: create tui to edit the config
- **tui.editclient**: suppress irrelevant keys for integer fields

### Fix

- **tui.editclient**: fix variable spelling
- **clients**: make the type of entry_date datetime.date
- **taetigkeitsbericht_check_key**: check_key demanded cli input when the key was not in the list of allowed keys
- **tui.editclient**: use DateInput and prevent dashes in the wrong position
- **add_convenience_data**: update add_convenience_data to reflect changes in data types to date
- **clients.py**: fix the constraint for lrst_last_test_by
- **clients.py**: fix the name of estimated_graduation_date in the constructor
- **tui.editclient**: fix spelling mistakes
- **tui.editconfig**: set encoding to utf-8
- **tui.editclient**: convert int input to int and handle non-character key presses
- pass missing arguments to the tui function

### Refactor

- refactor according to ruff rules
- **clients**: remove redundant code in __init__()
- **managers**: refactor for readability
- **managers**: remove redundant list of boolean db columns
- **clients**: remove redundant code in validates methods
- **managers**: use session.get instead of session.query for better readability
- move code without user I/O to core
- **tui.editclient**: read field names from the Client model
- **tui**: move tui code into its own submodule
- **cli.py**: fix import of importlib
- **fill_form.py**: improve type hint and add underscore for private method

## 4.0.0 (2025-06-10)

### BREAKING CHANGE

- adds a new column lrst_last_test to the database
- old databases will need to be upgraded by adding an nta_nos_end_grade and a nta_nos_end column
- the name of some fields added by the add_convenience_data function chages; removed the nta_measures and nos_measures generated by add_convenience data

### Feat

- **clients.py**: add lrst_last_test
- add nta_nos_end_grade column to the database
- add tui for editing clients

### Fix

- **add_convenience_data**: handle lrst_last_test=None
- **cli.py**: fix type hinting
- **clients.py**: fix type errors
- **add_convenience_data.py**: add lrst_last_test_de
- **managers.py**: convert 1 and 0 to bool in set_client
- **clients.py**: validate nta_zeitv_vieltext and nta_zeitv_wenigtext to turn strings into int
- **tui.py**: fix incorrect checkbox attribute and on_button_pressed call

### Refactor

- **reports.py**: improve type hints
- use fpdf2 (instead of fpdf2)
- correct import path for `__version__` to avoid potential import errors
- **encrypt.py**: remove superfluous type check
- **encrypt.py**: return a string from encrypt
- add type hints and improve docstrings
- make add_convenience_data consistent and document it better

## 4.0.0a0 (2025-04-08)

### BREAKING CHANGE

- add new variable to db model (nos_rs)
- several nta client attributes were renamed which will break any forms you used with edupsyadmin

### Feat

- **clients.py**: add nos_rs to db model
- add some nta attributes to clients, rename some, add setters and getters

### Fix

- **cli.py**: make lazy imports truly lazy
- **clients.py**: replace getters and setters with @validates functions
- **clients.py**: add correct column name to mapped_column calls with private attributes

### Refactor

- **cli.py**: use lazy import to speed up execution
- **config.py**: remove the option to use environment variables for config

## 3.3.1 (2025-03-20)

### Refactor

- change logging level from warning to lower level where possible

## 3.3.0 (2025-03-19)

### Feat

- **managers.py**: show all nta columns for get_clients

### Fix

- handle backslashes in windows paths for form_set
- **managers.py**: fix get_clients when used with a single client_id
- **cli.py**: remove duplicate logging

### Refactor

- **uv.lock**: update dependencies
- **add_convenience_data.py**: remove ns_zeugnisbemerkung

## 3.2.1 (2025-03-17)

### Fix

- **fill_form.py**: replace None with an empty string for fill_form
- **add_convenience_data.py**: allow None values for lrst_diagnosis
- **add_convenience_data.py**: correct spelling of Lese-Rechtschreib-Störung

## 3.2.0 (2025-03-17)

### Feat

- **add_convenience_data.py**: add lrst_diagnosis_long for forms
- add a delete_client subcommand to the cli

### Fix

- **shellscripts**: update lrst shellscripts
- **managers.py**: handle 0 and 1 instead of True/False for set_client
- **add_convenience_data.py**: remove automatic setting of nta_font
- **cli.py**: fix call of the delete_client subcommand

## 3.1.2 (2025-03-10)

### Fix

- **clients.py**: initialize nta boolean attributes properly

## 3.1.1 (2025-03-04)

### Fix

- **taetigkeitsbericht_check_key.py**: fix the path to the taetigkeitsbericht_categories file

## 3.1.0 (2025-03-03)

### Feat

- **clients.py**: add types of nta as new columns to database

### Refactor

- **managers.py**: show lrst_diagnosis in the overview
- expose core and init for imports of edupsyadmin
- remove obsolete shellscripts

## 3.0.0 (2025-02-24)

### BREAKING CHANGE

- the lrst_diagnosis variable is no longer encrypted and the taetigkeitsbericht keyword is now encrypted in the database

### Fix

- **lgvt.py**: change config_path to salt_path

### Refactor

- read taetigkeitsbericht keys from a csv file instead of ods
- encrypt gender and leave lrst_diagnosis unencrypted
- **clients.py**: change todo comment for lrst_diagnosis

## 2.0.1 (2025-02-17)

### Fix

- **cli.py**: use args.config_path[0] to copy the sample config if missing

## 2.0.0 (2025-02-11)

### BREAKING CHANGE

- the salt value will no longer be read from the config.yml file

### Feat

- **encrypt.py**: use a separate salt file instead of the config.yml
- add get_clients to the cli and managers.py

### Fix

- **cli.py**: change the default for --config to a list
- **encrypt.py**: add a missing f before a logging fstring
- use salt_path consistently

### Refactor

- **managers.py**: remove superfluous warning
- move the convert_config_to_dict function removed in the last commit to config.py

## 2.0.0b1 (2025-01-07)

## 2.0.0b0 (2025-01-06)

### Feat

- **add_convenience_data.py**: add schoolpsy_address_multiline to convenience data

### Fix

- handle the fact that config_path is a list not a string
- **sampleconfig.yml**: change the field name for uid from uid to app_uid

### Refactor

- **clients.py**: add nta arguments to the constructor for clients
- **test_encrypt.py**: use the mock_config fixture from conftest.py

## 1.0.0b0 (2025-01-04)

### BREAKING CHANGE

- new_client --csv now requires a --name argument

### Feat

- handle the extraction of a student from a webuntis csv with several rows

### Fix

- **encrypt.py**: don't load the config file in encrypt.py
- **cli.py**: handle config files correctly
- **cli.py**: catch KeyError exception when no app_username is set

### Refactor

- remove redundant scripts
- **fill_form.py**: raise FileNotFoundError
- refactor tests
- mock keyring for testing
- use importlib.resources.files instead of deprecated path
- **pyproject.toml**: change name of dependency group to bwbackend

## 1.0.0 (2025-01-06)

### Fix

- handle the fact that config_path is a list not a string

## 1.0.0b1 (2025-01-06)

### Feat

- **add_convenience_data.py**: add schoolpsy_address_multiline to convenience data

### Fix

- **sampleconfig.yml**: change the field name for uid from uid to app_uid

### Refactor

- **clients.py**: add nta arguments to the constructor for clients
- **test_encrypt.py**: use the mock_config fixture from conftest.py

## 1.0.0b0 (2025-01-04)

### BREAKING CHANGE

- new_client --csv now requires a --name argument

### Feat

- handle the extraction of a student from a webuntis csv with several rows

### Fix

- **encrypt.py**: don't load the config file in encrypt.py
- **cli.py**: handle config files correctly
- **cli.py**: catch KeyError exception when no app_username is set

### Refactor

- remove redundant scripts
- **fill_form.py**: raise FileNotFoundError
- refactor tests
- mock keyring for testing
- use importlib.resources.files instead of deprecated path
- **pyproject.toml**: change name of dependency group to bwbackend

## 1.0.0a2 (2024-12-19)

### Fix

- do input validation for school
- **managers.py**: normalize form paths
- use form_paths variable name consistently
- **cli.py**: make form_paths optional in create documentation
- **taetigkeitsbericht_from_db.py**: set pdflibs_imported when the libraries can be imported
- **add_convenience_data.py**: correct wrong dict key

## 1.0.0a1 (2024-12-16)

### Fix

- **teatigkeitsbericht_from_db.py**: make dataframe_image and fpdf truly optional
- change version in __version__.py back to string

### Refactor

- remove superfluous version from pyproject.toml

## 1.0.0a0 (2024-12-15)

### BREAKING CHANGE

- You will need to add schoolpsy data to your config.yml. See
the sampleconfig.yml in ./data/
- This will break imports and shellscripts that call edupsy_admin instead of edupsyadmin. This also changes the config path and the data path.

### Feat

- **add_convenience_data.py**: set nta_font to True if lrst_diagnosis is lrst or iLst
- accept sets of form files from config and add schoolpsy convenience data
- **cli.py**: copy sample config if config.yml does not exist
- add a flatten_pdfs function

### Fix

- **core**: explicitly set the encoding for config files to UTF-8
- change default and type hint for encrypted variables

### Refactor

- **.gitignore**: ignore .pypirc
- move code for creation of sample pdf to separate file
- update readme with new project name
- change the project name
- move the test.sqlite db to tmp_path
