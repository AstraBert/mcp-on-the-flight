"""Main app script."""

from utils import assistant_index
import websockets
import gradio as gr


async def websocket_chat(prompt):
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(prompt)
            full_response = ""

            while True:
                message = await websocket.recv()
                if message == "[END]":
                    break
                full_response += message
                yield full_response
            yield full_response

    except Exception as e:
        yield f"Error: {e}"


def chat(message, history):
    return assistant_index(message)


def launch_interface():
    with gr.Blocks(
        theme=gr.themes.Citrus(primary_hue="indigo", secondary_hue="teal")
    ) as frontend:
        gr.HTML("<h1 align='center'>Flight Ticket Information</h1>")
        gr.HTML("<h2 align='center'>Get all the info from your flight ticket!</h2>")
        with gr.Row():
            usr_txt = gr.File(
                label="Upload your plane ticket",
                file_count="single",
                file_types=[".pdf", ".PDF"],
            )
            with gr.Column():
                resp = gr.Markdown(
                    label="Agent Output",
                    container=True,
                    show_label=True,
                    show_copy_button=True,
                )

        with gr.Row():
            gr.Button("Submit!").click(
                fn=websocket_chat, inputs=[usr_txt], outputs=[resp]
            )

    chatif = gr.ChatInterface(
        fn=chat,
        title="Chat with the QA Assistant",
        theme=gr.themes.Citrus(primary_hue="indigo", secondary_hue="teal"),
    )

    iface = gr.TabbedInterface(
        interface_list=[frontend, chatif],
        tab_names=["Get Ticket Info🎫", "Chat With Assistant🤖"],
    )
    iface.launch()


if __name__ == "__main__":
    launch_interface()
