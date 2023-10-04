import tkinter as tk
from tkinter import font
from Class.MAVlink import MyMAVlink
from PIL import ImageTk, Image
import io
import base64
from datetime import datetime
class DroneControlApp:
    def __init__(self, string, baud, queue) -> None:
        self.MyCopter = MyMAVlink(connection_string= string, baudrate= baud, queue= queue)
        self.window = tk.Tk()
        self.window.geometry()
        self.window.title('Drone Control App')
        #Customize font
        self.custom_font_title = font.Font(family="Tahoma", size=30, weight="bold", slant="italic")
        self.custom_font_label = font.Font(underline=True,weight='bold')
        self.custom_font_drop = font.Font(family="Tahoma", size=18, weight="bold")
        self.custom_font_arrow = font.Font(size=23)
        
        self.label_title = tk.Label(master=self.window, text= 'Drone Control',font=self.custom_font_title, width= 20)
        self.label_title.grid(row=0,column= 0, columnspan=2)

        self.create_search_frame()
        self.create_transit_frame()
        self.create_logo_frame()
        self.create_movement_frame()
        self.create_mavlink_terminal_frame()
        self.create_ai_data_terminal_frame()
        self.window.mainloop()
        
    def create_logo_frame(self):
        self.frame_logo = tk.Frame(self.window,borderwidth=1,width=300, height=350)
        self.frame_logo.grid_propagate(False)
        self.frame_logo.place(x=0,y=0)

        #Linh's Path
        # self.path_logo_bk = r'C:\Users\Duy Linh\Desktop\Desktop\[STUDY]\223\Fly_Me Project\followme_hw\followme_hw\CopterAAVC\Logo\logo_bk.png'
        # self.path_logo_crsc = r'C:\Users\Duy Linh\Desktop\Desktop\[STUDY]\223\Fly_Me Project\followme_hw\followme_hw\CopterAAVC\Logo\logo_crsc.png'
        
        #Thien's Path
        self.path_logo_bk = r'C:\Users\Admin\Desktop\PersonalFile\Python\CRSC\followme_hw\CopterAAVC\Logo\logo_bk.png'
        self.path_logo_crsc = r'C:\Users\Admin\Desktop\PersonalFile\Python\CRSC\followme_hw\CopterAAVC\Logo\logo_crsc.png'

        with open(self.path_logo_bk, "rb") as img_file:
            self.image_base64 = base64.b64encode(img_file.read())

        self.image_data = base64.b64decode(self.image_base64)
        self.image = Image.open(io.BytesIO(self.image_data))
        self.image = self.image.resize((70, 50))

        self.image_tk = ImageTk.PhotoImage(self.image)

        self.image_label = tk.Label(self.frame_logo, image=self.image_tk)
        self.image_label.pack(side='left')

        with open(self.path_logo_crsc, "rb") as img_file:
            self.image_base64_2 = base64.b64encode(img_file.read())

        self.image_data_2 = base64.b64decode(self.image_base64_2)
        self.image_2 = Image.open(io.BytesIO(self.image_data_2))
        self.image_2 = self.image_2.resize((30, 30))

        self.image_tk_2 = ImageTk.PhotoImage(self.image_2)

        self.image_label_2 = tk.Label(self.frame_logo, image=self.image_tk_2)
        self.image_label_2.pack(side='left')
        pass
    
    def create_search_frame(self):
        self.frame_search = tk.Frame(self.window,borderwidth=1,relief='solid',width=320, height=400)
        self.frame_search.grid_propagate(False)
        self.frame_search.grid(row=1,column=1,padx = 5,pady=5)

        button_width = 15
        button_heigth = 2

        def button_drop_warning():
            top = tk.Toplevel()
            top.title("WARNING!!")

            # Set the width and height of the dialog
            dialog_width = 300
            dialog_height = 170
            
            # Get the screen width and height
            screen_width = top.winfo_screenwidth()
            screen_height = top.winfo_screenheight()

            # Calculate the x and y coordinates of the top-left corner
            x = (screen_width - dialog_width) // 2
            y = (screen_height - dialog_height) // 2

            # Set the geometry of the dialog to position it in the center
            top.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

            label_warning = tk.Label(top, text="Do you want to drop the package ?", font='Arial 13')
            label_warning.grid(row=0, column=0, columnspan=2, padx=15,pady=30)

            button_yes = tk.Button(top, text="Yes",background="green", command=lambda:[self.MyCopter.rc_channel_override([[6],[2000]]),(top.destroy())], width=15, height= 2)
            button_yes.grid(row=1, column=0, columnspan=1)

            button_no = tk.Button(top, text="No",background="red", command=top.destroy,width=15, height=2)
            button_no.grid(row=1, column=1, columnspan=1)

        self.label_search = tk.Label(master=self.frame_search, text='Search Operation', font = self.custom_font_label)
        self.button_cont = tk.Button(master=self.frame_search, text='Continue',width=button_width,height=button_heigth,command= lambda: [self.MyCopter.mission_interaction(1), self.print_cmd_ack()])
        self.button_stop = tk.Button(master=self.frame_search, text='Stop',width=button_width,height=button_heigth,command= lambda: [self.MyCopter.mission_interaction(0), self.print_cmd_ack()])
        self.button_takeGPS = tk.Button(master=self.frame_search, text='Take GPS',width=button_width,height=button_heigth,command= lambda: [self.MyCopter.get_gps_position(), self.print_data(data= self.MyCopter.mannequin_GPS, frame= self.mavlink_text, text= "Mannequin GPS: ")])
        self.button_go_to_mannequin = tk.Button(master=self.frame_search, text='Go To Mannequin',width=button_width,height=button_heigth,command= lambda: [self.MyCopter.do_reposition(self.MyCopter.mannequin_GPS), self.print_cmd_ack()])
        self.button_drop = tk.Button(master=self.frame_search, text='DROP',font = self.custom_font_drop,width=10,height=1,bg = 'red',bd=5,command=button_drop_warning)
        self.get_AI_data = tk.Button(master=self.frame_search, text="Get AI Data",width=button_width,height=button_heigth,command= lambda: [self.MyCopter.get_ai_target_data(), self.print_data(data= self.MyCopter.AI_data, frame= self.ai_data_text, text= "AI Data: "), self.print_data(data= self.MyCopter.AI_control_parameters, frame= self.ai_data_text, text= "Control parameters: ")])
        self.AI_control = tk.Button(master=self.frame_search, text="AI Control",width=button_width,height=button_heigth,command= lambda: self.MyCopter.ai_control())
        self.AI_control_start = tk.Button(master=self.frame_search, text="AIAC Start",width=button_width,height=button_heigth,command= lambda: self.MyCopter.ai_start_autocontrol())
        self.AI_control_stop = tk.Button(master=self.frame_search, text="AIAC Stop",width=button_width,height=button_heigth,command= lambda: self.MyCopter.ai_stop_autocontrol())
        
        padx_button_search = 20
        pady_button_search = 10
        
        self.label_search.grid(row=0,column=0,columnspan=2,padx=20,pady=10)
        self.button_cont.grid(row=1,column=0,padx=padx_button_search,pady=pady_button_search)
        self.button_stop.grid(row=1,column=1,padx=padx_button_search,pady=pady_button_search)
        self.button_takeGPS.grid(row=2,column=0,padx=padx_button_search,pady=pady_button_search)
        self.button_go_to_mannequin.grid(row=2,column=1,padx=padx_button_search,pady=pady_button_search)
        self.get_AI_data.grid(row=3,column=0,padx=padx_button_search,pady=pady_button_search)
        self.AI_control.grid(row=3,column=1,padx=padx_button_search,pady=pady_button_search)
        self.AI_control_start.grid(row=4,column=0,padx=padx_button_search,pady=pady_button_search)
        self.AI_control_stop.grid(row=4,column=1,padx=padx_button_search,pady=pady_button_search)
        self.button_drop.grid(row=5,column=0,columnspan=2,padx= padx_button_search,pady=pady_button_search)

    def create_transit_frame(self):
        self.frame_transit = tk.Frame(self.window,borderwidth=1,relief='solid',width=320, height=400)
        self.frame_transit.grid_propagate(False)
        self.frame_transit.grid(row=1,column=0,padx = 5,pady=5)

        button_width = 15
        button_heigth = 2
        entry_width = 5

        self.label_transit = tk.Label(master=self.frame_transit, text='Transit Operation', font = self.custom_font_label)
        self.label_m = tk.Label(master=self.frame_transit,text = 'm')
        self.label_ms = tk.Label(master=self.frame_transit,text = 'm/s')
        self.button_guidedmode = tk.Button(master=self.frame_transit, text='Guided', width=button_width,height=button_heigth,command= lambda: [self.MyCopter.set_mode(4), self.print_cmd_ack()])
        self.button_RTH = tk.Button(master=self.frame_transit, text='RTH',width=button_width,height=button_heigth,command= lambda: [self.MyCopter.return_to_land(), self.print_cmd_ack()])
        self.button_automode = tk.Button(master=self.frame_transit, text='Auto', width=button_width,height=button_heigth,command= lambda: [self.MyCopter.set_mode(3), self.print_cmd_ack()])
        self.button_arm = tk.Button(master=self.frame_transit, text='Arm', width=button_width,height=button_heigth,command= lambda: [self.MyCopter.arm_disarm(1), self.print_cmd_ack()])
        self.button_takeoff = tk.Button(master=self.frame_transit, text='Takeoff',width=button_width,height=button_heigth,command= lambda: [self.MyCopter.take_off(int(self.entry_arm.get())), self.print_cmd_ack()])
        self.button_setspeed = tk.Button(master=self.frame_transit, text='Set Speed',width=button_width,height=button_heigth,command= lambda: [self.MyCopter.set_speed([1,int(self.entry_setspeed.get())]), self.print_cmd_ack()])
        self.button_123 = tk.Button(master=self.frame_transit, text='Enter transit 1-2-3',width=button_width,height=button_heigth,command= lambda: [self.MyCopter.set_current_mission(1), self.print_cmd_ack()])
        self.button_321 = tk.Button(master=self.frame_transit, text='Exit transit 3-2-1',width=button_width,height=button_heigth,command= lambda: [self.MyCopter.set_current_mission(20), self.print_cmd_ack()])
        self.button_sethome_takeoffpoint = tk.Button(master=self.frame_transit, text='Home Takeoff Point',width=button_width,height=button_heigth,command= lambda: [self.MyCopter.set_home(self.MyCopter.takeoff_point_GPS), self.print_cmd_ack()])
        self.button_sethome_transitpoint1 = tk.Button(master=self.frame_transit, text='Home Transit Point 1',width=button_width,height=button_heigth,command= lambda: [self.MyCopter.set_home(self.MyCopter.transit_point_GPS), self.print_cmd_ack()])
        
        self.entry_setspeed = tk.Entry(master= self.frame_transit,width=entry_width,font='Arial 18')
        self.entry_arm = tk.Entry(master= self.frame_transit,width=entry_width,font = 'Arial 18')
        
        padx_button_transit = 20
        pady_button_transit = 10
        
        self.label_transit.grid(row=0,column=0,columnspan=2,padx=padx_button_transit,pady=pady_button_transit)
        self.label_m.place(x=115,y=240)
        self.label_ms.place(x=270,y=240)
        self.button_arm.grid(row=1,column=0,padx=padx_button_transit,pady=pady_button_transit)
        self.button_guidedmode.grid(row=1,column=1,padx=padx_button_transit,pady=pady_button_transit)
        self.button_automode.grid(row=2,column=0,padx=padx_button_transit,pady=pady_button_transit)
        self.button_RTH.grid(row=2,column=1,padx=padx_button_transit,pady=pady_button_transit)
        self.button_takeoff.grid(row=3,column=0,padx=padx_button_transit,pady=pady_button_transit)
        self.button_setspeed.grid(row=3,column=1,padx=padx_button_transit,pady=pady_button_transit)
        self.button_123.grid(row=5,column=0,padx=padx_button_transit,pady=pady_button_transit)
        self.button_321.grid(row=5,column=1,padx=padx_button_transit,pady=pady_button_transit)
        self.button_sethome_takeoffpoint.grid(row=6,column=0,padx=padx_button_transit,pady=pady_button_transit)
        self.button_sethome_transitpoint1.grid(row=6,column=1,padx=padx_button_transit,pady=pady_button_transit)

        padx_entry = 20
        pady_entry = 1
        self.entry_arm.grid(row=4,column=0,padx=padx_entry,pady=pady_entry)
        self.entry_setspeed.grid(row=4,column=1,padx=padx_entry,pady=pady_entry)
    
    def create_movement_frame(self):
        self.frame_movement = tk.Frame(self.window,borderwidth=1,relief='solid',width=660, height=200)
        self.frame_movement.grid_propagate(False)
        self.frame_movement.grid(row=2,column=0,columnspan=2,padx = 10,pady=10)

        #Create component
        self.label_movement = tk.Label(master=self.frame_movement, text='Drone Movement', font = self.custom_font_label)
        self.label_DistantToMove = tk.Label(master=self.frame_movement, text='Distance:         m',font = 'Arial 13')
        self.label_AltitudeToMove = tk.Label(master=self.frame_movement, text='Altitude:         m',font = 'Arial 13')
        self.label_YawAngleToRotate = tk.Label(master=self.frame_movement, text='Yaw:         deg',font = 'Arial 13')
        self.button_forward = tk.Button(master=self.frame_movement, text='↑',font=self.custom_font_arrow,width=3,height=1,bd = 3,command= lambda: self.MyCopter.move_forward(float(self.entry_DistantToMove.get())))
        self.button_backward = tk.Button(master=self.frame_movement, text='↓',font=self.custom_font_arrow,width=3,height=1,bd = 3,command= lambda: self.MyCopter.move_backward(float(self.entry_DistantToMove.get())))
        self.button_left = tk.Button(master=self.frame_movement, text='←',font=self.custom_font_arrow,width=3,height=1,bd = 3,command= lambda: self.MyCopter.move_left(float(self.entry_DistantToMove.get())))
        self.button_right = tk.Button(master=self.frame_movement, text='→',font=self.custom_font_arrow,width=3,height=1,bd = 3,command= lambda: self.MyCopter.move_right(float(self.entry_DistantToMove.get())))
        self.button_up = tk.Button(master=self.frame_movement, text='⏫',font=self.custom_font_arrow,width=5,height=1,bd = 3,command= lambda: self.MyCopter.move_up(float(self.entry_AltitudeToMove.get())))
        self.button_down = tk.Button(master=self.frame_movement, text='⏬',font=self.custom_font_arrow,width=5,height=1,bd = 3,command= lambda: self.MyCopter.move_down(float(self.entry_AltitudeToMove.get())))
        self.button_rotate_clockwise = tk.Button(master=self.frame_movement, text='↩️',font=self.custom_font_arrow,width=5,height=1,bd = 3,command= lambda: [self.MyCopter.do_change_yaw([int(self.entry_YawAngleToRotate.get()), 1]), self.print_cmd_ack()])
        self.button_rotate_counterclockwise = tk.Button(master=self.frame_movement, text='↪️',font=self.custom_font_arrow,width=5,height=1,bd = 3,command= lambda: [self.MyCopter.do_change_yaw([int(self.entry_YawAngleToRotate.get()), -1]), self.print_cmd_ack()])
        self.entry_DistantToMove = tk.Entry(master = self.frame_movement, width= 5)
        self.entry_AltitudeToMove = tk.Entry(master = self.frame_movement, width= 5)
        self.entry_YawAngleToRotate = tk.Entry(master= self.frame_movement, width= 5)
        
        #Place component
        self.label_movement.place(x=250,y=5)
        self.label_DistantToMove.place(x = 80, y = 170)
        self.entry_DistantToMove.place(x = 160, y = 172)
        self.label_AltitudeToMove.place(x = 320, y = 170)
        self.entry_AltitudeToMove.place(x = 390, y = 172)
        self.label_YawAngleToRotate.place(x = 500, y = 170)
        self.entry_YawAngleToRotate.place(x = 545, y = 172)
        
        self.button_forward.place(x = 110, y= 30)
        self.button_backward.place(x = 110, y= 100)
        self.button_left.place(x = 40, y= 65)
        self.button_right.place(x = 180, y= 65)
        self.button_up.place(x = 330, y = 30)
        self.button_down.place(x = 330, y = 100)
        self.button_rotate_clockwise.place(x = 505, y = 30)
        self.button_rotate_counterclockwise.place(x = 505, y = 100)
        
    def create_mavlink_terminal_frame(self):
        self.frame_mavlink = tk.Frame(self.window,borderwidth=1,relief='solid',width=320, height=300)
        self.frame_mavlink.grid_propagate(False)
        self.frame_mavlink.grid(row=3,column=0,padx = 5,pady=5)
        
        self.mavlink_text = tk.Text(master= self.frame_mavlink, width= 36, height= 15)
        self.mavlink_text.grid(row=1,column=0,padx=14,pady=0)
        
        self.label_mavlink_terminal= tk.Label(master=self.frame_mavlink, text='Mavlink Terminal', font = self.custom_font_label)
        self.label_mavlink_terminal.grid(row=0,column=0,columnspan=2,padx=95,pady=10)
        
    def create_ai_data_terminal_frame(self):
        self.frame_ai_data = tk.Frame(self.window,borderwidth=1,relief='solid',width=320, height=300)
        self.frame_ai_data.grid_propagate(False)
        self.frame_ai_data.grid(row=3,column=1,padx = 5,pady=0)
        
        self.ai_data_text = tk.Text(master= self.frame_ai_data, width= 36, height= 15)
        self.ai_data_text.grid(row=1,column=0,padx=14,pady=0)
        
        self.label_ai_data_terminal= tk.Label(master=self.frame_ai_data, text='AI Data Terminal', font = self.custom_font_label)
        self.label_ai_data_terminal.grid(row=0,column=0,columnspan=2,padx=85,pady=10)
        
    def print_data(self, data, frame, text):
        self.current_time = datetime.now().strftime("%H:%M:%S")
        """Print data to tk frame

        Args:
            data (_data_): Data to print 
            frame (_tk frame_): Frame to print on
            text (_str_): Text before data
        """
        frame.insert(tk.END, f"[{self.current_time}] {text}\n   {data}\n")
        frame.see(tk.END)
        
    def print_cmd_ack(self):
        self.current_time = datetime.now().strftime("%H:%M:%S")
        self.mavlink_text.insert(tk.END, f"[{self.current_time}]\n   {self.MyCopter.command_acknowledge()}\n")
        self.mavlink_text.see(tk.END)