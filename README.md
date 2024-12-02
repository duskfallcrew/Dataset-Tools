# Dataset-Tools: Enhancing Dataset Visualization and Text Editing
Dataset-Tools is a versatile script designed to assist in visualizing datasets and editing associated text files. Developed using PyQt6, it provides an intuitive graphical interface for managing images and their corresponding annotations. Inspired by tools within the Civitai community, this project aims to empower users in enhancing their dataset management capabilities.

<img width="1201" alt="Screenshot 2024-12-02 at 21 34 51" src="https://github.com/user-attachments/assets/0665932e-4710-4687-b0ce-4e94f6e2a5cd">

You're more than welcome to help develop this tool, I am not really a programmer, I am aware of this - I am doing tiny things with Chat GPT to further help my community! 

## How to Use Dataset-Tools
### Launching the Application

Ensure Python is installed on your system.
Clone or download the Dataset-Tools repository from GitHub.
Setting Up Environment

### Install necessary dependencies using pip:
Copy code
pip install PyQt6 Pillow
Running the Application

### Navigate to the directory where main.py is located.
Run the application using Python:
css
Copy code
python main.py
### User Interface Overview

#### Main Window: The application window opens with options to view images, edit associated text, and select themes.
Image Display: Images are displayed in the top section of the window with options for scaling and centering.
Text Editor: Below the image, there's a text box for editing and saving text associated with the selected image.
Listboxes: Lists images and text files available in the current directory.
Buttons: Includes "Save" to save edited text, "Close" to exit the application gracefully, and "Select Image" to pick an image for editing.
Managing Images and Text

#### Selecting Images: Click on an image in the listbox or gallery to display it in the main window.
Editing Text: Edit the text in the text box. Use the "Save" button to save changes to the associated text file.
Changing Themes

#### Theme Selection: Use the dropdown menu labeled "Theme Selection" to choose from available themes.
Applying Themes: Themes change the background, text colors, and button styles to suit different preferences.
Customizing Themes (Advanced)

#### Editing Themes: Modify or add themes in the themes dictionary within the main.py file. Each theme consists of background color (bg), foreground color (fg), text background (text_bg), text foreground (text_fg), button background (button_bg), and button foreground (button_fg).


## Overview of Themes
Dataset-Tools offers a range of themes to customize the interface according to user preferences:

Beetlejuice Inspired
Light Theme
Dark Theme
Pastel V2
Night Sky
Fire Red
Sunset Orange
Lavender
Ocean Blue
Mint
Forest Green
Some themes, like Pastel V1, are currently disabled due to issues with text colors, which are being addressed in ongoing development.

## Key Features
Graphical User Interface (GUI): Designed initially with Tkinter and later migrated to PyQt6 for improved functionality and aesthetics.
Image Gallery: Allows for browsing and selection of images within the dataset.
Text Editing: Supports real-time editing and saving of associated text files.
Theme Customization: Choose from various predefined themes to personalize the application's appearance.
## Future Developments
Educational Resources: Planned video tutorials and comprehensive text guides to aid users in navigating Dataset-Tools effectively.
Enhanced Theme Functionality: Ongoing improvements to themes, focusing on legibility and aesthetic appeal across different datasets.
Deployment and Testing: Targeting broader compatibility across operating systems and screen resolutions to optimize user experience.
## About the Creator
Dataset-Tools is developed by the Duskfall Portal Crew, a diverse system navigating life with DID, ADHD, Autism, and CPTSD. Our motivation stems from leveraging AI to promote inclusivity and mental health awareness. Join us in exploring identity and creative expression through technology.

## Join Our Community
Website: Earth & Dusk Portal
Discord: Join our Discord
Backups: Hugging Face
Support Us
Send a Pizza: Buy us a pizza
Subreddit: Reddit Community
Thank you for supporting us on our journey and contributing to the Earth and Dusk community.

## Credits
ChatGPT 3.5 & 4o: Powering innovative solutions and creative endeavors.
Canvas icons created by Freepik - Flaticon: Enhancing visual appeal and functionality.
Claude - for literally reworking this.

## Sample Images 
Here you can see the themes and gui overlook.
### GUI Overview
<img width="1199" alt="Screenshot 2024-06-15 at 19 09 31" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/23cf71c2-2a4b-482c-81fd-c2b06f691da8">

