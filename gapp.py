# Semestral project - NPRG030 - 2023/2024 - MFF UK
# Author: David Válek
# Messenger Analytics is a Python application designed to analyze Facebook Messenger chat logs.
# It provides insights such as the number of messages sent by each participant, the most common
# words used, and the moving average of the number of messages over a specified number of days.

try:
    import json
    import os
    import subprocess
    import sys
    import mplcursors
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QApplication, QComboBox, QWidget, QHBoxLayout, QListWidget, QTextEdit, QPushButton, \
        QVBoxLayout
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    from json_core import main as analyse


    class Data:

        def __init__(self):

            try:
                # Your code here
                file = open("Datas_j/data.json", "r", encoding="utf-8")
                self.data = json.load(file)  # If the file exists, load the data from it.
                file.close()
            except FileNotFoundError:
                print("File not found. Running json_handler2.py...")
                self.data = analyse()  # Run the main function from json_core.py -> will create the data.json file

            self.data_participants = {}
            self.participants = []
            self.convs = {}
            self.group_names = []
            self.groups = {}
            self.conv_names = []

        def show_info(self):
            for x in self.data:
                for key, value in x.items():
                    self.data_participants[key] = value
                    self.participants.append(key)

        def filler(self):
            """Function to fill the conversations and groups dictionaries."""
            for name in self.participants[:-1]:
                # exclude the last one, which is directory with general information
                if self.data_participants[name][0] == "2ppl":
                    self.convs[name] = self.data_participants[name]
                    self.conv_names.append(name + " - " + str(self.data_participants[name][2]))
                else:
                    self.groups[name] = self.data_participants[name]
                    self.group_names.append(name + " - " + str(self.data_participants[name][2]))

        def sorter(self):
            """Function to sort the conversations and groups by the number of messages."""

            # Sort list of conversations by number of messages from highest to lowest
            counts = []
            for x in self.conv_names:
                counts.append(int(x.split(" - ")[1]))
            self.conv_names = [x for _, x in sorted(zip(counts, self.conv_names), reverse=True)]

            # Sort list of groups by number of messages from highest to lowest
            counts = []
            for x in self.group_names:
                counts.append(int(x.split(" - ")[1]))
            self.group_names = [x for _, x in sorted(zip(counts, self.group_names), reverse=True)]


    data = Data()
    data.show_info()
    data.filler()
    data.sorter()

    class JsonViewer(QWidget):
        def __init__(self):
            super().__init__()  # Call the parent class constructor.

            self.data = Data()  # Initialize data.
            self.data.show_info()  # Show the data.
            self.data.filler()  # Fill the data.
            self.data.sorter()  # Sort the data.
            self.groups = self.data.group_names  # Get the group names.
            self.conversations = self.data.conv_names  # Get the conversation names.
            self.selected_chat = ""

            self.setWindowIcon(QIcon('addons/mess_icon.ico'))  # Set the window icon.
            self.setWindowTitle('Messenger Analytics')  # Set the window name.

            self.init_ui()  # Call the init_ui method.

            # Set the initial index to "Conversations" in the combo box.
            index = self.comboBox1.findText("Conversations")
            if index >= 0:
                self.comboBox1.setCurrentIndex(index)  # Set the current index to the index of "Conversations".

            self.load_list()  # Call the load_list method.

        def init_ui(self):
            """Initialize the user interface."""

            layout = QVBoxLayout()  # Main layout

            # Horizontal layout for the combo box and the button
            h_layout_top = QHBoxLayout()

            # Combo Box 1
            self.comboBox1 = QComboBox()
            self.comboBox1.addItem("Conversations")
            self.comboBox1.addItem("Groups")
            self.comboBox1.addItem("General")
            self.comboBox1.currentIndexChanged.connect(
                self.load_list)  # Connect the currentIndexChanged signal to the load_list method
            h_layout_top.addWidget(self.comboBox1)  # Add the combo box to the horizontal layout

            # Button next to the combo box
            self.button = QPushButton()
            self.button.setFixedSize(self.comboBox1.sizeHint())  # Set the size of the button to match the combo box
            self.button.clicked.connect(self.button_clicked)  # Connect the clicked signal to the button_clicked method
            # Button color
            self.button.setStyleSheet("background-color: #d000ff; border: 1px solid #f0f0f0; border-radius: 5px;")
            h_layout_top.addWidget(self.button)  # Add the button to the horizontal layout

            # Combo Box 2
            self.comboBox2 = QComboBox()
            self.comboBox2.addItem("*_Sum_*")
            self.comboBox2.addItem("Option 1")  # Will be updated based on the current item in the list widget
            self.comboBox2.addItem("Option 2")  # Will be updated based on the current item in the list widget
            self.comboBox2.currentIndexChanged.connect(
                self.update_graphs)  # Connect the currentIndexChanged signal to the update_graphs method.
            h_layout_top.addWidget(self.comboBox2)  # Add the combo box to the horizontal layout

            # Add the horizontal layout to the main layout
            layout.addLayout(h_layout_top)

            # Horizontal layout for the list widget and the text edit
            h_layout = QHBoxLayout()

            # Left column with scrollbar
            self.file_list_widget = QListWidget()
            # Set the visibility based on the initial selection
            self.file_list_widget.setVisible(self.comboBox1.currentText() != "General")
            self.file_list_widget.itemSelectionChanged.connect(
                self.update_info_text_edit)  # Connect the itemSelectionChanged signal to the update_info_text_edit method
            h_layout.addWidget(self.file_list_widget)  # Add the list widget to the horizontal layout
            self.file_list_widget.itemSelectionChanged.connect(
                self.update_comboboxes)  # Connect the itemSelectionChanged signal to the update_comboboxes method

            # Right space for displaying info
            self.info_text_edit = QTextEdit()
            h_layout.addWidget(self.info_text_edit)

            # Add the horizontal layout to the main layout
            layout.addLayout(h_layout)

            # Right space for displaying info
            self.top_words_bar = QTextEdit()
            h_layout.addWidget(self.top_words_bar)

            # Create a figure object and canvas for the first graph
            fig1 = Figure(figsize=(5, 5), dpi=100)
            self.plot1 = fig1.add_subplot(111)
            self.plot1.plot(([1, 2], [3, 4]))
            self.canvas1 = FigureCanvas(fig1)

            # Create a figure object and canvas for the second graph
            fig2 = Figure(figsize=(5, 5), dpi=100)
            self.plot2 = fig2.add_subplot(111)
            self.plot2.bar([1, 2], [3, 4])
            self.canvas2 = FigureCanvas(fig2)

            # Create a QHBoxLayout object for the charts
            self.chart_layout1 = QHBoxLayout()

            # Add the canvas widgets to the layout
            self.chart_layout1.addWidget(self.canvas1)
            self.chart_layout1.addWidget(self.canvas2)

            # Add the chart layout to the main layout
            layout.addLayout(self.chart_layout1)

            # Horizontal layout for the combo boxes at the bottom
            h_layout_bottom = QHBoxLayout()

            # Add the bottom layout to the main layout
            layout.addLayout(h_layout_bottom)

            # Set the main layout
            self.setLayout(layout)

        def update_top_words(self):
            """Update the top words based on the current item in the list widget and the combo box."""
            self.current_item = self.file_list_widget.currentItem().text().split(" - ")[0]
            current_item_2 = self.comboBox2.currentText()
            data_ = self.data.data_participants[self.current_item]
            result = f"""<p><b>Most common words - {current_item_2}:</b><br> {"<br>".join(f'{key}: {value}' for key, value in data_[7][current_item_2])}</p>"""
            self.top_words_bar.setText(result)

        def update_graphs(self):
            try:
                # Get the current item in the list widget
                self.current_item = self.file_list_widget.currentItem().text().split(" - ")[0]

                current_item_1 = current_item_2 = current_item_3 = self.comboBox2.currentText()

                if current_item_1 in list(
                        self.data.data_participants[self.current_item][5].keys()) and current_item_2 in list(
                    self.data.data_participants[self.current_item][4].keys()):

                    self.update_top_words()

                    # Update the graphs based on the item text
                    self.plot1.clear()
                    self.plot1.plot(self.data.data_participants[self.current_item][5][current_item_1][0],
                                    self.data.data_participants[self.current_item][5][current_item_1][1],
                                    c="forestgreen",
                                    linewidth=0.4)  # Replace with your actual data
                    # Load the setting file
                    setting = open("setting.txt", "r")
                    setting_data = setting.read().splitlines()
                    moving_avarage = int(setting_data[0].split(":")[1])
                    setting.close()

                    # If the moving average is less than the length of the data, plot the moving average, otherwise there would not be enough data points to plot it.
                    if moving_avarage <= (len(self.data.data_participants[self.current_item][6][current_item_1][1])):
                        self.plot1.plot(self.data.data_participants[self.current_item][6][current_item_1][0],
                                        self.data.data_participants[self.current_item][6][current_item_1][1],
                                        c="red",
                                        linewidth=0.8)  # Replace with your actual data

                    self.plot1.set_title("Messages per day")
                    # Grid
                    self.plot1.grid(True)

                    # self.plot1.set_xticks(self.data.data_participants[self.current_item][5][current_item_1][0][::(len(self.data.data_participants[self.current_item][5][current_item_1][0])) // 2])
                    xticks_indices = [0] + [
                        int(len(self.data.data_participants[self.current_item][5][current_item_1][0]) * n) for n in
                        [1 / 4, 2 / 4, 3 / 4]] + [len(self.data.data_participants[self.current_item][5][current_item_1][0]) - 1]
                    xticks_labels = [self.data.data_participants[self.current_item][5][current_item_1][0][i] for i in
                                     xticks_indices]
                    self.plot1.set_xticks(xticks_indices, xticks_labels)
                    self.canvas1.draw()

                    # Add cursor to the plot
                    mplcursors.cursor(self.plot1)

                    self.plot2.clear()
                    self.plot2.bar(self.data.data_participants[self.current_item][4][current_item_2][0],
                                   self.data.data_participants[self.current_item][4][current_item_2][
                                       1])  # Replace with your actual data
                    self.plot2.set_title("Hour activity")
                    self.plot2.set_xticks(self.data.data_participants[self.current_item][4][current_item_2][0][::1])
                    for i, value in enumerate(self.data.data_participants[self.current_item][4][current_item_2][1]):
                        self.plot2.text(self.data.data_participants[self.current_item][4][current_item_2][0][i], value,
                                        str(value), ha='center', va='bottom', fontsize=7)

                    self.canvas2.draw()

                    # Add cursor to the plot
                    mplcursors.cursor(self.plot1)

            except:
                pass

        def update_comboboxes(self):
            try:
                # Get the current item in the list widget.
                current_item = self.file_list_widget.currentItem()
                if current_item:
                    item_text = current_item.text()

                    # Update the combo boxes based on the item text
                    # This is just an example, replace it with your actual logic

                    self.comboBox2.clear()
                    self.comboBox2.addItems(list(self.data.data_participants[item_text.split(" - ")[0]][4].keys()))
            except:
                pass

        def update_info_text_edit(self):
            """Update the QTextEdit with the data associated with the current item in the list widget."""
            current_item = self.file_list_widget.currentItem()
            if current_item:
                item_text = current_item.text()  # Item text is the name of the file
                # Get the data associated with the item
                self.selected_chat = item_text.split(" - ")[0]
                item_data = self.get_item_data(item_text)
                # Update the QTextEdit with the item data
                self.info_text_edit.setText(item_data)

        def get_item_data(self, item_text):
            """Information about the selected chat."""
            try:
                # Replace this with the actual code that retrieves the data
                self.selected_chat = item_text.split(" - ")[0]
                data_ = self.data.data_participants[item_text.split(" - ")[0]]

                return f"""
                            <h2>Chat name: {item_text.split(" - ")[0]}</h2>
                            <p><b>Number of participants:</b> {len(data_[1])} = {", ".join(data_[1])}</p>
                            <p><b>Number of messages:</b> {data_[2]}</p>
        <p><b>Number of messages from each participant:</b><br> {"<br>".join(f'{key}: {value}' for key, value in data_[3].items())}</p>
                            """
            except:
                pass

        def button_clicked(self):
            """Button click event handler. Runs the json_core.py script and reloads the data."""
            self.delete_files()
            subprocess.call("python json_core.py", shell=False)
            self.reload_data()

        def delete_files(self):
            """Delete all files in the Datas_j folder."""
            folder_path = 'Datas_j'

            # Get the list of files in the folder
            files = os.listdir(folder_path)

            # Iterate through the files and delete each one
            for file in files:
                file_path = os.path.join(folder_path, file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

        def reload_data(self):
            """Reload the data from the data.json file."""
            self.data = Data()
            self.data.show_info()
            self.data.filler()
            self.data.sorter()
            self.groups = self.data.group_names
            self.conversations = self.data.conv_names
            self.load_list()

        def load_list(self):
            """Load the list widget based on the current selection in the combo box."""
            current_option = self.comboBox1.currentText()
            # Remember the currently selected items in the combo boxes
            current_item_2 = self.comboBox2.currentText()
            self.file_list_widget.clear()  # Clear the list widget
            self.info_text_edit.clear()  # Clear the text edit widget

            if current_option == "General":
                self.file_list_widget.setVisible(False)  # Hide the list widget
                self.comboBox2.setVisible(False)  # Hide the second combo box
                self.top_words_bar.setVisible(False)  # Hide the second combo box

                # Display general data if the "General" option is selected.
                general_data = self.data.data_participants["*-General-*"]

                general_dispay = f"""
                                    <h2>General Data</h2>
                                    <p><b>Number of sent messages:</b> {self.data.data_participants["*-General-*"]["sent"]}</p>
                                    <p><b>Number of received messages:</b> {self.data.data_participants["*-General-*"]["received"]}</p>
                                    <p><b>Number of all messages:</b> {self.data.data_participants["*-General-*"]["received"] + self.data.data_participants["*-General-*"]["sent"]}</p>
                                    """

                self.info_text_edit.setText(
                    general_dispay)  # Set the text of the info_text_edit widget to general_dispay
                self.update_graphs_general()  # Update the graphs with general data.
            else:
                # If the "Conversations" or "Groups" option is selected.
                self.file_list_widget.setVisible(True)  # Show the list widget
                self.comboBox2.setVisible(True)  # Hide the second combo box
                self.top_words_bar.setVisible(True)  # the second combo box

                for i in range(self.chart_layout1.count()):  # Show all widgets in chart_layout1

                    self.chart_layout1.itemAt(i).widget().setVisible(True)

                if current_option == "Conversations":

                    self.load_conversations()

                elif current_option == "Groups":

                    self.load_groups()

                # Select the first item in the list widget

                self.file_list_widget.setCurrentRow(0)

            # Restore the selected items in the combo boxes
            index2 = self.comboBox2.findText(current_item_2)
            if index2 >= 0:
                self.comboBox2.setCurrentIndex(index2)

        def load_conversations(self):
            """Function to load the conversations into the list widget."""
            self.file_list_widget.clear()
            _conversations = self.conversations
            self.file_list_widget.addItems(_conversations)

        def update_graphs_general(self):
            """Function to update the graphs with general data."""
            data_1 = self.data.data_participants["*-General-*"]["dates"]
            data_2 = list(self.data.data_participants["*-General-*"]["hours"].values())

            self.plot1.clear()  # Clear the plot
            self.plot1.plot(data_1[0], data_1[1], c="forestgreen",
                            linewidth=0.4)  # consistent styling with update_graphs
            self.plot1.set_title("Messages per day")
            xticks_indices = [0] + [int(len(data_1[0]) * n) for n in [1 / 4, 2 / 4, 3 / 4]] + [
                len(data_1[0]) - 1]  # consistent xticks with update_graphs
            xticks_labels = [data_1[0][i] for i in xticks_indices]
            self.plot1.set_xticks(xticks_indices, xticks_labels)

            # Load the setting file
            setting = open("setting.txt", "r")
            setting_data = setting.read().splitlines()
            moving_avarage = int(setting_data[0].split(":")[1])
            setting.close()

            # If the moving average is less than the length of the data, plot the moving average, otherwise there would not be enough data points to plot it.
            if moving_avarage <= (len(self.data.data_participants["*-General-*"]["moving_average"][1])):
                self.plot1.plot(self.data.data_participants["*-General-*"]["moving_average"][0],
                                self.data.data_participants["*-General-*"]["moving_average"][1],
                                c="red",
                                linewidth=0.8)  # Replace with your actual data
            self.plot1.grid(True)
            self.canvas1.draw()

            self.plot2.clear()
            self.plot2.bar(data_2[0], data_2[1])  # consistent styling with update_graphs
            self.plot2.set_title("Hour activity")
            self.plot2.set_xticks(data_2[0][::1])  # consistent xticks with update_graphs
            for i, value in enumerate(data_2[1]):
                self.plot2.text(data_2[0][i], value, str(value), ha='center', va='bottom',
                                fontsize=7)  # consistent text with update_graphs
            self.canvas2.draw()

            mplcursors.cursor(self.plot1)  # consistent cursor with update_graphs

        def load_groups(self):
            """Function to load the groups into the list widget."""
            self.file_list_widget.clear()
            _groups = self.groups
            self.file_list_widget.addItems(_groups)

        def print_data(self):
            """Print the data."""
            print(self.data.data_participants.keys())


    if __name__ == '__main__':
        # Create the application
        app = QApplication(sys.argv)  # Create an instance of QApplication
        viewer = JsonViewer()  # Create an instance of the main window
        viewer.showMaximized()  # Show the window maximized
        sys.exit(app.exec())  # Start the event loop

except Exception as e:
    print(e)
    input("Press Enter to exit...")
    exit()
