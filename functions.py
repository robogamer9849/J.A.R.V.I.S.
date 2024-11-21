from pathlib import Path
import os
import ollama
from config import *

# chat history stuff
def save_history(USERmessage,AImessage):
    lastAnswer  = "last-answer.txt"
    file_name = "history.txt"
    with open(Path(__file__).parent.resolve()/file_name, 'a') as file:
        file.write("\n[user]: " + f'[{USERmessage}]' + "\n[AI]: " + f'[{AImessage}]')
        file.close()
    with open(Path(__file__).parent.resolve()/lastAnswer, 'w') as file:
        file.write(f"user:  {USERmessage}\nAI: {AImessage}")
        file.close()

def save_command_history(USERmessage,command,AImessage):
    lastAnswer  = "last-answer.txt"
    file_name = "history.txt"
    with open(Path(__file__).parent.resolve()/file_name, 'a') as file:
        file.write("\n\n\n\n[user]: " + f'[{USERmessage}]' + "\n[AI]: " + f'[{AImessage}]' + '\n[command ran]:' + f'[{command}]\n')
        file.close()
    with open(Path(__file__).parent.resolve()/lastAnswer, 'w') as file:
        file.write(f"user:  {USERmessage}\nAI: {AImessage}")
        file.close()

def show_history_to_AI():
    file_name = f"history.txt"
    if os.path.exists(Path(__file__).parent.resolve()/file_name):
        with open(Path(__file__).parent.resolve()/file_name, 'r') as file:
            history = file.read()
            file.close()
    else:
        history = "no History!"
    return history
def clear_history():
    lastAnswer  = "last-answer.txt"
    file_name = "history.txt"
    if os.path.exists(Path(__file__).parent.resolve()/lastAnswer):
        os.remove(Path(__file__).parent.resolve()/lastAnswer)
    if os.path.exists(Path(__file__).parent.resolve()/file_name):
        os.remove(Path(__file__).parent.resolve()/file_name)
    if os.path.exists(Path(__file__).parent.resolve()/'commands.txt'):
        os.remove(Path(__file__).parent.resolve()/'commands.txt')
        answer = "I forgot our chat history!"
    else:
        answer = "our chat history is already empty!"
    return answer

# run system commands
def need_command(txt):
    if 'who' in txt or 'what' in txt or 'why' in txt or 'how' in txt or 'which' in txt or 'you' in txt:
        return False

    response = ollama.chat(model=chackCommandNeedModel, messages=[{
                        'role': 'user',
                        'content': f"""you are a help ful assistant who can use terminal commands. this is the software that you can run commands for:{systemOs}
                         this is the  user wnats this from you:{txt}
                         is it needed to run any commands?
                         os is : {systemOs}
                         GIVE ME THE SHORTEST ANSWER POSSIBLE.
                         DO NOT say whatt to do or what code to run, just say if its needed or not
                         DO NOT ever say anything exept yes or no
                         DO NOT say yes to qustions like: what is pi, who are you, why is sun white, what is smart watch, etc.
                        """
                        }])
    isneed = response['message']['content'].lower()
    print (isneed)
    if 'yes' in isneed:
        return True
    else:
        return False
    
def fail_safe(command):
    if 'shutdown' in command or 'reboot' in command or 'restart' in command or 'rm' in command or 'remove' in command or 'sudo' in command  or 'kill' in command:
        return False
    else:
        return True