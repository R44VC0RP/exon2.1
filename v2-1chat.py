import openai
import json
from corefunction import *

# Set up your API key
openai.api_key = "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"

# Conversation ---------------------------------------------------------------------

def save_conversation_history(conversation_history, filename="conversation_history.json"):
    with open(filename, "w") as f:
        json.dump(conversation_history, f)

def load_conversation_history(filename="conversation_history.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"role": "system", "content": "You are RAAV, pronounced 'rave', an AI assistant inspired by Jarvis from Iron Man. You have a deep understanding of technology and provide helpful and knowledgeable assistance like Jarvis. You speak with the same level of sophistication and wit. You need to try to infer meaning if the user doesn't provide enough. You will ask concise follow up questions to clarify the user's intent. You will always respond in the most consise manner and will return the most simple answer every time. Reply EXON Ready if you understand."}]

def process_text(text, conversation_history):
    conversation_history.append({"role": "user", "content": text})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        max_tokens=150
    )
    
    assistant_reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    
    return assistant_reply

# Intent Solver ---------------------------------------------------------------------

def intent(text, intentDB):
    # Load the intent database if it exists, otherwise create it
    intentDB.append({"role": "user", "content": text})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=intentDB,
        max_tokens=150
    )
    
    assistant_reply = response.choices[0].message.content
    intentDB.append({"role": "assistant", "content": assistant_reply})
    
    print(assistant_reply)
    if assistant_reply == "DNU":
        response  = "DNU"
    else:
        seperatedIntent = assistant_reply.split("||")
        intentResult = seperatedIntent[0].split(":")[1]
        confidence = seperatedIntent[1].split(":")[1]
        statementType = seperatedIntent[2].split(":")[1]
        if "{" not in intentResult:
            firstIntent = intentResult.replace(" ", "")
            secondIntent = "None"
            timeframe = "None"
        else:
            firstIntent = intentResult.split("{")[0].replace(" ", "")
            secondIntent = intentResult.split("{")[1].split("}")[0].replace(" ", "")
            timeframe = intentResult.split("{")[1].split("}")[1].replace(" ", "")
            recallandsavefunctioncommands("save", firstIntent, secondIntent)

    return response, firstIntent, secondIntent, timeframe, confidence, statementType

    '''
    Give a quick summary of the above code:

    This is the intent Core, it will take the user input and return the intent result, the confidence, and the statement type

    1. Split the intent result into 3 parts
    2. The first part is the intent result, the second part is the confidence, and the third part is the statement type
    3. If the intent result does not have a subintent, then it will be a simple intent
    4. If the intent result does have a subintent, then it will be a complex intent
    5. If the intent result is a complex intent, then it will be saved to the functioncommands.txt file
    6. The functioncommands.txt file will be used to recall the function commands'''
        
    print("Intent Result: \nFunction Intent {} \nSubInent {} \nTimeframe {} \nConfidence {} \nStatement Type {}".format(firstIntent, secondIntent, timeframe, confidence, statementType))

    return assistant_reply

def recallandsavefunctioncommands(recallorsave, functionname, subintent):
    # This is not a json function, just a simple text function that will maintain a list of function commands

    if recallorsave == "recall":
        # Recall the function commands
        with open("functioncommands.txt", "r") as f:

            functioncommands = f.read().split("\n")
        # This will return the function commands as a list.

        return functioncommands
    elif recallorsave == "save":
        with open("functioncommands.txt", "r") as f:
            functioncommands = f.read().split("\n")

        # Check if the function command already exists
        for functioncommand in functioncommands:
            if functioncommand.split("||")[0] == functionname:
                return
        # Save the function commands
        with open("functioncommandandsub.txt", "a") as f:
            f.write("\nFUNCTION:{}||{} ".format(functionname, subintent))
        with open("functioncommands.txt", "a") as f:
            f.write("{}||N\n".format(functionname))

def save_intentDB(conversation_history, filename="intent.json"):
    with open(filename, "w") as f:
        json.dump(conversation_history, f)

