
- Run: docker compose up --build
- Insert test data:  docker compose exec backend python -m app.test_data
- pgAdmin: http://localhost:5050
  * Login: admin@test.com & admin
  * Add server:
    * Host: postgres
    * Port: 5432
    * Database: merch_db
    * Username: admin
    * Password: admin
- Stop: docker compose down -v
- Clear browser session: 
  * localStorage.removeItem("chat_messages"); 
  * localStorage.removeItem("chat_session_id")


<img src="1.png" alt="Screenshot 1" width="300" height="400">
<img src="2.png" alt="Screenshot 2" width="300" height="400">
<img src="3.png" alt="Screenshot 3" width="300" height="400">
<img src="4.png" alt="Screenshot 4" width="300" height="400">
<img src="5.png" alt="Screenshot 5" width="300" height="400">
<img src="6.png" alt="Screenshot 6" width="300" height="400">