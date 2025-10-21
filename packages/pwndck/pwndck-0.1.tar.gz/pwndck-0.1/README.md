# pwndck

Check the the HaveIBeenPwned password database to see if a particular password
has been compromised.

It uses the [haveibeenpwned API](https://haveibeenpwned.com/API/v3#PwnedPasswords)
for the check:
  * This use does not require an API key. Anyone can run it.
  * This is more secure than the [web page tool](https://haveibeenpwned.com/Passwords).
    your password is not exposed beyond your local machine.
  * It returns the number of times the password occurs in the database.

# Usage

    $ pwndck.py -h
    usage: pwndck.py [-h] [password]
    
    Report # of password hits in HaveIBeenPwned
    
    positional arguments:
      password    The password to check
    
    options:
      -h, --help  show this help message and exit
    
    Evaluate a password agains the HaveIBeenPwned password database,
    and return the number of accounts for which it has been reported
    as compromised. If the password is not specified on the command
    line, the user will be prompted.

    See https://haveibeenpwned.com/API/v3#PwnedPasswords
