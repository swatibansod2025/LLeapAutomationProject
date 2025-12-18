*** Settings ***
Library  AppiumLibrary
Library    Collections
Library    ../customutilities/desktop_library.py
Resource     ../configs/config.robot    
  
*** Variables ***


${expected_run_a_session_in_mode_page_title}   Select theme
${manual_mode_automationid}                    ManualModeButton
${manual_mode}                                 Manual Mode 
${manual_mode_tile}                            On-the-fly, using a theme as a basis for clinical states   
${healthy_patient_theme_text}                  Healthy male patient
${run_a_session_text}                          Run a Session

*** Keywords ***
Click on Manual Mode tile
    #Switch to the Select Simulator window and click on Local computer text
    ${instructor_window}=   switch_to_window_containing_element      ${run_a_session_text}
    Click Element Using Automation Id  ${instructor_window}    ${manual_mode_automationid}
    #Verify that Run a Session screen is displayed
    verify the window title  ${expected_run_a_session_in_mode_page_title}  ${healthy_patient_theme_text}