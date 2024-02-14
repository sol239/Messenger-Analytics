1. **Messenger Analytics User   Documentation**

    **Introduction:**

    - Messenger Analytics is a Python application that analyzes Facebook Messenger chat logs. It provides insights such as the number of messages sent by each participant, the most common words used, and the moving average of the number of messages over a specified number of days.

    **Requirements:**

    - Python 3.7 or higher
    - PyQt5
    - Matplotlib
    - mplcursors

    **Installation:**

    - pip install PyQt5 matplotlib mplcursors

    **Usage:**

    1. Run the gapp.py script to start the application
    2. The application will prompt you to select a directory containing your Facebook Messenger chat logs in JSON format. The folder you should select is the extraxted folder you downloaded from: https://accountscenter.facebook.com/info_and_permissions
    3. Once the directory is selected, the application will analyze the chat logs and display the results in a user-friendly interface.


    - The top left combobox allows you to choose between two people conversations, groups and general data tab. The top middle button allows you to start the new analysis. The top right combobox allows you to choose whose data you want to show. The asterisk underscore Sum underscore asterisk tag represents data of all participants combined.
    - The left column shows chatlogs with their number of messages, sorted, the middle column shows acquired informations about the selected chatlog, the right column shows the most common words, sorted.
    - The left graph shows number of messages per date, the green line represents the exact number of messages on given day and the red line represents moving avarage of given range. The right graphs shows number of messages per hour.
    - Result of the analysis will be stored in Datas_j folder, which will be created by the program. The next time you run the gapp.py it will open the last analysis.
    - If you want to choose different folder, you can click on purple button at top of UI or delete Datas_j folder, or content of the folder.
    - You can change some of anylysis settings in setting.txt.  In case you change the setting.txt and want to see new data, you have the start new analysis, either by deleting Datas_j folder or clicking on megenta button at top of UI. 
    - - moving_average: 30		# you can change the value to change lenght of MA window
    - - top_words: 300			# you can change the value to see different number of top words.
    - - top_words_minimal_len: 5	# you can change the value to set words which will contribute to top words.
    - You can download your data here: https://accountscenter.facebook.com/info_and_permissions. Select specific type of informations. Select messages. Select data for a specific date range or for your entire Facebook history, and choose the JSON format. After downloading and extracting the .zip file, select the extracted folder (which should be in JSON format) in gapp.py.
    - The asterisk underscore Sum underscore asterisk tag represents data from all participants. The name of the tag was selected intentionally to be not mismatched with name of participant.
    - If you want to reset settings, delete Datas_j folder and setting.txt file.
    - If you click on purple button and not select some folder with data, the program will crash.

    **Features:**

    - Conversations and Groups: You can choose to view data for individual conversations or group chats. Select the desired option from the first dropdown menu.
    Chat Selection: Once you've chosen to view either Conversations or Groups, a list of available chats will be displayed. Click on a chat to view its analytics.

    - Participant Selection: After selecting a chat, you can choose to view data for individual participants. Select the desired participant from the second dropdown menu.

    - Message Count: The application displays the total number of messages sent by each participant.

    - Most Common Words: The application displays the most common words used by each participant, along with their frequency.

    - Moving Average of Messages: The application calculates and displays the moving average of the number of messages sent over a specified number of days.
    Graphs: The application provides two graphs. The first graph shows the number of messages sent per day. The second graph shows the activity of the chat participants by hour.
    - General Data Tab: The application calculates all your sent and received messages across your all chat logs excluding groupchats. Graphs in General Data tab show just your activity -> analysis just of messages you sent.
    
    **Support:**

    - If you need help with the program, you can reach me: david.valek17@gmail.com

    **License:**

    GNU GENERAL PUBLIC LICENSE
    Version 3, 29 June 2007

    Copyright (C) 2024 David Válek

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

    **Disclaimer:**

    - This application is intended for personal use only. Please respect the privacy of others and do not use this tool to analyze chat logs without the consent of all participants. This application does not send you data anywhere. 

    **Project Status:**

    - For now, I consider the program finished. I am not planning to update the program anytime soon.

1. **Messenger Analytics Technical Documentation**

    **Overview**:

    - Messenger Analytics is a Python application designed to analyze Facebook Messenger chat logs. It provides insights such as the number of messages sent by each participant, the most common words used, and the moving average of the number of messages over a specified number of days.
    - The functioning of the program is further documented through comments in the source code.
    - The app uses PyQt5 for its GUI, Matplotlib for plotting graphs and mplcursors for graph cursors.

    **Modules**:

    <details><summary>json_address_handler.py
    </summary>
    This module is responsible for handling the addresses of JSON files. It contains functions to select a directory using PyQt5 file manager window, find chat addresses, and sequence JSON addresses.
    </details>
    
    <details><summary>json_core.py
    </summary>
    This module contains the core classes and functions for handling and analyzing JSON files. It includes classes for handling JSON files (JsonFile), repairing JSON files (JsonHandler), analyzing JSON files (JsonAnalytics), and storing general data (GeneralData). It also includes functions for storing data to a JSON file (store_data), creating a directory (make_dir), deleting files (delete_files), and the main function (main) that takes care of the entire analysis.  
    </details>

    <details><summary>gapp.py</summary>
    This module is the main application module. It contains the Data class for handling data and the JsonViewer class for the user interface. The JsonViewer class includes methods for initializing the user interface, updating the information displayed, loading the list widget based on the current selection in the combo box, and handling button click events.
    </details>
  
