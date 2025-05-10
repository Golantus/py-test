import threading
from socket import *
from customtkinter import *
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2) 


class MainWindow(CTk):
   def __init__(self):
       super().__init__()
       self.geometry('400x300')
       set_appearance_mode('light')
       self.label = None
       # menu frame

       self.menu_frame = CTkFrame(self, fg_color='#E5C275', width=30, height=300)
       self.menu_frame.pack_propagate(False)
       self.menu_frame.place(x=0, y=0)
       self.is_show_menu = False
       self.speed_animate_menu = -5
       self.btn = CTkButton(self, text='▶️', fg_color = '#E6810A' , command=self.toggle_show_menu, width=30, hover_color= '#C86F08')
       self.btn.place(x=0, y=0)
       # main
       self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disable')
       self.chat_field.place(x=0, y=0)
       self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
       self.message_entry.place(x=0, y=0)
       self.message_entry.bind('<Return>', lambda event: self.send_message())
       self.send_button = CTkButton(self, text='>', fg_color = '#E6810A', hover_color= '#C86F08' ,  width=50, height=40, command=self.send_message)
       self.send_button.place(x=0, y=0)
       self.message_entry
       self.username = 'You'
       try:
           self.sock = socket(AF_INET, SOCK_STREAM)
           self.sock.connect(('26.37.53.140', 8080))
           hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
           self.sock.send(hello.encode('utf-8'))
           threading.Thread(target=self.recv_message, daemon=True).start()
       except Exception as e:
           self.add_message(f"Не вдалося підключитися до сервера: {e}")

       self.adaptive_ui()

   def toggle_show_menu(self):
       if self.is_show_menu:
           self.is_show_menu = False
           self.speed_animate_menu *= -1
           self.btn.configure(text='▶️')
           self.show_menu()
       else:
           self.is_show_menu = True
           self.speed_animate_menu *= -1
           self.btn.configure(text='◀️')
           self.show_menu()
           # setting menu widgets
           if not self.label:
            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack()
            self.save_button=CTkButton(self.menu_frame,fg_color='#E6810A',hover_color='#C86F08', text = 'Зберегти', command=self.save_name)
            self.save_button.pack()
            self.label_theme = CTkCheckBox(self.menu_frame,  text='Темна тема', command=self.chenge_theme, hover_color="#E6810A",fg_color="#E6810A")
            self.label_theme.pack(side='bottom', pady=20)


   def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        self.btn.configure(width=self.menu_frame.winfo_width())

        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(5, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            
            self.after(5, self.show_menu)
        elif not self.is_show_menu:
            if self.label and self.entry and self.save_button and self.label_theme:
                self.label.destroy()
                self.label=None
                self.entry.destroy()
                self.save_button.destroy()
                self.label_theme.destroy()

   def save_name(self):
       new_name = self.entry.get().strip()
       if new_name:
           self.username = new_name
           self.add_message(f'Ваш новий нік: {self.username} ')

   def chenge_theme(self):
       if self.label_theme.get():
           set_appearance_mode('dark')
           self.menu_frame.configure(fg_color='#4A4A46')
       else:
           set_appearance_mode('light')
           self.menu_frame.configure(fg_color='#E5C275')



   def adaptive_ui(self):
       self.menu_frame.configure(height=self.winfo_height())
       self.chat_field.place(x=self.menu_frame.winfo_width())
       self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width(),
                                 height=self.winfo_height() - 40)
       self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
       self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
       self.message_entry.configure(
           width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())

       self.after(50, self.adaptive_ui)

   def add_message(self, text):
       self.chat_field.configure(state='normal')
       self.chat_field.insert(END, text + '\n')
       self.chat_field.configure(state='disable')

   def send_message(self):
       message = self.message_entry.get()
       if message:
           self.add_message(f"{self.username}: {message}")
           data = f"TEXT@{self.username}@{message}\n"
           try:
               self.sock.sendall(data.encode())
           except:
               pass
       self.message_entry.delete(0, END)

   def recv_message(self):
       buffer = ""
       while True:
           try:
               chunk = self.sock.recv(4096)
               if not chunk:
                   break
               buffer += chunk.decode()

               while "\n" in buffer:
                   line, buffer = buffer.split("\n", 1)
                   self.handle_line(line.strip())
           except:
               break
       self.sock.close()

   def handle_line(self, line):
       if not line:
           return
       parts = line.split("@", 3)
       msg_type = parts[0]

       if msg_type == "TEXT":
           if len(parts) >= 3:
               author = parts[1]
               message = parts[2]
               self.add_message(f"{author}: {message}")
       elif msg_type == "IMAGE":
           if len(parts) >= 4:
               author = parts[1]
               filename = parts[2]

               self.add_message(f"{author} надіслав(ла) зображення: {filename}")

       else:
           self.add_message(line)


win = MainWindow()
win.mainloop()