import tempfile
import subprocess
import platform
from PIL import Image
from io import BytesIO
from geniebottle import Magic
from geniebottle.spellbooks import OpenAI, StabilityAI, Local
from uuid import uuid4
import random

def open_with_default_media_player(file_path):
    """Opens a file with the system's default media player based on the OS."""
    system_platform = platform.system()
    
    try:
        if system_platform == "Darwin":  # macOS
            result = subprocess.run(['open', file_path], check=True, capture_output=True, text=True)
        elif system_platform == "Windows":  # Windows
            result = subprocess.run(['start', file_path], shell=True, check=True, capture_output=True, text=True)
        elif system_platform == "Linux":  # Linux
            result = subprocess.run(['xdg-open', file_path], check=True, capture_output=True, text=True)
        else:
            raise OSError("Unsupported operating system for opening media files.")
        
        print(result.stdout)  # Output if successful
        print(result.stderr)  # Any error output

    except subprocess.CalledProcessError as e:
        print("Error opening file:", e.stderr or e.output)



# Initialize magic instance
magic = Magic(max_cost_per_cast=1.5)

# Define and add spells
chatgpt = OpenAI().get('chatgpt')
stable_diffusion = StabilityAI().get('stable_image_ultra')
stable_video_diffusion = StabilityAI().get('stable_video_diffusion')
magic.add([chatgpt, stable_diffusion, stable_video_diffusion])
save = Local().get('save_content')

save_dir = "./gens"

countries = [
    "Afghanistan", "Åland Islands", "Albania", "Algeria", "American Samoa", "Andorra", "Angola",
    "Anguilla", "Antarctica", "Antigua & Barbuda", "Argentina", "Armenia", "Aruba", "Australia",
    "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium",
    "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bosnia & Herzegovina", "Botswana",
    "Bouvet Island", "Brazil", "British Indian Ocean Territory", "British Virgin Islands", "Brunei",
    "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde",
    "Caribbean Netherlands", "Cayman Islands", "Central African Republic", "Chad", "Chile", "China",
    "Christmas Island", "Cocos (Keeling) Islands", "Colombia", "Comoros", "Congo - Brazzaville",
    "Congo - Kinshasa", "Cook Islands", "Costa Rica", "Côte d’Ivoire", "Croatia", "Cuba", "Curaçao",
    "Cyprus", "Czechia", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt",
    "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Falkland Islands",
    "Faroe Islands", "Fiji", "Finland", "France", "French Guiana", "French Polynesia",
    "French Southern Territories", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar",
    "Greece", "Greenland", "Grenada", "Guadeloupe", "Guam", "Guatemala", "Guernsey", "Guinea",
    "Guinea-Bissau", "Guyana", "Haiti", "Heard & McDonald Islands", "Honduras", "Hong Kong SAR China",
    "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Isle of Man", "Israel",
    "Italy", "Jamaica", "Japan", "Jersey", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait",
    "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein",
    "Lithuania", "Luxembourg", "Macao SAR China", "Madagascar", "Malawi", "Malaysia", "Maldives",
    "Mali", "Malta", "Marshall Islands", "Martinique", "Mauritania", "Mauritius", "Mayotte", "Mexico",
    "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique",
    "Myanmar (Burma)", "Namibia", "Nauru", "Nepal", "Netherlands", "New Caledonia", "New Zealand",
    "Nicaragua", "Niger", "Nigeria", "Niue", "Norfolk Island", "North Korea", "North Macedonia",
    "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau", "Palestinian Territories",
    "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Pitcairn Islands", "Poland",
    "Portugal", "Puerto Rico", "Qatar", "Réunion", "Romania", "Russia", "Rwanda", "Samoa",
    "San Marino", "São Tomé & Príncipe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles",
    "Sierra Leone", "Singapore", "Sint Maarten", "Slovakia", "Slovenia", "Solomon Islands", "Somalia",
    "South Africa", "South Georgia & South Sandwich Islands", "South Korea", "South Sudan", "Spain",
    "Sri Lanka", "St. Barthélemy", "St. Helena", "St. Kitts & Nevis", "St. Lucia", "St. Martin",
    "St. Pierre & Miquelon", "St. Vincent & Grenadines", "Sudan", "Suriname", "Svalbard & Jan Mayen",
    "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste",
    "Togo", "Tokelau", "Tonga", "Trinidad & Tobago", "Tunisia", "Turkey", "Turkmenistan",
    "Turks & Caicos Islands", "Tuvalu", "U.S. Outlying Islands", "U.S. Virgin Islands", "Uganda",
    "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan",
    "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Wallis & Futuna", "Western Sahara", "Yemen",
    "Zambia", "Zimbabwe"
]
prompt = input("Prompt: ")
# random.shuffle(countries)

# while True:
# have default of 1
num_times_to_repeat = int(input("Number of times to repeat the prompt (default = 1): ") or 1)

# for country in countries:
    # prompt = f"A dog wearing traditional clothing in {country}"
    # prompt = f'A god from traditional mythology of {country}. Adjust this template, but do not deviate too much: "a full wide photo shot of a person standing in the water next to a Chinese dragon, in the style of fantasy scenes, realistic detail, theo prins, magewave, ferrania p30, evgeni gordiets, kuang hong, 8k sharp focus, photorealism, highly detailed."'
print(f'Prompt: {prompt}')
for _ in range(num_times_to_repeat):
    stream = magic.cast(
        input=prompt,
        model="gpt-4o",
        system="""
        You respond with prompts for an image generation stable diffusion model 
        based on the users input. You only respond with the prompt.
        """,
        max_input_tokens=1000,
        max_output_tokens=4096,
        separator="\n",
    )

    for chunk in stream:
        if isinstance(chunk, str):
            print(chunk, end="")
        # elif isinstance(chunk, Image.Image):  # For images
        #     chunk.show()
        elif isinstance(chunk, (BytesIO, bytes)):  # For video bytes
            video_data = chunk if isinstance(chunk, bytes) else chunk.read()
            
            # Save video to a temporary file
            video_path = f"{save_dir}/{uuid4()}"
            save(video_data, 'video', video_path)
            
            # Open the video with the default media player
            open_with_default_media_player(f"{video_path}.mp4")

    print('\n')
