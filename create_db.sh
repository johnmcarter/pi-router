grn=$'\e[1;32m'
end=$'\e[0m'

echo "[${grn}INFO${end}] Creating user database..."

sqlite3 << EOF
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    username TEXT NOT NULL,
    encrypted_password TEXT NOT NULL
);
.save users.db
EOF