#!/bin/bash
#
# Switch Burner KlipperScreen supplemental installer

set -e

SCRIPT="$(readlink -f "$0")"
SWITCH_BURNER_DIR="$(cd "$(dirname "$SCRIPT")" && pwd)"
KLIPPERSCREEN_DIR="$(dirname "$SWITCH_BURNER_DIR")"
KLIPPER_CONFIG_HOME="${HOME}/printer_data/config"
OLD_KLIPPER_CONFIG_HOME="${HOME}/klipper_config"
MENU_CONFIG="switch_burner_klipperscreen.conf"

INFO='\033[0;36m'
WARNING='\033[1;33m'
ERROR='\033[1;31m'
OFF='\033[0m'

usage() {
    echo "Usage: $0 [-c <klipper_config_dir>]"
    exit 1
}

while getopts "c:h" arg; do
    case $arg in
        c) KLIPPER_CONFIG_HOME=${OPTARG};;
        h) usage;;
        *) usage;;
    esac
done

verify_config_dir() {
    if [ -d "${KLIPPER_CONFIG_HOME}" ]; then
        return
    fi
    if [ -d "${OLD_KLIPPER_CONFIG_HOME}" ]; then
        KLIPPER_CONFIG_HOME="${OLD_KLIPPER_CONFIG_HOME}"
        return
    fi
    echo -e "${ERROR}Klipper config directory not found. Use '-c <dir>' to override.${OFF}"
    exit 1
}

restart_klipperscreen() {
    echo -e "${INFO}Restarting KlipperScreen...${OFF}"
    if systemctl list-unit-files 2>/dev/null | grep -q '^KlipperScreen.service'; then
        sudo systemctl restart KlipperScreen
    elif systemctl list-unit-files 2>/dev/null | grep -q '^klipperscreen.service'; then
        sudo systemctl restart klipperscreen
    else
        echo -e "${WARNING}KlipperScreen service not found; restart it manually to load Switch Burner.${OFF}"
    fi
}

install_menu_config() {
    local ks_config="${KLIPPER_CONFIG_HOME}/KlipperScreen.conf"
    local sb_config="${KLIPPER_CONFIG_HOME}/${MENU_CONFIG}"

    echo -e "${INFO}Installing Switch Burner menu config...${OFF}"
    cp "${SWITCH_BURNER_DIR}/menus.conf" "${sb_config}"

    if [ -f "${ks_config}" ]; then
        if grep -Fq "[include ${MENU_CONFIG}]" "${ks_config}"; then
            echo -e "${INFO}Switch Burner include already exists.${OFF}"
            return
        fi
        local tmp
        tmp="$(mktemp)"
        {
            echo "# Switch Burner KlipperScreen menus"
            echo "[include ${MENU_CONFIG}]"
            echo
            cat "${ks_config}"
        } > "${tmp}"
        cp "${tmp}" "${ks_config}"
        rm -f "${tmp}"
    else
        {
            echo "# Switch Burner KlipperScreen menus"
            echo "[include ${MENU_CONFIG}]"
            echo
        } > "${ks_config}"
    fi
}

install_panel_link() {
    local target="${KLIPPERSCREEN_DIR}/panels/switch_burner.py"
    local source="${SWITCH_BURNER_DIR}/switch_burner.py"

    echo -e "${INFO}Installing Switch Burner panel link...${OFF}"
    if [ -e "${target}" ] && [ ! -L "${target}" ]; then
        echo -e "${ERROR}${target} exists and is not a symlink. Refusing to overwrite it.${OFF}"
        exit 1
    fi
    ln -sfn "${source}" "${target}"
}

install_icons() {
    echo -e "${INFO}Installing Switch Burner icons...${OFF}"
    find "${KLIPPERSCREEN_DIR}/styles" -mindepth 2 -maxdepth 2 -type d -name images | while read -r image_dir; do
        find "${SWITCH_BURNER_DIR}/images" -maxdepth 1 -type f \( -name '*.svg' -o -name '*.png' \) | while read -r image; do
            ln -sfn "${image}" "${image_dir}/$(basename "${image}")"
        done
    done
}

verify_config_dir
install_menu_config
install_panel_link
install_icons
restart_klipperscreen

echo -e "${INFO}Switch Burner panel installed.${OFF}"
