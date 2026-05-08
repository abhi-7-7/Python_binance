binance-futures-cli/
├── .env                    ← API keys (git-ignored)
├── .env.example            ← committed template
├── .gitignore
├── requirements.txt
├── README.md
├── logs/
│   └── trades.log          ← auto-created, committed as proof
├── main.py                 ← entry point
├── config.py               ← loads .env
├── logger.py               ← logging setup
├── cli/
│   ├── __init__.py
│   └── commands.py         ← Click CLI definitions
├── core/
│   ├── __init__.py
│   ├── models.py           ← OrderRequest / OrderResult dataclasses
│   ├── validator.py        ← all input validation logic
│   ├── order_service.py    ← business logic, ties validator + api
│   └── error_handler.py    ← Binance error code mapping
└── api/
    ├── __init__.py
    ├── endpoints.py        ← URL constants
    └── binance_client.py   ← HMAC signing, HTTP calls



### cli commands
# 1. Create project folder and enter it
mkdir binance-futures-cli && cd binance-futures-cli

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate it (Linux/Mac)
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# 4. Create all folders
mkdir -p cli core api logs

# 5. Create all empty Python files
touch main.py config.py logger.py
touch cli/__init__.py cli/commands.py
touch core/__init__.py core/models.py core/validator.py
touch core/order_service.py core/error_handler.py
touch api/__init__.py api/endpoints.py api/binance_client.py

# 6. Create the .env file (fill in your real keys)
cat > .env << 'EOF'
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_secret_here
BINANCE_BASE_URL=https://testnet.binancefuture.com
EOF

# 7. Create .env.example (safe to commit)
cat > .env.example << 'EOF'
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_secret_here
BINANCE_BASE_URL=https://testnet.binancefuture.com
EOF

# 8. Create .gitignore
cat > .gitignore << 'EOF'
.env
venv/
__pycache__/
*.pyc
.DS_Store
EOF

# 9. Install dependencies
pip install click python-dotenv requests

# 10. Freeze requirements
pip freeze > requirements.txt    