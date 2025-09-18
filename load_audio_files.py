import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, 'config/audio_paths.json')

with open(config_path, 'r') as config_file:
    audio_paths = json.load(config_file)

background_music = os.path.join(base_dir, audio_paths['background_music'])  # courtesy of mixkit.co
explosion_sound = os.path.join(base_dir, audio_paths['explosion_sound'])
