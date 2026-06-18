#!/bin/bash
#
# Switch Burner KlipperScreen supplemental remover

set -e

SCRIPT="$(readlink -f "$0")"
SWITCH_BURNER_DIR="$(cd "$(dirname "$SCRIPT")" && pwd)"
KLIPPERSCREEN_DIR="$(dirname "$SWITCH_BURNER_DIR")"
KLIPPER_CONFIG_HOME="${HOME}/printer_data/config"
OLD_KLIPPER_CONFIG_HOME="${HOME}/klipper_config"
MENU_CONFIG="switch_burner_klipperscreen.conf"

INFO='\033[0;36m'
WARNING='\033[1;33m'
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
    echo -e "${WARNING}Klipper config directory not found. Continuing with repo cleanup only.${OFF}"
}

restart_klipperscreen() {
    echo -e "${INFO}Restarting KlipperScreen...${OFF}"
    if systemctl list-unit-files 2>/dev/null | grep -q '^KlipperScreen.service'; then
        sudo systemctl restart KlipperScreen
    elif systemctl list-unit-files 2>/dev/null | grep -q '^klipperscreen.service'; then
        sudo systemctl restart klipperscreen
    else
        echo -e "${WARNING}KlipperScreen service not found; restart it manually to finish removal.${OFF}"
    fi
}

remove_menu_config() {
    local ks_config="${KLIPPER_CONFIG_HOME}/KlipperScreen.conf"
    local sb_config="${KLIPPER_CONFIG_HOME}/${MENU_CONFIG}"

    if [ -f "${ks_config}" ]; then
        echo -e "${INFO}Removing Switch Burner include...${OFF}"
        sed -i.bak \
            -e "/^\[include ${MENU_CONFIG}\]$/d" \
            -e "/^# Switch Burner KlipperScreen menus$/d" \
            "${ks_config}"
    fi
    rm -f "${sb_config}"
}

remove_panel_link() {
    local target="${KLIPPERSCREEN_DIR}/panels/switch_burner.py"
    local source="${SWITCH_BURNER_DIR}/switch_burner.py"

    if [ -L "${target}" ]; then
        if [ "$(readlink -f "${target}")" = "${source}" ]; then
            echo -e "${INFO}Removing Switch Burner panel link...${OFF}"
            rm -f "${target}"
        else
            echo -e "${WARNING}${target} is a symlink but does not point to Switch Burner; leaving it untouched.${OFF}"
        fi
    fi
}

remove_icons() {
    echo -e "${INFO}Removing Switch Burner icon links...${OFF}"
    find "${KLIPPERSCREEN_DIR}/styles" -mindepth 2 -maxdepth 2 -type d -name images | while read -r image_dir; do
        find "${SWITCH_BURNER_DIR}/images" -maxdepth 1 -type f \( -name '*.svg' -o -name '*.png' \) | while read -r image; do
            local target="${image_dir}/$(basename "${image}")"
            if [ -L "${target}" ] && [ "$(readlink -f "${target}")" = "${image}" ]; then
                rm -f "${target}"
            fi
        done
    done
}

verify_config_dir
remove_menu_config
remove_panel_link
remove_icons
restart_klipperscreen

echo -e "${INFO}Switch Burner panel removed.${OFF}"