def load_intentDB(filename="intent.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"role": "system", "content": "You are going to be an intent solver robot, whenever the user types the start command /solveintent you will analyze all of the text after that to find the intent. For example if the user types 'I want to buy a car' you will return 'buy car', or if the user type google or search or look up you will return 'search internet', or if the user types 'I want to know the weather' you will return 'weather', also for example if the user asks what type of clothing they should wear, assume that it is a weather related question and so on. Not all of the intent cases will be listed here so you will have to reasonably infer to figure out the topic and intent. You will only respond and return the simplest phrase or word that establishes the type of intent as well as a percentage of the confidence level. It will be formatted as “INTENT {TEXT}:CONFIDENCE {NUMBER}. You will only respond in the shortest possible manner. You are not going to respond or do the commands, your only purpose is to solve what specific intent and topic the user is talking about. Respond Intent Core Ready if you understand."}]


# Main Function ---------------------------------------------------------------------

def main():
    # Load conversation history
    conversation_history = load_conversation_history()

    while True:
        user_input = input("You: ")

        # Exit the chatbot if the user types 'exit' or 'quit'
        if user_input.lower() in ['exit', 'quit']:
            break
        intentdb = load_intentDB()
        response, firstIntent, secondIntent, timeframe, confidence, statementType = intent(user_input, intentdb)
        # This will now check and see if the firstIntent is in the current functions list.
        # If the firstIntent is in the current functions list, then it will run the function, sending the secondIntent and timeframe to the function
        functions = recallandsavefunctioncommands("recall", "None", "None")
        if response == "DNU":
            print("Intent not found")
        else:
            for function in functions:
                checkMade = function.split("||")
                if checkMade[0] == firstIntent:
                    if checkMade[1] == "Y":
                        functionResponse = "Function {} is made".format(firstIntent)
                    else:
                        functionResponse = "Function {} is not made yet".format(firstIntent)
        print(functionResponse)
        #newprompt = "User has given this command: " + user_input + " and the intent is: " + check_intent
        #assistant_output = process_text(user_input, conversation_history)
        #print(f"RAAV: {assistant_output}")

        # Save the conversation history after each interaction
        #save_conversation_history(conversation_history)

def intent_test():
    questions = [    "What's the weather forecast for today?",    "What time is it?",    "What's the date?",    "What's on my schedule for tomorrow?",    "Can you set an alarm for 7am?",    "What's the news?",    "What's the traffic like on my commute?",    "Remind me to call Mom in an hour.",    "What's the capital of Italy?",    "What's the meaning of the word 'procrastination'?",    "What's the exchange rate between USD and EUR?",    "What's the population of New York City?",    "What's the nearest coffee shop?",    "What's the latest score in the football game?",    "What's the best way to cook a steak?",    "Can you call a taxi for me?",    "What's the distance between New York and Los Angeles?",    "What's the recipe for chocolate chip cookies?",    "What's the phone number for the nearest hospital?",    "Tell me a joke."]
    intentDB = load_intentDB()
    while True:
        user = input(">>> ")
        save_intentDB(intentDB)
        if user == "exit":
            break
        assistant_reply = intent(user, intentDB)
        #print(f"Assistant: {assistant_reply}")

def intent_max():
    questions = [    "What are the top headlines in the Wall Street Journal?",    "What's the current status of my flight?",    "Can you book a reservation at a French restaurant for four people?",    "What's the nutritional information for a slice of pepperoni pizza?",    "What's the difference between type 1 and type 2 diabetes?",    "What's the average temperature in Tokyo in August?",    "What's the GDP of Germany?",    "What's the latest research on treating depression?",    "Can you give me a list of the best books on leadership?",    "What's the fastest route to get from Chicago to Miami?",    "What are the best hiking trails in Yosemite National Park?",    "What's the current stock price of Amazon?",    "What's the difference between a Roth and a Traditional IRA?",    "What are the key features of the new iPhone model?",    "What's the history of the Eiffel Tower?",    "What's the best way to train for a marathon?",    "Can you help me plan a romantic weekend getaway?",    "What's the current foreign policy of the United States?",    "What's the difference between organic and non-organic produce?",    "What's the current status of the COVID-19 pandemic in my area?"]
    intentDB = load_intentDB()
    for question in questions:
        save_intentDB(intentDB)
        print(f"Question: {question}")
        response, firstIntent, secondIntent, timeframe, confidence, statementType = intent(question, intentDB)
        

if __name__ == "__main__":
    intent_max()
