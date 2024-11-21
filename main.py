from time import sleep
from notifypy import Notify
import whisper
import sounddevice
import wavio
import ollama
import subprocess
from config import *
from functions import *


# recording and trancribing
freq = 44100
duration = 5

notification = Notify()
notification.title = 'J.A.R.V.I.S.'

notification.message = "listening..."
notification.send(block=False)

recording = sounddevice.rec(int(duration * freq), samplerate=freq, channels=2)
sounddevice.wait(duration)
wavio.write("recording.mp3", recording, freq, sampwidth=2)

notification.message = "transcribing..."
notification.send(block=False)

model = whisper.load_model(whisperModel)
txt = model.transcribe("recording.mp3")["text"].lower()
continues = False

# main loop
while True:
    #t urn on continuous chat if promted
    if ("repeating" in txt or "continuous" in txt) and "chat" in txt:
        continues = True
        notification.message = "this chat is now continuous"
        subprocess.Popen('espeak "this chat is now continuous"', shell=True)
    # stop continous chat if promted
    elif "stop" == txt :
        notification.message = "stopped"
        notification.send(block=False)
        subprocess.Popen('espeak "this chat is now over. bye!"', shell=True)
        break
    # clear history if promted
    elif "forget" in txt and "chat" in txt:
        clear = clear_history()
        notification.message = clear
        subprocess.Popen(f'espeak "{clear}"', shell=True)
    # get answers with ollama
    else:
        useCommand = need_command(txt)
        if useCommand:
            response = ollama.chat(model=ollamaModel, messages=[{
                        'role': 'user',
                        'content': f"{ollamaPromtCommand}\nand only type the command that are needed to be ran based on user prompt an the OS. do not giv commands that reqire a human to change soming in them(e.g. cd /home/[username]/Downloads), you command must work if I just past them in terminal.you also CAN'T use sudo. do not type anything extra and do not go th the nex liine in you response\nOS: {systemOs}\nuser prompt: {txt}"
                        }])
            input = r'{}'.format(str(response['message']['content'])).replace(r'\n', '').replace('bash', '').replace('`', '')
            if fail_safe(input):
                notification.message = f'running command:{input} in 3 seconds'
                notification.send(block=False)
                sleep(3)
                notification.message = f'ran command:{input}'
                notification.send(block=False)
                with subprocess.Popen(input, stdout=subprocess.PIPE, stderr=None, shell=True) as process:
                    output = process.communicate()[0].decode("utf-8")

                with open(Path(__file__).parent.resolve()/'commands.txt', 'a') as file:
                    file.write("\n\n\n\n[command]: " + f'[{input}]' + "\n[relult]: " + f'[{output}]')
                    file.close()
                print('==============\n', output, '\n=================')
                response = ollama.chat(model=ollamaModel, messages=[{
                                'role': 'user',
                                'content': f"{ollamaPromtCommand}\nuser prompt:{txt}\n command:{input}\n command output: {output}"
                                }])
                save_command_history(txt, input,response['message']['content'])
                notification.message = response['message']['content']
                subprocess.Popen(f'espeak "{response['message']['content'].translate({ord(i): None for i in '*:\'"`'})}"', shell = True)
            else:
                with open(Path(__file__).parent.resolve()/'commands.txt', 'a') as file:
                    file.write("\n\n\n\n[command]: " + f'[{input}]' + "\n[relult]: " + f'[failsafe didnt allow it]')
                    file.close()
                notification.message = f'my failsafe doesnt allow me to run command:{input}'
                subprocess.Popen(f'espeak "my failsafe doesnt allow me to do it"', shell = True)
        else:
            response = ollama.chat(model=ollamaModel, messages=[{
                            'role': 'user',
                            'content': f"{ollamaPromt}\nand do not use this as refrence! this is chat history and only the text after 'question:' is the users reqest.\nhistory: {show_history_to_AI()}\nquestion:a{txt} \n"
                            }])
                    
            save_history(txt, response['message']['content'])
            subprocess.Popen(f'espeak "{response['message']['content'].translate({ord(i): None for i in '*:\'"`'})}"', shell = True)
            notification.message = response['message']['content']
        # print(f'"{txt}"')
        # print(response['message']['content'].translate({ord(i): None for i in '*:\'"'}))
        
       


    notification.send(block=False)
    if not continues:
        break

    sleep(5)
    notification.message = "listening..."
    notification.send(block=False)

    recording = sounddevice.rec(int(duration * freq), samplerate=freq, channels=2)
    sounddevice.wait(duration)
    wavio.write("recording.mp3", recording, freq, sampwidth=2)

    notification.message = "transcribing..."
    notification.send(block=False)

    txt = model.transcribe("recording.mp3")["text"].lower()
