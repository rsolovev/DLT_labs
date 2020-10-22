import sqlite3

"""
NOTE: YOU NEED sqlite3 LIBRARY INSTALLED TO RUN
"""


def prepare():
    c.execute('''DROP TABLE IF EXISTS accounts''')
    c.execute('''DROP TABLE IF EXISTS ledger''')

    # create tables for account and ledger
    c.execute('''CREATE TABLE IF NOT EXISTS accounts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, credit INTEGER, bankName text)''')

    c.execute('''CREATE TABLE IF NOT EXISTS ledger
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, from_acc INTEGER, to_acc INTEGER,
                     fee INTEGER, amount INTEGER, transactionDateTime text,
                     FOREIGN KEY (from_acc) REFERENCES accounts (id),
                     FOREIGN KEY (to_acc) REFERENCES accounts (id))''')


# create accounts with given amount of money
def create_accounts():
    c.execute('''INSERT INTO accounts (name, credit, bankName) VALUES ('account1',1000, 'SpearBank')''')
    c.execute('''INSERT INTO accounts (name, credit, bankName) VALUES ('account2',1000, 'Tinkoff')''')
    c.execute('''INSERT INTO accounts (name, credit, bankName) VALUES ('account3',1000, 'SpearBank')''')
    c.execute('''INSERT INTO accounts (name, credit, bankName) VALUES ('account4',0, 'feeCollector')''')
    conn.commit()


# check if transaction requires fee
def check_fee(from_account, to_account):
    c.execute('''SELECT bankName FROM accounts WHERE name = \'{}\''''.format(from_account))
    bank1 = c.fetchall()[0][0]
    c.execute('''SELECT bankName FROM accounts WHERE name = \'{}\''''.format(to_account))
    bank2 = c.fetchall()[0][0]
    if bank1 == bank2:
        return 0
    else:
        return 30


# fetch ids of accounts
def check_ids(from_account, to_account):
    c.execute('''SELECT id FROM accounts WHERE name = \'{}\''''.format(from_account))
    id1 = c.fetchall()[0][0]
    c.execute('''SELECT id FROM accounts WHERE name = \'{}\''''.format(to_account))
    id2 = c.fetchall()[0][0]
    return id1, id2


# perform a transaction (transfer money from account to account, apply fee if needed, log the transaction in ledger)
def run_transaction(from_account, to_account, amount, fee_included):
    if fee_included:
        fee = check_fee(from_account, to_account)
    else:
        fee = 0

    fee_account = 'account4'
    id1, id2 = check_ids(from_account, to_account)
    c.execute('''
                UPDATE accounts
                   SET credit = credit - {}
                 WHERE name = \'{}\';'''.format(amount, from_account))

    c.execute('''UPDATE accounts
                   SET credit = credit + {}
                 WHERE name = \'{}\';'''.format(amount, to_account))

    c.execute('''INSERT INTO ledger(from_acc, to_acc, fee, amount, transactionDateTime) 
                VALUES({}, {}, {}, {}, datetime('now'));'''.format(id1, id2, fee, amount))

    if fee != 0:
        c.execute('''UPDATE accounts
                           SET credit = credit + {}
                         WHERE name = \'{}\';'''.format(fee, fee_account))
        c.execute('''UPDATE accounts
                                   SET credit = credit - {}
                                 WHERE name = \'{}\';'''.format(fee, from_account))
    conn.commit()


def print_state(num):
    print("\nAFTER TASK {} (no fees):".format(num))
    print("ACCOUNTS STATE:")
    print(("{:<15}" * len(format_accounts)).format(*format_accounts))
    for row in c.execute('''SELECT * FROM accounts'''):
        print(("{:<15}" * len(row)).format(*row))

    print("\nLEDGER STATE:")
    print(("{:<15}" * len(format_ledger)).format(*format_ledger))
    for row in c.execute('''SELECT * FROM ledger'''):
        print(("{:<15}" * len(row)).format(*row))


conn = sqlite3.connect('ex1_banks.db')
c = conn.cursor()
prepare()
create_accounts()
format_accounts = ['id', 'name', 'credit', 'bankName']
format_ledger = ['id', 'from_account', 'to_account', 'fee', 'amount', 'transactionDateTime']

# transactions from slide 1 (no fees)
run_transaction(from_account='account1', to_account='account3', amount=500, fee_included=0)
run_transaction(from_account='account2', to_account='account1', amount=700, fee_included=0)
run_transaction(from_account='account2', to_account='account3', amount=100, fee_included=0)
print_state(1)

# transactions from slide 2 (with fees)
prepare()
create_accounts()
run_transaction(from_account='account1', to_account='account3', amount=500, fee_included=1)
run_transaction(from_account='account2', to_account='account1', amount=700, fee_included=1)
run_transaction(from_account='account2', to_account='account3', amount=100, fee_included=1)
print_state(2)

c.close()
