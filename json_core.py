import json
from datetime import datetime, timedelta
import string
import collections
import os

from json_address_handler import json_addresses


class JsonHandler():
    """Class that takes care of json file repair. Fixes diacritics and formatting.
    The argument is a dictionary that is in json_address_handler.py."""

    def __init__(self, json_dict):
        self.data = json_dict

    def print_participants(self):
        """Prints all chat participants."""
        for participant in self.data["participants"]:
            print(participant["name"])

    def print_messages(self):
        """Prints all messages."""
        for message in self.data["messages"]:
            print(message)

    def repair_names(self):
        """Function that fixes diacritics in participant names. Fixes Facebook encoding."""
        repaired_names = []
        for participant in (self.data["participants"]):
            text = participant["name"]
            corrected_text = text.encode('latin-1').decode('utf-8')
            repaired_names.append({"name": corrected_text})
        self.data["participants"] = repaired_names

    def repair_title(self):
        """Function that fixes diacritics in the chat title."""
        self.data["title"] = self.data["title"].encode('latin-1').decode('utf-8')

    def repair_messages(self):
        """Function that fixes diacritics in the content of individual messages. And also fixes the message timestamp."""

        for message in self.data["messages"]:
            # message is a dict
            # {sender_name : str, content : str, reaction : list[{reaction : str, actor : str}]} These three keys and values will need to be fixed.

            # fixes the sender name of the message
            if "sender_name" in message:
                message["sender_name"] = message["sender_name"].encode('latin-1').decode('utf-8')

            # fixes the content of the message
            if "content" in message:
                message["content"] = message["content"].encode('latin-1').decode('utf-8')

            # fixes the reactions to the message
            if "reactions" in message:
                reaction_list = []
                for reaction in (message["reactions"]):
                    reaction["actor"] = reaction["actor"].encode('latin-1').decode('utf-8')
                    reaction["reaction"] = reaction["reaction"].encode('latin-1').decode('utf-8')
                    reaction_list.append(reaction)
                message["reactions"] = reaction_list

            # fixes the message timestamp, so it matches the format "Y-m-d H:M:S"
            if "timestamp_ms" in message:
                message["timestamp_ms"] = datetime.fromtimestamp(message["timestamp_ms"] / 1000.0).strftime(
                    "%Y-%m-%d %H:%M:%S")


class JsonFile:
    """Class that takes care of loading json files. The argument is a list of json file addresses.
    Combines multiple logs into single one."""

    def __init__(self, json_address_list):
        self.json_address_list = json_address_list

    def load_json(self):
        """If the json chat is very long, Facebook will divide it into several parts. This function is able to load all parts and combine them into one dictionary."""
        dictionary_combined = {}
        dictionary_combined["messages"] = []
        for json_filename in self.json_address_list:
            file = open(json_filename, "r")
            file = json.load(file)

            dictionary_combined["participants"] = file["participants"]
            dictionary_combined["title"] = file["title"]
            dictionary_combined["messages"].extend(file["messages"])

        return dictionary_combined


