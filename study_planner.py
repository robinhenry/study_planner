import datetime
import pickle
import tkinter as tk


class Timetable(object):

    def __init__(self):
        self.schedules = {}
        self.update()
        return

    def update(self):
        for s in self.schedules.values():
            s.update()
        with open('timetable_backup', 'wb') as f:
            pickle.dump(self, f)
        return

    def add_schedule(self, name, freq):
        self.schedules[name] = Schedule(name, freq)
        self.update()
        return

    def add_topic(self, schedule, topic, freq=None):
        self.schedules[schedule].add_topic(topic, freq)
        self.update()
        return

    def update_frequency(self, schedule, freq):
        self.schedules[schedule].update_frequency(freq)
        return

    def summary(self):
        print('Schedules:')
        print('----------')
        if not self.schedules:
            print('No schedules yet!')
        for s in self.schedules:
            print(s + f' (frequency: {s.frequency})')
        return

    def display_schedule(self, day):
        to_be_displayed = ''
        for s in self.schedules.values():
            to_be_displayed += s.print_date(day) + '\n'

        return to_be_displayed


class Schedule(object):

    def __init__(self, name, freq):
        ''' Initialise a new schedule.'''
        self.name = name
        self.current_date = datetime.date.today()
        self.dates = {}
        self.start_dates = {}
        self.frequency = freq
        return

    def update(self):
        ''' Update the schedule to today.'''
        self.current_date = datetime.date.today()
        for d in self.dates:
            if d < self.current_date:
                del self.current_date[d]
        return

    def update_frequency(self, freq):
        '''Update frequency at which topics are revised.'''
        self.frequency = freq
        return

    def add_topic(self, topic, freq=None):
        ''' Add a study topic.'''
        self.update()
        self.start_dates[topic] = self.current_date
        # Use study frequency given as argument if present.
        if not freq:
            frequency = self.frequency
        else:
            frequency = freq
        for f in frequency:
            to_add = datetime.timedelta(days=f)
            try:
                self.dates[self.current_date + to_add].append(topic)
            except KeyError:
                self.dates[self.current_date + to_add] = [topic]
        return

    def get_topic_schedule(self, topic):
        revision_dates = []
        for d, top in self.dates.items():
            if topic in top:
                revision_dates.append(d)
        return revision_dates

    def print_topic_schedule(self, topic):
        print('Topic: ' + topic)
        print('--------------------------')
        for d in self.get_topic_schedule(topic):
            print(d)
        return

    def print_date(self, day):
        '''Print a list of topics to revise today.'''
        self.update()
        to_be_printed = 'Schedule: ' + self.name + '\n'
        to_be_printed += '----------------------------\n'
        try:
            topics = self.dates[day]
        except KeyError:
            to_be_printed += 'Nothing to do.\n'
            return to_be_printed
        for t in topics:
            to_be_printed += t + ': day ' + str((day - self.start_dates[
                t]).days)+ '\n'
        return to_be_printed

    def print_today(self):
        self.print_date(0)
        return




