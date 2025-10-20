from colorama import Fore, Back, Style
import time
import configparser
from pathlib import Path


def choose_alphabet(config, config_path, alphabet):
    print(f"{Fore.LIGHTBLACK_EX}\nCurrect alphabet is: {alphabet}{Style.RESET_ALL}")
    asking = input(f"{Fore.LIGHTBLUE_EX}Do you wish to change it (y/N)?:{Style.RESET_ALL}")
    if (
            asking.lower() == "y"
            or asking.lower() == "yes"
            or asking.lower() == "1"
            or asking.lower() == "yeah"
            or asking.lower() == "yep"
            or asking.lower() == "sure"
        ):
        print(f"""{Fore.LIGHTBLACK_EX}\nTooltip: How to change your alphabet?
1. Open alphabet.py
2. Make a new dictionary with your alphabet name
3. Add it to aliases value in a function at the bottom of alphabet.py
4. Remember that exact name and either type in here or change the runs/config.ini""")
        desired_alphabet_name = input(f"{Fore.LIGHTGREEN_EX}Enter alphabet name (empty = default):{Style.RESET_ALL}")
        if desired_alphabet_name == "":
            desired_alphabet_name = "nato_phonetic_alphabet"
        try:
            print(f"{Fore.LIGHTBLACK_EX}\nApplying...{Style.RESET_ALL}")
            config.set("nato_phonetics", "alphabet", desired_alphabet_name)
            with open(str(config_path), "w") as configfile:
                config.write(configfile)
            print(f"{Fore.LIGHTGREEN_EX}Applied!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Failed to apply: {e}{Style.RESET_ALL}")


def main():
    config = configparser.ConfigParser(inline_comment_prefixes=("#", ";"))
    config_path = Path(__file__).parent / "runs" / "config.ini"
    config.read(str(config_path))

    alphabet = config.get("nato_phonetics", "alphabet")

    # Runs (modules) imports
    from runs.nato_phonetics import run_nato_phonetics

    print(
        f"""{Fore.GREEN}Welcome to the weird phonetic alphabets translator!{Style.RESET_ALL}
{Fore.CYAN}1: NATO phonetic alphabet
l: Load custom alphabet
q/e/enter: Quit"""
    )

    chosen_action = input(f"{Fore.LIGHTBLUE_EX}Choose operation mode:{Style.RESET_ALL}")

    if chosen_action.lower() == "1":
        run_nato_phonetics()
    elif chosen_action == "q" or chosen_action == "e" or chosen_action == "":
        print(f"{Fore.RED}Quitting..{Style.RESET_ALL}")
        quit()
    elif chosen_action.lower() == "l":
        choose_alphabet(config, config_path, alphabet)


if __name__ == "__main__":
    main()