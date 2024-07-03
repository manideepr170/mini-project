import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from hashlib import sha256
import os
import pickle
from Block import Block
from Blockchain import Blockchain

class CertificateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blockchain Based Certificate Validation")
        self.root.geometry("800x600")
        self.root.state("zoomed")

        # Initialize Blockchain
        self.blockchain = Blockchain()
        if os.path.exists('blockchain_contract.txt'):
            with open('blockchain_contract.txt', 'rb') as fileinput:
                self.blockchain = pickle.load(fileinput)

        # Load the background image
        self.bg_image = Image.open("blockchain-wallpaper.jpg")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Create a canvas to place the background image
        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Container frame
        self.container = tk.Frame(self.root, bg=self.root["bg"], bd=0, highlightthickness=3, highlightbackground="green")

        #self.container = tk.Frame(self.root, bg=self.root["bg"], bd=3)
        self.container.place(relx=0.5, rely=0.5, anchor="center", width=800, height=500)

        # Title
        self.title = tk.Label(self.container, text="Blockchain Based Certificate Validation", font=("Arial", 30, "bold"), bg=self.root["bg"], fg="blue")
        self.title.pack(pady=10)

        # Input frame
        self.input_frame = tk.Frame(self.container, bg=self.root["bg"])
        self.input_frame.pack(pady=10)

        # Input fields and labels
        self.create_input_field("Roll Number:", "roll_entry", 0)
        self.create_input_field("Student Name:", "name_entry", 1)
        self.create_input_field("Contact No.:", "contact_entry", 2)

        # Certificate File
        self.file_label = tk.Label(self.input_frame, text="Certificate File:", font=("Arial", 14, "bold"), bg=self.root["bg"])
        self.file_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.file_button = tk.Button(self.input_frame, text="Choose File", command=self.choose_file)
        self.file_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.file_chosen_label = tk.Label(self.input_frame, text="No file chosen", font=("Arial", 14, "bold"), bg=self.root["bg"])
        self.file_chosen_label.grid(row=3, column=2, padx=5, pady=5, sticky="w")

        # Save and Verify Buttons
        self.button_frame = tk.Frame(self.container, bg=self.root["bg"])
        self.button_frame.pack(pady=10)

        button_style = {"bg": "red", "fg": "white", "font": ("Arial", 14, "bold"), "width": 15, "height": 1}

        self.save_button = tk.Button(self.button_frame, text="Save Certificate", **button_style, command=self.save_certificate)
        self.save_button.pack(side="left", padx=20)

        self.verify_button = tk.Button(self.button_frame, text="Verify Certificate", **button_style, command=self.verify_certificate)
        self.verify_button.pack(side="left", padx=20)

        # Certificate Text Area
        self.certificate_text = tk.Text(self.container, height=4, width=40, font=("Arial", 14))
        self.certificate_text.pack(padx=10, pady=20, expand=True, fill='both')

    def create_input_field(self, label_text, attr_name, row):
        label = tk.Label(self.input_frame, text=label_text, font=("Arial", 14, "bold"), bg=self.root["bg"])
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        entry = tk.Entry(self.input_frame, width=40, font=("Arial", 14))
        entry.grid(row=row, column=1, columnspan=2, padx=10, pady=5, sticky="w")
        setattr(self, attr_name, entry)

    def choose_file(self):
        self.filepath = filedialog.askopenfilename(initialdir="certificate_templates")
        if self.filepath:
            self.file_chosen_label.config(text=self.filepath.split('/')[-1])

    def save_certificate(self):
        roll_no = self.roll_entry.get()
        student_name = self.name_entry.get()
        contact_no = self.contact_entry.get()
        
        if self.filepath and roll_no and student_name and contact_no and contact_no.isdigit() and (9 < len(contact_no) < 11):
            with open(self.filepath, "rb") as f:
                bytes = f.read()
            digital_signature = sha256(bytes).hexdigest()
            data = f"{roll_no}#{student_name}#{contact_no}#{digital_signature}"
            self.blockchain.add_new_transaction(data)
            hash = self.blockchain.mine()
            b = self.blockchain.chain[-1]
            self.certificate_text.insert(tk.END, f"Blockchain Previous Hash : {b.previous_hash}\nBlock No : {b.index}\nCurrent Hash : {b.hash}\n")
            self.certificate_text.insert(tk.END, f"Certificate Digital Signature : {digital_signature}\n\n")
            self.blockchain.save_object(self.blockchain, 'blockchain_contract.txt')
            messagebox.showinfo("Save Certificate", "Certificate saved with digital signature!")
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields, select a file, and ensure contact number is valid.")

    def verify_certificate(self):
        if self.filepath:
            with open(self.filepath, "rb") as f:
                bytes = f.read()
            digital_signature = sha256(bytes).hexdigest()
            flag = True
            for i in range(1, len(self.blockchain.chain)):
                b = self.blockchain.chain[i]
                data = b.transactions[0]
                arr = data.split("#")
                if arr[3] == digital_signature:
                    self.certificate_text.insert(tk.END, "Uploaded Certificate Validation Successful\n")
                    self.certificate_text.insert(tk.END, "Details extracted from Blockchain after Validation\n\n")
                    self.certificate_text.insert(tk.END, f"Roll No : {arr[0]}\n")
                    self.certificate_text.insert(tk.END, f"Student Name : {arr[1]}\n")
                    self.certificate_text.insert(tk.END, f"Contact No   : {arr[2]}\n")
                    self.certificate_text.insert(tk.END, f"Digital Sign : {arr[3]}\n")
                    flag = False
                    break
            if flag:
                self.certificate_text.insert(tk.END, "Verification failed or certificate modified")
                messagebox.showwarning("Verify Certificate", "Verification failed or certificate modified")
        else:
            messagebox.showwarning("Input Error", "Please select a file to verify.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CertificateApp(root)
    root.mainloop()
