import tkinter as tk
from tkinter import ttk
from datetime import datetime

from mnemosyne_journal import JournalEntry, list_available_journal_entries, read_entry


def save_entry(
    input_text: tk.Text,
    password_field: ttk.Entry,
    return_message: tk.StringVar,
    journal_entries: ttk.Combobox,
):
    plaintext = input_text.get("1.0", "end")
    password = password_field.get()

    if len(plaintext) <= 1:
        return_message.set("Please write a journal entry.")
        return

    if len(password) <= 0:
        return_message.set("Please specify a password.")
        return

    entry = JournalEntry(plaintext)
    entry.get_encryption_key(password)
    entry.encrypt_text()
    entry.write_entry()
    return_message.set("Journal entry was saved.")
    input_text.delete("1.0", tk.END)
    password_field.delete(0, tk.END)

    # TODO fix this - this seems bad, but I can't think of a better way to reflect the new saved
    #      entry for reading purposes
    journal_entries.configure(values=load_possible_entries())


def load_entry(
    entry_id: str,
    password_field: ttk.Entry,
    text_var: tk.StringVar,
    message_var: tk.StringVar,
) -> None:
    password = password_field.get()

    if len(password) <= 0:
        message_var.set("Please enter password.")
        return

    entry_time = datetime.strptime(entry_id, "%b %d %Y - %H:%M:%S")
    entry_name = entry_time.strftime("%Y%m%d%H%M%S.txt")
    entry: JournalEntry = read_entry(entry_name)
    decrypt_message = entry.decrypt_text(password)
    if decrypt_message:
        message_var.set(decrypt_message)
    text_var.set(entry.plaintext)


def load_possible_entries() -> list[str]:
    raw_entries = list_available_journal_entries()
    formatted_entries: list[str] = []
    for index, entry_name in enumerate(raw_entries, start=1):
        entry: datetime = datetime.strptime(entry_name, "%Y%m%d%H%M%S")
        formatted_entries.append(entry.strftime("%b %d %Y - %H:%M:%S"))
    return formatted_entries


def start_tkinter_gui() -> None:
    root = tk.Tk()
    root.title("Mnemosyne Journal")

    tab_manager = ttk.Notebook(root)
    tab_write = ttk.Frame(tab_manager)
    tab_read = ttk.Frame(tab_manager)
    tab_manager.add(tab_write, text="Write New Entry")
    tab_manager.add(tab_read, text="Read Existing Entry")
    tab_manager.pack(expand=True, fill="both")

    # Writing Entries Tab
    input_text_helper = ttk.Entry(tab_write)
    input_text = tk.Text(
        input_text_helper,
        borderwidth=0,
        width=80,
        height=15,
        highlightthickness=3,
        highlightcolor="#8fb0df",
        font=(
            "Helvetica",
            14,
        ),
    )
    input_text.pack()
    input_text_helper.grid(column=0, row=0, columnspan=4)

    password_label = ttk.Label(tab_write, text="Password:")
    password_label.grid(column=0, row=2, columnspan=1, sticky="e")

    password = ttk.Entry(tab_write, show="*")
    password.grid(column=1, row=2, columnspan=1, sticky="w")

    message = tk.StringVar(value="No new messages.")
    message_label = ttk.Label(tab_write, textvariable=message)
    message_label.grid(column=0, row=3, columnspan=4)

    save_button = ttk.Button(
        tab_write,
        text="Save",
        command=lambda: save_entry(input_text, password, message, journal_entries),
    )
    save_button.grid(column=3, row=2, columnspan=1, sticky="e")

    # Reading Entries Tab
    journal_entries_label = ttk.Label(tab_read, text="Entries")
    journal_entries_label.grid(column=0, row=1, padx=10, sticky="e")

    journal_entries = ttk.Combobox(tab_read, values=load_possible_entries())
    journal_entries.grid(column=1, row=1)

    journal_entry_select_button = ttk.Button(
        tab_read,
        text="Open",
        command=lambda: load_entry(
            journal_entries.get(),
            password_entry_open,
            entry_text,
            message_label_text_open,
        ),
    )
    journal_entry_select_button.grid(column=2, row=1, padx=10)

    password_label_open = ttk.Label(tab_read, text="Password")
    password_label_open.grid(column=0, row=2, sticky="e")

    password_entry_open = ttk.Entry(tab_read, show="*")
    password_entry_open.grid(column=1, row=2)

    message_label_text_open = tk.StringVar(value="No new messages.")
    message_label_open = ttk.Label(tab_read, textvariable=message_label_text_open)
    message_label_open.grid(column=0, row=0, columnspan=3)

    entry_text = tk.StringVar(value="")
    journal_entry_box = ttk.Label(tab_read, textvariable=entry_text)
    journal_entry_box.grid(column=0, row=3, columnspan=3, sticky="w", pady=20)

    root.mainloop()
