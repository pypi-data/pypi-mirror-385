import os
import textwrap

import rich

from egse.settings import Settings

from dotenv import load_dotenv

load_dotenv(override=False)

settings = Settings.load("Hexapod Controller")

def main():
    print("Hello from cubespec-puna!")
    print(f"{os.getenv('PROJECT') = }")
    print(f"{os.getenv('SITE_ID') = }")

    rich.print("Loaded settings:")
    rich.print(settings)

    print(
        textwrap.dedent(
            """
            First make sure the above settings are correct.
            
            Start the GUI with the following command:
            
                $ puna_ui --device-type direct PUNA_01
            
            This will start a GUI with a direct connection to the Symétrie Hexapod Controller. 
            """
        )
    )

if __name__ == "__main__":
    main()
