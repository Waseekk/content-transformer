@echo off
echo ========================================
echo   Test Translation API
echo ========================================
echo.

echo Testing backend translation endpoint...
echo.

curl -X POST "http://localhost:8000/api/translate/translate-text" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
  -d "{\"text\":\"Cox's Bazar is a beautiful beach destination in Bangladesh.\",\"title\":\"Test Article\",\"save_to_history\":false}"

echo.
echo.
echo ========================================
echo   Test Complete
echo ========================================
echo.
echo If you see Bengali text above, translation is working!
echo If you see "Unauthorized", you need to login first.
echo.
pause
