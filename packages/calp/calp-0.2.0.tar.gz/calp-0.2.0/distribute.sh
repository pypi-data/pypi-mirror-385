rm -rf build dist *.spec

# uses hock-arcade.py
uv run pyinstaller --clean  src/calp/__main__.py --onefile --collect-all calp --additional-hooks-dir=. --distpath ./dist --workpath ./build -noconfirm --name calp --noconsole --icon=src/calp/assets/images/icon.png --windowed

echo ""
echo "run bundled game"
./dist/calp
