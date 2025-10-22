import os
import json

pathCurrent = os.path.dirname(os.path.abspath(__file__))
pathConfig = os.path.join(pathCurrent, 'config.json' )
pathConfigDefault = os.path.join(pathCurrent, 'configDefault.json' )

def configLoadFrom(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    return content

def configSaveTo(content: dict, path: str):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

def configLoad():
    return configLoadFrom(pathConfig)

def configSave(content: dict):
    configSaveTo(content, pathConfig)

def configReset():
    default = configLoadFrom(pathConfigDefault)
    configSave(default)

def configUpdateBy(content: dict, configType: str, configItem: str, configValue: str | int):
    content[configType][configItem] = configValue
    return content

def configUpdate(configType: str, configItem: str, configValue: str | int):
    content = configLoad()
    content = configUpdateBy(content, configType, configItem, configValue)
    configSave(content)




