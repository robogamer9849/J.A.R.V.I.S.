# J.A.R.V.I.S.
this is just a simple AI assistant that uses olama and whisper
this app is fully local and needs no internet connection to work

keywords: if you day these words in one sentence, jarvis will do what they do</br>
forget, chat: this will clear your chat history</br>
repeating, chat: this will enable repeating chat, something live gemeni live or gpt-4o</br>
stop: this will stop the conversation</br>

‼️note that this allaws AI to run command on your system and if AI does something that breacks your system I am NOT responsible for it‼️</br>
 there is a failsafe to stop ai from doing dangres things but you still have 3 seconds befor it runs the code that ai made to see if its harmfull
 for now all you can do is to power of your ps if the command is dagres but i try to add a better way in the future</br>

a presentation video:
[![Watch the video](https://github.com/user-attachments/assets/87a30e82-adac-4c91-a78d-03da7f0ee324)](https://github.com/user-attachments/assets/d23b8733-ebd4-4a9b-9468-1d950d6c52fc)




reqirements:</br>
python:</br>
notifypy `pip install notifypy`</br>
whisper `pip install whisper`</br>
sounddevice `pip install sounddevice`</br>
wavio `pip install wavio`</br>
ollama python `pip install ollama`</br>
subprocess `pip install subprocess`</br>
or: `pip install -r requirements.txt` to install all <br/>
app:</br>
[ollama app](www.ollama.com)</br>
 espeak:</br> 
  arch: `sudo pacman -S espeak`</br> 
  debian/ubuntu: `sudo apt install espeak`</br> 
  fedora: `dnf install espeak`</br> 
  mac : `brew install espeak`<br/>
  windows : [toturial](https://medium.com/@harsh_jinger/espeak-on-windows-your-key-to-effortless-text-to-speech-in-windows-terminal-f7560357aff5)<br/>

how to install:</br>
1. clone this repo: `git clone https://github.com/robogamer9849/J.A.R.V.I.S..git` or download the files from realeses page **note that you have to download all files for this to work**</br>
2. `cd J.A.R.V.I.S.`
3. open `config.py` and change the values to your liking</br>
4. run **main.py**: `python PATH/TO/MAIN.PY`</br>
   or run **runTypingMode.py**: `python PATH/TO/RUNTYPINGMODE.PY` for text only mode

for easy acces bind a keyboard shortcut to `python PATH/TO/MAIN.PY` or `python PATH/TO/RUNTYPINGMODE.PY`:</br>
on linux gnome: setting > keyboard > view and customize shortcuts > custom shortcuts > +</br>
on linux kde: Settings > Shortcuts > Add Application</br>
on windows: make a file named `jarvis.bat` > open it with text editor > type the command > save > open its properties > shortcut > sortcut key</br>
on mac: Apple menu  > System Settings > Keyboard > Keyboard Shortcuts > (idk the rest i dont have a mac😅)</br>
