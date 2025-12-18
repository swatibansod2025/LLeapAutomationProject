*** Settings ***
Library   AppiumLibrary
Library   Collections
Library   ../customutilities/desktop_library.py
Resource  ../customutilities/common_utilities.robot


*** Variables ***
${APP_PATH}       C:/Program Files (x86)/Laerdal Medical/Laerdal Simulation Home/LaunchPortal.exe
${PLATFORM}       Windows
${APPIUM_SERVER}  http://127.0.0.1:4723
${HOME_PAGE_TITLE}   Laerdal Simulation Home - v 8.7.3.10398
${LSH_page_title}           Laerdal Simulation Home - v 8.7.3.10398

*** Keywords ***

Setup 
    Launch LLEAP Application
    
TearDown
    Close LLEAP Application

Launch LLEAP Application
    Open Application    ${APPIUM_SERVER}   platformName=${PLATFORM}   deviceName=WindowsPC   automationName=Windows   app=${APP_PATH}    ms:initialWindowState=Maximized
    maximize_window_by_title     ${LSH_page_title}
    verify title       ${HOME_PAGE_TITLE}
    
Close LLEAP Application
    Close Application