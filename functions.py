from pathlib import Path
import os
import ollama
from config import *
import json

# File names for storing chat history and last answer
LAST_ANSWER_FILE = "last-answer.txt"
HISTORY_FILE = "history.json"

def save_history(user_message, ai_message):
    """Save a conversation exchange between user and AI to history files"""
    try:
        # Get existing history or start fresh
        current_history = show_history_to_AI()
        history_list = [] if current_history == [{'role': 'system', 'content': 'no History!'}] else current_history

        # Save to history JSON file
        with open(Path(__file__).parent.resolve()/HISTORY_FILE, 'w') as file:
            new_messages = [
                {'role': 'user', 'content': user_message},
                {'role': 'assistant', 'content': r'{}'.format(ai_message).replace(r'\n', '')}
            ]
            file.write(json.dumps(history_list + new_messages, indent=2))

        # Save last exchange to text file
        with open(Path(__file__).parent.resolve()/LAST_ANSWER_FILE, 'w') as file:
            file.write(f"user:  {user_message}\nAI: {ai_message}")

    except json.decoder.JSONDecodeError:
        clear_history()

def save_command_history(user_message, command, ai_message, command_output):
    """Save a conversation exchange that includes command execution to history files"""
    try:
        # Get existing history or start fresh
        current_history = show_history_to_AI()
        history_list = [] if current_history == [{'role': 'system', 'content': 'no History!'}] else current_history

        # Save to history JSON file
        with open(Path(__file__).parent.resolve()/HISTORY_FILE, 'w') as file:
            new_messages = [
                {'role': 'user', 'content': user_message},
                {'role': 'assistant', 'content': r'{}'.format(ai_message).replace(r'\n', '')},
                {'role': 'tool', 'content': 'command: ' + command},
                {'role': 'tool', 'content': 'command output: ' + command_output}
            ]
            file.write(json.dumps(history_list + new_messages, indent=2))

        # Save last exchange to text file
        with open(Path(__file__).parent.resolve()/LAST_ANSWER_FILE, 'w') as file:
            file.write(f"user:  {user_message}\nAI: {ai_message}")

    except json.decoder.JSONDecodeError:
        clear_history()

def show_history_to_AI():
    """Retrieve conversation history from file"""
    try:
        history_path = Path(__file__).parent.resolve()/HISTORY_FILE
        if history_path.exists():
            with open(history_path, 'r') as file:
                return json.load(file)
        return [{'role': 'system', 'content': 'no History!'}]

    except json.decoder.JSONDecodeError:
        clear_history()
        return [{'role': 'system', 'content': 'no History!'}]

def clear_history():
    """Delete history files and return appropriate message"""
    last_answer_path = Path(__file__).parent.resolve()/LAST_ANSWER_FILE
    history_path = Path(__file__).parent.resolve()/HISTORY_FILE
    
    if last_answer_path.exists() or history_path.exists():
        if last_answer_path.exists():
            os.remove(last_answer_path)
        if history_path.exists():
            os.remove(history_path)
        return "I forgot our chat history!"
    return "our chat history is already empty!"

# def need_command(user_text):
#     """Determine if user request requires command execution"""
#     # Skip command execution for question words
#     if any(word in user_text.lower() for word in ['who', 'why', 'which']):
#         return False

#     # Ask AI if command execution is needed
#     prompt = f"""you are a helpful assistant who can use terminal commands. this is the software that you can run commands for:{systemOs}
#                 this is the  user wants this from you:{user_text}
#                 this is user chat history with you:{str(show_history_to_AI())}
#                 is it needed to run any commands?
#                 os is : {systemOs}
#                 DO NOT say what to do or what code to run, just say if its needed or not
#                 DO NOT ever say anything except yes or no
#                 DO NOT say yes to questions like: what is pi, who are you, why is sun white, what is smart watch, etc.
#                 do not explane anything. just say yes or no!
#                 """
#     response = ollama.generate(model=ollamaModel, prompt=prompt)
#     return 'yes' in response['response'].lower()

def need_command(user_text):
    """Determine if user request requires command execution"""
    # Skip command execution for question words and common queries
    skip_words = ['who', 'why', 'which', 'when', 'where', 'how']
    if any(word in user_text.lower() for word in skip_words):
        return False
        
    # Keywords that suggest command execution is needed
    command_indicators = [
        'run', 'execute', 'start', 'launch', 'open',
        'show', 'list', 'display', 'find', 'search',
        'create', 'make', 'delete', 'remove',
        'check', 'verify', 'install', 'update',
        'directory', 'folder', 'file', 'path',
        'process', 'service', 'program'
    ]
    
    # Check if any command indicators are present
    if any(indicator in user_text.lower() for indicator in command_indicators):
        return True
        
    # Ask AI if command execution is needed
    prompt = f"""you are a helpful assistant who can use terminal commands. this is the software that you can run commands for:{systemOs}
                this is the  user wants this from you:{user_text}
                this is user chat history with you:{str(show_history_to_AI())}
                is it needed to run any commands?
                os is : {systemOs}
                DO NOT say what to do or what code to run, just say if its needed or not
                DO NOT ever say anything except yes or no
                DO NOT say yes to questions like: what is pi, who are you, why is sun white, what is smart watch, etc.
                do not explain anything. just say yes or no!
                """
    response = ollama.generate(model=ollamaModel, prompt=prompt)
    return 'yes' in response['response'].lower()


def fail_safe(command):
    """Check if command is safe to execute"""
    # List of dangerous or sensitive commands/keywords
    dangerous_commands = [
        # System control
        'shutdown', 'reboot', 'restart', 'poweroff', 'halt',
        # Deletion/modification
        'rm', 'remove', 'del', 'format', 'mkfs', 'rmdir', 'rd',
        # Privileged access
        'sudo', 'su', 'passwd', 'chown', 'chmod', 'runas', 'net user',
        # Process control
        'kill', 'pkill', 'taskkill', 'wmic',
        # Network sensitive
        'iptables', 'firewall', 'netsh', 'route', 'ipconfig', 'ifconfig',
        # File system sensitive
        'mkfs', 'fdisk', 'mount', 'diskpart', 'format',
        # Package managers
        'apt', 'yum', 'pacman', 'dnf', 'brew', 'winget', 'choco', 'scoop',
        # Registry and system modifications
        'reg', 'regedit', 'gpedit', 'sysctl',
        # Shell escapes
        'cmd', 'powershell', 'bash', 'sh', 'ksh', 'csh',
    ]
    
    # Convert command to lowercase for case-insensitive checking
    command_lower = command.lower().split(" ")
    
    # Check for dangerous commands
    if any(dangerous_cmd in command_lower for dangerous_cmd in dangerous_commands):
        return False
    return True