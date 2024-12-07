import dotenv
import logging
import os
import pymysql
from pymysql import cursors, Error
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

global DB_HOST, DB_USER, DB_PASSWORD, DB_PORT, DB_NAME, TABLE_PROXY, VERSION, APP_NAME, filename, proxy_list

APP_NAME = "Proxy Extractor"
VERSION = 1.0
filename = " "
proxy_list = []

BASE_DIR = os.path.dirname(__file__)
APPDATA_PATH = os.path.join(os.getenv('LOCALAPPDATA'), 'YD', APP_NAME)
DOTENV_PATH = os.path.join(APPDATA_PATH, ".env")


if not os.path.exists(APPDATA_PATH):
    os.makedirs(APPDATA_PATH)

logging.basicConfig(
    filename=os.path.join(APPDATA_PATH, f'{APP_NAME}.log'),
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %I:%M:%S %p',
)


if sys.platform == "win32":
    # show logo in taskbar when app is opened
    try:
        from ctypes import windll  # Only exists on Windows.
        myappid = "yd.proxy_extractor.1_0"
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError as e:
        logging.error(e)



def create_new_env_file():
    file_content = f'''DB_HOST=\nDB_USER=\nDB_PASSWORD=\nDB_PORT=\nDB_NAME=\nTABLE_PROXY=\nVERSION={VERSION}'''
    os.makedirs(APPDATA_PATH, exist_ok=True)
    with open(DOTENV_PATH, "x") as f:
        f.write(file_content)



def load_env_variables():
    # if not (os.path.exists(DOTENV_PATH) and os.access(DOTENV_PATH, os.R_OK)):
    if not os.path.isfile(DOTENV_PATH):
        create_new_env_file()

    dotenv.load_dotenv(DOTENV_PATH)
    global DB_HOST, DB_USER, DB_PASSWORD, DB_PORT, DB_NAME, TABLE_PROXY
    DB_HOST = os.environ.get("DB_HOST")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_PORT = os.environ.get("DB_PORT")
    DB_NAME = os.environ.get("DB_NAME")
    TABLE_PROXY = os.environ.get("TABLE_PROXY")



def open_text_file():
    # file type
    filetypes = (
        ('Text Files (*.txt)', '*.txt'),
    )

    # show the open file dialog
    f = filedialog.askopenfile(filetypes=filetypes)
    global filename
    filename = f.name

    # read the text file and show its content in the Text
    try:
        text.config(state=tk.NORMAL)
        text.delete('1.0', tk.END)
        text.insert('1.0', "\n".join(f.readlines()))
        text.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror(title = "Error!", message = "There was an error reading the file.")



def format_proxies():
    if filename.isspace():
        messagebox.showinfo(title="", message="Choose a file first.")
    else:
        text.config(state=tk.NORMAL)
        text.delete('1.0', tk.END)
        global proxy_list

        try:
            f = open(f"{filename}", "rt")
            for line in f:
                split = line.strip().split(":")
                converted_proxy = f"{split[2]}:{split[3]}@{split[0]}:{split[1]}"
                proxy_list.append(converted_proxy)
            text.insert('1.0', "\n\n".join(proxy_list))
            text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror(title = "Error!", message = "Failed to change the format of the proxies.")
            logging.error(e)



def transfer_proxies():
    if filename.isspace():
        messagebox.showinfo(title="", message="Choose a file first.")
    elif len(proxy_list)==0:
        messagebox.showinfo(title="", message="Format the proxies first.")
    else:
        answer = messagebox.askyesno("Confirm", f"Are you sure you want to update the proxies in {DB_HOST}:{DB_PORT}/{DB_NAME}?")
        if answer:
            try:
                cnx = pymysql.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=int(DB_PORT), 
                                    database=DB_NAME, connect_timeout=5, cursorclass=cursors.DictCursor)
                cursor = cnx.cursor()
                truncate_query = f"TRUNCATE `{TABLE_PROXY}`;"
                cursor.execute(truncate_query)

                data = [(link,) for link in proxy_list]
                insert_proxy_query = f"INSERT INTO `{TABLE_PROXY}` (proxy_url) VALUES (%s);"
                cursor.executemany(insert_proxy_query, data)
                cnx.commit()

                text.config(state=tk.NORMAL)
                text.delete('1.0', tk.END)
                text.config(state=tk.DISABLED)
                
                messagebox.showinfo(title="Success!", message=f"{cursor.rowcount} proxies inserted successfully.")
            except Error as e:
                messagebox.showerror(title = "Error!", message = "There was an error transferring the proxies to the database.")
                logging.error(e)
            except Exception as e:
                messagebox.showerror(title = "Error!", message = "An unexpected error occurred. Check the database connection details.")
                logging.error(e)
            finally:
                if cnx.open:
                    cursor.close()
                    cnx.close()



