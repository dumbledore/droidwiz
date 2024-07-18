#!/bin/bash
declare -ra PLATFORMS=(
    # Android 2.3
    [9]=default
    # Android 2.3.3
    [10]=default
    # Android 3.0
    [11]=default
    # Android 3.1
    [12]=default
    # Android 3.2
    [13]=default
    # Android 4.0
    [14]=default
    # Android 4.0.3
    [15]=default
    # Android 4.1
    [16]=default
    # Android 4.2
    [17]=default
    # Android 4.3
    [18]=default
    # Android 4.4
    [19]=default
    # Android 5.0
    [21]=default
    # Android 5.1
    [22]=default
    # Android 6.0
    [23]=default
    # Android 7.0
    [24]=default
    # Android 7.1
    [25]=default
    # Android 8.0
    [26]=default
    # Android 8.1
    [27]=default
    # Android 9
    [28]=default
    # Android 10
    [29]=default
    # Android 11
    [30]=default
    # Android 12
    [31]=default
    [32]=default
    # Android 13
    [33]=default
    # Android 14
    [34]=default
    # Android 15
    [35]=google_apis
)

function delete_avd() {
    local avd="${1}"
    avdmanager list avds | grep "Name: ${avd}" > /dev/null && avdmanager -s delete avd -n "${avd}"
    # Remove directory (if empty)
    rmdir .avd 2>/dev/null
}

function run_avd() {
    local platform="${1}"
    local image_type=${PLATFORMS["${platform}"]}
    local platform_package="platforms;android-${platform}"
    local image_package="system-images;android-${platform};${image_type};x86_64"
    local avd="droidwiz"

    if [[ -z ${image_type} ]]
    then
        echo "Unknown platform :${platform}. Please choose from: ${!PLATFORMS[@]}"
        return
    fi

    # install packages

    # ADB is in platform-tools
    sdkmanager --install platform-tools
    sdkmanager --install emulator

    # You need the platform package in order to run the image in emulator
    sdkmanager --install "${platform_package}"
    sdkmanager --install "${image_package}"

    # delete AVD if exists
    delete_avd "${avd}"

    # create AVD
    avdmanager -s create avd -n "${avd}" -k "${image_package}" -p ".avd/${avd}"

    # run AVD trough emulator
    emulator "@${avd}"

    # AVD not needed anymore
    delete_avd "${avd}"
}

run_avd "${1}"
