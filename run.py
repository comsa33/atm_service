import os
import sys
import time
from datetime import datetime
import json

class ATM:
    def __init__(self):
        self._power = True
        self._status = False

        self._auth = False
        self._auth_id = 'manager'
        self._auth_pw = 'ruobankmanger'
        self._auth_limit = 5
        self._atm_balance = 50000

        self.card = None
        self.user_limit = 5

        self.welcome_message = 'Welcome to RUO BANK.\nPlease insert your card to use bank services.'
        self.terminate_service_message = 'Thank you, we will terminate your service.'
        self.service_message = 'Please select the service.'
        self.wrong_user_pw_error_message = 'Wrong PIN Code!'
        self.card_insert_error_message = 'Make Sure to Insert Your Card Correctly!\nTerminate your service.'
        self.user_inputError_message = "There was something wrong with the previous input."
        self.not_enough_balance_message = "It seems your account holds not enough balance."
        self.transaction_cancel_message = "You cancled the transaction."
        self.atm_balance_error_message = 'Currently, service is not in use.'
        self.user_limit_warning_message = f'You have {self.user_limit} times left to try.'
        self._auth_limit_warning_message = f'You have {self._auth_limit} times left to try.'
        self.exceed_limit_message = 'You exceeded the limit to try.'
        
    def transaction(self, card):
        self.card = card
        if self._atm_balance > 0:
            self.initiate_service()
        else:
            self.shutdown_atm_service()
    
    def _get_auth(self):
        if self._auth_limit > 0:
            while self._auth_limit > 0:
                print(self._auth_limit_warning_message)
                self._auth_limit -= 1
                auth_id = input("Manager ID: ")
                assert auth_id == self._auth_id, "Incorrect ID"
                auth_pw = input("Manager PW: ")
                assert auth_pw == self._auth_pw, "Incorrect PW"
                self._auth_limit = 5
                return True
        print(self.exceed_limit_message)
        return False

    def _supply_atm_balance(self):
        self._auth = self._get_auth()
        assert self._auth == True, "You can't access the system!"
        amount = int(input("Credit: "))
        assert amount > 0, "You should put more than 0 credit."
        self._atm_balance += amount

    def _retrieve_atm_balance(self, auth_id, auth_pw, amount=0):
        self._auth = self._get_auth()
        assert self._auth == True, "You can't access the system!"
        amount = int(input("Credit: "))
        assert amount > 0, "You should put more than 0 credit."
        self._atm_balance -= amount

    def initiate_service(self):
        print(self.welcome_message)
        self.user_id, self.user_name, self.user_password, self.user_accounts = self.read_card()
        while self._status:
            self.display_service()

    def terminate_service(self):
        print(self.terminate_service_message)
        self._record_logs()
        del self.card, self.user_id, self.user_name, self.user_password, self.user_accounts, self.user_log
        self._status = False

    def _record_logs(self):
        if not os.path.exists('./logs'):
            os.makedirs('./logs')
        timestamp = str(time.time()).replace('.', '_')
        with open(f'./logs/{timestamp}.json', 'w') as f:
            json.dump(self.user_log, f, ensure_ascii=False, indent=4)

    def shutdown_atm_service(self):
        print(self.atm_balance_error_message)
        self._power = False

    def display_service(self):
        print(f"{self.user_name}'s Account No: {self.selected_account['account_no'][:-5]+'*****'}")
        print(self.service_message)
        print('[1] Check Balance\t[2] Withdraw\t[3] Deposit\t[4] Exit')
        self.service = input()
        if self.service == '1':
            self.check_balance()
        elif self.service == '2':
            self.withdraw()
        elif self.service == '3':
            self.deposit()
        elif self.service == '4':
            self.terminate_service()

    def check_user_pw(self, user_password):
        while self.user_limit > 0:
            print(self.user_limit_warning_message)
            input_pw = input('Enter your PIN Code: ')
            self.user_limit -= 1
            if input_pw == user_password:
                self.user_limit = 5
                return True
            else:
                print(self.wrong_user_pw_error_message)
                print('Please Try it again.')
        assert self.user_limit > 0, self.exceed_limit_message

    def select_account(self, user_accounts):
        assert type(user_accounts) == dict
        user_accounts_list = list(enumerate(user_accounts.keys()))
        for i, account_name in enumerate(user_accounts.keys()):
            print(f'[{i}] {account_name}')
        user_input = int(input('Select Your Account: '))
        selected_account = user_accounts_list[user_input][1]
        return user_accounts[selected_account]

    def read_card(self):
        assert self.card is not None, self.card_insert_error_message
        assert type(self.card) == dict
        user_id = self.card['user_id']
        user_name = self.card['user_name']
        user_password = self.card['password']
        user_accounts = self.card['accounts']

        self._status = self.check_user_pw(user_password=user_password)
        self.selected_account = self.select_account(user_accounts=user_accounts)

        timestamp = datetime.now().strftime('%Y%m%dZ%H%M%S')
        self.user_log = {'id':user_id, 
                        'name':user_name, 
                        'transaction_start':timestamp, 
                        'transactions':{
                            self.selected_account['account_no']:{'transaction':{}}
                            }
                        } 
        return user_id, user_name, user_password, user_accounts

    def check_balance(self):
        balance = self.selected_account['balance']
        print(f"Your Balance : ${balance}")
        timestamp = datetime.now().strftime('%Y%m%dZ%H%M%S')
        self.user_log['transactions'][self.selected_account['account_no']]['transaction'][timestamp] = f'check_balance : {balance}'

    def deposit(self):
        input_deposit_amount = int(input("Select the amount you want to deposit: "))
        user_input = input(f"Deposit credit : ${input_deposit_amount}, Is it Correct?(y/n): ")
        if user_input == 'y':
            self.selected_account['balance'] += input_deposit_amount
            balance = self.selected_account['balance']
            print(f"Deposited : ${input_deposit_amount}")
            print(f"Your Balance : ${balance}")
            timestamp = datetime.now().strftime('%Y%m%dZ%H%M%S')
            self.user_log['transactions'][self.selected_account['account_no']]['transaction'][timestamp] = f'deposit : {input_deposit_amount}, balance : {balance}'
        elif user_input == 'n':
            print(self.transaction_cancel_message)
        else:
            print(self.user_inputError_message)

    def withdraw(self):
        balance = self.selected_account['balance']
        print(f"Your Balance : ${balance}")
        while True:
            input_withdraw_amount = int(input("Select the amount you want to withdraw: "))
            if self.selected_account['balance'] < input_withdraw_amount:
                print(self.not_enough_balance_message)
                print("Try it again.")
            else:
                break
        user_input = input(f"Withdraw credit : ${input_withdraw_amount}, Is it Correct?(y/n): ")
        if user_input == 'y':
            self.selected_account['balance'] -= input_withdraw_amount
            balance = self.selected_account['balance']
            print(f"Withdrawn : ${input_withdraw_amount}")
            print(f"Your Balance : ${balance}")
            timestamp = datetime.now().strftime('%Y%m%dZ%H%M%S')
            self.user_log['transactions'][self.selected_account['account_no']]['transaction'][timestamp] = f'withdraw : {input_withdraw_amount}, balance : {balance}'
        elif user_input == 'n':
            print(self.transaction_cancel_message)
        else:
            print(self.user_inputError_message)


if __name__ == '__main__':
    # user_id = self.card['user_id']
    # user_name = self.card['user_name']
    # user_password = self.card['password']
    # user_accounts = self.card['accounts']
    my_card = {'user_id':'ruo33', 'user_name':'Ruo Lee', 'password':'1234', 'accounts':{'123-456-789':{'account_no':'123-456-789', 'balance':100000}}}
    my_atm = ATM()
    my_atm.transaction(card=my_card)