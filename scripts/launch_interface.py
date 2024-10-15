import gradio as gr

def dummy_response_function(_):
    return "Hello World!"

chat_interface = gr.ChatInterface(fn=dummy_response_function, type="messages")

if __name__ == "__main__":
    chat_interface.launch()
