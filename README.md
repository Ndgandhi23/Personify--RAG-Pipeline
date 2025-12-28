# Personify - AI-Powered Job Search Assistant

An intelligent assistant that automates job application tracking by reading your emails, extracting key details, and organizing everything into a centralized dashboard—so you never miss an opportunity.

## 🎯 Overview

Job hunting shouldn't require managing a second full-time job. **Personify** uses AI to automatically track your job applications by monitoring your Gmail inbox, extracting relevant information (company names, positions, interview dates, deadlines), and logging everything into an organized dashboard.

**You apply. We track. You focus on landing the role.**

## ✨ Features

- 📧 **Automatic Email Monitoring** - Connects via Gmail API to detect job-related emails
- 🤖 **Smart Extraction** - Uses NLP/ML to identify companies, positions, dates, and follow-ups
- 📊 **Organized Dashboard** - Clean interface showing applications, pending items, and deadlines
- ⏰ **Never Miss Deadlines** - Automatic tracking of interview dates and follow-up requirements
- 🔒 **Secure Authentication** - User account system with credential management

## 🚀 Quick Start

### Prerequisites

- Python 3.x
- Gmail account
- Visual Studio Code (or any IDE)
- Live Server extension (for VS Code)

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/nikhil68596/Personify--New-Repo.git
   cd Personify--New-Repo
```

2. **Verify remote URL**
```bash
   git remote -v
```
   
   Should return:
```
   origin  https://github.com/nikhil68596/Personify--New-Repo (fetch)
   origin  https://github.com/nikhil68596/Personify--New-Repo (push)
```
   
   If not, set the correct remote:
```bash
   git remote set-url origin https://github.com/nikhil68596/Personify--New-Repo
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

### Running the Application

1. **Start the Flask backend**
```bash
   python3 backend_api/api.py
```

2. **Launch the frontend**
   - Right-click `login.html`
   - Select **"Open with Live Server"**

3. **Create an account**
   - Register with a new username and password
   - Start tracking your applications!

## 🛠️ Tech Stack

**Backend:**
- Python - Core backend logic
- Flask - RESTful API framework
- Gmail API - Email retrieval and monitoring
- NLP & ML - Intelligent email classification and extraction

**Frontend:**
- HTML5 - Structure
- CSS3 - Styling
- JavaScript - Interactivity

## 📁 Project Structure
```
Personify--New-Repo/
├── backend_api/
│   └── api.py              # Flask API server
├── login.html              # Login/registration page
├── requirements.txt        # Python dependencies
└── README.md
```

## 🔧 Configuration

1. **Gmail API Setup**
   - Enable Gmail API in Google Cloud Console
   - Download credentials and place in project root
   - Configure OAuth consent screen

2. **Environment Variables**
   - Create `.env` file with necessary API keys
   - Configure email monitoring preferences

## 📊 How It Works
```
Email Arrives → Gmail API Detection → NLP Classification → Data Extraction → Dashboard Update
```

1. **Monitor** - Continuously scans your Gmail inbox
2. **Detect** - Identifies job-related emails using ML classifiers
3. **Extract** - Pulls key information (company, role, dates)
4. **Organize** - Logs everything into your dashboard
5. **Alert** - Notifies you of upcoming deadlines

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Troubleshooting

**Remote URL issues:**
```bash
git remote -v  # Check current remote
git remote set-url origin https://github.com/nikhil68596/Personify--New-Repo
```

**Flask not starting:**
- Ensure you're in the correct directory (`pwd` should show project root)
- Check Python version: `python3 --version`
- Verify dependencies: `pip install -r requirements.txt`

**Live Server issues:**
- Install Live Server extension in VS Code
- Right-click the HTML file and select "Open with Live Server"

## 📄 License

MIT License - see LICENSE file for details

## 👥 Team

Built with ❤️ by the Personify team

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Stop juggling applications. Start focusing on interviews.** 🎯