class Application(tk.Frame):

    def __init__(self, master=None):
        self.master = master
        super().__init__(master)
        master.title('Study timetable')

        self.load_backup()
        self.init_add_schedule()
        self.init_add_topic()
        self.display_schedule()

        # Button to view current topics.
        #self.current_topics_button = tk.Button(master, text='View current
        # topics', command=self.current_topics())
        #self.current_topics_button.pack()

        self.updater()

        return

    def load_backup(self):
        ''' Try to retrieve the backed up file.'''
        try:
            with open('timetable_backup', 'rb') as f:
                self.timetable = pickle.load(f)
        except IOError:
            print('Backup file not found.')

            # Create a new timetable, if needed.
            answer = input('Do you want to create a new timetable? ')
            if answer == 'yes':
                self.timetable = Timetable()
            else:
                print('OK, never mind.')
                exit()
        return

    def updater(self):
        self.update_add_topic()
        #self.update_display_schedule()
        self.after(1000, self.updater)
        return


    def init_add_schedule(self):
        ### ADD A NEW CALENDAR ###
        # Title of new calendar.
        tk.Label(self.master, text='Add a new class',
                                     font='Verdana 12 bold').grid(row=0,
                                                                  column=0)

        # Specify name of calendar.
        tk.Label(self.master, text='Class name').grid(row=1, column=0)

        new_calendar_name = tk.StringVar()
        new_calendar_entry = tk.Entry(self.master,
                                      textvariable=new_calendar_name)
        new_calendar_entry.grid(row=2, column=0)

        # Specify default frequency of new calendar.
        tk.Label(self.master, text="Frequency").grid(row=3, column=0)

        new_calendar_freq = tk.StringVar()
        new_calendar_freq_entry = tk.Entry(self.master,
                                      textvariable=new_calendar_freq)
        new_calendar_freq_entry.grid(row=4, column=0)

        # Confirm the new calendar.
        def add_new_cal():
            s = list(map(int, new_calendar_freq.get().split()))
            self.timetable.add_schedule(new_calendar_name.get(),
                                        list(map(int, new_calendar_freq.get(
                                        ).split())))
            return

        tk.Button(self.master, text='Add class', command=add_new_cal).grid(
            row=5, column=0)
        self.master.grid_rowconfigure(6, minsize=20)

        return

    def init_add_topic(self):
        ### ADD A NEW TOPIC ###
        # Title of section to add topic.
        tk.Label(self.master, text='Add a new topic',
                 font='Verdana 12 bold').grid(row=7, column=0)

        # Specify name of topic.
        tk.Label(self.master, text='Topic name').grid(row=8, column=0)
        add_name_entry = tk.Entry(self.master)
        add_name_entry.grid(row=9, column=0)

        # Specify frequency at which to study the topic.
        tk.Label(self.master, text="Frequency").grid(row=10, column=0)
        add_frequency_entry = tk.Entry(self.master)
        add_frequency_entry.grid(row=11, column=0)

        # Specify in which calendar to add the new topic.
        tk.Label(self.master, text='Corresponding class').grid(row=12,
                                                                  column=0)

        calendars = list(self.timetable.schedules)
        self.v = tk.IntVar()
        self.v.set(1)
        self.radiobuttons = {}
        self.buttons_row = tk.IntVar()
        self.buttons_row.set(13)
        for idx, schedule in enumerate(calendars):
            freq = str(self.timetable.schedules[schedule].frequency)
            if freq:
                text = schedule + ' (default: ' + freq + ')'
            else:
                text = schedule
            button = tk.Radiobutton(self.master, text=text, padx=20,
                                    variable=self.v,
                                    value=idx + 1).grid(
                row=self.buttons_row.get(), column=0, sticky='W')
            self.radiobuttons[schedule] = button
            self.buttons_row.set(self.buttons_row.get() + 1)

        def add_topic():
            try:
                schedule = list(self.timetable.schedules)[self.v.get() - 1]
            except IndexError:
                print('There is no current calendar.')
                return

            freq = list(map(int, add_frequency_entry.get().split()))
            self.timetable.add_topic(schedule, add_name_entry.get(), freq)
            return

        self.add_button = tk.Button(self.master, text='Add topic',
                                 command=add_topic)
        self.add_button.grid(row=self.buttons_row.get() + 1, column=0)

        return

    def update_add_topic(self):

        for s in self.timetable.schedules:
            if s not in self.radiobuttons:
                freq = str(self.timetable.schedules[s].frequency)
                if freq:
                    text = s + ' (default: ' + freq + ')'
                else:
                    text = s
                button = tk.Radiobutton(self.master, text=text, padx=20,
                                        variable=self.v,
                                        value=len(self.radiobuttons) + 1)
                button.grid(row=self.buttons_row.get(), column=0, sticky='w')
                self.buttons_row.set(self.buttons_row.get() + 1)
                self.radiobuttons[s] = button

                # Move 'add topic' button down
                self.add_button.grid_forget()
                self.add_button.grid(row=self.buttons_row.get() + 1, column=0)

        return



    def display_schedule(self):
        ''' Display the topics to be studied on a specific date.'''

        tk.Label(self.master, text='Display schedule',
                font='Verdana 12 bold').grid(row=0, column=1, columnspan=2)
        tk.Label(self.master, text='Date').grid(row=1, column=1)

        self.display_date = tk.StringVar()
        self.display_date.set(datetime.date.today().strftime("%d/%m/%y"))
        display_date_entry = tk.Entry(self.master,
                                           textvariable=self.display_date)
        display_date_entry.grid(row=1, column=2)

        tk.Button(self.master, text='Refresh schedule',
                  command=self.update_display_schedule).grid(row=2, column=2)

        return

    def update_display_schedule(self):
        day = datetime.datetime.strptime(self.display_date.get(), '%d/%m/%y')
        day = day.date()
        if day:
            to_be_displayed = self.timetable.display_schedule(day)
            tk.Label(self.master, text=to_be_displayed).grid(row=3, column=1,
                                                             columnspan=2,
                                                             rowspan=1000,
                                                             sticky='n')
        return

    def current_topics(self):
        pass


if __name__ == '__main__':

    # Start Application.
    root = tk.Tk()
    my_GUI = Application(root)
    root.mainloop()
