*** Settings ***
Library  AppiumLibrary
Library    Collections
Library    ../customutilities/desktop_library.py
Resource     ../configs/config.robot    
  
 
   

*** Variables ***
${LLEAP_instructor_tile}     name=LLEAP - Instructor Application
${Add License Later}         name=Add license later
${Local_computer}            Local computer
${simman 3g plus}            name=SimMan 3G PLUS
${manual mode}               name=Manual Mode
${ok button}                 name=Ok
${expected_select_simulator_page_title}   Startup
${LSH_page_title}           Laerdal Simulation Home - v 8.7.3.10398





*** Keywords ***
Click on Leap Instructor tile  
    Click Element       ${LLEAP_instructor_tile}
    #Verify that Select Simulator screen is displayed
    verify the window title  ${expected_select_simulator_page_title}  ${Local_computer} 

    
    
    







    
  




   
    




