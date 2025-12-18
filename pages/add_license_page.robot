*** Settings ***
Library  AppiumLibrary
Library    Collections
Library    ../customutilities/desktop_library.py
Resource     ../configs/config.robot    
  
 
   

*** Variables ***
${Add License Later}         name=Add license later



*** Keywords ***
Click on Add License Later
    [Documentation]       This method verifies if teh Add license page is displayed, if dispalyed, it cliks on Add license
    ${exists}=  Run Keyword And Return Status    Element Should Be Visible    ${Add_License_Later}    2s
    IF    ${exists}
        ${instructor_window}=  switch_to_window_containing_element    ${Add_License_Later}
        click_element_in_window    ${instructor_window}    ${Add_License_Later}
    ELSE
        Log    Add License window is not present!    WARN
    END










    
  




   
    




