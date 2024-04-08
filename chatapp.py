import flet as ft
from datetime import datetime
import firebase_admin
from firebase_admin import firestore,credentials
import uuid
user_id = str(uuid.uuid4())
from flet import Column, Text, ElevatedButton, FilePicker,FilePickerResultEvent,Page,Row,Text,icons
import cv2
import time
import os
import base64



cred =  credentials.Certificate("service_account.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

class Message():
    def __init__(self, user_name: str, text: str, message_type: str, timestamp: datetime = None):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type
        self.timestamp = timestamp if timestamp else datetime.now()
        
        
        
class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__(alignment="start")
        avatar = ft.CircleAvatar(
            content=ft.Text(self.get_initials(message.user_name)),
            color=ft.colors.WHITE,
            bgcolor=self.get_avatar_color(message.user_name),
        )
        user_info = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(message.user_name, weight="bold"),
                        ft.Text(f" {message.timestamp.strftime('%H:%M')}", color=ft.colors.GREY, size=12),
                    ],
                    alignment="start",
                ),
                ft.Text(message.text, selectable=True),
            ],
            tight=True,
            spacing=5,
        )
        self.controls = [avatar, user_info]

    def get_initials(self, user_name: str):
        return user_name[:1].capitalize() if user_name else "U"

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER, ft.colors.BLUE, ft.colors.BROWN, ft.colors.CYAN,
            ft.colors.GREEN, ft.colors.INDIGO, ft.colors.LIME, ft.colors.ORANGE,
            ft.colors.PINK, ft.colors.PURPLE, ft.colors.RED, ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


emojis = {
    ":grin:": "\U0001F603",
    ":wink:": "\U0001F609",
    ":kiss:": "\U0001F617",
    ":heart eyes": "\U0001F60D",
    ":cry:": "\U0001F622",
    ":angry:": "\U0001F620",
    ":joy:": "\U0001F602",
    ":clap:": "\U0001F44F",
    ":rolling_eyes:": "\U0001F644",
    ":stuck_out_tongue_winking_eye:": "\U0001F61C",
    ":grin:": "\U0001F603",
    ":wink:": "\U0001F609",
    ":kiss:": "\U0001F617",
    ":heart_eyes:": "\U0001F60D",
    ":cry:": "\U0001F622",
    ":angry:": "\U0001F620",
    ":joy:": "\U0001F602",
    ":clap:": "\U0001F44F",
    ":rolling_eyes:": "\U0001F644",
    ":stuck_out_tongue_winking_eye:": "\U0001F61C",
    ":thumbs_up:": "\U0001F44D",
    ":thumbs_down:": "\U0001F44E",
    ":thinking_face:": "\U0001F914",
    ":fire:": "\U0001F525",
    ":ok_hand:": "\U0001F44C",
    ":heart:": "\U00002764",
    ":rocket:": "\U0001F680",
    ":star:": "\U00002B50",
    ":sparkles:": "\U00002728",
    ":sunglasses:": "\U0001F60E",
    ":smirk:": "\U0001F60F",
    ":nerd_face:": "\U0001F913",
    ":laughing:": "\U0001F606",
    ":sob:": "\U0001F62D",
    ":sleeping:": "\U0001F634",
    ":confused:": "\U0001F615",
    ":heart_eyes_cat:": "\U0001F63B",
    ":dog:": "\U0001F415",
    ":cat:": "\U0001F431",
    ":panda_face:": "\U0001F43C",
    ":unicorn:": "\U0001F984",
    ":pizza:": "\U0001F355",
    ":taco:": "\U0001F32E",
    ":hamburger:": "\U0001F354",
    ":icecream:": "\U0001F368",
    ":doughnut:": "\U0001F369",
    ":cake:": "\U0001F370",
    ":cookie:": "\U0001F36A",
    ":coffee:": "\U00002615",
    ":tea:": "\U0001F375",
    ":beer:": "\U0001F37A",
    ":wine_glass:": "\U0001F377",
    ":cocktail:": "\U0001F378",
    ":tropical_drink:": "\U0001F379",
    ":baby:": "\U0001F476",
    ":girl:": "\U0001F467",
    ":boy:": "\U0001F466",
    ":man:": "\U0001F468",
    ":woman:": "\U0001F469",
    ":older_man:": "\U0001F474",
    ":older_woman:": "\U0001F475",
    ":baby_angel:": "\U0001F47C",
    ":alien:": "\U0001F47D",
    ":ghost:": "\U0001F47B",
    ":skull:": "\U0001F480",
    ":santa:": "\U0001F385",
    ":mummy:": "\U0001F9DF",
    ":zombie:": "\U0001F9DF\u200D\u2642\uFE0F",
    ":clown_face:": "\U0001F921",
    ":robot:": "\U0001F916",
    ":superhero:": "\U0001F9B8",
    ":prince:": "\U0001F934",
    ":princess:": "\U0001F478",
    ":detective:": "\U0001F575",
    ":police_officer:": "\U0001F46E",
    ":firefighter:": "\U0001F692",
    ":scientist:": "\U0001F468\u200D\U0001F52C",
    ":teacher:": "\U0001F468\u200D\U0001F3EB",
    ":farmer:": "\U0001F468\u200D\U0001F33E",
    ":cook:": "\U0001F468\u200D\U0001F373",
}

