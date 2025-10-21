from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, Input
from textual.containers import Horizontal, Vertical
from tkinter import filedialog

todo_list = []


class application(App):
    BINDINGS = [("q", "quit", "Quit the app")]
    CSS_PATH = "main.tcss"
    TITLE = "To-Do List"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Enter a new to-do item:", id="label")
        yield Input(placeholder="New to-do item...", id="todo_input")
        yield Horizontal(
            Button("Add Item", id="add_button"),
            Button("Remove Item", id="remove_button"),
            Button("Export", id="export_button"),
            Button("Import", id="import_button")
        )
        yield Static("Your To-Do List:", id="list_label")
        yield Static("", id="todo_list")
        yield Static("To-Do List V0.2, press Q to exit.", id="footer")
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
            with open(file_path, "w") as file:
                for item in todo_list:
                    file.write(f"{item}\n")
    def import_todo_list(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
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
            if item_to_remove in todo_list:
                todo_list.remove(item_to_remove)
                input_widget.value = ""
                self.update_todo_list()
        elif event.button.id == "export_button":
            self.export_todo_list()
        elif event.button.id == "import_button":
            self.import_todo_list()
if __name__ == "__main__":
    app = application()
    app.run()