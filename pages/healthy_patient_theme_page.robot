*** Settings ***
Library    AppiumLibrary
Library    Collections
Library    ../customutilities/desktop_library.py
Resource     ../configs/config.robot   

  
*** Variables ***
${eyes_to_be_set_to}                    Closed
${eyes_combobox_auto_id}                EyesComboBox
${healthy_patient_theme_page_title}     Healthy patient - Virtual SimMan 3G - Manual Mode - LLEAP 
${HR_auto_id}                           11
${HR_text_box_auto_id}                          2093
${OK_button_set_heart_rate_auto_id}            1
${control_type_for_vocals}                    TreeItem
${play_button_auto_id}                        PlayButton
${tool_tip_text_lung_compliance}              Total lung compliance
${lung_compliance_67_text}                    67
${xpath_for_slider_for_67}                    //*[contains(@AutomationId, 'lung compliance')]
${Maximize_button_automation_id}               Maximize-Restore
${healthy_patient_text}                        Healthy patient

*** Keywords ***


Select Eyelid status from the eyes combobox 
  [Arguments]   ${eyes_to_be_set_to}
  select_status_from_Eyecombobox    ${eyes_to_be_set_to}
  is_eye_status_closed    ${healthy_patient_theme_page_title}


Set the lung compliance value
    #${instructor_window}=   switch_to_window_by_title_regex      ${healthy_patient_theme_page_title}
    #${window_title}=     get_window_title_by_contained_element     ${healthy_patient_theme_page_title}
    #click_element_by_xpath_in_window    ${instructor_window}   ${xpath_for_slider_for_67}
    #click_element_by_partial_name_help_automationid   ${healthy_patient_theme_page_title}   67     
    #click_custom_under_label    ${healthy_patient_theme_page_title}    0       67      0  
    #click_vertical_slider_on_tab     ${healthy_patient_theme_page_title}    6       67      1      75      1
    #set_slider_by_label_under_tab      ${healthy_patient_theme_page_title}    6   67    1   50    1    #set_slider_by_label_index    ${healthy_patient_theme_page_title}   ${lung_compliance_value}       1         67        2
    #click_tab_by_index     ${healthy_patient_theme_page_title}     6
    #Click on slider for 67
    #Click At Coordinates Using Appium  1040       513
    #click_at  1040       513     ${healthy_patient_theme_page_title}
    #drag_slider         1040      513      1101     513      ${healthy_patient_theme_page_title}      2
    #Verify that the lung compliance value is set correctly  ${lung_compliance_value}
    set_lung_compliance         ${healthy_patient_theme_page_title} 


Set the value for HR
    [Arguments]    ${Hr_value_to_be_changed_to}
    ${window}=    get_window_by_title    ${healthy_patient_theme_page_title}
    Click on HR on the patient monitor   ${window}
    Change the value in HR textbox    ${window}   ${Hr_value_to_be_changed_to}
    Click on the OK button on the Set heart Rate box   ${window}
    #Verify that the correct value is set for HR   ${Hr_value_to_be_changed_to}
    #verify_HR_value  ${healthy_patient_theme_page_title}
    

Select Coughing sound and play it
    [Arguments]    ${sound_name_to_be_played}  
    click_child_element_by_name     ${healthy_patient_theme_page_title}    ${sound_name_to_be_played}  ${control_type_for_vocals}   2
    click_and_verify_disabled    ${healthy_patient_theme_page_title}     ${play_button_auto_id}  2
    #Verify that the the button is disabled when coughing was played
    #Element Should Be Disabled    ${play_button_auto_id}      loglevel=Sound was played!
    
Click on HR on the patient monitor
    [Arguments]    ${window}
    Click Element Using Automation Id  ${window}    ${HR_auto_id}

Change the value in HR textbox
    [Arguments]    ${window}  ${Hr_value_to_be_changed_to}
    set_textbox_value   ${window}   ${HR_text_box_auto_id}   ${Hr_value_to_be_changed_to}    2

Click on the OK button on the Set heart Rate box
    [Arguments]    ${window}
    Click Element Using Automation Id      ${window}     ${OK_button_set_heart_rate_auto_id}



Verify that the lung compliance value is set correctly
   [Arguments]  ${lung_compliance_value}
    ${get_slider_value}=  get_slider_value  ${healthy_patient_theme_page_title}
    Should Be Equal  ${get_slider_value}  ${lung_compliance_value}  msg=Eyes ComboBox value is not as expected!
    
Verify that the correct value is set for HR
    [Arguments]   ${value_of_HR}
    ${get_value_of_HR}=   get_element_value  ${healthy_patient_theme_page_title}      ${HR_auto_id}
    Should Be Equal  ${get_value_of_HR}  ${value_of_HR}  msg=HR value is not as expected!

CLick on CLose button
    ${window}=    get_window_by_title    ${healthy_patient_theme_page_title}
    click_on_button  ${window}    Close


Click At Coordinates Using Appium
    [Arguments]    ${x}    ${y}
    ${action}=    Evaluate    {"actions":[{"type":"pointer","id":"finger1","parameters":{"pointerType":"mouse"},"actions":[{"type":"pointerMove","duration":0,"x":${x},"y":${y}},{"type":"pointerDown","button":0},{"type":"pointerUp","button":0}]}]}
    Execute Script    driver.performActions(${action})

Maximize the session screen
  ${instructor_window}=   switch_to_window_containing_element      ${healthy_patient_theme_page_title}
  maximize_window_by_title     ${healthy_patient_theme_page_title}

connect to the session
    connect_to_running_app  ${healthy_patient_theme_page_title}

Maximize the Window 
    ${window}=    get_window_by_title    ${healthy_patient_theme_page_title}
    click_on_button  ${window}    Maximise
 
Click on slider for 67
   ${new_window}=   get_window_by_title  ${healthy_patient_theme_page_title}
   click_at_coordinates         1040       513   ${healthy_patient_theme_page_title}



