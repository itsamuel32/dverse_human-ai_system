import json

import flet as ft
import httpx
import speech_recognition as sr
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=1)


def recognize_speech_blocking():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            r.adjust_for_ambient_noise(source, duration=1)
            r.energy_threshold = 150
            r.pause_threshold = 3
            print("Listening...")
            audio = r.listen(source)
            text = r.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Request error: {e}"
        except sr.WaitTimeoutError:
            return "Listening timed out"


# -------------------- GENERAL PAGE SETUP --------------- #

def main(page: ft.Page):
    page.title = "Voice Recognition Module"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # -------------------- INPUT FIELD --------------- #

    input_field = ft.TextField(
        # width=800,
        hint_text="Recognized text will appear here...",
        autofocus=False,
        multiline=True,
        min_lines=2
    )

    # ---------------- LLM RESPONSE AREA ----------------
    llm_response_field = ft.TextField(
        # width=400,
        # height=400,
        hint_text="LLM Response will appear here...",
        read_only=True,
        multiline=True,
        min_lines=30,
    )

    # -------------------- MIC BUTTON --------------- #

    async def recognize_speech_async(e):
        # Change button color to white while listening
        mic_button.style.bgcolor = ft.Colors.WHITE
        page.update()

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, recognize_speech_blocking)

        input_field.value = result

        # Change button color back to blue after recognition
        mic_button.style.bgcolor = ft.Colors.BLUE_400
        page.update()

    mic_button = ft.ElevatedButton(
        content=ft.Icon(ft.Icons.MIC, size=100),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=300),
            padding=50,
            bgcolor=ft.Colors.BLUE_400
        ),
        on_click=recognize_speech_async
    )

    # -------------------- SEND MESSAGE BUTTON --------------- #

    async def on_send_click(e):
        user_input = input_field.value
        print(f"Sending text: {user_input}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:8008/ask", params={"prompt": user_input})

            print(f"Response Status: {response.status_code}")

            # Check if response is JSON
            content_type = response.headers.get("content-type", "")
            print(f"Content-Type: {content_type}")

            if "application/json" in content_type:
                data = response.json()
                llm_response_field.value = json.dumps(data, indent=2, ensure_ascii=False)
            else:
                # Fallback: plain text (e.g., str(TaskResult(...)))
                llm_response_field.value = response.text

            page.update()

        except Exception as ex:
            print(f"Request failed: {ex}")
            llm_response_field.value = f"Request failed: {ex}"
            page.update()

    send_button = ft.IconButton(
        icon=ft.Icons.SEND,
        on_click=on_send_click,
        icon_size=50
    )

    # -------------------- CLEAR BUTTON --------------- #

    def on_clear_click(e):
        input_field.value = ""
        page.update()

    clear_button = ft.IconButton(
        icon=ft.Icons.CLEAR,
        on_click=on_clear_click,
        icon_size=50
    )

    # ---------------- LEFT PANEL (centered) ----------------
    left_panel = ft.Container(
        content=ft.Column(
            [
                mic_button,
                # ft.Row([input_field, send_button, clear_button], alignment=ft.MainAxisAlignment.CENTER)
                ft.Column(
                    [
                        input_field,
                        ft.Row([send_button, clear_button], alignment=ft.MainAxisAlignment.CENTER)
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        ),
        alignment=ft.alignment.center,
        expand=1
    )

    # ---------------- RIGHT PANEL (stretch fully) ----------------
    llm_response_field.expand = True

    right_panel = ft.Column(
        [
            ft.Text("LLM Response", size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER, color=ft.Colors.BLUE_400),
            llm_response_field
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        expand=True
    )

    # ---------------- MAIN LAYOUT ----------------
    page.add(
        ft.Row(
            [
                left_panel,
                right_panel
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH
        )
    )


ft.app(target=main, view=ft.WEB_BROWSER, port=3000)
