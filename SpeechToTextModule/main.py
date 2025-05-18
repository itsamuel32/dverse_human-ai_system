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


def main(page: ft.Page):
    page.title = "Voice Recognition Module"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # ---------------- PROMPT INPUT FIELD ---------------- #

    input_field = ft.TextField(
        hint_text="Recognized text will appear here...",
        autofocus=False,
        multiline=True,
        min_lines=2
    )
    # ---------------- LLM RESPONSE TEXTFIELD ---------------- #

    llm_response_field = ft.TextField(
        hint_text="LLM Response will appear here...",
        read_only=True,
        multiline=True,
        min_lines=30,
        expand=True
    )

    # ---------------- EXEC TIMER ---------------- #
    exec_time_text = ft.Text("", size=14, italic=True, color=ft.Colors.GREY)

    # ---------------- LOADING SPINNER ---------------- #

    loading_spinner = ft.Row(
        controls=[
            ft.ProgressRing(),
            ft.Text("Loading...", size=16)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        visible=False
    )

    async def recognize_speech_async(e):
        mic_button.style.bgcolor = ft.Colors.WHITE
        page.update()

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, recognize_speech_blocking)

        input_field.value = result
        mic_button.style.bgcolor = ft.Colors.BLUE_400
        page.update()

    # ---------------- MIC BUTTON ---------------- #

    mic_button = ft.ElevatedButton(
        content=ft.Icon(ft.Icons.MIC, size=100),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=300),
            padding=80,
            bgcolor=ft.Colors.BLUE_400
        ),
        on_click=recognize_speech_async
    )

    async def on_send_click(e):
        user_input = input_field.value
        print(f"Sending text: {user_input}")
        exec_time_text.value = ""
        llm_response_field.value = ""
        loading_spinner.visible = True
        page.update()

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(600.0)) as client:
                response = await client.post("http://localhost:8008/ask", params={"prompt": user_input})

            if response.status_code == 200:
                data = response.json()

                if isinstance(data, list) and len(data) == 2:
                    messages, exec_time = data
                    llm_response_field.value = json.dumps(messages, indent=2, ensure_ascii=False)
                    exec_time_text.value = f"Execution time: {exec_time:.2f} seconds"
                else:
                    llm_response_field.value = json.dumps(data, indent=2, ensure_ascii=False)

            else:
                llm_response_field.value = f"Error {response.status_code}: {response.text}"

        except Exception as ex:
            llm_response_field.value = f"Request failed: {ex}"

        loading_spinner.visible = False
        page.update()

    mic_button_container = ft.Container(
        content=mic_button,
        margin=ft.Margin(0, 0, 0, 50)  # top, right, bottom, left
    )

    # ---------------- PROMPT CONTROL BUTTONS ---------------- #

    send_button = ft.IconButton(icon=ft.Icons.SEND, on_click=on_send_click, icon_size=50)
    clear_button = ft.IconButton(icon=ft.Icons.CLEAR,
                                 on_click=lambda e: (setattr(input_field, "value", ""), page.update()), icon_size=50)

    # ---------------- LEFT SCREEN PANEL ---------------- #

    left_panel = ft.Container(
        content=ft.Column(
            [
                mic_button_container,
                ft.Column([
                    input_field,
                    ft.Row([send_button, clear_button], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=10)
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        ),
        alignment=ft.alignment.center,
        expand=1
    )

    # ---------------- RIGHT SCREEN PANEL ---------------- #

    right_panel = ft.Column(
        [
            ft.Text("LLM Response", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,
                    color=ft.Colors.BLUE_400),
            exec_time_text,
            loading_spinner,
            llm_response_field
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        expand=True
    )

    # ---------------- MAIN LAYOUT ---------------- #

    page.add(
        ft.Row([left_panel, right_panel], expand=True, vertical_alignment=ft.CrossAxisAlignment.STRETCH)
    )


ft.app(target=main, view=ft.WEB_BROWSER, port=3000, assets_dir="assets")
