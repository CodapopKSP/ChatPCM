@REM pip3 install pyinstaller
@REM make sure to add the function "resource_path" and use it to generate the path to the "deep_based" checkpoints folder
pyinstaller --noconfirm --log-level=WARN --clean^
    --onefile ^
    --add-data="deep_based;deep_based" ^
    --name="Deep_Based" ^
    generate_input.py

del Deep_Based.spec
del /S /Q build