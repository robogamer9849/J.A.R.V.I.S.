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
duration = 7

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
    # turn on continuous chat if promted
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
        print (useCommand)
        if useCommand:
            response = ollama.generate(model=CommandModel, prompt=f"""
                        {ollamaPromtCommandGenarate}
                        chat history:{str(show_history_to_AI())}
                        user prompt : {txt}
                        os : {systemOs}
                        """)
            # input = r'{}'.format(str(response['response'])).replace(r'\n', '').replace('bash', '').replace('`', '').replace('username', userName).replace('[username]', userName).replace('yourusername', userName).replace('[command]: ' , '').replace('$USER', userName).replace('yourname', userName)
            input = r'{}'.format(str(response['response'])).replace(r'\n', '').replace('bash', '').replace('`', '')
            if fail_safe(input):
                notification.message = f'running command:{input} in 3 seconds'
                notification.send(block=False)
                sleep(3)
                notification.message = f'ran command:{input}'
                notification.send(block=False)
                with subprocess.Popen(input, stdout=subprocess.PIPE, stderr=None, shell=True) as process:
                    output = process.communicate()[0].decode("utf-8")

                print('==============\n', output, '\n=================')

                response = ollama.chat(model=ollamaModel, messages=
                 [{'role' : 'system', 'content' : f'{ollamaPromtCommandExplane}'}] +
                 show_history_to_AI() +
                 [{'role': 'user', 'content': f'command ran:{input}\n command output:{output}\nuser prompt:{txt}'}])

                save_command_history(txt, input,response['message']['content'],output)
                notification.message = response['message']['content']
                subprocess.Popen(f'espeak "{response['message']['content'].translate({ord(i): None for i in '*:\'"`'})}"', shell = True)
            else:
                save_command_history(txt, input,response['response'], "falisafe didnt allow")
                notification.message = f'my failsafe doesnt allow me to run command:{input}'
                subprocess.Popen(f'espeak "my failsafe doesnt allow me to do it"', shell = True)
        else:
            response = ollama.chat(model=ollamaModel, messages=
                 [{'role' : 'system', 'content' : f'{ollamaPromt}'}] +
                 show_history_to_AI() +
                 [{'role': 'user', 'content': f'{txt}'}])
                    
            save_history(txt, response['message']['content'])
            subprocess.Popen(f'espeak "{response['message']['content'].translate({ord(i): None for i in '*:\'"`'})}"', shell = True)
            notification.message = response['message']['content']
        # print(f'"{txt}"')
        # print(response['message']['content'].translate({ord(i): None for i in '*:\'"'}))
        
       

    # listen again if continuous chat in on
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
