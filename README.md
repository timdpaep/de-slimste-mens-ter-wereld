# De Slimste Mens Ter Wereld

This repository was forked from [AntheSevenants](https://github.com/AntheSevenants/dsmtw)

## Before you start

Make sure you have installed Python. You can use your native install Python version, or if you want to manage your Python environments, use Conda.

### Installing Conda

- on [Windows](https://conda.io/projects/conda/en/latest/user-guide/install/windows.html)
- on [Mac](https://conda.io/projects/conda/en/latest/user-guide/install/macos.html)

#### Create a new Conda environment

- In case of Conda, make a new environment for dsmtw: 'conda create -n dsmtw python=3.11'
- Open up your environment by: 'conda activate dsmtw'

_Note: Python 3.11 has been successfully tested_

### Anaconda Navigator

If you want to control your Python environments with a Graphical User Interface, use: [Anaconda Navivator](https://docs.anaconda.com/free/navigator/index.html)

## Installation

- Navigate to the project folder
- Install all Python requirements: `pip install -r requirements.txt`

## Assets

The assests folder contains all the JSON files, images and videos that are needed to play the game.

- You can use the _default_ assets as a starting point. Fill in answers, add videos, images, etc.
- On [this location](https://drive.google.com/drive/folders/12WWNlmYh9vjv9atfELKr7bAB-YRkfpPX?usp=drive_link) you can find some open sourced questions and assets. You can use this as a reference. **Please note that you need to create own videos for the "Open Deur" round.**

## Start The Game

Open up the application by: `python3 dsmtw.py listen [PATH OF QUESTIONS] [LIST OF PLAYERS]`. If you want to open up the default questions, this command should work: `python3 dsmtw.py listen "./default" "Tim,Willy,René"`
