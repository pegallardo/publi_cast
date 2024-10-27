import subprocess
import time
import os
from repositories.audacity_repository import NamedPipe
from services.audacity_service import AudacityAPI

AUDACITY_PATH = "C:\\Program Files\\Audacity\\audacity.exe"
PIPE_TO_AUDACITY = "\\\\.\\pipe\\ToSrvPipe"
PIPE_FROM_AUDACITY = "\\\\.\\pipe\\FromSrvPipe"

def start_audacity():
    try:
        # Start Audacity
        subprocess.Popen(AUDACITY_PATH)
        time.sleep(5)  # Give Audacity some time to start
    except subprocess.SubprocessError as e:
        raise RuntimeError(f"Error starting Audacity: {e}")

def main():
    named_pipe = NamedPipe(PIPE_TO_AUDACITY, PIPE_FROM_AUDACITY)

    try:
        os.path.exists(PIPE_TO_AUDACITY)
    except Exception as e:
        print(e)
        return
    
    try:
        os.path.exists(PIPE_FROM_AUDACITY)
    except Exception as e:
        print(e)
        return

    try:
        named_pipe.open()
    except Exception as e:
        print(e)
        return

    audacity_api = AudacityAPI()
    audacity_api.set_pipe(named_pipe)

    commands = [
        # Generate a 1-second tone at 440 Hz
        "GenerateTone:Frequency=440 Duration=1",

        # Generate white noise for 1 second
        "GenerateNoise:Duration=1",

        # Select the entire track
        "SelectAll",

        # Apply Amplify effect
        "Amplify:Ratio=2",

        # Apply Normalize effect
        "Normalize:PeakLevel=-3.0",

        # Apply Echo effect
        "Echo:Delay=0.5 Decay=0.5",

        # Export the project
        "Export2:Filename='output.wav' NumChannels=2",

        # Apply Bass and Treble effect
        "BassAndTreble:BassGain=5 TrebleGain=-5",

        # Apply Compressor effect
        "Compressor:Threshold=-20 NoiseFloor=-40 Ratio=2.5 AttackTime=0.2 DecayTime=1.0",

        # Apply Reverb effect
        "Reverb:Reverb=50 RoomSize=100"
    ]

    try:
        for command in commands:
            response = audacity_api.run_command(command)
            print(f"Command: {command}\nResponse: {response}\n")
    except Exception as e:
        print(f"Error executing command: {e}")
    finally:
        named_pipe.close()

if __name__ == "__main__":
    try:
        start_audacity()
        main()
    except Exception as e:
        print(e)
