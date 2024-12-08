from time import sleep
from notifypy import Notify
import whisper
import sounddevice
import wavio
import ollama
import subprocess
from config import *
from functions import *


# Initialize recording parameters and notification system
freq = 44100
duration = 7
notification = initialize_notification()

notification = Notify()
notification.title = 'J.A.R.V.I.S.'

# Start listening phase
notification.message = "listening..."
notification.send(block=False)

# Record audio
recording = sounddevice.rec(int(duration * freq), samplerate=freq, channels=2)
sounddevice.wait(duration)
wavio.write("recording.mp3", recording, freq, sampwidth=2)

# Transcribe audio to text
notification.message = "transcribing..."
notification.send(block=False)

model = whisper.load_model(whisperModel)
txt = model.transcribe("recording.mp3")["text"].lower()
continues = False

# Main interaction loop
while True:
    # Check if user said anything
    if txt == '':
        notification.message = "you didn't say anything!"
        notification.send(block=False)
        break

    # Handle different user commands
    # Enable continuous chat mode
    if ("repeating" in txt or "continuous" in txt) and "chat" in txt:
        continues = True
        notification.message = "this chat is now continuous"
        subprocess.Popen('espeak "this chat is now continuous"', shell=True)
    # Stop continuous chat mode
    elif "stop" == txt :
        notification.message = "stopped"
        notification.send(block=False)
        subprocess.Popen('espeak "this chat is now over. bye!"', shell=True)
        break
    # Clear chat history
    elif "forget" in txt and "chat" in txt:
        clear = clear_history()
        notification.message = clear
        subprocess.Popen(f'espeak "{clear}"', shell=True)
    # Process other inputs
    else:
        useCommand = need_command(txt)
        print (useCommand)
        # Handle system commands
        if useCommand:
            # Generate command using AI
            response = ollama.generate(model=CommandModel, prompt=f"""
                        {ollamaPromptCommandGenerate}
                        chat history:{str(show_history_to_AI())}
                        user prompt : {txt}
                        os : {systemOs}
                        """,)
            input = r'{}'.format(str(response['response'])).replace(r'\n', '').replace('bash', '').replace('`', '')
            
            # Execute command if it passes safety check
            if fail_safe(input):
                notification.message = f'running command:{input} in 3 seconds'
                notification.send(block=False)
                sleep(3)
                notification.message = f'ran command:{input}'
                notification.send(block=False)
                with subprocess.Popen(input, stdout=subprocess.PIPE, stderr=None, shell=True) as process:
                    output = process.communicate()[0].decode("utf-8")

                print('==============\n', output, '\n=================')

                # Get AI explanation of command output
                response = ollama.chat(model=ollamaModel, messages=
                    [{'role' : 'system', 'content' : f'{ollamaPromptCommandExplane}'  + 'give me the shortest answer possible.' + show_history_to_AI()},
                    {'role': 'user', 'content': f'command ran:{input}\n command output:{output}\nuser prompt:{txt}'}])

                save_command_history(txt, input,response['message']['content'],output)
                notification.message = response['message']['content']
                subprocess.Popen(f'espeak "{response['message']['content'].translate({ord(i): None for i in '*:\'"`'})}"', shell = True)
            else:
                # Handle failed safety check
                save_command_history(txt, input,response['response'], "failsafe didn't allow")
                notification.message = f"my failsafe doesn't allow me to run command:{input}"
                subprocess.Popen(f'espeak "my failsafe doesn\'t allow me to do it"', shell = True)
        else:
            # Handle regular chat interactions
            response = ollama.chat(model=ollamaModel, messages=
                [{'role' : 'system', 'content' : f'{ollamaPrompt}' + 'show me the shortest answer possible.'}] +
                show_history_to_AI() +
                [{'role': 'user', 'content': f'{txt}'}])
                    
            save_history(txt, response['message']['content'])
            subprocess.Popen(f'espeak "{response['message']['content'].translate({ord(i): None for i in '*:\'"`'})}"', shell = True)
            notification.message = response['message']['content']
    notification.send(block=True)

    # Break loop if not in continuous mode
    if not continues:
        break

    # Prepare for next interaction in continuous mode
    sleep(5)
    notification.message = "listening..."
    notification.send(block=False)

    # Record new audio
    recording = sounddevice.rec(int(duration * freq), samplerate=freq, channels=2)
    sounddevice.wait(duration)
    wavio.write("recording.mp3", recording, freq, sampwidth=2)

    # Transcribe new audio
    notification.message = "transcribing..."
    notification.send(block=False)

    txt = model.transcribe("recording.mp3")["text"].lower()