class JsonAnalytics:
    """Class that takes care of chatlog analysis. The argument is a dictionary, which is the result of the JsonFile class and its load_json() method."""

    def __init__(self, prepared_data):
        self.data = prepared_data  # corrected data from JsonFile class
        self.dates_1 = []  # list that will contain the message date in the format: year-month-day
        self.dates_2 = []  # list that will contain the message hour in the format: hour-minute-second
        self.all_days = []
        self.day_counts = {}  # dictionary which will contain counts of words
        for name in self.data["participants"]:
            self.day_counts[name["name"]] = []

        self.day_counts_graph = {}
        self.day_counts_graph["*_Sum_*"] = []

        for name in self.data["participants"]:
            self.day_counts_graph[name["name"]] = []

        self.hour_counts = {}  # dictionary which will contain counts of words
        for name in self.data["participants"]:
            self.hour_counts[name["name"]] = []

        self.hour_counts_graph = {}
        self.hour_counts_graph["*_Sum_*"] = []

        for name in self.data["participants"]:
            self.hour_counts_graph[name["name"]] = []

        self.dates_1_all = []
        self.dates_2_all = []

        self.ma_values = {}
        for name in self.data["participants"]:
            self.ma_values[name["name"]] = []

        self.counts = {}  # dictionary, which as keys will contain the names of chat participants and as values the number of messages.
        for name in self.data["participants"]:
            self.counts[name["name"]] = 0

        self.top_words = {}  # dictionary, which will contain word:count of words sorted by count of words
        self.top_words["*_Sum_*"] = []
        for name in self.data["participants"]:
            self.top_words[name[
                "name"]] = []  # The keys will be the names of chat participants and the values will be lists of words,
            # which will be sorted by the number of occurrences. And also the total sum.

        self.stored_data = {}

    def chat_type(self) -> str:
        """Function, whether it is a group chat or a chat between two people. Returns a string."""

        # If the number of participants is equal to 2, it is a chat between two people.
        if len(self.counts.values()) == 2:
            return "2ppl"

        # Otherwise, it is a group chat.
        else:
            return "grp"

    def count_messages(self):
        """Function that counts the number of messages from individual chat participants. The result sorted in descending order is stored in a dictionary."""

        # Gradually goes through message by message.
        for message in self.data["messages"]:

            try:
                # if the sender name of the message is in counts, its value is increased by 1.
                self.counts[message["sender_name"]] += 1

            except KeyError:
                # if sender_name is not in counts, it is added and will have a value of 1. This can happen,
                # if someone leaves the group, the person will not be in participants, but his messages will be in messages.
                # it must be handled.
                # alternatively, it could be handled by adding a person to participants, but that would be unnecessary.
                self.counts[message["sender_name"]] = 1

        # Sorts the dictionary in descending order by values and stores in self.counts.
        self.counts = dict(sorted(self.counts.items(), key=lambda item: item[1], reverse=True))

    def store_data(self):
        """Function that stores the results of the analysis in a dictionary. self.stored_data will be used as input data for the GeneralData class."""
        self.stored_data = {self.data["title"]: [self.chat_type(),
                                                 [name["name"] for name in self.data["participants"]],
                                                 sum(self.counts.values()),
                                                 self.counts,
                                                 self.hour_counts_graph,
                                                 self.day_counts_graph,
                                                 self.ma_values,
                                                 self.top_words]}
        # {"chatlog name:[
        # [0] = chat_type
        # [1] = participants
        # [2] = total_messages
        # [3] = counts:
        # [4] = hour_counts_graph: [name: [hours, counts]]
        # [5] = day_counts_graph: [name: [dates, counts]]
        # [6] = top_words: [name: [word, count]]
        # ]}

    def dates(self):
        """Function that returns dictionaries with dates, where the key is the participant's name and the value is
        a list where the first element is a list of dates and the second element is a list of the number of messages."""
        for message in self.data["messages"]:
            try:

                self.day_counts[message["sender_name"]].append(
                    message["timestamp_ms"].split()[0])  # Adds Year-Month-Day to the list.
                self.hour_counts[message["sender_name"]].append(
                    int(message["timestamp_ms"].split()[1].split(":")[0]))  # Adds Hour-Minute-Second to the list.
                self.dates_1_all.insert(0, message["timestamp_ms"].split()[
                    0])  # Adds Year-Month-Day to the list of all dates.
                self.dates_2_all.insert(0, int(message["timestamp_ms"].split()[1].split(":")[
                                                   0]))  # Adds Hour-Minute-Second to the list of all dates.

            except KeyError:
                # If the sender's name is not in participants, it adds it to the dictionary as a key and the value is a list with the date.
                self.day_counts[message["sender_name"]] = [message["timestamp_ms"].split()[0]]
                self.hour_counts[message["sender_name"]] = [int(message["timestamp_ms"].split()[1].split(":")[0])]
                self.dates_1_all.insert(0, message["timestamp_ms"].split()[0])
                self.dates_2_all.insert(0, int(message["timestamp_ms"].split()[1].split(":")[0]))

        # Sorts the lists with dates and hours for each chat participant chronologically.
        for participant in self.data["participants"]:
            participant = participant["name"]
            self.day_counts[participant] = sorted(self.day_counts[participant])

        self.dates_1_all = sorted(self.dates_1_all)  # Sorts the list of all dates chronologically.
        start_date = self.data["messages"][-1]["timestamp_ms"].split()[0]  # The first date in the chatlog.
        end_date = datetime.now().strftime('%Y-%m-%d')  # The last date in the chatlog.

        def date_adder(start: str, end: str):
            """Function that returns a list of all dates between two dates."""
            start = datetime.strptime(start, "%Y-%m-%d")
            end = datetime.strptime(end, "%Y-%m-%d")
            date_array = (start + timedelta(days=x) for x in range(0, (end - start).days + 1))
            return [date.strftime("%Y-%m-%d") for date in date_array]

        self.all_days = date_adder(start_date,
                                   end_date)  # list of all dates between the first and last date in the chatlog.
        all_hours = [_ for _ in range(00, 24)]  # list of all hours... 0 - 23
        for participant, days in self.day_counts.items():
            messages_per_day = []

            # Counts the number of messages for each day.
            for time in self.all_days:
                messages_per_day.append(days.count(
                    time))  # For each day, it counts the number of messages on that day and adds to the list.
            try:
                # Storing in a dictionary where the key is the participant's name and the value is a list where the first element is a list of dates and the second element is a list of the number of messages on individual days.
                self.day_counts_graph[participant].append(self.all_days)
                self.day_counts_graph[participant].append(messages_per_day)
            except KeyError:
                # If the participant's name is not in participants, it adds it to the dictionary as a key and the value is a list with dates and the number of messages.
                self.day_counts_graph[participant] = [self.all_days, messages_per_day]

        messages_per_day = []
        for time in self.all_days:
            messages_per_day.append(self.dates_1_all.count(
                time))  # Counts the number of messages for each day regardless of the chat participant. Will be used for GeneralData.

        self.day_counts_graph["*_Sum_*"] = [self.all_days,
                                            messages_per_day]  # Stores in a dictionary where the key is *_Sum_* and the value is a list [dates, counts of messages on individual dates].
        del messages_per_day

        # The same procedure as for dates, but for hours.
        for participant, hours in self.hour_counts.items():

            hours_per_day = []

            for time in all_hours:
                hours_per_day.append(hours.count(time))

            try:
                self.hour_counts_graph[participant].append(all_hours)
                self.hour_counts_graph[participant].append(hours_per_day)
            except KeyError:
                self.hour_counts_graph[participant] = [all_hours, hours_per_day]

        hours_per_day = []
        for time in all_hours:
            hours_per_day.append(self.dates_2_all.count(time))

        self.hour_counts_graph["*_Sum_*"] = [all_hours, hours_per_day]
        del hours_per_day

    def most_words(self, n: int, length: int):
        """Returns a dictionary where the key is the name of the chat participant and the value is a list of words that are sorted by the number of occurrences.
            n  = is the number of characters that a word must have to be included in the list.
            length = is the number of words that will be displayed."""
        translator = str.maketrans('', '', string.punctuation)

        for message in self.data["messages"]:
            if "content" in message:
                for content_of_message in message["content"].split():
                    content_of_message = content_of_message.translate(
                        translator).lower()  # Removes punctuation and converts to lowercase.
                    # Filter for words that are longer than n characters and do not contain a link.
                    try:
                        if len(content_of_message) >= n and "http" not in content_of_message and "www" not in content_of_message:
                            self.top_words[message["sender_name"]].append(content_of_message)
                            self.top_words["*_Sum_*"].append(content_of_message)
                    except KeyError:
                        # If the sender's name is not in participants, it adds it to the dictionary as a key and the value is a list with words.
                        if len(content_of_message) >= n and "http" not in content_of_message and "www" not in content_of_message:
                            self.top_words[message["sender_name"]] = [content_of_message]
                            self.top_words["*_Sum_*"].append(content_of_message)

        # Sorts words by amount of word and write count of word to dictionary, sorted.
        for participant, words in self.top_words.items():
            word_counts = collections.Counter(words)  # Spočítá počet výskytů slov.
            self.top_words[participant] = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[
                                          0:length]  # [0:length] = number of words that will be displayed.

    def moving_avarage(self, n=30):
        """Function that calculates the moving average of the number of messages for n days. The result is stored in a dictionary
         where the key is the name of the chat participant and the value is a list of dates and the number of messages."""
        for name, counts in self.day_counts_graph.items():
            dates = counts[0]
            values = counts[1]

            ma_dates_ = []
            ma_values_ = []

            ma_dates_.extend(dates[0:n - 1])
            ma_values_.extend([0] * (n - 1))
            x = 0
            y = n - 1

            # Calculates the moving average and stores it in a dictionary where the key is the name of the chat participant and the value is a list of dates and the number of messages.
            while y < len(values):
                ma_values_.append(sum(values[x:y + 1]) / len(values[x:y + 1]))
                ma_dates_.append(dates[y])

                # Moving the window by one day.
                x += 1
                y += 1

            self.ma_values[name] = [ma_dates_, ma_values_]  # Uloží data do slovníku

    # My version of most_words function, which is not working as fast as it the one above.

    # def most_words(self, n):
    #     """Returns dictionary with names of participants as keys and list of top words and their counts as values."""
    #
    #     for message in self.data["messages"]:
    #         if "content" in message:
    #             for content_of_message in message["content"].split():
    #                 while ("." or "," or "!" or "?" or ":" or ";" or "(" or ")" or '"' or "'" or "“" or "”" or "’" or "‘") in content_of_message:
    #                     content_of_message = content_of_message.replace("." or "," or "!" or "?" or ":" or ";" or "(" or ")" or '"' or "'" or "“" or "”" or "’" or "‘", "")
    #
    #                 content_of_message = content_of_message.lower()
    #
    #                 try:

    #                     self.top_words[message["sender_name"]].append(content_of_message)
    #                 except KeyError:
    #                     self.top_words[message["sender_name"]] = [content_of_message]
    #
    #     # Sort words by amount of word and write count of word to dictionary, sorted
    #     count = []
    #     words_1 = []
    #     for participant, words in self.top_words.items():
    #         for word in words:
    #             count.append(words.count(word))
    #             words_1.append(word)
    #         self.top_words[participant] = sorted(zip(count, words_1), reverse=True)
    #         count.clear()
    #         words_1.clear()