### Sample Themes

<img width="1194" alt="Screenshot 2024-06-15 at 19 09 40" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/f8d762db-3f46-48ef-9e95-63c613b622ad">
<img width="1196" alt="Screenshot 2024-06-15 at 19 09 48" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/32818e21-56ea-4e0d-86de-5d3085960e09">
<img width="1197" alt="Screenshot 2024-06-15 at 19 10 27" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/c1452a29-3b90-493c-b9eb-9553fa2b4935">
<img width="1202" alt="Screenshot 2024-06-15 at 19 10 36" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/295bf87c-f213-427c-ae42-55c60988ed96">

### Errors to Fix
<img width="1202" alt="Screenshot 2024-06-15 at 19 11 19" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/81948737-4c6d-4db1-9070-dfc66570ca4d">
<img width="1198" alt="Screenshot 2024-06-15 at 19 11 31" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/9b064e53-17e9-4ddb-9e3f-91f49f2f644b">

## Changelog

Started with Tkinter Gui, but moved to PYQT6.

Realized it needed more to it. 

Added gallery, text editing, image preview.

Text box list.

Save, Close and Select Image. 

Commented out themes that don't work. 

Tried to add an icon.

Fixing aspect ratio is ... well i'm on a retina 5k screen, so go figure. - This is because if you select a TALLER image it'll break and you can't close it or edit the text, i'm working on it.

The OLDER file in this specific repo, as i'm finally merging to main will give you back some stuff btue the images are tiny. 

Indentation issues are fixed. 

### What the OLD FILE Looks like - and that's ok! 


<img width="1388" alt="Screenshot 2024-06-15 at 16 56 14" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/27b6bfef-ef80-449a-b307-b842b91ec28f">



## Coming Soon

Video tutorial via youtube.

Tutorial in text, images.

Fixing themes where the text is just attrocious. That's my fault, sorry.

When we're out of MAIN development mode, i want to try and get this as a homebrew cask, and figure out how to all that - we're just not ready yet.

Get people to test it on different OS boxes, so we can decide WHAT sizing is best. 


# About the Creator:
We are the Duskfall Portal Crew, a DID system with over 300 alters, navigating life with DID, ADHD, Autism, and CPTSD. We believe in AI’s potential to break down barriers and enhance mental health, despite its challenges. Join us on our creative journey exploring identity and expression.

## Join Our Community:

### Website: 
[End Media](https://www.end-media.org/)

### Discord: 
[Join our Discord](https://discord.gg/5t2kYxt7An)

### Backups: 
[Hugging Face](https://huggingface.co/EarthnDusk)

### Support Us: 
[Send a Pizza](https://www.end-media.org/)

### Subreddit:
[Reddit](https://www.reddit.com/r/earthndusk/)

Thank you for being part of our journey and supporting the Earth and Dusk community. 

# Credits

ChatGPT 3.5 & 4o

Support of my peers, and the community at Large..

[Canvas icons created by Freepik - Flaticon](https://www.flaticon.com/free-icons/canvas)

#### Where we started from over 24 hours ago:
<img width="459" alt="Screenshot 2024-06-14 at 22 00 40" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/9dc7f859-13d5-4e75-9f21-171648b3061e">
<img width="464" alt="Screenshot 2024-06-14 at 22 09 01" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/dbfd0678-aff4-47f2-a23f-e7cfa14582ef">
<img width="1202" alt="Screenshot 2024-06-15 at 00 03 47" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/a2e1b5bb-7ffc-43e9-8002-56aa977478f6">
<img width="1198" alt="Screenshot 2024-06-15 at 00 03 55" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/8f948d75-96ae-4ae7-b87b-0ad8887e6745">
<img width="1678" alt="Screenshot 2024-06-15 at 00 04 16" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/bba4d2a7-9aaa-42f3-82f8-b866db8f0084">
<img width="1183" alt="Screenshot 2024-06-15 at 14 06 00" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/a513f6df-1fca-421b-ae8b-401abc7741cb">
<img width="1190" alt="Screenshot 2024-06-15 at 15 01 45" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/10d386f8-ae21-4672-964c-5d4ebc889275">

