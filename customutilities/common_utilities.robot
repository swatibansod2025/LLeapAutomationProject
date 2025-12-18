*** Settings ***
Library   AppiumLibrary
Library   Collections
Library   ../customutilities/desktop_library.py

*** Keywords ***
verify the window title
    [Arguments]   ${expected_title}   ${Text_ON_PAGE}  
    ${actual_title}=   get_window_title_by_contained_element  ${Text_ON_PAGE}
    Should Be Equal As Strings    ${actual_title}    ${expected_title}
    

    
  

verify title
    [Arguments]   ${expected_title}
    ${actual_title}=   get_window_title 
    Should Be Equal As Strings    ${actual_title}    ${expected_title}





    
    