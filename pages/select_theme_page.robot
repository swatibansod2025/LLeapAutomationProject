*** Settings ***
Library  AppiumLibrary
Library    Collections
Library    ../customutilities/desktop_library.py
Resource     ../configs/config.robot  


*** Variables ***
${expected_session_page_title}     PAUSE - Healthy male patient - Virtual SimMan 3G - Manual Mode - LLEAP
${ok_button_auotomation_id}        OKButton 
${healthy_patient_theme_text}      Healthy male patient  
${session_is_not_started_yet_page}     The session is not started yet  
${expected_run_a_session_in_mode_page_title}   Select theme   


*** Keywords ***
Click on ok button on the theme page
    #Switch to the Select Simulator window and click on Local computer text
    ${instructor_window}=   switch_to_window_containing_element      ${healthy_patient_theme_text}
    Click Element Using Automation Id  ${instructor_window}    ${ok_button_auotomation_id}
    #Verify that Run a Session screen is displayed
    #verify the window title  ${expected_session_page_title}  ${session_is_not_started_yet_page}

Expand the list of Themes
    expand_themes_if_not_expanded     ${expected_run_a_session_in_mode_page_title}

CLick on patient theme
    [Arguments]   ${theme_name}
    ${window}=    get_window_by_title    ${expected_run_a_session_in_mode_page_title}
    click_theme       ${window}      ${theme_name}


    