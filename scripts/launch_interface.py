import json
import gradio as gr


def generate_calendar_html(data):
    html = "<div class='calendar'>"
    for date, slots in data.items():
        html += f"<div class='date'>{date}</div>"
        for slot in slots:
            color = "green" if slot["available"] else "red"
            html += f"<div class='slot' style='color: {color};'>{slot['start']} - {slot['end']}</div>"
        html += "<hr>"
    html += "</div>"
    return html

def update_calendar():
    with open("data/calendar.json", "r") as f:
        data = json.load(f)
    return generate_calendar_html(data)


def dummy_response_function(msg, history):
    return "Hello World!"

chat_interface = gr.ChatInterface(fn=dummy_response_function, type="messages")

def main():

    CSS = """#row1 {flex-grow: 1; align-items: unset;}
        .form {height: fit-content;}"""

    with gr.Blocks(fill_height=True, css=CSS) as demo:
        with gr.Row(elem_id="row1"):
            with gr.Column(scale=15):
                gr.ChatInterface(dummy_response_function, type="messages")
            with gr.Column():
                calendar = gr.HTML()

        demo.load(update_calendar, outputs=[calendar])
    demo.launch()


if __name__ == "__main__":
    main()
