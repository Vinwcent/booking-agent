import logging
import json
import gradio as gr

from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

from booking_agent.booking_agent import BookingAgent
from booking_agent.calendar import Calendar
from booking_agent.calendar_toolkit import CalendarToolkit

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("booking-agent")
logger.setLevel(logging.DEBUG)

def generate_calendar_html(calendar_dict):
    """
    Ugly function to generate the gradio html

    :param calendar_dict dict: The calendar used to create the html
    """
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
    """
    Launch a gradio interface that displays a chat interface with a booking
    agent in it and its associated calendar on the left.
    """
    CSS = """#row1 {flex-grow: 1; align-items: unset;}
        .form {height: fit-content;}
        #interface {height: 800px;}"""

    with open("data/calendar.json", "r") as f:
        calendar_dict = json.load(f)

    model = ChatOpenAI()
    vectorstore = FAISS.load_local("data/policy_index",
                                   embeddings=OpenAIEmbeddings(),
                                   allow_dangerous_deserialization=True)
    agent = BookingAgent(model, CalendarToolkit(Calendar(**calendar_dict)), vectorstore)



    with gr.Blocks(fill_height=True, css=CSS) as demo:
        with gr.Row(elem_id="row1"):
            with gr.Column():
                gr.HTML(lambda:generate_calendar_html(agent.get_calendar_json()), every=2)
            with gr.Column(scale=15, elem_id="interface"):
                def invoke_and_update_calendar(m: str):
                    result = agent.invoke(m)
                    return result
                interface = gr.ChatInterface(lambda m, _: invoke_and_update_calendar(m),
                             type="messages")

                def reset():
                    logger.debug("Memory and calendar reset")
                    agent.reset_agent_and_calendar(CalendarToolkit(Calendar(**calendar_dict)))

                button = gr.ClearButton(interface.chatbot, value="Reset memory and calendar")
                button.click(reset, [], [])
    demo.launch()


if __name__ == "__main__":
    main()
