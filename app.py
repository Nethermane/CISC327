import constants
import re
import os.path
from os import path
import datetime

user_status = constants.idle_state
current_file_output = []
accounts_list = []
def main():
    print(constants.first_launch_message)
    while True:
        user_command = input(constants.enter_command_text)
        parsed_command = user_command.lower().strip()
        #Prevent all commands but login before logging in
        if(user_status == constants.idle_state and parsed_command != constants.login_command):
            print(constants.not_logged_in_message)
        #login
        elif(user_command == constants.login_command):
            login()
        #logout
        elif(user_command == constants.logout_command):
            logout()
        #createacct
        elif(user_command == constants.createacct_command):
            create_account()
        #deleteacct
        elif(user_command == constants.deleteacct_command):
            delete_account()
        #deposit
        elif(user_command == constants.deposit_command):
            deposit()
        #withdraw
        elif(user_command == constants.withdraw_command):
            withdraw()
        #transfer
        elif(user_command == constants.transfer_command):
            transfer()
        elif(user_command == constants.help_command):
            print(constants.help_text)
        else:
            print(constants.unrecognized_command)

#TODO: open valid accounts file when login
def login():
    global user_status, accounts_list
    if(user_status != constants.idle_state):
        print(constants.logged_in_login)
        return
    while True:
        user_input = input(constants.login_message)
        parsed_login = user_input.lower().strip()
        if(parsed_login == constants.atm_state):
            user_status = constants.atm_state
            print(constants.successful_login(constants.atm_state))
            with open(constants.accounts_file) as fp:
                accounts_list = fp.readlines()
            return
        elif(parsed_login == constants.agent_state):
            user_status = constants.agent_state
            print(constants.successful_login(constants.agent_state))
            with open(constants.accounts_file) as fp:
                accounts_list = fp.readlines()
            return
        elif(parsed_login == constants.cancel_command):
            return
        else:
            user_status = constants.idle_state
            print(constants.unrecognized_login_command(user_input))
def logout():
    global user_status, current_file_output
    if(user_status == constants.idle_state):
        print(constants.logged_out_logout_message)
        return
    else:
        print(constants.logout_message)
        current_file_output.append([constants.end_of_file_key,
                            constants.empty_account_number,
                            constants.empty_money_amount,
                            constants.empty_account_number,
                            constants.empty_account_name
                            ])
        print(current_file_output)
        timestamp = str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        log_number = 0
        potential_file = constants.summary_transaction_file(timestamp, log_number)
        while(True):
            if(path.exists(potential_file)):
                log_number +=1
                continue
            else:
                os.makedirs(os.path.dirname(potential_file), exist_ok=True)
                break
        with open(potential_file, 'w+') as fp:
            for transaction in current_file_output:
                fp.write(' '.join(transaction) + '\n')
        current_file_output = []
        user_status = constants.idle_state
def create_account():
    global user_status
    if(user_status != constants.agent_state):
        print(constants.create_account_without_privilege)
        return
    account_number = get_valid_account_number()
    if(account_number is None):
        return
    account_name = get_valid_account_name()
    if(account_name is None):
        return
    current_file_output.append([constants.create_account_output_key,
                                account_number,
                                empty_money_amount,
                                constants.empty_account_number,
                                account_name
                                ])
    print(constants.successful_delete)

def delete_account():
    global user_status
    if(user_status != constants.agent_state):
        print(constants.create_account_without_privilege)
        return
    account_number = get_valid_account_number()
    if(account_number is None):
        return
    account_name = get_valid_account_name()
    if(account_name is None):
        return
    current_file_output.append([constants.delete_account_output_key,
                                account_number,
                                empty_money_amount,
                                constants.empty_account_number,
                                account_name
                                ])
    print(constants.successful_delete)

