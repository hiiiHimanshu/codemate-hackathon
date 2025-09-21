## 📥 Installation

1. Clone the repository:
```bash
git clone https://github.com/hiiiHimanshu/codemate-hackathon.git
cd codemate-hackathon
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Running Locally

1. Start the Streamlit interface:
```bash
streamlit run app.py
```

2. Run the API server:
```bash
python -m flask run
```

## 🌐 API Usage

### Get System Status
```bash
curl https://code-mate-hack-im51txm1m-hiiihimanshus-projects.vercel.app/api/system/status
```

### Get Memory Information
```bash
curl https://code-mate-hack-im51txm1m-hiiihimanshus-projects.vercel.app/api/system/memory
```

### Get Disk Usage
```bash
curl https://code-mate-hack-im51txm1m-hiiihimanshus-projects.vercel.app/api/system/disk
```

## 🧪 Testing

Run the test suite:
```bash
python -m pytest
```

## 📜 License

MIT License - feel free to use and modify for your own projects!

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

- Create an issue for bug reports or feature requests
- Star the repository if you find it useful!

## 🙏 Acknowledgments

- Built during Codemate Hackathon 2025
- Thanks to all contributors and testers