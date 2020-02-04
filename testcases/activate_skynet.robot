*** Settings ***
Library    OperatingSystem

*** Test Cases ***
Should Activate Skynet
    [Tags]    smoke
    [Setup]    Set Environment Variable    SKYNET    activated
    Environment Variable Should Be Set    SKYNET