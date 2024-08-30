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

ENVIRONMENT="$(uname -s)"

case "${ENVIRONMENT}" in
    CYGWIN*)
        AVD_MANAGER=avdmanager.bat
        SDK_MANAGER=sdkmanager.bat
        EMULATOR=emulator.exe
        ;;
    MINGW*)
        AVD_MANAGER=avdmanager.bat
        SDK_MANAGER=sdkmanager.bat
        EMULATOR=emulator.exe
        ;;
    *)
        # Assume Unix-like, e.g. Linux, MacOS, etc.
        AVD_MANAGER=avdmanager
        SDK_MANAGER=sdkmanager
        EMULATOR=emulator
        ;;
esac

if [[ ! -d "${ANDROID_SDK}" ]]
then
    echo "Please specify Android SDK location by exporting \$ANDROID_SDK"
    exit 1
fi

AVD_MANAGER="${ANDROID_SDK}/cmdline-tools/latest/bin/${AVD_MANAGER}"
SDK_MANAGER="${ANDROID_SDK}/cmdline-tools/latest/bin/${SDK_MANAGER}"
EMULATOR="${ANDROID_SDK}/emulator/${EMULATOR}"

function delete_avd() {
    local avd="${1}"
    "${AVD_MANAGER}" list avds | grep "Name: ${avd}" > /dev/null && "${AVD_MANAGER}" -s delete avd -n "${avd}"
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
    "${SDK_MANAGER}" --install platform-tools
    "${SDK_MANAGER}" --install emulator

    # You need the platform package in order to run the image in emulator
    "${SDK_MANAGER}" --install "${platform_package}"
    "${SDK_MANAGER}" --install "${image_package}"

    # delete AVD if exists
    delete_avd "${avd}"

    # create AVD
    "${AVD_MANAGER}" -s create avd -n "${avd}" -k "${image_package}" -p ".avd/${avd}"

    # run AVD trough emulator
    "${EMULATOR}" "@${avd}"

    # AVD not needed anymore
    delete_avd "${avd}"
}

run_avd "${1}"
