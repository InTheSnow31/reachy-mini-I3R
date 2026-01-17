# 📖 User documentation

## ⁉️ Purpose of this documentation

This documentation is intended to the **end users** of your work.
They are usually engineering-agnostic and are not able to understand mecatronics or software engineering.
Imagine that you are giving instructions to your little bro. 

## ⁉️ Do we really need to feed this section? 

Maybe not, if your project does not target end users. Drop the section and the links if you feel that it is not relevant.

## ⁉️ What is expected here

The user documentation must explain how to **start** your project and how to use each feature, most of the time without technical terms.
Inspire from the User Manual of your washing machine. Add screenshots and pictures when relevant for your end users.


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

4. Install Reachy Mini's SDK.
    ```
    pip install "reachy-mini"    
    ```
   
5. Install MuJoCo (necessary for method n°2).
    ```
    pip install "reachy-mini[mujoco]"    
    ```
   
6. Run the simulation (necessary for method n°2).
    ```
    reachy-mini-daemon --sim
    ```

7. Open **another terminal**, and run the main script.
    ```
    cd src
    python main.py
    ```

## Next steps
From now on, you will be guided by the terminal, into which choices will be proposed to you directly.

You will be asked to choose one of the 3 approaches, and be able to use them after this choice.