import tkinter as tk
import os, sys

PLATFORM = sys.platform

if PLATFORM == "win32":
    kvks_route = "Program Files (x86)/Steam/steamapps/commons/FPS Aim Trainer"
elif PLATFORM == "darwin":
    raise Exception("Unknown platform")
elif PLATFORM == "linux":
    kvks_route = "Program Files (x86)/Steam/steamapps/commons/FPS Aim Trainer"
else:
    raise Exception("Unknown platform")

HOME = "/".join(os.getenv("HOME").split("/")[:-2])
DEF_KVKS_PATH = os.path.join(HOME, kvks_route)

def sync(kvks_path: str):
    stats_path = os.path.join(kvks_path, "FPS Aim Trainer/stats")
    print(stats_path)

def main():
    app = tk.Tk()

    app.geometry("600x800")
    app.configure(
        background="#222222"
    )
    tk.Wm.wm_title(app, "Kovaaks tracker")

    kvks_path_var = tk.StringVar(app)

    tk.Label(
        app,
        text="Kovaaks install path",
        justify="center",
        bg="#222222",
        fg="#DDDDDD"
    ).pack(
        fill=tk.Y,
        expand=False
    )

    e = tk.Entry(
        app,
        bg="#DDDDDD",
        fg="#222222",
        justify="left",
        textvariable=kvks_path_var,
    )
    e.insert(tk.END, DEF_KVKS_PATH)
    e.pack(
        fill=tk.X,
        expand=False
    )

    tk.Label(
        app,
        bg="#222222",
        fg="#DDDDDD"
    ).pack(fill=tk.BOTH, expand=True)

    tk.Button(
        app,
        text="Quick sync",
        bg="#DDDDDD",
        fg="#161616",
        relief="flat",
        command=lambda: sync(kvks_path=kvks_path_var.get())
    ).pack(
        fill=tk.Y,
        expand=False
    )

    app.mainloop()

if __name__ == "__main__":
    main()
