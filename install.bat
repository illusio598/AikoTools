@echo off
title Septim Tools - Installation
color 0B
echo.
echo  ============================================
echo            SEPTIM TOOLS v2.0 - INSTALL
echo  ============================================
echo.
echo  [+] Installation des dependances...
echo.
python -m pip install --upgrade pip
python -m pip install requests colorama
echo.
echo  ============================================
echo   Installation terminee !
echo   1) Configurez votre token dans config.json
echo   2) Lancez : python septim_tools.py
echo  ============================================
echo.
pause
