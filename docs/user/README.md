# 📖 User documentation

## Introduction

This repository contains the demo of an experiment which aims to create expressive poses for Reachy Mini. If you want to try it yourself, here is how to do it.

1. Open a code editor, such as [Visual Studio Code](https://code.visualstudio.com/) for instance.

2. Open a terminal into it.

3. Type the commands described as follows, according to your personnal configuration.

## Commands to type

**Note:** These commands work for Windows, you might need to translate them for another computer configuration.

1. Create a virtual environment on your machine.
   ```
   python -m venv reachy_mini_env
   ```

2. Activate the virtual environment.
    ```
    reachy_mini_env\Scripts\Activate 
    ```

3. Install the required packages.
    ```
    pip install -r requirements.txt
    ```
    **Note:** if you need to upgrade pip, do it. You might need to retype the command line after.

4. Install [Git Large Files Storage (LFS)](https://git-lfs.com/) on your computer if you do not already have it.

5. Install Reachy Mini's SDK.
    ```
    pip install "reachy-mini"    
    ```
   
6. Install MuJoCo (necessary for method n°2).
    ```
    pip install "reachy-mini[mujoco]"    
    ```
   
7. Run the simulation (necessary for method n°2, optionnal but useful for method n°1).
    ```
    reachy-mini-daemon --sim
    ```

8. Open **another terminal**, and run the main script.
    ```
    cd src
    python main.py
    ```

## Next steps
From now on, you will be guided by the terminal, into which choices will be proposed to you directly.

You will be asked to choose one of the 3 approaches, and be able to use them after this choice.