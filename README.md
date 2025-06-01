# To start the env and make it able to work
cd /Users/jake/Desktop/coding/LinkedIn/One_more_time

## create env
python3 -m venv venv

## activating venv
source venv/bin/activate

## install selenium
python -m pip install --upgrade pip
pip install selenium

## if error
# python -m pip install selenium

## Point VS Code at your venv interpreter

### Hit ⇧⌘P → “Python: Select Interpreter”
 
### Choose the one under /Users/jake/Desktop/coding/LinkedIn/One_more_time/venv/bin/python

# run the script
python your_script.py

# enter credentials

# input company people url (e.g., https://www.linkedin.com/company/ocean-conservancy/people/)
## need to include /people