def show_about():
    about_text = "An app to convert Bright Data proxies to an HTTP request-friendly format and save to database specified in the .env file.\n\n브라이트 데이터 프록시를 크롤러 친화적인 형식으로 변환하고 .env 파일에 지정된 데이터베이스에 저장하는 앱입니다."
    messagebox.showinfo(title = "About", message = f"{about_text}\n\nContributor: Yaw\n©2024")



def save_db_details():
    try:
        env_file = dotenv.find_dotenv(DOTENV_PATH)
        for tb in textboxes:
            os.environ[tb[0]] = tb[1].get()

            # Write changes to .env file.
            dotenv.set_key(env_file, tb[0], os.environ[tb[0]])

        load_env_variables()
        messagebox.showinfo(title="", message="Connection details saved.")
    except Exception as e:
        messagebox.showerror(title = "Error!", message = f"{e}")
        logging.error(e)



load_env_variables()

root = tk.Tk()
root.title(f"{APP_NAME} {VERSION}")
root.iconbitmap(os.path.join(BASE_DIR, "logo.ico"))
root.geometry('950x600')

frame = tk.Frame(root)
frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

text = scrolledtext.ScrolledText(frame, height=20)
text.config(state=tk.DISABLED)
text.pack(side=tk.LEFT, padx=15, pady=5)

form_frame = tk.Frame(frame)
form_frame.pack(side=tk.LEFT, pady=5)
form_labels = [("Host: ", "DB_HOST", DB_HOST), ("Port: ", "DB_PORT", DB_PORT), ("Database: ", "DB_NAME", DB_NAME), 
               ("Table: ", "TABLE_PROXY", TABLE_PROXY), ("User: ", "DB_USER", DB_USER), 
               ("Password: ", "DB_PASSWORD", DB_PASSWORD)]
textboxes = []

for fl in form_labels:
    label = tk.Label(form_frame, text=fl[0], anchor="w")
    label.pack(pady=5)

    if fl[1] == "DB_PASSWORD":
        textbox = tk.Entry(form_frame, show="*", width=40)
    else:
        textbox = tk.Entry(form_frame, width=40)

    if fl[2] is not None:
        textbox.insert(0, fl[2])
    else:
        textbox.insert(tk.END, "")

    textbox.pack(fill=tk.X, padx=5, pady=2)
    textboxes.append((fl[1], textbox))

btn_save = tk.Button(form_frame, text="Save DB details", command=save_db_details, bg="#008CBA")
btn_save.pack(fill=tk.X, padx=5, pady=10)

button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=100)


btn_choose_file = tk.Button(button_frame, text="Choose file...", command=open_text_file, width=15, bg="#008CBA")
btn_format = tk.Button(button_frame, text="Format", command=format_proxies, width=15, bg="#008CBA")
btn_db = tk.Button(button_frame, text="Save in DB", command=transfer_proxies, width=15, bg="#008CBA")
btn_about = tk.Button(button_frame, text="About", command=show_about, width=15, bg="#04AA6D")

btn_choose_file.pack(side=tk.LEFT, padx=10)
btn_format.pack(side=tk.LEFT, padx=10)
btn_db.pack(side=tk.LEFT, padx=10)
btn_about.pack(side=tk.LEFT, padx=10)

root.mainloop()
