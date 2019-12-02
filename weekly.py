import io
import sys

import daily


# runs the daily script 5 times, providing the correct input
def main():
    # at the start of the week, start with an empty accounts list
    with open('valid_accounts.txt', 'w') as wf:
        wf.write('0000000')
    open('master_accounts.txt', 'w').close()  # wipe master accounts file
    days = [
        # day 1
        ['login', 'agent', 'createacct', '1001001', 'Coolest account', 'logout',
         'login', 'agent', 'createacct', '2222222', 'Acct 2', 'logout',
         'login', 'agent', 'createacct', '3333333', 'Acct 3', 'logout'],
        # day 2
        ['login', 'agent', 'createacct', '1111111', 'Acct 1', 'logout',
         'login', 'machine', 'deposit', '1001001', '33300', 'logout',
         'login', 'machine', 'transfer', '1001001', '3333333', '33300', 'logout'],
        # day 3
        ['login', 'machine', 'deposit', '2222222', '20000000', '200000', 'logout',
         'login', 'machine', 'deposit', '2222222', '200000', 'logout',
         'login', 'machine', 'deposit', '2222222', '100000', 'logout'],
        # day 4
        ['login', 'machine', 'deposit', '1111111', '1700', 'logout',
         'login', 'machine', 'withdraw', '3333333', '100100', '1000', 'logout',
         'login', 'agent', 'deleteacct', '1001001', 'Coolest account', 'logout',
         'login', 'agent', 'createacct', '123456', '1234567', 'hi', 'give me your money', 'logout'],
        # day 5
        ['login', 'machine', 'transfer', '1111111', '1234567', '1700', 'logout',
         'login', 'machine', 'transfer', '2222222', '1234567', '500000', 'logout',
         'login', 'machine', 'transfer', '3333333', '1234567', '32300', 'logout']]

    # run daily script for each day detailed above
    for i in range(5):
        sys.stdin = io.StringIO(
            '\n'.join(days[i]))
        if i != 3:
            daily.main()
        else:
            daily.main(4)


if __name__ == "__main__":
    main()
