import constants
import re

user_status = constants.idle_state
def main():
    print(constants.first_launch_message)
    while True:
        user_command = input(constants.enter_command_text)
        parsed_command = user_command.lower().strip()
        #Prevent all commands but login before logging in
        if(user_status == constants.idle_state and parsed_command != constants.login_command):
            print(constants.not_logged_in_message)
        #Login command
        elif(user_command == constants.login_command):
            login()
        #logout command
        elif(user_command == constants.logout_command):
            logout()
        #createacct
        elif(user_command == constants.createacct_command):
            create_account()

#TODO: open file when login
def login():
    global user_status
    if(user_status != constants.idle_state):
        print(constants.logged_in_login)
        return
    while True:
        user_input = input(constants.login_message)
        parsed_login = user_input.lower().strip()
        if(parsed_login == constants.atm_state):
            user_status = constants.atm_state
            print(constants.successful_login(constants.atm_state))
            return
        elif(parsed_login == constants.agent_state):
            user_status = constants.agent_state
            print(constants.successful_login(constants.agent_state))
            return
        elif(parsed_login == cancel_command):
            return
        else:
            user_status = constants.idle_state
            print(constants.unrecognized_login_command(user_input))
def logout():
    global user_status
    if(user_status == constants.idle_state):
        print(constants.logged_out_logout_message)
        return
    else:
        print(constants.logout_message)
        user_status = constants.idle_state
    #TODO: Write to file on logout
def create_account():
    global user_status
    if(user_status != constants.agent_state):
        print(constants.create_account_without_privilege)
        return
    account_number = None
    account_name = None
    while True:
        account_number = input(constants.account_number_input)
        if(valid_account_number(account_number)):
            break
        elif account_number == constants.cancel_command:
            return
        else:
            print(constants.invalid_account_number)
    while True:
        account_name = input(constants.account_name_input)
        if(valid_account_name(account_name)):
            break
        elif account_name == constants.cancel_command:
            return
        else:
            print(constants.invalid_account_name)
    #TODO: Actually write this command to file.
    
def valid_account_name(name):
    return name is not None and re.search('^[\w][\w ]{1,28}[\w]$', name) is not None
def valid_account_number(number):
    return number is not None and re.search('^[1-9][0-9]{6}$', number) is not None


if __name__ == "__main__":
    main()
