from PyQt5.QtWidgets import QApplication, QFileDialog
import os


def folder_path_pyqt() -> str:
    """Returns the path to the selected directory using PyQt5 file manager window."""
    app = QApplication([])
    folder_path = QFileDialog.getExistingDirectory(None, "Select Folder")
    return folder_path


def find_chats(path):
    """Returns a list of addresses where json chatlogs are located."""
    current_directory = os.listdir(path)
    chat_adresses = []

    # Searches for folders with chatlogs and adds them to the list.
    for folder in current_directory:
        if "your_activity" in folder:
            path = path + "/" + folder
            current_directory = os.listdir(path)
            for folder in current_directory:
                if "messages" in folder:
                    path = path + "/" + folder
                    current_directory = os.listdir(path)
                    for folder in current_directory:
                        # Facebook chatlogs are located in different folders, so we need to search for them in different places.
                        if "archived" in folder:
                            path1 = path + "/" + folder
                            chat_logs = (os.listdir(path1))
                            for log in chat_logs:
                                chat_adresses.append(path1 + "/" + log)
                        if "inbox" in str(folder):
                            path2 = path + "/" + folder
                            chat_logs = (os.listdir(path2))
                            for log in chat_logs:
                                chat_adresses.append(path2 + "/" + log)
                        if "e2ee_cutover" in str(folder):
                            path3 = path + "/" + folder
                            chat_logs = (os.listdir(path3))
                            for log in chat_logs:
                                chat_adresses.append(path3 + "/" + log)
            break
    if len(chat_adresses) == 0:
        raise FileNotFoundError("No chatlogs found. Run the program again and select the correct folder.")
    return chat_adresses


def json_sequator(chat_adresses: list) -> dict:
    """Returns dictionary with names of people and their chatlogs. Searches for json files in the given list of addresses from find_chats()."""
    all_adresses = {}
    for x in range(0, len(chat_adresses)):
        json_adrss = []
        for y in os.listdir(chat_adresses[x]):
            if ".json" in y:
                messager_name = chat_adresses[x].split("/")[-1]
                if chat_adresses[x] + "/" + y not in json_adrss:
                    print(chat_adresses[x] + "/" + y)
                    json_adrss.append(chat_adresses[x] + "/" + y)
        all_adresses[messager_name] = json_adrss
    return all_adresses


def json_addresses():
    """ Main function that returns a dictionary where the key is the name of the person leading the chat and the value
    is a list of addresses of json chatlogs. A .txt file with settings is also created."""
    try:
        adrress = folder_path_pyqt()
        chat_adresses = find_chats(adrress)
        print(chat_adresses)
        json_adrressess = (json_sequator(chat_adresses))
        # if setting.txt does not exist, it is created.
        if not os.path.exists("setting.txt"):
            setting = open("setting.txt", "w")
            setting.write("moving_average: 30\ntop_words: 50\ntop_words_minimal_len: 1")
            setting.close()

        return json_adrressess
    except Exception as e:
        print(e)
        input("Press enter to exit.")
        exit()


if __name__ == "__main__":
    json_addresses()