def insert_emoji(page, new_message, emoji_code):
    # Insert the selected emoji into the text field
    new_message.value += emoji_code
    page.update()

def show_emoji_picker(page, new_message):
    def on_emoji_click(e, emoji_code):
        insert_emoji(page, new_message, emoji_code)
        if hasattr(page, "emoji_picker"):
            page.controls.remove(page.emoji_picker)
            page.update()


    rows = []
    row = []
    for _, emoji_code in emojis.items():
        
        button = ft.TextButton(text=emoji_code, on_click=lambda e, em=emoji_code: on_emoji_click(e, em))
        row.append(button)
        if len(row) == 5:
            rows.append(ft.Row(controls=row))
            row = []
    if row:  
        rows.append(ft.Row(controls=row))

    emoji_grid = ft.Column(controls=rows, spacing=10)

    if not hasattr(page, "emoji_picker"):
        page.emoji_picker = ft.Container(content=emoji_grid, width=300, height=200, bgcolor=ft.colors.BLACK, border_radius=10)
    else:
        page.emoji_picker.content = emoji_grid

    if page.emoji_picker not in page.controls:
        page.add(page.emoji_picker)
    else:
        page.controls.remove(page.emoji_picker)
    page.update()




def main(page: ft.Page):
    chat = ft.ListView()  # Initialize your chat UI component
    active_users = ft.ListView() 
    page.update()
    page.horizontal_alignment = "stretch"
    page.title = "Flet Chat Enhanced"
    
    page.add(chat)
    
    
    

    new_message = ft.TextField(hint_text="Write a message...", autofocus=True)

    
    emoji_button = ft.TextButton(text="😊", on_click=lambda e: show_emoji_picker(page, new_message), tooltip="Emoji")

    camera_button= ft.ElevatedButton(text="📷", bgcolor="blue", on_click=lambda e: takemepicture(e)),
    

    # Add emoji_button and new_message to the page
    
    def open_emoji_picker(e):
        show_emoji_picker(page, new_message)


    image_holder= ft.Image(visible=False,fit=ft.ImageFit.CONTAIN)



    



    def handle_loaded_file(e: ft.FilePickerResultEvent):
        if e.files:
            print(f"Selected files: {[file.name for file in e.files]}")


            upload_url = "YOUR_SERVER_UPLOAD_ENDPOINT"
            upload_files = [
                ft.FilePickerUploadFile(name=file.name, upload_url=upload_url)
                for file in e.files
            ]
            file_picker.upload(upload_files)

            for file in e.files:
                print(f"Preparing {file.name} for upload...")

        if e.files and len(e.files):
        
            file_content = e.files[0].content  
        
        # If you want to display the image directly without saving, convert to base64
        if file_content:
            image_base64 = base64.b64encode(file_content).decode('utf-8')
            image_holder.src_base64 = image_base64
            image_holder.visible = True
            page.update()
        else:
            print("No content available in the selected file.")


    file_picker= ft.FilePicker(on_result=handle_loaded_file)
    page.overlay.append(file_picker)



    def select_files_action(e):
        file_picker.pick_files()



    myimage = ft.Image(
        src= False,
        width= 1,
        height= 1,
        fit="cover"

    )

    def removeallyouphoto():
        folder_path="Photosholder/"
        files = os.listdir(folder_path)
        #check all files in youphoto folder
        for file in files:
            file_path= os.path.join(folder_path,file)
            #and if found then remove
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"you file success remove {file_path}")

        page.update()




    def takemepicture(e):
        removeallyouphoto()  
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return  

        cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Webcam", 400, 600)

        timestamp = str(int(time.time()))
        myfileface = "mycamfacefile_" + timestamp + ".jpg"
    
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Failed to capture image from webcam")
                break  # Exit loop if frame is invalid
        
            cv2.imshow("Webcam", frame)
            key = cv2.waitKey(1) & 0xFF  # Correct way to wait for a key press

            if key == ord("q"):
                break
            elif key == ord("s"):
                cv2.imwrite(f"Photosholder/{myfileface}", frame)
                cv2.putText(frame, "Picture Captured!!!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow("Webcam", frame)
                cv2.waitKey(3000)
                myimage.src = f"Photosholder/{myfileface}"  
                break

        cap.release()
        cv2.destroyAllWindows()

   
    def process_message(message):
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.colors.RED, size=12)
            active_users.controls.append(ft.Text(message.user_name))  # Update active users list
        chat.controls.append(m)
        page.update()

    page.pubsub.subscribe(lambda message: process_message(message))

    def join_chat_click(e):
        user_name = join_user_name.value.strip()
        if not user_name:
            join_user_name.error_text = "Name cannot be blank!"
            join_user_name.update()
        else:
            page.session.set("user_name", user_name)
            page.dialog.open = False
            new_message.prefix = ft.Text(f"{user_name}: ")
            page.pubsub.send_all(Message(user_name=user_name, text=f"{user_name} has joined the chat.", message_type="login_message"))
            page.update()

    def send_message_click(e):
        user_name = page.session.get("user_name")
        if new_message.value:
        # Firestore document structure
            message_doc = {
                "user_name": user_name,
                "text": new_message.value,
                "timestamp": datetime.now()  
        }
        
            db.collection("messages").add(message_doc)

        
        page.pubsub.send_all(Message(user_name=user_name, text=new_message.value, message_type="chat_message"))
        new_message.value = ""
        new_message.focus()
        page.update()
        
    def subscribe_to_pubsub(message, page, chat, active_users):
        process_message(message, page, chat, active_users)

    page.pubsub.subscribe(lambda message: subscribe_to_pubsub(message, page, chat, active_users))

    def process_message(message, page, chat, active_users):
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.colors.RED, size=12)
            active_users.controls.append(ft.Text(message.user_name))  # Update active users list
        chat.controls.append(m)
        page.update()


    
    join_user_name = ft.TextField(
        label="Enter your name to join the chat",
        autofocus=True,
        on_submit=join_chat_click,
    )
    page.dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Welcome!"),
        content=ft.Column([join_user_name], width=300, height=70, tight=True),
        actions=[ft.ElevatedButton(text="Join chat", on_click=join_chat_click)],
        actions_alignment="end",
    )

   

    
    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )


    emoji_button = ft.IconButton(icon=ft.icons.INSERT_EMOTICON, on_click=open_emoji_picker, tooltip="Emoji")
    camera_button = ft.IconButton(icon=ft.icons.PHOTO_CAMERA, on_click=takemepicture, tooltip="Take a picture")
    select_files_button = ft.IconButton(icon=ft.icons.FOLDER_OPEN, on_click=select_files_action,tooltip="Select Files",)


    
    page.add(image_holder)
    page.add(
    ft.Column([
        ft.Text("FLET CHAT APPLICATION", size=30, weight="bold"),
          
        
        myimage
          
    ]),
    ft.Container(
        content=ft.Row([
            ft.Container(
                content=chat,  
                border=ft.border.all(1, ft.colors.GREEN),
                border_radius=5,
                padding=10,
                expand=True,
            ),
            ft.Container(
                content=active_users,  
                border=ft.border.all(1, ft.colors.GREEN),
                border_radius=5,
                padding=10,
                width=200,
            ),
        ]),
        expand=True,
    ),
    ft.Row([
        emoji_button,  
        camera_button,  
        new_message,
        select_files_button,
        ft.IconButton(
            icon=ft.icons.SEND_ROUNDED,
            tooltip="Send message",
            on_click=lambda e: send_message_click(new_message)  
        ),
    ]),
)

if __name__ == "__main__":
    ft.app(port=8550, target=main, view=ft.WEB_BROWSER)