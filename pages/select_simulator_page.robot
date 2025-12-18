*** Settings ***
Library  AppiumLibrary
Library    Collections
Library    ../customutilities/desktop_library.py
Resource     ../configs/config.robot    
  
 
   

*** Variables ***

${Local computer}                          Local computer
${expected_virtual_simulator_page_title}   Startup
${Simman_3g_text}                          SimMan 3G PLUS


*** Keywords ***
Click on Local Computer
    #Switch to the Select Simulator window and click on Local computer text${window}=    get_window_by_title    ${Local computer} 
    ${instructor_window}=   switch_to_window_containing_element      ${Local computer}
    click_element_in_window    ${instructor_window}    ${Local computer}
    #Verify that the Select Virtual Simulator screen is displayed
    #verify the window title  ${expected_virtual_simulator_page_title}  ${Simman_3g_text}










    
  




   
    




