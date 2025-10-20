import argparse
import json
import os
from deep_translator import GoogleTranslator


def get_missing_keys(master_dict, target_dict):
    missing_keys = {}
    for key, value in master_dict.items():
        if key not in target_dict:
            missing_keys[key] = value
        elif isinstance(value, dict) and isinstance(target_dict.get(key), dict):
            nested_missing_keys = get_missing_keys(value, target_dict[key])
            if nested_missing_keys:
                missing_keys[key] = nested_missing_keys
    return missing_keys


def remove_extra_keys(master_dict, target_dict):
    keys_to_remove = []
    for key, value in target_dict.items():
        if key not in master_dict:
            keys_to_remove.append(key)
        elif isinstance(value, dict) and isinstance(master_dict.get(key), dict):
            remove_extra_keys(master_dict[key], value)
            if not value:  # If the dictionary becomes empty after removing keys
                keys_to_remove.append(key)

    for key in keys_to_remove:
        del target_dict[key]
    return target_dict


def translate_and_update(missing_keys, target_data, lang):
    translator = GoogleTranslator(source="en", target=lang)
    for key, value in missing_keys.items():
        if isinstance(value, dict):
            if key not in target_data:
                target_data[key] = {}
            translate_and_update(value, target_data[key], lang)
        elif isinstance(value, str):
            try:
                translated_text = translator.translate(value)
                target_data[key] = translated_text
                print(f"Translated '{value}' to '{translated_text}' for {lang}")
            except Exception as e:
                print(f"Error translating '{value}' for {lang}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Translate missing keys in localization files."
    )
    parser.add_argument(
        "--locales-dir",
        type=str,
        default="public/assets/locales",
        help="The directory where the locale files are stored.",
    )
    parser.add_argument(
        "--master-lang",
        type=str,
        default="en",
        help="The master language to translate from.",
    )
    args = parser.parse_args()

    locales_dir = args.locales_dir
    master_lang = args.master_lang
    other_langs = [
        d
        for d in os.listdir(locales_dir)
        if os.path.isdir(os.path.join(locales_dir, d)) and d != master_lang
    ]

    master_filepath = os.path.join(locales_dir, master_lang, "translation.json")
    with open(master_filepath, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    for lang in other_langs:
        target_filepath = os.path.join(locales_dir, lang, "translation.json")
        os.makedirs(os.path.dirname(target_filepath), exist_ok=True)
        try:
            with open(target_filepath, "r", encoding="utf-8") as f:
                target_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            target_data = {}

        # Remove keys from target that are not in master
        updated_target_data = remove_extra_keys(master_data, target_data)

        missing_keys = get_missing_keys(master_data, updated_target_data)

        if missing_keys:
            print(f"Missing keys for {lang}:")
            print(json.dumps(missing_keys, indent=2, ensure_ascii=False))
            translate_and_update(missing_keys, updated_target_data, lang)

        with open(target_filepath, "w", encoding="utf-8") as f:
            json.dump(updated_target_data, f, indent=4, ensure_ascii=False)
        print(f"Updated and cleaned {target_filepath}")


if __name__ == "__main__":
    main()
