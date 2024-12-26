# Dataset-Tools: A Simple Dataset Viewer for AI Art

Dataset-Tools is a desktop application designed to help users browse and manage their image and text datasets, particularly those used with AI art generation tools like Stable Diffusion. Developed using PyQt6, it provides a simple and intuitive graphical interface for browsing images, viewing metadata, and examining associated text prompts. This project is inspired by tools within the AI art community and aims to empower users in improving their dataset curation workflow.

<img width="797" alt="Screenshot of the Application" src="https://github.com/user-attachments/assets/7e14c542-482d-42f4-a9ae-4305c9e2c383" />

## How to Use Dataset-Tools

### Launching the Application

1.  Ensure Python is installed on your system.
2.  Clone or download the Dataset-Tools repository from GitHub.
3.  Install the required dependencies:

    ```bash
    pip install PyQt6 pypng
    ```

4.  Navigate to the directory where `main.py` is located.
5.  Run the application using Python:

    ```bash
    python main.py
    ```

### User Interface Overview

The application window has the following main components:

*   **Current Folder:** Displays the path of the currently loaded folder.
*   **Open Folder:** A button to select a folder containing images and text files.
*   **Image List:** Displays a list of images and text files found in the selected folder.
*   **Image Preview:** An area to display a selected image.
*   **Metadata Box:** A text area to display the extracted metadata from the selected image (including Stable Diffusion prompt, settings, etc.).
*   **Prompt Text:** A text label to display the prompt from the selected image.
*   **Text File Content Area:** A text area to display the content of any associated text files.

### Managing Images and Text

*   **Selecting Images:** Click on an image or text file in the list to display its preview, metadata, and associated text content.
*   **Viewing Metadata:** Metadata associated with the selected image is displayed on the text area, such as steps, samplers, seeds, and more.
*   **Viewing Text:** The content of any text file associated with the selected image is displayed on the text box.

## Key Features

*   **Graphical User Interface (GUI):** Built with PyQt6 for a modern and cross-platform experience.
*   **Image Previews:** Quickly view images in a dedicated preview area.
*   **Metadata Extraction:** Extract and display relevant metadata from PNG image files, especially those generated from Stable Diffusion.
*   **Text Viewing:** Display the content of text files.
*   **Clear Layout:** A simple and intuitive layout, with list view on the left, and preview on the right.

## Future Developments

*   **Thumbnail Generation:** Implement thumbnails for faster browsing.
*   **JPEG Metadata:** Add support for extracting metadata from JPEG files.
*   **Themes:** Introduce customizable themes for appearance.
*   **Filtering/Sorting:** Options to filter and sort files.
*   **Better User Experience:** Test on different operating systems and screen resolutions to optimize user experience.
*   **Video Tutorials:** Create video tutorials to show users how to use the program.
*   **Text Tutorials:** Create detailed tutorials in text and image to show the user how to use the program.

## About the Creator

Dataset-Tools is developed by the Duskfall Portal Crew, a diverse system navigating life with DID, ADHD, Autism, and CPTSD. Our motivation stems from leveraging AI to promote inclusivity and mental health awareness. Join us in exploring identity and creative expression through technology.

## Join Our Community

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

## Credits

*   ChatGPT 3.5 & 4o: Powering innovative solutions and creative endeavors.
*   Support of my peers, and the community at Large.
*   [Canvas icons created by Freepik - Flaticon](https://www.flaticon.com/free-icons/canvas)
*   Inspired by [receyuki/stable-diffusion-prompt-reader](https://github.com/receyuki/stable-diffusion-prompt-reader)

### Where we started from

Here you can see some screenshots of previous versions of the application.

<img width="459" alt="Screenshot 2024-06-14 at 22 00 40" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/9dc7f859-13d5-4e75-9f21-171648b3061e">
<img width="464" alt="Screenshot 2024-06-14 at 22 09 01" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/dbfd0678-aff4-47f2-a23f-e7cfa14582ef">
<img width="1202" alt="Screenshot 2024-06-15 at 00 03 47" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/a2e1b5bb-7ffc-43e9-8002-56aa977478f6">
<img width="1198" alt="Screenshot 2024-06-15 at 00 03 55" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/8f948d75-96ae-4ae7-b87b-0ad8887e6745">
<img width="1678" alt="Screenshot 2024-06-15 at 00 04 16" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/bba4d2a7-9aaa-42f3-82f8-b866db8f0084">
<img width="1183" alt="Screenshot 2024-06-15 at 14 06 00" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/a513f6df-1fca-421b-ae8b-401abc7741cb">
<img width="1190" alt="Screenshot 2024-06-15 at 15 01 45" src="https://github.com/duskfallcrew/Dataset-Tools/assets/58930427/10d386f8-ae21-4672-964c-5d4ebc889275">

