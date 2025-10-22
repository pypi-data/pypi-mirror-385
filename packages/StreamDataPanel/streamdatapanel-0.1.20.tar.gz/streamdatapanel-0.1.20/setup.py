#!/usr/bin/python
#coding = utf-8

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="StreamDataPanel",
    version="0.1.20",
    author="Syuya_Murakami",
    author_email="wxy135@mail.ustc.edu.cn",
    description="StreamDataPanel is a web app used to show frequently-freshed data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    project_urls={
        "Bug Tracker": "https://github.com/SyuyaMurakami/StreamDataPanel",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=['websockets','eel'],
    entry_points={
        'console_scripts': [
            'runSDP = StreamDataPanel:run_app',
            'testSDP = StreamDataPanel:test',
            'setSDP = StreamDataPanel:set_config',
            'showSDP = StreamDataPanel:show_config',
            'resetSDP = StreamDataPanel:reset_config'
        ]
    }
)
