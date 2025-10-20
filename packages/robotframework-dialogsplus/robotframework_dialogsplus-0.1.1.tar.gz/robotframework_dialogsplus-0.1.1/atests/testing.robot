*** Settings ***
Library           DialogsPlus    #config=D:/robotframework-dialogsplus/atests/config.yaml
Library           OperatingSystem

Suite Setup       Set Log Level    level=TRACE
Test Setup        Log Test Case Name


*** Keywords ***
Log Test Case Name
    [Tags]    robot:flatten
    Log    <p style="background-color: #06bdb1; font-weight: bold; display: inline-block; padding: 4px;">*** Running Test: ${TEST NAME} ***</p>    html=${True}


*** Variables ***

@{fields_val}     username    password    email    phone
@{fields}         username    password
&{default_val}    username=admin    password=P@55    phone=1234567
&{default}        username=user1    password=P@55

*** Test Cases ***

Get Value From User Default
    ${result}    Get Value From User Input   
    ...    prompt=Enter your name:    
    ...    default=Robot framework
    
    Should Be Equal    ${result}    Robot framework

Run Manual Steps Executes
    ${steps}    Create List    Open the app    Click Start button    Verify status
    Run Manual Steps    ${steps}
    Log    Manual steps executed successfully

Count Down Runs
    Count Down    3
    Log    Countdown executed for 3 seconds

Get Confirmation Returns Boolean
    ${result}    Get Confirmation    Are you sure?
    Should Be True    isinstance(${result}, bool)

Get Multi Value
    ${result}    Get Multi Value    ${fields}    default=${default}
    Should Be Equal    ${result}[username]    user1


Get Multi Value Multiple Fields
    ${result}    Get Multi Value    ${fields_val}    default=${default_val}
    Should Be Equal    ${result}[password]    P@55
    Should Be Equal    ${result}[phone]       1234567

Choose Single XML File
    ${XML_FILETYPES}    Evaluate    [("xml files", "*.xml")]
    ${result}=    Choose File    
    ...    message=Select Single XML File    
    ...    filetypes=${XML_FILETYPES}
    
    Should Contain    ${result}    .xml

Choose Multiple HTML Files
    ${HTML_FILETYPES}    Evaluate    [("HTML", "*.html")]
    ${result}=    Choose File    
    ...    message=Select Multiple HTML Files    
    ...    filetypes=${HTML_FILETYPES}   multiple=True

    Should Contain    ${result}[0]    .html

Choose Folder Test
    ${result}=    Choose Folder    message=Select Any Directory
    Directory Should Exist    ${result}

Single Ceckbox Test
    ${r}    Confirm With Checkbox    
    ...    message=Do you accept the terms?    
    ...    checkbox_text=I accept, no matter what!

    Should Be True    ${r}

Select Many Checkbox Test
    ${r}    Select Options With Checkboxes    
    ...    message=Select as much as you want   
    ...    options=${fields_val}

    Should Not Be True    ${r}[username]
    Should Not Be True    ${r}[password]
    Should Not Be True    ${r}[email]
    Should Not Be True    ${r}[phone]

Select Many Checkbox With Defaults Test
    @{Contacts}    Create List        Email    SMS    Phone    Slack    Discord
    @{Selected_Defaults}    Create List    Email    SMS
    ${selected}=    Select Options With Checkboxes
    ...    message=Choose your preferences
    ...    options=${Contacts}
    ...    defaults=@{Selected_Defaults}         # Default Selected!
    
    Should Be True        ${selected}[Email]
    Should Be True        ${selected}[SMS]
    Should Not Be True    ${selected}[Phone]
    Should Not Be True    ${selected}[Slack]
    Should Not Be True    ${selected}[Discord]

Pause The Test
    Pause Test Execution    message=Check If System Is Running!