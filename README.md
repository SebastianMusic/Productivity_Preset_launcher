# Disclaimer
This application is currently developed for use on MacOS. The application is using applescript for almost all functionality, therefore functionality on other operating systems is not guaranteed.

# Introduction
Throughout the weeks, days, and months, I worked on similar types of tasks. For my first coding project, I wanted to create an application that could quickly re-organize my desktop to include only the applications and websites I needed for a specific task. The goal was to transition quickly from one task to another, and so this Task Manager Application was born.

# Task Manager Application

This application helps you manage your tasks by controlling the applications and websites you need for any specific task. It uses a .txt file with `task_related_apps` and `task_related_websites` to determine which applications and websites are necessary for your task.

## Features

- Closes any application that is not listed in the `task_related_apps` in your .txt file.
- Opens all the applications listed in the `task_related_apps`.
- Minimizes your instance of Chrome and creates a new one with your preferred websites listed in `task_related_websites`.
- Can launch a Cold Turkey website blocker with or without time duration.

## Installation

Ensure you have Python 3 installed. Then, install the necessary packages with pip:

pip install PyQt5

There is also the option to utilize a Cold Turkey Blocker, this project is not affiliated with Cold Turkey Blocker, but for my personal use i wanted to be able to block unrelated websites quickly. you can check out turkey blocker here https://getcoldturkey.com/

## How to Use

1. Create a .txt file with your `task_related_apps` and `task_related_websites`. An example of how to make a preset file is provided in [Example .txt file (Lyrics preset).txt](Presets/Example%20.txt%20file%20(Lyrics%20preset).txt).
2. You can also create a .txt with your default websites and apps that you want to be common amongst your preset.
3. Use the bundle_id of apps when adding to `task_related_apps`. You can find the bundle_id of an application by using the script provided in [find_bundle_id.py](./Bundle_ID_Name_Finder.py).
4. Run the `FinalApp.py` script to start the task manager.

## Requirements

- Python 3
- PyQt5
- Cold Turkey Blocker (optional)

## Contributing
If you want to contribute, please get in touch via GitHub (https://github.com/SebastianMusic). This is my first coding project and interaction with GitHub, and I welcome all contributions and suggestions.