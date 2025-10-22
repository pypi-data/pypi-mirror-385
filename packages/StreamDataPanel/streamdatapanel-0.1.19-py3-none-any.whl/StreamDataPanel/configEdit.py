import os
import json

path_current = os.path.dirname(os.path.abspath(__file__))
path_config = os.path.join(path_current, 'config.json' )
path_config_default = os.path.join(path_current, 'configDefault.json' )

def config_load_from(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    return content

def config_save_to(content: dict, path: str):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

def config_load():
    return config_load_from(path_config)

def config_save(content: dict):
    config_save_to(content, path_config)

def config_reset():
    default = config_load_from(path_config_default)
    config_save(default)

def config_update_by(content: dict, config_type: str, config_item: str, config_value: str | int):
    content[config_type][config_item] = config_value
    return content

def config_update(config_type: str, config_item: str, config_value: str | int):
    content = config_load()
    content = config_update_by(content, config_type, config_item, config_value)
    config_save(content)




