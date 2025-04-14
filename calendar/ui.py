from model import graph,config
import tkinter as tk
from tkinter import scrolledtext


def send_message():
    user_input = entry.get()
    if not user_input.strip():
        return

    chat_box.insert(tk.END, "You: " + user_input + "\n", "user")
    entry.delete(0, tk.END)

    # Store the user message in ChromaDB
    for event in graph.stream({'messages':[{'role':"user",'content':user_input}]}
                            ,config,stream_mode='values'):
        for value in event.values():
            pass
    
    bot_reply = value[-1].content

    chat_box.insert(tk.END, "Bot: " + bot_reply + "\n", "bot")
    chat_box.yview(tk.END)

# Set up the GUI
root = tk.Tk()
root.title("AI agent with Memory & Retrieval")
root.geometry("500x600")

# Chat display
chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=25, font=("Arial", 12))
chat_box.tag_config("user", foreground="blue")
chat_box.tag_config("bot", foreground="red")
chat_box.pack(pady=10, padx=10)

# Input field
entry = tk.Entry(root, width=50, font=("Arial", 14))
entry.pack(pady=5)

# Send button
send_button = tk.Button(root, text="Send", command=send_message, font=("Arial", 12), bg="lightblue")
send_button.pack(pady=5)

# Run the GUI
root.mainloop()