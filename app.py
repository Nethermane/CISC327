import constants

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
        #

def login():
    global user_status
    if(user_status != constants.idle_state):
        print(constants.logged_in_login)
        return
    while True:
        user_input = input(constants.login_message)
        parsed_login = user_input.lower().strip()
        if(parsed_login == constants.atm_state or parsed_login == constants.agent_state):
            user_status = parsed_login
            print(constants.successful_login(parsed_login))
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
    else:
        print(constants.logout_message)
        user_status = constants.idle_state
if __name__ == "__main__":
    main()
