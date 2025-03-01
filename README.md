# Personify--New-Repo
Personified – Your AI-Powered Job Search Assistant Overview Personified is an AI-driven assistant designed to take the hassle out of job searching. Instead of sifting through countless emails and struggling to keep track of applications, Personified ensures everything stays organized—so you don’t have to. 
How It Works All you have to do is apply for jobs—Personified handles the rest. It reads your emails using the Gmail API, detecting job-related messages. It extracts key details like company names, positions, interview dates, and follow-ups. It automatically logs everything into a neatly organized sheet, giving you a clear view of what you’ve applied for, what’s pending, and what needs your attention. No more searching through inboxes or forgetting deadlines—Personified keeps you on track effortlessly. Tech Stack Python for backend logic Gmail API for seamless email retrieval NLP & ML for intelligent classification Flask, HTML, CSS for a clean, intuitive user interface Why Personified? Job hunting is already a full-time job—Personified ensures you never miss an opportunity. Instead of taking over, it works alongside you, simplifying the process so you can focus on landing the perfect role. Stay in control, stay organized, and let AI handle the details.


How to run the file (make sure you are in the main project folder -> do pwd, and it should return personify-front):

First, follow these instructions before doing the next instructions:
1. git remote -v
    1. -> Should return this: origin  https://github.com/nikhil68596/Personify--New-Repo (fetch)
                              origin  https://github.com/nikhil68596/Personify--New-Repo (push)
2. If not, do this:
      1. git remote set-url origin https://github.com/nikhil68596/Personify--New-Repo
          1. Run git remote -v again, and you should get what is expected
          2. Else, search it up for related errors.
        
Now, once the following above works, follow these instructions:
1. Run the Flask API using the command: python3 backend_api/api.py
2. Right click in login.html, and click on Open with Live Server.
3. Register for an account with a new username and password

Now you can access the page, yay!

How to clone the project repo:
1. Go to a new Visual Studio Code window or for wtvr IDE you guys are using.
2. If you have a Github option under Start, then click on it, and follow it from there.
3. Otherwise:
    1. Click on connect to
    2. Select Open Remote Repository on the drop-down menu in the top.
    3. Then Select Open Repository from Github