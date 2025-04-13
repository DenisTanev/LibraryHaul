import re
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from utils.scrapper import get_books
import os
import tkinter as tk
from tkinter import ttk, filedialog

def fetch_books():
    search_query = search_entry.get()
    format_input = format_var.get()

    if not search_query:
        messagebox.showwarning("Input Error", "Please enter a search term.")
        return

    for widget in result_frame.winfo_children():
        widget.destroy()

    books = get_books(search_query, format_input)

    if not books:
        messagebox.showinfo("No Results", "No books found with the given query.")
        return

    col_count = 3  # Number of columns for the book grid

    for idx, book in enumerate(books):
        title = book['title']
        author = book['author']
        cover_image_url = book['cover_image']
        download_link = book['link']

        try:
            cover_response = requests.get(cover_image_url)
            img_data = cover_response.content
            img = Image.open(BytesIO(img_data))
            img.thumbnail((150, 200))

            img_tk = ImageTk.PhotoImage(img)

            row = (idx // col_count) * 3
            col = idx % col_count

            cover_label = tk.Label(result_frame, image=img_tk)
            cover_label.image = img_tk
            cover_label.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            text_label = tk.Label(result_frame, text=f"{title}\n{author}", font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
            text_label.grid(row=row + 1, column=col, padx=10, pady=5, sticky="nsew")

            download_button = tk.Button(result_frame, text="Download", command=lambda url=download_link: download_book(url))
            download_button.grid(row=row + 2, column=col, padx=10, pady=5, sticky="nsew")
            download_button.config(bg="#800000")

        except Exception as e:
            print(f"Error loading cover image: {e}")
            row = (idx // col_count) * 3
            col = idx % col_count
            cover_label = tk.Label(result_frame, text=f"{title}\n{author}", font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
            cover_label.grid(row=row, column=col, padx=10, pady=10)


def download_book(url):
    print(f"Attempting to download from: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        with requests.get(url, headers=headers, stream=True, timeout=30) as response:
            response.raise_for_status()

            if "Content-Disposition" in response.headers:
                content_disposition = response.headers.get('Content-Disposition')
                filename = re.findall('filename="(.+)"', content_disposition)
                if filename:
                    filename = filename[0]
                else:
                    filename = url.split("/")[-1]
            else:
                filename = url.split("/")[-1]

            import urllib.parse
            filename = urllib.parse.unquote(filename)

            filename = re.sub(r'[\\/*?:"<>|]', "", filename)

            from tkinter import filedialog
            save_path = filedialog.asksaveasfilename(
                defaultextension="." + filename.split('.')[-1] if '.' in filename else ".pdf",
                initialfile=filename
            )

            if not save_path:
                return


            total_size = int(response.headers.get('Content-Length', 0))
            progress_window = None
            progress_bar = None

            if total_size > 1024 * 1024:
                progress_window = tk.Toplevel()
                progress_window.title("Downloading...")
                progress_window.geometry("300x100")

                tk.Label(progress_window, text=f"Downloading {filename}").pack(pady=10)

                progress_bar = tk.ttk.Progressbar(progress_window, length=250, mode="determinate")
                progress_bar.pack(pady=10)

            # Download the file in chunks
            with open(save_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

                        if progress_bar and total_size:
                            downloaded += len(chunk)
                            progress = int((downloaded / total_size) * 100)
                            progress_bar["value"] = progress
                            progress_window.update()

            if progress_window:
                progress_window.destroy()

            messagebox.showinfo("Download Complete", f"Book downloaded as {os.path.basename(save_path)}")

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Download Error", f"Request error: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Error downloading: {str(e)}")


root = tk.Tk()
root.geometry("1400x800")
root.title("Library Haul")

search_label = tk.Label(root, text="Search for Books (Title or Author)", font=('Arial', 14))
search_label.pack(pady=10)

search_entry = tk.Entry(root, font=('Arial', 14), width=40)
search_entry.pack()

format_var = tk.StringVar(value="all")
format_label = tk.Label(root, text="File Format", font=("Arial", 12))
format_label.pack(pady=5)

format_entry = tk.Entry(root, textvariable=format_var, font=("Arial", 12), width=20)
format_entry.pack(pady=5)

search_button = tk.Button(root, text="Find", font=('Arial', 14), command=fetch_books)
search_button.pack(padx=20, pady=20)

canvas = tk.Canvas(root)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

result_frame = tk.Frame(canvas, bg="#2E2E2E")
canvas.create_window((0, 0), window=result_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

result_frame.bind("<Configure>", on_frame_configure)

def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

root.bind_all("<MouseWheel>", on_mouse_wheel)

root.config(bg="#2E2E2E")
search_label.config(bg="#2E2E2E", fg="#FFFFFF")
search_entry.config(bg="#3C3C3C", fg="#FFFFFF", insertbackground='white', bd=2, relief="solid")
search_button.config(bg="#3C3C3C", fg="#FFFFFF", activebackground="#555555", activeforeground="white")
format_label.config(bg="#2E2E2E", fg="#FFFFFF")
format_entry.config(bg="#3C3C3C", fg="#FFFFFF", insertbackground='white', bd=2, relief="solid")
canvas.config(bg="#2E2E2E")

root.mainloop()
