import random
import _sqlite3
import re

conn = _sqlite3.connect("card.s3db")
cur = conn.cursor()
cur.execute("DROP TABLE card;")
conn.commit()

# Write your code here
exit_value = True
login_success = False
user_s_choice = 0
id_calc = 1

SELECT_DATA_card_number = "SELECT * FROM card WHERE number = ?;"
SELECT_DATA_pin = "SELECT * FROM card WHERE pin = ?;"
SELECT_DATA_BAlANCE = "SELECT balance from card WHERE number = ?"
INSERT_DATA = "INSERT INTO card (number, pin) VALUES ( ?, ?);"
UPDATE_DATA = "UPDATE card SET pin = ? WHERE pin = ?"
UPDATE_BALANCE = "UPDATE card SET balance = ? WHERE balance = ? AND number = ?"
SELECT_DATA_ACCOUNT = "SELECT number FROM card WHERE number = ?"
DELETE_ACCOUNT = "DELETE FROM card WHERE number = ? AND PIN = ?"


def checking_database_exists():
    cur.execute(
        "CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY AUTOINCREMENT , number TEXT, pin TEXT, balance INTEGER DEFAULT 0 );")
    conn.commit()


class CardNumber:
    def __init__(self):
        self.start_number = str(400000)
        self.account_id = ""
        self.luhn_number = ""
        self.pin = ""
        self.checksum = ""

    def making_card_number(self):
        # making account id
        self.account_id += self.start_number
        for i in range(0, 9, 1):  # generate the id
            self.account_id += str(random.randint(0, 9))

        list_car_number = [int(i) for i in self.account_id]  # put the id in an integer list for processions

        for index, _ in enumerate(list_car_number):
            if index % 2 == 0:
                list_car_number[index] *= 2
            if list_car_number[index] > 9:
                list_car_number[index] -= 9

        check_sum = str((10 - sum(list_car_number) % 10) % 10)
        self.account_id += check_sum

        conn.commit()
        cur.execute(INSERT_DATA, (self.account_id, 0))
        conn.commit()
        return str(self.account_id)

    def making_pin(self):
        self.pin = str(random.randint(1000, 9999))
        cur.execute(UPDATE_DATA, (self.pin, 0))
        conn.commit()

        return str(self.pin)


class Action:
    def __init__(self, account, current_balance):
        self.account = account,
        self.current_balance = current_balance

    def display_value(self, base_value):
        display = "Balance : {}".format(base_value)
        return display

    def add_income(self, base_value, money_in, money_in_account):
        new_value = int(base_value) + money_in
        cur.execute(UPDATE_BALANCE, (new_value, base_value, money_in_account))
        conn.commit()
        return "Income was added !"

    def check_transfer(self, account_to_transfer, account_number):
        temp_card_number = cur.execute(SELECT_DATA_card_number, (account_to_transfer,)).fetchone()
        conn.commit()
        final_string = ""
        if account_to_transfer == account_number:
            final_string = "You can't transfer money to the same account!"
        elif Action.luhn_checksum(self, account_to_transfer) is False:
            if Action.luhn_checksum(self, account_to_transfer) is False:
                final_string = "Probably you made a mistake in the card number. Please try again!"
            else:
                final_string = "Such a card does not exist."
        elif temp_card_number is None:
            final_string = "Such a card does not exist."
        else:
            final_string = "True"

        return final_string

    def luhn_checksum(self, card_number):
        list_car_number = [int(i) for i in card_number]  # put the id in an integer list for processions
        for index, _ in enumerate(list_car_number):
            if index % 2 == 0:
                list_car_number[index] *= 2
            if list_car_number[index] > 9:
                list_car_number[index] -= 9

        checksum = sum(list_car_number)
        return checksum % 10 == 0

    def make_transfer(self, account_to_transfer, money_to_transfer, cash_in_account, account_number):
        if money_to_transfer > cash_in_account:
            return "Not enough money!"
        else:
            # get the money in the account to transfer
            money_in_account_to_transfer = cur.execute(SELECT_DATA_BAlANCE, (account_to_transfer,)).fetchall()
            conn.commit()
            money_in_account_to_transfer = int(''.join(map(str, money_in_account_to_transfer[0])))
            # update balance in the account to transfer
            cur.execute(UPDATE_BALANCE, (money_in_account_to_transfer + money_to_transfer, money_in_account_to_transfer, account_to_transfer))
            conn.commit()
            # update balance in the source account
            cur.execute(UPDATE_BALANCE, (cash_in_account - money_to_transfer, cash_in_account, account_number ))
            conn.commit()

            print(money_to_transfer)
            print(cash_in_account)
            print(money_in_account_to_transfer)
            return "Success!"

    def closing_account(self, number, pin):
        cur.execute(DELETE_ACCOUNT, (number, pin))
        conn.commit()
        return "The account has been closed!"


while exit_value is True:
    print("____________________")
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    checking_database_exists()

    user_s_choice = int(input())
    if user_s_choice == 1:
        new_card = CardNumber()
        temp_card = str(new_card.making_card_number())
        temp_PIN = int(new_card.making_pin())
        print("Your card has been created")
        print("Your card number:")
        print(temp_card)
        print("You card PIN:")
        print(temp_PIN)

    elif user_s_choice == 2:
        temp_card = str(input("Enter your card number:"))
        temp_PIN = int(input("Enter your PIN:"))

        data_card = cur.execute(SELECT_DATA_card_number, (temp_card,)).fetchone()
        conn.commit()
        pin_from_data_card = int(''.join(map(str, data_card[2])))
        
        if pin_from_data_card != temp_PIN:
            print("Wrong card number or PIN!")
        else:
            print("You have successfully logged in!")
            login_success = True
        
        while login_success:
            user_balance = cur.execute(SELECT_DATA_BAlANCE, (temp_card,)).fetchall()
            conn.commit()
            user_balance_int = int(''.join(map(str, user_balance[0])))
            print("____________________")
            print("1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")
            user_s_choice = int(input())
            new_account = Action(temp_card, user_balance_int)
            if user_s_choice == 1:
                print(new_account.display_value(user_balance_int))
            elif user_s_choice == 5:
                print("You have successfully logged out!")
                login_success = False
            elif user_s_choice == 2:
                income_to_add = int(input("Enter income :"))
                print(new_account.add_income(user_balance_int, income_to_add, temp_card))
            elif user_s_choice == 3:
                card_to_transfer = input("Enter card number:")
                checking = new_account.check_transfer(card_to_transfer, temp_card)  # !!! doesn't work properly !!!
                if checking == "True":
                    money_flow = int(input("Enter how much money you want to transfer:"))
                    print(new_account.make_transfer(card_to_transfer, money_flow, user_balance_int, temp_card))
                else:
                    print(checking)
            elif user_s_choice == 4:
                print(new_account.closing_account(temp_card, temp_PIN))
                login_success = False
            else:
                login_success = False
                exit_value = False

    elif user_s_choice == 0:
        exit_value = False
        print("Bye!")
        conn.close()
