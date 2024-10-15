import logging
import json
import gradio as gr

from langchain_openai import ChatOpenAI

from booking_agent.booking_agent import BookingAgent
from booking_agent.calendar import Calendar
from booking_agent.calendar_toolkit import CalendarToolkit

logging.basicConfig(level=logging.INFO)

def generate_calendar_html(calendar_dict):
    html = "<div class='calendar'>"
    for date, slots in calendar_dict.items():
        html += f"<div class='date'>{date}</div>"
        for slot in slots:
            color = "green" if slot["available"] else "red"
            html += f"<div class='slot' style='color: {color};'>{slot['start']} - {slot['end']}</div>"
        html += "<hr>"
    html += "</div>"
    return html

def main():
    CSS = """#row1 {flex-grow: 1; align-items: unset;}
        .form {height: fit-content;}"""

    with open("data/calendar.json", "r") as f:
        calendar_dict = json.load(f)

    model = ChatOpenAI()
    agent = BookingAgent(model, CalendarToolkit(Calendar(**calendar_dict)))

    with gr.Blocks(fill_height=True, css=CSS) as demo:
        with gr.Row(elem_id="row1"):
            with gr.Column(scale=15):
                gr.ChatInterface(lambda m, _: agent.invoke(m),
                                 type="messages")
            with gr.Column():
                gr.HTML(generate_calendar_html(calendar_dict))
    demo.launch()


if __name__ == "__main__":
    main()
