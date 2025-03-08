# Monkey Maze
![Thumbnail for Monkey Maze](images/Monkey%20Maze%20Thumbnail.png)
Welcome to the [**Monkey Maze**](https://pillagerplayz.itch.io/monkey-maze/) Github repository. This is where the source code of the game is.
# Instructions
This is the **DEV** edition of the game for **Windows**. If you want to mod the game, this is the instructions for how.

## Setup the project for building

1. Install the required tools for development:
    - **Git**
    - **Python** and **PIP**
2. Configure Git for your account. The brackets are placeholders for what is inside them:<br />
    `git config --global user.name "[Name]"`<br />
    `git config --global user.email [YourEmail]`
2. Clone this repository: `git clone https://github.com/Pillagerplayz/Monkey-Maze-WIN.git`.
3. Navigate to `Monkey Maze WIN`: `cd "Monkey Maze WIN"`
3. Create a .venv in the created directory with this command: `python3 -m venv .venv`.
4. Activate the venv: `.venv/Scripts/Activate`.
5. Install pygame: `pip install pygame`.
6. You can modify `main.py` and add images, sounds, and maybe fonts.
7. To test the mod, run this command: `python main.py`.

## Packaging the mod

1. Save your changes before proceeding to package the mod.
2. Install Pyinstaller for packaging to an executable: `pip install pyinstaller`
3. Package the mod with the built-in `package.bat`: `./package`.
4. The results are available in the `dist` folder.
5. Keep the `build` folder and `main.spec` file for updating the mod.