class GeneralData:
    def __init__(self):

        self.file = open("Datas_j/data.json", "r", encoding="utf-8")  # Opens the file with the results of the analysis.
        self.data = json.load(self.file)  # Loads the file with the results of the analysis.
        self.me = "Undjsfě2384JWFJDKcn"  # Random string, which will be replaced by the name of the chat participant.
        self.me = self.identify()  # Calls the identify function, which tries to identify the name of the chat participant.
        self.sent = 0  # Number of messages you sent.
        self.received = 0  # Number of messages you received.

        self.all_dates = {}
        self.all_dates["dates"] = []
        self.all_dates["counts"] = []

        self.all_hours = {}
        self.all_hours["hours"] = []
        self.all_hours["counts"] = []

        self.stats = {}

    def identify(self) -> str:
        """Function wich will try to identify your name"""

        all_names = []
        all_counts = {}

        for log_data in self.data:
            for key, value in log_data.items():
                for name in value[1]:
                    all_names.append(name)

        # Counts the number of occurrences of each name.
        for name in all_names:
            if name in all_counts:
                all_counts[name] += 1
            else:
                all_counts[name] = 1

        # key, value with max value
        return max(all_counts, key=all_counts.get)

    def collect_data(self, include_groups=False):
        """Function that collects data from all chatlogs and stores them in a dictionary. If include_groups is False,
        it will only collect data from chatlogs between two people. If include_groups is True, it will collect data from all chatlogs,
        but this setting is not currently supported.
        These data will be used for the GeneralData Tab."""
        for log_data in self.data:
            for key, value in log_data.items():
                if include_groups == False:
                    if value[0] == "2ppl":
                        self.sent += value[3][self.me]

                        for name, count in value[3].items():
                            if name != self.me and name != "*_Sum_*":
                                self.received += count

                        me = self.identify()
                        self.all_hours["hours"] = (value[4][me][0])  # Adds hours to the list.
                        self.all_hours["counts"].append(value[4][me][1])  # Adds the number of messages to the list.
                        self.all_dates["dates"].extend(value[5][me][0])  # Adds dates to the list.
                        self.all_dates["counts"].extend(value[5][me][1])  # Adds the number of messages to the list.

                else:
                    for name, count in value[3].items():
                        if name == self.me:
                            self.sent += count
                        if name != "*_Sum_*" and name != self.me:
                            self.received += count

        # Sums the number of messages for each hour. Will be used for General Data tab.
        lists = [f for f in self.all_hours["counts"]]
        result = []
        for x in range(0, 24):
            val = 0
            for y in lists:
                val += y[x]
            result.append(val)
        self.all_hours["counts"] = result

        # Sums the number of messages for each day. Will be used for General Data tab.
        result_dates = {}

        for x in range(0, len(self.all_dates["dates"])):
            result_dates[self.all_dates["dates"][x]] = 0

        for x in range(0, len(self.all_dates["dates"])):
            result_dates[self.all_dates["dates"][x]] += self.all_dates["counts"][x]

        # Sorts the dictionary by date.
        days = sorted(list(result_dates.keys()))

        # Creates a list of all dates between the first and last date in the chatlog.
        start_date = days[0]
        end_date = datetime.now().strftime('%Y-%m-%d')

        def date_adder(start, end):

            start = datetime.strptime(start, "%Y-%m-%d")
            end = datetime.strptime(end, "%Y-%m-%d")
            date_array = (start + timedelta(days=x) for x in range(0, (end - start).days + 1))
            return [date.strftime("%Y-%m-%d") for date in date_array]

        days = date_adder(start_date, end_date)

        result_dates_1 = days  # list of all dates between the first and last date in the chatlog.
        result_dates_2 = [0] * len(days)  # list with counts of messages for each day.

        # Adds the number of messages to the list.
        for day, count in result_dates.items():
            if day in result_dates_1:
                result_dates_2[result_dates_1.index(day)] = count

        # Stores the results in a dictionary.
        self.all_dates = [result_dates_1, result_dates_2]

        # Stores the results in a dictionary. These data will be used for the GeneralData Tab.
        self.stats = {"sent": self.sent, "received": self.received, "hours": self.all_hours, "dates": self.all_dates}

    def moving_avarage(self, n=30):

        """Function that calculates the moving average of the number of messages for n days. The result is stored in a dictionary."""

        dates_1 = self.stats["dates"][0]
        counts_1 = self.stats["dates"][1]

        dates = dates_1
        values = counts_1
        ma_dates_ = []
        ma_values_ = []

        ma_dates_.extend(dates[0:n - 1])
        ma_values_.extend([0] * (n - 1))
        x = 0
        y = n - 1

        while y < len(values):
            ma_values_.append(sum(values[x:y + 1]) / len(values[x:y + 1]))
            ma_dates_.append(dates[y])

            x += 1
            y += 1

        self.stats["moving_average"] = [ma_dates_, ma_values_]

    def save_data(self):
        """Function that stores the results of the analysis in a json file."""
        self.data.append({"*-General-*": self.stats})
        store_data(self.data)


