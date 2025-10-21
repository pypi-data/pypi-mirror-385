# Reskinner Version 3.0.0
from psg_reskinner import animated_reskin, reskin, __version__
from random import choice as rc

from FreeSimpleGUI import (
    LOOK_AND_FEEL_TABLE,
    Button,
    Push,
    Text,
    Titlebar,
    Window,
    theme,
    theme_list,
)

right_click_menu = [
    "",
    [["Hi", ["Next Level", ["Deeper Level", ["a", "b", "c"]], "Hoho"]], "There"],
]

window_layout = [
    [Titlebar("Reskinner Demo")],
    [Text("Hello!", font=("Helvetica", 20))],
    [Text("You are currently running the Reskinner demo.")],
    [Text("The theme of this window changes every 2 seconds.")],
    [Text("Changing to:")],
    [
        Button(
            "DarkBlue3",
            k="current_theme",
            font=("Helvetica", 16),
            right_click_menu=right_click_menu,
        )
    ],
    [Text(f"Reskinner v{__version__}", font=("Helvetica", 8), pad=(0, 0)), Push()],
]

window = Window(
    "Reskinner Demo",
    window_layout,
    element_justification="center",
    keep_on_top=True,
)

def _reskin_job():
    themes = theme_list()
    themes.remove(theme())
    new = rc(themes)
    window["current_theme"].update(new)
    animated_reskin(
        window=window,
        new_theme=new,
        theme_function=theme,
        lf_table=LOOK_AND_FEEL_TABLE,
    )
    window.TKroot.after(2000, _reskin_job)

started = False

while True:
    e, v = window.read(timeout=2000)

    if e in (None, "Exit"):
        window.Close()
        break
    if e == "current_theme":
        print("BUTTON")
        _reskin_job()
