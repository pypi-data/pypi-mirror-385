from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, Input
from textual.containers import Horizontal, Vertical
# from textual.reactive import reactive - for clock widget
from tkinter import filedialog
import importlib.resources as pkg_resources
import todolist_angrypig555
# import datetime
import re

todo_list = []

def clean_text(text: str) -> str:
    """Remove any markup tags from the text."""
    return re.sub(r"\[.*?\]", "", text)

def clean_checkmark(text: str) -> str:
    return text.replace("✅ ", "")


# class Clock(Static):
#    time: reactive[str] = reactive("")
#    def on_mount(self):
#        self.set_interval(1, self.update_time)
#        self.styles.dock = "bottom"
#        self.styles.align = ("right", "bottom")
#        self.styles.padding = (0, 2)
#    def update_time(self):
#        self.time = datetime.datetime.now().strftime("%H:%M:%S")
#        self.update(self.time)
# todo: create a clock widget that doesnt make the whole app mushed

class application(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load CSS content from package resource
        with pkg_resources.open_text(todolist_angrypig555, "main.tcss") as f:
            css_content = f.read()
        self.stylesheet.add_source(css_content)  # load CSS directly from str

    BINDINGS = [("q", "quit", "Quit the app")]
    
    TITLE = "To-Do List"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Enter a new to-do item:", id="label")
        yield Input(placeholder="New to-do item...", id="todo_input")
        yield Horizontal(
            Button("Add Item", id="add_button"),
            Button("Check off item", id="check_button"),
            Button("Export", id="export_button"),
            Button("Import", id="import_button"),
            Button("Remove Item", id="remove_button")
        )
        yield Static("Your To-Do List:", id="list_label")
        yield Static("", id="todo_list")
        yield Static("To-Do List v0.2.", id="custom_footer")
        yield Footer()

    def update_todo_list(self) -> None:
        todo_list_widget = self.query_one("#todo_list", Static)
        if todo_list:
            todo_list_widget.update("\n".join(f"- {item}" for item in todo_list))
        else:
            todo_list_widget.update("No items in the to-do list.")

    def export_todo_list(self) -> None:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                for item in todo_list:
                    file.write(f"{item}\n")
    def import_todo_list(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    item = line.strip()
                    if item and item not in todo_list:
                        todo_list.append(item)
            self.update_todo_list()
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_button":
            input_widget = self.query_one("#todo_input", Input)
            new_item = input_widget.value.strip()
            if new_item:
                todo_list.append(new_item)
                input_widget.value = ""
                self.update_todo_list()
        elif event.button.id == "remove_button":
            input_widget = self.query_one("#todo_input", Input)
            item_to_remove = input_widget.value.strip()
            for item in todo_list:
                if clean_text(item) or clean_checkmark(item) == item_to_remove:
                    item_to_remove = item
                    break
            if item_to_remove in todo_list:
                todo_list.remove(item_to_remove)
                input_widget.value = ""
                self.update_todo_list()
        elif event.button.id == "export_button":
            self.export_todo_list()
        elif event.button.id == "import_button":
            self.import_todo_list()
        elif event.button.id == "check_button":
            input_widget = self.query_one("#todo_input", Input)
            item_to_check = input_widget.value.strip()
            if item_to_check in todo_list:
                index = todo_list.index(item_to_check)
                todo_list[index] = f"[strike]{item_to_check}[/strike]✅"
                input_widget.value = ""
                self.update_todo_list()
if __name__ == "__main__":
    app = application()
    app.run()