def deposit():
    global user_status, current_file_output
    if(user_status == constants.idle_state):
        print(constants.must_be_signed_in_for_command(constants.deposit_command))
        return
    account_number = get_valid_account_number(True)
    #Check number less than max single transaction
    cents = get_valid_numeric_amount(constants.max_deposit_atm_once if user_status == constants.atm_state else constants.max_deposit_teller_once)
    if(cents is None):
        return
    #Check if total deposits that day less than total
    if(user_status == constants.agent_state or total_less_than_daily_limit(constants.deposit_output_key, account_number, constants.max_deposit_atm_daily)):
        current_file_output.append([constants.deposit_output_key,
                                    account_number,
                                    cents,
                                    constants.empty_account_number,
                                    constants.empty_account_name
                                    ])
        print(constants.successful_deposit)
    else:
        print(constants.deposit_over_max)

def withdraw():
    global user_status, current_file_output
    if(user_status == constants.idle_state):
        print(constants.must_be_signed_in_for_command(constants.withdraw_command))
        return
    account_number = get_valid_account_number(True)
    #Check number less than max single transaction
    cents = get_valid_numeric_amount(constants.max_withdraw_atm_once if user_status == constants.atm_state else constants.max_withdraw_agent_once)
    if(cents is None):
        return
    #Check if total withdrawl less than total limit
    if(user_status == constants.agent_state or total_less_than_daily_limit(constants.withdraw_output_key, account_number, constants.max_withdraw_atm_daily)):
        current_file_output.append([constants.deposit_output_key,
                                    constants.empty_account_number,
                                    cents,
                                    account_number,
                                    constants.empty_account_name
                                    ])
        print(constants.successful_withdraw)
    else:
        print(constants.withdraw_over_max)

def transfer():
    global user_status, current_file_output
    if(user_status == constants.idle_state):
        print(constants.must_be_signed_in_for_command(constants.withdraw_command))
        return
    from_account = get_valid_account_number(True, constants.from_account_prompt)
    to_number = get_valid_account_number(True, constants.to_account_prompt)
    #Check number less than max single transaction
    cents = get_valid_numeric_amount(constants.max_transfer_atm_once if user_status == constants.atm_state else constants.max_transfer_agent_once)
    if(cents is None):
        return
    #Check if total withdrawl less than total limit
    if(user_status == constants.agent_state or total_less_than_daily_limit(constants.transfer_output_key, account_number, constants.max_transfer_atm_once)):
        current_file_output.append([constants.deposit_output_key,
                                    to_account,
                                    cents,
                                    from_account,
                                    constants.empty_account_name
                                    ])
        print(constants.successful_withdraw)
    else:
        print(constants.withdraw_over_max)


def valid_account_name(name):
    return name is not None and re.search('^[\w][\w ]{1,28}[\w]$', name) is not None
def valid_account_number(number):
    return number is not None and re.search('^[1-9][0-9]{6}$', number) is not None
def valid_cents_amount(number, max_value):
    return number is not None and number <= max_value
def total_less_than_daily_limit(transaction_type, account_number, limit):
    return sum(map(lambda row: int(row[2]),filter(lambda row: row[0] == transaction_type, current_file_output))) <= limit
    
#returns a valid account number from user input
#If check_accounts_list is True, requires the number to be in the accounts list
#returns None if exit command is provided
def get_valid_account_number(check_accounts_list, prompt=constants.account_number_input):
    while True:
        account_number = input(prompt)
        if(valid_account_number(account_number)):
            if((not check_accounts_list) or (check_accounts_list and account_number in accounts_list)):
                return account_number
            else:
                print(constants.account_number_not_in_list)
        elif account_number == constants.cancel_command:
            return None
        else:
            print(constants.invalid_account_number)

#returns a valid account name from user input
#returns None if exit command is provided
def get_valid_account_name():
    while True:
        account_name = input(constants.account_name_input)
        if(valid_account_name(account_name)):
            return account_name
        elif account_name == constants.cancel_command:
            return None
        else:
            print(constants.invalid_account_name)

#returns a valid cents amount less than or equal to max value
#returns None if exit command provided
#returns a string, ensuring it is validly numeric.
def get_valid_numeric_amount(max_value):
    while True:
        cents = input(constants.cents_value).replace(',','')
        try:
            cents_int = int(cents)
            if(valid_cents_amount(cents_int, max_value)):
                return str(cents_int)
            else:
                print(constants.error_cents_less_than(str(max_value)))
        except ValueError:
            if cents == constants.cancel_command:
                return None
            print(constants.parse_number_error)



if __name__ == "__main__":
    main()
