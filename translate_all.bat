@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ====================================
echo Starting mass translation...
echo ====================================
echo.

:loop
    echo Checking remaining questions...

    for /f "delims=" %%i in ('docker-compose --profile dev exec -T backend python manage.py shell -c "from api.models import Question; print(Question.objects.filter(translation_text__isnull=True).count())"') do set REMAINING=%%i

    set REMAINING=%REMAINING: =%
    set REMAINING=%REMAINING:~0,-1%

    echo Remaining questions: %REMAINING%
    echo.

    if "%REMAINING%"=="0" (
        echo ====================================
        echo All questions translated! 🎉
        echo ====================================
        goto end
    )

    echo [%date% %time%] Translating batch of 50...
    docker-compose --profile dev exec backend python manage.py translate_questions --batch-size 50

    echo.
    echo Sleeping 3 seconds...
    timeout /t 3 /nobreak > nul
    echo.
    echo ====================================
    echo.

goto loop

:end
echo Translation complete!
pause