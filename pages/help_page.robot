*** Settings ***
Library  AppiumLibrary
Library    Collections
Library    ../customutilities/desktop_library.py
Resource     ../configs/config.robot 


** Variables ***

${home_page_title}        Laerdal Simulation Home - v 8.7.3.10398
${elemet_name_help}       Help
${collect_clietnt_log_files_option}       Collect client log files
${directory_path}                        C:\\Users\\Public\\Documents\\Laerdal Report Zipped
${file_prefix}                            report

*** Keywords ***
Right click on help tile and click on Collect client logs
  right_click_element_by_name1    ${home_page_title}     ${elemet_name_help}  
  click_context_menu_option    ${collect_clietnt_log_files_option}
  Verify that the folder is empty

Verify that the logs are collected
  verify_report_file_present  ${directory_path}   ${file_prefix}
   
Verify that the folder is empty
    verify_folder_is_empty  ${directory_path}