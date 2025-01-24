import js
from pyodide.ffi.wrappers import add_event_listener


def myfunc():
    print("You clicked the button with py-click")


def click(event):
    print("You clicked the button with the added event listener in javascript")


js_button = js.document.getElementById("js-click")
add_event_listener(js_button, "click", click)
