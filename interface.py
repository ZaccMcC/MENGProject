import tkinter as tk

def on_click():
    label.config(text="Hello, Tkinter!")


def toggle():
    if toggle_button.config('text')[-1] == 'OFF':
        toggle_button.config(text="ON", bg="#d0f0c0", activebackground="#c0e8b0")
    else:
        toggle_button.config(text="OFF", bg="#f0d0d0", activebackground="#e8b0b0")

# Create the main window
root = tk.Tk()

# Set window title
root.title("Attitude determinator")

# Set window size (width x height)
root.geometry("600x400")

# Label
label = tk.Label(root, text="Click the button below")
label.pack(pady=10)

# Button
button = tk.Button(root, text="Click Me", command=on_click)
button.pack(pady=10)

toggle_button = tk.Button(root, text='OFF', width=10, command=toggle, bg='white')
toggle_button.pack(pady=20)

# Start the GUI event loop
root.mainloop()