def store_data(data):
    """Function which stores data to json file"""

    file = open("Datas_j/data.json", "w", encoding="utf-8")

    data = json.dumps(data)
    file.write(data)
    file.close()


def make_dir(name):
    import os

    # Specify the name of the directory you want to create
    directory_name = name

    # Get the current working directory
    current_directory = os.getcwd()

    # Combine the current working directory with the new directory name
    new_directory_path = os.path.join(current_directory, directory_name)

    # Check if the directory already exists
    if not os.path.exists(new_directory_path):
        # Create the directory
        os.mkdir(new_directory_path)
        print(f"Directory '{directory_name}' created successfully.")
    else:
        print(f"Directory '{directory_name}' already exists.")


def delete_files():
    """Function that deletes all files in the folder."""
    folder_path = 'Datas_j'

    # Get the list of files in the folder
    files = os.listdir(folder_path)

    # Iterate through the files and delete each one
    for file in files:
        file_path = os.path.join(folder_path, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                # print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


def main():
    """Main function that takes care of the entire analysis. It returns the results of the analysis."""

    json_data = []
    make_dir(
        "Datas_j")  # Creates a folder where the results of the analysis will be stored if it does not exist, otherwise it does nothing.
    delete_files()  # Deletes all files in the folder.
    json_dictionary = json_addresses()  # Returns a dictionary where the key is the name of the chatlog and the
    # value is a list of addresses of json chatlogs.

    # Reads the settings from the file.
    setting = open("setting.txt", "r")
    setting_data = setting.read().splitlines()
    moving_avarage_window = int(setting_data[0].split(":")[1])
    top_words = int(setting_data[1].split(":")[1])
    minimal_len = int(setting_data[2].split(":")[1])
    setting.close()

    # For each chatlog, it floads the json file, repairs it, analyzes it and stores the results in a list.
    for log_name, addr_list in json_dictionary.items():
        a = JsonFile(addr_list)  # Creates an instance of the JsonFile class.
        json_dict = a.load_json()  # Loads the json file and combines it into one dictionary.

        b = JsonHandler(json_dict)  # Creates an instance of the JsonHandler class.
        b.repair_messages()  # Repairs messages in the dictionary.
        b.repair_names()  # Repairs names in the dictionary.
        b.repair_title()  # Repairs title in the dictionary.

        c = JsonAnalytics(b.data)  # Creates an instance of the JsonAnalytics class.
        c.count_messages()  # Counts the number of messages from individual chat participants.
        c.dates()  # Analyzes the dates of messages.
        c.most_words(minimal_len, top_words)  # Analyzes the most common words in the chatlog.
        c.moving_avarage(moving_avarage_window)  # Calculates the moving average of the number of messages for n days.
        c.store_data()  # Stores the results of the analysis in a dictionary.
        json_data.append(c.stored_data)  # Adds the results of the analysis to the list.
        # This list will contain the results of the analysis of all chatlogs.

        print(c.data["title"])  # Prints the name of the chatlog which was analyzed.

    store_data(json_data)  # Stores the results of the analysis in a json file.

    d = GeneralData()  # Creates an instance of the GeneralData class.
    d.identify()  # Tries to identify your name.
    d.collect_data()  # Analysis of data from all chatlogs.
    d.moving_avarage(moving_avarage_window)  # Calculates the moving average of the number of messages for n days.
    d.save_data()  # Stores the results of the analysis in a json file.
    return d.data


# The main function is called.
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        input("Press enter to exit.")
        exit()
