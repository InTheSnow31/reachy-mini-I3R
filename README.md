## How to run this experiment
**Note:** this tutorial works on Windows, but you might change some commands if you use Linux or Mac/OS.

### Tutorial steps
1. Create a virtual environment on your machine.
   ```
   python -m venv reachy_mini_env
   ```

2. Activate the virtual environment.
    ```
    reachy_mini_env\Scripts\activate 
    ```

3. Install Reachy Mini's SDK.
    ```
    pip install "reachy-mini"    
    ```

    **Note:** if you need to upgrade pip, do it and then reinstall reachy-mini.
   
4. Install MuJoCo.
    ```
    pip install "reachy-mini[mujoco]"    
    ```
   
5. Run the simulation.
    ```
    reachy-mini-daemon --sim
    ```

6. Open another terminal, and run the desired script (do not forget to check if you are in the right folder).