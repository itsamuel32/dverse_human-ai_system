import flet as ft
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

    input_field = ft.TextField(
        width=500,
        hint_text="Recognized text will appear here...",
        autofocus=False,
        multiline=True,
        min_lines=2
    )

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

    # Define mic_button at main scope so it's accessible inside async
    mic_button = ft.ElevatedButton(
        content=ft.Icon(ft.Icons.MIC, size=50),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=400),
            padding=40,
            bgcolor=ft.Colors.BLUE_400
        ),
        on_click=recognize_speech_async
    )

    def on_send_click(e):
        print(f"Sending text: {input_field.value}")
        page.snack_bar = ft.SnackBar(ft.Text(f"Sent: {input_field.value}"))
        page.snack_bar.open = True
        page.update()

    send_button = ft.IconButton(
        icon=ft.Icons.SEND,
        on_click=on_send_click
    )

    def on_clear_click(e):
        input_field.value = ""
        page.update()

    clear_button = ft.IconButton(
        icon=ft.Icons.CLEAR,
        on_click=on_clear_click
    )

    page.add(
        mic_button,
        ft.Row(
            [input_field, send_button,clear_button],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )


ft.app(target=main)
