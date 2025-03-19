import threading
from socket import *
from tkinter import *
import tkinter as tk
import customtkinter
from selenium import webdriver
import time
import sys
import os


# closes the server
def close_server():
    global serverSocket
    try:
        serverSocket.close()
    except OSError:
        pass  # Ignore if already closed



# Runs the actual server on a seperate thread for multitasking
def handle_client(connectionSocket, addr):
    global logged_request #flag variable so the server knows new connections

    try:
        message = connectionSocket.recv(1024).decode()  # Receive the HTTP request
        if not message:
            connectionSocket.close()
            return  # No message, return

        # Print the request headers (only once, and for new connections)
        if not logged_request:
            print(f"Received request from {addr}:") #sends to terminal which is redirected to GUI
            print(message)
            redirect_output(f"Received request from {addr}:\n{message}\n")  # Log to textbox
            logged_request = True  # Prevent logging multiple times

        # Process the requested file
        filename = message.split()[1]
        filename = filename.replace("\\", "/")
        filename = filename[1:]
        filename = os.path.normpath(filename)

        if filename.endswith(".html"):
            content_type = "text/html"  # Set content-type for HTML
        elif filename.endswith(".css"):
            content_type = "text/css"  # Set content-type for CSS
        elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
            content_type = "image/jpeg"  # Set content-type for JPG/JPEG
        elif filename.endswith(".png"):
            content_type = "image/png"  # Set content-type for PNG
        else:
            content_type = "text/plain"  # Default content-type for unknown files

        try:
            with open("Webpages/"+filename, 'rb') as f:
                outputdata = f.read()

            responseHeader = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n"      #document sent correctly
            connectionSocket.send(responseHeader.encode())  #sends encoded response header

            connectionSocket.send(outputdata)  # Send the file content to the webpage (already in bytes)

        except IOError:
            # Handle file not found and sends encoded server response to webpage
            responseHeader = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n"
            responseBody = "<html><head></head><body><h1>404 Not Found</h1></body></html>"
            connectionSocket.send(responseHeader.encode())
            connectionSocket.send(responseBody.encode())

    #displays any errors to terminal which gets redirected to GUI
    except OSError as e:
        print(f"Error with client {addr}: {e}")  #curly brackets allows variables inbedded in strings
    finally:
        connectionSocket.close()  # Close connection after handling the client, otherwise connections refuse

# Server update function that accepts and handles multiple connections
def server_update():
    global serverSocket
    while switch_var.get() == "on":
        try:
            # Accept a new client connection
            connectionSocket, addr = serverSocket.accept()
            print(f"New connection from {addr}")

            # Start a new thread to handle the client
            threading.Thread(target=handle_client, args=(connectionSocket, addr), daemon=True).start()

        #displays any errors to terminal
        except Exception as e:
            print(f"Error accepting new connection: {e}")
            break

# Function to start the server
def start_server():
    global serverSocket, number_of_clients
    print("This server runs on localHost and will not allow other devices on the netowrk to connect\n")
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverPort = 4305  # Port number
    serverSocket.bind(('', serverPort)) 
    
    #change to ("0.0.0.0", serverPort) for all connections (firewall/security threat)
    #you will also need to enable port forwarding using your router and public ip adress (not private ip adress asigned to your pc)
    #you can also port forward using 3rd party applications to take care of that
    #port forwarding involves security risks as it allows anyone to have access (if shared)
    #windows security or your router may block port forwarding
    #if enabled anyway, it will allow others to connect to your webserver as long as it is listening for clients
    #this program allows upto 8 configurable clients (simple code only allows 1)
    #allowing multiple clients to access the webpage simultaneously can cause performance issues since each client 
    #recieves a single thread to manage their requests, this is done for improved server performance rather than 
    #client side reliability as managing 50 clients requires 51 threads + 4 to run host OS. 8 clients is a soft limit
    #that can be changed by altering the program code near the end to allow as many clients as you want (not recomended)
    #Also note that connecting more clients than what you select will overload the server and close all connections
    #until all are close or when server is restarted or if the limit is increased


    serverSocket.listen(number_of_clients)  # Allow up to {x} clients to queue up

    print(f'Server is ready and listening on port {serverPort}...')
    # Start accepting and handling connections with new threads
    threading.Thread(target=server_update, daemon=True).start()


