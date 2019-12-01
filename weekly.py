import io
import sys

import daily


def main():
    with open('valid_accounts.txt', 'w') as wf:
        wf.write('0000000')
    open('master_accounts.txt', 'w').close()
    days = [
        # day 1
        'login', 'agent', 'createacct', '1111111', 'Acct 1', 'logout',
        'login', 'agent', 'createacct', '2222222', 'Acct 2', 'logout',
        'login', 'agent', 'createacct', '3333333', 'Acct 3', 'logout',
        # day 2
        'login', 'agent', 'createacct', '1001001', 'Coolest account', 'logout',
        'login', 'machine', 'deposit', '1001001', '3333333', 'logout',
        'login', 'machine', 'transfer', '1001001', '3333333', '33300', 'logout',
        # day 3
        'login', 'machine', 'deposit', '2222222', '20000000', '200000', 'logout',
        'login', 'machine', 'deposit', '2222222', '200000', 'logout',
        'login', 'machine', 'deposit', '2222222', '100000', 'logout',
        # day 4
        'login', 'machine', 'deposit', '1111111', '1700', 'logout',
        'login', 'machine', 'withdraw', '3333333', '100100', '1000', 'logout',
        'login', 'agent', 'deleteacct', '1001001', 'Coolest account', 'logout',
        # day 5
        'login', 'agent', 'createacct', '123456', '1234567', 'hi', 'give me your money', 'logout',
        'login', 'machine', 'transfer', '1111111', '1234567', '1700', 'logout',
        'login', 'machine', 'transfer', '2222222', '1234567', '500000', 'logout',
        'login', 'machine', 'transfer', '3333333', '1234567', '32300', 'logout']

    sys.stdin = io.StringIO(
        '\n'.join(days))
    for i in range(5):
        daily.main()


if __name__ == "__main__":
    main()
