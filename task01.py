from collections import UserDict, defaultdict
from datetime import datetime, timedelta

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "No such contact found."

    return inner

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if not self.validate():
            raise ValueError("Invalid phone number format")
        
    def validate(self):
        return len(self.value) == 10 and self.value.isdigit()

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        if not self.validate():
            raise ValueError("Invalid date format")
        
    def validate(self):
        try:
            datetime.strptime(self.value, '%d.%m.%Y')
            return True
        except ValueError:
            return False

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        self.phones = [phone for phone in self.phones if phone.value != phone_number]

    def edit_phone(self, old_number, new_number):
        phone = self.find_phone(old_number)
        phone.value = new_number

    def add_birthday(self, birthday):
        if self.birthday:
            raise ValueError("Birthday already exists for this contact")
        self.birthday = Birthday(birthday)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    def __str__(self):
        phone_info = '; '.join(p.value for p in self.phones)
        birthday_info = f", Birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phone_info}{birthday_info}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def get_birthdays_per_week(self):
        next_monday = datetime.today().date() + timedelta(days=(7 - datetime.weekday(datetime.today().date())) % 7)
        today = next_monday
        birthdays = defaultdict(list)

        for record in self.data.values():
            name = record.name.value
            birthday = record.birthday.value
            if birthday:
                birthday_this_year = datetime.strptime(birthday, "%d.%m.%Y").date().replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                delta_days = (birthday_this_year - today).days

                if delta_days < 7:
                    weekday = (today + timedelta(days=delta_days)).strftime("%A")
                    if weekday in ["Saturday", "Sunday"]:
                        weekday = "Monday"
                    birthdays[weekday].append(name)

        return birthdays

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_birthday(args, address_book):
    name, birthday = args
    contact = address_book.find(name)
    if contact:
        contact.add_birthday(birthday)
        return f"Birthday added for {name}"
    else:
        return "No such contact found"

@input_error
def show_birthday(args, address_book):
    name = args[0]
    contact = address_book.find(name)
    if contact and contact.birthday:
        return f"{name}'s birthday: {contact.birthday.value}"
    elif contact and not contact.birthday:
        return f"{name} doesn't have a birthday set."
    else:
        return "No such contact found."

@input_error
def show_birthdays(address_book):
    birthdays_per_week = address_book.get_birthdays_per_week()
    output = ""
    for weekday, names in birthdays_per_week.items():
        output += f"{weekday}: {', '.join(names)}\n"
    return output

def main():
    address_book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Goodbye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            name, phone = args
            record = Record(name)
            try:
                record.add_phone(phone)
                address_book.add_record(record)
                print("Contact added.")
            except ValueError as e:
                print(str(e))
        elif command == "change":
            name, phone = args
            record = address_book.find(name)
            if record:
                try:
                    record.add_phone(phone)
                    print(f"Phone number updated for {name}")
                except ValueError as e:
                    print(str(e))
            else:
                print("No such contact found.")
        elif command == "phone":
            name = args[0]
            record = address_book.find(name)
            if record:
                print(record.phones[0])  
            else:
                print("No such contact found.")
        elif command == "all":
            for record in address_book.values():
                print(record)
        elif command == "add-birthday":
            print(add_birthday(args, address_book))
        elif command == "show-birthday":
            print(show_birthday(args, address_book))
        elif command == "birthdays":
            print(show_birthdays(address_book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
