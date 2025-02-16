db = db.getSiblingDB('api_user_db');

db.createUser({
  user: "api_user",
  pwd: "api_password",
  roles: [{ role: "readWrite", db: "api_user_db" }]
});

print("MongoDB user and database created.");
