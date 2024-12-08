from time import sleep
import ollama
from config import *
from functions import *
import subprocess

# ANSI color codes for terminal output
GREEN = '\033[32m'
ORANGE = '\033[33m'
RESET = '\033[0m'

# Get initial user input
txt = input('>>> ')

# Main interaction loop
while True:
    answer = ''
    
    # Handle empty input
    if txt == '':
        print("you didn't say anything!\n")
    
    # Handle chat history clearing
    elif "forget" in txt and "chat" in txt:
        clear = clear_history() + '\n'
        print(clear)
    
    # Process user input and generate responses
    else:
        useCommand = need_command(txt)
        
        # Handle command generation and execution
        if useCommand:
            # Generate command using AI
            response = ollama.generate(model=CommandModel, prompt=f"""
                        {ollamaPromptCommandGenerate}
                        chat history:{str(show_history_to_AI())}
                        user prompt : {txt}
                        os : {systemOs}
                        """,)
            
            # Clean up the generated command
            cmd = r'{}'.format(str(response['response'])).replace(r'\n', '').replace('bash', '').replace('`', '')
            
            # Execute command if it passes safety check
            if fail_safe(cmd):
                print(ORANGE + f'running command:{cmd} in 3 seconds')
                sleep(3)
                print(ORANGE + f'ran command:{cmd}')
                
                # Execute command and capture output
                with subprocess.Popen(cmd.replace('%', ''), stdout=subprocess.PIPE, stderr=None, shell=True) as process:
                    output = process.communicate()[0].decode("utf-8")
                
                # Get AI explanation of command results
                response = ollama.chat(model=ollamaModel, messages=
                [{'role' : 'system', 'content' : f'{ollamaPromptCommandExplane}'}] +
                show_history_to_AI() +
                [{'role': 'user', 'content': f'command ran:{cmd}\n command output:{output}\nuser prompt:{txt}'}],
                stream=True,)

                # Stream and save AI response
                for chunk in response:
                    print(GREEN + chunk['message']['content'], end='', flush=True)
                    answer = answer + chunk['message']['content']

                save_command_history(txt, cmd, answer, output)
            else:
                save_command_history(txt, cmd, response['response'], "failsafe didn't allow")
                print(ORANGE + f'my failsafe doesn\'t allow me to run command:{cmd}')
        
        # Handle regular chat interactions
        else:
            response = ollama.chat(model=ollamaModel, messages=
                [{'role' : 'system', 'content' : f'{ollamaPrompt}'}] +
                show_history_to_AI() +
                [{'role': 'user', 'content': f'{txt}'}],
                stream=True)
            
            # Stream and save AI response
            for chunk in response:
                print(GREEN + chunk['message']['content'], end='', flush=True)
                answer = answer + chunk['message']['content']
            save_history(txt, answer)
    
    # Get next user input
    txt = input(RESET + '>>> ')