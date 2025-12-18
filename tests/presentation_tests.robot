*** Settings ***
Resource   ../configs/config.robot
Resource   ../pages/lardel_simulation_home_page.robot
Resource   ../pages/add_license_page.robot
Resource   ../pages/select_simulator_page.robot
Resource   ../pages/select_virtual_simulator_page.robot
Resource   ../pages/mode_page.robot
Resource   ../pages/select_theme_page.robot
Resource   ../pages/session_not_started_page.robot
Resource   ../pages/healthy_patient_theme_page.robot
Resource   ../pages/help_page.robot


Test Setup  Setup
#Test Teardown  TearDown

*** Variables ***
${eyes_closed}             Closed
${lung_compliance_value}   67
${value_of_HR}             100
${sound_to_be_played}      Coughing
${healthy_patient_theme_text}    Healthy patient

*** Test Cases ***
It is possible to run a session using Virtual SimMan3G without the license installed
    Click on Leap Instructor tile
    CLick on Add License Later
    Click on Local Computer
    Click on SimMan 3G PLUS Simulator
    Click on Manual Mode tile
    Click on ok button on the theme page
    Click on Start session
    Maximize the Window 
    Select Eyelid status from the eyes combobox    ${eyes_closed}
    #Set the lung compliance value   
    Set the value for HR    ${value_of_HR}
    Select Coughing sound and play it  ${sound_to_be_played}
    CLick on CLose button
    
connect to the session    
    Select Coughing sound and play it  ${sound_to_be_played}
    CLick on CLose button

It is possible to collect client logs
    Right click on help tile and click on Collect client logs
    Verify that the logs are collected
    