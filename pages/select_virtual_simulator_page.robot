*** Settings ***
Library  AppiumLibrary
Library    Collections
Library    ../customutilities/desktop_library.py
Resource     ../configs/config.robot    
  
 
   

*** Variables ***


${expected_virtual_simulator_page_title}   Startup
${Simman_3g_text}                          SimMan 3G PLUS
${Run_a_session_text}                      Run a Session
${expected_run_a_session_page_title}       Startup
${simman_3g_plus_button}                   Start virtual simulator of type SimMan 3G PLUS on local computer
                                            

*** Keywords ***
Click on SimMan 3G PLUS Simulator
    #Switch to the Select Simulator window and click on Local computer text
    ${instructor_window}=   switch_to_window_containing_element      ${Simman_3g_text}
    Click Element In Tile    ${instructor_window}    ${Simman_3g_text}
    #Verify that Run a Session screen is displayed
    verify the window title  ${expected_run_a_session_page_title}  ${Run_a_session_text}
    