def switch_toggle():
    global switch, switch_var
    if switch_var.get() == "on":
        switch.configure(state="disabled", progress_color="green")  # Green when on
        GUI.after(2000, lambda: switch.configure(state="normal"))  # Re-enable after 2 sec
        start_server()  # Start the server
    else:
        switch.configure(progress_color="red", fg_color="red")  # Red when off
        close_server()  # Close the server


#sends terminal data to GUI
def redirect_output(text):
    textbox.configure(state=NORMAL) #the textbox is momentarily active for system to write
    textbox.insert("end", text)  # Insert message to the end of the textbox
    textbox.yview("end")  # Auto-scroll to the latest message
    textbox.configure(state=DISABLED) #otherwise, the textbox is closed from the user

#adds time to the program
def update_time():
    current_time = time.strftime("%H:%M:%S")  # Get current time
    clock_label.configure(text=current_time)  # Update label
    GUI.after(1000, update_time)  # Call function again after 1 sec

#automatically opens up the correct webpage, you can edit the link to show 404
#if localHost is changed, the weblink needs to be altered. Likewise if HTML file is changed or port.
def open_webpage():
    driver = webdriver.Chrome()
    driver.get("http://localhost:4305/sev.html")

#runs functions with threads to allow main program to not freeze
def thread_offload():
    threading.Thread(target=open_webpage, daemon=True).start()


# GUI Setup
GUI = customtkinter.CTk()
GUI.title("Web Server")
GUI.geometry("400x500")
GUI.minsize(width=400, height=500)
GUI.maxsize(width=400, height=500)
customtkinter.set_appearance_mode("dark")
GUI.configure(fg_color="black")

# Create a variable to track switch state
switch_var = customtkinter.StringVar(value="off")

#enables and disables the server
switch = customtkinter.CTkSwitch(GUI, text="Server Switch", command=switch_toggle, variable=switch_var, onvalue="on",
                                 offvalue="off", font=("Arial", 20), progress_color="red", fg_color="red", corner_radius=20, border_width=0)
switch.place(relx=0.83, rely=0.853, anchor=SE)

# Frame for terminal output
frame = customtkinter.CTkFrame(GUI, corner_radius=40, fg_color="black")
frame.place(relx=0.5, rely=0.05, relwidth=0.9, relheight=0.7, anchor=N)

# Create the scrollable Textbox for terminal output
textbox = customtkinter.CTkTextbox(frame, wrap="word", height=10, state=DISABLED)
textbox.pack(side="left", fill="both", expand=True)

#the time text label configuration
clock_label = customtkinter.CTkLabel(GUI, text="", font=("Arial", 20))
clock_label.place(relx=0.15, rely=0.86, anchor=SW)
update_time()  # Start updating the time



#setting up number of connections
# List of values from 1 to 8
combo_values = [str(i) for i in range(1, 9)]

# Create the ComboBox widget with the values from 1 to 8
combo_box = customtkinter.CTkComboBox(GUI, values=combo_values, width=50)
combo_box.place(relx=0.84, rely=0.953, anchor=SE)
combo_box.set("1")  # Set the default number of connections to 1
number_of_clients = int(combo_box.get()) #retrieves an the selected value and converts to integer

connections_label = customtkinter.CTkLabel(GUI, text = "Connections", font=("Arial", 20))
connections_label.place(relx=0.69, rely=0.953, anchor=SE)

#creating test button
open_button = customtkinter.CTkButton(GUI, text="Test", command= lambda: thread_offload(), font=("Arial", 20), fg_color="grey18", width=80,
                                    hover_color="green", corner_radius=20)
open_button.place(relx=0.15, rely=0.953, anchor=SW)

# flag variable to indicate if the request was already performed
logged_request = False

# Redirect sys.stdout to the textbox
sys.stdout.write = redirect_output


GUI.mainloop()
