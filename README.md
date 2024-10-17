# ℹ️🔗 Booking agent 🔗ℹ️

This repository illustrates a proof of concept of an AI Agent which goal is to help users to book appointments in a calendar while following specific booking policies.

## Representation
The calendar is a JSON file

The booking policies are represented as a vector database

## Quick installation

### With poetry
You simply have to install the project,
```bash
poetry install
```

### Manually
1. Create a python `3.11` environment and activate it
2. Install requirements,
```bash
pip install -r requirements.txt
```
3. Install the package (to work with the way poetry reference path)
```bash
pip install -e . # at the root of the project
```

## Usage

First, set your OpenAI api key as an environment variable (you can also use your own llm with minimal modifications, cf. below)

```
export OPENAI_API_KEY=... # In shell or bashrc
```

### Launch the interface

There is gradio interface that makes it easy to see the capabilities of the agent, run this script to launch the web server hosting it,
```bash
python scripts/launch_interface.py
```

### Interface layout

On the left, you have the calendar that is managed by the agent.
You can interact with it through the ChatInterface to make him give you 
informations about the calendar or to issue appointments reservation.

## Use your own data

### Calendar
You can modify the calendar used by changing the `data/calendar.json` file.

### Booking policies
If you want to change the policies followed by the agent, write a file with one
policy per line and run `scripts/create_db.py` on it.

```
python scripts/create_db.py my_awesome_booking_policies.txt
```

### LLM used

The whole project is based on Langchain which means you can easily change the LLM you use by using the abstractions Langchain provides.

To do so, simply create a Langchain `BaseChatModel` object (either with an open source model or another closed source one) and modify the instantiation of `BookingAgent` with it (in the `scripts/launch_interface.py` file for example) and you're done !
