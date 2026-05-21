if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

python3 update.py
python3 -m bot
