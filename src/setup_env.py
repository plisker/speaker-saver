import os


def create_env_file():
    env_file_path = os.path.join(os.getcwd(), ".env")

    if os.path.exists(env_file_path):
        print(".env file already exists. Skipping creation.")
        return

    client_id = input("Enter your Spotify CLIENT_ID: ")
    client_secret = input("Enter your Spotify CLIENT_SECRET: ")
    speakers_ip = input("Enter the IP of the Kasa SmartPlug used with your speakers: ")
    mixer_ip = input("Enter the IP of the Kasa SmartPlug used with your audio mixer: ")
    tv_ip = input("Enter your Sony TV IP: ")

    with open(env_file_path, "w") as env_file:
        env_file.write(f"source venv/bin/activate\n")
        env_file.write(f"CLIENT_ID={client_id}\n")
        env_file.write(f"CLIENT_SECRET={client_secret}\n")
        env_file.write(f"SPEAKERS_IP={speakers_ip}\n")
        env_file.write(f"MIXER_IP={mixer_ip}\n")
        env_file.write(f"TV_IP={tv_ip}\n")

    print(".env file created successfully!")


if __name__ == "__main__":
    create_env_file()
