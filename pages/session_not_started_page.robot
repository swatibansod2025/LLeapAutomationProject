*** Settings ***
Library  AppiumLibrary
Library    Collections
Library    ../customutilities/desktop_library.py
Resource     ../configs/config.robot    
  
*** Variables ***


${expected_session_page_title}                The session is not started yet
${start_session_text}                          Start session
${session_page_text}                           ABC

*** Keywords ***
Click on Start session
    #Switch to the Select Simulator window and click on Local computer text
    ${instructor_window}=   switch_to_window_containing_element      ${start_session_text}
    Wait Until Keyword Succeeds      10s      0.5s   click_element_in_window  ${instructor_window}    ${start_session_text}
    #Verify that Run a Session screen is displayed
    #verify the window title  ${expected_session_page_title}  ${expected_session_page_title}

    